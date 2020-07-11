import os
from datetime import datetime
from io import BytesIO

import pytest

from app import create_app, db
from app.models import User
from app.note_writter import NoteRepo, OrgStore
from app.schemas import File
from app.note import Reader
from app.main.tasks import drive_to_org

from app.gdrive.drive_folder import DriveFolder



@pytest.fixture
def app():
    from app import create_app
    app = create_app(testing=True)
    return app

@pytest.fixture()
def test_client(app):

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture
def credentials(user):
    return [('Authentication', user.get_auth_token())]

@pytest.fixture
def user(app):
    app = create_app()
    with app.app_context():
        yield User.query.first()

# @pytest.fixture
# def user(db):
#     user = db.session.query(User).first()

@pytest.fixture
def evernote_token():
    token = os.getenv('EVERNOTE_TOKEN')
    return token

def test_evernote_repo(evernote_token):
    note_repo = NoteRepo(evernote_token)
    print(note_repo.tags)
    assert len(note_repo.tags) > 0

@pytest.fixture
def file():

    f = open('test_file.pdf', 'rb')

    file_content = BytesIO(f.read())

    file = File(
            source_id='12345',
            name='test_file.pdf',
            modifiedTime=datetime.utcnow(),
            mimeType='application/pdf',
            source='local',
            content=file_content,
            )

    yield file

    f.close()


def test_reader(file):

    target_tags = ['reporting', 'work', 'gym', 'place']
    reader = Reader(target_tags)

    note = reader.parse(file)

    assert note.tags == ['reporting']



def test_drive_folder(user):
    new_files = DriveFolder(
            credentials=user.google_creds,
            folder_name='CamScanner'
            )

    files_list = new_files.list_files()

    print(files_list)

    names = [file.name for file in files_list]

    assert 'hake.pdf' in names



def test_org_store(file):

    target_tags = ['reporting', 'work', 'gym', 'place']
    reader = Reader(target_tags)

    note = reader.parse(file)
    store = OrgStore('/Users/serge/Dropbox/org/', 'notes.org')
    store.create(note)


def test_drive_to_org(user):
    print(f'user: {user}')
    drive_to_org(user)
    assert False

# TODO NEXT FIX drive to org




