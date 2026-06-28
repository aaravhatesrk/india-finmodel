const QUICK_TICKERS = [
  { symbol: "TCS", label: "TCS" },
  { symbol: "INFY", label: "Infosys" },
  { symbol: "RELIANCE", label: "Reliance" },
  { symbol: "HDFCBANK", label: "HDFC Bank" },
  { symbol: "ITC", label: "ITC" },
  { symbol: "TATAMOTORS", label: "Tata Motors" },
];

export default function TickerButtons({ onSelect, activeSymbol }) {
  return (
    <div className="flex flex-wrap gap-2 mt-4" role="group" aria-label="Quick ticker shortcuts">
      {QUICK_TICKERS.map((t) => (
        <button
          key={t.symbol}
          type="button"
          onClick={() => onSelect(t.symbol)}
          className={`focus-ring px-3 py-1.5 rounded-full text-sm font-medium transition-colors border ${
            activeSymbol === t.symbol
              ? "bg-coral border-coral text-white"
              : "bg-white/10 border-white/30 text-white hover:bg-white/20"
          }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
