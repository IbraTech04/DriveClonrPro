import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.photos.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
        'creds.json', SCOPES)
creds = flow.run_local_server(port=0)
DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'
service = build('drive', 'v3', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)

# We want to get the pictures stored in the user's Google Photos account
pictures = service.files().list(q="mimeType='image/jpeg'", spaces='photos', fields='nextPageToken, files(id, name)', pageToken=None).execute()

# get a list of all drives in the user's account
drives = service.drives().list().execute()
drives = drives['drives']
x=1