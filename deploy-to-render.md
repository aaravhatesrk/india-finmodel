# Deploying IndiaFinModel to Render (single Web Service)

This repo ships as **one** Render Web Service: Flask serves both the API
(`/api/*`) and the built React frontend (everything else), so there's no
separate static site to configure.

## 1. Push the repo to GitHub (or GitLab/Bitbucket)

Render deploys from a git remote, so create a repo and push this project
there first if you haven't already.

## 2. Create the Web Service on Render

1. [render.com](https://render.com) → **New** → **Web Service**.
2. Connect your repository and select the `IndiaFinModel` repo.
3. Configure:
   - **Environment**: `Python 3`
   - **Build Command**:
     ```
     bash -lc "cd frontend && npm ci && npm run build && cd .. && pip install -r requirements.txt"
     ```
   - **Start Command**:
     ```
     gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
     ```
   - **Instance type**: Starter is enough to demo this.

Render automatically sets the `$PORT` environment variable — `app.py` and
the start command both read it, so no extra config is required there.

## 3. Environment variables

Copy the keys from `.env.example` into Render's **Environment** tab if you
want non-default values. Nothing is required for a basic deploy — sensible
defaults are baked in:

| Key | Default | Purpose |
|---|---|---|
| `SCRAPER_DELAY_SECONDS` | `2` | Minimum gap between screener.in requests |
| `SCRAPER_TIMEOUT_SECONDS` | `10` | Per-request timeout |
| `CACHE_TTL_SECONDS` | `21600` (6h) | How long company data is cached on disk |
| `FLASK_DEBUG` | `0` | Keep `0` in production |

## 4. Deploy

Click **Create Web Service**. Render will run the build command (installs
frontend deps, builds the Vite bundle into `frontend/dist`, then installs
Python deps), then start gunicorn. The first build typically takes 2–4
minutes.

## 5. Verify

Once live, open the service URL and:
- The hero page with the search bar should load (served by Flask's static
  handler from `frontend/dist`).
- `https://<your-service>.onrender.com/api/health` should return
  `{"status": "ok"}`.
- Search for "TCS" and generate an Excel/Power BI report to confirm the
  full path works end-to-end.

## Notes on disk cache

`backend/cache/*.json` is a simple file cache for scraped pages. Render's
free/starter disks are ephemeral across deploys (not across requests within
a running instance), so the cache simply rebuilds itself after a redeploy —
no action needed.
