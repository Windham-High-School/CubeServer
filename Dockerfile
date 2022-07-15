FROM tiangolo/uwsgi-nginx-flask:python3.10
# RUN apk --update add bash
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./src/webapp/ /app/
RUN pip3 install .
