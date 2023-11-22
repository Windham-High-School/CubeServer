ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE} as base

ENV APP_HOME /code

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists

RUN python -m venv /code/.venv-api
RUN python -m venv /code/.venv-app

COPY ./src/CubeServer-common/requirements.txt ./requirements-common.txt
COPY ./src/CubeServer-api/requirements.txt ./requirements-api.txt
COPY ./src/CubeServer-app/requirements.txt ./requirements-app.txt

RUN .venv-api/bin/pip install -r requirements-common.txt -r requirements-api.txt
RUN .venv-app/bin/pip install -r requirements-common.txt -r requirements-app.txt

COPY ./src/CubeServer-common/cubeserver_common ./cubeserver_common
COPY ./src/CubeServer-api/cubeserver_api ./cubeserver_api
COPY ./src/CubeServer-app/cubeserver_app ./cubeserver_app

COPY Docker/CubeServer/CubeServer-app/package_internal.sh ./package_internal.sh
COPY Docker/CubeServer/CubeServer-app/package_lib.sh ./package_lib.sh

ARG LOGLEVEL
ENV LOGLEVEL=${LOGLEVEL}

#---
FROM base as api

COPY Docker/CubeServer/CubeServer-api/gunicorn.conf.py ./api.conf.py
COPY Docker/CubeServer/CubeServer-api/gunicorn_start.sh /code/api_start.sh

ENTRYPOINT /code/api_start.sh

#---
FROM base as app

COPY Docker/CubeServer/CubeServer-app/gunicorn.conf.py ./app.conf.py
COPY Docker/CubeServer/CubeServer-app/gunicorn_start.sh /code/app_start.sh

ENTRYPOINT /code/app_start.sh
