from . import BaseConfig
import os

class DevelopmentConfig(BaseConfig):
    try:
        import config.dev as dev_config  # config/dev.py # noqa: F811
    except ModuleNotFoundError:
        raise EnvironmentError("Please create config/dev.py")

    APP_SECRET_KEY = "somekey"
    SECRET_KEY = "somekey"
    DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/donor_app')

    PROPAGATE_EXCEPTIONS = True
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PORT = dev_config.PORT
    DEBUG = True
    LOGGING_ON = True
    PRINTLOG = True
    NOTIFICATIONS_ON = True

    MAIL_USERNAME = dev_config.MAIL_USERNAME
    MAIL_PASSWORD = dev_config.MAIL_PASSWORD
    MAIL_SERVER = dev_config.MAIL_SERVER
    MAIL_PORT = dev_config.MAIL_PORT
    CATCH_ALL_EMAIL_ADDRESS = dev_config.CATCH_ALL_EMAIL_ADDRESS
    INVOICE_EMAIL_ADDRESS = dev_config.INVOICE_EMAIL_ADDRESS


    MAIL_DEFAULT_SENDER = dev_config.MAIL_DEFAULT_SENDER
    MAIL_SUBJECT_PREFIX = dev_config.MAIL_SUBJECT_PREFIX
    MAIL_SENDER = dev_config.MAIL_SENDER
