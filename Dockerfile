FROM python:3.9-slim-buster

WORKDIR /mc/

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN apt-get update \
    && apt-get install --no-install-recommends curl -qy wait-for-it gdal-bin \
    && rm -rf /var/lib/apt/list/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .
