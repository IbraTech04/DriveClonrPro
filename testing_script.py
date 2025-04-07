from core.auth import GoogleAuth
from core.tree_builder import build_drive_tree
from pprint import pprint

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

auth = GoogleAuth("assets/creds.json", SCOPES)
creds = auth.authenticate()
drive = auth.build_service("drive", "v3")

def query_drive(q):
    return drive.files().list(
        q=q,
        pageSize=1000,
        fields="files(id, name, mimeType, parents, owners)"
    ).execute().get("files", [])

print("Fetching My Drive files...")
my_files = query_drive("trashed = false and 'me' in owners")

print("Fetching Shared with Me files...")
shared_files = query_drive("trashed = false and not 'me' in owners")

print("Fetching Trashed files...")
trash_files = query_drive("trashed = true")

tree = build_drive_tree(my_files, shared_files, trash_files)

def print_tree(node, indent=0):
    print("  " * indent + f"- {node.name}")
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(tree)
