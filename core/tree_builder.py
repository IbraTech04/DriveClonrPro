# core/tree_builder.py

from core.model.tree_node import DriveNode

def build_drive_tree(my_files: list[dict], shared_files: list[dict], trash_files: list[dict]) -> DriveNode:
    """
    Builds a unified tree with three roots: My Drive, Shared with Me, and Trash.
    """
    virtual_root = DriveNode("virtual-root", "Google Drive", "virtual")

    # Build each subtree
    my_drive_root = build_subtree(my_files, "My Drive")
    shared_root = build_subtree(shared_files, "Shared with Me")
    trash_root = build_subtree(trash_files, "Trash")

    virtual_root.add_child(my_drive_root)
    virtual_root.add_child(shared_root)
    virtual_root.add_child(trash_root)

    return virtual_root

def build_subtree(file_list: list[dict], label: str) -> DriveNode:
    """
    Builds a tree from a flat file list and returns a labeled root node.
    """
    id_to_node = {}
    children_map = {}

    # Step 1: Create nodes
    for file in file_list:
        node = DriveNode(file['id'], file['name'], file['mimeType'])
        id_to_node[file['id']] = node
        for parent_id in file.get('parents', []):
            children_map.setdefault(parent_id, []).append(node)

    root = DriveNode(label.lower() + "-root", label, "application/vnd.google-apps.folder")

    # Step 2: Link children to parents
    for parent_id, children in children_map.items():
        parent_node = id_to_node.get(parent_id, root)
        for child in children:
            parent_node.add_child(child)

    return root
