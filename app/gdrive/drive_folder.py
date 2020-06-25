from io import BytesIO

import google
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.schemas import File, Files

API_SERVICE_NAME = "drive"
API_VERSION = "v3"





class DriveFolder:

    def __init__(self, credentials, folder_id, modified_since=None):

        self.filters = {
            "mime_types": ["image/jpeg", "image/png", "image/jpg", "application/pdf"],
            "modified_since": modified_since,
        }

        self.credentials = credentials
        self.folder_id = folder_id

        self._intialise_drive_folder()

    def _intialise_drive_folder(self):
        self.drive, self._returned_credentials = build_drive_service(self.credentials)
        query = construct_drive_query(self.folder_id, self.filters)
        drive_files = get_drive_files_metadata(query, self.drive)

        self.files_dict = {file['id'] : File(**file) for file in drive_files}


    def get_file(self, file_id):
        file = self.files_dict[file_id]

        if file.content is None:
            file.content = download_drive_file(file.id, self.drive)
            self.files_dict[file_id] = file

        return file

    def get_files(self, file_ids):
        files = [self.get_file(id) for id in file_ids]
        return files

    def list_files(self) -> Files:
        return Files.parse_obj(list(self.files_dict.values()))

    def __iter__(self):
        for file in self.files_dict.values():
            yield self.get_file(file.id)



def build_drive_service(credentials):
    credentials = google.oauth2.credentials.Credentials(**credentials)
    drive = build(
        API_SERVICE_NAME, API_VERSION, cache_discovery=False, credentials=credentials
    )
    return drive, credentials


def download_drive_file(file_id, drive):
    """ download file from gdrive and return BytesIo object """
    request = drive.files().get_media(fileId=file_id)
    file_buff = BytesIO()
    downloader = MediaIoBaseDownload(file_buff, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return file_buff

def construct_drive_query(parent_folder_id, filters):
    #TODO refactor

    q = f"'{parent_folder_id}' in parents"
    q+= " and "

    mimes = []
    for mime_type in filters["mime_types"]:
        mime =  f"mimeType = '{mime_type}'"
        mimes.append(mime)
    q +="("
    q += " or ".join(mimes)
    q += ")"

    if filters["modified_since"] is not None:
        time = filters["modified_since"]
        modified_time = time.strftime("%Y-%m-%dT%H:%M:%S")
        q += " and "
        q += f"modifiedTime > '{modified_time}'"

    print("GDrive query:", q)
    return q


def get_drive_files_metadata(query, drive):
    page_token = None
    files = []

    while True:
        response = (
            drive.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, modifiedTime, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )

        for file in response.get("files", []):
            # Process change
            files.append(file)
            print(f"Found file {file.get('name')} : {file.get('id')}")
        page_token = response.get("nextPageToken", None)

        if page_token is None:
            break


    return files


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


