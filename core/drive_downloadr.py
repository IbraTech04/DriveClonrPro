import os
from queue import Queue, Empty
import time
from io import BytesIO

import httplib2
from core import auth
from core.auth import DISCOVERY_SERVICE_URL, GoogleAuth
from core.model.clonr_config import ClonrConfig
from core.model.tree_node import DriveNode
from core.utils import sanitize_filename, get_extension
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

class DownloadStats:
    def __init__(self):
        self.total_files = 0
        self.downloaded = 0
        self.failed = 0
        self.start_time = time.time()

    def eta(self):
        if self.downloaded == 0:
            return "ETA: Calculating..."
        elapsed = time.time() - self.start_time
        avg_time = elapsed / self.downloaded
        remaining = self.total_files - self.downloaded - self.failed
        if remaining <= 0:
            return "Download complete"
        eta_seconds = int(remaining * avg_time)
        
        # Format the ETA into minutes and seconds for better readability
        if eta_seconds < 60:
            return f"ETA: {eta_seconds}s"
        else:
            minutes = eta_seconds // 60
            seconds = eta_seconds % 60
            return f"ETA: {minutes}m {seconds}s"

def walk_drive_tree(node: DriveNode, config: ClonrConfig, tasks, current_path=None):
    """
    Recursively generate download tasks: (DriveNode, output_path)
    """
    if not node or not hasattr(node, 'name'):
        return

    # Set base path
    current_path = current_path or config.destination
    node_path = os.path.join(current_path, sanitize_filename(node.name))

    if 'folder' in node.mime_type:
        # Make sure the folder exists
        os.makedirs(node_path, exist_ok=True)

        for child in node.children:
            walk_drive_tree(child, config, tasks, node_path)
    else:
        if not node.is_checked:
            return

        extension = get_extension(config.mime_types.get(node.mime_type))
        file_path = node_path + extension

        tasks.append((node, file_path))

def download_file(service: GoogleAuth, file_id, export_mime):
    """
    Download a file from Google Drive
    """
    try:
        new_service = service.build_new_service_from_creds()
        if export_mime:  # Google Docs/Sheets/etc. need to be exported
            request = new_service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:  # Regular files can be downloaded directly
            request = new_service.files().get_media(fileId=file_id)
            
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return fh
    except HttpError as e:
        raise e

def run_download_worker(service, config, log_file, tasks: Queue, progress_callback, stats: DownloadStats, thread_id):
    """
    Worker thread that processes download tasks from the queue
    """
    while True:
        try:
            # Get the next task from the queue
            node, file_path = tasks.get_nowait()
        except Empty:  # Fixed: use Empty exception instead of IndexError
            # No more tasks in the queue
            break

        progress_callback("downloading", node.name, thread_id)
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Get the export MIME type (if applicable)
            export_mime = config.mime_types.get(node.mime_type)
            
            # Download the file
            file_data = download_file(service, node.id, export_mime)
            
            # Write the file to disk
            with open(file_path, "wb") as f:
                f.write(file_data.read())
                
            stats.downloaded += 1
            log_file.write(f"Successfully downloaded: {node.name} to {file_path}\n")
            
        except HttpError as e:
            stats.failed += 1
            log_file.write(f"Error downloading {node.name}: {str(e)}\n")
        except Exception as e:
            stats.failed += 1
            log_file.write(f"Unexpected error downloading {node.name}: {str(e)}\n")
        finally:
            # Mark task as done
            tasks.task_done()
            # Update progress 
            progress_callback("update", node.name, thread_id)