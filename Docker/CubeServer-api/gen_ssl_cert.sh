#!/usr/bin/env bash
# Generates a new self-signed SSL certificate w/ OpenSSL
# Usage: bash gen_ssl_cert.sh [subj] [altName] [days'TillExpiration]

#TODO: check to see if the arguments are specified before relying on them

# Make sure the directory exists...
mkdir -p /etc/ssl/build_api_cert/
echo "Subject: $1"
echo "alt subj: $2"
echo "EXPIRES IN $3 DAYS"
if [ ! -f "/etc/ssl/build_api_cert/cert.pem" ]; then
    echo "Generating a new self-signed SSL certificate..."
    openssl req -new -newkey rsa:4096 -days $3 -nodes -x509 \
        -subj "$1" -addext "subjectAltName = $2" \
        -keyout /etc/ssl/build_api_cert/key.key -out /etc/ssl/build_api_cert/cert.pem
else
    echo "An SSL certificate already exists; leaving that one."
fi
