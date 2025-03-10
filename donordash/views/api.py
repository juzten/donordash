# -*- coding: utf-8 -*-

import csv
import os
import uuid

from flask import jsonify, request
from flask_classful import FlaskView, route

from donordash import app, csrf, mail
from donordash.lib.helpers import send_email
from donordash.models.donation import Donation
from donordash.models.donationfile import DonationFile

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

    @route("/process_donations", methods=["POST"])
    @csrf.exempt
    def process_donations(self):
        """Process all donation records."""
        unprocessed_files = DonationFile.query.filter_by(processed=False).all()

        for unprocessed_file in unprocessed_files:
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], unprocessed_file.uuid_filename
            )

            if os.path.isfile(file_path):
                # Open the CSV file and read the rows
                with open(file_path, mode="r") as file:
                    csv_reader = csv.DictReader(file)

                    # Initialize counters and sums
                    new_donations_count = 0
                    anonymous_donations = 0
                    new_donations_sum = 0.0

                    for row in csv_reader:
                        new_donations_count += 1
                        donation_amount = float(row["donation_amount"])
                        new_donations_sum += donation_amount

                        # Create a Donation object from the row
                        donation = Donation(
                            donor_id=row["donor_id"], donation_amount=donation_amount
                        )

                        # Check and assign optional fields if they exist
                        if row.get("donor_name"):
                            donation.donor_name = row["donor_name"]
                        if row.get("donor_email"):
                            donation.donor_email = row["donor_email"]
                        if row.get("donor_gender"):
                            donation.donor_gender = row["donor_gender"]
                        if row.get("donor_address"):
                            donation.donor_address = row["donor_address"]

                        # If any value is missing (None), mark the donation as anonymous
                        if any(value == "" or value is None for value in row.values()):
                            donation.anonymous = True
                            anonymous_donations += donation_amount

                        # Save the donation
                        donation.save()

                    if new_donations_sum > 0:
                        anonymous_donations_percentage = round(
                            anonymous_donations / new_donations_sum * 100, 2
                        )
                    else:
                        anonymous_donations_percentage = 0  # Default when no donations

                    # If the file has an associated email, send a notification
                    if unprocessed_file.email:
                        mail.subject = "Donation File Processed"
                        mail.email = unprocessed_file.email
                        mail.new_donations_count = new_donations_count
                        mail.new_donations_sum = new_donations_sum
                        mail.anonymous_donations_percentage = (
                            anonymous_donations_percentage
                        )
                        send_email(
                            [unprocessed_file.email],
                            mail.subject,
                            "mail/submission_complete",
                            mail=mail,
                            reply_to="juzten+donordash@gmail.com",
                            sender="juzten+donordash@gmail.com",
                        )

                # Mark the file as processed
                unprocessed_file.processed = True
                unprocessed_file.save()

        return jsonify({"Success": "Donations processed"})

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
