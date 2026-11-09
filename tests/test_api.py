# CODE MAP / COMMENTING GUIDE
# File purpose: Testit Remote Job Fit -sovelluksen HTTP-rajapinnalle ja sen vastauksille.
# Structure: test setup and helper functions first, followed by individual test cases.
# Jokainen testifunktio on oma tarkistuskokonaisuutensa.

from fastapi.testclient import TestClient

from remotefit.api import app


# TEST SECTION START: test_health_endpoint.
def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health", headers={"Host": "127.0.0.1"})
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "remote-job-fit",
    }


# TEST SECTION START: test_scan_rejects_untrusted_browser_origin.
# FUNCTION SECTION END: test_health_endpoint. The next section starts at the next function or class.
def test_scan_rejects_untrusted_browser_origin():
    # The request must be rejected before loading settings or contacting feeds.
    client = TestClient(app)
    response = client.post(
        "/api/scan",
        headers={"Origin": "https://untrusted.example", "Host": "127.0.0.1"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Origin is not allowed."


# TEST SECTION START: test_api_rejects_non_local_host_header.
# FUNCTION SECTION END: test_scan_rejects_untrusted_browser_origin. The next section starts at the next function or class.
def test_api_rejects_non_local_host_header():
    client = TestClient(app)
    response = client.get(
        "/api/health",
        headers={"Host": "attacker.example"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "This API is for local development only."

# FUNCTION SECTION END: test_api_rejects_non_local_host_header. The next section starts at the next function or class.