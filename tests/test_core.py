import httpx
import pytest

from remotefit import config, sources
from remotefit.db import connect, list_jobs, save_jobs


def test_settings_load_from_project_root_not_current_directory(tmp_path, monkeypatch):
    project = tmp_path / "project"
    config_dir = project / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "profile.yaml").write_text(
        "profile:\n  title: Example developer\n", encoding="utf-8"
    )
    (config_dir / "sources.example.yaml").write_text(
        "sources:\n  remotive:\n    enabled: false\nfilters:\n  reject_restrictions: []\n",
        encoding="utf-8",
    )
    unrelated = tmp_path / "elsewhere"
    unrelated.mkdir()
    monkeypatch.chdir(unrelated)
    monkeypatch.setenv("DATABASE_PATH", "tmp/test.sqlite3")
    monkeypatch.setenv("SMTP_PORT", "465")

    settings = config.load_settings(project)

    assert settings["profile"]["title"] == "Example developer"
    assert settings["sources"]["remotive"]["enabled"] is False
    assert settings["filters"]["reject_restrictions"] == []
    assert settings["database_path"] == "tmp/test.sqlite3"
    assert settings["smtp"]["port"] == 465


def test_settings_reject_non_mapping_yaml_sections(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "profile.yaml").write_text("- unexpected\n- list\n", encoding="utf-8")
    (config_dir / "sources.example.yaml").write_text("sources: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="profile.yaml must contain a YAML mapping"):
        config.load_settings(tmp_path)


def test_remotive_adapter_skips_invalid_rows_and_normalizes_tags(monkeypatch, tmp_path):
    monkeypatch.setenv("REMOTE_JOB_FIT_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(sources, "_get_json", lambda _url: {
        "jobs": [
            {"id": 42, "title": "Frontend Developer", "company_name": "Example",
             "tags": ["React", None, "  TypeScript  "]},
            {"title": "Missing stable ID"},
            None,
            {"id": 43, "title": "", "tags": "not-a-list"},
        ]
    })

    jobs = sources.fetch_remotive("https://feed.example/jobs")

    assert len(jobs) == 1
    assert jobs[0]["source_id"] == "42"
    assert jobs[0]["title"] == "Frontend Developer"
    assert jobs[0]["tags"] == ["React", "TypeScript"]
    assert jobs[0]["source"] == "Remotive"
    assert jobs[0]["fetched_at"].endswith("+00:00")


def test_remoteok_adapter_skips_feed_metadata_and_malformed_rows(monkeypatch):
    monkeypatch.setattr(sources, "_get_json", lambda _url: [
        {"legal": "Please link back to Remote OK and mention Remote OK as a source.",
         "last_updated": 1794000000},
        {"slug": "python-role", "position": "Python Developer", "tags": ["Python"]},
        {"id": 99, "position": "No stable URL", "tags": None},
        "not a record",
        {"id": 100, "position": ""},
    ])

    jobs = sources.fetch_remoteok("https://feed.example/jobs")

    assert [job["source_id"] for job in jobs] == ["python-role", "99"]
    assert jobs[0]["company"] == ""
    assert jobs[0]["tags"] == ["Python"]
    assert jobs[1]["tags"] == []


def test_remoteok_notice_is_returned_to_callback(monkeypatch):
    monkeypatch.setattr(sources, "_get_json", lambda _url: [
        {"legal": "Credit Remote OK and link to each original listing.",
         "last_updated": 1794000000},
    ])
    notices = []
    assert sources.fetch_remoteok(
        "https://feed.example/jobs",
        notice_callback=lambda source, notice: notices.append((source, notice)),
    ) == []
    assert notices == [("Remote OK", {
        "legal": "Credit Remote OK and link to each original listing.",
        "last_updated": 1794000000,
    })]


def test_remoteok_rejects_missing_legal_notice(monkeypatch):
    monkeypatch.setattr(sources, "_get_json", lambda _url: [
        {"last_updated": 1794000000},
        {"id": 1, "position": "Python Developer"},
    ])
    with pytest.raises(ValueError, match="no usable legal notice"):
        sources.fetch_remoteok("https://feed.example/jobs")


def test_fetch_all_redacts_sensitive_source_urls_from_warnings(monkeypatch, tmp_path):
    monkeypatch.setenv("REMOTE_JOB_FIT_CACHE_DIR", str(tmp_path))
    secret_url = "https://feed.example/jobs?token=do-not-leak"

    def fail(_url):
        raise httpx.ConnectError(f"Unable to connect to {secret_url}")

    monkeypatch.setattr(sources, "fetch_remotive", fail)
    jobs, errors = sources.fetch_all({
        "remotive": {"enabled": True, "url": secret_url},
        "unknown": {"enabled": True, "url": "https://ignored.example"},
        "disabled": {"enabled": False, "url": "https://ignored.example"},
    })

    assert jobs == []
    assert errors == ["remotive: ConnectError"]
    assert "do-not-leak" not in " ".join(errors)


def test_database_ignores_duplicate_provider_records(tmp_path):
    connection = connect(tmp_path / "jobs.sqlite3")
    job = {
        "source": "Remotive",
        "source_id": "job-1",
        "title": "Frontend Developer",
        "company": "Example",
        "url": "https://example.test/job-1",
        "tags": ["React"],
        "analysis": {"score": 8.5},
    }

    try:
        assert save_jobs(connection, [job]) == 1
        assert save_jobs(connection, [job]) == 0
        rows = list_jobs(connection)

        assert len(rows) == 1
        assert rows[0]["title"] == "Frontend Developer"
        assert rows[0]["score"] == 8.5
    finally:
        connection.close()



def test_remotive_enforces_six_hour_request_interval(monkeypatch, tmp_path):
    monkeypatch.setenv("REMOTE_JOB_FIT_CACHE_DIR", str(tmp_path))
    calls = []
    monkeypatch.setattr(sources, "_get_json", lambda url: calls.append(url) or {"jobs": []})

    assert sources.fetch_remotive("https://feed.example/jobs") == []
    with pytest.raises(ValueError, match="rate-limited"):
        sources.fetch_remotive("https://feed.example/jobs")
    assert calls == ["https://feed.example/jobs"]



def test_digest_sent_tracking_skips_already_sent_jobs(tmp_path):
    from remotefit.db import list_unsent_jobs, mark_jobs_sent

    connection = connect(tmp_path / "digest.sqlite3")
    try:
        jobs = [
            {"source": "Remote OK", "source_id": f"job-{n}",
             "title": f"Developer {n}", "analysis": {"score": 7}}
            for n in range(1, 4)
        ]
        assert save_jobs(connection, jobs) == 3
        unsent = list_unsent_jobs(connection)
        assert len(unsent) == 3
        assert mark_jobs_sent(connection, [unsent[0]["id"], unsent[1]["id"]]) == 2
        remaining = list_unsent_jobs(connection)
        assert len(remaining) == 1
        assert remaining[0]["title"] == unsent[2]["title"]
    finally:
        connection.close()
