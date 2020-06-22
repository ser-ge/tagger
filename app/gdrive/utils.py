import io
from collections import namedtuple

import google
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app import db

API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

def save_new_drive_creds(user, refreshed_credentials):
    '''save creds returned by google in case of refresh'''
    user.google_creds = refreshed_credentials
    db.session.commit()

def build_drive_service(user):
    credentials = google.oauth2.credentials.Credentials(**user.google_creds)
    drive = build(API_SERVICE_NAME, API_VERSION,cache_discovery=False, credentials=credentials)
    save_new_drive_creds(user, credentials)
    return drive

def get_drive_folders(user):
    ''' retrieve all folders'''

    drive= build_drive_service(user)

    page_token = None
    folders =[]

    q = "mimeType = 'application/vnd.google-apps.folder'"

    print(f"Gdrive Api Query: '{q}'")
    while True:
        response = drive.files().list(q=q,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name, modifiedTime)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            folders.append(file)
            print(f"Found file {file.get('name')} : {file.get('id')}")
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return folders

def construct_drive_query(parent_folder_id, modified_since=None):
    '''query for files in parent_folder modified after modified_since'''

    q= f"'{parent_folder_id}' in parents"

    if not modified_since: return q

    if isinstance(modified_since, str):
        start_time = modified_since
    else:
        start_time = modified_since.strftime('%Y-%m-%dT%H:%M:%S')

    q_time =f"modifiedTime > '{start_time}'"

    q = f'{q} and {q_time}'
    print('GDrive query:', q)
    return q


def get_files(query, drive):
    '''
    retrieve files in folder which have been modified since last_sync
    '''

    page_token = None
    files =[]

    while True:
        response = drive.files().list(q=query,
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


GdriveFile = namedtuple('GdriveFile',['name', 'content'])

def download_new_drive_files(folder, drive):
    ''' get a list of unsynced drive files
    Args:
        user object: requires google_creds and optionally last_gdrive_sync attributes
    Returns:
        files: list containing tuples of (file_name, BytesIO of file content)
   '''

    query = construct_drive_query(folder['id'], folder['last_sync'])
    files = get_files(query, drive)

    files = [GdriveFile(name, content) for name, content in download(files,drive)]
    return files





def download(files, drive):
    """ download file from gdrive and return BytesIo object """
    for file in files:
        request = drive.files().get_media(fileId=file.get("id"))
        file_buff = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buff, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        yield (file.get('name'), file_buff)


