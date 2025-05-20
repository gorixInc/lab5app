FROM python:3.12-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p ./static/images

COPY . .

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["flask", "run"]
