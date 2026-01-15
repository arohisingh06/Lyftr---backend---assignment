# 🚀 Lyftr AI — Containerized Webhook API

A production-grade **FastAPI** service that ingests WhatsApp-like webhooks **exactly once**, verifies **HMAC signatures**, persists messages in **SQLite**, and exposes **query, analytics, health, and metrics** endpoints — all fully containerized with **Docker**.

Built to meet **Lyftr AI’s backend engineering evaluation criteria**.

---

## ✨ Features

### 🔐 Secure Webhook Ingestion
- HMAC-SHA256 signature verification  
- Rejects unsigned or tampered requests  

### ♻️ Idempotent Message Processing
- `message_id` enforced as primary key  
- Same message can be sent multiple times without duplication  

### 🗄️ SQLite Persistence
- Database stored on Docker volume  
- File path: `/data/app.db`  

### 🔍 Searchable & Paginated Message API
- Filter by sender  
- Filter by timestamp  
- Free-text search  

### 📊 Analytics Endpoint
- Total messages  
- Unique senders  
- Top senders  
- First & last message timestamps  

### ❤️ Health Probes
- `/health/live`  
- `/health/ready`  

### 📈 Prometheus Metrics
- HTTP request counters  
- Webhook processing counters  
- Request latency histogram  

### 🧾 Structured JSON Logs
- One JSON log per request  
- Includes:
  - `request_id`
  - `latency_ms`
  - `status`
  - webhook `result`  

### 🐳 Fully Dockerized
- Zero local setup  
- Runs with Docker Compose  

---

## 🛠️ Tech Stack

- **API** → FastAPI  
- **Database** → SQLite  
- **Metrics** → Prometheus client  
- **Logging** → JSON structured logs  
- **Containerization** → Docker & Docker Compose  

---

## ▶️ How to Run

### 1️⃣ Prerequisites
Make sure you have:
- **Docker Desktop** installed and running

---

### 2️⃣ Start the Service

From the project root:

```
docker compose up --build
```
The API will be available at:
```
http://localhost:8000
```
## ❤️ Health Check
```
GET /health/live
GET /health/ready
```

- /health/live → Returns 200 if the app is running
- /health/ready → Returns 200 only if:

   -Database is reachable
   -WEBHOOK_SECRET is set

## 🔐 Webhook API
### Endpoint
```http
POST /webhook
```

### Headers
```http
Content-Type: application/json
X-Signature: <HMAC_SHA256 of raw body using WEBHOOK_SECRET>```
```
### Body
```json
{
  "message_id": "m1",
  "from": "+919876543210",
  "to": "+14155550100",
  "ts": "2025-01-15T10:00:00Z",
  "text": "Hello"
}
```

### Success Response
```json
{
  "status": "ok"
}
```

- Invalid or missing signature → 401

- Invalid payload → 422

- Duplicate message_id → still returns 200 (idempotent)

## 📬 List Messages
```http
GET /messages
```

### Supports:

- limit

- offset

- from

- since

- q

### Example response:
```json
{
  "data": [
    {
      "message_id": "m1",
      "from": "+919876543210",
      "to": "+14155550100",
      "ts": "2025-01-15T10:00:00Z",
      "text": "Hello"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

## 📊 Stats
```
GET /stats
```


### Example:
```json

{
  "total_messages": 1,
  "senders_count": 1,
  "messages_per_sender": [
    { "from": "+919876543210", "count": 1 }
  ],
  "first_message_ts": "2025-01-15T10:00:00Z",
  "last_message_ts": "2025-01-15T10:00:00Z"
}
```

## 📈 Metrics
```http
GET /metrics
```


Returns Prometheus-style metrics including:

- http_requests_total

- webhook_requests_total

- request_latency_ms_*

## 🧠 Design Decisions
### 🔐 HMAC Verification

The webhook body is validated using:
```
HMAC_SHA256(WEBHOOK_SECRET, raw_request_body)
```


and compared against the X-Signature header using constant-time comparison.

### ♻️ Idempotency

message_id is the SQLite primary key.
Duplicate inserts throw an integrity error, which is caught and treated as a valid duplicate request.

### 📄 Pagination

/messages returns both:

- paginated results

- total matching count

so frontends can build proper pagination.

## 🧪 Setup Used

Built using:

- VS Code

- Docker Desktop





