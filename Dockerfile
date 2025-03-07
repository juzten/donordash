FROM python:3.12-bullseye

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    postgresql-client \
    cron \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY pip.txt .

# Install dependencies with specific version of pip and setuptools
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r pip.txt

# Copy the rest of the application
COPY . .

# Make the manage.py file executable
RUN chmod +x ./manage.py

# Expose the Flask port
EXPOSE 5000

# Use an environment variable to determine config
ENV FLASK_APP=run.py
ENV FLASK_ENV=development
ENV CONFIG_FILE=config.dev
ENV ENVIRONMENT=dev

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
