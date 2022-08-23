#!/usr/bin/env bash

while [ ! -f "/api_cert/cert.pem" ]; do
echo "Waiting for API certs to be copied into persistent storage..."
sleep 1
done

# TODO: Change to only using the CA cert method as in the CircuitPython wrapper instead of generating fingerprints
# Generate fingerprints of the API's certs:
echo "Generating SHA1 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/cert.pem -fingerprint -sha1 -noout | cut -d "=" -f2 > /api_cert/sha1_fingerprint.txt
echo "Generating SHA256 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/cert.pem -fingerprint -sha256 -noout | cut -d "=" -f2 > /api_cert/sha256_fingerprint.txt

export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_app.main:app -c /gunicorn.conf.py
