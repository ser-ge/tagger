from app import create_app, db
from app.models import User

app = create_app()

def user():
    with app.app_context():
        user = User.query.first()
        print(user.google_creds_json)

