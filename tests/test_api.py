# KOMMENTOINTIOHJE / CODE MAP
# Tiedoston tarkoitus: Testit Remote Job Fit -sovelluksen HTTP-rajapinnalle ja sen vastauksille.
# Rakenne: testien valmistelut ja apufunktiot ensin, yksittäiset testitapaukset seuraavaksi.
# Jokainen testifunktio on oma tarkistuskokonaisuutensa.

from fastapi.testclient import TestClient

from remotefit.api import app


# TESTIOSIO ALKAA: test_health_endpoint.
def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health", headers={"Host": "127.0.0.1"})
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "remote-job-fit",
    }


# TESTIOSIO ALKAA: test_scan_rejects_untrusted_browser_origin.
def test_scan_rejects_untrusted_browser_origin():
    # The request must be rejected before loading settings or contacting feeds.
    client = TestClient(app)
    response = client.post(
        "/api/scan",
        headers={"Origin": "https://untrusted.example", "Host": "127.0.0.1"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Origin is not allowed."


# TESTIOSIO ALKAA: test_api_rejects_non_local_host_header.
def test_api_rejects_non_local_host_header():
    client = TestClient(app)
    response = client.get(
        "/api/health",
        headers={"Host": "attacker.example"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "This API is for local development only."
