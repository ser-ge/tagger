import os
from datetime import datetime


from flask_login import current_user

from app import db
from app import celery
from app.models import User, Tag

from app.evernote.utils import build_evernote_store, get_evernote_tags
from app.gdrive.utils import download_new_drive_files, build_drive_service
from app.note import Note


def sync_evernote_tags(user_id):
    user = User.query.get(user_id)
    ever_tags = get_evernote_tags(user)
    user_tags = [tag.text for tag in user.tags]
    new_tags = [Tag(text=tag) for tag in ever_tags if tag  not in user_tags]
    user.tags += new_tags
    db.session.commit()


def send_notes_to_evernote(notes, note_store):
    for note in notes:
        try:
            note.to_evernote(note_store)
        except Exception as e:
            print(f'{note.path} failed with exception: {e}')

def notes_from_gdrive_files(gdrive_files, target_tags):
    notes = [Note(f.name, f.content, target_tags) for f in gdrive_files]
    return notes

from app.adapters import DriveFolder

@celery.task(name='sync_drive_to_evernote')
def sync_drive_to_evernote(user_id):

    user = User.query.get(user_id)

    target_tags = [str(tag) for tag in user.tags]
    note_store = build_evernote_store(user)
    new_files = DriveFolder(user.google_creds, user.gdrive_folder_id, user.last_gdrive_sync)
    user.google_creds = new_files.returned_credentials

    for file in new_files:
        note = Note(file.name, file.content, target_tags)
        note.to_evernote(note_store)

    user.last_gdrive_sync = datetime.utcnow()
    db.session.commit()

# @celery.task(name='sync_drive_to_evernote')
# def sync_drive_to_evernote(user_id):

#     user = User.query.get(user_id)
#     target_tags = [str(tag) for tag in user.tags]
#     folder = {'id' : user.gdrive_folder_id, 'last_sync':user.last_sync}

#     drive = build_drive_service(user)
#     gdrive_files = download_new_drive_files(folder, drive)

#     if not gdrive_files: return {'status': 'Done', 'message':'no new files to sync'}

#     notes = notes_from_gdrive_files(gdrive_files, target_tags)

#     note_store = build_evernote_store(user)

#     send_notes_to_evernote(notes, note_store)

#     user.last_gdrive_sync = datetime.utcnow()

#     db.session.commit()
#     return {'status': 'Done!'}

@celery.task(bind=True,name='sync_all_users')
def sync_all_users(self):
    users = db.session.query(User).all()
    n = len(users)
    for i, user in enumerate(users):
        sync_evernote_tags(user.user_id)
        sync_drive_to_evernote(user.user_id)
        message = f"{i} of {n} users synced"
        print(message)







