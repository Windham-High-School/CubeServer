FROM tiangolo/uwsgi-nginx-flask:python3.8
# RUN apk --update add bash
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip3 install -r /var/www/requirements.txt

COPY ./app/uwsgi.ini /app/uwsgi.ini
COPY ./app /app
WORKDIR /app
