#!/bin/bash

docker compose build
docker compose up -d $1
