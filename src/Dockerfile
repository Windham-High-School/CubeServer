FROM tiangolo/uwsgi-nginx-flask:python3.8
# RUN apk --update add bash
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./webapp/ /app/

RUN pip3 install /app

WORKDIR /app
