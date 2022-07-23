#!/usr/bin/env bash

gunicorn --chdir /app/ cubeserver_app.main:app -c /gunicorn.conf.py
