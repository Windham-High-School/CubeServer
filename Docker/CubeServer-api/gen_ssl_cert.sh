#!/usr/bin/env bash
# Generates a new self-signed SSL certificate w/ OpenSSL

openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/" -keyout /etc/ssl/key.key -out /etc/ssl/cert.pem
