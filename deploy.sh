#!/bin/bash

git pull
docker compose --profile $1 build
docker compose --profile $1 up -d
