#!/usr/bin/env bash

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
.venv-app/bin/gunicorn --chdir /code/ cubeserver_app:app --log-level $LOGLEVEL -c /code/app.conf.py
