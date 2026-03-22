import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
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
import BreakdownPanel from "../scoreOverrideManager/BreakdownPanel";
import { pct } from "../scoreOverrideManager/formatters";
import MetricRow from "../scoreOverrideManager/MetricRow";
import { METRIC_DESCRIPTIONS, METRIC_LABELS } from "../scoreOverrideManager/metadata";
import ScoreGauge from "../scoreOverrideManager/ScoreGauge";
import "../styles/ScoreOverridePage.css";

function scoreDiffColor(diff: number): string {
  if (diff > 0) return "#27ae60";
  if (diff < 0) return "#e74c3c";
  return "#718096";
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
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedProjectId = searchParams.get("project") ?? "";
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

      // At least one code metric must remain
      const totalCodeMetrics = Object.keys(codeMetrics).length;
      if (next.size >= totalCodeMetrics) {
        showStatus("error", "At least one code metric must remain included.");
        return prev;
      }

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

  const remainingMetrics = Object.entries(codeMetrics).filter(
    ([name]) => !excludedMetrics.has(name)
  );
  const allRemainingAtMax =
    hasChanges &&
    Math.abs(scoreDiff) < 0.0001 &&
    remainingMetrics.length > 0 &&
    remainingMetrics.every(([, m]) => m.normalized >= 1.0);

  // Show info message when excluding a metric doesn't change the score
  useEffect(() => {
    if (preview && allRemainingAtMax) {
      showStatus(
        "info",
        "The score hasn't changed because all remaining metrics are already at their maximum (100% normalized)."
      );
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preview]);

  return (
    <div className="page-container flex-column sor-page">
      <button
        className="settings-back-btn"
        onClick={() => navigate(-1)}
        aria-label="Go back"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Back
      </button>

      <div className="sor-header-section">
        <h1 className="sor-title">Score Override</h1>
        <p className="sor-subtitle">
          Adjust which metrics contribute to a project's score. Excluded metrics are removed
          and the remaining weights are renormalized automatically.
        </p>
        {status && (
          <div className={`sor-status sor-status-${status.type}`}>{status.text}</div>
        )}
      </div>

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

        {selectedId && !loadingBreakdown && !breakdown && (
          <div className="sor-info-banner" style={{ marginTop: "var(--spacing-md)" }}>
            <div className="sor-info-banner-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
            </div>
            <div>
              <p className="sor-info-banner-title">Unable to load score breakdown</p>
              <p className="sor-info-banner-text">
                The score breakdown for this project could not be loaded. Try selecting the
                project again or check if it has been analyzed.
              </p>
            </div>
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
                    Uncheck a metric to exclude it from the score calculation.
                    Only code metrics can be excluded — at least one must remain included.
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
                  <div className="sor-info-banner">
                    <div className="sor-info-banner-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="16" x2="12" y2="12" />
                        <line x1="12" y1="8" x2="12.01" y2="8" />
                      </svg>
                    </div>
                    <div>
                      <p className="sor-info-banner-title">No code metrics available</p>
                      <p className="sor-info-banner-text">
                        This project does not have overrideable code metrics. It may need to be
                        re-analyzed, or it may be a documentation-only project.
                      </p>
                    </div>
                  </div>
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
                    <p className="sor-panel-hint">
                      Shown for reference only — documentation metrics cannot be excluded from the score.
                    </p>
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

                {allRemainingAtMax && (
                  <p className="sor-saturation-note">
                    All remaining metrics are at 100% — excluding a metric won't change the score.
                  </p>
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
