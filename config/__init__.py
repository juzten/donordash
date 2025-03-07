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

    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        # Render uses postgres://, but SQLAlchemy expects postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback database URI
        SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/donordash'
        config.DEBUG = False

    APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "default_dev_key_not_for_production")

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
    DEBUG = True
    LOGGING_ON = True
    PRINTLOG = True
    NOTIFICATIONS_ON = True

    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False

    USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
    USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
    USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
    USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
    USER_ENABLE_EMAIL = True  # Register with Email
    USER_ENABLE_REGISTRATION = True  # Allow new users to register
    USER_ENABLE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
    USER_ENABLE_USERNAME = True  # Register and Login with username
    USER_ENABLE_INVITATION = True
    USER_REQUIRE_INVITATION = True



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
