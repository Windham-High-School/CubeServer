#!/bin/bash

git pull
docker compose build
docker compose --profile $1 up -d
