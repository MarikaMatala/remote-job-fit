"""Adapters for documented public job-listing endpoints.

Provider payloads are external input: validate their shape, skip malformed rows,
and never include a configured URL in error messages (it may contain a token).
"""

# CODE MAP / COMMENTING GUIDE
# File purpose: Defines job sources, fetches listings, and processes source data.
# Structure: imports and settings first, followed by data structures and helper functions, with main operations last.
# Function start points are marked separately to make them easier to find.

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

import httpx

USER_AGENT = "RemoteJobFit/0.2 (open-source job discovery tool)"
# Remotive recommends no more than four API requests per day. A six-hour
# minimum interval enforces that limit across separate CLI invocations.
REMOTIVE_MIN_INTERVAL_SECONDS = 6 * 60 * 60


# FUNCTION SECTION START: _remotive_rate_limit_path.
def _remotive_rate_limit_path(url):
    cache_root = Path(os.environ.get(
        "REMOTE_JOB_FIT_CACHE_DIR",
        Path.home() / ".cache" / "remote-job-fit",
    )).expanduser()
    parsed = urlsplit(url)
    endpoint = f"{parsed.netloc.lower()}{parsed.path}"
    digest = hashlib.sha256(endpoint.encode("utf-8")).hexdigest()
    return cache_root / f"remotive-request-{digest}.txt"


# FUNCTION SECTION START: _get_remotive_json.
# FUNCTION SECTION END: _remotive_rate_limit_path. The next section starts at the next function or class.
def _get_remotive_json(url):
    marker = _remotive_rate_limit_path(url)
    now = time.time()
    try:
        last_request = float(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        last_request = 0
    remaining = REMOTIVE_MIN_INTERVAL_SECONDS - (now - last_request)
    if remaining > 0:
        minutes = max(1, int((remaining + 59) // 60))
        raise ValueError(
            f"Remotive refresh is rate-limited; try again in about {minutes} minutes."
        )

    payload = _get_json(url)
    marker.parent.mkdir(parents=True, exist_ok=True)
    temporary = marker.with_suffix(".tmp")
    temporary.write_text(str(now), encoding="utf-8")
    temporary.replace(marker)
    return payload


# FUNCTION SECTION START: _get_json.
# FUNCTION SECTION END: _get_remotive_json. The next section starts at the next function or class.
def _get_json(url):
    """Fetch one JSON response with a bounded timeout and a descriptive UA."""
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return response.json()


# FUNCTION SECTION START: _records.
# FUNCTION SECTION END: _get_json. The next section starts at the next function or class.
def _records(value):
    """Return only mapping-like records from an untrusted provider payload."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


# FUNCTION SECTION START: _tags.
# FUNCTION SECTION END: _records. The next section starts at the next function or class.
def _tags(value):
    """Normalize provider tags to a list of non-empty strings."""
    if not isinstance(value, list):
        return []
    return [str(tag).strip() for tag in value if tag is not None and str(tag).strip()]


# FUNCTION SECTION START: _timestamp.
# FUNCTION SECTION END: _tags. The next section starts at the next function or class.
def _timestamp():
    return datetime.now(timezone.utc).isoformat()


# FUNCTION SECTION START: fetch_remotive.
# FUNCTION SECTION END: _timestamp. The next section starts at the next function or class.
def fetch_remotive(url):
    """Map Remotive's public feed into the application's common job shape."""
    payload = _get_remotive_json(url)
    jobs = _records(payload.get("jobs")) if isinstance(payload, dict) else []
    fetched_at = _timestamp()
    results = []
    for item in jobs:
        source_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()
        # A missing stable ID would make unrelated rows collide in SQLite.
        if not source_id or not title:
            continue
        results.append({
            "source": "Remotive",
            "source_id": source_id,
            "title": title,
            "company": str(item.get("company_name") or ""),
            "location": str(item.get("candidate_required_location") or ""),
            "description": str(item.get("description") or ""),
            "url": str(item.get("url") or ""),
            "published_at": item.get("publication_date"),
            "deadline": item.get("deadline"),
            "applicant_count": None,
            "fetched_at": fetched_at,
            "tags": _tags(item.get("tags")),
            "category": str(item.get("category") or ""),
        })
    return results


# FUNCTION SECTION START: fetch_remoteok.
# FUNCTION SECTION END: fetch_remotive. The next section starts at the next function or class.
def fetch_remoteok(url, notice_callback=None):
    """Map Remote OK's feed and surface its current first-item legal notice."""
    payload = _get_json(url)
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], dict):
        raise ValueError("Remote OK feed is missing its legal notice metadata.")
    metadata = payload[0]
    legal = metadata.get("legal")
    if not isinstance(legal, str) or not legal.strip():
        raise ValueError("Remote OK feed has no usable legal notice.")
    notice = {
        "legal": legal.strip(),
        "last_updated": metadata.get("last_updated"),
    }
    if notice_callback:
        notice_callback("Remote OK", notice)
    items = _records(payload[1:])
    fetched_at = _timestamp()
    results = []
    for item in items:
        source_id = str(item.get("id") or item.get("slug") or "").strip()
        title = str(item.get("position") or "").strip()
        if not source_id or not title:
            continue
        results.append({
            "source": "Remote OK",
            "source_id": source_id,
            "title": title,
            "company": str(item.get("company") or ""),
            "location": str(item.get("location") or ""),
            "description": str(item.get("description") or ""),
            "url": str(item.get("url") or ""),
            "published_at": item.get("date"),
            "deadline": None,
            "applicant_count": None,
            "fetched_at": fetched_at,
            "tags": _tags(item.get("tags")),
            "category": "",
        })
    return results


# FUNCTION SECTION START: fetch_all.
# FUNCTION SECTION END: fetch_remoteok. The next section starts at the next function or class.
def fetch_all(source_config, notice_callback=None):
    """Fetch enabled providers and expose provider notices without logging secrets."""
    collected = []
    errors = []
    adapters = {"remotive": fetch_remotive, "remoteok": fetch_remoteok}
    for name, settings in source_config.items():
        if not isinstance(settings, dict) or not settings.get("enabled", False):
            continue
        adapter = adapters.get(name)
        if not adapter:
            continue
        try:
            url = settings.get("url")
            if not isinstance(url, str) or not url.strip():
                raise ValueError("Missing source URL")
            if name == "remoteok":
                collected.extend(adapter(url, notice_callback=notice_callback))
            else:
                collected.extend(adapter(url))
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            # Do not include exception text: a custom URL may contain a token.
            errors.append(f"{name}: {type(exc).__name__}")
    return collected, errors

# FUNCTION SECTION END: fetch_all. The next section starts at the next function or class.