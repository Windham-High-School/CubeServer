FROM python:3.10-slim-bullseye

# Subject line of the self-signed ssl cert:
ARG CERT_SUBJ
ARG CERT_SUBJALTNAME
ARG CERT_EXP_DAYS

WORKDIR /app

# Helper files:
COPY Docker/CubeServer-api/gen_ssl_cert.sh /
RUN chmod +x /gen_ssl_cert.sh
RUN /gen_ssl_cert.sh ${CERT_SUBJ} ${CERT_SUBJALTNAME} ${CERT_EXP_DAYS}

COPY Docker/CubeServer-api/gunicorn.conf.py /

# Entrypoint:
COPY Docker/CubeServer-api/gunicorn_start.sh /
RUN chmod +x /gunicorn_start.sh
ENTRYPOINT /gunicorn_start.sh

# Requirements:
COPY Docker/CubeServer-api/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Common dependency:
COPY ./src/CubeServer-common/ /tmp/common
RUN pip3 install /tmp/common
RUN rm -r /tmp/common

# API package itself:
COPY ./src/CubeServer-api/ /app/
RUN pip3 install /app
