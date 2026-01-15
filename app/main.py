from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import hmac, hashlib, time
from datetime import datetime
from typing import Optional

from app.config import WEBHOOK_SECRET
from app.models import init_db
from app.storage import insert_message, list_messages, stats
from app.metrics import http_requests_total, webhook_requests_total, request_latency
from app.logging_utils import logger, new_request_id

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

# ------------------ Utilities ------------------

def verify_signature(raw: bytes, sig: str) -> bool:
    mac = hmac.new(WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)

# ------------------ Schemas ------------------

class MessageIn(BaseModel):
    message_id: str = Field(min_length=1)
    from_: str = Field(alias="from", min_length=2)
    to: str = Field(min_length=2)
    ts: str
    text: Optional[str] = Field(default=None, max_length=4096)

# ------------------ Middleware ------------------

@app.middleware("http")
async def metrics_and_logs(request: Request, call_next):
    rid = new_request_id()
    start = time.time()

    response = await call_next(request)

    latency = int((time.time() - start) * 1000)

    http_requests_total.labels(
        path=request.url.path,
        status=str(response.status_code)
    ).inc()

    request_latency.observe(latency)

    logger.info({
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": rid,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": latency
    })

    return response

# ------------------ Health ------------------

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
def ready():
    if not WEBHOOK_SECRET:
        raise HTTPException(503)
    return {"status": "ready"}

# ------------------ Webhook ------------------

@app.post("/webhook")
async def webhook(req: Request):
    start = time.time()
    raw = await req.body()
    sig = req.headers.get("X-Signature")

    if not sig or not verify_signature(raw, sig):
        webhook_requests_total.labels(result="invalid_signature").inc()
        raise HTTPException(401, "invalid signature")

    try:
        data = await req.json()
        msg = MessageIn(**data)
    except Exception:
        webhook_requests_total.labels(result="validation_error").inc()
        raise HTTPException(422, "invalid payload")

    result = insert_message({
        "message_id": msg.message_id,
        "from": msg.from_,
        "to": msg.to,
        "ts": msg.ts,
        "text": msg.text
    })

    webhook_requests_total.labels(result=result).inc()

    logger.info({
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": new_request_id(),
        "method": "POST",
        "path": "/webhook",
        "status": 200,
        "latency_ms": int((time.time() - start) * 1000),
        "message_id": msg.message_id,
        "dup": result == "duplicate",
        "result": result
    })

    return {"status": "ok"}

# ------------------ Messages ------------------

@app.get("/messages")
def messages(
    limit: int = 50,
    offset: int = 0,
    from_: Optional[str] = None,
    since: Optional[str] = None,
    q: Optional[str] = None
):
    total, rows = list_messages(limit, offset, from_, since, q)

    data = [
        {
            "message_id": r[0],
            "from": r[1],
            "to": r[2],
            "ts": r[3],
            "text": r[4]
        }
        for r in rows
    ]

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ------------------ Stats ------------------

@app.get("/stats")
def get_stats():
    total, senders, top, first, last = stats()

    return {
        "total_messages": total,
        "senders_count": senders,
        "messages_per_sender": [
            {"from": r[0], "count": r[1]} for r in top
        ],
        "first_message_ts": first,
        "last_message_ts": last
    }

# ------------------ Metrics ------------------

@app.get("/metrics")
def metrics():
    from prometheus_client import generate_latest
    return PlainTextResponse(generate_latest(), media_type="text/plain")
