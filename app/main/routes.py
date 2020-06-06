from flask import Flask, redirect, request, url_for, session, jsonify, Blueprint
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



@main.route("/")
def index():
    if current_user.is_authenticated:
        return (
           f"<p>Hello, {current_user.name}! You're logged in! Email: {current_user.email}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<a class="button" href="/logout">Logout </a>'
            '<a class="button" href="/test">GDrive </a>'
            '<a class="button" href="/revoke">Revoke Google Creds </a>'
            '<a class="button" href="/drive">Drive </a>'
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


if __name__ == '__main__':
    app.run(ssl_context="adhoc")
