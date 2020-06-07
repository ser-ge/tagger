from flask import Flask, redirect, request, url_for, session, jsonify, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
import json
import os
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import requests


from app.models import User
from app import db

from app.main import main



# @main.route("/")
# def index():
#     if current_user.is_authenticated:
#         return (
#            f"<p>Hello, {current_user.name}! You're logged in! Email: {current_user.email}</p>"
#             "<div><p>Google Profile Picture:</p>"
#             '<a class="button" href="/logout">Logout </a>'
#             '<a class="button" href="/test">GDrive </a>'
#             '<a class="button" href="/revoke">Revoke Google Creds </a>'
#             '<a class="button" href="/sync_drive">Sync Drive </a>'
#             '<div><a class="button" href="/get_evernote_tags"> All tags </a> </div>'
#         )
#     else:
#         return '<a class="button" href="/login">Google Login</a>'

@main.route("/")
def index():
    return current_app.send_static_file('index.html')

@main.route("/user")
def user():
    if current_user.is_authenticated:
        name = current_user.name
        print(name)
    else:
        name = 'User not Logged in'

    return jsonify({'name': current_user.name})
