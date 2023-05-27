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
  **CubeServer**<br>
    - The name of the software backing "The Project"
    This includes the web application and leaderboard, the admin panel,
    the team API, and any other software contained within this repository.<br>
  **Cube**<br>
    - An individual team's station that will be mounted atop the roof of the school

## Versioning:
This project uses Semantic Versioning in the format major.minor.patch
Versions 0.0.0 until 1.0.0 are development releases.
Version 1.0.0 will be the first production release.
A new major or minor version may indicate database incompatibility unless otherwise noted, however patch versions should maintain database compatibility. See [CONTRIBUTING.md](./CONTRIBUTING.md) for more info.

| Version | Notes |
| ------- | ----- |
| v0.1.0-alpha | basic web interface & structure demo |
| v0.1.1-alpha | early API implementation |
| v0.1.2-alpha | early API improvements |
| v0.2.0-alpha | preconfigured library packages |
| v0.3.0-alpha | preconfigured library improvements |
| v0.4.0-beta  | partially functional; basics working |
| v0.5.0-beta  | **First Deployable Release** |
| _v1.0.0_  | [Version 1.0.0](https://github.com/snorklerjoe/CubeServer/milestone/2) |
| _v1.?.?_  | [Fully-functional Production Release Milestone](https://github.com/snorklerjoe/CubeServer/milestone/3) |


### Version suffices
| Ending | Meaning |
| ------ | ------- |
| -dev   | Tracks the development of that release |
| -beta  | Prerelease version |

## Building/running:

### The Easy Way-
Use the Ubuntu install script:
```bash
git clone https://github.com/snorklerjoe/CubeServer
cd CubeServer
sudo ./tools/install_ubuntu.sh
```
This will install a Systemd service for the server and everything will be automatic and work... Unless it doesn't.

**Note that this method is now unsupported and will be removed in a future version**

--------------------------------------------------------------------------
### Using &nbsp; `docker compose build` -
Install Docker dependency-
```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose
```
Then use Docker-Compose to build and run:
```bash
./configure
docker-compose build
docker-compose up
```

To permanantly reset the installation to the defaults and erase ALL data, run the following:
```bash
docker-compose down && docker volume rm cubeserver_mongodb-data cubeserver_api-ssl-cert cubeserver_flask-secret
```

### Cross-building and Docker Hub

Containers are built on Docker Hub for arm64 and amd64 linux (moving forward)

```bash
docker buildx bake -f docker-compose.yml -f .env --set *.platform=linux/arm64,linux/amd64
```

Thus, the latest version can also be installed for arm64 and amd64:
```bash
./configure
docker compose pull
```

_Note:_ This relies upon MongoDB, which no longer officially supports binaries for ARM architectures below 8.2.
Thus, for arm64v8 systems, a [community build of MongoDB](https://hub.docker.com/r/arm64v8/mongo) is substituted.
See #60 for more information

## Topology & Docker Containers
CubeServer is built upon the containerization platform Docker. As described in docker-compose.yml, CubeServer is essentially comprised of the following parts as Docker containers:
- CubeServer-app
  - The web app, served by GUnicorn and Flask.
- CubeServer-api
  - The API for Cubes, also served by GUnicorn and Flask
- CubeServer-mongodb
  - A standalone MongoDB server, central to the other containers
- CubeServer-accesspoint
  - The container from which the WiFi access point and routing is taken care of to allow Cubes to connect to the API.

Files used for building each of these containers (other than CubeServer-mongodb, which is prebuilt) may be found in Docker/.

## Customization:
The rules and workings of the "game" may be customized and/or modified as described in [CUSTOMIZATION.md](./CUSTOMIZATION.md).

## Todos:
CubeServer development is tracked by this [GitHub Project](https://github.com/orgs/Windham-High-School/projects/1)
