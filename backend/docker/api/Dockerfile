FROM python:3.13

LABEL authors="e1_m"

WORKDIR /app

COPY pyproject.toml ./

RUN pip install pip-tools
RUN pip-compile pyproject.toml
RUN pip install -r requirements.txt

COPY src src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]