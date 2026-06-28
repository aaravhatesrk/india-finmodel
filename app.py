"""Entry point for gunicorn (`gunicorn app:app`). The real Flask app and all
routes live in backend/app.py; this module just re-exports it from the repo
root so the Render start command and `python app.py` both work."""
from backend.app import app

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
