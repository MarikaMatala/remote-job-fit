import csv

from remotefit.cli import export_jobs, show_list
from remotefit.db import connect, save_jobs
from remotefit.emailer import send_digest


def _saved_job(connection):
    save_jobs(connection, [{
        "source": "Remote OK",
        "source_id": "example-1",
        "title": "Python Developer",
        "company": "Example Co",
        "location": "Worldwide",
        "url": "https://remoteok.com/remote-jobs/example-1",
        "published_at": "2026-11-01",
        "deadline": None,
        "tags": ["Python"],
        "analysis": {"score": 8.5},
    }])


def test_cli_list_and_csv_include_source_and_original_url(tmp_path, capsys):
    database = tmp_path / "jobs.sqlite3"
    connection = connect(database)
    _saved_job(connection)
    connection.close()
    settings = {"database_path": str(database)}

    show_list(settings)
    output = capsys.readouterr().out
    assert "Source: Remote OK" in output
    assert "https://remoteok.com/remote-jobs/example-1" in output

    target = tmp_path / "exports" / "jobs.csv"
    export_jobs(settings, target)
    with target.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["source"] == "Remote OK"
    assert row["url"] == "https://remoteok.com/remote-jobs/example-1"


def test_email_digest_includes_source_and_original_listing(monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            pass

        def login(self, *_args):
            pass

        def send_message(self, message):
            captured["message"] = message

    monkeypatch.setattr("remotefit.emailer.smtplib.SMTP", FakeSMTP)
    send_digest(
        {"host": "smtp.example", "port": 587, "username": "user",
         "password": "secret", "from": "from@example.test",
         "to": "to@example.test", "use_tls": True},
        [{"title": "Python Developer", "company": "Example Co",
          "source": "Remote OK", "url": "https://remoteok.com/remote-jobs/example-1",
          "analysis": {"score": 8.5}}],
    )

    message = captured["message"]
    assert "saved matching listings" in message["Subject"]
    body = message.get_content()
    assert "Source: Remote OK" in body
    assert "https://remoteok.com/remote-jobs/example-1" in body
