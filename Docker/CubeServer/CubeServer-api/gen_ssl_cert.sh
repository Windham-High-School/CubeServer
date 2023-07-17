#!/usr/bin/env bash
#           gen_ssl_cert.sh
# Copyright 2022-2023 Joseph R. Freeston
#
# Generates a new self-signed SSL certificate w/ OpenSSL
# (creates "$4.pem" and "$4.key" in the cwd)
# Usage: bash gen_ssl_cert.sh [subj] [altName] [days'TillExpiration] [outputName]
#

if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters."
    echo "USAGE: bash gen_ssl_cert.sh [subj] [altName] [days'TillExpiration] [outputName]"
    exit 1
fi

# Make sure the directory exists...
mkdir -p /etc/ssl/build_api_cert/
echo "Subject: $1"
echo "alt subj: $2"
echo "EXPIRES IN $3 DAYS"
if [ ! -f "/etc/ssl/build_api_cert/$4.pem" ]; then
    cd /etc/ssl/build_api_cert/
    echo
    echo "Generating a new certificate..."
    echo "Generating a new self-signed SSL certificate..."
    openssl req -new -newkey rsa:4096 -days $3 -nodes -x509 \
        -subj "$1" -addext "subjectAltName=IP:$2" \
        -keyout "$4.key" -out "$4.pem"
    echo
    echo "Checking the certificate..."
    openssl verify -CAfile "$4.pem" "$4.pem"
    if [ $? != 0 ]; then
        echo "There's something wrong with the certificate."
        exit 1
    else
        echo "Everything looks good!"
    fi
else
    echo "An SSL certificate already exists; leaving that one."
fi
