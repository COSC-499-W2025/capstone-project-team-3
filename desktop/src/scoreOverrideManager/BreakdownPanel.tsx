import {
  OverridePreview,
  ScoreBreakdown,
  ScoreBreakdownMetric,
} from "../api/projects";
import { pct } from "./formatters";
import { METRIC_LABELS } from "./metadata";

interface BreakdownPanelProps {
  breakdown: ScoreBreakdown["breakdown"] | null;
  previewBreakdown: OverridePreview["breakdown"] | null;
  excludedMetrics: Set<string>;
}

interface BreakdownBarProps {
  name: string;
  metric: ScoreBreakdownMetric;
  excluded: boolean;
  max: number;
  readOnly?: boolean;
}

function BreakdownBar({ name, metric, excluded, max, readOnly }: BreakdownBarProps) {
  const label = METRIC_LABELS[name] ?? name;
  const barPct = max > 0 ? ((excluded ? 0 : metric.contribution) / max) * 100 : 0;

  return (
    <div
      className={`sor-breakdown-bar-row ${excluded ? "sor-bar-excluded" : ""} ${readOnly ? "sor-bar-readonly" : ""}`}
    >
      <div className="sor-bar-header">
        <span className="sor-bar-label">
          {label}
          {readOnly && <span className="sor-bar-readonly-badge">read-only</span>}
          {excluded && <span className="sor-bar-excluded-badge">excluded</span>}
        </span>
        <span className="sor-bar-value">
          {excluded ? "—" : pct(metric.contribution)}
          <span className="sor-bar-weight"> ({pct(metric.weight)} weight)</span>
        </span>
      </div>
      <div className="sor-bar-track">
        <div className="sor-bar-fill" style={{ width: `${barPct}%` }} />
      </div>
    </div>
  );
}

export default function BreakdownPanel({
  breakdown,
  previewBreakdown,
  excludedMetrics,
}: BreakdownPanelProps) {
  const active = previewBreakdown ?? breakdown;
  if (!active) return null;

  const codeMetrics = active.code?.metrics ?? {};
  const nonCodeMetrics = active.non_code?.metrics ?? {};
  const blend = active.blend;
  const allContributions = [
    ...Object.values(codeMetrics).map((metric) => metric.contribution),
    ...Object.values(nonCodeMetrics).map((metric) => metric.contribution),
  ];
  const max = Math.max(...allContributions, 0.01);

  return (
    <div className="sor-breakdown">
      <h3 className="sor-section-title">Score Breakdown</h3>

      {blend && (
        <div className="sor-blend-info">
          <div className="sor-blend-bar">
            <div
              className="sor-blend-segment sor-blend-code"
              style={{ width: `${(blend.code_percentage ?? 0) * 100}%` }}
              title={`Code: ${pct(blend.code_percentage ?? 0)}`}
            >
              Code {pct(blend.code_percentage ?? 0)}
            </div>
            <div
              className="sor-blend-segment sor-blend-docs"
              style={{ width: `${(blend.non_code_percentage ?? 0) * 100}%` }}
              title={`Docs: ${pct(blend.non_code_percentage ?? 0)}`}
            >
              Docs {pct(blend.non_code_percentage ?? 0)}
            </div>
          </div>
          <p className="sor-blend-hint">
            Score is blended from code activity and documentation
          </p>
        </div>
      )}

      {Object.keys(codeMetrics).length > 0 && (
        <div className="sor-breakdown-section">
          <h4 className="sor-breakdown-category">
            Code Metrics
            <span className="sor-subtotal">subtotal {pct(active.code?.subtotal ?? 0)}</span>
          </h4>
          {Object.entries(codeMetrics).map(([name, metric]) => (
            <BreakdownBar
              key={name}
              name={name}
              metric={metric}
              excluded={excludedMetrics.has(name)}
              max={max}
            />
          ))}
        </div>
      )}

      {Object.keys(nonCodeMetrics).length > 0 && (
        <div className="sor-breakdown-section">
          <h4 className="sor-breakdown-category">
            Documentation Metrics
            <span className="sor-subtotal">subtotal {pct(active.non_code?.subtotal ?? 0)}</span>
          </h4>
          {Object.entries(nonCodeMetrics).map(([name, metric]) => (
            <BreakdownBar
              key={name}
              name={name}
              metric={metric}
              excluded={false}
              max={max}
              readOnly
            />
          ))}
        </div>
      )}
    </div>
  );
}
