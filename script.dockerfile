FROM python:3.9.10

WORKDIR /app

COPY db /app/db

COPY meta /app/meta

COPY parsers /app/parsers

COPY monitoring_script.py /app

COPY tg_bot /app/tg_bot

COPY requirements.txt /app

RUN python -m pip install --upgrade pip

RUN python -m pip install -r requirements.txt