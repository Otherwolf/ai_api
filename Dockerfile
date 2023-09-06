FROM python:3.9.8-slim-buster

RUN apt-get update \
  && apt-get install -y curl gnupg g++ \
  && apt-get install -y libgssapi-krb5-2 \
  && apt-get install -y libpq-dev \
  && apt-get autoremove -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /my_app/
COPY . ./

RUN pip install --upgrade pip && pip install -r req.txt
