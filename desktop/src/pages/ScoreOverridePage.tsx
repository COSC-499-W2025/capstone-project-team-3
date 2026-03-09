import { useEffect, useMemo, useState } from "react";
import {
  type Project,
  type ScoreBreakdown,
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
  code_files_changed: "Code Files Changed",
  test_files_changed: "Test Files Changed",
  total_files: "Total Files",
};

type BannerType = "success" | "error" | "info";
type Banner = { type: BannerType; text: string } | null;

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

export default function ScoreOverridePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [breakdown, setBreakdown] = useState<ScoreBreakdown | null>(null);
  const [excludedMetrics, setExcludedMetrics] = useState<string[]>([]);
  const [previewScore, setPreviewScore] = useState<number | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [saving, setSaving] = useState(false);
  const [banner, setBanner] = useState<Banner>(null);

  const currentScore = breakdown?.score ?? 0;
  const effectivePreviewScore = previewScore ?? currentScore;
  const scoreDelta = effectivePreviewScore - currentScore;

  const sortedCodeMetrics = useMemo(
    () =>
      Object.entries(breakdown?.breakdown.code.metrics ?? {}).sort(
        (a, b) => b[1].contribution - a[1].contribution
      ),
    [breakdown]
  );

  function setMessage(type: BannerType, text: string): void {
    setBanner({ type, text });
  }

  useEffect(() => {
    getProjects()
      .then(setProjects)
      .catch((error) => setMessage("error", getErrorMessage(error, "Failed to load projects")))
      .finally(() => setLoadingProjects(false));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setBreakdown(null);
      setExcludedMetrics([]);
      setPreviewScore(null);
      return;
    }

    setLoadingBreakdown(true);
    setPreviewScore(null);
    getScoreBreakdown(selectedId)
      .then((data) => {
        setBreakdown(data);
        setExcludedMetrics(data.exclude_metrics ?? []);
      })
      .catch((error) =>
        setMessage("error", getErrorMessage(error, "Failed to load score breakdown"))
      )
      .finally(() => setLoadingBreakdown(false));
  }, [selectedId]);

  async function refreshBreakdown(): Promise<void> {
    if (!selectedId) return;
    const data = await getScoreBreakdown(selectedId);
    setBreakdown(data);
    setExcludedMetrics(data.exclude_metrics ?? []);
  }

  async function updatePreview(nextExcluded: string[]): Promise<void> {
    if (!selectedId) return;
    setLoadingPreview(true);
    try {
      const preview = await previewScoreOverride(selectedId, nextExcluded);
      setPreviewScore(preview.preview_score);
    } catch (error) {
      setMessage("error", getErrorMessage(error, "Failed to compute preview"));
    } finally {
      setLoadingPreview(false);
    }
  }

  function toggleMetric(metricName: string): void {
    const nextExcluded = excludedMetrics.includes(metricName)
      ? excludedMetrics.filter((name) => name !== metricName)
      : [...excludedMetrics, metricName];

    setExcludedMetrics(nextExcluded);
    void updatePreview(nextExcluded);
  }

  async function handleApply(): Promise<void> {
    if (!selectedId) return;
    setSaving(true);
    try {
      await applyScoreOverride(selectedId, excludedMetrics);
      await refreshBreakdown();
      setPreviewScore(null);
      setMessage("success", "Override saved.");
    } catch (error) {
      setMessage("error", getErrorMessage(error, "Failed to apply override"));
    } finally {
      setSaving(false);
    }
  }

  async function handleClear(): Promise<void> {
    if (!selectedId) return;
    setSaving(true);
    try {
      await clearScoreOverride(selectedId);
      await refreshBreakdown();
      setExcludedMetrics([]);
      setPreviewScore(null);
      setMessage("success", "Override cleared.");
    } catch (error) {
      setMessage("error", getErrorMessage(error, "Failed to clear override"));
    } finally {
      setSaving(false);
    }
  }

  function handleReset(): void {
    if (!breakdown) return;
    const original = breakdown.exclude_metrics ?? [];
    setExcludedMetrics(original);
    void updatePreview(original);
  }

  return (
    <div className="score-override-container">
      <h1 className="page-title">Score Override</h1>
      <p className="page-subtitle">
        Exclude selected code metrics from scoring and preview the recalculated score.
      </p>

      {banner && <div className={`score-banner score-banner-${banner.type}`}>{banner.text}</div>}

      <section className="score-panel">
        <label htmlFor="score-project-select" className="score-select-label">
          Project
        </label>
        {loadingProjects ? (
          <p>Loading projects...</p>
        ) : (
          <select
            id="score-project-select"
            className="score-select"
            value={selectedId}
            onChange={(event) => setSelectedId(event.target.value)}
          >
            <option value="">Select a project</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name} ({pct(project.score)})
              </option>
            ))}
          </select>
        )}
      </section>

      {loadingBreakdown && <p className="score-loading">Loading score breakdown...</p>}

      {breakdown && !loadingBreakdown && (
        <div className="score-grid">
          <section className="score-panel">
            <h2>Code Metrics</h2>
            {sortedCodeMetrics.length === 0 && <p>No overrideable metrics for this project.</p>}
            {sortedCodeMetrics.map(([metricName, metric]) => {
              const isExcluded = excludedMetrics.includes(metricName);
              return (
                <label className="score-metric-row" key={metricName}>
                  <input
                    type="checkbox"
                    checked={!isExcluded}
                    onChange={() => toggleMetric(metricName)}
                  />
                  <span className="score-metric-title">
                    {METRIC_LABELS[metricName] ?? metricName}
                  </span>
                  <span className="score-metric-value">
                    raw {metric.raw} | weight {pct(metric.weight)} | contribution{" "}
                    {isExcluded ? "excluded" : pct(metric.contribution)}
                  </span>
                </label>
              );
            })}
          </section>

          <section className="score-panel">
            <h2>Preview</h2>
            <p>Current score: {pct(currentScore)}</p>
            <p>
              Preview score: {pct(effectivePreviewScore)}{" "}
              <span className={scoreDelta >= 0 ? "score-up" : "score-down"}>
                ({scoreDelta >= 0 ? "+" : ""}
                {pct(scoreDelta)})
              </span>
            </p>
            {loadingPreview && <p className="score-loading">Updating preview...</p>}
            <div className="score-actions">
              <button onClick={handleReset} disabled={saving}>
                Reset
              </button>
              <button onClick={handleClear} disabled={saving || !breakdown.score_overridden}>
                Clear Override
              </button>
              <button onClick={handleApply} disabled={saving}>
                {saving ? "Saving..." : "Apply Override"}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
