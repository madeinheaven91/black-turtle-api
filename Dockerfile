# syntax=docker/dockerfile:1
FROM python:3.13-rc-alpine
WORKDIR /code
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3003
COPY . .
CMD BOT_TOKEN=(INSERT BOT TOKEN) python3 main.py
