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
from dotenv import load_dotenv

# from flask_marshmallow import Marshmallow
from flask_wtf.csrf import CSRFProtect

from config import config

warnings.filterwarnings("ignore", category=DeprecationWarning)

requests.packages.urllib3.disable_warnings()

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()


def create_app(environment=None):
    app = Flask(
        __name__,
        template_folder="templates",  # Make sure this path is correct
        static_folder="static",
    )

    # set config
    load_dotenv()
    app_settings = environment if environment else os.getenv("APP_SETTINGS")

    if os.environ.get("ENVIRONMENT") == "dev":
        app_settings = "config.DevelopmentConfig.DevelopmentConfig"
    elif os.environ.get('ENVIRONMENT') == 'ci':
        app_settings = "config.CiConfig.CiConfig"
    elif os.environ.get('ENVIRONMENT') == 'test':
        app_settings = "config.TestConfig.TestConfig"
    elif os.environ.get("ENVIRONMENT") == "prod":
        app_settings = "config.ProductionConfig.ProductionConfig"

    app.config.from_object(app_settings)

    if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    # ma = Marshmallow(app)
    # enable CORS
    CORS(app)

    if not app.debug:
        logging.basicConfig(
            filename="error.log", level=logging.INFO, format="%(asctime)s %(message)s"
        )
    else:
        DebugToolbarExtension(app)
        app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

    # custom jinja line delimeters
    app.jinja_env.line_statement_prefix = "%"
    app.jinja_env.line_comment_prefix = "##"

    # register views
    from donordash.views import init_views  # noqa: E402

    init_views(app)

    return app
