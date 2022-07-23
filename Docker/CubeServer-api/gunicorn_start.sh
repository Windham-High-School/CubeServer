#!/usr/bin/env bash

gunicorn --chdir /app/ cubeserver_api:app -c /gunicorn.conf.py