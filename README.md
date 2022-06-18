# CubeServer
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

