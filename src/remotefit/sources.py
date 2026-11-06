"""Adapters for public job listing endpoints."""

from datetime import datetime, timezone
import httpx

USER_AGENT = "RemoteJobFit/0.1 (open-source job discovery tool)"


def _get_json(url):
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_remotive(url):
    payload = _get_json(url)
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    results = []
    for item in jobs:
        results.append({
            "source": "Remotive",
            "source_id": str(item.get("id", "")),
            "title": item.get("title", ""),
            "company": item.get("company_name", ""),
            "location": item.get("candidate_required_location", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "published_at": item.get("publication_date"),
            "deadline": item.get("deadline"),
            "applicant_count": None,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tags": item.get("tags", []),
            "category": item.get("category", ""),
        })
    return results


def fetch_remoteok(url):
    payload = _get_json(url)
    items = payload[1:] if isinstance(payload, list) and payload else []
    results = []
    for item in items:
        results.append({
            "source": "Remote OK",
            "source_id": str(item.get("id", item.get("slug", ""))),
            "title": item.get("position", ""),
            "company": item.get("company", ""),
            "location": item.get("location", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "published_at": item.get("date"),
            "deadline": None,
            "applicant_count": None,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tags": item.get("tags", []),
            "category": "",
        })
    return results


def fetch_all(source_config):
    collected = []
    errors = []
    adapters = {"remotive": fetch_remotive, "remoteok": fetch_remoteok}
    for name, settings in source_config.items():
        if not settings.get("enabled", False):
            continue
        adapter = adapters.get(name)
        if not adapter:
            continue
        try:
            collected.extend(adapter(settings["url"]))
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    return collected, errors
