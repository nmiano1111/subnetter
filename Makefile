# Makefile for Subnetter (FastAPI + Postgres + Kind)

CLUSTER_NAME=subnetter
IMAGE_NAME=subnetter-api
IMAGE_TAG=dev
K8S_NS=ipam

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  kind-create     Create kind cluster"
	@echo "  kind-delete     Delete kind cluster"
	@echo "  docker-build    Build API docker image"
	@echo "  kind-load       Load local docker image into kind"
	@echo "  k8s-apply       Apply all k8s manifests"
	@echo "  k8s-delete      Delete all k8s manifests"
	@echo "  rollout         Restart API deployment"
	@echo "  logs            Tail API logs"
	@echo "  port-forward    Port forward API to localhost:8000"
	@echo "  all             Build, load, deploy"

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
	kubectl rollout restart deploy/ipam-api -n $(K8S_NS)

logs:
	kubectl -n $(K8S_NS) logs -f deploy/ipam-api

port-forward:
	kubectl -n $(K8S_NS) port-forward svc/ipam-api 8000:8000

# --- One-shot full deploy ---

all: kind-create kind-load k8s-apply

