import os

from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

from . import excel_gen, powerbi_gen, scraper

FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"
)

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/search")
def search():
    query = request.args.get("q", "")
    try:
        results = scraper.search_companies(query)
    except scraper.ScraperError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"query": query, "results": results})


@app.get("/api/company/<symbol>")
def company(symbol):
    consolidated = request.args.get("consolidated", "true").lower() != "false"
    try:
        data = scraper.get_company_data(symbol, consolidated=consolidated)
    except scraper.ScraperError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify(data)


@app.post("/api/generate/excel")
def generate_excel():
    payload = request.get_json(silent=True) or {}
    symbol = payload.get("symbol")
    options = payload.get("options") or {}
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    try:
        company_data = scraper.get_company_data(symbol)
    except scraper.ScraperError as exc:
        return jsonify({"error": str(exc)}), 502

    xlsx_bytes = excel_gen.build_excel_report(company_data, options)
    return send_file(
        io_bytes(xlsx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"{symbol.upper()}_financial_model.xlsx",
    )


@app.post("/api/generate/powerbi")
def generate_powerbi():
    payload = request.get_json(silent=True) or {}
    symbol = payload.get("symbol")
    options = payload.get("options") or {}
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    try:
        company_data = scraper.get_company_data(symbol)
    except scraper.ScraperError as exc:
        return jsonify({"error": str(exc)}), 502

    zip_bytes = powerbi_gen.build_powerbi_package(company_data, options)
    return send_file(
        io_bytes(zip_bytes),
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{symbol.upper()}_powerbi_package.zip",
    )


def io_bytes(data: bytes):
    import io

    return io.BytesIO(data)


# --- Serve the built React app (single Render web service) ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path.startswith("api/"):
        return jsonify({"error": "not found"}), 404
    full_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.exists(full_path):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
