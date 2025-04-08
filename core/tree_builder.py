from core.model.tree_node import DriveNode, PhotosNode

def build_drive_tree(my_files: list[dict], shared_files: list[dict], trash_files: list[dict]) -> DriveNode:
    """
    Builds a unified tree with three roots: My Drive, Shared with Me, and Trash.
    """
    virtual_root = DriveNode("virtual-root", "Google Drive", "virtual")

    # Build each subtree
    my_drive_root = build_subtree_drive(my_files, "My Drive")
    shared_root = build_subtree_drive(shared_files, "Shared with Me")
    trash_root = build_subtree_drive(trash_files, "Trash")

    virtual_root.add_child(my_drive_root)
    virtual_root.add_child(shared_root)
    virtual_root.add_child(trash_root)

    return virtual_root

def build_photos_tree(uncategorized_photos: list[dict], albums: dict[str, list[dict]]) -> PhotosNode:
    """
    Tree-ifies the Google Photos albums and uncategorized photos.
    Returns a PhotosNode with two branches: Albums and Uncategorized Photos.

    Parameters:
      uncategorized_photos: List of media items that are not in any album.
      albums: A dictionary where each key is an album title and each value is a list of media items in that album.
    """
    virtual_root = PhotosNode("virtual-root", "Google Photos", "virtual")

    albums_root = PhotosNode("photos-albums", "Albums", "photos/albums")

    # Iterate over the albums dictionary.
    for album_title, media_items in albums.items():
        # Since we do not have separate album metadata, use the album title as the id.
        album_node = PhotosNode(album_title, album_title, "photos/album")

        for item in media_items:
            photo_id = item.get("id")
            name = item.get("filename")
            mime_type = item.get("mimeType", "image/jpeg")
            base_url = item.get("baseUrl")
            photo_node = PhotosNode(photo_id, name, mime_type, base_url=base_url)
            album_node.add_child(photo_node)

        albums_root.add_child(album_node)
    
    # Build the uncategorized photos branch.
    uncategorized_root = PhotosNode("photos-uncategorized", "Uncategorized", "photos/uncategorized")
    for item in uncategorized_photos:
        photo_id = item.get("id")
        name = item.get("filename")
        mime_type = item.get("mimeType", "image/jpeg")
        base_url = item.get("baseUrl")
        photo_node = PhotosNode(photo_id, name, mime_type, base_url=base_url)
        uncategorized_root.add_child(photo_node)
    
    virtual_root.add_child(albums_root)
    virtual_root.add_child(uncategorized_root)
    
    return virtual_root


def build_subtree_drive(file_list: list[dict], label: str) -> DriveNode:
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

