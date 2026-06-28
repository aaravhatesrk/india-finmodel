const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function handleJson(resp) {
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${resp.status})`);
  }
  return resp.json();
}

export async function searchCompanies(query) {
  if (!query || !query.trim()) return { results: [] };
  const resp = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(query)}`);
  return handleJson(resp);
}

export async function fetchCompany(symbol) {
  const resp = await fetch(`${BASE_URL}/company/${encodeURIComponent(symbol)}`);
  return handleJson(resp);
}

async function downloadFile(path, payload, fallbackName) {
  const resp = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${resp.status})`);
  }
  const blob = await resp.blob();
  const disposition = resp.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : fallbackName;

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function generateExcel(symbol, options) {
  return downloadFile(
    "/generate/excel",
    { symbol, options },
    `${symbol}_financial_model.xlsx`
  );
}

export function generatePowerBi(symbol, options) {
  return downloadFile(
    "/generate/powerbi",
    { symbol, options },
    `${symbol}_powerbi_package.zip`
  );
}
