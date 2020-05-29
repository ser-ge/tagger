import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '\xadv\x14\x9b@nL??\\\xcdF\x1f3\x0c\xa4{F!\xa8\xebctb'
    SQLALCHEMY_DATABASE_URI = "postgresql:///tagger_dev"
    DATABASE_URI = "postgresql:///tagger_dev"
    SSL_CONTEXT="adhoc"

#TODO: MOVE ALL CONFIG TO ENVIROMENT