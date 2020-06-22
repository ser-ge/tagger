from app import db, create_app
from app.models import User
from app.gdrive import DriveFolder, File






test_file ={'id': '1', 'modifiedTime' : '2012-06-04T12:00:00', 'name':'my.jpeg', 'mimeType':'image/jpeg'}



if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        user = User.query.first()


