import pytest

from donordash import app, db


@pytest.fixture(scope="session")
def test_app():
    # Set up the app for testing
    app.config.update(
        {
            "TESTING": True,
            # 'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL')
            "SQLALCHEMY_DATABASE_URI": "donor_app_test",
        }
    )

    # Create all tables
    with app.app_context():
        db.create_all()

    yield app

    # Tear down
    with app.app_context():
        db.session.remove()
        db.drop_all()
