#!/usr/bin/env bash

# version <= 0.5.3 COMPATIBILITY:
if [ -f "/etc/ssl/api_cert/cert.pem" ]; then
    echo "Moving [cert.pem -> server.pem, key.key -> server.key] for compatibility with newer versions!"
    echo "These file names are now DEPRECATED for future reference."
    mv /etc/ssl/api_cert/cert.pem /etc/ssl/api_cert/server.pem
    mv /etc/ssl/api_cert/key.key  /etc/ssl/api_cert/server.key
fi

if [ -f "/etc/ssl/build_api_cert/beacon.pem" ]; then
    echo "WARNING: A persistent build_api_cert exists! This could be compromised if the image came from a public source!"
    #exit 1  # Will be fatal in a future release
fi

if [ ! -f "/etc/ssl/api_cert/server.pem" ]; then
    echo "Copying generated SSL cert from build-time into persistent storage."
    echo "If this breaks server host key verification, there is a backup folder!"
    mkdir -p /ect/ssl/api_cert_backup
    cp -r /etc/ssl/api_cert /ect/ssl/api_cert_backup
    /CubeServer-api/gen_ssl_cert.sh ${CERT_SUBJ} ${CERT_SUBJALTNAME} ${CERT_EXP_DAYS} server
    cp /etc/ssl/build_api_cert/* /etc/ssl/api_cert/
fi
