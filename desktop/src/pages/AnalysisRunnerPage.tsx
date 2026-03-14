import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config/api";
import "../styles/AnalysisRunnerPage.css";

interface Project {
  name: string;
  path: string;
  mode: string;
}

interface RunResult {
  analyzed_projects: number;
  skipped_projects: number;
  failed_projects: number;
}

type SimilarityAction = "create_new" | "update_existing";

export function AnalysisRunnerPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const uploadId: string | undefined = (
    location.state as { uploadId?: string } | null
  )?.uploadId;

  const [projects, setProjects] = useState<Project[]>([]);
  const [defaultMode, setDefaultMode] = useState<"local" | "ai">("local");
  const [similarityAction, setSimilarityAction] =
    useState<SimilarityAction>("create_new");

  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(false);

  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  // Auto-load projects when page mounts with a valid upload_id
  useEffect(() => {
    if (!uploadId) return;

    const fetchProjects = async () => {
      setLoadingProjects(true);
      setLoadError(null);
      try {
        const res = await fetch(
          `${API_BASE_URL}/api/analysis/uploads/${encodeURIComponent(uploadId)}/projects`,
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to load projects");
        const loaded: Project[] = (data.projects || []).map(
          (p: { name: string; path: string }) => ({
            name: p.name,
            path: p.path,
            mode: "local",
          }),
        );
        setProjects(loaded);
      } catch (err) {
        setLoadError(
          err instanceof Error ? err.message : "Failed to load projects",
        );
      } finally {
        setLoadingProjects(false);
      }
    };

    fetchProjects();
  }, [uploadId]);

  // Keep all project modes in sync when default changes
  const handleDefaultModeChange = (mode: "local" | "ai") => {
    setDefaultMode(mode);
    setProjects((prev) => prev.map((p) => ({ ...p, mode })));
  };

  const handleProjectModeChange = (index: number, mode: string) => {
    setProjects((prev) =>
      prev.map((p, i) => (i === index ? { ...p, mode } : p)),
    );
  };

  const handleRunAnalysis = async () => {
    if (!uploadId) return;

    const project_analysis_types: Record<string, string> = {};
    projects.forEach((p) => {
      project_analysis_types[p.name] = p.mode;
    });

    setRunning(true);
    setRunResult(null);
    setRunError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/analysis/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          upload_id: uploadId,
          default_analysis_type: defaultMode,
          project_analysis_types,
          similarity_action: similarityAction,
          cleanup_zip: true,
          cleanup_extracted: true,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setRunResult({
        analyzed_projects: data.analyzed_projects ?? 0,
        skipped_projects: data.skipped_projects ?? 0,
        failed_projects: data.failed_projects ?? 0,
      });
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setRunning(false);
    }
  };

  // Not arrived here via upload — send them back
  if (!uploadId) {
    return (
      <div className="ar-container">
        <div className="ar-card ar-card--empty">
          <p className="ar-empty-msg">
            No upload found. Please upload a project first.
          </p>
          <button className="ar-btn" onClick={() => navigate("/uploadpage")}>
            Go to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ar-container">
      {/* Header */}
      <div className="ar-header">
        <h1 className="ar-title">Configure Analysis</h1>
        <p className="ar-subtitle">
          Review projects and optional settings, then run the analysis.
        </p>
      </div>

      {/* Settings */}
      <div className="ar-card">
        <h2 className="ar-section-title">Settings</h2>
        <div className="ar-settings-row">
          <div className="ar-field">
            <label className="ar-label" htmlFor="defaultMode">
              Default Analysis Type
            </label>
            <select
              id="defaultMode"
              className="ar-select"
              value={defaultMode}
              onChange={(e) =>
                handleDefaultModeChange(e.target.value as "local" | "ai")
              }
            >
              <option value="local">Local (rule-based)</option>
              <option value="ai">AI (language model)</option>
            </select>
          </div>

          <div className="ar-field">
            <label className="ar-label" htmlFor="similarityAction">
              Similarity Action
            </label>
            <select
              id="similarityAction"
              className="ar-select"
              value={similarityAction}
              onChange={(e) =>
                setSimilarityAction(e.target.value as SimilarityAction)
              }
            >
              <option value="create_new">Create new</option>
              <option value="update_existing">Update existing</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects */}
      <div className="ar-card">
        <h2 className="ar-section-title">Projects</h2>

        {loadingProjects && <p className="ar-loading">Loading projects…</p>}
        {loadError && <p className="ar-error">{loadError}</p>}

        {!loadingProjects && !loadError && (
          <table className="ar-table">
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Analysis Type</th>
                <th>Path</th>
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 ? (
                <tr>
                  <td colSpan={3} className="ar-table-empty">
                    No projects found.
                  </td>
                </tr>
              ) : (
                projects.map((project, index) => (
                  <tr key={project.name}>
                    <td className="ar-table-name">{project.name}</td>
                    <td>
                      <select
                        className="ar-select ar-select--inline"
                        value={project.mode}
                        onChange={(e) =>
                          handleProjectModeChange(index, e.target.value)
                        }
                        aria-label={`Analysis type for ${project.name}`}
                      >
                        <option value="local">Local</option>
                        <option value="ai">AI</option>
                      </select>
                    </td>
                    <td className="ar-table-path">{project.path}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Run */}
      <div className="ar-actions">
        <button
          className="ar-btn ar-btn--primary"
          onClick={handleRunAnalysis}
          disabled={running || loadingProjects || projects.length === 0}
        >
          {running ? "Running…" : "Run Analysis"}
        </button>
      </div>

      {/* Result */}
      {runResult && (
        <div className="ar-result ar-result--success">
          <strong>Analysis complete</strong>
          <span className="ar-result-stats">
            <span className="ar-stat ar-stat--ok">
              {runResult.analyzed_projects} analyzed
            </span>
            <span className="ar-stat">
              {runResult.skipped_projects} skipped
            </span>
            {runResult.failed_projects > 0 && (
              <span className="ar-stat ar-stat--warn">
                {runResult.failed_projects} failed
              </span>
            )}
          </span>
        </div>
      )}

      {runError && (
        <div className="ar-result ar-result--error">
          <strong>Error:</strong> {runError}
        </div>
      )}
    </div>
  );
}

export default AnalysisRunnerPage;
