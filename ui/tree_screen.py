# ui/tree_screen.py

import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from core.tree_builder import build_drive_tree
from core.model.tree_node import DriveNode

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
        checked = self.tree.get_checked()
        print("✅ Selected:")
        for i in checked:
            node = self.node_map[i]
            print(f"- {node.name} ({node.id})")
        self.controller.show_config_screen(self.service)

