FROM tiangolo/uwsgi-nginx-flask:python3.10
# RUN apk --update add bash
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# Common dependency:
COPY ./src/CubeServer-common/ /tmp/common
RUN pip3 install /tmp/common
RUN rm -r /tmp/common

# Webapp itself:
COPY ./src/CubeServer-app/ /app/
RUN pip3 install .
