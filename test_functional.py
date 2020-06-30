import os
from app.note_writter import NoteRepo
import pytest
from datetime import datetime

from app.note_writter import NoteRepo
from app.schemas import File
from app.note import Reader
from io import BytesIO

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
def db(app):
    app = create_app()
    from app import db
    with app.app_context:
        yield db
        db.session.commit()
        db.session.remove()

@pytest.fixture
def user(db):
    user = db.session.query(User).first()

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

