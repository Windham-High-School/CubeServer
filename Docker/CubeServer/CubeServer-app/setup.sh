#!/usr/bin/env bash

# TODO: Change to only using the CA cert method as in the CircuitPython wrapper instead of generating fingerprints
# Generate fingerprints of the API's certs:
echo "Generating SHA1 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/server.pem -fingerprint -sha1 -noout | cut -d "=" -f2 > /api_cert/sha1_fingerprint.txt
echo "Generating SHA256 Fingerprint for client constants code generation..."
openssl x509 -in /api_cert/server.pem -fingerprint -sha256 -noout | cut -d "=" -f2 > /api_cert/sha256_fingerprint.txt
