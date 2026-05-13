type MetricCardProps = {
  label: string;
  value: string | number;
  accent: string;
  helper: string;
};

export function MetricCard({ label, value, accent, helper }: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-accent" style={{ background: accent }} />
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-helper">{helper}</div>
    </div>
  );
}

