import json
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

SCOPES = ['https://www.googleapis.com/auth/photoslibrary']

flow = InstalledAppFlow.from_client_secrets_file(
        'creds.json', SCOPES)
creds = flow.run_local_server(port=0)

DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'
service = build('drive', 'v3', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)


def get_response_from_medium_api():
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
    payload = {
                  "filters": {
                  }
                }
    headers = {
        'content-type': 'application/json',
        'Authorization': 'Bearer {}'.format(creds.token)
    }
    
    try:
        res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    except:
        print('Request error') 
    
    print(res.json())
    # dump the response to a file
    with open('response.json', 'w') as f:
        json.dump(res.json(), f)
    x = res.json()
    next_page_token = x.get('nextPageToken')
    while next_page_token:
        for i in x['mediaItems']:
            # download the image
            url = i['baseUrl']
            res = requests.get(url)
            with open(i['filename'], 'wb') as f:
                f.write(res.content)
        # get the next page
        url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
        payload = {
                      "filters": {
                      },
                      "pageToken": next_page_token
                    }
        try:
            res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        except:
            print('Request error')
        x = res.json()
        next_page_token = x.get('nextPageToken')
    print('Done')

get_response_from_medium_api()
