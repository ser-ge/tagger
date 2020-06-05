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

def get_files(folder_id, drive):
    page_token = None
    files =[]
    q= f"'{folder_id}' in parents"
    while True:
        response = drive.files().list(q=q,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
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
    print(type(files[0]))
    files = [(file.get('name'), download_file(file['id'],drive)) for file in files]
    sync_to_notion(files)

def sync_drive(creds_dict):
    drive= build_drive_service(creds_dict)
    files = get_files(TARGET_FOLDER, drive)
    print(f'{len(files)} files downloaded')
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


