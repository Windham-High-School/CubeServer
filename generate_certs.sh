#!/bin/bash

mkdir -p config
openssl rand -base64 64 > config/secret_key.txt
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout config/server.key -out config/server.pem -subj "/C=US/ST=New Hampshire/L=Windham"
