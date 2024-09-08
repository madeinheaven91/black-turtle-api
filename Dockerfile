# syntax=docker/dockerfile:1
FROM python:3.12-rc-alpine

# Locale setup
RUN apk add musl-locales
RUN apk add lang
ENV MUSL_LOCPATH=/usr/share/i18n/locales/musl
ENV LC_TIME=ru_RU.UTF-8

# Project setup
WORKDIR /code
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
CMD python3 main.py
