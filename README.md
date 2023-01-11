# CubeServer
[![Documentation Status](https://readthedocs.org/projects/cubeserver/badge/?version=latest)](https://cubeserver.readthedocs.io/en/latest/?badge=latest)
[![Dependency Review](https://github.com/snorklerjoe/CubeServer/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/dependency-review.yml)
[![CodeQL](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/codeql-analysis.yml)
[![Pylint](https://github.com/snorklerjoe/CubeServer/actions/workflows/pylint.yml/badge.svg)](https://github.com/snorklerjoe/CubeServer/actions/workflows/pylint.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/0c7fad7ea7ff1a8380e0/maintainability)](https://codeclimate.com/github/snorklerjoe/CubeServer/maintainability)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Software to manage, store, score, and publish data received by Wifi-equipped microcontrollers for managing a school contest called The Project.
A live instance of this may or may not be available at https://whsproject.club/.

## Terminology:
  CubeServer
    - The name of the software backing "The Project"
    This includes the web application and leaderboard, the admin panel,
    the team API, and any other software contained within this repository.
  Cube
    - An individual team's station that will be mounted atop the roof of the school

## Versioning:
This project uses Semantic Versioning in the format major.minor.patch
Versions 0.0.0 until 1.0.0 are development releases.
Version 1.0.0 will be the first production release.
A new major or minor version may indicate database incompatibility unless otherwise noted, however patch versions should maintain database compatibility.

| Version | Notes |
| ------- | ----- |
| v0.1.0-alpha | basic web interface & structure demo |
| v0.1.1-alpha | early API implementation |
| v0.1.2-alpha | early API improvements |
| v0.2.0-alpha | preconfigured library packages |
| v0.3.0-alpha | preconfigured library improvements |
| v0.4.0-beta  | partially functional; basics working |
| v0.5.0-beta  | **First Deployable Release** |
| _v1.0.0-beta_  | [Fully-functional Beta Release Milestone](https://github.com/snorklerjoe/CubeServer/milestone/2) |
| _v1.0.0_  | [Fully-functional Production Release Milestone](https://github.com/snorklerjoe/CubeServer/milestone/3) |

## Building/running:

### The Easy Way-
Use the Ubuntu install script:
```bash
git clone https://github.com/snorklerjoe/CubeServer
cd CubeServer
sudo ./tools/install_ubuntu.sh
```
This will install a Systemd service for the server and everything will be automatic and work... Unless it doesn't.

--------------------------------------------------------------------------
### The Hard Way-
Install Docker dependency-
```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose
```
Then use Docker-Compose to build and run:
```bash
docker-compose build
docker-compose up
```

To permanantly reset the installation to the defaults and erase ALL data, run the following:
```bash
docker-compose down && docker volume rm cubeserver_mongodb-data cubeserver_api-ssl-cert cubeserver_flask-secret
```

## Topology & Docker Containers
CubeServer is built upon the containerization platform Docker. As described in docker-compose.yml, CubeServer is essentially comprised of the following parts as Docker containers:
- CubeServer-app
    The web app, served by GUnicorn and Flask.
- CubeServer-api
    The API for Cubes, also served by GUnicorn and Flask
- CubeServer-mongodb
    A standalone MongoDB server, central to the other containers
- CubeServer-accesspoint
    The container from which the WiFi access point and routing is taken care of to allow Cubes to connect to the API.
Files used for building each of these containers (other than CubeServer-mongodb, which is prebuilt) may be found in Docker/.

## Customization:
The rules and workings of the "game" may be customized and/or modified as described in [CUSTOMIZATION.md](./CUSTOMIZATION.md).

## Todos:
  See the [Issues](https://github.com/snorklerjoe/CubeServer/issues)
