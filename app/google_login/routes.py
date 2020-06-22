import os
import json
import requests
from flask import Blueprint, redirect, request, url_for, session, jsonify
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from oauthlib.oauth2 import WebApplicationClient

from app.models import User
from app import db

from app.google_login import google_login


#GOOGLE CONFIG
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


client = WebApplicationClient(GOOGLE_CLIENT_ID)

@google_login.route("/login")
def login():
    # Find out what URL to hit for Google login

    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        access_type='offline',
        redirect_uri=url_for("google_login.callback", _external=True),
        #redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@google_login.route("/login/callback")
def callback():
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
        user_id=unique_id, name=users_name, email=users_email,
    )



    # Doesn't exist? Add it to the database.
    if not User.query.get(unique_id):
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("main.index"))

@google_login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))



#retrieve Google provider config - add error handling
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


