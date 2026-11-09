# KOMMENTOINTIOHJE / CODE MAP
# Tiedoston tarkoitus: Regressiotestit aiemmin havaittujen virheiden ja laadunvarmistuksen varmistamiseksi.
# Rakenne: testien valmistelut ja apufunktiot ensin, yksittäiset testitapaukset seuraavaksi.
# Jokainen testifunktio on oma tarkistuskokonaisuutensa.

from email import message_from_string
from starlette.requests import Request

from remotefit import api, cli, emailer
from remotefit.analysis import is_worldwide_remote


# TESTIOSIO ALKAA: test_worldwide_filter_rejects_common_country_and_time_zone_restrictions.
def test_worldwide_filter_rejects_common_country_and_time_zone_restrictions():
    assert not is_worldwide_remote({
        "location": "Worldwide",
        "description": "US citizens only",
    })
    assert not is_worldwide_remote({
        "eligible_locations": ["Worldwide"],
        "description": "Any location in Europe",
    })
    assert not is_worldwide_remote({
        "location": "Remote - Worldwide",
        "description": "Must overlap with PST working hours",
    })
    assert not is_worldwide_remote({
        "location": "Worldwide",
        "description": "Applicants must be based in Canada",
    })


# TESTIOSIO ALKAA: test_worldwide_filter_keeps_unrestricted_structured_worldwide_role.
# FUNKTIO-OSIO PÄÄTTYY: test_worldwide_filter_rejects_common_country_and_time_zone_restrictions. Seuraava osio alkaa seuraavasta määrittelystä tai tiedoston lopusta.
def test_worldwide_filter_keeps_unrestricted_structured_worldwide_role():
    assert is_worldwide_remote({
        "location": "Worldwide",
        "description": "Work remotely with a distributed team.",
    })


# TESTIOSIO ALKAA: test_api_scan_persists_and_returns_provider_notice.
# FUNKTIO-OSIO PÄÄTTYY: test_worldwide_filter_keeps_unrestricted_structured_worldwide_role. Seuraava osio alkaa seuraavasta määrittelystä tai tiedoston lopusta.
def test_api_scan_persists_and_returns_provider_notice(monkeypatch):
    notice = {"legal": "Credit Remote OK and link to the original listing.", "last_updated": "2026-11-09"}
    saved_notices = []
    class Connection:
        def close(self):
            pass

    monkeypatch.setattr(api, "load_settings", lambda: {
        "sources": {}, "filters": {"reject_restrictions": []},
        "database_path": ":memory:", "profile": {},
    })
    def fetch_all(_sources, notice_callback=None):
        notice_callback("remoteok", notice)
        return ([{"title": "Developer", "location": "Worldwide"}], [])
    monkeypatch.setattr(api, "fetch_all", fetch_all)
    monkeypatch.setattr(api, "is_worldwide_remote", lambda *_args: True)
    monkeypatch.setattr(api, "score_job", lambda *_args: {"score": 8})
    monkeypatch.setattr(api, "connect", lambda _path: Connection())
    monkeypatch.setattr(api, "save_jobs", lambda _connection, _jobs: 1)
    monkeypatch.setattr(api, "save_source_notice", lambda _connection, source, value: saved_notices.append((source, value)))

    request = Request({
        "type": "http", "method": "POST", "path": "/api/scan",
        "headers": [], "query_string": b"",
    })
    result = api.scan_jobs(request)

    assert result["saved"] == 1
    assert result["source_notices"] == [{
        "source": "remoteok", "legal": notice["legal"],
        "last_updated": notice["last_updated"],
    }]
    assert saved_notices == [("remoteok", notice)]


# TESTIOSIO ALKAA: test_email_digest_uses_first_seen_timestamp.
# FUNKTIO-OSIO PÄÄTTYY: test_api_scan_persists_and_returns_provider_notice. Seuraava osio alkaa seuraavasta määrittelystä tai tiedoston lopusta.
def test_email_digest_uses_first_seen_timestamp(monkeypatch):
    sent = {}
    class FakeSMTP:
        def __init__(self, *_args, **_kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            return False
        def starttls(self):
            pass
        def login(self, *_args):
            pass
        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setattr(emailer.smtplib, "SMTP", FakeSMTP)
    emailer.send_digest(
        {"host": "smtp.example.test", "port": 587, "username": "user",
         "password": "secret", "from": "from@example.test",
         "to": "to@example.test", "use_tls": True},
        [{"title": "Developer", "company": "Example", "first_seen_at": "2026-11-09T10:00:00+00:00",
          "analysis": {"score": 8}, "source": "remoteok", "url": "https://example.test/job"}],
    )
    assert "First seen: 2026-11-09T10:00:00+00:00" in sent["message"].get_content()


# TESTIOSIO ALKAA: test_cli_digest_reports_unsent_saved_listings.
# FUNKTIO-OSIO PÄÄTTYY: test_email_digest_uses_first_seen_timestamp. Seuraava osio alkaa seuraavasta määrittelystä tai tiedoston lopusta.
def test_cli_digest_reports_unsent_saved_listings(monkeypatch, capsys):
    class Connection:
        def close(self):
            pass
    monkeypatch.setattr(cli, "connect", lambda _path: Connection())
    monkeypatch.setattr(cli, "list_unsent_jobs", lambda *_args, **_kwargs: [])
    cli.digest({"database_path": ":memory:"})
    assert "No unsent saved listings to email." in capsys.readouterr().out

# FUNKTIO-OSIO PÄÄTTYY: test_cli_digest_reports_unsent_saved_listings. Seuraava osio alkaa seuraavasta määrittelystä tai tiedoston lopusta.