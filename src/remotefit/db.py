"""SQLite persistence for locally discovered job listings."""

from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone


def connect(database_path):
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            published_at TEXT,
            deadline TEXT,
            first_seen_at TEXT NOT NULL,
            applicant_count INTEGER,
            description TEXT,
            tags_json TEXT,
            score REAL,
            analysis_json TEXT,
            UNIQUE(source, source_id)
        )
    """)
    connection.commit()
    return connection


def save_jobs(connection, jobs):
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    for job in jobs:
        cursor = connection.execute("""
            INSERT OR IGNORE INTO jobs (
                source, source_id, title, company, location, url,
                published_at, deadline, first_seen_at, applicant_count,
                description, tags_json, score, analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get("source", ""), job.get("source_id", ""), job.get("title", ""),
            job.get("company", ""), job.get("location", ""), job.get("url", ""),
            job.get("published_at"), job.get("deadline"), now,
            job.get("applicant_count"), job.get("description", ""),
            json.dumps(job.get("tags", [])), job.get("analysis", {}).get("score"),
            json.dumps(job.get("analysis", {})),
        ))
        inserted += cursor.rowcount
    connection.commit()
    return inserted


def list_jobs(connection, limit=50):
    return connection.execute(
        "SELECT * FROM jobs ORDER BY first_seen_at DESC LIMIT ?", (limit,)
    ).fetchall()
