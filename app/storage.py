from app.models import get_conn
from datetime import datetime
import sqlite3

def insert_message(m):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO messages VALUES (?,?,?,?,?,?)",
            (
                m["message_id"],
                m["from"],
                m["to"],
                m["ts"],
                m.get("text"),
                datetime.utcnow().isoformat() + "Z"
            )
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        conn.close()

def list_messages(limit, offset, from_msisdn=None, since=None, q=None):
    base = "FROM messages WHERE 1=1"
    params = []

    if from_msisdn:
        base += " AND from_msisdn=?"
        params.append(from_msisdn)

    if since:
        base += " AND ts>=?"
        params.append(since)

    if q:
        base += " AND LOWER(text) LIKE ?"
        params.append(f"%{q.lower()}%")

    conn = get_conn()

    total = conn.execute(f"SELECT COUNT(*) {base}", params).fetchone()[0]

    rows = conn.execute(
        f"""SELECT message_id, from_msisdn, to_msisdn, ts, text
            {base}
            ORDER BY ts ASC, message_id ASC
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    ).fetchall()

    conn.close()

    return total, rows

def stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders = conn.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages").fetchone()[0]

    top = conn.execute("""
        SELECT from_msisdn, COUNT(*) as c
        FROM messages
        GROUP BY from_msisdn
        ORDER BY c DESC
        LIMIT 10
    """).fetchall()

    first = conn.execute("SELECT MIN(ts) FROM messages").fetchone()[0]
    last = conn.execute("SELECT MAX(ts) FROM messages").fetchone()[0]

    conn.close()

    return total, senders, top, first, last
