# -*- coding: utf-8 -*-

import os
import config
from donordash.errors import ConfigVarNotFoundError

"""Set up config variables."""


class BaseConfig(object):
    USER_APP_NAME = "donordash"
    APP_NAME = "donordash"

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
    # USER_SEND_REGISTERED_EMAIL
    UPLOAD_FOLDER = os.getcwd() + "/uploads"
    UPLOADED_FILE_DEST = os.getcwd() + "/uploads"
