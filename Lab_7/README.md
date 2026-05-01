# Лабораторная 7 — Метрики, трейсинг, Prometheus, Tempo, Grafana

## Структура проекта

```
Lab_7/
├── docker-compose.yaml              # все сервисы: app, db, prometheus, tempo, grafana
├── Dockerfile                       # сборка Flask-приложения
├── requirements.txt
├── prometheus/
│   └── prometheus.yml               # scrape configs (job: app, prometheus)
├── tempo/
│   └── tempo.yaml                   # конфигурация Grafana Tempo (OTLP HTTP/gRPC + storage)
├── grafana/
│   ├── datasources.yaml             # автопровижининг Prometheus + Tempo
│   ├── dashboard-provisioning.yaml  # автопровижининг дашборда
│   └── dashboards/
│       └── backend.json             # дашборд "Cloring Backend" с PromQL-панелями
├── src/
│   ├── run.py                       # Flask-приложение: /metrics, OTLP-трейсинг
│   └── ...
└── docs/
    └── screenshots/lab7/            # скриншоты для отчёта
```

## Реализация

### Метрики (`/metrics`)
- **HTTP counter + histogram** — через `prometheus-flask-exporter`, label = Flask endpoint (шаблон маршрута, не произвольный path с ID)
- **Бизнес-метрика 1** — `user_registrations_total`: счётчик успешных регистраций
- **Бизнес-метрика 2** — `items_donated_total`: счётчик добавленных вещей
- **app_info** — gauge с версией приложения

### Трейсинг (OTLP → Tempo)
- Экспорт через `opentelemetry-instrumentation-flask` по протоколу OTLP HTTP
- **Опционален**: если переменная `OTLP_ENDPOINT` не задана — приложение работает без трейсинга
- Сервис называется `cloring-flask`

### Grafana
- Datasource **Prometheus** (`http://prometheus:9090`) — по умолчанию
- Datasource **Tempo** (`http://tempo:3200`) — HTTP API Tempo
- Дашборд **Cloring Backend** с панелями:
  - HTTP Request Rate по endpoint и status
  - Latency percentiles p50 / p95
  - 5xx Error Rate
  - Total Registrations, Total Items Donated (бизнес-метрики)
  - Business Events Rate (per minute)

---

## Как воспроизвести

### 1. Запуск

```bash
docker compose up -d --build
```

Дождаться поднятия всех контейнеров (~10 сек):

```bash
docker compose ps
```

### 2. Проверка сервисов

| Сервис | URL |
|---|---|
| Приложение | http://localhost:5001 |
| Метрики | http://localhost:5001/metrics |
| Healthcheck | http://localhost:5001/healthz |
| Prometheus Targets | http://localhost:9090/targets |
| Grafana | http://localhost:3000 (admin / admin) |

### 3. Prometheus — убедиться в UP

Открыть http://localhost:9090/targets — оба job (`app`, `prometheus`) должны быть зелёными **UP**.

### 4. Grafana — дашборд с метриками

1. Открыть http://localhost:3000, войти как `admin` / `admin`
2. Перейти **Dashboards → Cloring Backend**
3. Для появления данных на графиках — сделать несколько запросов к приложению:
   ```bash
   for i in $(seq 1 10); do
     curl -s http://localhost:5001/ > /dev/null
     curl -s http://localhost:5001/sign_in > /dev/null
     curl -s http://localhost:5001/about > /dev/null
   done
   ```

### 5. Grafana — трейсы в Tempo

1. Перейти **Explore → Tempo**
2. Query type: **Search**, нажать **Run query**
3. Выбрать любой trace из списка → кликнуть на span для просмотра атрибутов

### 6. Остановка

```bash
docker compose down
```

---

## Скриншоты

Находятся в `docs/screenshots/lab7/`:

| Файл | Содержимое |
|---|---|
| `*13.22.13*` | Prometheus → Targets, оба job UP |
| `*13.22.32*` | Grafana → Dashboard "Cloring Backend" с метриками |
| `*13.29.21*` | Grafana → Explore → Tempo, развёрнутый trace со span-ами |
