import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from core.auth import GoogleAuth
from core.tree_builder import build_drive_tree
from core.model.tree_node import DriveNode

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class TreeSelectorApp(tk.Tk):
    def __init__(self, root_node: DriveNode):
        super().__init__()
        self.title("DriveClonr - Select Files to Clone")
        self.geometry("700x600")

        self.root_node = root_node
        self.tree = None
        self.node_map = {}

        self.render_ui()

    def render_ui(self):
        # Header
        ttk.Label(self, text="Select Files and Folders to Clone", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(self, text="Use checkboxes to select the items you want to clone", font=("Helvetica", 12, "italic")).pack(pady=5)

        # Treeview frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = CheckboxTreeview(tree_frame, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Insert tree
        self.insert_drive_node(self.root_node, "")

        # Button group
        controls = ttk.Frame(self)
        controls.pack(pady=10)

        ttk.Button(controls, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Next ➡️", command=self.on_next).pack(side=tk.LEFT, padx=10)

    def insert_drive_node(self, node: DriveNode, parent_id: str):
        label = f"{node.name}"
        node_id = self.tree.insert(parent_id, "end", text=label)
        self.node_map[node_id] = node
        for child in node.children:
            self.insert_drive_node(child, node_id)

    def select_all(self):
        for node_id in self.node_map:
            self.tree.change_state(node_id, "checked")

    def deselect_all(self):
        for node_id in self.node_map:
            self.tree.change_state(node_id, "unchecked")

    def on_next(self):
        """
        Convert checked items into a new tree of TreeNodes for cloning.
        """
        from TreeNode import TreeNode  # Your custom class
        checked = self.tree.get_checked()
        print("✅ Selected for cloning:")
        root = TreeNode(None, [])
        for item_id in checked:
            node = self.node_map.get(item_id)
            if node:
                root.add_child(TreeNode(node.id, node.name, node.mime_type))
        self.print_selected_tree(root)

    def print_selected_tree(self, node, indent=0):
        if node.name:
            print("  " * indent + f"- {node.name}")
        for child in node.children:
            self.print_selected_tree(child, indent + 1)


def query_drive(service, q):
    return service.files().list(
        q=q,
        pageSize=1000,
        fields="files(id, name, mimeType, parents, owners)"
    ).execute().get("files", [])


if __name__ == "__main__":
    print("🔐 Authenticating...")
    auth = GoogleAuth("assets/creds.json", SCOPES)
    creds = auth.authenticate()
    drive = auth.build_service("drive", "v3")

    print("📂 Querying Google Drive...")
    my_files = query_drive(drive, "trashed = false and 'me' in owners")
    shared_files = query_drive(drive, "trashed = false and not 'me' in owners")
    trash_files = query_drive(drive, "trashed = true")

    print("🌲 Building tree...")
    tree_root = build_drive_tree(my_files, shared_files, trash_files)

    print("🖼️ Launching UI...")
    app = TreeSelectorApp(tree_root)
    app.mainloop()
