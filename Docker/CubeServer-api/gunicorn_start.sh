#!/usr/bin/env bash

# version <= 0.5.3 COMPATIBILITY:
if [ -f "/etc/ssl/api_cert/cert.pem" ]; then
echo "Moving [cert.pem -> server.pem, key.key -> apserveri.key] for compatibility with newer versions!"
echo "These file names are now DEPRECATED for future reference."
mv /etc/ssl/api_cert/cert.pem /etc/ssl/api_cert/server.pem
mv /etc/ssl/api_cert/key.key  /etc/ssl/api_cert/server.key
fi

# Ensure that the SSL certificate exists-
if [ ! -f "/etc/ssl/build_api_cert/server.pem" ]; then
echo "For some reason, an SSL certificate wasn't generated at build-time..."
echo "This is a fatal issue."
exit 1
fi

if [ ! -f "/etc/ssl/api_cert/server.pem" ]; then
echo "Copying generated SSL cert from build-time into persistent storage."
echo "If this breaks server host key verification, there is a backup folder!"
mkdir -p /ect/ssl/api_cert_backup
cp -r /etc/ssl/api_cert /ect/ssl/api_cert_backup
cp /etc/ssl/build_api_cert/* /etc/ssl/api_cert/
fi

echo "Starting GUnicorn..."
export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_api:app -c /gunicorn.conf.py
