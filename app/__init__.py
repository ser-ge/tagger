from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from celery import Celery
import redis
from app.config import TestConfig, DevConfig
load_dotenv()



redis_uri = "redis://localhost:6379" # TODO Move Celery Config!
celery = Celery(__name__, backend=redis_uri, broker=redis_uri)
db = SQLAlchemy()
login = LoginManager()


def create_app(testing=False):
    # TODO move to config!
    build_dir = '/Users/serge/projects/neonotes/tagger-frontend/build/'
    app = Flask(__name__,static_folder=build_dir, static_url_path='/')
    config = TestConfig if testing else DevConfig
    app.config.from_object(config)

    db.init_app(app)
    login.init_app(app)

    init_celery(app)
    from app.main import main
    app.register_blueprint(main)

    from app.google_login import google_login
    app.register_blueprint(google_login)

    from app.gdrive import gdrive
    app.register_blueprint(gdrive)

    from app.evernote import evernote
    app.register_blueprint(evernote)

    return app

def init_celery(app=None):
    app = app or create_app()

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
