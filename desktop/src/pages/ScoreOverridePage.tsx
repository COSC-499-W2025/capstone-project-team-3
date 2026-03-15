import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  OverridePreview,
  Project,
  ScoreBreakdown,
  ScoreBreakdownMetric,
  applyScoreOverride,
  clearScoreOverride,
  getProjects,
  getScoreBreakdown,
  previewScoreOverride,
} from "../api/projects";
import "../styles/ScoreOverridePage.css";

const METRIC_LABELS: Record<string, string> = {
  total_commits: "Total Commits",
  duration_days: "Project Duration",
  total_lines: "Lines of Code",
  code_files_changed: "Code Files",
  test_files_changed: "Test Files",
  total_files: "Total Files",
  maintainability_score: "Maintainability",
  completeness_score: "Documentation Completeness",
};

const METRIC_DESCRIPTIONS: Record<string, string> = {
  total_commits: "Number of git commits in the project history",
  duration_days: "Time span from first to last commit",
  total_lines: "Total lines of code across all source files",
  code_files_changed: "Number of source code files modified",
  test_files_changed: "Number of test files present",
  total_files: "Total number of files in the project",
  maintainability_score: "Code maintainability index (0–100)",
  completeness_score: "Documentation completeness ratio",
};

function scoreColor(value: number): string {
  if (value >= 0.75) return "#27ae60";
  if (value >= 0.5) return "#f39c12";
  return "#e74c3c";
}

function scoreDiffColor(diff: number): string {
  if (diff > 0) return "#27ae60";
  if (diff < 0) return "#e74c3c";
  return "#718096";
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

interface MetricRowProps {
  name: string;
  metric: ScoreBreakdownMetric;
  excluded: boolean;
  onChange: (name: string, excluded: boolean) => void;
  maxContribution: number;
}

function MetricRow({ name, metric, excluded, onChange, maxContribution }: MetricRowProps) {
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
            <span className="sor-stat-value">{typeof metric.raw === "number" ? metric.raw.toLocaleString() : metric.raw}</span>
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

interface ScoreGaugeProps {
  label: string;
  value: number;
  badge?: React.ReactNode;
}

function ScoreGauge({ label, value, badge }: ScoreGaugeProps) {
  const color = scoreColor(value);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const dash = circumference * value;
  return (
    <div className="sor-gauge-wrap">
      <svg className="sor-gauge-svg" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} className="sor-gauge-track" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          className="sor-gauge-fill"
          style={{
            stroke: color,
            strokeDasharray: `${dash} ${circumference}`,
          }}
        />
        <text x="60" y="60" className="sor-gauge-text" dy=".35em">
          {pct(value)}
        </text>
      </svg>
      <p className="sor-gauge-label">{label}</p>
      {badge}
    </div>
  );
}

interface BreakdownPanelProps {
  breakdown: ScoreBreakdown["breakdown"] | null;
  previewBreakdown: OverridePreview["breakdown"] | null;
  excludedMetrics: Set<string>;
}

function BreakdownPanel({ breakdown, previewBreakdown, excludedMetrics }: BreakdownPanelProps) {
  const active = previewBreakdown ?? breakdown;
  if (!active) return null;

  const codeMetrics = active.code?.metrics ?? {};
  const nonCodeMetrics = active.non_code?.metrics ?? {};
  const blend = active.blend;

  const allContributions = [
    ...Object.values(codeMetrics).map((m) => m.contribution),
    ...Object.values(nonCodeMetrics).map((m) => m.contribution),
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
          <p className="sor-blend-hint">Score is blended from code activity and documentation</p>
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
    <div className={`sor-breakdown-bar-row ${excluded ? "sor-bar-excluded" : ""} ${readOnly ? "sor-bar-readonly" : ""}`}>
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

type StatusType = "success" | "error" | "info";
interface StatusMsg {
  type: StatusType;
  text: string;
}

function getErrorText(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

interface ImprovementHint {
  name: string;
  metric: ScoreBreakdownMetric;
  potentialUplift: number;
}

export default function ScoreOverridePage() {
  const [searchParams] = useSearchParams();
  const preselectedProjectId = searchParams.get("project") ?? "";
  const fromPortfolio = searchParams.get("from") === "portfoliopage";
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string>(preselectedProjectId);
  const [breakdown, setBreakdown] = useState<ScoreBreakdown | null>(null);
  const [excludedMetrics, setExcludedMetrics] = useState<Set<string>>(new Set());
  const [preview, setPreview] = useState<OverridePreview | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<StatusMsg | null>(null);
  const previewTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const statusTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const breakdownRequestRef = useRef(0);
  const previewRequestRef = useRef(0);

  // Load all projects on mount
  useEffect(() => {
    getProjects()
      .then(setProjects)
      .catch((error) => showStatus("error", getErrorText(error, "Failed to load projects")))
      .finally(() => setLoadingProjects(false));
  }, []);

  useEffect(() => {
    return () => {
      if (previewTimerRef.current) clearTimeout(previewTimerRef.current);
      if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (preselectedProjectId) {
      setSelectedId(preselectedProjectId);
    }
  }, [preselectedProjectId]);

  function showStatus(type: StatusType, text: string) {
    setStatus({ type, text });
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
    statusTimerRef.current = setTimeout(() => setStatus(null), 4000);
  }

  // Load breakdown when project changes
  useEffect(() => {
    const requestId = ++breakdownRequestRef.current;
    if (!selectedId) {
      setBreakdown(null);
      setPreview(null);
      setExcludedMetrics(new Set());
      setLoadingBreakdown(false);
      return;
    }
    setLoadingBreakdown(true);
    setBreakdown(null);
    setPreview(null);
    previewRequestRef.current += 1;
    if (previewTimerRef.current) clearTimeout(previewTimerRef.current);
    getScoreBreakdown(selectedId)
      .then((data) => {
        if (requestId !== breakdownRequestRef.current) return;
        setBreakdown(data);
        setExcludedMetrics(new Set(data.exclude_metrics ?? []));
      })
      .catch((error) => {
        if (requestId !== breakdownRequestRef.current) return;
        showStatus("error", getErrorText(error, "Failed to load score breakdown"));
      })
      .finally(() => {
        if (requestId === breakdownRequestRef.current) {
          setLoadingBreakdown(false);
        }
      });
  }, [selectedId]);

  // Debounced auto-preview when exclusions change
  const schedulePreview = useCallback(
    (id: string, exclusions: Set<string>) => {
      if (previewTimerRef.current) clearTimeout(previewTimerRef.current);
      const requestId = ++previewRequestRef.current;
      previewTimerRef.current = setTimeout(async () => {
        setLoadingPreview(true);
        try {
          const result = await previewScoreOverride(id, Array.from(exclusions));
          if (requestId !== previewRequestRef.current) return;
          setPreview(result);
        } catch (error) {
          if (requestId !== previewRequestRef.current) return;
          showStatus("error", getErrorText(error, "Failed to compute preview"));
        } finally {
          if (requestId === previewRequestRef.current) {
            setLoadingPreview(false);
          }
        }
      }, 400);
    },
    []
  );

  function handleMetricToggle(name: string, nowExcluded: boolean) {
    setExcludedMetrics((prev) => {
      const next = new Set(prev);
      if (nowExcluded) next.add(name);
      else next.delete(name);
      if (selectedId) schedulePreview(selectedId, next);
      return next;
    });
  }

  async function handleApply() {
    if (!selectedId) return;
    setSaving(true);
    try {
      previewRequestRef.current += 1;
      if (previewTimerRef.current) clearTimeout(previewTimerRef.current);
      await applyScoreOverride(selectedId, Array.from(excludedMetrics));
      const fresh = await getScoreBreakdown(selectedId);
      setBreakdown(fresh);
      setPreview(null);
      showStatus("success", "Score override applied successfully");
    } catch (error) {
      showStatus("error", getErrorText(error, "Failed to apply override"));
    } finally {
      setSaving(false);
    }
  }

  async function handleClear() {
    if (!selectedId) return;
    setSaving(true);
    try {
      previewRequestRef.current += 1;
      if (previewTimerRef.current) clearTimeout(previewTimerRef.current);
      await clearScoreOverride(selectedId);
      const fresh = await getScoreBreakdown(selectedId);
      setBreakdown(fresh);
      setExcludedMetrics(new Set());
      setPreview(null);
      showStatus("success", "Score override cleared — original score restored");
    } catch (error) {
      showStatus("error", getErrorText(error, "Failed to clear override"));
    } finally {
      setSaving(false);
    }
  }

  function handleReset() {
    if (!breakdown) return;
    const original = new Set(breakdown.exclude_metrics ?? []);
    setExcludedMetrics(original);
    if (selectedId) schedulePreview(selectedId, original);
  }

  const selectedProject = projects.find((p) => p.id === selectedId);
  const codeMetrics = breakdown?.breakdown?.code?.metrics ?? {};
  const maxContribution = Math.max(
    ...Object.values(codeMetrics).map((m) => m.contribution),
    0.01
  );
  const improvementHints: ImprovementHint[] = Object.entries(codeMetrics)
    .filter(([name]) => !excludedMetrics.has(name))
    .map(([name, metric]) => ({
      name,
      metric,
      potentialUplift: Math.max(0, (1 - metric.normalized) * metric.weight),
    }))
    .filter((item) => item.potentialUplift > 0.005)
    .sort((a, b) => b.potentialUplift - a.potentialUplift)
    .slice(0, 3);

  const currentScore = preview?.current_score ?? breakdown?.score ?? 0;
  const previewScore = preview?.preview_score ?? currentScore;
  const scoreDiff = previewScore - currentScore;
  const hasChanges =
    breakdown &&
    JSON.stringify(Array.from(excludedMetrics).sort()) !==
      JSON.stringify((breakdown.exclude_metrics ?? []).slice().sort());

  return (
    <div className="sor-page">
      {/* Header */}
      <header className="sor-header">
        <div className="sor-header-inner">
          <div>
            {fromPortfolio && (
              <Link to="/portfoliopage" className="sor-context-link">
                Back to Portfolio
              </Link>
            )}
            <h1 className="sor-title">Score Override</h1>
            <p className="sor-subtitle">
              Adjust which metrics contribute to a project's score. Excluded metrics are removed
              and the remaining weights are renormalized automatically.
            </p>
            {fromPortfolio && (
              <p className="sor-context-note">
                Changes applied here will be reflected in the portfolio view and in the downloaded portfolio export.
              </p>
            )}
          </div>
          {status && (
            <div className={`sor-status sor-status-${status.type}`}>{status.text}</div>
          )}
        </div>
      </header>

      <main className="sor-main">
        {/* Project Selector */}
        <section className="sor-selector-section">
          <label className="sor-select-label" htmlFor="project-select">
            Select Project
          </label>
          <div className="sor-select-wrap">
            {loadingProjects ? (
              <div className="sor-spinner-inline" />
            ) : (
              <select
                id="project-select"
                className="sor-select"
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              >
                <option value="">— Choose a project —</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                    {p.score_overridden ? " ✦" : ""}{" "}
                    — {pct(p.score)}
                  </option>
                ))}
              </select>
            )}
            {selectedProject?.score_overridden && (
              <span className="sor-override-badge sor-override-badge-active">Override Active</span>
            )}
          </div>
        </section>

        {/* Main content */}
        {!selectedId && !loadingProjects && (
          <div className="sor-empty-state">
            <div className="sor-empty-icon">⚖</div>
            <p>Select a project above to manage its score metrics</p>
          </div>
        )}

        {loadingBreakdown && (
          <div className="sor-loading">
            <div className="sor-spinner" />
            <p>Loading breakdown…</p>
          </div>
        )}

        {breakdown && !loadingBreakdown && (
          <div className="sor-content">
            {/* Left: Metrics panel */}
            <div className="sor-left-panel">
              <div className="sor-panel">
                <div className="sor-panel-header">
                  <h2 className="sor-panel-title">Code Metrics</h2>
                  <p className="sor-panel-hint">
                    Uncheck a metric to exclude it from the score calculation
                  </p>
                </div>
                <div className="sor-scoring-guide">
                  <p className="sor-scoring-guide-title">How to read each metric</p>
                  <div className="sor-scoring-guide-grid">
                    <span className="sor-scoring-guide-label">Raw</span>
                    <span className="sor-scoring-guide-value">Observed repository value (for example, commit count or lines).</span>
                    <span className="sor-scoring-guide-label">Normalized</span>
                    <span className="sor-scoring-guide-value">Raw value scaled to 0-100% for scoring.</span>
                    <span className="sor-scoring-guide-label">Weight</span>
                    <span className="sor-scoring-guide-value">How much that metric influences the score model.</span>
                    <span className="sor-scoring-guide-label">Contribution</span>
                    <span className="sor-scoring-guide-value">Current weighted impact of that metric.</span>
                  </div>
                  <p className="sor-scoring-guide-note">
                    Tip: Focus improvement on metrics with high weight and low normalized values.
                  </p>
                </div>

                {Object.keys(codeMetrics).length === 0 ? (
                  <p className="sor-no-metrics">No overrideable code metrics found for this project.</p>
                ) : (
                  <div className="sor-metrics-list">
                    {Object.entries(codeMetrics).map(([name, metric]) => (
                      <MetricRow
                        key={name}
                        name={name}
                        metric={metric}
                        excluded={excludedMetrics.has(name)}
                        onChange={handleMetricToggle}
                        maxContribution={maxContribution}
                      />
                    ))}
                  </div>
                )}

                {/* Non-code metrics — read only */}
                {Object.keys(breakdown.breakdown?.non_code?.metrics ?? {}).length > 0 && (
                  <div className="sor-non-code-section">
                    <h3 className="sor-non-code-title">Documentation Metrics</h3>
                    <p className="sor-panel-hint">These metrics cannot be excluded</p>
                    {Object.entries(breakdown.breakdown.non_code.metrics).map(([name, metric]) => (
                      <div key={name} className="sor-metric-row sor-metric-readonly">
                        <label className="sor-metric-label">
                          <input type="checkbox" className="sor-checkbox" checked readOnly disabled />
                          <span className="sor-metric-name">{METRIC_LABELS[name] ?? name}</span>
                          <span className="sor-readonly-tag">read-only</span>
                        </label>
                        <div className="sor-metric-stats">
                          <span className="sor-stat">
                            <span className="sor-stat-label">Raw</span>
                            <span className="sor-stat-value">{typeof metric.raw === "number" ? metric.raw.toFixed(3) : metric.raw}</span>
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
                            <span className="sor-stat-value">{pct(metric.contribution)}</span>
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Action buttons */}
                <div className="sor-actions">
                  <button
                    className="sor-btn sor-btn-secondary"
                    onClick={handleReset}
                    disabled={!hasChanges || saving}
                  >
                    Reset
                  </button>
                  <button
                    className="sor-btn sor-btn-danger"
                    onClick={handleClear}
                    disabled={saving || !breakdown.score_overridden}
                  >
                    {saving ? "Clearing…" : "Clear Override"}
                  </button>
                  <button
                    className="sor-btn sor-btn-primary"
                    onClick={handleApply}
                    disabled={saving}
                  >
                    {saving ? "Applying…" : "Apply Override"}
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Preview panel */}
            <div className="sor-right-panel">
              {/* Score display */}
              <div className="sor-panel sor-score-panel">
                <h2 className="sor-panel-title">Score Preview</h2>
                {loadingPreview && <div className="sor-preview-loading">Computing preview…</div>}
                <div className="sor-gauges">
                  <ScoreGauge
                    label="Current Score"
                    value={currentScore}
                    badge={
                      breakdown.score_overridden ? (
                        <span className="sor-override-pill">overridden</span>
                      ) : null
                    }
                  />
                  <div className="sor-gauge-arrow">→</div>
                  <ScoreGauge
                    label="Preview Score"
                    value={previewScore}
                    badge={
                      hasChanges ? (
                        <span
                          className="sor-diff-pill"
                          style={{ color: scoreDiffColor(scoreDiff) }}
                        >
                          {scoreDiff >= 0 ? "+" : ""}
                          {pct(scoreDiff)}
                        </span>
                      ) : null
                    }
                  />
                </div>

                {breakdown.score_overridden && (
                  <div className="sor-original-note">
                    Original (unoverridden) score:{" "}
                    <strong>{pct(breakdown.score_original)}</strong>
                  </div>
                )}

                {excludedMetrics.size > 0 && (
                  <div className="sor-exclusion-tags">
                    <span className="sor-exclusion-label">Excluded:</span>
                    {Array.from(excludedMetrics).map((m) => (
                      <span key={m} className="sor-exclusion-tag">
                        {METRIC_LABELS[m] ?? m}
                        <button
                          className="sor-exclusion-remove"
                          onClick={() => handleMetricToggle(m, false)}
                          title={`Re-include ${m}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="sor-panel sor-opportunities-panel">
                <h2 className="sor-panel-title">Top Improvement Opportunities</h2>
                <p className="sor-panel-hint">
                  Estimated upside if these included metrics move closer to 100% normalized.
                </p>
                {improvementHints.length === 0 ? (
                  <p className="sor-opportunities-empty">
                    No major bottlenecks detected in currently included code metrics.
                  </p>
                ) : (
                  <div className="sor-opportunities-list">
                    {improvementHints.map(({ name, metric, potentialUplift }) => (
                      <div key={name} className="sor-opportunity-item">
                        <div className="sor-opportunity-header">
                          <span className="sor-opportunity-name">{METRIC_LABELS[name] ?? name}</span>
                          <span className="sor-opportunity-uplift">~+{pct(potentialUplift)}</span>
                        </div>
                        <p className="sor-opportunity-meta">
                          normalized {pct(metric.normalized)} · weight {pct(metric.weight)} · contribution{" "}
                          {pct(metric.contribution)}
                        </p>
                        {METRIC_DESCRIPTIONS[name] && (
                          <p className="sor-opportunity-desc">{METRIC_DESCRIPTIONS[name]}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Breakdown visualization */}
              <BreakdownPanel
                breakdown={breakdown.breakdown}
                previewBreakdown={preview?.breakdown ?? null}
                excludedMetrics={excludedMetrics}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
