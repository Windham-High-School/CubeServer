FROM mcr.microsoft.com/devcontainers/python:0-3.11 as base

ENV APP_HOME /code

WORKDIR $APP_HOME

RUN python -m venv /code/.venv-api
RUN python -m venv /code/.venv-app

COPY ./src/CubeServer-common/requirements.txt ./requirements-common.txt
COPY ./src/CubeServer-api/requirements.txt ./requirements-api.txt
COPY ./src/CubeServer-app/requirements.txt ./requirements-app.txt

RUN .venv-api/bin/pip install -r requirements-common.txt -r requirements-api.txt
RUN .venv-app/bin/pip install -r requirements-common.txt -r requirements-app.txt

COPY ./src/CubeServer-common/cubeserver_common ./cubeserver_common
COPY ./src/CubeServer-api/cubeserver_api ./cubeserver_api
COPY ./src/CubeServer-api/cubeserver_app ./cubeserver_app

ARG LOGLEVEL
ENV LOGLEVEL=${LOGLEVEL}

COPY Docker/CubeServer/CubeServer-api/gunicorn.conf.py ./api.conf.py
COPY Docker/CubeServer/CubeServer-app/gunicorn.conf.py ./app.conf.py

#---
FROM combined as api

COPY Docker/CubeServer/CubeServer-api/gunicorn_start.sh /code/api_start.sh

ENTRYPOINT /code/api_start.sh

#---
FROM combined as app

COPY Docker/CubeServer/CubeServer-app/gunicorn_start.sh /code/app_start.sh

ENTRYPOINT /code/app_start.sh