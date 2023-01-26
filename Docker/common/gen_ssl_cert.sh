#!/usr/bin/env bash
# Generates a new self-signed SSL certificate w/ OpenSSL
# Usage: bash gen_ssl_cert.sh [subj] [altName] [days'TillExpiration]

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters."
    echo "USAGE: bash gen_ssl_cert.sh [subj] [altName] [days'TillExpiration]"
    exit 1
fi

# Make sure the directory exists...
mkdir -p /etc/ssl/build_api_cert/
echo "Subject: $1"
echo "alt subj: $2"
echo "EXPIRES IN $3 DAYS"
if [ ! -f "/etc/ssl/build_api_cert/cert.pem" ]; then
    cd /etc/ssl/build_api_cert/
    echo
    echo "Generating a new certificate..."
    echo "Generating a new self-signed SSL certificate..."
    openssl req -new -newkey rsa:4096 -days $3 -nodes -x509 \
        -subj "$1" -addext "subjectAltName=IP:$2" \
        -keyout key.key -out cert.pem
    echo
    echo "Checking the certificate..."
    openssl verify -CAfile cert.pem cert.pem
    if [ $? != 0 ]; then
        echo "There's something wrong with the certificate."
        exit 1
    fi
else
    echo "An SSL certificate already exists; leaving that one."
fi
