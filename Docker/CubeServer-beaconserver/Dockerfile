FROM python:3.10-slim-bullseye

# Subject line of the self-signed ssl cert:
ARG CERT_SUBJ
ENV CERT_SUBJ=${CERT_SUBJ}

ARG CERT_SUBJALTNAME
ENV CERT_SUBJALTNAME=${CERT_SUBJALTNAME}

ARG CERT_EXP_DAYS
ENV CERT_EXP_DAYS=${CERT_EXP_DAYS}

WORKDIR /app

# Helper files:
COPY Docker/common/gen_ssl_cert.sh /
RUN chmod +x /gen_ssl_cert.sh
#RUN /gen_ssl_cert.sh ${CERT_SUBJ} ${CERT_SUBJALTNAME} ${CERT_EXP_DAYS} beacon

# Requirements:
COPY Docker/CubeServer-beaconserver/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Common dependency:
COPY ./src/CubeServer-common/ /tmp/common
RUN pip3 install /tmp/common
RUN rm -r /tmp/common

# API package itself:
COPY ./src/CubeServer-beaconserver/ /app/
RUN pip3 install /app

# Entrypoint:
COPY Docker/CubeServer-beaconserver/entrypoint.sh /
RUN chmod +x /entrypoint.sh
CMD ["/usr/bin/env", "bash", "/entrypoint.sh"]
