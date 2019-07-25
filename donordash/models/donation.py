# -*- coding: utf-8 -*-

from arrow import utcnow
from sqlalchemy_utils import ArrowType
from sqlalchemy import Column, Integer, Boolean, Numeric
from donordash import db
from donordash.models import ModelMixin


class Donation(db.Model, ModelMixin):
    id = Column(Integer, primary_key=True)
    created_on = Column(ArrowType, default=utcnow)
    donor_id = Column(db.Unicode, nullable=False)
    donor_name = Column(db.Unicode)
    donor_email = Column(db.Unicode)
    donor_gender = Column(db.Unicode)
    donor_address = Column(db.Unicode)
    donation_amount = Column(Numeric, nullable=False)
    anonymous = Column(Boolean, nullable=False, server_default="0")

    donation_file_id = Column(Integer, db.ForeignKey("donation_file.id"), index=True)
    donation_file = db.relationship("DonationFile", backref="donations")

    def __init__(self, donor_id, donation_amount):
        self.donor_id = donor_id
        self.donation_amount = donation_amount

    def __repr__(self):
        return self.filename
