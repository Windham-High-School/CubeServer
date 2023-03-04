#!/usr/bin/env bash

# Wait for CubeServer-api to be in a good spot first:
while [ ! -f "/api_cert/server.pem" ]; do
echo "Waiting for API certs to be copied into persistent storage..."
sleep 1
done

# TODO: Change to only using the CA cert method as in the CircuitPython wrapper instead of generating fingerprints
# Generate fingerprints of the API's certs:
echo "Generating SHA1 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/api.pem -fingerprint -sha1 -noout | cut -d "=" -f2 > /api_cert/sha1_fingerprint.txt
echo "Generating SHA256 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/api.pem -fingerprint -sha256 -noout | cut -d "=" -f2 > /api_cert/sha256_fingerprint.txt

export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_app.main:app --log-level $LOGLEVEL -c /gunicorn.conf.py
