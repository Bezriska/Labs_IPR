ENV        ?= dev
NAMESPACE  ?= $(ENV)
IMAGE_NAME  = cloring-web
IMAGE_TAG  ?= $(ENV)
CLUSTER_NODE ?= desktop-control-plane

HELM_INFRA_CHART  = ./infra/helm/postgresql
HELM_APP_CHART    = ./k8s/helm/cloring
KUST_INFRA        = ./infra/kustomize/overlays/$(ENV)
KUST_APP          = ./k8s/kustomization/overlays/$(ENV)


# Быстрый старт

## Поднять всё (инфра + приложение) через Helm для выбранного ENV
up: build load-image load-pg-image infra-up app-up forward
	@echo "Приложение доступно: http://localhost:8080  (ENV=$(ENV))"

## Поднять всё через Kustomize для выбранного ENV
up-kust: build load-image infra-up-kust app-up-kust forward
	@echo "Приложение доступно: http://localhost:8080  (ENV=$(ENV))"

## Остановить и удалить всё (Helm)
down: infra-down app-down
	@echo "Namespace $(NAMESPACE) очищен"

## Остановить и удалить всё (Kustomize)
down-kust:
	kubectl delete -k $(KUST_APP)    --ignore-not-found
	kubectl delete -k $(KUST_INFRA)  --ignore-not-found

# Сборка образа

## Собрать Docker-образ
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

## Загрузить образ в кластер (kind / desktop k8s)
load-image:
	docker save $(IMAGE_NAME):$(IMAGE_TAG) | \
	  docker exec -i $(CLUSTER_NODE) ctr --namespace k8s.io images import -

## Загрузить образ в minikube
load-minikube:
	minikube image load $(IMAGE_NAME):$(IMAGE_TAG)

## Загрузить образ PostgreSQL в кластер (kind / desktop k8s)
load-pg-image:
	docker pull postgres:15.3-alpine
	docker save postgres:15.3-alpine | \
	  docker exec -i $(CLUSTER_NODE) ctr --namespace k8s.io images import -

# Инфраструктура (PostgreSQL)

## Создать namespace и задеплоить PostgreSQL через Helm
infra-up:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	helm upgrade --install cloring-pg $(HELM_INFRA_CHART) \
	  -f $(HELM_INFRA_CHART)/values-$(ENV).yaml \
	  --namespace $(NAMESPACE) \
	  --wait --timeout 120s
	@echo "PostgreSQL запущен в namespace=$(NAMESPACE)"

## Задеплоить PostgreSQL через Kustomize
infra-up-kust:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -k $(KUST_INFRA)
	kubectl rollout status deployment/cloring-postgresql -n $(NAMESPACE) --timeout=120s

## Удалить PostgreSQL (Helm)
infra-down:
	helm uninstall cloring-pg --namespace $(NAMESPACE) --ignore-not-found

# Приложение (Flask)

## Задеплоить приложение через Helm
app-up:
	helm upgrade --install cloring $(HELM_APP_CHART) \
	  -f $(HELM_APP_CHART)/values-$(ENV).yaml \
	  --namespace $(NAMESPACE) \
	  --wait --timeout 120s
	@echo "Приложение задеплоено в namespace=$(NAMESPACE)"

## Задеплоить приложение через Kustomize
app-up-kust:
	kubectl apply -k $(KUST_APP)
	kubectl rollout status deployment/cloring-web -n $(NAMESPACE) --timeout=120s

## Удалить приложение (Helm)
app-down:
	helm uninstall cloring --namespace $(NAMESPACE) --ignore-not-found

# Health-checks

## Проверить /healthz backend
health:
	kubectl exec -n $(NAMESPACE) \
	  $$(kubectl get pods -n $(NAMESPACE) -l app=cloring-web -o jsonpath='{.items[0].metadata.name}') \
	  -- python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/healthz').read().decode())"
	@echo ""

## Показать статус всех ресурсов
status:
	@echo "── Pods ──────────────────────────────────────"
	kubectl get pods -n $(NAMESPACE) -o wide
	@echo "── Services / Ingress ────────────────────────"
	kubectl get svc,ingress -n $(NAMESPACE)
	@echo "── PVC ───────────────────────────────────────"
	kubectl get pvc -n $(NAMESPACE)
	@echo "── HPA ───────────────────────────────────────"
	kubectl get hpa -n $(NAMESPACE) 2>/dev/null || true

# Проброс портов

## Пробросить порт приложения на localhost:8080
forward:
	kubectl port-forward -n $(NAMESPACE) svc/cloring-web 8080:5000

## Пробросить порт PostgreSQL на localhost:5432
forward-db:
	kubectl port-forward -n $(NAMESPACE) svc/cloring-postgresql 5432:5432

# Логи

## Логи приложения (follow)
logs:
	kubectl logs -n $(NAMESPACE) -l app=cloring-web --follow

## Логи PostgreSQL (follow)
logs-db:
	kubectl logs -n $(NAMESPACE) -l app=cloring-postgresql --follow

# Helm утилиты

## Проверить рендер Helm-шаблонов инфраструктуры
helm-lint-infra:
	helm lint $(HELM_INFRA_CHART) -f $(HELM_INFRA_CHART)/values-$(ENV).yaml

## Проверить рендер Helm-шаблонов приложения
helm-lint-app:
	helm lint $(HELM_APP_CHART) -f $(HELM_APP_CHART)/values-$(ENV).yaml

## Показать итоговые манифесты Helm (dry-run)
helm-template-infra:
	helm template cloring-pg $(HELM_INFRA_CHART) -f $(HELM_INFRA_CHART)/values-$(ENV).yaml

helm-template-app:
	helm template cloring $(HELM_APP_CHART) -f $(HELM_APP_CHART)/values-$(ENV).yaml

## Показать итоговые манифесты Kustomize (dry-run)
kust-build-infra:
	kubectl kustomize $(KUST_INFRA)

kust-build-app:
	kubectl kustomize $(KUST_APP)

# Ingress

## Установить Nginx Ingress Controller (один раз)
install-ingress:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml
	kubectl wait --namespace ingress-nginx \
	  --for=condition=ready pod \
	  --selector=app.kubernetes.io/component=controller \
	  --timeout=120s

## Добавить cloring.local в /etc/hosts (нужен sudo)
add-hosts:
	echo "127.0.0.1 cloring.local" | sudo tee -a /etc/hosts


.PHONY: up up-kust down down-kust build load-image load-minikube \
        infra-up infra-up-kust infra-down \
        app-up app-up-kust app-down \
        health status forward forward-db logs logs-db \
        helm-lint-infra helm-lint-app helm-template-infra helm-template-app \
        kust-build-infra kust-build-app \
        install-ingress add-hosts help
