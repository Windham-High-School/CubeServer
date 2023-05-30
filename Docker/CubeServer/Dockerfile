FROM mcr.microsoft.com/devcontainers/python:0-3.11 as common

ENV APP_HOME /code

WORKDIR $APP_HOME

COPY ./src/CubeServer-common/requirements.txt requirements-common.txt
RUN pip install -r requirements-common.txt

COPY ./src/CubeServer-common/cubeserver_common ./cubeserver_common

#---
FROM common as combined

## -- API --

# Subject line of the self-signed ssl cert:
ARG CERT_SUBJ
ENV CERT_SUBJ=${CERT_SUBJ}

ARG CERT_SUBJALTNAME
ENV CERT_SUBJALTNAME=${CERT_SUBJALTNAME}

ARG CERT_EXP_DAYS
ENV CERT_EXP_DAYS=${CERT_EXP_DAYS}

ARG LOGLEVEL
ENV LOGLEVEL=${LOGLEVEL}

RUN mkdir /CubeServer-api
COPY Docker/CubeServer/CubeServer-api/gunicorn.conf.py \
    Docker/CubeServer/CubeServer-api/gen_ssl_cert.sh \
    Docker/CubeServer/CubeServer-api/setup.sh \
    Docker/CubeServer/CubeServer-api/gunicorn_start.sh /CubeServer-api/
RUN chmod +x /CubeServer-api/gen_ssl_cert.sh \
    && chmod +x /CubeServer-api/setup.sh \
    && chmod +x /CubeServer-api/gunicorn_start.sh

COPY ./src/CubeServer-api/requirements.txt requirements-api.txt
RUN pip install -r requirements-api.txt

COPY ./src/CubeServer-api/cubeserver_api ./cubeserver_api

## -- APP --
RUN mkdir /CubeServer-app
COPY Docker/CubeServer/CubeServer-app/gunicorn.conf.py \
    Docker/CubeServer/CubeServer-app/package_internal.sh \
    Docker/CubeServer/CubeServer-app/package_lib.sh \
    Docker/CubeServer/CubeServer-app/setup.sh \
    Docker/CubeServer/CubeServer-app/gunicorn_start.sh /CubeServer-app/
RUN chmod +x /CubeServer-app/package_lib.sh \
    && chmod +x /CubeServer-app/package_internal.sh \
    && chmod +x /CubeServer-app/setup.sh \
    && chmod +x /CubeServer-app/gunicorn_start.sh

COPY ./src/CubeServer-app/requirements.txt requirements-app.txt
RUN pip install -r requirements-app.txt

COPY ./src/CubeServer-app/cubeserver_app ./cubeserver_app

#---
FROM combined as combined-dev

RUN /CubeServer-api/setup.sh
RUN /CubeServer-app/setup.sh

#---
FROM combined as api

ENTRYPOINT /CubeServer-api/gunicorn_start.sh

#---
FROM combined as app

ENTRYPOINT /CubeServer-app/gunicorn_start.sh