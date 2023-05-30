#!/usr/bin/env bash

# Wait for CubeServer-api to be in a good spot first:
while [ ! -f "/api_cert/server.pem" ]; do
    echo "Waiting for API certs to be copied into persistent storage..."
    sleep 1
done

/CubeServer_app/setup.sh

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_app.main:app --log-level $LOGLEVEL -c /CubeServer-app/gunicorn.conf.py
