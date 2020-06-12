from datetime import datetime

from flask import  redirect, url_for, session, jsonify

from googleapiclient.discovery import build
import google
import googleapiclient

from flask_login import login_required, current_user
from app.gdrive import google_auth
# from .sync_gdrive_folder import sync_google_drive

from app.gdrive import gdrive
from app import db


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


# @gdrive.route('/sync_drive')
# @login_required
# def sync_drive():
#     last_sync = current_user.last_gdrive_sync
#     print(f'Last Sync: {last_sync}')
#     try:
#         sync_google_drive(current_user.google_creds, last_sync)
#     except AttributeError:
#         pass
#     current_user.last_gdrive_sync = datetime.utcnow()
#     db.session.commit()
#     return redirect(url_for('main.index'))

@gdrive.route('/test')
@login_required
def test_api_request():
    print("/test route")
    print(current_user.google_creds)
    if current_user.google_creds is None:
        return redirect('gdrive.authorize')

# Load credentials from the db.
    credentials = google.oauth2.credentials.Credentials(
      **current_user.google_creds)

    drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    files = drive.files().list().execute()

# Save credentials back to db in case access token was refreshed.
    current_user.google_creds = credentials
    return jsonify(**files)


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
        print(revoke)
        return('An error occurred.')
