# Data sourcing & scraping policy

IndiaFinModel pulls company fundamentals from publicly available pages on
[screener.in](https://www.screener.in), a well-known Indian equity research
site. This document describes exactly what is fetched, how often, and the
rules the scraper follows.

## Endpoints used

| Purpose | URL pattern |
|---|---|
| Company search (JSON) | `https://www.screener.in/api/company/search/?q=<query>` |
| Company financials (consolidated) | `https://www.screener.in/company/<SYMBOL>/consolidated/` |
| Company financials (standalone fallback) | `https://www.screener.in/company/<SYMBOL>/` |

Only **public, unauthenticated** pages are read. No login, session cookie,
or paid/Premium data is accessed.

## Politeness rules (enforced in `backend/scraper.py`)

1. **Rate limiting** — at most one outbound request every
   `SCRAPER_DELAY_SECONDS` (default **2 seconds**), enforced process-wide
   with a lock, regardless of how many concurrent API requests arrive.
2. **Caching** — every response is cached to disk (`backend/cache.py`) for
   `CACHE_TTL_SECONDS` (default 6 hours for company pages, 30 minutes for
   search). Repeat lookups within the TTL never hit screener.in again.
3. **Identification** — requests send a descriptive `User-Agent` string
   identifying this as an educational/research tool, not a disguised
   browser.
4. **Timeouts** — requests time out after `SCRAPER_TIMEOUT_SECONDS`
   (default 10s) so a slow upstream never hangs the API.
5. **Graceful degradation** — if a page or section fails to parse (e.g. the
   site changes its HTML), that section is returned empty rather than
   crashing the request. Search failures return an empty result list.

## What is parsed

From each company page:
- **Name** and **ratio panel** (P/E, ROE, ROCE, market cap, etc.)
- **Profit & Loss**, **Balance Sheet**, **Cash Flow**, and **Quarterly
  Results** tables, parsed with `pandas.read_html` against the table inside
  each section's `id` (`#profit-loss`, `#balance-sheet`, `#cash-flow`,
  `#quarters`).

Numbers are cleaned (commas removed, parenthesised negatives converted) and
returned as native floats/ints wherever possible, falling back to the raw
string if a value can't be parsed.

## Known limitations

- screener.in's HTML structure can change at any time. This scraper is
  best-effort: if a section's selectors stop matching, that section comes
  back empty instead of breaking the whole request.
- Some smaller/delisted companies may have incomplete sections (e.g. no
  quarterly data).
- This tool is for personal research and educational use. Respect
  screener.in's [Terms of Use](https://www.screener.in/terms/) and
  `robots.txt` if you deploy this beyond light personal use, and consider
  reaching out to screener.in for an API key/bulk-data arrangement for
  any heavier or commercial usage.

## Adjusting the rate limit

Set `SCRAPER_DELAY_SECONDS` (and `CACHE_TTL_SECONDS`) in your `.env` (see
`.env.example`). Increase the delay if you are scraping many symbols in a
short period.
