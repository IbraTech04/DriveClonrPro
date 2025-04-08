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


def download_random_photo(service, output_folder="downloads"):
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
    download_random_photo(service)
