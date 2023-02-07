#!/usr/bin/env bash

echo Executing at entrypoint...

# Ensure that the SSL certificate exists-
if [ ! -f "/etc/ssl/build_api_cert/beacon.pem" ]; then
echo "For some reason, an SSL certificate wasn't generated at build-time..."
echo "This is a fatal issue."
exit 1
fi

if [ ! -f "/etc/ssl/beacon_cert/beacon.pem" ]; then
echo "Copying generated SSL cert from build-time into persistent storage."
echo "If this breaks server host key verification, there is a backup folder!"
mkdir -p /ect/ssl/beacon_cert_backup
cp -r /etc/ssl/beacon_cert /ect/ssl/beacon_cert_backup
cp /etc/ssl/build_api_cert/* /etc/ssl/beacon_cert/
fi

echo certs installed

cd /app/
python3 -u -m cubeserver_beaconserver 0.0.0.0 8888
