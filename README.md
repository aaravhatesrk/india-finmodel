# IndiaFinModel

Search any NSE/BSE listed Indian company, view its key fundamentals and
trends, and generate a polished multi-sheet Excel financial model or a
Power BI starter package — all from one React + Flask web app.

## Stack

- **Frontend**: Vite + React, custom CSS via Tailwind, [Recharts](https://recharts.org/)
  for charts. Palette: deep teal `#0f766e`, warm coral `#ff6b6b`, soft sand `#f7efe5`.
- **Backend**: Flask, serving both the JSON API and the built frontend as
  one process (ready for a single Render Web Service).
- **Data**: scraped from public pages on [screener.in](https://www.screener.in)
  with rate limiting + caching — see [DATA_README.md](DATA_README.md).

## Project layout

See [handover.md](handover.md) for the full breakdown of every file.

```
backend/    Flask app, scraper, Excel/Power BI generators, tests
frontend/   Vite + React app (src/components, src/api.js)
samples/    Sample .xlsx / .csv / .zip outputs (real TCS data)
```

## Running locally

```bash
# 1. Backend
python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev                        # http://localhost:5173, proxies /api to :5000

# 3. Backend, in the first terminal
python app.py                      # http://localhost:5000
```

For a production-style run (single process serving everything):

```bash
cd frontend && npm install && npm run build && cd ..
pip install -r requirements.txt
python app.py
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/search?q=` | Company name/symbol search suggestions |
| GET | `/api/company/<symbol>` | Fundamentals + financial tables for a symbol |
| POST | `/api/generate/excel` | `{symbol, options}` → streams a `.xlsx` |
| POST | `/api/generate/powerbi` | `{symbol, options}` → streams a `.zip` (CSV + .pbit placeholder + instructions) |

`options` for both generators: `growth_rate`, `discount_rate`,
`terminal_growth` (decimals, e.g. `0.10`), `projection_years` (int).

## Tests

```bash
python -m pytest backend/tests -q
```

11 tests cover the API routes (mocked scraper) and both report generators
(real Excel/zip structure assertions).

## Smoke test (against a running instance)

```bash
python smoke_test.py http://localhost:5000
```

Hits health, frontend serving, search, company lookup, and both generators
against a live process — useful right after a deploy.

## 3 quick verification checks

1. **It's alive**: `curl http://<host>/api/health` → `{"status": "ok"}`.
2. **Search works**: `curl "http://<host>/api/search?q=tcs"` returns a
   non-empty `results` array with a `TCS` symbol.
3. **Reports generate**: in the UI, search "TCS" → "Generate report" →
   both "Download Excel model" and "Download Power BI package" should
   produce non-empty files (or run `smoke_test.py`, which automates this).

## Deploying

See [deploy-to-render.md](deploy-to-render.md) for exact Render build/start
commands (single Web Service, no separate static site needed).

## Samples

`/samples` contains a real Excel model, Power BI CSV, and Power BI zip
package generated from live TCS data, so you can see the output without
running the app.
