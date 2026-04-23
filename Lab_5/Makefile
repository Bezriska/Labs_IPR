IMAGE_REMOTE = bezriska/cloring-web-test:1.6.0@sha256:13f696bdf9b13f0950dfa5c237509bec964159fa1dd9e480272ea93601b54f4c
IMAGE_LOCAL  = cloring-web:local
CLUSTER_NODE = desktop-control-plane

# Запустить всё
up: load-image apply forward

# Остановить и удалить всё
down:
	kubectl delete -f k8s/ --ignore-not-found

# Применить манифесты
apply:
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/pvc.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl rollout status deployment/cloring-web

# Загрузить образ в кластер
load-image:
	docker pull --platform linux/amd64 $(IMAGE_REMOTE)
	docker tag $(IMAGE_REMOTE) $(IMAGE_LOCAL)
	docker save $(IMAGE_LOCAL) | docker exec -i $(CLUSTER_NODE) ctr --namespace k8s.io images import -

# Открыть доступ на localhost:8080
forward:
	kubectl port-forward svc/cloring-web 8080:5000

# Посмотреть статус
status:
	kubectl get pods,svc,pvc -l app=cloring-web

# Посмотреть логи
logs:
	kubectl logs -l app=cloring-web --follow

.PHONY: up down apply load-image forward status logs
