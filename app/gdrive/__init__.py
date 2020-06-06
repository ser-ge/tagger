from flask import Blueprint

gdrive  = Blueprint('gdrive', __name__)

from app.gdrive import routes
