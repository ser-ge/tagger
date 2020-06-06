from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

from app.config import Config
load_dotenv()


db = SQLAlchemy()
login = LoginManager()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login.init_app(app)

    from app.main import main
    app.register_blueprint(main)

    from app.google_login import google_login
    app.register_blueprint(google_login)

    from app.gdrive import gdrive
    app.register_blueprint(gdrive)

    return app
