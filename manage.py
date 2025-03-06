#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
from flask_script import Server, Manager, Shell, Command, Option, prompt_bool, prompt
from flask_migrate import Migrate, MigrateCommand
from flask import url_for
from sqlalchemy_utils.functions import create_database, database_exists
from donordash import db
from donordash import app, mail
from donordash.lib.helpers import send_email

from donordash.models.donation import Donation
from donordash.models.donationfile import DonationFile

migrate = Migrate(app, db)
manager = Manager(app)
db_manager = Manager(usage="Perform database operations")


def _make_context():
    return dict(app=app, Donation=Donation, DonationFile=DonationFile, db=db)


@manager.command
def create_db():
    """Creates database if it doesn't exist."""
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_exists(db_uri):
        print("Creating database ...")
        create_database(db_uri)
        # db.create_all()
    else:
        print("Database already exists. Nothing to create.")


@manager.command
def process_donations():
    """Process donation files.
    Ran by: python manange.py process_donations

    get all unprocessed donationfile records
    loop each one
        create new donation record
        after each donationfile is done processing
            check for email and send notification to it


    """
    unprocessed_files = DonationFile.query.filter_by(processed=False).all()

    for unprocessed_file in unprocessed_files:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unprocessed_file.uuid_filename)

        if os.path.isfile(file_path):
            # Open the CSV file and read the rows
            with open(file_path, mode='r') as file:
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
                    donation = Donation(donor_id=row["donor_id"], donation_amount=donation_amount)

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
                    if any(value == '' or value is None for value in row.values()):
                        donation.anonymous = True
                        anonymous_donations += donation_amount

                    # Save the donation
                    donation.save()

                # Calculate the percentage of anonymous donations
                anonymous_donations_percentage = round(anonymous_donations / new_donations_sum * 100, 2)

                # If the file has an associated email, send a notification
                if unprocessed_file.email:
                    mail.subject = "Donation File Processed"
                    mail.email = unprocessed_file.email
                    mail.new_donations_count = new_donations_count
                    mail.new_donations_sum = new_donations_sum
                    mail.anonymous_donations_percentage = anonymous_donations_percentage
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
        else:
            print(f"Error: File not found at path: {file_path}")


manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("db", MigrateCommand)


port = int(os.environ.get("PORT", 5000))
manager.add_command("runserver", Server(use_debugger=True, use_reloader=True, host="0.0.0.0", port=port))


@db_manager.command
def drop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        print("Database tables dropped!")


@db_manager.command
def create(default_data=True, sample_data=False):
    "Creates database tables from sqlalchemy models"
    db.configure_mappers()
    db.create_all()
    print("Database tables created!")


@db_manager.command
def recreate(default_data=True, sample_data=False):
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop()
    create(default_data, sample_data)


manager.add_command("database", db_manager)


@manager.command
def init_db():
    """
    Drops and re-creates the SQL schema
    Ran by: python manage.py init_db
    """
    db.drop_all()
    db.configure_mappers()
    db.create_all()
    db.session.commit()


@manager.command
def routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ",".join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:25s} {:25s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def test():
    """Run the unit tests
    Ran by: python manage.py test
    """
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def cov():
    import coverage
    import unittest

    """Runs the unit tests with coverage.
    Ran by: python manage.py cov
    """
    cov = coverage.coverage(branch=True, include="cis/*")
    cov.start()
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print("Coverage Summary:")
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, "coverage")
    cov.html_report(directory=covdir)
    cov.erase()


if __name__ == "__main__":
    manager.run()
