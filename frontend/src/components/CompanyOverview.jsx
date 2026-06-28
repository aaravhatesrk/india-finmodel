export default function CompanyOverview({ company }) {
  const ratios = Object.entries(company.ratios || {});

  return (
    <section className="bg-white rounded-2xl shadow-card p-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">{company.name}</h2>
          <p className="text-sm text-slate-500">{company.symbol}</p>
        </div>
        {company.source_url && (
          <a
            href={company.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-teal hover:text-teal-dark underline focus-ring"
          >
            View source
          </a>
        )}
      </div>

      {ratios.length > 0 && (
        <dl className="mt-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {ratios.map(([label, value]) => (
            <div key={label} className="bg-sand rounded-xl px-4 py-3">
              <dt className="text-xs text-slate-500 uppercase tracking-wide">
                {label}
              </dt>
              <dd className="text-base font-semibold text-teal-dark mt-0.5">
                {value}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}
