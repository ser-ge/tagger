from flask import Flask, redirect, request, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import os
from googleapiclient.discovery import build
import google
import googleapiclient
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from .config import Config


import google_auth
from .sync_gdrive_folder import sync_drive
#SET UP ENV
from dotenv import load_dotenv
load_dotenv()

DRIVE_SCOPES =["https://www.googleapis.com/auth/drive"]
LOGIN_SCOPES = ["https://www.googleapis.com/auth/userinfo.profile",  "openid", "https://www.googleapis.com/auth/userinfo.email"]
ALL_SCOPES = DRIVE_SCOPES + LOGIN_SCOPES
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'


app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#DB
db = SQLAlchemy(app)

#LOGIN SESSION MANAGER
login = LoginManager(app)
@login.user_loader
def load_user(id):
    return User.query.get(id)

#GOOGLE CONFIG
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

print(GOOGLE_CLIENT_ID)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


from .models import User

@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
           f"<p>Hello, {current_user.name}! You're logged in! Email: {current_user.email}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<a class="button" href="/logout">Logout </a>'
            '<a class="button" href="/auth_gdrive">GDrive </a>'
            '<a class="button" href="/revoke">Revoke Google Creds </a>'
            '<a class="button" href="/drive">Drive </a>'
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        access_type='offline',
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    creds = dict(token_response.json())
    print(creds)
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id=unique_id, name=users_name, email=users_email,
    )



    # Doesn't exist? Add it to the database.
    if not User.query.get(unique_id):
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route('/auth_gdrive')
@login_required
def auth_gdrive():
  authorization_url, state = google_auth.get_auth_url(ALL_SCOPES,'auth_gdrive_callback')
  session['state'] = state
  return redirect(authorization_url)

@app.route('/auth_gdrive/callback')
@login_required
def auth_gdrive_callback():
  state = session['state']
  credentials =  google_auth.get_credentials(state, 'auth_gdrive_callback' , ALL_SCOPES)
  current_user.google_creds = credentials
  db.session.commit()
  return redirect(url_for('test_api_request'))


@app.route('/drive')
@login_required
def drive():
    sync_drive(current_user.google_creds)
    return redirect(url_for('index'))

@app.route('/test')
@login_required
def test_api_request():
  if current_user.google_creds is None:
    return redirect('authorize')

  # Load credentials from the db.
  credentials = google.oauth2.credentials.Credentials(
      **current_user.google_creds)

  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  files = drive.files().list().execute()

  # Save credentials back to db in case access token was refreshed.
  current_user.google_creds = credentials
  return jsonify(**files)


@app.route('/revoke')
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))





#GOOGLE LOGIN UTILS

#retrieve Google provider config - add error handling
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == '__main__':
    app.run(ssl_context="adhoc")
