import os
from datetime import datetime
from typing import Iterable


from flask_login import current_user

from app import db
from app import celery
from app.models import User, Tag

from app.evernote.utils import build_evernote_store, get_evernote_tags
from app.note import Note

from app.adapters import DriveFolder, File

def sync_evernote_tags(user_id):
    user = User.query.get(user_id)
    ever_tags = get_evernote_tags(user)
    user_tags = [tag.text for tag in user.tags]
    new_tags = [Tag(text=tag) for tag in ever_tags if tag  not in user_tags]
    user.tags += new_tags
    db.session.commit()


@celery.task(name='sync_drive_to_evernote')
def sync_drive_to_evernote(user_id: str):

    user = User.query.get(user_id)

    target_tags = [str(tag) for tag in user.tags]
    note_store = build_evernote_store(user)

    new_files: Iterable[File] = DriveFolder(user.google_creds, user.gdrive_folder_id, user.last_gdrive_sync)


    for file in new_files:
        note = Note(file, target_tags)
        note.to_evernote(note_store)
        file.content.close()

    # save credentials from gdrive call in case they were refreshed
    user.google_creds = new_files._returned_credentials

    user.last_gdrive_sync = datetime.utcnow()
    db.session.commit()

@celery.task(bind=True,name='sync_all_users')
def sync_all_users(self):
    users = db.session.query(User).all()
    n = len(users)
    for i, user in enumerate(users):
        sync_evernote_tags(user.user_id)
        sync_drive_to_evernote(user.user_id)
        message = f"{i} of {n} users synced"
        print(message)







