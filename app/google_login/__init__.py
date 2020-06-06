from flask import Blueprint

google_login = Blueprint('google_login', __name__)

from app.google_login import routes
