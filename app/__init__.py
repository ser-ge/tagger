from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

from app.config import Config
load_dotenv()


db = SQLAlchemy()
login = LoginManager()


def create_app():
    build_dir = '/Users/serge/projects/neonotes/tagger-frontend/build/'
    app = Flask(__name__,static_folder=build_dir, static_url_path='/')
    app.config.from_object(Config)

    db.init_app(app)
    login.init_app(app)

    from app.main import main
    app.register_blueprint(main)

    from app.google_login import google_login
    app.register_blueprint(google_login)

    from app.gdrive import gdrive
    app.register_blueprint(gdrive)

    from app.evernote import evernote
    app.register_blueprint(evernote)

    return app
