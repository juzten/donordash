# -*- coding: utf-8 -*-

from arrow import utcnow
from sqlalchemy_utils import ArrowType
from sqlalchemy import Column, Integer, Boolean
from donordash import db
from donordash.models import ModelMixin


class DonationFile(db.Model, ModelMixin):
    id = Column(Integer, primary_key=True)
    created_on = Column(ArrowType, default=utcnow)
    filename = Column(db.Unicode, nullable=False)
    uuid_filename = Column(db.Unicode, nullable=False)
    processed = Column(Boolean, nullable=False, server_default="0")
    email = Column(db.Unicode)

    def __init__(self, filename, uuid_filename):
        self.filename = filename
        self.uuid_filename = uuid_filename

    def __repr__(self):
        return self.filename
