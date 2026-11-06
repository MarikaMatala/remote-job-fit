"""Load local settings.

User-editable values belong in:
- config/profile.yaml: private job titles and skill keywords.
- config/sources.yaml: local source toggles and restriction phrases.
- .env: SMTP credentials and the local database path.

The example templates are committed; the personal files above are ignored by Git.
WORK IN PROGRESS: this configuration flow may change during development.
Add your own profile details only to config/profile.yaml, source overrides only
to config/sources.yaml, and SMTP secrets only to the local .env file. Never
hard-code API keys, passwords, tokens, email addresses, or personal data here.
"""

from pathlib import Path
import os

import yaml
from dotenv import load_dotenv

ROOT = Path.cwd()
PROFILE_PATH = ROOT / "config" / "profile.yaml"
SOURCES_PATH = ROOT / "config" / "sources.yaml"


def load_settings():
    # Add your own SMTP values to the ignored local .env file, or supply them
    # through your operating system environment. Never put real credentials
    # in this Python module, committed YAML examples, or browser-side code.
    load_dotenv(ROOT / ".env")
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "Private profile not found. Copy config/profile.example.yaml "
            "to config/profile.yaml and edit it locally."
        )
    with PROFILE_PATH.open("r", encoding="utf-8") as handle:
        profile_data = yaml.safe_load(handle) or {}
    if SOURCES_PATH.exists():
        with SOURCES_PATH.open("r", encoding="utf-8") as handle:
            source_data = yaml.safe_load(handle) or {}
    else:
        example_path = ROOT / "config" / "sources.example.yaml"
        with example_path.open("r", encoding="utf-8") as handle:
            source_data = yaml.safe_load(handle) or {}
    return {
        "profile": profile_data.get("profile", {}),
        "sources": source_data.get("sources", {}),
        "filters": source_data.get("filters", {}),
        "database_path": os.getenv("DATABASE_PATH", "data/jobs.sqlite3"),
        "smtp": {
            "host": os.getenv("SMTP_HOST", ""),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from": os.getenv("SMTP_FROM", ""),
            "to": os.getenv("SMTP_TO", ""),
            "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        },
    }
