from unittest.mock import patch

import pytest

from backend.app import app

SAMPLE_COMPANY = {
    "symbol": "TCS",
    "name": "Tata Consultancy Services",
    "source_url": "https://www.screener.in/company/TCS/consolidated/",
    "ratios": {"P/E": "28.5", "ROE": "45.2%"},
    "profit_loss": [
        {"Metric": "Revenue", "Mar 2023": 1500, "Mar 2024": 1700},
        {"Metric": "Net Profit", "Mar 2023": 300, "Mar 2024": 340},
    ],
    "balance_sheet": [{"Metric": "Total Assets", "Mar 2023": 5000, "Mar 2024": 5400}],
    "cash_flow": [{"Metric": "Operating Cash Flow", "Mar 2023": 400, "Mar 2024": 450}],
    "quarterly": [],
}


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_search_empty_query_returns_empty_list(client):
    resp = client.get("/api/search?q=")
    assert resp.status_code == 200
    assert resp.get_json()["results"] == []


@patch("backend.app.scraper.search_companies")
def test_search_proxies_scraper(mock_search, client):
    mock_search.return_value = [{"symbol": "TCS", "name": "Tata Consultancy Services", "url": "x"}]
    resp = client.get("/api/search?q=tcs")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["results"][0]["symbol"] == "TCS"
    mock_search.assert_called_once_with("tcs")


@patch("backend.app.scraper.get_company_data")
def test_company_endpoint(mock_get, client):
    mock_get.return_value = SAMPLE_COMPANY
    resp = client.get("/api/company/TCS")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Tata Consultancy Services"


@patch("backend.app.scraper.get_company_data")
def test_generate_excel_requires_symbol(mock_get, client):
    resp = client.post("/api/generate/excel", json={})
    assert resp.status_code == 400
    mock_get.assert_not_called()


@patch("backend.app.scraper.get_company_data")
def test_generate_excel_streams_xlsx(mock_get, client):
    mock_get.return_value = SAMPLE_COMPANY
    resp = client.post("/api/generate/excel", json={"symbol": "TCS", "options": {}})
    assert resp.status_code == 200
    assert resp.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(resp.data) > 0


@patch("backend.app.scraper.get_company_data")
def test_generate_powerbi_streams_zip(mock_get, client):
    mock_get.return_value = SAMPLE_COMPANY
    resp = client.post("/api/generate/powerbi", json={"symbol": "TCS", "options": {}})
    assert resp.status_code == 200
    assert resp.mimetype == "application/zip"
    assert len(resp.data) > 0
