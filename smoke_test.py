"""End-to-end smoke test against a *running* instance of the app.

Usage:
    python smoke_test.py [base_url]

Defaults to http://localhost:5000. Run this after starting the app locally
(`python app.py`) or against a deployed Render URL to confirm the whole
stack -- frontend static files, search, company lookup, and both report
generators -- is working.
"""
import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


def check(label, fn):
    try:
        fn()
        print(f"[PASS] {label}")
        return True
    except Exception as exc:  # noqa: BLE001 - smoke test, report and continue
        print(f"[FAIL] {label}: {exc}")
        return False


def main():
    results = []

    def health():
        resp = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert resp.status_code == 200, resp.text
        assert resp.json().get("status") == "ok"

    def frontend_served():
        resp = requests.get(BASE_URL, timeout=10)
        assert resp.status_code == 200, resp.text
        assert "<div id=\"root\">" in resp.text

    def search():
        resp = requests.get(f"{BASE_URL}/api/search", params={"q": "tcs"}, timeout=15)
        assert resp.status_code == 200, resp.text
        assert "results" in resp.json()

    def company():
        resp = requests.get(f"{BASE_URL}/api/company/TCS", timeout=15)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body.get("symbol") == "TCS"

    def excel():
        resp = requests.post(
            f"{BASE_URL}/api/generate/excel",
            json={"symbol": "TCS", "options": {}},
            timeout=20,
        )
        assert resp.status_code == 200, resp.text
        assert resp.headers.get("Content-Type", "").startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert len(resp.content) > 1000

    def powerbi():
        resp = requests.post(
            f"{BASE_URL}/api/generate/powerbi",
            json={"symbol": "TCS", "options": {}},
            timeout=20,
        )
        assert resp.status_code == 200, resp.text
        assert resp.headers.get("Content-Type", "").startswith("application/zip")
        assert len(resp.content) > 100

    results.append(check("Health check", health))
    results.append(check("Frontend is served", frontend_served))
    results.append(check("Search API", search))
    results.append(check("Company API", company))
    results.append(check("Excel report generation", excel))
    results.append(check("Power BI report generation", powerbi))

    print(f"\n{sum(results)}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
