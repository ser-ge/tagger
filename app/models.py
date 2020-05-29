from app import db
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin

from app import login

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)


    def __init__(self, url, result_all, result_no_stop_words):
        self.username = username
        self.email = email

    def __repr__(self):
        return f'<id {self.id} Name {self.first_name} {self.last_name}>'






@login.user_loader
def load_user(id):
    return User.query.get(int(id))