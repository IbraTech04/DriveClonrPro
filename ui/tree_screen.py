# ui/tree_screen.py

import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from core.model.clonr_config import ClonrConfig
from core.tree_builder import build_drive_tree
from core.model.tree_node import DriveNode
from core.utils import prune_checked_nodes

class TreeSelectorScreen(tk.Frame):
    def __init__(self, parent, controller, service):
        super().__init__(parent)
        self.controller = controller
        self.service = service
        self.node_map = {}

        ttk.Label(self, text="Select Files to Clone", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.tree = CheckboxTreeview(self, show="tree")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Query files
        my_files = self.query("trashed = false and 'me' in owners")
        shared_files = self.query("trashed = false and not 'me' in owners")
        trash_files = self.query("trashed = true")
        root_node = build_drive_tree(my_files, shared_files, trash_files)

        self.insert_drive_node(root_node, "")

        ttk.Button(self, text="Next ➡️", command=self.print_selection).pack(pady=10)

    def query(self, q):
        return self.service.files().list(
            q=q,
            pageSize=1000,
            fields="files(id, name, mimeType, parents, owners)"
        ).execute().get("files", [])

    def insert_drive_node(self, node: DriveNode, parent_id: str):
        tree_id = self.tree.insert(parent_id, "end", text=node.name)
        self.node_map[tree_id] = node
        for child in node.children:
            self.insert_drive_node(child, tree_id)


    def print_selection(self):
        checked_ids = set(self.tree.get_checked())

        def sync_all(tree_id):
            node = self.node_map[tree_id]
            node.is_checked = tree_id in checked_ids

            # Sync children first (post-order)
            for child_id in self.tree.get_children(tree_id):
                sync_all(child_id)

            # If any child is checked, ensure parent is marked as checked too
            node.is_checked = node.is_checked or any(
                self.node_map[child_id].is_checked for child_id in self.tree.get_children(tree_id)
            )


        for top_level in self.tree.get_children():
            sync_all(top_level)

        virtual_root_id = self.tree.get_children()[0]  # "Google Drive"
        virtual_root = self.node_map[virtual_root_id]

        pruned_root = prune_checked_nodes(virtual_root)
        if not pruned_root or not pruned_root.children:
            tk.messagebox.showerror("No files selected", "Please select at least one file or folder to clone.")
            return

        config = ClonrConfig(selected_root=pruned_root)
        self.controller.show_config_screen(self.service, config)


