#!/usr/bin/env bash

echo Executing at entrypoint...

# Ensure that the SSL certificate exists-
if [ -f "/etc/ssl/build_api_cert/beacon.pem" ]; then
echo "WARNING: A persistent build_api_cert exists! This could be compromised if the image came from a public source!"
#exit 1  # Will be fatal in a future release
fi

if [ ! -f "/etc/ssl/beacon_cert/beacon.pem" ]; then
echo "Copying generated SSL cert from build-time into persistent storage."
echo "If this breaks server host key verification, there is a backup folder!"
mkdir -p /ect/ssl/beacon_cert_backup
cp -r /etc/ssl/beacon_cert /ect/ssl/beacon_cert_backup
/gen_ssl_cert.sh ${CERT_SUBJ} ${CERT_SUBJALTNAME} ${CERT_EXP_DAYS} beacon
cp /etc/ssl/build_api_cert/* /etc/ssl/beacon_cert/
fi

echo certs installed

cd /app/
python3 -u -m cubeserver_beaconserver 0.0.0.0 8888
