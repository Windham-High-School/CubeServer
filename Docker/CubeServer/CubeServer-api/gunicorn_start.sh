#!/usr/bin/env bash

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
.venv-api/bin/gunicorn --chdir /code/ cubeserver_api:app --log-level $LOGLEVEL -c /code/api.conf.py
