# customer-pipeline

Built this as a data pipeline exercise — three services talking to each other over Docker.

The idea is simple: Flask acts as a mock backend serving customer records from a JSON file. FastAPI sits in the middle, pulls all that data from Flask, and pushes it into PostgreSQL. Once the data is in the database, you can query it back through FastAPI.

---

## What's inside

```
customer-pipeline/
├── docker-compose.yml
├── mock-server/          # Flask — serves customers from JSON
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── data/
│       └── customers.json
└── pipeline-service/     # FastAPI — ingests into PostgreSQL
    ├── main.py
    ├── database.py
    ├── Dockerfile
    ├── requirements.txt
    ├── models/
    │   └── customer.py
    └── services/
        └── ingestion.py
```

---

## Getting it running

Make sure Docker Desktop is open and running, then:

```bash
git clone <your-repo-url>
cd customer-pipeline
docker-compose up --build
```

First build takes a few minutes — it pulls the Python and PostgreSQL images and installs dependencies. Once you see these three lines you're good:

```
mock_server       |  * Running on http://0.0.0.0:5000
pipeline_service  | INFO: Uvicorn running on http://0.0.0.0:8000
postgres_db       | database system is ready to accept connections
```

---

## Testing it step by step

Open a second terminal and run these in order.

**1. Check Flask is up**
```bash
curl http://localhost:5000/api/health
```
Expected: `{"service": "mock-server", "status": "UP"}`

**2. Pull a page of customers from Flask**
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
```
Expected: first 5 customers with total: 20

**3. Fetch a single customer from Flask**
```bash
curl http://localhost:5000/api/customers/C001
```
Expected: Ravi Kumar's record

**4. Trigger the ingestion**

This is the main one — FastAPI fetches all 20 customers from Flask (handling pagination automatically) and upserts them into PostgreSQL.

```bash
curl -X POST http://localhost:8000/api/ingest
```
Expected: `{"status": "success", "records_processed": 20}`

**5. Query customers from the database**
```bash
curl "http://localhost:8000/api/customers?page=1&limit=5"
```
Expected: same customers, now served from PostgreSQL

**6. Single customer from database**
```bash
curl http://localhost:8000/api/customers/C001
```
Expected: Ravi Kumar's record from PostgreSQL

---

## Endpoints

**Flask mock server — port 5000**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| GET | /api/customers | Paginated list (page, limit) |
| GET | /api/customers/{id} | Single customer, 404 if not found |

**FastAPI pipeline — port 8000**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| POST | /api/ingest | Fetch from Flask, upsert into PostgreSQL |
| GET | /api/customers | Paginated list from database (page, limit) |
| GET | /api/customers/{id} | Single customer from database, 404 if not found |

---

## A few things worth noting

**Pagination** — both services support page and limit params. The ingestion service handles this automatically, keeps looping through Flask pages until there's nothing left to fetch.

**Upsert** — before inserting, it checks if the customer_id already exists. Updates the record if it does, inserts fresh if it doesn't. So you can run /api/ingest multiple times without duplicating data.

**Startup order** — docker-compose has a healthcheck on PostgreSQL. The other two services wait for the DB to be ready before starting, so you don't hit connection errors on boot.

**Port conflict** — if you have PostgreSQL running locally on 5432, change the left side of the port mapping in docker-compose.yml to 5433:5432. The internal container communication stays the same.

---

## Stack

- Python 3.11
- Flask 3.0.3
- FastAPI 0.111.0
- SQLAlchemy 2.0.30
- PostgreSQL 15
- Docker + Docker Compose