#!/bin/bash
# Load environment variables before running command
source /app/env.sh
# Run the process_donations command every minute
* * * * * su - root -c "cd /app && FLASK_APP=manage.py /usr/local/bin/python -m flask process-donations >> /app/notify.log 2>&1"
