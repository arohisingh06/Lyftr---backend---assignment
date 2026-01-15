# 🚀 Lyftr AI — Containerized Webhook API

A containerized FastAPI-based backend service designed to receive WhatsApp-style webhook events exactly once, validate request authenticity using HMAC-SHA256, store data in SQLite, and expose clean APIs for retrieval, analytics, health checks, and metrics.

 This project is implemented as part of Lyftr AI’s Backend Engineering Assignment  and follows production-oriented design practices.
---

## ✨ Features

### 🔐 Secure Webhook Ingestion
- Validates incoming requests using HMAC-SHA256 signatures
- Rejects missing, invalid, or tampered signatures
  
### ♻️ Idempotent Message Processing
- `message_id` enforced as a unique primary key
- Repeated webhook calls with the same ID are safely ignore

### 🗄️ SQLite Persistence
- Messages stored in SQLite
- Database backed by a Docker volume  
- File path: `/data/app.db`  

### 🔍 Searchable & Paginated Message API
- Pagination support
- Filter by sender (from)
- Filter by timestamp (since)
- Case-insensitive text search 

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
  - HTTP `status`
  - webhook processing `result`  

### 🐳 Fully Dockerized
- No local Python setup required
- Runs fully using Docker Compose 

---

## 🛠️ Tech Stack

- **API** → FastAPI  
- **Database** → SQLite  
- **Metrics** → Prometheus client  
- **Logging** → JSON structured logs  
- **Containerization** → Docker & Docker Compose  

---

## ▶️ Running the Application

### 1️⃣ Prerequisites
Ensure the following is installed and running
- **Docker Desktop** 

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

- Invalid or missing signature → 401 Unauthorized

- Invalid payload → 422 Validation Error

- Duplicate `message_id` →  200  OK(idempotent behaviour)

## 📬 List Messages API
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


Returns Prometheus-compatible metrics such as:

- http_requests_total

- webhook_requests_total

- request_latency_ms_*

## 🧠 Design Notes
### 🔐 Signature Verification

Incoming webhook payloads are validated using:
```
HMAC_SHA256(WEBHOOK_SECRET, raw_request_body)
```

The computed signature is compared with the X-Signature header using constant-time comparison to prevent timing attacks.

### ♻️ Idempotency Strategy

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





