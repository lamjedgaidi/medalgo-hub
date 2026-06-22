# Single-image monolith. Build: docker build -t medalgo-hub .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Dependencies first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static at build time (WhiteNoise serves them).
RUN SECRET_KEY=build DEBUG=False python manage.py collectstatic --noinput

EXPOSE 8000

# Migrate on boot, then serve. For multi-instance prod, run migrate as a
# separate release step instead.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"]
