FROM python:3.11-slim

# ubuntu pkg 설치
RUN apt-get update \
    && rm -rf /var/lib/apt/lists/* \

# ubuntu working directory 설정
WORKDIR /app

# uv 설치
RUN pip install uv

RUN uv venv --python=3.11

COPY . .
RUN uv sync


# CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]