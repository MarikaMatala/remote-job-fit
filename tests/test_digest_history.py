

def test_cli_digest_sends_only_unsent_jobs_and_marks_after_success(tmp_path, monkeypatch, capsys):
    from remotefit import cli
    from remotefit.db import connect, save_jobs

    database = tmp_path / "digest.sqlite3"
    connection = connect(database)
    save_jobs(connection, [
        {"source": "Remote OK", "source_id": "digest-1",
         "title": "First role", "analysis": {"score": 8}},
        {"source": "Remotive", "source_id": "digest-2",
         "title": "Second role", "analysis": {"score": 7}},
    ])
    connection.close()
    sent = []
    monkeypatch.setattr(cli, "send_digest", lambda _settings, jobs: sent.extend(jobs))
    settings = {"database_path": str(database), "smtp": {"host": "smtp.example"}}

    cli.digest(settings)
    assert len(sent) == 2
    cli.digest(settings)
    assert len(sent) == 2
    assert "No new saved listings" in capsys.readouterr().out


def test_cli_digest_does_not_mark_jobs_when_smtp_fails(tmp_path, monkeypatch):
    from remotefit import cli
    from remotefit.db import connect, list_unsent_jobs, save_jobs

    database = tmp_path / "digest-failure.sqlite3"
    connection = connect(database)
    save_jobs(connection, [
        {"source": "Remote OK", "source_id": "digest-fail",
         "title": "Retry role", "analysis": {"score": 6}},
    ])
    connection.close()

    def fail_send(_settings, _jobs):
        raise RuntimeError("SMTP unavailable")

    monkeypatch.setattr(cli, "send_digest", fail_send)
    with pytest.raises(RuntimeError, match="SMTP unavailable"):
        cli.digest({"database_path": str(database), "smtp": {"host": "smtp.example"}})

    connection = connect(database)
    try:
        assert len(list_unsent_jobs(connection)) == 1
    finally:
        connection.close()
