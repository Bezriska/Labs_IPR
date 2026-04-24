FROM python:3.13-slim

WORKDIR /app

# Копирование только requirements.txt для кеширования слоя
COPY requirements.txt .

# Установка зависимостей (psycopg2-binary включён для PostgreSQL)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY src/ ./src/
COPY templates/ ./templates/

# Создание необходимых директорий и добавление нового пользователя
RUN mkdir -p /app/static/uploads && \
    useradd -m -u 1000 webuser && \
    chown -R webuser:webuser /app

# Lab 6: DATABASE_URL для PostgreSQL; DATABASE_PATH удалён
ENV UPLOAD_FOLDER=/app/static/uploads \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

VOLUME /app/static/uploads

USER webuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/healthz'); print('ok')" || exit 1

CMD ["python", "src/run.py"]
