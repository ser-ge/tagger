import google
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from main import sync_to_notion
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

TARGET_FOLDER = '14XoumtXaKPkcTUIxp-gZDyJUgnAcXjfg'



def build_drive_service(creds_dict):
    credentials = google.oauth2.credentials.Credentials(
      **creds_dict)
    drive = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    return drive

def get_files(folder_id, drive, modified_since=None):

    page_token = None
    files =[]
    q= f"'{folder_id}' in parents"

    if modified_since is not None:
        start_time = modified_since.strftime('%Y-%m-%dT%H:%m:%S')
        q_time =f"modifiedTime > '{start_time}'"
        q = f'{q} and {q_time}'
    print(f"Gdrive Api Query: '{q}'")
    while True:
        response = drive.files().list(q=q,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name, modifiedTime)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            files.append(file)
            print(f"Found file {file.get('name')} : {file.get('id')}")
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files

def process_files(files,drive):
    files = [(file.get('name'), download_file(file['id'],drive)) for file in files]
    if len(files) > 0:
        sync_to_notion(files)

def sync_google_drive(creds_dict, modified_since):
    drive= build_drive_service(creds_dict)
    files = get_files(TARGET_FOLDER, drive, modified_since)
    process_files(files,drive)


def download_file(file_id, drive):
    request = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}".format( int(status.progress() * 100)))
    fh.seek(0)
    with open('downloads/test.pdf', 'wb') as f:
        f.write(fh.read())

    return fh


