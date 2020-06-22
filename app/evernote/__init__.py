from flask import Blueprint
from app.evernote import evernote_patch
evernote = Blueprint('evernote', __name__)

from app.evernote import routes



