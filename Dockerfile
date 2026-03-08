FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "gunicorn -w 4 -b 0.0.0.0:${APP_PORT} app:app"