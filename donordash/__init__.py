# -*- coding: utf-8 -*-

import logging
import os
import warnings

import requests.packages.urllib3
from flask import Flask
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect

from config import config

warnings.filterwarnings("ignore", category=DeprecationWarning)

requests.packages.urllib3.disable_warnings()

app = Flask(__name__,
          template_folder='templates',  # Make sure this path is correct
          static_folder='static')
app.secret_key = config.APP_SECRET_KEY
app.config["SECRET_KEY"] = config.APP_SECRET_KEY
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.debug = config.DEBUG

app.config["MAIL_USERNAME"] = config.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = config.MAIL_PASSWORD
app.config["MAIL_DEFAULT_SENDER"] = config.MAIL_DEFAULT_SENDER
app.config["MAIL_SERVER"] = config.MAIL_SERVER
app.config["MAIL_PORT"] = config.MAIL_PORT

app.config["USER_ENABLE_CHANGE_PASSWORD"] = config.USER_ENABLE_CHANGE_PASSWORD
app.config["USER_ENABLE_CHANGE_USERNAME"] = config.USER_ENABLE_CHANGE_USERNAME
app.config["USER_ENABLE_CONFIRM_EMAIL"] = config.USER_ENABLE_CONFIRM_EMAIL
app.config["USER_ENABLE_FORGOT_PASSWORD"] = config.USER_ENABLE_FORGOT_PASSWORD
app.config["USER_ENABLE_EMAIL"] = config.USER_ENABLE_EMAIL
app.config["USER_ENABLE_REGISTRATION"] = config.USER_ENABLE_REGISTRATION
app.config["USER_ENABLE_RETYPE_PASSWORD"] = config.USER_ENABLE_RETYPE_PASSWORD
app.config["USER_ENABLE_USERNAME"] = config.USER_ENABLE_USERNAME
app.config["USER_ENABLE_INVITATION"] = USER_ENABLE_INVITATION = True
app.config["USER_REQUIRE_INVITATION"] = USER_REQUIRE_INVITATION = True
app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["USER_AFTER_LOGIN_ENDPOINT"] = "AdminView:index"
# app.config['USER_SEND_REGISTERED_EMAIL'] = config.USER_SEND_REGISTERED_EMAIL
app.config["UPLOAD_FOLDER"] = os.getcwd() + "/uploads"

if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


# Uploads settings
app.config["UPLOADED_FILE_DEST"] = os.getcwd() + "/uploads"

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
mail = Mail(app)
# ma = Marshmallow(app)
# enable CORS
CORS(app)

if not app.debug:
    logging.basicConfig(
        filename="error.log", level=logging.INFO, format="%(asctime)s %(message)s"
    )
else:
    toolbar = DebugToolbarExtension(app)
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

# custom jinja line delimeters
app.jinja_env.line_statement_prefix = "%"
app.jinja_env.line_comment_prefix = "##"

# register views
from donordash.views import init_views  # noqa: E402

init_views(app)
