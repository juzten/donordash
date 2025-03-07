import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Get the DATABASE_URL from environment
database_url = os.environ.get("DATABASE_URL")
print(f"Using DATABASE_URL: {database_url}")

# Make sure it uses postgresql:// not postgres://
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    print(f"Converted to: {database_url}")

try:
    # Create engine and connect
    engine = create_engine(database_url)
    connection = engine.connect()
    print("Successfully connected to database!")

    # Import your models to create tables
    print("Importing models...")
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from donordash import db
    from donordash.models.donation import Donation
    from donordash.models.donationfile import DonationFile

    # Create tables
    print("Creating tables...")
    db.metadata.create_all(engine)
    print("Tables created successfully!")

    connection.close()
    print("Database setup complete!")

except SQLAlchemyError as e:
    print(f"Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
