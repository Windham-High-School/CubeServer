#!/usr/bin/env bash

/CubeServer_api/setup.sh

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /code/ cubeserver_api:app --log-level $LOGLEVEL -c /CubeServer-api/gunicorn.conf.py
