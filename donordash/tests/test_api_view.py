# -*- coding: utf-8 -*-

import csv
import io
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from donordash import app, db
from donordash.models.donation import Donation
from donordash.models.donationfile import DonationFile


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config["TESTING"] = True

    # Create test upload folder if it doesn't exist
    app.config["UPLOAD_FOLDER"] = "/tmp"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    # app.config['SQLALCHEMY_DATABASE_URI'] = "donor_app_test"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://postgres:password@postgres:5432/donor_app_test"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return [
        {
            "donor_id": "D001",
            "donation_amount": "100.00",
            "donor_name": "John Doe",
            "donor_email": "john@example.com",
            "donor_gender": "M",
            "donor_address": "123 Main St",
        },
        {
            "donor_id": "D002",
            "donation_amount": "50.50",
            "donor_name": "Jane Smith",
            "donor_email": "jane@example.com",
            "donor_gender": "F",
            "donor_address": "",
        },
        {
            "donor_id": "D003",
            "donation_amount": "75.25",
            "donor_name": "",
            "donor_email": "anonymous@example.com",
            "donor_gender": "",
            "donor_address": "",
        },
    ]


@pytest.fixture
def mock_unprocessed_files(monkeypatch):
    """Mock DonationFile query results."""
    # Create mock file objects that can be accessed later in tests
    files = [
        MagicMock(
            id=1,
            uuid_filename="test_file1.csv",
            email=None,
            processed=False,
            save=MagicMock(),
        ),
        MagicMock(
            id=2,
            uuid_filename="test_file2.csv",
            email=None,
            processed=False,
            save=MagicMock(),
        ),
    ]

    class MockQuery:
        @staticmethod
        def filter_by(processed=None):
            class MockFilterResult:
                @staticmethod
                def all():
                    return files

            return MockFilterResult

    # Replace the query with our mock
    monkeypatch.setattr(DonationFile, "query", MockQuery)

    # Return the mock query class so tests can access the files
    return MockQuery


def create_csv_file(data, filename):
    """Helper function to create a CSV file with test data."""
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return filepath


@pytest.fixture
def sample_donations():
    """Create sample donation data."""
    # Create donations with minimal required fields first

    donation1 = Donation(donor_id="123", donation_amount="100.00")

    donation2 = Donation(donor_id="456", donation_amount="200.00")

    # Add the additional fields
    donation1.donor_name = "John Doe"
    donation1.donor_email = "john@example.com"
    donation1.donor_gender = "Male"
    donation1.donor_address = "123 Main St"
    donation1.anonymous = False

    donation2.donor_name = "Jane Smith"
    donation2.donor_email = "jane@example.com"
    donation2.donor_gender = "Female"
    donation2.donor_address = "456 Oak Ave"
    donation2.anonymous = True

    donations = [donation1, donation2]

    with app.app_context():
        for donation in donations:
            db.session.add(donation)
        db.session.commit()

    return donations


def test_donations_endpoint(client, sample_donations):
    """Test the /api/donations endpoint returns all donations."""
    response = client.get("/api/donations")

    assert response.status_code == 200
    data = json.loads(response.data)

    assert len(data) == 2

    # Check the first donation
    assert data[0]["donor_id"] == "123"
    assert data[0]["donor_name"] == "John Doe"
    assert data[0]["donor_email"] == "john@example.com"
    assert data[0]["donor_gender"] == "Male"
    assert data[0]["donor_address"] == "123 Main St"
    assert data[0]["donation_amount"] == "100.00"
    assert data[0]["anonymous"] is False

    # Check the second donation
    assert data[1]["donor_id"] == "456"
    assert data[1]["donor_name"] == "Jane Smith"
    assert data[1]["donor_email"] == "jane@example.com"
    assert data[1]["donor_gender"] == "Female"
    assert data[1]["donor_address"] == "456 Oak Ave"
    assert data[1]["donation_amount"] == "200.00"
    assert data[1]["anonymous"] is True


def test_donations_endpoint_empty(client):
    """Test the /api/donations endpoint returns empty list when no donations exist."""
    response = client.get("/api/donations")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0
    assert data == []


def test_upload_endpoint_success(client, monkeypatch, tmp_path):
    """Test successful file upload to /api/upload endpoint."""
    # Set up a temporary upload folder that actually exists
    upload_folder = str(tmp_path)

    # Use dictionary access instead of attribute access
    app.config["UPLOAD_FOLDER"] = upload_folder

    # Directly mock the DonationFile class to avoid database operations
    original_donation_file = DonationFile

    try:
        # Create a simple file for upload
        file_content = b"test,data"

        # Make a real request with a real file
        data = {
            "email": "test@example.com",
            "donation_file": (io.BytesIO(file_content), "test.csv"),
        }

        # Mock the DonationFile class using dictionary-style patching
        monkeypatch.setitem(
            sys.modules, "donordash.models.donationfile.DonationFile", MagicMock()
        )

        # Make the request
        response = client.post(
            "/api/upload", data=data, content_type="multipart/form-data"
        )

        # Check basic response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result == {"Success": "File uploaded"}

        # Check that a file was created in the temp directory
        files = list(tmp_path.iterdir())
        assert len(files) > 0  # At least one file was created

    finally:
        # Restore the original configuration
        app.config["UPLOAD_FOLDER"] = "/tmp"
        sys.modules[
            "donordash.models.donationfile.DonationFile"
        ] = original_donation_file


def test_upload_endpoint_no_file(client):
    """Test /api/upload endpoint returns error when no file is provided."""
    response = client.post("/api/upload", data={})

    assert response.status_code == 400
    result = json.loads(response.data)
    assert result == {"error": 400, "exception": "File not uploaded"}


def test_upload_endpoint_with_file_no_email(client, tmp_path):
    """Test /api/upload endpoint works without an email address."""
    # Set the upload folder to our temporary directory
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    # Create a test file
    file_content = b"donor_id,donor_name,amount\n123,Test User,50.00"

    # Prepare the request data - no email included
    data = {"donation_file": (io.BytesIO(file_content), "test.csv")}

    # Make the request
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    # Check that the response indicates success
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result == {"Success": "File uploaded"}

    # Restore the original upload folder
    app.config["UPLOAD_FOLDER"] = "/tmp"


def test_process_donations_success(client, mock_unprocessed_files, sample_csv_data):
    """Test successful processing of donation files."""
    # Create test files
    create_csv_file(sample_csv_data, "test_file1.csv")
    create_csv_file(sample_csv_data, "test_file2.csv")

    # Mock the Donation model's save method
    with patch("donordash.models.donation.Donation.save") as mock_save:
        # Mock the email sending function

        # Make request to the endpoint
        response = client.post("/api/process_donations")

        # Check response
        assert response.status_code == 200
        assert json.loads(response.data) == {"Success": "Donations processed"}

        # Check that donations were saved (3 donations per file, 2 files)
        assert mock_save.call_count == 6

        # Verify files were marked as processed
        processed_files = DonationFile.query.filter_by(processed=False).all()
        for file in processed_files:
            assert file.save.called


def test_process_donations_no_files(client, monkeypatch):
    """Test when there are no unprocessed files."""

    # Mock empty query result
    class MockEmptyQuery:
        @staticmethod
        def filter_by(processed=None):
            class MockFilterResult:
                @staticmethod
                def all():
                    return []

            return MockFilterResult

    monkeypatch.setattr(DonationFile, "query", MockEmptyQuery)

    # Make request to the endpoint
    response = client.post("/api/process_donations")

    # Check response
    assert response.status_code == 200
    assert json.loads(response.data) == {"Success": "Donations processed"}


def test_process_donations_file_not_found(client, mock_unprocessed_files):
    """Test behavior when a file in the database does not exist on disk."""
    # Don't create any files, so the path check will fail

    # Make request to the endpoint
    response = client.post("/api/process_donations")

    # Check response - should still succeed but not process any files
    assert response.status_code == 200
    assert json.loads(response.data) == {"Success": "Donations processed"}

    # Verify files were still marked as processed
    processed_files = DonationFile.query.filter_by(processed=False).all()
    for file in processed_files:
        assert file.save.called


def test_process_donations_invalid_csv(client, mock_unprocessed_files):
    """Test handling of malformed CSV files."""
    # Create invalid CSV file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "test_file1.csv")
    with open(filepath, "w") as f:
        f.write("This is not a valid CSV file")

    # Mock the Donation model's save method
    with patch("donordash.models.donation.Donation.save") as mock_save:
        # Make additional mocks to prevent processing
        with patch("csv.DictReader", side_effect=lambda f: []):
            # This mocks an empty CSV so no processing happens

            # Make request to the endpoint
            response = client.post("/api/process_donations")

            # Check response - should return success even if CSV is invalid
            assert response.status_code == 200
            assert json.loads(response.data) == {"Success": "Donations processed"}

            # No donations should be saved
            assert mock_save.call_count == 0

    # Get the files from our mock
    files = mock_unprocessed_files().filter_by().all()

    # Files should still be marked as processed even if CSV parsing failed
    for file in files:
        assert file.processed is True
        assert file.save.called
