FROM python:3.10-slim-bullseye

COPY Docker/CubeServer-app/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Entrypoint:
COPY Docker/CubeServer-app/gunicorn.conf.py /
COPY Docker/CubeServer-app/gunicorn_start.sh /
RUN chmod +x /gunicorn_start.sh
ENTRYPOINT [ "/gunicorn_start.sh" ]

# Common dependency:
COPY src/CubeServer-common/ /tmp/common
RUN pip3 install /tmp/common
RUN rm -r /tmp/common

# Webapp itself:
COPY src/CubeServer-app/ /app/
RUN pip3 install /app
