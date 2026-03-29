# Flask + FastAPI ETL Pipeline

A microservices-based ETL (Extract, Transform, Load) pipeline that fetches customer data from a mock REST API and stores it in a PostgreSQL database.

---

## Architecture

```
┌─────────────────┐        HTTP        ┌──────────────────────┐        SQL        ┌──────────────┐
│   mock-server   │ ◄────────────────► │   pipeline-service   │ ────────────────► │  PostgreSQL  │
│   (Flask)       │   /api/customers   │   (FastAPI)          │                   │  Database    │
│   Port: 5000    │                    │   Port: 8000         │                   │              │
└─────────────────┘                    └──────────────────────┘                   └──────────────┘
```

### Services

| Service | Framework | Port | Role |
|---|---|---|---|
| `mock-server` | Flask | 5000 | Fake data source — serves customer records via REST API |
| `pipeline-service` | FastAPI | 8000 | ETL engine — fetches, transforms, and loads data into PostgreSQL |

---

## Tech Stack

| Category | Technology |
|---|---|
| Backend API (Pipeline) | FastAPI |
| Backend API (Mock) | Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| DB Driver | psycopg2 |
| HTTP Client | Requests |
| ASGI Server | Uvicorn |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Image Registry | Docker Hub |
| Language | Python 3.10 |

---

## Project Structure

```
flask-fastapi-etl-pipeline/
├── mock-server/
│   ├── app.py                  # Flask app — serves customer data
│   ├── Dockerfile
│   ├── requirements.txt
│   └── data/
│       └── customers.json      # Sample customer records
│
├── pipeline-service/
│   ├── main.py                 # FastAPI app — ETL endpoints
│   ├── database.py             # SQLAlchemy engine & session setup
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── models/
│   │   └── customer.py         # Customer DB model
│   └── services/
│       └── ingestion.py        # Fetches all pages from mock-server
│
└── .github/
    └── workflows/
        └── docker.yml          # CI/CD — builds & pushes Docker images
```

---

## How It Works (ETL Flow)

1. **Extract** — `pipeline-service` calls `mock-server` at `http://mock-server:5000/api/customers` with pagination
2. **Transform** — checks if customer already exists (upsert logic)
3. **Load** — inserts new records or updates existing ones in PostgreSQL

---

## API Endpoints

### mock-server (Port 5000)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/customers` | List customers with pagination (`?page=1&limit=10`) |
| GET | `/api/customers/<id>` | Get single customer by ID |
| GET | `/api/health` | Health check |

### pipeline-service (Port 8000)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ingest` | Trigger ETL — fetch from mock-server and load into PostgreSQL |
| GET | `/api/customers` | List customers from DB (`?page=1&limit=10`) |
| GET | `/api/customers/{id}` | Get single customer from DB |

---

## Customer Data Model

```
customer_id     String (Primary Key)
first_name      String
last_name       String
email           String
phone           String
address         String
date_of_birth   Date
account_balance Decimal
created_at      Timestamp
```

---

## Running Locally with Docker

### Step 1 — Build Images

```bash
docker build -t flask-fast-api:mock ./mock-server
docker build -t flask-fast-api:pipeline ./pipeline-service
```

### Step 2 — Create a Docker Network

```bash
docker network create etl-network
```

### Step 3 — Run mock-server

```bash
docker run -d \
  --name mock-server \
  --network etl-network \
  -p 5000:5000 \
  flask-fast-api:mock
```

### Step 4 — Run pipeline-service

```bash
docker run -d \
  --name pipeline-service \
  --network etl-network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@<db-host>:5432/dbname \
  flask-fast-api:pipeline
```

### Step 5 — Trigger the ETL

```bash
curl -X POST http://localhost:8000/api/ingest
```

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | pipeline-service | PostgreSQL connection string e.g. `postgresql://user:pass@host:5432/db` |

---

## CI/CD — GitHub Actions

On every push to `main` branch, the workflow automatically:

1. Builds `mock-server` Docker image
2. Pushes it to Docker Hub as `7838nisha/flask-fast-api:mock`
3. Builds `pipeline-service` Docker image
4. Pushes it to Docker Hub as `7838nisha/flask-fast-api:pipeline`

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `USER_NAME` | Docker Hub username |
| `SECRET_TOKEN` | Docker Hub access token |

---

## Docker Hub Images

```
7838nisha/flask-fast-api:mock       # Flask mock server
7838nisha/flask-fast-api:pipeline   # FastAPI pipeline service
```
