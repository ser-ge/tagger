from app import db
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin



class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(), primary_key=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)



    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<id {self.id} Name {self.first_name} {self.last_name}>'





