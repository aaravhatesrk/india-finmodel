"""Builds a Power BI starter package: a tidy CSV of the company's financials,
a .pbit placeholder (Power BI Desktop template files are a binary/zip format
that cannot be meaningfully generated server-side without Power BI Desktop
itself), and a step-by-step instructions file -- all zipped together."""
import csv
import io
import zipfile

PBIT_PLACEHOLDER_NOTE = b"""This is a PLACEHOLDER, not a real .pbit file.

Power BI template files (.pbit) are produced by Power BI Desktop when you
choose File > Export > Export this file as a template. They cannot be
generated correctly by a backend service without running Power BI Desktop,
so IndiaFinModel ships a tidy CSV plus instructions instead -- see
INSTRUCTIONS.txt in this zip for the exact steps to build your own .pbit
from the CSV in a couple of minutes.
"""

INSTRUCTIONS_TMPL = """IndiaFinModel - Power BI Quick Start
=====================================

Company: {name} ({symbol})
Generated CSV: data.csv

1. Open Power BI Desktop.
2. Home > Get Data > Text/CSV.
3. Select data.csv from this zip and click Load.
4. In the Fields pane, confirm "Period" is recognized as text/date and
   "Metric" / "Value" as text/decimal. Use Transform Data if you need to
   fix column types.
5. Build visuals, e.g.:
   - Line chart: Period (axis) x Value (values), filtered by Metric.
   - Table: Metric x Value for the latest Period.
   - Card: a single KPI (e.g. latest Revenue or PAT).
6. Once your report looks right, save as .pbix, then optionally
   File > Export > Export this file as a template to produce a real .pbit
   you can re-use for other companies.

Tip: re-run "Generate report > Power BI" for another company/symbol to get
a fresh CSV with the same column layout, so your visuals keep working.
"""


def _flatten_to_rows(company: dict):
    """Turn the company dict's tabular sections into tidy
    (section, period/column, metric, value) rows for a single CSV."""
    rows = []
    sections = {
        "Profit & Loss": company.get("profit_loss") or [],
        "Balance Sheet": company.get("balance_sheet") or [],
        "Cash Flow": company.get("cash_flow") or [],
        "Quarterly": company.get("quarterly") or [],
    }
    for section_name, records in sections.items():
        for record in records:
            keys = list(record.keys())
            if not keys:
                continue
            metric_key = keys[0]
            metric = record.get(metric_key)
            for period_key in keys[1:]:
                rows.append(
                    {
                        "Section": section_name,
                        "Metric": metric,
                        "Period": period_key,
                        "Value": record.get(period_key),
                    }
                )

    for name, value in (company.get("ratios") or {}).items():
        rows.append({"Section": "Key Ratios", "Metric": name, "Period": "Latest", "Value": value})

    return rows


def build_csv(company: dict) -> bytes:
    rows = _flatten_to_rows(company)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["Section", "Metric", "Period", "Value"])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def build_powerbi_package(company: dict, options: dict | None = None) -> bytes:
    """Returns a zip (bytes) containing data.csv, placeholder.pbit and
    INSTRUCTIONS.txt."""
    csv_bytes = build_csv(company)
    instructions = INSTRUCTIONS_TMPL.format(
        name=company.get("name", company.get("symbol", "Company")),
        symbol=company.get("symbol", ""),
    ).encode("utf-8")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("data.csv", csv_bytes)
        zf.writestr("placeholder.pbit", PBIT_PLACEHOLDER_NOTE)
        zf.writestr("INSTRUCTIONS.txt", instructions)
    buffer.seek(0)
    return buffer.read()
