from datetime import datetime

from flask import  redirect, url_for, session, jsonify

from googleapiclient.discovery import build
import google
import googleapiclient

from flask_login import login_required, current_user
from app.gdrive import google_auth

from app.gdrive import gdrive

from app import db
from app.gdrive.drive_folder import DriveFolder
from app.models import User
from app.schemas import File, Files

DRIVE_SCOPES =["https://www.googleapis.com/auth/drive"]
LOGIN_SCOPES = ["https://www.googleapis.com/auth/userinfo.profile",  "openid", "https://www.googleapis.com/auth/userinfo.email"]
ALL_SCOPES = DRIVE_SCOPES + LOGIN_SCOPES

API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'



@gdrive.route('/auth_gdrive')
@login_required
def auth_gdrive():
  authorization_url, state = google_auth.get_auth_url(ALL_SCOPES,'gdrive.auth_gdrive_callback')
  session['state'] = state
  return redirect(authorization_url)

@gdrive.route('/auth_gdrive/callback')
@login_required
def auth_gdrive_callback():
  state = session['state']
  credentials =  google_auth.get_credentials(state, 'gdrive.auth_gdrive_callback' , ALL_SCOPES)
  current_user.google_creds = credentials
  db.session.commit()
  return redirect(url_for('gdrive.test_api_request'))

# @gdrive.route('/get_gdrive_folders')
# @login_required
# def get_gdrive_folders():
#     folders = get_drive_folders(user)
#     folders_dict = {folder['name']:folder['id'] for folder in folders}
#     return jsonify(folders_dict)



@gdrive.route('/test')
def test_api_request():

    user = User.query.first()

    folder  = DriveFolder(user.google_creds, user.gdrive_folder_id)
    files: Files = folder.list_files()

    return files.json(by_alias=True)


@gdrive.route('/revoke')
@login_required
def revoke():
    print(current_user.google_creds)
    if current_user.google_creds is None:
        return "No creds to revoke"

    credentials = google.oauth2.credentials.Credentials(
      **current_user.google_creds)
    revoke = requests.post('https://oauth2.googleapis.com/revoke',
    params={'token': credentials.token},
    headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')

    if status_code == 200:
        return('Credentials successfully revoked.')
    else:
        return('An error occurred.')
