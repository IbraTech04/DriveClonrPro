import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread, Lock, Event
from queue import Queue, Empty
import time
import os

from core.drive_downloadr import walk_drive_tree, run_download_worker as run_drive_download_worker
from core.photos_downloadr import walk_photos_tree, run_photos_download_worker
from core.model.clonr_config import ClonrConfig
from core.model.download_stats import DownloadStats


class DriveDownloadScreen(tk.Frame):
    """
    Enhanced download screen with better progress visualization, error handling,
    and the ability to cancel downloads.
    """
    def __init__(self, parent, controller, service, config: ClonrConfig, log_file, num_threads=4):
        super().__init__(parent)
        self.controller = controller
        self.auth = service
        self.config = config
        self.log_file = log_file
        self.num_threads = num_threads

        self.stats = DownloadStats()
        self.tasks = Queue()
        self.lock = Lock()
        self.stop_event = Event()  # For cancellation
        
        self.threads = []
        self.thread_status = {}    # Track status of each thread
        self.thread_progress = {}  # Track progress of current file in each thread
        
        self.create_widgets()
        self.prepare_download()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=10)
        
        ttk.Label(header_frame, text="Download Progress", font=("Helvetica", 16, "bold")).pack(side="left")
        
        # Cancel button
        self.cancel_btn = ttk.Button(header_frame, text="Cancel", command=self.cancel_download)
        self.cancel_btn.pack(side="right")
        
        # Stats frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", pady=5)
        
        # Stats display
        self.stats_label = ttk.Label(stats_frame, text="Files: 0/0 | Success: 0 | Failed: 0")
        self.stats_label.pack(side="left")
        
        self.eta_label = ttk.Label(stats_frame, text="ETA: Calculating...")
        self.eta_label.pack(side="right")
        
        # Overall progress section
        overall_frame = ttk.LabelFrame(main_frame, text="Overall Progress")
        overall_frame.pack(fill="x", pady=10)
        
        self.overall_progress = ttk.Progressbar(overall_frame, mode="determinate")
        self.overall_progress.pack(fill="x", padx=10, pady=10)
        
        # Thread details section
        threads_frame = ttk.LabelFrame(main_frame, text="Thread Details")
        threads_frame.pack(fill="both", expand=True, pady=10)
        
        # Create scrollable frame for thread progress
        canvas = tk.Canvas(threads_frame)
        scrollbar = ttk.Scrollbar(threads_frame, orient="vertical", command=canvas.yview)
        self.thread_container = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=self.thread_container, anchor="nw")
        
        self.thread_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Status bar at bottom
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Preparing download...", anchor="w")
        self.status_label.pack(fill="x")
        
        # Create thread progress rows
        self.thread_frames = []
        for i in range(self.num_threads):
            thread_frame = ttk.Frame(self.thread_container)
            thread_frame.pack(fill="x", pady=2)
            
            # Thread number
            ttk.Label(thread_frame, text=f"Thread {i+1}", width=10).pack(side="left")
            
            # Current file
            current_file = ttk.Label(thread_frame, text="Waiting...", width=30, anchor="w")
            current_file.pack(side="left", padx=(0, 10))
            
            # Progress bar
            progress = ttk.Progressbar(thread_frame, mode="determinate")
            progress.pack(side="left", fill="x", expand=True)
            
            self.thread_frames.append({
                "frame": thread_frame,
                "file_label": current_file,
                "progress": progress
            })
            
            # Initialize status tracking
            self.thread_status[i] = "Waiting"
            self.thread_progress[i] = 0

    def prepare_download(self):
        """Collect all download tasks and start the worker threads"""
        self.status_label["text"] = "Collecting files to download..."
        
        # Start a separate thread for task collection to keep UI responsive
        Thread(target=self._collect_tasks, daemon=True).start()

    def _collect_tasks(self):
        """Collects all tasks and updates the queue"""
        tasks = Queue()
        
        # Walk Drive tree
        if self.config.drive_root:
            for child in self.config.drive_root.children:
                if child.is_checked:
                    walk_drive_tree(child, self.config, tasks)
        
        # Walk Photos tree
        if self.config.photos_root:
            for child in self.config.photos_root.children:
                if child.is_checked:
                    walk_photos_tree(child, self.config, tasks)
        
        self.stats.total_files = tasks.qsize()
        
        # Update UI with total files count
        self.after(0, lambda: self._update_stats_display())
        self.after(0, lambda: self.overall_progress.configure(maximum=tasks.qsize()))
        
        # Queue all tasks
        for task in tasks.queue:
            self.tasks.put(task)
        
        # Start worker threads
        for i in range(self.num_threads):
            t = Thread(target=self.worker_thread, args=(i,), daemon=True)
            self.threads.append(t)
            t.start()
        
        self.after(0, lambda: self.status_label.configure(text=f"Started download of {tasks.qsize()} files"))
        
        # Start ETA update
        self.update_eta_loop()

    def worker_thread(self, thread_id):
        """Worker thread that handles both Drive and Photos downloads"""
        while not self.stop_event.is_set():
            try:
                node, file_path = self.tasks.get(timeout=1)
            except Empty:
                # No more tasks
                self.thread_status[thread_id] = "Finished"
                self.after(0, lambda tid=thread_id: self._update_thread_status(tid, "Finished", ""))
                break
            
            # Update UI to show what we're downloading
            filename = os.path.basename(file_path)
            self.thread_status[thread_id] = f"Downloading {filename}"
            self.after(0, lambda tid=thread_id, name=filename: self._update_thread_status(tid, "Downloading", name))
            
            try:
                # Determine which type of download to use
                if hasattr(node, 'base_url'):  # PhotosNode has base_url
                    # Create a single-item queue for the photos downloader
                    task_queue = Queue()
                    task_queue.put((node, file_path))
                    run_photos_download_worker(task_queue, self.progress_callback, self.stats, thread_id)
                else:
                    # Create a single-item queue for the drive downloader
                    task_queue = Queue()
                    task_queue.put((node, file_path))
                    run_drive_download_worker(self.auth, self.config, self.log_file, task_queue, self.progress_callback, self.stats, thread_id)
                
                # Mark task as done
                self.tasks.task_done()
                
                # Update overall progress
                self.after(0, self._update_overall_progress)
                
            except Exception as e:
                # Log the error
                self.log_file.write(f"Error downloading {filename}: {str(e)}\n")
                
                # Update stats
                with self.lock:
                    self.stats.failed += 1
                
                # Update UI
                self.after(0, self._update_stats_display)
                self.after(0, lambda tid=thread_id, err=str(e): self._update_thread_status(tid, "Error", f"Failed: {filename}"))
                
                # Mark task as done despite error
                self.tasks.task_done()

    def progress_callback(self, action, value, thread_id):
        """Callback to update progress from worker threads"""
        if self.stop_event.is_set():
            return
            
        if action == "downloading":
            # A new file download has started
            self.after(0, lambda tid=thread_id, name=value: self._update_thread_status(tid, "Downloading", name))
            
        elif action == "update":
            if isinstance(value, int):
                # Progress percentage for current file
                self.thread_progress[thread_id] = value
                self.after(0, lambda tid=thread_id, val=value: self._update_thread_progress(tid, val))
            else:
                # Completed a file
                with self.lock:
                    self.stats.downloaded += 1
                
                self.after(0, self._update_stats_display)
                self.after(0, self._update_overall_progress)
                
                # Check if all done
                if self.stats.downloaded + self.stats.failed >= self.stats.total_files:
                    self.after(0, self._download_complete)

    def update_eta_loop(self):
        """Updates the estimated time remaining display"""
        if self.stop_event.is_set():
            return
            
        eta_text = self.stats.eta()
        self.eta_label["text"] = eta_text
        
        # Continue updating if not done
        if self.stats.downloaded + self.stats.failed < self.stats.total_files:
            self.after(1000, self.update_eta_loop)

    def _update_thread_status(self, thread_id, status, filename):
        """Update the status display for a thread"""
        if thread_id >= len(self.thread_frames):
            return
            
        frame_data = self.thread_frames[thread_id]
        frame_data["file_label"]["text"] = filename
        
        # Reset progress when starting a new file
        if status == "Downloading":
            frame_data["progress"]["value"] = 0

    def _update_thread_progress(self, thread_id, progress_value):
        """Update the progress bar for a thread"""
        if thread_id >= len(self.thread_frames):
            return
            
        frame_data = self.thread_frames[thread_id]
        frame_data["progress"]["value"] = progress_value

    def _update_overall_progress(self):
        """Update the overall progress bar and check for completion"""
        completed = self.stats.downloaded + self.stats.failed
        self.overall_progress["value"] = completed
        
        if completed >= self.stats.total_files:
            self._download_complete()

    def _update_stats_display(self):
        """Update the statistics display"""
        completed = self.stats.downloaded + self.stats.failed
        total = self.stats.total_files
        success = self.stats.downloaded
        failed = self.stats.failed
        
        self.stats_label["text"] = f"Files: {completed}/{total} | Success: {success} | Failed: {failed}"

    def _download_complete(self):
        """Handle completion of all downloads"""
        self.status_label["text"] = "Download complete!"
        self.cancel_btn["text"] = "Close"
        self.cancel_btn["command"] = self.controller.show_main_screen
        
        # Show summary in a message box
        total = self.stats.total_files
        success = self.stats.downloaded
        failed = self.stats.failed
        
        message = f"Download complete!\n\nTotal files: {total}\nSuccessfully downloaded: {success}\nFailed: {failed}"
        
        if failed > 0:
            message += "\n\nSee log file for details on failed downloads."
            messagebox.showinfo("Download Complete", message)
        else:
            messagebox.showinfo("Download Complete", message)

    def cancel_download(self):
        """Cancel all ongoing downloads"""
        if self.stop_event.is_set():
            # We've already cancelled, so this is now a "Close" button
            self.controller.show_main_screen()
            return
            
        if messagebox.askyesno("Cancel Download", "Are you sure you want to cancel the download?"):
            self.status_label["text"] = "Cancelling download..."
            self.stop_event.set()
            
            # Stop accepting new tasks
            with self.lock:
                while not self.tasks.empty():
                    try:
                        self.tasks.get_nowait()
                        self.tasks.task_done()
                    except Empty:
                        break
            
            # Wait for threads to exit (with timeout)
            for t in self.threads:
                t.join(timeout=0.5)
                
            self.status_label["text"] = "Download cancelled."
            self.cancel_btn["text"] = "Close"