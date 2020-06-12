import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'fdsgdfgsdfgdfsgdsfgewrgr44534rtergsdfv'
    SQLALCHEMY_DATABASE_URI = "postgresql:///tagger_prod"
    DATABASE_URI = "postgresql:///tagger_prod"
    SSL_CONTEXT="adhoc"

    SQLALCHEMY_TRACK_MODIFICATIONS= False
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
#TODO: MOVE ALL CONFIG TO ENVIROMENT
