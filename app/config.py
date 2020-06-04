import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'fdsgdfgsdfgdfsgdsfgewrgr44534rtergsdfv'
    SQLALCHEMY_DATABASE_URI = "postgresql:///tagger_dev"
    DATABASE_URI = "postgresql:///tagger_dev"
    SSL_CONTEXT="adhoc"

#TODO: MOVE ALL CONFIG TO ENVIROMENT