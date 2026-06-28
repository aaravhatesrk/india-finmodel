import { useState } from "react";
import Hero from "./components/Hero.jsx";
import SearchBar from "./components/SearchBar.jsx";
import TickerButtons from "./components/TickerButtons.jsx";
import CompanyOverview from "./components/CompanyOverview.jsx";
import FinancialCharts from "./components/FinancialCharts.jsx";
import ReportGenerator from "./components/ReportGenerator.jsx";
import { fetchCompany } from "./api.js";

export default function App() {
  const [symbol, setSymbol] = useState("");
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadCompany(sym) {
    setSymbol(sym);
    setLoading(true);
    setError("");
    setCompany(null);
    try {
      const data = await fetchCompany(sym);
      setCompany(data);
    } catch (err) {
      setError(err.message || "Could not load company data.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Hero>
        <SearchBar onSelect={loadCompany} />
        <TickerButtons onSelect={loadCompany} activeSymbol={symbol} />
      </Hero>

      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 py-10 w-full">
        {loading && (
          <div className="text-center py-16 text-teal-dark" role="status" aria-live="polite">
            Loading company data…
          </div>
        )}

        {!loading && error && (
          <div
            role="alert"
            className="bg-coral/10 text-coral-dark border border-coral/30 rounded-xl px-4 py-3 max-w-xl mx-auto text-center"
          >
            {error}
          </div>
        )}

        {!loading && !error && !company && (
          <div className="text-center py-16 text-slate-500">
            Search for a company above, or pick a quick ticker, to get started.
          </div>
        )}

        {company && !loading && (
          <div className="grid lg:grid-cols-[1fr_320px] gap-6 items-start">
            <div className="space-y-6">
              <CompanyOverview company={company} />
              <FinancialCharts company={company} />
            </div>
            <ReportGenerator symbol={company.symbol} />
          </div>
        )}
      </main>

      <footer className="text-center text-xs text-slate-400 py-6">
        Data sourced from publicly available pages on screener.in for
        educational use. See DATA_README.md for scraping policy.
      </footer>
    </div>
  );
}
