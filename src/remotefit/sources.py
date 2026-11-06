"""Adapters for documented public job-listing endpoints.

Provider payloads are external input: validate their shape, skip malformed rows,
and never include a configured URL in error messages (it may contain a token).
"""

from datetime import datetime, timezone

import httpx

USER_AGENT = "RemoteJobFit/0.2 (open-source job discovery tool)"


def _get_json(url):
    """Fetch one JSON response with a bounded timeout and a descriptive UA."""
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return response.json()


def _records(value):
    """Return only mapping-like records from an untrusted provider payload."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _tags(value):
    """Normalize provider tags to a list of non-empty strings."""
    if not isinstance(value, list):
        return []
    return [str(tag).strip() for tag in value if tag is not None and str(tag).strip()]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def fetch_remotive(url):
    """Map Remotive's public feed into the application's common job shape."""
    payload = _get_json(url)
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


def fetch_remoteok(url):
    """Map Remote OK's array feed, whose first item is feed metadata."""
    payload = _get_json(url)
    items = _records(payload[1:]) if isinstance(payload, list) and payload else []
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


def fetch_all(source_config):
    """Fetch enabled known providers and return safe, non-sensitive warnings."""
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
            collected.extend(adapter(url))
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            # Do not include exception text: a custom URL may contain a token.
            errors.append(f"{name}: {type(exc).__name__}")
    return collected, errors
