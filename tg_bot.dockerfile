FROM python:3.9.10

WORKDIR /app

COPY tg_bot /app/tg_bot

COPY meta /app/meta

COPY db /app/db

COPY requirements.txt /app

RUN python -m pip install --upgrade pip

RUN python -m pip install -r requirements.txt