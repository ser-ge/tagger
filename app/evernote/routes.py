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
from app.evernote import evernote_patch

from app.evernote.utils import get_evernote_tags
from app import db
from app.models import Tag
from app.evernote import evernote


@evernote.route("/get_evernote_tags")
@login_required
def get_evernote_tags():
    '''Retrieve all tags in evernote and add to DB'''

    ever_tags = get_evernote_tags(current_user)
    user_tags = [tag.text for tag in current_user.tags]

    new_tags = [Tag(text=tag) for tag in ever_tags if tag  not in user_tags]

    current_user.tags += new_tags
    db.session.commit()
    return jsonify([str(tag) for tag in current_user.tags])

