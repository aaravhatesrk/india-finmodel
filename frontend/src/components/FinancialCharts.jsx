import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const SERIES_COLORS = ["#0f766e", "#ff6b6b", "#d97706", "#3b82f6"];

function pivotByPeriod(records) {
  if (!records || records.length === 0) return { data: [], metrics: [] };

  const metricKey = Object.keys(records[0])[0];
  const periodKeys = Object.keys(records[0]).filter((k) => k !== metricKey);
  const metrics = records.map((r) => r[metricKey]);

  const data = periodKeys.map((period) => {
    const row = { period };
    records.forEach((record) => {
      const metricName = record[metricKey];
      row[metricName] = Number(record[period]) || 0;
    });
    return row;
  });

  return { data, metrics };
}

function Chart({ title, records }) {
  const { data, metrics } = pivotByPeriod(records);

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-card p-6">
        <h3 className="font-semibold text-slate-700 mb-2">{title}</h3>
        <p className="text-sm text-slate-400">No data available for this section.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-card p-6">
      <h3 className="font-semibold text-slate-700 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0e9dd" />
          <XAxis dataKey="period" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ borderRadius: 8, borderColor: "#0f766e" }}
            formatter={(value) => Number(value).toLocaleString("en-IN")}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {metrics.slice(0, 4).map((metric, idx) => (
            <Line
              key={metric}
              type="monotone"
              dataKey={metric}
              stroke={SERIES_COLORS[idx % SERIES_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function FinancialCharts({ company }) {
  return (
    <div className="grid sm:grid-cols-2 gap-6">
      <Chart title="Profit & Loss" records={company.profit_loss} />
      <Chart title="Balance Sheet" records={company.balance_sheet} />
      <Chart title="Cash Flow" records={company.cash_flow} />
      <Chart title="Quarterly Results" records={company.quarterly} />
    </div>
  );
}
