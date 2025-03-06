#!/bin/bash
# Load environment variables before running command
source /app/env.sh
# Run the process_donations command every minute
* * * * * su - root -c "/usr/local/bin/python /app/manage.py process_donations >> /app/notify.log 2>&1"
