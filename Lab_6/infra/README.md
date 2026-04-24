# PostgreSQL Infrastructure — Cloring App

## Контракт для приложения

Приложение ожидает переменную окружения **`DATABASE_URL`** в формате:

```
postgresql://<user>:<password>@<host>:<port>/<dbname>
```

| Окружение | Значение DATABASE_URL |
|-----------|-----------------------|
| dev       | `postgresql://cloring:devpassword@cloring-postgresql:5432/cloring_dev` |
| prod      | `postgresql://cloring:${POSTGRES_PASSWORD}@cloring-postgresql:5432/cloring_prod` |

> В **prod** пароль берётся из Kubernetes Secret и НЕ хранится в репозитории.

---

## Структура

```
infra/
├── helm/
│   └── postgresql/
│       ├── Chart.yaml
│       ├── values.yaml          # базовые значения
│       ├── values-dev.yaml      # переопределения для dev
│       ├── values-prod.yaml     # переопределения для prod
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── secret.yaml
│           └── pvc.yaml
└── kustomize/
    ├── base/
    │   ├── kustomization.yaml
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── secret.yaml
    │   └── pvc.yaml
    └── overlays/
        ├── dev/
        │   └── kustomization.yaml
        └── prod/
            └── kustomization.yaml
```

---

## Порядок деплоя

### Вариант A — Helm

```bash
# dev
helm upgrade --install cloring-pg ./infra/helm/postgresql \
  -f ./infra/helm/postgresql/values-dev.yaml \
  --namespace dev --create-namespace

# prod (пароль передаётся через --set или отдельный Secret)
helm upgrade --install cloring-pg ./infra/helm/postgresql \
  -f ./infra/helm/postgresql/values-prod.yaml \
  --set postgresql.password="${POSTGRES_PASSWORD}" \
  --namespace prod --create-namespace
```

### Вариант B — Kustomize

```bash
# dev
kubectl apply -k ./infra/kustomize/overlays/dev

# prod
kubectl apply -k ./infra/kustomize/overlays/prod
```

### Проверка готовности

```bash
kubectl get pods -n dev
kubectl logs -n dev -l app=cloring-postgresql
kubectl exec -n dev -it deploy/cloring-postgresql -- psql -U cloring -d cloring_dev -c '\l'
```

---

## Health-check PostgreSQL

Pod содержит `livenessProbe` и `readinessProbe` через `pg_isready`:

```yaml
livenessProbe:
  exec:
    command: ["pg_isready", "-U", "$(POSTGRES_USER)"]
readinessProbe:
  exec:
    command: ["pg_isready", "-U", "$(POSTGRES_USER)"]
```
