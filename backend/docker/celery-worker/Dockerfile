FROM python:3.13

LABEL authors="e1_m"

WORKDIR /app

COPY pyproject.toml ./

RUN pip install pip-tools
RUN pip-compile pyproject.toml
RUN pip install -r requirements.txt

COPY src src
