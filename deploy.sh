#!/bin/bash

git pull
export STATIC_VERSION=`git rev-parse --short HEAD`
docker compose --profile $1 build
docker compose --profile $1 up -d
