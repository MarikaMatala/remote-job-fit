"""Load private, machine-local settings without depending on the shell's cwd.

User-editable values belong in:
- config/profile.yaml: private job titles and skill keywords.
- config/sources.yaml: local source toggles and restriction phrases.
- .env: SMTP credentials and the local database path.

Only example templates are committed. Never hard-code credentials or personal data.
"""

from pathlib import Path
import os

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


def _mapping(value, label):
    """Require a YAML mapping while treating an empty document as defaults."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a YAML mapping.")
    return value


def _read_yaml(path, label):
    with path.open("r", encoding="utf-8") as handle:
        return _mapping(yaml.safe_load(handle), label)


def load_settings(project_root: Path | None = None):
    """Load settings from a project directory (defaults to this checkout).

    The optional root makes the loader deterministic in tests and supports
    invoking the installed CLI from outside the repository directory.
    """
    root = Path(project_root).expanduser().resolve() if project_root else ROOT
    config_dir = root / "config"

    # Secrets stay in the ignored local .env file or process environment.
    load_dotenv(root / ".env")

    profile_path = config_dir / "profile.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(
            "Private profile not found. Copy config/profile.example.yaml "
            "to config/profile.yaml and edit it locally."
        )
    profile_data = _read_yaml(profile_path, "config/profile.yaml")

    sources_path = config_dir / "sources.yaml"
    if sources_path.exists():
        source_data = _read_yaml(sources_path, "config/sources.yaml")
    else:
        source_data = _read_yaml(config_dir / "sources.example.yaml", "config/sources.example.yaml")

    profile = _mapping(profile_data.get("profile", {}), "The profile section")
    sources = _mapping(source_data.get("sources", {}), "The sources section")
    filters = _mapping(source_data.get("filters", {}), "The filters section")

    return {
        "profile": profile,
        "sources": sources,
        "filters": filters,
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
