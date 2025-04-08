# ui/tree_screen.py

import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from core.auth import GoogleAuth
from core.model.clonr_config import ClonrConfig
from core.tree_builder import build_drive_tree, build_photos_tree, build_subtree_drive
from core.model.tree_node import DownloadableNode, DriveNode, PhotosNode
from core.utils import prune_checked_nodes

from threading import Thread

class TreeSelectorScreen(tk.Frame):

    auth: GoogleAuth

    def __init__(self, parent, controller, service: GoogleAuth):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.auth = service
        self.node_map = {}
        self.virtual_root = None
        self.photos_root = None
        self.loading_label = ttk.Label(self, text="Loading your drive...", font=("Helvetica", 14, "italic"))
        self.loading_label.pack(pady=20)

        self.spinner = ttk.Progressbar(self, mode="indeterminate")
        self.spinner.pack(pady=10)
        self.spinner.start()

        Thread(target=self.load_tree_async, daemon=True).start()


    def load_tree_async(self):
        # Query files
        # Create virtual root
        self.virtual_root = DriveNode("virtual-root", "Google Drive", "virtual/root")

        # My Drive, Shared, Trash
        my_files = self.query("trashed = false and 'me' in owners")
        shared_files = self.query("trashed = false and not 'me' in owners")
        trash_files = self.query("trashed = true")

        combined = build_drive_tree(my_files, shared_files, trash_files)
        self.virtual_root.children.extend(combined.children)

        # Photos:
        self.photos_root = PhotosNode("photos-root", "Google Photos", "photos")
        albums, uncategorized = self.get_albums_and_uncategorized(
            self.auth.get_photos_service())
        self.photos_root = build_photos_tree(uncategorized, albums)

        # # Shared Drives
        # for drive in self.list_shared_drives():
        #     drive_id = drive["id"]
        #     drive_name = drive["name"]
        #     files = self.query_shared_drive_files(drive_id)

        #     if files:
        #         self.virtual_root.add_child(build_subtree_drive(files, drive_name))
        #         shared_drive_node = build_drive_tree(files, [], [])
        #         shared_drive_node.id = drive_id
        #         shared_drive_node.name = drive_name
        #         shared_drive_node.mime_type = "shared/drive"
        #         virtual_root.add_child(shared_drive_node)
        self.after(0, lambda: self.on_tree_build_complete())

    def on_tree_build_complete(self):
        self.spinner.stop()
        self.spinner.destroy()
        self.loading_label.destroy()

        # Title
        ttk.Label(self, text="Select Files to Clone", font=("Helvetica", 16, "bold")).pack(pady=10)

        # 📦 Frame to hold TreeView + Scrollbar side-by-side
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 📜 Scrollbar
        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 🌲 TreeView
        self.tree = CheckboxTreeview(tree_frame, show="tree", yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scroll.config(command=self.tree.yview)

        # 🌲 Insert your Drive nodes
        self.insert_drive_node(self.virtual_root, "")
        self.insert_drive_node(self.photos_root, "")
        # ✅ Button under tree
        ttk.Button(self, text="Next ➡️", command=self.print_selection).pack(pady=10)



    def query(self, q):
        """Query Google Drive API with error handling"""
        files = []
        page_token = None

        try:
            while True:
                response = self.auth.service.files().list(
                    q=f"({q}) and mimeType != 'application/vnd.google-apps.form'",
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, parents, owners)",
                    pageToken=page_token
                ).execute()

                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken")

                if not page_token:
                    break
        except Exception as e:
            print(f"Drive API query error: {str(e)}")
            raise
            
        return files



    def insert_drive_node(self, node: DownloadableNode, parent_id: str):
        tree_id = self.tree.insert(parent_id, "end", text=node.name)
        self.node_map[tree_id] = node
        for child in node.children:
            self.insert_drive_node(child, tree_id)

    def list_shared_drives(self):
        drives = self.auth.service.drives().list(pageSize=100).execute()
        return drives.get("drives", [])

    def query_shared_drive_files(self, drive_id: str):
        files = []
        next_page_token = None

        while True:
            response = self.auth.service.files().list(
                q="trashed = false and mimeType != 'application/vnd.google-apps.form' and mimeType != 'application/vnd.google-apps.shortcut'",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, parents, owners)",
                corpora="drive",
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageToken=next_page_token
            ).execute()

            files.extend(response.get("files", []))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return files


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

        # virtual_root_id = self.tree.get_children()[0]  # "Google Drive"
        # virtual_root = self.node_map[virtual_root_id]
    
        prune_checked_nodes(self.virtual_root)
        prune_checked_nodes(self.photos_root)
        # if not pruned_root or not pruned_root.children:
        #     tk.messagebox.showerror("No files selected", "Please select at least one file or folder to clone.")
        #     return

        config = ClonrConfig(drive_root=self.virtual_root, photos_root=self.photos_root)
        self.controller.show_config_screen(self.auth, config)


    def list_all_photos(self, service):
        """Retrieve all media items from the Photos library."""
        media_items = []
        next_page_token = None

        while True:
            # Base parameters
            params = {
                "pageSize": 100
            }
            
            # Only add pageToken if we have one
            if next_page_token:
                params["pageToken"] = next_page_token
                
            response = service.mediaItems().list(**params).execute()

            media_items.extend(response.get("mediaItems", []))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return media_items


    def list_albums(self, service):
        """List all albums in the Photos library."""
        print("📚 Fetching albums...")
        albums = []
        next_page_token = None

        while True:
            # Base parameters
            params = {
                "pageSize": 50
            }
            
            # Only add pageToken if we have one
            if next_page_token:
                params["pageToken"] = next_page_token
                
            response = service.albums().list(**params).execute()

            albums.extend(response.get("albums", []))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return albums


    def list_album_contents(self, service, album_id):
        """Retrieve all media items for a given album by its album_id."""
        media_items = []
        next_page_token = None

        while True:
            # Base request body
            body = {
                "albumId": album_id,
                "pageSize": 100
            }
            
            # Only add pageToken if we have one
            if next_page_token:
                body["pageToken"] = next_page_token
                
            response = service.mediaItems().search(body=body).execute()

            media_items.extend(response.get("mediaItems", []))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return media_items


    def get_albums_and_uncategorized(self, service):
        """
        Retrieves two distinct lists:
        1. A dictionary mapping each album title to its media items.
        2. A list of uncategorized media items that do not belong to any album.
        """
        albums = self.list_albums(service)
        album_contents = {}
        album_photo_ids = set()

        # Process each album: list its media items and keep track of their IDs.
        for album in albums:
            album_id = album.get("id")
            album_title = album.get("title", "Untitled")
            contents = self.list_album_contents(service, album_id)
            album_contents[album_title] = contents

            for item in contents:
                if "id" in item:
                    album_photo_ids.add(item["id"])

        # List all photos and then determine which ones are not in any album.
        all_photos = self.list_all_photos(service)
        uncategorized_items = [photo for photo in all_photos if photo.get("id") not in album_photo_ids]

        return album_contents, uncategorized_items