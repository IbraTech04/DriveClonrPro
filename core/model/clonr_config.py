from dataclasses import dataclass, field
from typing import Optional, Dict
from core.model.tree_node import DriveNode

@dataclass
class ClonrConfig:
    destination: Optional[str] = None
    mime_types: Dict[str, str] = field(default_factory=dict)
    selected_root: Optional[DriveNode] = None

    def is_valid(self) -> bool:
        return (
            self.destination is not None and
            self.selected_root is not None
        )

    def summary(self) -> str:
        return f"Destination: {self.destination}\n" \
               f"Selected Tree: {len(self.selected_root.children) if self.selected_root else 0} top-level nodes\n"\
                f"Export Options: {', '.join(self.mime_types.keys()) if self.mime_types else 'None'}\n"
