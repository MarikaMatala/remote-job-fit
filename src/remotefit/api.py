"""Local HTTP API for the optional TypeScript dashboard.

WORK IN PROGRESS: this API is experimental and intended for localhost only.
Keep profile details, SMTP credentials, API keys, and private endpoints out of
this source file. Add personal settings only to ignored local config/.env files.
The API never returns profile or SMTP settings to the browser.
"""

# CODE MAP / COMMENTING GUIDE
# File purpose: Python API used by the browser interface to access Remote Job Fit features.
# Structure: imports and settings first, followed by data structures and helper functions, with main operations last.
# Navigation map: local host validation -> health endpoint -> job listing endpoint -> scan endpoint -> local server startup.
# Editing tip: keep this API bound to localhost and return only the fields required by the browser dashboard.

import json

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .analysis import is_worldwide_remote, score_job
from .config import load_settings
from .db import connect, list_jobs, save_jobs, save_source_notice
from .sources import fetch_all

app = FastAPI(
    title="Remote Job Fit API",
    version="0.2.0",
    description="Local API for the Remote Job Fit dashboard.",
)

# Vite's local development server. The API itself should be bound to localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
# FUNCTION SECTION START: restrict_host_header.
async def restrict_host_header(request: Request, call_next):
    """Reduce DNS-rebinding risk by accepting only local development hosts."""
    host = (request.url.hostname or "").lower()
    if host not in {"127.0.0.1", "localhost"}:
        return JSONResponse(
            status_code=400,
            content={"detail": "This API is for local development only."},
        )
    return await call_next(request)


@app.get("/api/health")
# FUNCTION SECTION START: health.
# FUNCTION SECTION END: restrict_host_header. The next section starts at the next function or class.
def health():
    """Basic readiness endpoint; does not read or reveal local configuration."""
    return {"status": "ok", "service": "remote-job-fit"}


@app.get("/api/jobs")
# FUNCTION SECTION START: get_jobs.
# FUNCTION SECTION END: health. The next section starts at the next function or class.
def get_jobs(limit: int = Query(default=100, ge=1, le=1000)):
    """Return saved job listings without exposing profile or email settings."""
    try:
        settings = load_settings()
        connection = connect(settings["database_path"])
        try:
            rows = list_jobs(connection, limit=limit)
            result = []
            for row in rows:
                item = dict(row)
                item["tags"] = json.loads(item.pop("tags_json") or "[]")
                item["analysis"] = json.loads(item.pop("analysis_json") or "{}")
                # Do not return the full description in the dashboard list API.
                item.pop("description", None)
                result.append(item)
            return {"jobs": result, "count": len(result)}
        finally:
            connection.close()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/scan")
# FUNCTION SECTION START: scan_jobs.
# FUNCTION SECTION END: get_jobs. The next section starts at the next function or class.
def scan_jobs(request: Request):
    """Fetch supported public sources, filter and score listings, then save them."""
    # Block cross-origin browser sites from triggering a local scan (CSRF-style
    # request). Requests without an Origin header remain available to local tools.
    origin = request.headers.get("origin")
    allowed_origins = {"http://127.0.0.1:5173", "http://localhost:5173"}
    if origin and origin not in allowed_origins:
        raise HTTPException(status_code=403, detail="Origin is not allowed.")
    try:
        settings = load_settings()
        notices = []
        jobs, errors = fetch_all(
            settings["sources"],
            notice_callback=lambda source, notice: notices.append((source, notice)),
        )
        accepted = []
        for job in jobs:
            if not is_worldwide_remote(
                job, settings["filters"].get("reject_restrictions", [])
            ):
                continue
            job["analysis"] = score_job(settings["profile"], job)
            accepted.append(job)

        connection = connect(settings["database_path"])
        try:
            inserted = save_jobs(connection, accepted)
            for source, notice in notices:
                save_source_notice(connection, source, notice)
        finally:
            connection.close()

        return {
            "fetched": len(jobs),
            "accepted": len(accepted),
            "saved": inserted,
            "warnings": errors,
            "source_notices": [
                {
                    "source": source,
                    "legal": notice["legal"],
                    "last_updated": notice.get("last_updated"),
                }
                for source, notice in notices
            ],
        }
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

# FUNCTION SECTION END: scan_jobs. The next section starts at the next function or class.