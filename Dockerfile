FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

# 디폴트 구동 명령
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
