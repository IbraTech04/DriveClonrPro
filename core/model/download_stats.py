import time

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
        minutes = eta_seconds // 60
        seconds = eta_seconds % 60
        return f"ETA: {minutes}m {seconds}s" if minutes else f"ETA: {seconds}s"