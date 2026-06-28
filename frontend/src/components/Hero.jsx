export default function Hero({ children }) {
  return (
    <header className="bg-gradient-to-br from-teal to-teal-dark text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <p className="inline-block text-xs font-semibold tracking-wide uppercase bg-white/15 px-3 py-1 rounded-full mb-4">
          Indian equities, modeled in seconds
        </p>
        <h1 className="text-3xl sm:text-5xl font-bold leading-tight max-w-2xl">
          Search any NSE/BSE company,{" "}
          <span className="text-coral">build a financial model</span> instantly.
        </h1>
        <p className="mt-4 text-teal-50/90 max-w-xl text-sm sm:text-base">
          IndiaFinModel pulls public fundamentals, then generates a polished
          multi-sheet Excel model or a tidy Power BI package — ready for your
          own analysis.
        </p>
        <div className="mt-8">{children}</div>
      </div>
    </header>
  );
}
