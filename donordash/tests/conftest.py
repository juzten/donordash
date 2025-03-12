import os

import pytest

from donordash import create_app, db


@pytest.fixture(scope="session")
def test_app():
    # Set up the app for testing
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:password@postgres:5432/donor_app_test",
            "UPLOAD_FOLDER": "/tmp",
            "APPLICATION_ROOT": "/",
        }
    )

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Database is created but tables aren't - we'll do that in a separate fixture
    yield app


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client for the app."""
    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()
