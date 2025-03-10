# -*- coding: utf-8 -*-

import os
import config
from donordash.errors import ConfigVarNotFoundError

"""Set up config variables.

If environment variable APP_SETTINGS is set to dev and the config/dev.py
file exists then use that file as config settings, otherwise pull in settings from the production environment
"""

if os.environ.get("ENVIRONMENT") == "dev":
    try:
        import config.dev as config  # config/dev.py
    except:
        raise EnvironmentError("Please create config/dev.py")
elif os.environ.get('CI') == 'true':
    try:
        import config.ci as config  # config/ci.py
    except:
        raise EnvironmentError("Please create config/ci.py")
else:
    # production server environment variables
    # import config.prod as config  # config/prod.py

    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    print(f"Original DATABASE_URL: {database_url}")  # Debug output

    # Render provides Postgres URLs starting with postgres://, but SQLAlchemy
    # needs postgresql://, so we need to replace the protocol
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"Modified DATABASE_URL: {database_url}")  # Debug output

    config.database_url = database_url
    config.DATABASE_URI = database_url
    config.SQLALCHEMY_DATABASE_URI = database_url
    print(f"Final config.SQLALCHEMY_DATABASE_URI: {config.SQLALCHEMY_DATABASE_URI}")  # Debug output

    config.APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "default_dev_key_not_for_production")

    # Mail configuration
    config.MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    config.MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    config.MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    config.MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    config.CATCH_ALL_EMAIL_ADDRESS = os.environ.get("CATCH_ALL_EMAIL_ADDRESS", "")
    config.INVOICE_EMAIL_ADDRESS = os.environ.get("INVOICE_EMAIL_ADDRESS", "")
    config.MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
    config.MAIL_SUBJECT_PREFIX = os.environ.get("MAIL_SUBJECT_PREFIX", "Donor Dash")
    config.MAIL_SENDER = os.environ.get("MAIL_SENDER", "")

    config.PORT = 5000
    config.DEBUG = True
    config.FLASK_DEBUG=1
    config.LOGGING_ON = True
    config.PRINTLOG = True
    config.NOTIFICATIONS_ON = True

    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False

    config.USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
    config.USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
    config.USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
    config.USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
    config.USER_ENABLE_EMAIL = True  # Register with Email
    config.USER_ENABLE_REGISTRATION = True  # Allow new users to register
    config.USER_ENABLE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
    config.USER_ENABLE_USERNAME = True  # Register and Login with username
    config.USER_ENABLE_INVITATION = True
    config.USER_REQUIRE_INVITATION = True



config.USER_APP_NAME = "donordash"
config.APP_NAME = "donordash"

required_config_vars = [config.APP_SECRET_KEY, config.DEBUG, config.PORT]

try:
    any(required_config_vars) is None
except Exception as e:
    missing_var = e.message.split()[-1]
    raise ConfigVarNotFoundError(missing_var)


class BaseConfig(object):
    """Base configuration."""

    SECRET_KEY = "my_precious"
    DEBUG = False


class TestingConfig(BaseConfig):
    """Testing configuration."""

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    TESTING = True
    SECRET_KEY = "my_precious"
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
