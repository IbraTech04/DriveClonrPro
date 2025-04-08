# ui/tree_screen.py

import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from core.auth import GoogleAuth
from core.model.clonr_config import ClonrConfig
from core.photos import build_photos_tree
from core.tree_builder import build_drive_tree, build_subtree
from core.model.tree_node import DriveNode
from core.utils import prune_checked_nodes

from threading import Thread

class TreeSelectorScreen(tk.Frame):

    auth: GoogleAuth

    def __init__(self, parent, controller, service: GoogleAuth):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.auth = service
        self.node_map = {}
        self.virtual_root = None
        self.photos_root = None
        self.loading_label = ttk.Label(self, text="Loading your drive...", font=("Helvetica", 14, "italic"))
        self.loading_label.pack(pady=20)

        self.loading_caption = ttk.Label(
            self,
            text="Tip: We're parsing your Google Drive file structure into what's known as an AST (Abstract Syntax Tree) in Computer Science. This allows us to efficiently traverse and manipulate the file structure. It's like creating a family tree for your files! This will take a few seconds, relative to your drive size. Your patience is appreciated!",
            font=("Helvetica", 10, "italic"),
            wraplength=500,  
            justify="left"   
        )
        self.loading_caption.pack(pady=10)


        self.spinner = ttk.Progressbar(self, mode="indeterminate")
        self.spinner.pack(pady=10)
        self.spinner.start()

        Thread(target=self.load_tree_async, daemon=True).start()


    def load_tree_async(self):
        # Query files
        # Create virtual root
        self.virtual_root = DriveNode("virtual-root", "Google Drive", "virtual/root")

        # My Drive, Shared, Trash
        my_files = self.query("trashed = false and 'me' in owners")
        shared_files = self.query("trashed = false and not 'me' in owners")
        trash_files = self.query("trashed = true")

        combined = build_drive_tree(my_files, shared_files, trash_files)
        self.virtual_root.children.extend(combined.children)



        # Shared Drives
        # for drive in self.list_shared_drives():
        #     drive_id = drive["id"]
        #     drive_name = drive["name"]
        #     files = self.query_shared_drive_files(drive_id)

        #     if files:
        #         self.virtual_root.add_child(build_subtree(files, drive_name))
        #         # shared_drive_node = build_drive_tree(files, [], [])
        #         # shared_drive_node.id = drive_id
        #         # shared_drive_node.name = drive_name
        #         # shared_drive_node.mime_type = "shared/drive"
        #         # virtual_root.add_child(shared_drive_node)

        self.photos_root = build_photos_tree(self.auth.creds)

        self.after(0, lambda: self.on_tree_build_complete())


    def on_tree_build_complete(self):
        self.spinner.stop()
        self.loading_caption.destroy()
        self.spinner.destroy()
        self.loading_label.destroy()

        # Title
        ttk.Label(self, text="Select Files to Clone", font=("Helvetica", 16, "bold")).pack(pady=10)

        # 📦 Frame to hold TreeView + Scrollbar side-by-side
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 📜 Scrollbar
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 🌲 TreeView
        self.tree = CheckboxTreeview(tree_frame, show="tree", yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scroll.config(command=self.tree.yview)

        # 🌲 Insert your Drive nodes
        self.insert_drive_node(self.virtual_root, "")
        self.insert_drive_node(self.photos_root, "")
        # ✅ Button under tree
        ttk.Button(self, text="Next ➡️", command=self.print_selection).pack(pady=10)



    def query(self, q):
        files = []
        page_token = None

        while True:
            response = self.auth.service.files().list(
                q=f"({q}) and mimeType != 'application/vnd.google-apps.form' and mimeType != 'application/vnd.google-apps.shortcut'",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, parents, owners)",
                pageToken=page_token
            ).execute()

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return files



    def insert_drive_node(self, node: DriveNode, parent_id: str):
        tree_id = self.tree.insert(parent_id, "end", text=node.name)
        self.node_map[tree_id] = node
        for child in node.children:
            self.insert_drive_node(child, tree_id)

    def list_shared_drives(self):
        drives = self.auth.service.drives().list(pageSize=100).execute()
        return drives.get("drives", [])

    def query_shared_drive_files(self, drive_id: str):
        files = []
        page_token = None

        while True:
            response = self.auth.service.files().list(
                q="trashed = false and mimeType != 'application/vnd.google-apps.form' and mimeType != 'application/vnd.google-apps.shortcut'",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, parents, owners)",
                corpora="drive",
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageToken=page_token
            ).execute()

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return files


    def print_selection(self):
        checked_ids = set(self.tree.get_checked())

        def sync_all(tree_id):
            node = self.node_map[tree_id]
            node.is_checked = tree_id in checked_ids

            for child_id in self.tree.get_children(tree_id):
                sync_all(child_id)

            node.is_checked = node.is_checked or any(
                self.node_map[child_id].is_checked for child_id in self.tree.get_children(tree_id)
            )

        root_ids = self.tree.get_children()
        for tree_id in root_ids:
            sync_all(tree_id)

        virtual_root = DriveNode("virtual-root", "Selected Content", "virtual/root")
        for tree_id in root_ids:
            subtree = self.node_map[tree_id]
            pruned = prune_checked_nodes(subtree)
            if pruned and pruned.children:
                virtual_root.add_child(pruned)

        if not virtual_root.children:
            tk.messagebox.showerror("No files selected", "Please select at least one file or folder to clone.")
            return

        config = ClonrConfig(selected_root=virtual_root)
        self.controller.show_config_screen(self.auth, config)



