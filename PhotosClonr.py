import os
import random
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Required scope for read-only access to Photos library
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']


def get_photos_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'assets/creds.json',
        SCOPES,
    )
    creds = flow.run_local_server(port=0)
    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)


def list_all_photos(service):
    """Retrieve all media items from the Photos library."""
    print("📸 Fetching all photos...")
    media_items = []
    next_page_token = None

    while True:
        response = service.mediaItems().list(
            pageSize=100,
            pageToken=next_page_token
        ).execute()

        media_items.extend(response.get("mediaItems", []))
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"✅ Found {len(media_items)} media items.")
    return media_items


def list_albums(service):
    """List all albums in the Photos library."""
    print("📚 Fetching albums...")
    albums = []
    next_page_token = None

    while True:
        response = service.albums().list(
            pageSize=50,
            pageToken=next_page_token
        ).execute()

        albums.extend(response.get("albums", []))
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"✅ Found {len(albums)} albums.")
    return albums


def list_album_contents(service, album_id):
    """Retrieve all media items for a given album by its album_id."""
    media_items = []
    next_page_token = None

    while True:
        response = service.mediaItems().search(
            body={
                "albumId": album_id,
                "pageSize": 100,
                "pageToken": next_page_token
            }
        ).execute()

        media_items.extend(response.get("mediaItems", []))
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return media_items


def get_albums_and_uncategorized(service):
    """
    Retrieves two distinct lists:
      1. A dictionary mapping each album title to its media items.
      2. A list of uncategorized media items that do not belong to any album.
    """
    albums = list_albums(service)
    album_contents = {}
    album_photo_ids = set()

    # Process each album: list its media items and keep track of their IDs.
    for album in albums:
        album_id = album.get("id")
        album_title = album.get("title", "Untitled")
        print(f"🔍 Fetching contents for album: {album_title}")
        contents = list_album_contents(service, album_id)
        album_contents[album_title] = contents

        for item in contents:
            if "id" in item:
                album_photo_ids.add(item["id"])

    # List all photos and then determine which ones are not in any album.
    all_photos = list_all_photos(service)
    uncategorized_items = [photo for photo in all_photos if photo.get("id") not in album_photo_ids]

    return album_contents, uncategorized_items


def download_random_photo(service, output_folder="downloads"):
    """(Existing functionality) Download a random photo from all media items."""
    media_items = list_all_photos(service)
    if not media_items:
        print("⚠️ No photos found.")
        return

    random_item = random.choice(media_items)
    file_name = random_item.get("filename", "photo.jpg")
    base_url = random_item.get("baseUrl")
    full_url = base_url + "=d"

    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, file_name)

    print(f"⬇️ Downloading random photo: {file_name}")
    response = requests.get(full_url)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(response.content)

    print(f"✅ Saved to: {file_path}")


if __name__ == "__main__":
    service = get_photos_service()
    
    # Query for albums and uncategorized items.
    album_contents, uncategorized_items = get_albums_and_uncategorized(service)
    
    # Output the albums and their contents.
    print("\n=== Albums and Their Contents ===")
    for album_title, items in album_contents.items():
        print(f"Album: {album_title} | Items: {len(items)}")
        for item in items:
            print(f"  - {item.get('filename', 'Unnamed')}")
            
    # Output the uncategorized items.
    print("\n=== Uncategorized Items ===")
    print(f"Total Uncategorized Items: {len(uncategorized_items)}")
    for item in uncategorized_items:
        print(f" - {item.get('filename', 'Unnamed')}")

    # (Optional) You can still download a random photo if needed.
    # download_random_photo(service)
