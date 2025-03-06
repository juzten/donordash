# -*- coding: utf-8 -*-

import os
import io
import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from donordash import app, db
from donordash.models.donationfile import DonationFile
from donordash.models.donation import Donation

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    # app.config['SQLALCHEMY_DATABASE_URI'] = "donor_app_test"
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@postgres:5432/donor_app_test"
    app.config['UPLOAD_FOLDER'] = '/tmp'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_donations():
    """Create sample donation data."""
    # Create donations with minimal required fields first

    donation1 = Donation(
        donor_id='123',
        donation_amount='100.00'
    )

    donation2 = Donation(
        donor_id='456',
        donation_amount='200.00'
    )

    # Add the additional fields
    donation1.donor_name = 'John Doe'
    donation1.donor_email = 'john@example.com'
    donation1.donor_gender = 'Male'
    donation1.donor_address = '123 Main St'
    donation1.anonymous = False

    donation2.donor_name = 'Jane Smith'
    donation2.donor_email = 'jane@example.com'
    donation2.donor_gender = 'Female'
    donation2.donor_address = '456 Oak Ave'
    donation2.anonymous = True

    donations = [donation1, donation2]

    with app.app_context():
        for donation in donations:
            db.session.add(donation)
        db.session.commit()

    return donations

def test_donations_endpoint(client, sample_donations):
    """Test the /api/donations endpoint returns all donations."""
    response = client.get('/api/donations')

    assert response.status_code == 200
    data = json.loads(response.data)

    assert len(data) == 2

    # Check the first donation
    assert data[0]['donor_id'] == '123'
    assert data[0]['donor_name'] == 'John Doe'
    assert data[0]['donor_email'] == 'john@example.com'
    assert data[0]['donor_gender'] == 'Male'
    assert data[0]['donor_address'] == '123 Main St'
    assert data[0]['donation_amount'] == '100.00'
    assert data[0]['anonymous'] is False

    # Check the second donation
    assert data[1]['donor_id'] == '456'
    assert data[1]['donor_name'] == 'Jane Smith'
    assert data[1]['donor_email'] == 'jane@example.com'
    assert data[1]['donor_gender'] == 'Female'
    assert data[1]['donor_address'] == '456 Oak Ave'
    assert data[1]['donation_amount'] == '200.00'
    assert data[1]['anonymous'] is True

def test_donations_endpoint_empty(client):
    """Test the /api/donations endpoint returns empty list when no donations exist."""
    response = client.get('/api/donations')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0
    assert data == []

def test_upload_endpoint_success(client, monkeypatch, tmp_path):
    """Test successful file upload to /api/upload endpoint."""
    # Set up a temporary upload folder that actually exists
    upload_folder = str(tmp_path)

    # Use dictionary access instead of attribute access
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Directly mock the DonationFile class to avoid database operations
    original_donation_file = DonationFile

    try:
        # Create a simple file for upload
        file_content = b'test,data'

        # Make a real request with a real file
        data = {
            'email': 'test@example.com',
            'donation_file': (io.BytesIO(file_content), 'test.csv')
        }

        # Mock the DonationFile class using dictionary-style patching
        monkeypatch.setitem(sys.modules, 'donordash.models.donationfile.DonationFile', MagicMock())

        # Make the request
        response = client.post('/api/upload',
                             data=data,
                             content_type='multipart/form-data')

        # Check basic response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result == {'Success': 'File uploaded'}

        # Check that a file was created in the temp directory
        files = list(tmp_path.iterdir())
        assert len(files) > 0  # At least one file was created

    finally:
        # Restore the original configuration
        app.config['UPLOAD_FOLDER'] = '/tmp'
        sys.modules['donordash.models.donationfile.DonationFile'] = original_donation_file

def test_upload_endpoint_no_file(client):
    """Test /api/upload endpoint returns error when no file is provided."""
    response = client.post('/api/upload', data={})

    assert response.status_code == 400
    result = json.loads(response.data)
    assert result == {'error': 400, 'exception': 'File not uploaded'}

def test_upload_endpoint_with_file_no_email(client, tmp_path):
    """Test /api/upload endpoint works without an email address."""
    # Set the upload folder to our temporary directory
    app.config['UPLOAD_FOLDER'] = str(tmp_path)

    # Create a test file
    file_content = b'donor_id,donor_name,amount\n123,Test User,50.00'

    # Prepare the request data - no email included
    data = {
        'donation_file': (io.BytesIO(file_content), 'test.csv')
    }

    # Make the request
    response = client.post('/api/upload',
                         data=data,
                         content_type='multipart/form-data')

    # Check that the response indicates success
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result == {'Success': 'File uploaded'}

    # Restore the original upload folder
    app.config['UPLOAD_FOLDER'] = '/tmp'
