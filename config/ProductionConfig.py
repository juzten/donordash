from . import BaseConfig
import os

class ProductionConfig(BaseConfig):
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')

    # Render provides Postgres URLs starting with postgres://, but SQLAlchemy
    # needs postgresql://, so we need to replace the protocol
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    DATABASE_URI = database_url
    SQLALCHEMY_DATABASE_URI = database_url

    APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")

    # Mail configuration
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    CATCH_ALL_EMAIL_ADDRESS = os.environ.get("CATCH_ALL_EMAIL_ADDRESS", "")
    INVOICE_EMAIL_ADDRESS = os.environ.get("INVOICE_EMAIL_ADDRESS", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
    MAIL_SUBJECT_PREFIX = os.environ.get("MAIL_SUBJECT_PREFIX", "Donor Dash")
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "")

    PORT = 5000
    DEBUG = False
    FLASK_DEBUG = False
    LOGGING_ON = True
    PRINTLOG = True
    NOTIFICATIONS_ON = True
