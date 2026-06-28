"""
Scrapes public pages on screener.in for Indian listed-company financials.

Rules (see DATA_README.md for the full policy):
  * Only public, unauthenticated pages are read (no login, no paid data).
  * Requests are rate-limited (default: 1 request every SCRAPER_DELAY_SECONDS).
  * Responses are cached on disk (cache.py) so repeat lookups don't re-hit
    screener.in within the cache TTL.
  * A descriptive User-Agent identifies this as a research/education tool.
  * Screener.in's HTML structure can change at any time; parsing here is
    best-effort and degrades gracefully (missing sections are simply omitted
    rather than raising).
"""
import io
import os
import re
import threading
import time

import requests
from bs4 import BeautifulSoup

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

from . import cache

BASE_URL = "https://www.screener.in"
SEARCH_URL = f"{BASE_URL}/api/company/search/"
COMPANY_URL_TMPL = f"{BASE_URL}/company/{{symbol}}/"
COMPANY_URL_CONSOLIDATED_TMPL = f"{BASE_URL}/company/{{symbol}}/consolidated/"

USER_AGENT = (
    "IndiaFinModel/1.0 (+educational financial-model generator; "
    "polite scraper, see DATA_README.md)"
)

RATE_LIMIT_SECONDS = float(os.environ.get("SCRAPER_DELAY_SECONDS", "2"))
REQUEST_TIMEOUT = float(os.environ.get("SCRAPER_TIMEOUT_SECONDS", "10"))

_last_request_lock = threading.Lock()
_last_request_ts = 0.0


class ScraperError(RuntimeError):
    pass


def _throttle():
    """Block until at least RATE_LIMIT_SECONDS has passed since the last
    outbound request, process-wide."""
    global _last_request_ts
    with _last_request_lock:
        now = time.monotonic()
        wait = RATE_LIMIT_SECONDS - (now - _last_request_ts)
        if wait > 0:
            time.sleep(wait)
        _last_request_ts = time.monotonic()


def _get(url, params=None):
    _throttle()
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json"}
    resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp


def _symbol_from_url(url: str) -> str:
    """screener.in result URLs look like /company/TCS/ or
    /company/TCS/consolidated/ -- the symbol is always the segment right
    after "company"."""
    parts = [p for p in url.split("/") if p]
    if "company" in parts:
        idx = parts.index("company")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return parts[-1] if parts else ""


def search_companies(query: str):
    """Search screener.in for companies matching `query`.

    Returns a list of {"symbol": str, "name": str, "url": str} dicts.
    Falls back to an empty list (not an exception) if upstream is unreachable,
    so the frontend search box degrades gracefully.
    """
    query = (query or "").strip()
    if not query:
        return []

    cache_key = f"search:{query.lower()}"
    cached = cache.get(cache_key, ttl_seconds=60 * 30)
    if cached is not None:
        return cached

    try:
        resp = _get(SEARCH_URL, params={"q": query})
        raw = resp.json()
    except (requests.RequestException, ValueError):
        return []

    results = []
    for item in raw:
        url = item.get("url", "")
        symbol = _symbol_from_url(url) if url else str(item.get("id", ""))
        results.append(
            {
                "symbol": symbol,
                "name": item.get("name", symbol),
                "url": f"{BASE_URL}{url}" if url.startswith("/") else url,
            }
        )

    cache.set(cache_key, results)
    return results


def _clean_number(text: str):
    if text is None:
        return None
    text = text.strip().replace(",", "")
    if text in ("", "-", "—"):
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    try:
        value = float(text)
    except ValueError:
        return None
    return -value if negative else value


def _parse_ratios(soup: BeautifulSoup):
    ratios = {}
    top_ratios = soup.select_one("#top-ratios")
    if not top_ratios:
        return ratios
    for li in top_ratios.select("li"):
        name_el = li.select_one(".name")
        value_el = li.select_one(".value")
        if not name_el or not value_el:
            continue
        name = name_el.get_text(strip=True)
        value = value_el.get_text(" ", strip=True)
        ratios[name] = value
    return ratios


def _table_to_records(table_html_or_df):
    """Normalize a pandas-parsed table into a list of row dicts."""
    if pd is None or table_html_or_df is None:
        return []
    df = table_html_or_df
    df = df.fillna("")
    columns = [str(c).strip() for c in df.columns]
    if columns and columns[0].lower().startswith("unnamed"):
        columns[0] = "Metric"
    df.columns = columns

    records = df.to_dict(orient="records")
    metric_col = columns[0]
    for record in records:
        # screener.in renders expandable rows as "Sales\xa0+" -- strip the
        # non-breaking space + expand marker so the label is clean.
        label = str(record.get(metric_col, ""))
        record[metric_col] = label.replace("\xa0+", "").replace("\xa0", " ").strip()
        for key, value in record.items():
            if key == metric_col:
                continue
            number = _clean_number(str(value))
            if number is not None:
                record[key] = number
    return records


def _find_section_table(soup: BeautifulSoup, section_id: str):
    """Find the <table> inside a section like #profit-loss / #balance-sheet
    / #cash-flow and parse it with pandas.read_html."""
    if pd is None:
        return None
    section = soup.select_one(f"#{section_id}")
    if not section:
        return None
    table = section.select_one("table")
    if not table:
        return None
    try:
        dfs = pd.read_html(io.StringIO(str(table)))
    except ValueError:
        return None
    return dfs[0] if dfs else None


def get_company_data(symbol: str, consolidated: bool = True):
    """Fetch + parse a screener.in company page.

    Returns a dict with: symbol, name, ratios, profit_loss, balance_sheet,
    cash_flow, quarterly. Any section that fails to parse is returned as an
    empty list/dict rather than raising, so the API can still respond with
    partial data.
    """
    symbol = symbol.strip().upper()
    cache_key = f"company:{symbol}:{'cons' if consolidated else 'std'}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url_tmpl = COMPANY_URL_CONSOLIDATED_TMPL if consolidated else COMPANY_URL_TMPL
    url = url_tmpl.format(symbol=symbol)

    try:
        resp = _get(url)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404 and consolidated:
            return get_company_data(symbol, consolidated=False)
        raise ScraperError(f"Failed to fetch {url}: {exc}") from exc
    except requests.RequestException as exc:
        raise ScraperError(f"Failed to fetch {url}: {exc}") from exc

    soup = BeautifulSoup(resp.text, "html.parser")

    name_el = soup.select_one("h1.margin-0") or soup.select_one("h1")
    name = name_el.get_text(strip=True) if name_el else symbol

    data = {
        "symbol": symbol,
        "name": name,
        "source_url": url,
        "ratios": _parse_ratios(soup),
        "profit_loss": _table_to_records(_find_section_table(soup, "profit-loss")),
        "balance_sheet": _table_to_records(_find_section_table(soup, "balance-sheet")),
        "cash_flow": _table_to_records(_find_section_table(soup, "cash-flow")),
        "quarterly": _table_to_records(_find_section_table(soup, "quarters")),
    }

    cache.set(cache_key, data)
    return data
