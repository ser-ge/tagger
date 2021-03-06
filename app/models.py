from app import db, login
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
import json
# from app.gdrive.google_auth import credentials_to_json


class User(UserMixin,db.Model):

    user_id = db.Column(db.String(), primary_key=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    google_creds_json = db.Column(JSON, nullable=True)
    last_gdrive_sync = db.Column(db.DateTime, nullable=True)
    evernote_token = db.Column(db.String)
    tags = db.relationship('Tag', back_populates='user')
    test_field = db.Column(db.String(120), index=True, unique=True)

    # def __init__(self, user_id, name, email):
    #     self.user_id = user_id
    #     self.name = name
    #     self.email = email


    @property
    def google_creds(self):
        return json.loads(self.google_creds_json)

    @google_creds.setter
    def google_creds(self, creds):
        self.google_creds_json = credentials_to_json(creds)

    @google_creds.deleter
    def google_creds(self):
        del self.google_creds_json

    @property
    def gdrive_folder_id(self): #TODO store in db once folder selction flow works

        TARGET_FOLDER = '14XoumtXaKPkcTUIxp-gZDyJUgnAcXjfg'
        return TARGET_FOLDER

    @property
    def last_sync(self):
        return self.last_gdrive_sync.strftime('%Y-%m-%dT%H:%M:%S')

    def __repr__(self):
        return f'<id {self.user_id} Name {self.first_name} {self.last_name}>'

class Tag(db.Model):

    tag_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    text = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'),primary_key=True)
    user = db.relationship('User', back_populates='tags')

    def __str__(self):
        return self.text



@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def credentials_to_json(credentials):
    creds = {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
    return json.dumps(creds)
