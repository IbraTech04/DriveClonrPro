from __future__ import annotations

class DriveNode:
    def __init__(self, id: str, name: str, mime_type: str, is_checked=False):
        self.id = id
        self.name = name
        self.mime_type = mime_type
        self.is_checked = is_checked
        self.children: list[DriveNode] = []

    def add_child(self, child: DriveNode):
        self.children.append(child)

    def __repr__(self):
        return f"DriveNode(name={self.name}, id={self.id}, type={self.mime_type}, checked={self.is_checked}, children={len(self.children)})"

    def print_tree(self, indent=0):
        print("  " * indent + f"{'[✔]' if self.is_checked else '[ ]'} {self.name}")
        for child in self.children:
            child.print_tree(indent + 1)

class PhotosNode:
    def __init__(self, id, name, mime_type, base_url=None, is_checked=False):
        self.id = id
        self.name = name
        self.mime_type = mime_type
        self.base_url = base_url
        self.is_checked = is_checked
        self.children = []

    def add_child(self, node):
        self.children.append(node)
