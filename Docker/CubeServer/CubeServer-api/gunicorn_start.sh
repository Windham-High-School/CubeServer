#!/usr/bin/env bash

/CubeServer_api/setup.sh

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_api:app --log-level $LOGLEVEL -c /gunicorn.conf.py
