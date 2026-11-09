# KOMMENTOINTIOHJE / CODE MAP
# Tiedoston tarkoitus: Tietokantayhteydet, tietojen tallennus ja tietokantakyselyt.
# Rakenne: tuonnit ja asetukset ensin, tietorakenteet ja apufunktiot seuraavaksi, päätoiminnot lopuksi.
# FUNKTIOIDEN ALKUKOHDAT on merkitty erikseen, jotta niitä on helpompi etsiä.

"""SQLite persistence for locally discovered job listings.

WORK IN PROGRESS: the database is local application data, not a public example.
Its path is configured through the local DATABASE_PATH environment variable.
Do not commit database files or insert passwords, API keys, or account secrets.
"""

from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone


# FUNKTIO-OSIO ALKAA: connect.
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
    connection.execute("""
        CREATE TABLE IF NOT EXISTS source_notices (
            source TEXT PRIMARY KEY,
            legal TEXT NOT NULL,
            last_updated TEXT,
            checked_at TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS digest_sent (
            job_id INTEGER PRIMARY KEY,
            sent_at TEXT NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
    """)
    connection.commit()
    return connection


# FUNKTIO-OSIO ALKAA: save_jobs.
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


# FUNKTIO-OSIO ALKAA: list_jobs.
def list_jobs(connection, limit=50):
    return connection.execute(
        "SELECT * FROM jobs ORDER BY first_seen_at DESC LIMIT ?", (limit,)
    ).fetchall()



# FUNKTIO-OSIO ALKAA: save_source_notice.
def save_source_notice(connection, source, notice):
    """Persist the latest provider-supplied terms notice locally."""
    checked_at = datetime.now(timezone.utc).isoformat()
    last_updated = notice.get("last_updated")
    connection.execute("""
        INSERT INTO source_notices (source, legal, last_updated, checked_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(source) DO UPDATE SET
            legal = excluded.legal,
            last_updated = excluded.last_updated,
            checked_at = excluded.checked_at
    """, (source, notice["legal"], str(last_updated) if last_updated is not None else None, checked_at))
    connection.commit()


# FUNKTIO-OSIO ALKAA: list_unsent_jobs.
def list_unsent_jobs(connection, limit=25):
    """Return newest saved jobs that have not appeared in a successful digest."""
    return connection.execute("""
        SELECT jobs.* FROM jobs
        LEFT JOIN digest_sent ON digest_sent.job_id = jobs.id
        WHERE digest_sent.job_id IS NULL
        ORDER BY jobs.first_seen_at DESC
        LIMIT ?
    """, (limit,)).fetchall()


# FUNKTIO-OSIO ALKAA: mark_jobs_sent.
def mark_jobs_sent(connection, job_ids):
    """Mark jobs as delivered only after the SMTP send succeeds."""
    if not job_ids:
        return 0
    sent_at = datetime.now(timezone.utc).isoformat()
    connection.executemany(
        "INSERT OR IGNORE INTO digest_sent (job_id, sent_at) VALUES (?, ?)",
        [(int(job_id), sent_at) for job_id in job_ids],
    )
    connection.commit()
    return len(job_ids)
