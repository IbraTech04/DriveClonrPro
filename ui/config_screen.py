import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from core.constants import EXPORT_OPTIONS, GOOGLE_WORKSPACE_MIMETYPES, EXPORT_MIMETYPES
from core.utils import check_windows_registry_longpath
from core.model.clonr_config import ClonrConfig
import platform

# from ui.controller import AppController


class ConfigScreen(tk.Frame):

    # controller: AppController

    def __init__(self, parent, controller, service, config: ClonrConfig):
        super().__init__(parent)
        self.controller = controller
        self.auth = service
        self.config = config

        ttk.Label(self, text="Configure Clonr Settings", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(self, text="Select export options and source folders", font=("Helvetica", 12)).pack()

        self.init_export_section()
        self.init_destination_section()
        self.init_buttons()

    def init_export_section(self):
        self.export_frame = ttk.LabelFrame(self, text="Export Formats for Google Workspace Files")
        self.export_frame.pack(fill="x", padx=10, pady=10)

        self.doc_vars = {}
        self.export_dropdowns = {}

        for label, mime in GOOGLE_WORKSPACE_MIMETYPES.items():
            options = EXPORT_OPTIONS[mime]
            default = options[0]

            ttk.Label(self.export_frame, text=label).pack(anchor="w", padx=5)
            var = tk.StringVar(value=default)
            dropdown = ttk.OptionMenu(self.export_frame, var, default, *options)
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
        ttk.Button(self, text="Start Cloning ➡️", command=self.validate_and_continue).pack(pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_path.set(folder)

    def validate_and_continue(self):
        dest = self.destination_path.get()
        if not dest or not os.path.isdir(dest):
            messagebox.showerror("Invalid Directory", "Please choose a valid destination folder.")
            return

        if platform.system() == "Windows" and not check_windows_registry_longpath():
            messagebox.showwarning(
                "Registry Patch Required",
                "Windows needs LongPathsEnabled to support deep folders. Please enable it before continuing."
            )
            return

        # Check if there's enough space
        drive_size = int(self.auth.service.about().get(fields="storageQuota").execute()["storageQuota"]["usage"])
        drive_size_gb = drive_size / (1024 ** 3)
        free_space_gb = shutil.disk_usage(dest)[2] / (1024 ** 3)

        if drive_size_gb > free_space_gb:
            messagebox.showerror("Insufficient Space", "Not enough disk space to clone your Drive.")
            return

        self.config.destination = dest
        self.config.mime_types = {
            mime: EXPORT_MIMETYPES[self.doc_vars[mime].get()]
            for mime in self.doc_vars
        }

        print("Config:", self.config)

        self.controller.show_download_screen(self.auth, self.config)

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
