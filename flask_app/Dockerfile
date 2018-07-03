#FROM ubuntu:16.04
FROM debian:latest


RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade

RUN apt-get update
RUN apt-get -y install python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install uwsgi -I --no-cache-dir
RUN apt-get update && apt-get install -y supervisor \
        && rm -rf /var/lib/apt/lists/*

ENV APP_DIR /app

COPY requirements.txt /tmp

RUN pip3 install --no-cache-dir --upgrade --requirement /tmp/requirements.txt

COPY supervisord.conf /etc/supervisord.conf
COPY uwsgi.ini /etc/uwsgi/wsgi.ini


WORKDIR ${APP_DIR}

COPY . /app
WORKDIR /app

ENV FLASK_DEBUG 1
ENV PYTHONUNBUFFERED 1
ENV APP_SETTINGS config.Config

EXPOSE 5777


ENTRYPOINT ["/usr/bin/supervisord"]