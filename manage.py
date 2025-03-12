#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import click
from flask_migrate import Migrate
from flask import url_for, current_app
from sqlalchemy_utils.functions import create_database, database_exists
from donordash import db
from donordash import mail
from donordash import create_app
from donordash.lib.helpers import send_email

from donordash.models.donation import Donation
from donordash.models.donationfile import DonationFile

app = create_app()
migrate = Migrate(app, db)


# Create a shell context that adds the database and models to the shell session
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, Donation=Donation, DonationFile=DonationFile, db=db)


@app.cli.command("create-db")
def create_db():
    """Creates database if it doesn't exist."""
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_exists(db_uri):
        click.echo("Creating database ...")
        create_database(db_uri)
    else:
        click.echo("Database already exists. Nothing to create.")


@app.cli.command("process-donations")
def process_donations():
    """Process donation files."""
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
            click.echo(f"Error: File not found at path: {file_path}")


@app.cli.group()
def database():
    """Database management commands."""
    pass


@database.command("drop")
def db_drop():
    """Drops database tables"""
    if click.confirm("Are you sure you want to lose all your data"):
        db.drop_all()
        click.echo("Database tables dropped!")


@database.command("create")
@click.option("--default-data", is_flag=True, default=True, help="Create with default data")
@click.option("--sample-data", is_flag=True, default=False, help="Create with sample data")
def db_create(default_data, sample_data):
    """Creates database tables from sqlalchemy models"""
    db.configure_mappers()
    db.create_all()
    click.echo("Database tables created!")


@database.command("recreate")
@click.option("--default-data", is_flag=True, default=True, help="Create with default data")
@click.option("--sample-data", is_flag=True, default=False, help="Create with sample data")
def db_recreate(default_data, sample_data):
    """Recreates database tables (same as issuing 'drop' and then 'create')"""
    db_drop()
    db_create(default_data, sample_data)


@app.cli.command("init-db")
def init_db():
    """Drops and re-creates the SQL schema"""
    db.drop_all()
    db.configure_mappers()
    db.create_all()
    db.session.commit()


@app.cli.command("routes")
def routes():
    """Display all routes"""
    import urllib.parse as urllib_parse

    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = f"[{arg}]"
        methods = ",".join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib_parse.unquote(f"{rule.endpoint:25s} {methods:25s} {url}")
        output.append(line)

    for line in sorted(output):
        click.echo(line)


@app.cli.command("cov")
def cov():
    """Runs the unit tests with coverage."""
    import coverage
    import unittest

    cov = coverage.coverage(branch=True, include="cis/*")
    cov.start()
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    click.echo("Coverage Summary:")
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, "coverage")
    cov.html_report(directory=covdir)
    cov.erase()


if __name__ == "__main__":
    app.cli()
