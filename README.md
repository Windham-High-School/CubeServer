# CubeServer

[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/2.1.x/)

[![CodeQL](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml)

Software to manage, store, score, and publish data received by Wifi-equipped microcontrollers for managing a school contest

## Goals:
- Sets up the pi as an access point
- Receives/responds to TCP packets from clients
- Stores data in a database
- A leaderboard and admin web app

## Overview of user-side processes:
- Once allowed by the Admin panel, team sign-ups will happen via the website
  - Teams will enter a team name, the names of the team's participants, and whether they are entering for the varsity or junior varsity level.
  - Teams will receive a "secret identifier" by the server upon sign-up. This will be entered as a constant in their code and will be used behind-the-scenes to reduce the possibility of impersonating or sabotaging another group.
- Upon approval by an Admin, these teams will be added to the leaderboard

## Building/running:
Use Docker-Compose to build and run:
```bash
docker-compose build
docker-compose up
```

