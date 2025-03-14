# -*- coding: utf-8 -*-

import logging
import os
import warnings

import requests.packages.urllib3
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

warnings.filterwarnings("ignore", category=DeprecationWarning)

requests.packages.urllib3.disable_warnings()

db = SQLAlchemy()
mail = Mail()
api = Api(
    doc="/docs",
)


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
    elif os.environ.get("ENVIRONMENT") == "ci":
        app_settings = "config.CiConfig.CiConfig"
    elif os.environ.get("ENVIRONMENT") == "test":
        app_settings = "config.TestConfig.TestConfig"
    elif os.environ.get("ENVIRONMENT") == "prod":
        app_settings = "config.ProductionConfig.ProductionConfig"

    app.config.from_object(app_settings)

    if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

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

    from donordash.views.api import (
        donations_ns,
        process_donations_ns,
        upload_donations_ns,
    )

    api.add_namespace(donations_ns, path="/api/donations")
    api.add_namespace(process_donations_ns, path="/api/process_donations")
    api.add_namespace(upload_donations_ns, path="/api/upload")

    api.init_app(app)

    return app
