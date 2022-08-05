#!/usr/bin/env bash

export PYTHONUNBUFFERED=TRUE  # Log Python output
gunicorn --chdir /app/ cubeserver_app.main:app -c /gunicorn.conf.py
