import pytest

@pytest.fixture
def app():
    from app import create_app
    app = create_app(testing=True)
    return app

@pytest.fixture(scope='module')
def test_client(app):

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture
def credentials(user):
    return [('Authentication', user.get_auth_token())]

@pytest.fixture
def db(app):
    app = create_app()
    from app import db
    with app.app_context:
        yield db
        db.session.commit()
        db.session.remove()

@pytest.fixture
def user(db):
    user = db.session.query(User).first()


