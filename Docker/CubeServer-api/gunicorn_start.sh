#!/usr/bin/env bash

# Ensure that the SSL certificate exists-
if [ ! -f "/etc/ssl/build_api_cert/cert.pem" ]; then
echo "For some reason, an SSL certificate wasn't generated at build-time..."
echo "This is a fatal issue."
exit 1
fi

if [ ! -f "/etc/ssl/api_cert/cert.pem" ]; then
echo "Copying generated SSL cert from build-time into persistent storage."
echo "If this breaks server host key verification, there is a backup folder!"
mkdir -p /ect/ssl/api_cert_backup
cp -r /etc/ssl/api_cert /ect/ssl/api_cert_backup
cp /etc/ssl/build_api_cert/* /etc/ssl/api_cert/
fi

echo "Starting GUnicorn..."
gunicorn --chdir /app/ cubeserver_api:app -c /gunicorn.conf.py
