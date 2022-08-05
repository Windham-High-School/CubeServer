# CubeServer
[![Dependency Review](https://github.com/snorklerjoe/CubeServer/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/dependency-review.yml)
[![CodeQL](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml)
[![Pylint](https://github.com/snorklerjoe/CubeServer/actions/workflows/pylint.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/pylint.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/0c7fad7ea7ff1a8380e0/maintainability)](https://codeclimate.com/github/snorklerjoe/CubeServer/maintainability)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Software to manage, store, score, and publish data received by Wifi-equipped microcontrollers for managing a school contest

## Goals:
- Sets up the pi as an access point
- Receives/responds to TCP packets from clients
- Stores data in a database
- A leaderboard and admin web app

Note that these goals are not yet fully implemented.

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

## Customization:
The rules and workings of the "game" may be customized and/or modified as described in [CUSTOMIZATION.md](./CUSTOMIZATION.md).

## Todos:
* Finish implementing goals
  * Backend/receiving datapoints
* Security concerns:
  * Reimplement webapp password storage to use Bcrypt instead of just an HMAC hash; Each password should have its own salt for better security
  * Limit failed login attempts per user per time interval
    - via a database field OR (better option seems to be) using a local dictionary
* Clean up docstrings to use Sphynx markup for parameter/return definitions
