from dataclasses import dataclass, field
from typing import Optional, Dict
from core.model.tree_node import DriveNode, PhotosNode

@dataclass
class ClonrConfig:
    destination: Optional[str] = None
    mime_types: Dict[str, str] = field(default_factory=dict)
    drive_root: Optional[DriveNode] = None
    photos_root: Optional[PhotosNode] = None
    def is_valid(self) -> bool:
        return (
            self.destination is not None and
            any(self.drive_root, self.photos_root)
        )

    def summary(self) -> str:
        return f"Destination: {self.destination}\n" \
               f"Selected Tree: {len(self.drive_root.children) if self.drive_root else 0} top-level nodes\n"\
                f"Export Options: {', '.join(self.mime_types.keys()) if self.mime_types else 'None'}\n"
