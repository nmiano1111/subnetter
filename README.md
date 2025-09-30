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

## Running with Docker Compose

### 1. Clone and set up

```bash
git clone https://github.com/yourname/subnetter.git
cd subnetter
```

### 2. Create `.env`

Create a file called .env in the project root (see .env.example)

### 3. Start service

```bash
docker compose up --build
```

This will start:
    
* api: FastAPI app (http://localhost:8000)
* db: PostgreSQL database

### 4. API docs

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