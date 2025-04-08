import os
import requests
from queue import Queue, Empty

from core.model.tree_node import PhotosNode
from core.model.clonr_config import ClonrConfig
from core.model.download_stats import DownloadStats
from core.utils import sanitize_filename, get_extension


def walk_photos_tree(node: PhotosNode, config: ClonrConfig, tasks: Queue, current_path=None):
    """
    Recursively walks the PhotosNode tree and generates download tasks.
    Each task is a tuple of (PhotosNode, file_path).
    """
    if not node or not hasattr(node, 'name'):
        return

    current_path = current_path or config.destination
    node_path = os.path.join(current_path, sanitize_filename(node.name))

    if node.mime_type in ["virtual", "photos/albums", "photos/album", "photos/uncategorized"]:
        os.makedirs(node_path, exist_ok=True)
        for child in node.children:
            walk_photos_tree(child, config, tasks, node_path)
    else:
        if not node.is_checked:
            return

        extension = get_extension(node.mime_type)
        file_path = node_path + extension
        tasks.put((node, file_path))


def run_photos_download_worker(tasks: Queue, progress_callback, stats: DownloadStats, thread_id: int):
    """
    Worker thread to download files from Google Photos using baseUrl.
    Each task is a tuple of (PhotosNode, file_path).
    """
    while True:
        try:
            node, file_path = tasks.get_nowait()
        except Empty:
            break

        progress_callback("downloading", node.name, thread_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            download_url = node.base_url + "=d"

            response = requests.get(download_url)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)

            stats.downloaded += 1
        except Exception as e:
            stats.failed += 1
        finally:
            tasks.task_done()
            progress_callback("update", node.name, thread_id)
