# Makefile for Subnetter (FastAPI + Postgres + Kind)

CLUSTER_NAME=subnetter
IMAGE_NAME=subnetter-api
IMAGE_TAG=dev
K8S_NS=subnetter

.PHONY: help
help:
	@echo "Available targets:"
	@echo ""
	@echo "App (Docker Compose):"
	@echo "  app-up          Start app and dependencies (API + Postgres)"
	@echo "  app-down        Stop app and remove volumes"
	@echo "  app-logs        Tail logs from the app container"
	@echo ""
	@echo "Kind cluster (Kubernetes-in-Docker):"
	@echo "  kind-create     Create kind cluster"
	@echo "  kind-delete     Delete kind cluster"
	@echo "  docker-build    Build API docker image"
	@echo "  kind-load       Load local docker image into kind"
	@echo "  k8s-apply       Apply all k8s manifests"
	@echo "  k8s-delete      Delete all k8s manifests"
	@echo "  rollout         Restart API deployment"
	@echo "  logs            Tail API logs (in cluster)"
	@echo "  port-forward    Port forward API to localhost:8000"
	@echo "  kind-all        Build, load, and deploy to kind"
	@echo ""
	@echo "Observability (Prometheus + Grafana):"
	@echo "  obs-up          Start observability stack"
	@echo "  obs-down        Stop observability stack and remove volumes"
	@echo "  grafana         Open Grafana UI (http://localhost:3000)"
	@echo "  prometheus      Open Prometheus UI (http://localhost:9090)"

.PHONY: app-up app-down app-logs

# Spin up the app and its dependencies
app-up:
	docker compose up -d --build

# Tear it down
app-down:
	docker compose down -v

# Follow logs from the app container
app-logs:
	docker compose logs -f subnetter

# --- Kind cluster ---

kind-create:
	kind create cluster --name $(CLUSTER_NAME) --config kind.yml

kind-delete:
	kind delete cluster --name $(CLUSTER_NAME)

# --- Docker build + load into kind ---

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

kind-load: docker-build
	kind load docker-image $(IMAGE_NAME):$(IMAGE_TAG) --name $(CLUSTER_NAME)

# --- Kubernetes deploy ---

k8s-apply:
	kubectl apply -f k8s/namespace.yml
	kubectl apply -f k8s/secret.yml
	kubectl apply -f k8s/configmap.yml
	kubectl apply -f k8s/postgres.yml
	kubectl apply -f k8s/api.yml

k8s-delete:
	kubectl delete -f k8s/api.yml || true
	kubectl delete -f k8s/postgres.yml || true
	kubectl delete -f k8s/configmap.yml || true
	kubectl delete -f k8s/secret.yml || true
	kubectl delete -f k8s/namespace.yml || true

rollout:
	kubectl rollout restart deploy/subnetter-api -n $(K8S_NS)

logs:
	kubectl -n $(K8S_NS) logs -f deploy/subnetter-api

port-forward:
	kubectl -n $(K8S_NS) port-forward svc/subnetter-api 8000:8000

# --- Observability stack (Prometheus + Grafana) ---

obs-up:
	docker compose -f docker-compose.observability.yml up -d

obs-down:
	docker compose -f docker-compose.observability.yml down -v

grafana:
	@echo "Opening Grafana at http://localhost:3000"
	@open http://localhost:3000 || xdg-open http://localhost:3000 || true

prometheus:
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || xdg-open http://localhost:9090 || true

# --- One-shot full deploy ---

kind-all: kind-create kind-load k8s-apply

