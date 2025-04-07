import os
import platform
import winreg

from typing import Optional, Union
from .model.tree_node import DriveNode

def check_windows_registry_longpath():
    if platform.system() != "Windows":
        return True
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        return value == 1
    except Exception:
        return False


def prune_checked_nodes(node: DriveNode) -> DriveNode | None:
    """
    Recursively builds a new DriveNode tree with only checked nodes and their checked descendants.
    """
    if not node.is_checked:
        selected_children = [prune_checked_nodes(child) for child in node.children]
        selected_children = [child for child in selected_children if child]
        if selected_children:
            clone = DriveNode(node.id, node.name, node.mime_type, is_checked=False)
            clone.children = selected_children
            return clone
        return None

    # Node is checked
    clone = DriveNode(node.id, node.name, node.mime_type, is_checked=True)
    clone.children = [prune_checked_nodes(child) for child in node.children if prune_checked_nodes(child)]
    return clone
