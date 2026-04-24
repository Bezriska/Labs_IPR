# Lab 6 — Cloring: Kustomize + Helm + PostgreSQL

## Структура репозитория

```
Lab_6/
├── Dockerfile
├── requirements.txt
├── src/                        # Flask-приложение (SQLite → PostgreSQL)
│   ├── db.py                   # psycopg2 + DATABASE_URL
│   ├── run.py                  # /healthz endpoint добавлен
│   └── ...
├── templates/
├── infra/                      # PostgreSQL-инфраструктура (НЕ содержит манифестов приложения)
│   ├── README.md               # Контракт DATABASE_URL
│   ├── helm/postgresql/        # Helm-чарт PostgreSQL
│   │   ├── values-dev.yaml
│   │   └── values-prod.yaml
│   └── kustomize/              # Kustomize-вариант PostgreSQL
│       ├── base/
│       └── overlays/{dev,prod}/
└── k8s/                        # Манифесты приложения (БД — НЕ здесь)
    ├── kustomization/
    │   ├── base/               # Deployment, Service, ConfigMap, Ingress
    │   └── overlays/
    │       ├── dev/            # Secret (SECRET_KEY), PVC, патч replicas/image
    │       └── prod/           # Secret (SECRET_KEY), PVC, патч replicas/resources
    └── helm/
        └── cloring/
            ├── values-dev.yaml
            ├── values-prod.yaml
            └── templates/
```

---

## Контракт DATABASE_URL

Приложение читает **`DATABASE_URL`** из переменной окружения.  
Формат: `postgresql://<user>:<password>@<host>:<port>/<dbname>`

| Окружение | DATABASE_URL |
|-----------|--------------|
| dev  | `postgresql://cloring:devpassword@cloring-postgresql:5432/cloring_dev` |
| prod | `postgresql://cloring:<STRONG_PASSWORD>@cloring-postgresql:5432/cloring_prod` |

Значение хранится в `Secret` с именем **`cloring-pg-secret`**, создаваемом инфраструктурой.  
Приложение монтирует его через `secretKeyRef` — **не дублирует** в своих манифестах.

---

## Порядок деплоя (dev, вариант Helm)

### 1. Создать namespace

```bash
kubectl create namespace dev
```

### 2. Поднять инфраструктуру (PostgreSQL)

```bash
helm upgrade --install cloring-pg ./infra/helm/postgresql \
  -f ./infra/helm/postgresql/values-dev.yaml \
  --namespace dev

# Дождаться готовности
kubectl rollout status deployment/cloring-postgresql -n dev
kubectl get pods -n dev
```

### 3. Собрать образ приложения

```bash
# minikube
eval $(minikube docker-env)
docker build -t cloring-web:dev .
```

### 4. Поднять приложение

```bash
helm upgrade --install cloring ./k8s/helm/cloring \
  -f ./k8s/helm/cloring/values-dev.yaml \
  --namespace dev

# или через Kustomize:
kubectl apply -k ./k8s/kustomization/overlays/dev
```

### 5. Проверить health-checks

```bash
# Статус подов
kubectl get pods -n dev

# Health-check backend
kubectl exec -n dev deploy/cloring-web -- \
  wget -qO- http://localhost:5000/healthz
# Ожидаемый ответ: {"status":"ok"}

# Логи
kubectl logs -n dev -l app=cloring-web --tail=30

# Проброс порта для доступа к frontend
kubectl port-forward -n dev svc/cloring-web 8080:5000
# Открыть: http://localhost:8080
```

---

## Порядок деплоя (prod, вариант Helm)

```bash
kubectl create namespace prod

# Инфраструктура (пароль не хранится в values-prod.yaml)
helm upgrade --install cloring-pg ./infra/helm/postgresql \
  -f ./infra/helm/postgresql/values-prod.yaml \
  --set postgresql.password="${POSTGRES_PASSWORD}" \
  --namespace prod

# Ожидаем готовности PostgreSQL
kubectl rollout status deployment/cloring-postgresql -n prod

# Приложение
helm upgrade --install cloring ./k8s/helm/cloring \
  -f ./k8s/helm/cloring/values-prod.yaml \
  --set app.secretKey="${APP_SECRET_KEY}" \
  --namespace prod

kubectl rollout status deployment/cloring-web -n prod
```

---

## Порядок деплоя (Kustomize)

```bash
# dev
kubectl apply -k ./infra/kustomize/overlays/dev
kubectl apply -k ./k8s/kustomization/overlays/dev

# prod — сначала создать Secret вручную
kubectl create secret generic cloring-pg-secret \
  --from-literal=POSTGRES_USER=cloring \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  --from-literal=POSTGRES_DB=cloring_prod \
  --from-literal=DATABASE_URL="postgresql://cloring:${POSTGRES_PASSWORD}@cloring-postgresql:5432/cloring_prod" \
  -n prod

kubectl create secret generic cloring-secret \
  --from-literal=SECRET_KEY="${APP_SECRET_KEY}" \
  -n prod

kubectl apply -k ./infra/kustomize/overlays/prod
kubectl apply -k ./k8s/kustomization/overlays/prod
```

---

## Ключевые изменения относительно Lab 5

| Было (Lab 5) | Стало (Lab 6) |
|---|---|
| SQLite (`sqlite3`) | PostgreSQL (`psycopg2`) |
| `DATABASE_PATH=/app/data/database.db` | `DATABASE_URL=postgresql://...` |
| Единственный набор манифестов | kustomization/base + overlays/dev + overlays/prod |
| Нет Helm-чарта | `k8s/helm/cloring` с `values-dev/prod.yaml` |
| Нет инфраструктурного репо | `infra/` с PostgreSQL Helm + Kustomize |
| Нет `/healthz` | `GET /healthz` → `{"status":"ok"}` |
