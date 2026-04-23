IMAGE_REMOTE = bezriska/cloring-web-test:1.6.0@sha256:13f696bdf9b13f0950dfa5c237509bec964159fa1dd9e480272ea93601b54f4c
IMAGE_LOCAL  = cloring-web:local
CLUSTER_NODE = desktop-control-plane

# Задание 1: ConfigMap и Secret
# Применяет configmap.yaml и secret.yaml
lab1: load-image
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/pvc.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl rollout status deployment/cloring-web
	kubectl port-forward svc/cloring-web 8080:5000

# Задание 2: Ingress
# Устанавливает Nginx Ingress Controller и применяет ingress.yaml
lab2: lab1 install-ingress add-hosts
	kubectl apply -f k8s/ingress.yaml
	@echo "Приложение доступно по адресу: http://cloring.local"

# Задание 3: Мониторинг (Prometheus + Fluentd)
# Применяет манифесты Prometheus и Fluentd
lab3: apply-monitoring
	@echo "Prometheus будет доступен на localhost:9090 после: make forward-prometheus"

# Задание 4: HPA (Horizontal Pod Autoscaler)
# Применяет hpa.yaml и запускает нагрузочный тест
lab4:
	kubectl apply -f k8s/hpa.yaml
	@echo "HPA создан. Запускаем нагрузочный тест..."
	$(MAKE) load-test
	@echo "Наблюдайте за масштабированием: make hpa-status"
	@echo "Для остановки теста: make stop-load-test"

# Запустить всё (все задания)

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
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/hpa.yaml
	kubectl rollout status deployment/cloring-web

# Установить Nginx Ingress Controller (только один раз)
install-ingress:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml
	kubectl wait --namespace ingress-nginx \
	  --for=condition=ready pod \
	  --selector=app.kubernetes.io/component=controller \
	  --timeout=120s

# Добавить cloring.local в /etc/hosts (нужен sudo)
add-hosts:
	echo "127.0.0.1 cloring.local" | sudo tee -a /etc/hosts

# Установить мониторинг (Prometheus + Fluentd)
apply-monitoring:
	kubectl apply -f k8s/prometheus-configmap.yaml
	kubectl apply -f k8s/prometheus.yaml
	kubectl apply -f k8s/fluentd-configmap.yaml
	kubectl apply -f k8s/fluentd-daemonset.yaml

# Удалить мониторинг
delete-monitoring:
	kubectl delete -f k8s/prometheus.yaml --ignore-not-found
	kubectl delete -f k8s/prometheus-configmap.yaml --ignore-not-found
	kubectl delete -f k8s/fluentd-daemonset.yaml --ignore-not-found
	kubectl delete -f k8s/fluentd-configmap.yaml --ignore-not-found

# Открыть доступ к Prometheus на localhost:9090
forward-prometheus:
	kubectl port-forward svc/prometheus 9090:9090

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
	kubectl get pods,svc,pvc,ingress,hpa -l app=cloring-web

# Посмотреть статус HPA
hpa-status:
	kubectl get hpa cloring-web-hpa
	kubectl describe hpa cloring-web-hpa

# Создать нагрузку для проверки HPA
load-test:
	kubectl run load-generator --image=busybox --restart=Never -- \
	  /bin/sh -c "while true; do wget -q -O- http://cloring-web:5000/; done"

# Остановить нагрузочный тест
stop-load-test:
	kubectl delete pod load-generator --ignore-not-found

# Посмотреть логи
logs:
	kubectl logs -l app=cloring-web --follow

# Посмотреть логи Fluentd
logs-fluentd:
	kubectl logs -l app=fluentd --follow

.PHONY: lab1 lab2 lab3 lab4 up down apply install-ingress add-hosts apply-monitoring delete-monitoring \
        forward-prometheus load-image forward status hpa-status load-test stop-load-test \
        logs logs-fluentd
