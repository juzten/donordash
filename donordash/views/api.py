# -*- coding: utf-8 -*-

import os
import uuid

from flask import jsonify, request
from flask_classful import FlaskView, route

from donordash import app, csrf
from donordash.models.donation import Donation
from donordash.models.donationfile import DonationFile

prod = os.environ.get("ENVIRONMENT") != "dev"


__all__ = "ApiView"


class ApiView(FlaskView):
    route_base = "/api"

    @route("/donations", methods=["GET"])
    def donations(self):
        """Get all donation records."""
        donations = Donation.query.all()
        donations_dicts = []
        for donation in donations:
            donations_dicts.append(
                {
                    "donor_id": donation.donor_id,
                    "donor_name": donation.donor_name,
                    "donor_email": donation.donor_email,
                    "donor_gender": donation.donor_gender,
                    "donor_address": donation.donor_address,
                    "donation_amount": str(donation.donation_amount),
                    "anonymous": donation.anonymous,
                }
            )
        return jsonify(donations_dicts)

    @route("/upload", methods=["GET", "POST"])
    @csrf.exempt
    def upload(self):
        """Upload new CSV file and process it."""

        if request.files.get("donation_file"):
            email_address = request.form.get("email")
            donation_file = request.files.get("donation_file")
            donation_file_uuid_filename = "{}.{}".format(
                str(uuid.uuid4()).replace("-", ""),
                donation_file.filename.rsplit(".", 1)[1].lower(),
            )
            attachment_path = os.path.join(
                app.config["UPLOAD_FOLDER"], donation_file_uuid_filename
            )
            donation_file.save(attachment_path)

            donation_file = DonationFile(
                filename=donation_file.filename,
                uuid_filename=donation_file_uuid_filename,
            )

            if email_address:
                donation_file.email = email_address
            donation_file.save()

            return jsonify({"Success": "File uploaded"})

        return jsonify(error=400, exception="File not uploaded"), 400
