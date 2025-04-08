import tkinter as tk
from tkinter import ttk
from threading import Thread, Lock
from core.drive_downloadr import walk_drive_tree, run_download_worker, DownloadStats
from queue import Queue

class DriveDownloadScreen(tk.Frame):
    def __init__(self, parent, controller, service, config, log_file, num_threads=4):
        super().__init__(parent)
        self.controller = controller
        self.auth = service
        self.config = config
        self.log_file = log_file
        self.num_threads = num_threads

        self.stats = DownloadStats()
        self.tasks = Queue()  # Changed from LifoQueue to Queue for FIFO processing
        self.lock = Lock()
        self.thread_bars = []
        self.threads = []

        self.create_widgets()
        self.prepare_download()

    def create_widgets(self):
        ttk.Label(self, text="Cloning in Progress", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.eta_label = ttk.Label(self, text="ETA: Calculating...", font=("Helvetica", 10))
        self.eta_label.pack(pady=5)

        self.overall_progress = ttk.Progressbar(self, mode="determinate")
        self.overall_progress.pack(fill="x", padx=20, pady=10)

        self.thread_frame = ttk.Frame(self)
        self.thread_frame.pack(pady=10, fill="x")

        for i in range(self.num_threads):
            bar = ttk.Progressbar(self.thread_frame, mode="determinate")
            bar.pack(fill="x", padx=20, pady=2)
            self.thread_bars.append(bar)

        self.status_label = ttk.Label(self, text="Starting download...", font=("Helvetica", 10))
        self.status_label.pack(pady=10)

    def prepare_download(self):
        # Create a list to collect all tasks
        flat_tasks = []
        
        # Populate the flat_tasks list with download tasks
        for child in self.config.selected_root.children:
            if child.is_checked:
                walk_drive_tree(child, self.config, flat_tasks)
        
        # Set the progress bar maximum based on total tasks
        self.overall_progress["maximum"] = len(flat_tasks)
        self.stats.total_files = len(flat_tasks)
        
        # Put all tasks into the queue
        for task in flat_tasks:
            self.tasks.put(task)

        # Start worker threads
        for i in range(self.num_threads):
            t = Thread(target=run_download_worker, args=(
                self.auth,
                self.config,
                self.log_file,
                self.tasks,
                self.progress_callback,
                self.stats,
                i
            ))
            t.daemon = True
            self.threads.append(t)
            t.start()

        # Start the ETA update loop
        self.update_eta_loop()

    def progress_callback(self, action, value, thread_id):
        def update():
            if action == "downloading":
                self.status_label["text"] = f"Thread {thread_id+1} downloading: {value}"
            elif action == "update":
                self.thread_bars[thread_id]["value"] += 1
                self.overall_progress["value"] = self.stats.downloaded
                
                # Check if download is complete
                if self.stats.downloaded + self.stats.failed >= self.stats.total_files:
                    self.status_label["text"] = "Download complete."

        self.after(0, update)

    def update_eta_loop(self):
        self.eta_label["text"] = self.stats.eta()
        if self.stats.downloaded + self.stats.failed < self.stats.total_files:
            self.after(1000, self.update_eta_loop)
        else:
            self.status_label["text"] = "Download complete."