from flask import Blueprint

evernote = Blueprint('evernote', __name__)

from app.evernote import routes
