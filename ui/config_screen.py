import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.constants import GOOGLE_WORKSPACE_MIMETYPES, EXPORT_MIMETYPES
from core.utils import check_windows_registry_longpath
import platform


class ConfigScreen(tk.Frame):
    def __init__(self, parent, controller, service):
        super().__init__(parent)
        self.controller = controller
        self.service = service

        ttk.Label(self, text="Configure Clonr Settings", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(self, text="Select export options and source folders", font=("Helvetica", 12)).pack()

        # self.init_source_section()
        self.init_export_section()
        self.init_destination_section()
        self.init_buttons()

    def init_source_section(self):
        self.source_frame = ttk.LabelFrame(self, text="What to Clone")
        self.source_frame.pack(fill="x", padx=10, pady=10)

        self.my_drive = tk.BooleanVar(value=True)
        self.shared = tk.BooleanVar()
        self.trashed = tk.BooleanVar()
        self.photos = tk.BooleanVar()

        ttk.Checkbutton(self.source_frame, text="My Drive", variable=self.my_drive).pack(anchor="w")
        ttk.Checkbutton(self.source_frame, text="Shared with Me", variable=self.shared).pack(anchor="w")
        ttk.Checkbutton(self.source_frame, text="Trash", variable=self.trashed).pack(anchor="w")
        ttk.Checkbutton(self.source_frame, text="Google Photos (Coming Soon)", variable=self.photos, state="disabled").pack(anchor="w")

    def init_export_section(self):
        self.export_frame = ttk.LabelFrame(self, text="Export Formats for Google Workspace Files")
        self.export_frame.pack(fill="x", padx=10, pady=10)

        self.doc_vars = {}
        for doc_type, options in EXPORT_MIMETYPES.items():
            pass  # Filled in dynamically per file type

        self.export_dropdowns = {}
        for label, mime in GOOGLE_WORKSPACE_MIMETYPES.items():
            ttk.Label(self.export_frame, text=label).pack(anchor="w", padx=5)
            var = tk.StringVar(value="PDF")
            dropdown = ttk.OptionMenu(self.export_frame, var, "PDF", *EXPORT_MIMETYPES.keys())
            dropdown.pack(anchor="w", padx=20, pady=2)
            self.doc_vars[mime] = var

    def init_destination_section(self):
        self.dest_frame = ttk.LabelFrame(self, text="Destination Folder")
        self.dest_frame.pack(fill="x", padx=10, pady=10)

        self.destination_path = tk.StringVar()
        ttk.Entry(self.dest_frame, textvariable=self.destination_path, width=50).pack(side="left", padx=5)
        ttk.Button(self.dest_frame, text="Browse", command=self.browse_folder).pack(side="left")

    def init_buttons(self):
        ttk.Button(self, text="Learn What We Can Clone", command=self.learn_more_popup).pack(pady=10)
        ttk.Button(self, text="Continue ➡️", command=self.validate_and_continue).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_path.set(folder)

    def validate_and_continue(self):
        dest = self.destination_path.get()
        if not dest or not os.path.isdir(dest):
            messagebox.showerror("Invalid Directory", "Please choose a valid destination folder.")
            return

        if not self.my_drive.get() and not self.shared.get() and not self.trashed.get():
            messagebox.showerror("No Sources", "Please select at least one source to clone.")
            return

        if platform.system() == "Windows" and not check_windows_registry_longpath():
            messagebox.showwarning(
                "Registry Patch Required",
                "Windows needs LongPathsEnabled to support deep folders. Please enable it before continuing."
            )
            return

        # Check if there's enough space
        drive_size = int(self.service.about().get(fields="storageQuota").execute()["storageQuota"]["usage"])
        drive_size_gb = drive_size / (1024 ** 3)
        free_space_gb = shutil.disk_usage(dest)[2] / (1024 ** 3)

        if drive_size_gb > free_space_gb:
            messagebox.showerror("Insufficient Space", "Not enough disk space to clone your Drive.")
            return

        # Build config dict
        config = {
            "destination": dest,
            "shared": self.shared.get(),
            "my_drive": self.my_drive.get(),
            "trashed": self.trashed.get(),
            "photos": self.photos.get(),
            "mime_types": {
                mime: EXPORT_MIMETYPES[self.doc_vars[mime].get()]
                for mime in self.doc_vars
            }
        }

        # print("✅ Config validated. Proceeding...")
        # from ui.ready_screen import ReadyToStartScreen
        # self.controller.clear_screen()
        # ReadyToStartScreen(self.controller.container, self.controller, self.service, config).pack(fill="both", expand=True)

    def learn_more_popup(self):
        top = tk.Toplevel(self)
        top.title("What can and can't be cloned")
        top.geometry("500x400")
        content = [
            "✅ What DriveClonr can clone:",
            "- Files/folders in My Drive",
            "- Google Workspace files (exported)",
            "- Shared items (unless restricted)",
            "- Files in Trash",
            "",
            "⚠️ Limitations:",
            "- Cannot bypass Google's export restrictions",
            "- Some shared items may be inaccessible"
        ]
        for line in content:
            ttk.Label(top, text=line, wraplength=480, justify="left").pack(anchor="w", padx=10, pady=2)
