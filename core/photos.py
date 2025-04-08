# FILE: core/photos.py

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core.model.tree_node import DriveNode


def get_photos_service(creds):
    """Initialize the Google Photos API client"""
    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)


def list_albums(service):
    """Fetches all albums accessible to the user"""
    albums = []
    next_page = None

    while True:
        response = service.albums().list(pageSize=50, pageToken=next_page).execute()
        albums.extend(response.get("albums", []))
        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return albums


def list_photos_in_album(service, album_id):
    """Lists all media items in a given album"""
    photos = []
    next_page = None

    while True:
        body = {"albumId": album_id, "pageSize": 100, "pageToken": next_page}
        response = service.mediaItems().search(body=body).execute()
        photos.extend(response.get("mediaItems", []))
        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return photos


def list_all_photos(service):
    """Lists all media items in the user's entire library"""
    photos = []
    next_page = None

    while True:
        response = service.mediaItems().list(pageSize=100, pageToken=next_page).execute()
        photos.extend(response.get("mediaItems", []))
        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return photos


def build_photos_tree(creds):
    """Builds a DriveNode-style tree with albums and uncategorized photos"""
    try:
        service = get_photos_service(creds)
        albums = list_albums(service)
        all_media = list_all_photos(service)

        album_root = DriveNode("photos-albums", "Albums", "photos/albums")
        uncategorized_root = DriveNode("photos-uncategorized", "Uncategorized", "photos/uncategorized")

        categorized_ids = set()

        # Build albums
        for album in albums:
            album_id = album["id"]
            album_title = album.get("title", "Untitled Album")
            album_node = DriveNode(album_id, album_title, "photos/album")

            media_items = list_photos_in_album(service, album_id)
            for item in media_items:
                id = item.get("id")
                name = item.get("filename")
                mime_type = item.get("mimeType", "image/jpeg")
                base_url = item.get("baseUrl")
                photo_node = DriveNode(id, name, mime_type)
                photo_node.base_url = base_url  # Attach baseUrl to DriveNode
                album_node.add_child(photo_node)
                categorized_ids.add(id)

            album_root.add_child(album_node)

        # Build uncategorized
        for item in all_media:
            id = item.get("id")
            if id in categorized_ids:
                continue
            name = item.get("filename")
            mime_type = item.get("mimeType", "image/jpeg")
            base_url = item.get("baseUrl")
            photo_node = DriveNode(id, name, mime_type)
            photo_node.base_url = base_url  # Attach baseUrl to DriveNode
            uncategorized_root.add_child(photo_node)

        # Final virtual root node with both branches
        root = DriveNode("photos-root", "Google Photos", "photos/root")
        root.add_child(album_root)
        root.add_child(uncategorized_root)

        return root

    except HttpError as e:
        print("Failed to load Google Photos:", e)
        return DriveNode("photos-root", "Google Photos", "photos/root")