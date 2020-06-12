from app import db, login
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
import json
from app.gdrive.google_auth import credentials_to_json


class User(UserMixin,db.Model):

    user_id = db.Column(db.String(), primary_key=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    google_creds_json = db.Column(JSON, nullable=True)
    last_gdrive_sync = db.Column(db.DateTime, nullable=True)
    evernote_token = db.Column(db.String)
    tags = db.relationship('Tag', backref=db.backref('user'))
    test_field = db.Column(db.String(120), index=True, unique=True)

    @property
    def google_creds(self):
        return json.loads(self.google_creds_json)

    @google_creds.setter
    def google_creds(self, creds):
        self.google_creds_json = credentials_to_json(creds)

    @google_creds.deleter
    def google_creds(self):
        del self.google_creds_json


    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<id {self.id} Name {self.first_name} {self.last_name}>'

class Tag(db.Model):

    tag_id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.String(), nullable=False)
    user_id = db.relationship(db.String, db.ForeignKey('public.user.user_id'))

    def __str__(self):
        return self.text



@login.user_loader
def load_user(id):
    return User.query.get(id)


