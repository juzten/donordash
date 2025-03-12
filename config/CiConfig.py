from . import BaseConfig
import os

class CiConfig(BaseConfig):
    APP_SECRET_KEY = "asdfdsafdsafdsfa"
    DATABASE_URI = 'postgresql://postgres:password@postgres:5432/donor_app_test'
    DISABLE_CSRF = True
    LOG_LEVEL = 'INFO'
    PORT = 5000
    DEBUG = False
    TESTING = True
    LOGGING_ON = True
    PRINTLOG = True
    NOTIFICATIONS_ON = True

    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_SERVER = "smtp.mailgun.org"
    MAIL_PORT = 587
    CATCH_ALL_EMAIL_ADDRESS = ""
    INVOICE_EMAIL_ADDRESS = ""
    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = "Donor Dash <juzten+donordash@gmail.com>"
    MAIL_SUBJECT_PREFIX = "Donor Dash"
    MAIL_SENDER = "Donor Dash <juzten+donordash@gmail.com>"

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
