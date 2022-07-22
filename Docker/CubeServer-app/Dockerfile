FROM python:3.10-slim-bullseye

COPY Docker/CubeServer-app/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Common dependency:
COPY src/CubeServer-common/ /tmp/common
RUN pip3 install /tmp/common
RUN rm -r /tmp/common

# Entrypoint:
COPY Docker/CubeServer-app/gunicorn_start.sh /
RUN chmod +x /gunicorn_start.sh

ENTRYPOINT [ "/gunicorn_start.sh" ]

# Webapp itself:
COPY src/CubeServer-app/ /app/
RUN pip3 install /app
