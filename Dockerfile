FROM python:3.11-slim

RUN apt-get update && apt-get install -y python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .


CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]