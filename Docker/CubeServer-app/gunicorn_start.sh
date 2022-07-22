#!/usr/bin/env bash

gunicorn --chdir /app/ cubeserver_app.main:app -w 2 --threads 2 -b 0.0.0.0:80
