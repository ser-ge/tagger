from flask import Flask, redirect, request, url_for, session, jsonify, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime
from flask_login import (
    current_user,
    login_required,
)
import requests


from app.models import User
from app import db
from app.main import main
from app.main.tasks import sync_drive_to_evernote


@main.route("/")
def index():
    print(session)
    print(current_user.google_creds)
    return current_app.send_static_file('index.html')

@main.route("/user")
@login_required
def user():
    return jsonify(current_user.__dict__)


@main.route("/sync")
def schedule_sync():
    sync_drive_to_evernote.delay(current_user.user_id)
    return jsonify({'status': "IN PROGRESS"})

