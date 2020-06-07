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

from evernote.api.client import EvernoteClient
import evernote_patch

from app.models import User
from app import db

from app.evernote import evernote



@evernote.route("/get_evernote_tags")
@login_required
def get_evernote_tags():
    token = os.getenv('EVERNOTE_TOKEN')
    client = EvernoteClient(token=token, sandbox=False, china=False)
    note_store = client.get_note_store()
    tags = note_store.listTags()
    tags = [tag.name for tag in tags]
    return jsonify(tags)
