from flask import Flask, redirect, request, url_for, session, jsonify, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import requests


from app.models import User
from app import db
from app import celery as cl
from app.main import main
from app.gdrive.sync_gdrive_folder import get_new_drive_files
from app.note import Note
from app.evernote.evernote_utils import make_note_store


# @main.route("/")
# def index():
#     if current_user.is_authenticated:
#         return (
#            f"<p>Hello, {current_user.name}! You're logged in! Email: {current_user.email}</p>"
#             "<div><p>Google Profile Picture:</p>"
#             '<a class="button" href="/logout">Logout </a>'
#             '<a class="button" href="/test">GDrive </a>'
#             '<a class="button" href="/revoke">Revoke Google Creds </a>'
#             '<a class="button" href="/sync_drive">Sync Drive </a>'
#             '<div><a class="button" href="/get_evernote_tags"> All tags </a> </div>'
#         )
#     else:
#         return '<a class="button" href="/login">Google Login</a>'

@main.route("/")
def index():
    return current_app.send_static_file('index.html')

@main.route("/user")
def user():
    if current_user.is_authenticated:
        name = current_user.name
        print(name)
    else:
        name = 'User not Logged in'

    return jsonify({'name': current_user.name})

@main.route("/sync")
def schedule_sync():

    u = current_user
    target_tags = [str(tag) for tag in current_user.tags]
    evernote_token = os.getenv('EVERNOTE_TOKEN')
    # sync.delay(u.google_creds, evernote_token, u.last_gdrive_sync, target_tags)
    sync(u.google_creds, evernote_token, u.last_gdrive_sync, target_tags)
    u.last_gdrive_sync = datetime.utcnow()
    db.session.commit()
    return jsonify({'status': "Success"})

# @cl.task(bind=True)
def sync(google_creds, evernote_token, last_gdrive_sync, target_tags):
    files = get_new_drive_files(google_creds, last_gdrive_sync)
    if len(files) == 0: return {'status': 'Done', 'message':'no new files to sync'}
    print(files)
    note_store = make_note_store(evernote_token)
    notes = [Note(f[0], f[1], target_tags) for f in files]
    for note in notes:
        try:
        # self.update_state(state='PROGRESS',
        #         meta:{'current': i, 'total': len(notes)})
            note.to_evernote(note_store)

        except Exception as e:
            print(f'{note.path} failed with exception:')
            print(e)

    return {'status': 'Done!'}


