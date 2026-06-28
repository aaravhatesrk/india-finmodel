import { useState } from "react";
import { generateExcel, generatePowerBi } from "../api.js";

export default function ReportGenerator({ symbol }) {
  const [growthRate, setGrowthRate] = useState(10);
  const [discountRate, setDiscountRate] = useState(12);
  const [terminalGrowth, setTerminalGrowth] = useState(4);
  const [projectionYears, setProjectionYears] = useState(5);
  const [pending, setPending] = useState(null);
  const [error, setError] = useState("");
  const [lastSuccess, setLastSuccess] = useState("");

  const options = {
    growth_rate: growthRate / 100,
    discount_rate: discountRate / 100,
    terminal_growth: terminalGrowth / 100,
    projection_years: projectionYears,
  };

  async function handleGenerate(kind) {
    if (!symbol) {
      setError("Search for a company first.");
      return;
    }
    setError("");
    setLastSuccess("");
    setPending(kind);
    try {
      if (kind === "excel") {
        await generateExcel(symbol, options);
        setLastSuccess("Excel model downloaded.");
      } else {
        await generatePowerBi(symbol, options);
        setLastSuccess("Power BI package downloaded.");
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setPending(null);
    }
  }

  return (
    <aside className="bg-white rounded-2xl shadow-card p-6 sticky top-6 h-fit">
      <h3 className="text-lg font-bold text-slate-800">Generate report</h3>
      <p className="text-sm text-slate-500 mt-1">
        {symbol ? (
          <>
            For <span className="font-semibold text-teal-dark">{symbol}</span>
          </>
        ) : (
          "Pick a company to enable downloads."
        )}
      </p>

      <div className="mt-5 space-y-4">
        <NumberField
          label="Revenue growth rate (%)"
          value={growthRate}
          onChange={setGrowthRate}
        />
        <NumberField
          label="Discount rate / WACC (%)"
          value={discountRate}
          onChange={setDiscountRate}
        />
        <NumberField
          label="Terminal growth rate (%)"
          value={terminalGrowth}
          onChange={setTerminalGrowth}
        />
        <NumberField
          label="Projection years"
          value={projectionYears}
          onChange={setProjectionYears}
          step={1}
        />
      </div>

      <div className="mt-6 flex flex-col gap-3">
        <button
          type="button"
          disabled={!symbol || pending !== null}
          onClick={() => handleGenerate("excel")}
          className="focus-ring bg-teal hover:bg-teal-dark disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl px-4 py-3 transition-colors"
        >
          {pending === "excel" ? "Building Excel…" : "Download Excel model (.xlsx)"}
        </button>
        <button
          type="button"
          disabled={!symbol || pending !== null}
          onClick={() => handleGenerate("powerbi")}
          className="focus-ring bg-coral hover:bg-coral-dark disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl px-4 py-3 transition-colors"
        >
          {pending === "powerbi" ? "Building Power BI package…" : "Download Power BI package (.zip)"}
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-4 text-sm text-coral-dark bg-coral/10 rounded-lg px-3 py-2">
          {error}
        </p>
      )}
      {lastSuccess && !error && (
        <p role="status" className="mt-4 text-sm text-teal-dark bg-teal/10 rounded-lg px-3 py-2">
          {lastSuccess}
        </p>
      )}

      <p className="mt-4 text-xs text-slate-400">
        The Power BI package contains a tidy CSV, a placeholder .pbit, and
        step-by-step instructions to build your own template in Power BI
        Desktop.
      </p>
    </aside>
  );
}

function NumberField({ label, value, onChange, step = 0.5 }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-600">{label}</span>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="focus-ring mt-1 w-full rounded-lg border border-sand-dark bg-sand/60 px-3 py-2 text-slate-800"
      />
    </label>
  );
}
