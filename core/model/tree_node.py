from __future__ import annotations
from __future__ import annotations
from abc import ABC, abstractmethod

class DownloadableNode(ABC):
    id: str
    name: str
    mime_type: str
    is_checked: bool
    children: list[DownloadableNode]

    def __init__(self, id, name, mime_type, is_checked=False):
        self.id = id
        self.name = name
        self.mime_type = mime_type
        self.is_checked = is_checked
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    @abstractmethod
    def is_folder(self) -> bool:
        pass

class DriveNode(DownloadableNode):
    def __init__(self, id, name, mime_type, is_checked=False):
        super().__init__(id, name, mime_type, is_checked)

    def is_folder(self) -> bool:
        return self.mime_type == "application/vnd.google-apps.folder"

class PhotosNode(DownloadableNode):
    base_url: str
    
    def __init__(self, id, name, mime_type, is_checked=False, base_url=None):
        super().__init__(id, name, mime_type, is_checked)
        self.base_url = base_url

    def is_folder(self) -> bool:
        return self.mime_type == "photos/album" or self.mime_type == "photos/uncategorized"