import { ScoreBreakdownMetric } from "../api/projects";
import { pct } from "./formatters";
import { METRIC_DESCRIPTIONS, METRIC_LABELS } from "./metadata";

interface MetricRowProps {
  name: string;
  metric: ScoreBreakdownMetric;
  excluded: boolean;
  onChange: (name: string, excluded: boolean) => void;
  maxContribution: number;
}

export default function MetricRow({
  name,
  metric,
  excluded,
  onChange,
  maxContribution,
}: MetricRowProps) {
  const label = METRIC_LABELS[name] ?? name;
  const desc = METRIC_DESCRIPTIONS[name] ?? "";
  const barWidth = maxContribution > 0 ? (metric.contribution / maxContribution) * 100 : 0;

  return (
    <div className={`sor-metric-row ${excluded ? "sor-metric-excluded" : ""}`}>
      <label className="sor-metric-label">
        <input
          type="checkbox"
          className="sor-checkbox"
          checked={!excluded}
          onChange={(e) => onChange(name, !e.target.checked)}
        />
        <span className="sor-metric-name">{label}</span>
      </label>
      <div className="sor-metric-details">
        <div className="sor-metric-bar-track">
          <div
            className="sor-metric-bar-fill"
            style={{ width: `${excluded ? 0 : barWidth}%` }}
          />
        </div>
        <div className="sor-metric-stats">
          <span className="sor-stat">
            <span className="sor-stat-label">Raw</span>
            <span className="sor-stat-value">
              {typeof metric.raw === "number" ? metric.raw.toLocaleString() : metric.raw}
            </span>
          </span>
          <span className="sor-stat">
            <span className="sor-stat-label">Normalized</span>
            <span className="sor-stat-value">{pct(metric.normalized)}</span>
          </span>
          <span className="sor-stat">
            <span className="sor-stat-label">Weight</span>
            <span className="sor-stat-value">{pct(metric.weight)}</span>
          </span>
          <span className="sor-stat">
            <span className="sor-stat-label">Contribution</span>
            <span className="sor-stat-value">{excluded ? "—" : pct(metric.contribution)}</span>
          </span>
        </div>
        {desc && <p className="sor-metric-desc">{desc}</p>}
      </div>
    </div>
  );
}
