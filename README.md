# Subnetter – IP Address Management Service

Subnetter is a prototype **[IP Address Management (IPAM)](https://netboxlabs.com/docs/netbox/features/ipam/?utm_source=chatgpt.com)** service built with **[FastAPI](https://fastapi.tiangolo.com/)** and **[PostgreSQL](https://www.postgresql.org/)**.  
It provides APIs for managing:

- **Tenants** – logical groups of VRFs  
- **VRFs (Virtual Routing and Forwarding instances)** – isolated routing domains  
- **Prefixes** – network blocks (CIDR ranges) with hierarchy and overlap checks  
- **IP Addresses** – individual IP allocations within prefixes  

A companion **Go CLI** (based on Cobra) is included to exercise the API.

---

## Features

- Multi-tenant IPAM model  
- Create, update, delete, list tenants, VRFs, prefixes, and IPs  
- Carve sub-prefixes from a parent prefix  
- Allocate the next free IP in a prefix  
- REST API powered by FastAPI  
- Backed by PostgreSQL with async SQLAlchemy / SQLModel  
- CLI for testing and demos  

---
## Running Subnetter on Kubernetes with Kind

This section covers how to run the Subnetter service inside a local [Kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker) cluster.

---

### Setup

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

### Viewing Pods

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

### Helpful variations

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

### Cleanup 

Delete the deployment and cluster when finished:

```bash
make k8s-delete
make kind-delete
```

---

## Running with Docker Compose

### 1. Create `.env`

Create a file called .env in the project root (see .env.example)

### 2. Start service

```bash
docker compose up --build
```

This will start:
    
* api: FastAPI app (http://localhost:8000)
* db: PostgreSQL database

### 3. API docs

Once running, you can explore the API at:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc

---

## Go CLI

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