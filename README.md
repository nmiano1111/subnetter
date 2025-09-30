# 🌐 Subnetter – IP Address Management Service

Subnetter is a prototype **[IP Address Management (IPAM)](https://netboxlabs.com/docs/netbox/features/ipam/?utm_source=chatgpt.com)** service built with **[FastAPI](https://fastapi.tiangolo.com/)** and **[PostgreSQL](https://www.postgresql.org/)**.  
It provides APIs for managing:

- **Tenants** – logical groups of VRFs  
- **VRFs (Virtual Routing and Forwarding instances)** – isolated routing domains  
- **Prefixes** – network blocks (CIDR ranges) with hierarchy and overlap checks  
- **IP Addresses** – individual IP allocations within prefixes  

A companion **Go CLI** (based on Cobra) is included to exercise the API.



## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)  
- **Database**: [PostgreSQL](https://www.postgresql.org/)  
- **ORM / Models**: [SQLModel](https://sqlmodel.tiangolo.com/) + [SQLAlchemy](https://www.sqlalchemy.org/)  
- **CLI**: [Go](https://go.dev/) with [Cobra](https://cobra.dev/)  
- **Containerization**: Docker, Docker Compose  
- **Kubernetes (local)**: [Kind](https://kind.sigs.k8s.io/) for cluster-based deployments  



## ✨ Features

- Multi-tenant IPAM model  
- Create, update, delete, list tenants, VRFs, prefixes, and IPs  
- Carve sub-prefixes from a parent prefix  
- Allocate the next free IP in a prefix  
- REST API powered by FastAPI  
- Backed by PostgreSQL with async SQLAlchemy / SQLModel  
- CLI for testing and demos  



## 🐳 Running with Docker Compose

### 1. Create `.env`

Create a file called .env in the project root (see .env.example)

### 2. Start service

```bash
docker compose up --build
```

This will start:
    
* api: FastAPI app (http://localhost:8000)
* db: PostgreSQL database

### 3. 📖 API docs

Once running, you can explore the API at:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc


## 👁️ Observability: Prometheus & Grafana

The `subnetter` service exposes runtime and application metrics in
[Prometheus format](https://prometheus.io/docs/instrumenting/exposition_formats/) at
[`/metrics`](http://localhost:8001/metrics).

_*note: currently only configured to work with the docker-compose method of running the app*_

## Running the observability stack

Prometheus and Grafana are defined in a separate compose file:  
`docker-compose.observability.yml`

This allows you to run observability tools independently of the core application.

Bring up the base stack (API + DB):

```bash
make app-up
```

Then start the observability stack:

```bash
make obs-up
```

### Services

Prometheus → http://localhost:9090

Grafana → http://localhost:3000
 (login admin / admin by default)

Prometheus is configured to scrape the API container on the internal Docker network:

```yaml
scrape_configs:
  - job_name: "subnetter"
    metrics_path: /metrics
    static_configs:
      - targets: ["api:8000"]
```


## ☸️ Running Subnetter on Kubernetes with Kind

This section covers how to run the Subnetter service inside a local [Kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker) cluster.


### ⚙️ Setup


#### 1. Create the Kind cluster (uses `kind.yaml` for cluster config):

```bash
make kind-create
````

#### 2. Build and load the API image into Kind:

```bash
make kind-load 
```

#### 3. Deploy to Kubernetes (namespace, config, Postgres, API):

```bash
make k8s-apply
```

#### 4. Port-forward the API service:

```bash
make port-forward
# → FastAPI available at http://localhost:8000/docs
```


### 🔍 Viewing Pods

Check the status of the pods in the ipam namespace:

```bash
kubectl get pods -n ipam
```

Example output:

```bash
NAME                          READY   STATUS    RESTARTS   AGE
ipam-api-7c78f9dd8c-xgkns     1/1     Running   0          2m
ipam-postgres-0               1/1     Running   0          2m
```

Forward port to access api:

```bash
kubectl -n ipam port-forward svc/ipam-api 8000:8000
```


### 🛠 Helpful variations

* All namespaces:
    ```bash
    kubectl get pods -A 
    ```
* Watch pods continuously:
    ```bash
    kubectl get pods -n ipam -w 
    ```
* Describe a pod:
    ```bash
    kubectl describe pod ipam-api-7c78f9dd8c-xgkns -n ipam 
    ```
* Get logs
    ```bash
    kubectl logs -n ipam ipam-api-7c78f9dd8c-xgkns 
    ```


### 🧹 Cleanup 

Delete the deployment and cluster when finished:

```bash
make k8s-delete
make kind-delete
```



## 💻 Go CLI

A [Cobra](https://cobra.dev/)-based CLI is included under cli/.

### 1. Build the CLI

```bash
cd cli
go build -o subnetter
```

### 2. Run the CLI

Example commands:

```bash
# Create a tenant
./subnetter tenant create --name DemoTenant

# Create a VRF for that tenant
./subnetter vrf create --tenant-id <tenant-uuid> --name DemoVRF

# Create a prefix
./subnetter prefix create --vrf-id <vrf-uuid> --cidr 10.0.0.0/24

# Allocate the next free IP
./subnetter ip allocate --prefix-id <prefix-uuid>

# See `help` for more
./subnetter -help
```