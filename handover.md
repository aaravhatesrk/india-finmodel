# Handover notes

## Repo layout

```
IndiaFinModel/
├── app.py                  # gunicorn entry point (re-exports backend.app)
├── backend/
│   ├── app.py               # Flask app: API routes + SPA static serving
│   ├── scraper.py            # screener.in client: search + company parsing
│   ├── excel_gen.py           # multi-sheet .xlsx builder (openpyxl)
│   ├── powerbi_gen.py          # CSV + .pbit placeholder + instructions zip
│   ├── cache.py                # file-based TTL cache for scraped pages
│   ├── cache/                  # cache storage (gitignored contents)
│   └── tests/                  # pytest suite
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # page layout: hero, overview, charts, report card
│   │   ├── api.js                 # fetch wrappers for the Flask API
│   │   └── components/             # Hero, SearchBar, TickerButtons,
│   │                                  CompanyOverview, FinancialCharts,
│   │                                  ReportGenerator
│   └── dist/                       # production build output (generated, gitignored)
├── samples/                          # sample .xlsx / .csv / .zip outputs (real TCS data)
├── DATA_README.md                      # scraping policy and rules
├── deploy-to-render.md                  # Render deploy steps
├── demo-script.txt                       # narration for a live/recorded demo
├── smoke_test.py                          # hits a running instance's API end-to-end
├── requirements.txt / Procfile / .env.example
```

## How the pieces fit together

- **Single web service**: Flask (`backend/app.py`) serves the API under
  `/api/*` and falls back to `frontend/dist/index.html` for everything
  else, so the SPA's client-side routing and a single Render service both
  work without a separate static host.
- **Scraping** is centralized in `backend/scraper.py`, rate-limited and
  cached (see `DATA_README.md`). Both report generators
  (`excel_gen.py`, `powerbi_gen.py`) consume the same `get_company_data()`
  dict shape: `{symbol, name, source_url, ratios, profit_loss,
  balance_sheet, cash_flow, quarterly}`.
- **Report generation** is synchronous and in-memory (`io.BytesIO`) — no
  temp files on disk, so it's safe on Render's ephemeral filesystem.

## What's mocked vs. real

- The 3 sample files in `/samples` were generated from **live** screener.in
  data for TCS (not synthetic placeholders) — see `DATA_README.md` for the
  exact pages they came from.
- The Power BI `.pbit` is a documented **placeholder** (see
  `powerbi_gen.PBIT_PLACEHOLDER_NOTE`) — real `.pbit` files can only be
  produced by Power BI Desktop's "Export as template" action, not by a
  backend service. The zip includes `INSTRUCTIONS.txt` with the exact steps
  to turn the shipped CSV into a real `.pbit` in a couple of minutes.

## Likely next steps for whoever picks this up

1. **Broaden scraper coverage**: add NSE/BSE bulk-data fallbacks if
   screener.in's selectors drift, or add a second provider for resilience.
2. **Auth/rate-limit the API** if this goes beyond a personal/demo deploy —
   currently anyone hitting `/api/*` can trigger a scrape (rate-limited and
   cached, but still public).
3. **Persistent cache**: swap `backend/cache.py`'s file cache for Redis if
   you run multiple gunicorn workers/instances and want a shared cache
   (today each worker has its own cache directory in memory-mapped disk,
   which is fine for a single small instance but not for horizontal scale).
4. **DCF engine**: the "DCF Inputs" sheet currently captures assumptions
   only; a follow-up could project cash flows and compute an intrinsic
   value automatically.

## Running locally

```bash
# backend
python -m venv .venv && source .venv/Scripts/activate  # or .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python app.py            # serves API on :5000 (frontend/dist must exist, or use the dev server below)

# frontend (separate terminal, for hot reload during development)
cd frontend
npm install
npm run dev               # proxies /api to localhost:5000, see vite.config.js
```

Run tests: `python -m pytest backend/tests -q`
