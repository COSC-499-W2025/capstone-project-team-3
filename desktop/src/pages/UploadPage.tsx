import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { uploadZipFile } from "../api/upload";
import { API_BASE_URL } from "../config/api";
import { SimilarityIndicator } from "../components/SimilarityIndicator";
import "../styles/UploadPage.css";
import "../styles/AnalysisRunnerPage.css";
import "../styles/SimilarityIndicator.css";

interface FileTypeGroup {
  id: string;
  label: string;
  exts: readonly string[];
  namePrefix?: string; // case-insensitive filename stem prefix (e.g. "readme")
}

const FILE_TYPE_GROUPS: FileTypeGroup[] = [
  { id: "markdown", label: "Markdown",       exts: [".md", ".markdown"] },
  { id: "readme",   label: "README files",   exts: [], namePrefix: "readme" },
  { id: "text",     label: "Plain Text",     exts: [".txt"] },
  { id: "pdf",      label: "PDF",            exts: [".pdf"] },
  { id: "word",     label: "Word Docs",      exts: [".docx", ".doc"] },
  { id: "slides",   label: "Presentations",  exts: [".pptx", ".ppt"] },
  { id: "json",     label: "JSON / Config",  exts: [".json", ".toml", ".ini"] },
  { id: "yaml",     label: "YAML",           exts: [".yml", ".yaml"] },
  { id: "html",     label: "HTML",           exts: [".html", ".htm"] },
  { id: "css",      label: "Stylesheets",    exts: [".css", ".scss", ".sass", ".less"] },
  { id: "shell",    label: "Shell Scripts",  exts: [".sh", ".bash"] },
];

interface Project {
  name: string;
  path: string;
  mode: string;
  fileCount?: number;
  similarity?: {
    jaccard_similarity: number;
    containment_ratio: number;
    matched_project_name: string;
    match_reason: string;
  } | null;
  status?: "pending" | "scanning" | "similarity_detected" | "ready" | "analyzing" | "complete";
  userDecision?: "create_new" | "update_existing" | "skip";
}

interface ProjectResult {
  project_name: string;
  status: "analyzed" | "skipped" | "failed";
  reason: string | null;
}

interface RunResult {
  analyzed_projects: number;
  skipped_projects: number;
  failed_projects: number;
  results: ProjectResult[];
}

interface PendingAiSelection {
  type: "default" | "project";
  mode: "local" | "ai";
  projectIndex?: number;
}

interface SimilarityModalData {
  projectName: string;
  projectPath: string;
  projectIndex: number;
  similarity: {
    jaccard_similarity: number;
    containment_ratio: number;
    matched_project_name: string;
    match_reason: string;
  };
  existingDecision?: "create_new" | "update_existing";
}

export function UploadPage() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [projects, setProjects] = useState<Project[]>([]);
  const [defaultMode, setDefaultMode] = useState<"local" | "ai">("local");
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [aiConsentAccepted, setAiConsentAccepted] = useState(false);
  const [showAiConsentModal, setShowAiConsentModal] = useState(false);
  const [pendingAiSelection, setPendingAiSelection] = useState<PendingAiSelection | null>(null);
  const [similarityModalData, setSimilarityModalData] = useState<SimilarityModalData | null>(null);
  const [hasRunAnalysis, setHasRunAnalysis] = useState(false);

  // Per-project file type exclusions
  const [projectExcludeGroups, setProjectExcludeGroups] =
    useState<Record<string, Set<string>>>({});
  const [expandedExclude, setExpandedExclude] =
    useState<Set<string>>(new Set());

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
        setProjects(
          (data.projects || []).map((p: { name: string; path: string }) => ({
            name: p.name,
            path: p.path,
            mode: "local",
            similarity: null,
            status: "pending",
            userDecision: "create_new",
          })),
        );
      } catch (err) {
        setLoadError(err instanceof Error ? err.message : "Failed to load projects");
      } finally {
        setLoadingProjects(false);
      }
    };
    fetchProjects();
  }, [uploadId]);

  const uploadFile = async (file: File) => {
    setUploading(true);
    setUploadError(null);
    setRunResult(null);
    setRunError(null);
    setHasRunAnalysis(false);
    try {
      const result = await uploadZipFile(file);
      setUploadedFileName(file.name);
      setUploadId(result.upload_id);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const ZIP_ERROR = "Please upload a ZIP file. Only .zip files are allowed.";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setUploadError(ZIP_ERROR);
      e.target.value = "";
      return;
    }
    uploadFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (uploading) return;
    const file = e.dataTransfer.files?.[0];
    if (file && file.name.toLowerCase().endsWith(".zip")) {
      setUploadError(null);
      uploadFile(file);
    } else if (file) {
      setUploadError(ZIP_ERROR);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = uploading ? "none" : "copy";
  };

  const handleResetUpload = () => {
    setUploadId(null);
    setUploadedFileName(null);
    setUploadError(null);
    setDefaultMode("local");
    setProjects([]);
    setRunResult(null);
    setRunError(null);
    setLoadError(null);
    setAiConsentAccepted(false);
    setShowAiConsentModal(false);
    setPendingAiSelection(null);
    setSimilarityModalData(null);
    setHasRunAnalysis(false);
    setProjectExcludeGroups({});
    setExpandedExclude(new Set());
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const applyModeChange = (selection: PendingAiSelection) => {
    if (selection.type === "default") {
      setDefaultMode(selection.mode);
      setProjects((prev) => prev.map((project) => ({ ...project, mode: selection.mode })));
      return;
    }

    if (typeof selection.projectIndex === "number") {
      setProjects((prev) =>
        prev.map((project, index) =>
          index === selection.projectIndex ? { ...project, mode: selection.mode } : project,
        ),
      );
    }
  };

  const requestAiConsentFor = (selection: PendingAiSelection) => {
    if (selection.mode === "ai" && !aiConsentAccepted) {
      setPendingAiSelection(selection);
      setShowAiConsentModal(true);
      return;
    }
    applyModeChange(selection);
  };

  const handleDefaultModeChange = (mode: "local" | "ai") => {
    requestAiConsentFor({ type: "default", mode });
  };

  const handleProjectModeChange = (index: number, mode: string) => {
    requestAiConsentFor({
      type: "project",
      mode: mode as "local" | "ai",
      projectIndex: index,
    });
  };

  const handleAcceptAiConsent = () => {
    setAiConsentAccepted(true);
    if (pendingAiSelection) {
      applyModeChange(pendingAiSelection);
    }
    setPendingAiSelection(null);
    setShowAiConsentModal(false);
  };

  const handleCancelAiConsent = () => {
    setPendingAiSelection(null);
    setShowAiConsentModal(false);
  };

  const handleSimilarityDecision = (decision: "create_new" | "update_existing") => {
    if (!similarityModalData) return;

    setProjects((prev) =>
      prev.map((p, idx) =>
        idx === similarityModalData.projectIndex
          ? { ...p, userDecision: decision, status: "ready" }
          : p
      )
    );

    setSimilarityModalData(null);
    processNextProject(similarityModalData.projectIndex + 1);
  };

  const processNextProject = async (startIndex: number) => {
    for (let i = startIndex; i < projects.length; i++) {
      const project = projects[i];
      
      if (project.status !== "pending") continue;

      setProjects((prev) =>
        prev.map((p, idx) => (idx === i ? { ...p, status: "scanning" } : p))
      );

      try {
        const res = await fetch(
          `${API_BASE_URL}/api/analysis/uploads/${encodeURIComponent(uploadId!)}/scan-project`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_path: project.path }),
          }
        );
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Scan failed");

        // Handle exact match (100%) - auto-skip
        if (data.exact_match) {
          setProjects((prev) =>
            prev.map((p, idx) =>
              idx === i
                ? { 
                    ...p, 
                    similarity: data.similarity, 
                    fileCount: data.file_count,
                    status: "ready",
                    userDecision: "skip"
                  }
                : p
            )
          );
          // Continue to next project without showing modal
          continue;
        }

        // Handle similarity detected (show modal)
        if (data.similarity) {
          setProjects((prev) =>
            prev.map((p, idx) =>
              idx === i
                ? { ...p, similarity: data.similarity, fileCount: data.file_count, status: "similarity_detected" }
                : p
            )
          );

          setSimilarityModalData({
            projectName: project.name,
            projectPath: project.path,
            projectIndex: i,
            similarity: data.similarity,
          });
          return;
        } else {
          // No similarity - proceed
          setProjects((prev) =>
            prev.map((p, idx) =>
              idx === i ? { ...p, fileCount: data.file_count, status: "ready", userDecision: "create_new" } : p
            )
          );
        }
      } catch (err) {
        console.error(`Scan failed for ${project.name}:`, err);
        setProjects((prev) =>
          prev.map((p, idx) =>
            idx === i ? { ...p, status: "ready", userDecision: "create_new" } : p
          )
        );
      }
    }

    runActualAnalysis();
  };

  const runActualAnalysis = async () => {
  const toggleExcludeGroup = (projectPath: string, groupId: string) => {
    setProjectExcludeGroups((prev) => {
      const current = new Set(prev[projectPath] ?? []);
      current.has(groupId) ? current.delete(groupId) : current.add(groupId);
      return { ...prev, [projectPath]: current };
    });
  };

  const toggleExpandExclude = (projectPath: string) => {
    setExpandedExclude((prev) => {
      const next = new Set(prev);
      next.has(projectPath) ? next.delete(projectPath) : next.add(projectPath);
      return next;
    });
  };

  const handleRunAnalysis = async () => {
    if (!uploadId) return;

    const project_analysis_types: Record<string, string> = {};
    const project_similarity_actions: Record<string, string> = {};

    projects.forEach((p) => {
      // Only include projects that should be analyzed (not skipped)
      if (p.userDecision !== "skip") {
        project_analysis_types[p.path] = p.mode;
        project_similarity_actions[p.path] = p.userDecision || "create_new";
      }
    });

    const project_exclude_extensions: Record<string, string[]> = {};
    const project_exclude_name_prefixes: Record<string, string[]> = {};
    projects.forEach((p) => {
      const groups = projectExcludeGroups[p.path];
      if (groups?.size) {
        const matched = FILE_TYPE_GROUPS.filter((g) => groups.has(g.id));
        const exts = matched.flatMap((g) => [...g.exts]);
        const prefixes = matched.filter((g) => g.namePrefix).map((g) => g.namePrefix!);
        if (exts.length) project_exclude_extensions[p.path] = exts;
        if (prefixes.length) project_exclude_name_prefixes[p.path] = prefixes;
      }
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
          project_similarity_actions: projectSimilarityActions,
          project_exclude_extensions,
          project_exclude_name_prefixes,
          cleanup_zip: true,
          cleanup_extracted: true,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      
      const skippedCount = projects.filter(p => p.userDecision === "skip").length;
      
      setRunResult({
        analyzed_projects: data.analyzed_projects ?? 0,
        skipped_projects: (data.skipped_projects ?? 0) + skippedCount,
        failed_projects: data.failed_projects ?? 0,
        results: data.results ?? [],
      });
      // Keep the projects table visible with all similarity info
      setRunning(false);
      setUploadId(null);
      setUploadedFileName(null);
      setProjects([]);
      setProjectSimilarityActions({});
      setDefaultMode("local");
      setSimilarityAction("create_new");
      setLoadError(null);
      setAiConsentAccepted(false);
      setShowAiConsentModal(false);
      setPendingAiSelection(null);
      setProjectExcludeGroups({});
      setExpandedExclude(new Set());
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Analysis failed");
      setRunning(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!uploadId) return;

    setRunning(true);
    setRunResult(null);
    setRunError(null);
    setHasRunAnalysis(true);

    setProjects((prev) =>
      prev.map((p) => ({ ...p, status: "pending" as const, similarity: null }))
    );

    processNextProject(0);
  };

  const hasUpload = !!uploadId;
  const analysisDisabled = !hasUpload || loadingProjects || running || hasRunAnalysis;
  const isAiSelected =
    defaultMode === "ai" || projects.some((project) => project.mode === "ai");

  return (
    <div className="upload-page">
      <div className="upload-page-nav" aria-label="Page navigation">
        <div className="page-home-nav">
          <button
            type="button"
            className="page-home-link"
            onClick={() => navigate("/hubpage")}
          >
            Home
          </button>
          <span className="page-home-separator">›</span>
          <span className="page-home-current">Upload</span>
        </div>
      </div>

      <div className="upload-shell">
        <header className="upload-header">
          <h1 className="upload-title">Upload & Run Analysis</h1>
          <p className="upload-subtitle">
            {runResult 
              ? "Analysis complete! Review the results below or upload another ZIP."
              : "Upload a ZIP, configure analysis settings, and run. Similarity detection happens automatically during analysis."}
          </p>
        </header>

        <section className="upload-card" aria-label="Upload zip section">
          <div className="upload-card-main">
            <p className="upload-card-label">Project ZIP</p>
            <p className="upload-card-value">
              {uploadedFileName ? uploadedFileName : "No file selected"}
            </p>

            <div className="upload-card-actions">
              <button
                type="button"
                className="upload-select-btn"
                onClick={() => !uploading && fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? "Uploading…" : hasUpload ? "Upload another ZIP" : "Choose ZIP file"}
              </button>
              {hasUpload && (
                <button
                  type="button"
                  className="upload-clear-btn"
                  onClick={handleResetUpload}
                  disabled={uploading || running}
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          <div
            className={`upload-dropzone${uploading ? " upload-dropzone--loading" : ""}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => !uploading && fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) =>
              e.key === "Enter" && !uploading && fileInputRef.current?.click()
            }
            aria-label="Drop or click to select ZIP file"
          >
            <div className="upload-icon" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p className="upload-hint">
              {uploading ? "Uploading ZIP…" : "Drag and drop ZIP here"}
            </p>
            <p className="upload-dropzone-subhint">or click to browse</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={handleFileChange}
            className="upload-file-input"
            aria-label="Select ZIP file"
            disabled={uploading}
          />
        </section>

        {uploadError && (
          <div className="upload-error" role="alert">
            {uploadError}
          </div>
        )}

        <div className="ar-container upload-analysis-container">
          <div className="ar-card">
            <h2 className="ar-section-title">Settings</h2>
            <div className="ar-field">
              <label className="ar-label" htmlFor="defaultMode">Default Analysis Type</label>
              <select
                id="defaultMode"
                className="ar-select"
                value={defaultMode}
                onChange={(e) => handleDefaultModeChange(e.target.value as "local" | "ai")}
                disabled={analysisDisabled}
              >
                <option value="local">Local (rule-based)</option>
                <option value="ai">AI (language model)</option>
              </select>
              <p className="ar-field-hint">
                Choose the default analysis method. You can override this per project below.
              </p>
            </div>

            {isAiSelected && (
              <div className="upload-ai-disclaimer" role="note" aria-live="polite">
                AI mode notice: When analysis type is set to AI, selected project content may
                be sent to our configured LLM provider to generate insights. Avoid uploading
                sensitive, personal, or confidential data unless you have permission to share it.
              </div>
            )}

            {aiConsentAccepted && (
              <p className="upload-ai-consent-status">AI consent accepted for this upload session.</p>
            )}
          </div>

          <div className="ar-card">
            <h2 className="ar-section-title">Projects</h2>

            {!hasUpload && (
              <p className="upload-info-msg">Upload a ZIP to load projects for configuration.</p>
            )}
            {hasUpload && loadingProjects && <p className="ar-loading">Loading projects…</p>}
            {hasUpload && loadError && <p className="ar-error">{loadError}</p>}

            {hasUpload && !loadingProjects && !loadError && (
              <table className="ar-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Project Name</th>
                    <th>Files</th>
                    <th>Similarity Score</th>
                    <th>Matched Project</th>
                    <th>Analysis Type</th>
                    <th>Decision</th>
                    <th>Similarity Action</th>
                    <th>Exclude Types</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="ar-table-empty">No projects found.</td>
                    </tr>
                  ) : (
                    projects.map((project, index) => (
                      <tr 
                        key={project.name} 
                        className={project.status === "similarity_detected" ? "ar-table-row--similarity" : ""}
                      >
                        <td style={{ textAlign: "center" }}>
                          {project.status === "pending" && (
                            <span className="project-status project-status--pending" title="Pending analysis">⏳</span>
                          )}
                          {project.status === "scanning" && (
                            <span className="project-status project-status--scanning analyzing-spinner" title="Scanning for similarity">⟳</span>
                          )}
                          {(project.status === "similarity_detected" || project.status === "ready") && project.similarity && (
                            <button
                              type="button"
                              className="similarity-indicator-btn"
                              onClick={() => {
                                if (project.similarity && !hasRunAnalysis) {
                                  setSimilarityModalData({
                                    projectName: project.name,
                                    projectPath: project.path,
                                    projectIndex: index,
                                    similarity: project.similarity,
                                    existingDecision: project.userDecision as "create_new" | "update_existing" | undefined,
                                  });
                                }
                              }}
                              title={hasRunAnalysis ? "Analysis complete - cannot change decision" : `Click to view/change decision for: ${project.similarity.matched_project_name}`}
                              disabled={hasRunAnalysis}
                            >
                              <SimilarityIndicator
                                similarity={project.similarity}
                                projectName={project.name}
                              />
                            </button>
                          )}
                          {project.status === "ready" && !project.similarity && (
                            <SimilarityIndicator similarity={null} projectName={project.name} />
                          )}
                        </td>
                        <td className="ar-table-name">{project.name}</td>
                        <td className="ar-table-files" style={{ textAlign: "center" }}>
                          {project.status === "scanning" ? "..." : (project.fileCount ?? "—")}
                        </td>
                        <td className="ar-table-similarity" style={{ textAlign: "center" }}>
                          {project.similarity ? (
                            <span className={project.similarity.jaccard_similarity >= 70 ? "similarity-high" : project.similarity.jaccard_similarity >= 30 ? "similarity-medium" : "similarity-low"}>
                              {project.similarity.jaccard_similarity.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="similarity-none">—</span>
                          )}
                        </td>
                        <td className="ar-table-matched">
                          {project.similarity ? (
                            <span className="matched-project-name">{project.similarity.matched_project_name}</span>
                          ) : (
                            <span className="similarity-none">—</span>
                          )}
                        </td>
                        <td>
                          <select
                            className="ar-select ar-select--inline"
                            value={project.mode}
                            onChange={(e) => handleProjectModeChange(index, e.target.value)}
                            aria-label={`Analysis type for ${project.name}`}
                            disabled={analysisDisabled || running}
                          >
                            <option value="local">Local</option>
                            <option value="ai">AI</option>
                          </select>
                        </td>
                        <td>
                          {project.userDecision === "skip" ? (
                            <span className="ar-table-decision ar-table-decision--skip">⏭️ Skip (100% match)</span>
                          ) : project.status === "similarity_detected" && !hasRunAnalysis ? (
                            <span className="ar-table-decision ar-table-decision--pending" onClick={() => {
                              if (project.similarity) {
                                setSimilarityModalData({
                                  projectName: project.name,
                                  projectPath: project.path,
                                  projectIndex: index,
                                  similarity: project.similarity,
                                  existingDecision: project.userDecision as "create_new" | "update_existing" | undefined,
                                });
                              }
                            }} style={{ cursor: "pointer", color: "#f59e0b", fontWeight: 600 }}>
                              ⚠️ Similar to "{project.similarity?.matched_project_name}" - Click to decide
                            </span>
                          ) : project.userDecision === "update_existing" && project.similarity ? (
                            <span className="ar-table-decision ar-table-decision--update">↻ Update "{project.similarity.matched_project_name}"</span>
                          ) : project.userDecision === "create_new" ? (
                            <span className="ar-table-decision">+ New project</span>
                          ) : null}
                        </td>
                      </tr>
                    ))
                      <td colSpan={4} className="ar-table-empty">No projects found.</td>
                    </tr>
                  ) : (
                    projects.map((project, index) => {
                      const excluded = projectExcludeGroups[project.path];
                      const excludeCount = excluded?.size ?? 0;
                      const isExpanded = expandedExclude.has(project.path);
                      return (
                        <>
                          <tr key={project.name}>
                            <td className="ar-table-name">{project.name}</td>
                            <td>
                              <select
                                className="ar-select ar-select--inline"
                                value={project.mode}
                                onChange={(e) => handleProjectModeChange(index, e.target.value)}
                                aria-label={`Analysis type for ${project.name}`}
                                disabled={analysisDisabled}
                              >
                                <option value="local">Local</option>
                                <option value="ai">AI</option>
                              </select>
                            </td>
                            <td>
                              <select
                                className="ar-select ar-select--inline"
                                value={projectSimilarityActions[project.path] ?? similarityAction}
                                onChange={(e) =>
                                  handleProjectSimilarityActionChange(
                                    project.path,
                                    e.target.value as SimilarityAction,
                                  )
                                }
                                aria-label={`Similarity action for ${project.name}`}
                                disabled={analysisDisabled}
                              >
                                <option value="create_new">Create new</option>
                                <option value="update_existing">Update existing</option>
                              </select>
                            </td>
                            <td>
                              <button
                                type="button"
                                className={`ar-exclude-btn${isExpanded ? " ar-exclude-btn--open" : ""}`}
                                onClick={() => toggleExpandExclude(project.path)}
                                disabled={analysisDisabled}
                                aria-expanded={isExpanded}
                                aria-label={`Exclude file types for ${project.name}`}
                              >
                                {excludeCount > 0
                                  ? <span className="ar-exclude-badge">{excludeCount} type{excludeCount !== 1 ? "s" : ""}</span>
                                  : "None"
                                }
                                <span className="ar-exclude-chevron">{isExpanded ? "▴" : "▾"}</span>
                              </button>
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr key={`${project.name}-exclude`} className="ar-exclude-row">
                              <td colSpan={4} className="ar-exclude-cell">
                                <div className="ar-exclude-panel">
                                  <p className="ar-exclude-hint">
                                    Check types to <strong>exclude</strong> from analysis for this project.
                                  </p>
                                  <div className="ar-exclude-grid">
                                    {FILE_TYPE_GROUPS.map((group) => {
                                      const checked = excluded?.has(group.id) ?? false;
                                      return (
                                        <label key={group.id} className={`ar-exclude-group${checked ? " ar-exclude-group--checked" : ""}`}>
                                          <input
                                            type="checkbox"
                                            checked={checked}
                                            onChange={() => toggleExcludeGroup(project.path, group.id)}
                                            disabled={analysisDisabled}
                                          />
                                          <span className="ar-exclude-label">{group.label}</span>
                                          <span className="ar-exclude-exts">{group.exts.join(", ")}</span>
                                        </label>
                                      );
                                    })}
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      );
                    })
                  )}
                </tbody>
              </table>
            )}
          </div>

          <div className="ar-actions">
            <button
              className={`ar-btn ar-btn--primary ${hasRunAnalysis ? "ar-btn--disabled" : ""}`}
              onClick={handleRunAnalysis}
              disabled={analysisDisabled || projects.length === 0}
              title={hasRunAnalysis ? "Analysis already run. Upload another ZIP or clear to run again." : ""}
            >
              {running ? "Running…" : hasRunAnalysis ? "Analysis Complete" : "Run Analysis"}
            </button>
          </div>

          {runResult && (
            <div className="ar-result ar-result--success">
              <div className="ar-result-main">
                <strong>Analysis complete!</strong>
                <span className="ar-result-stats">
                  <span className="ar-stat ar-stat--ok">
                    {runResult.analyzed_projects} analyzed
                  </span>
                  <span className="ar-stat">{runResult.skipped_projects} skipped</span>
                  {runResult.failed_projects > 0 && (
                    <span className="ar-stat ar-stat--warn">
                      {runResult.failed_projects} failed
                    </span>
                  )}
                </span>
              </div>
              {runResult.results.filter((r) => r.reason === "all_files_excluded").length > 0 && (
                <p className="ar-result-excluded-note">
                  <strong>
                    {runResult.results
                      .filter((r) => r.reason === "all_files_excluded")
                      .map((r) => r.project_name)
                      .join(", ")}
                  </strong>{" "}
                  {runResult.results.filter((r) => r.reason === "all_files_excluded").length === 1
                    ? "was skipped"
                    : "were skipped"}{" "}
                  — all files were excluded by your filters.
                </p>
              )}
              <button
                type="button"
                className="ar-btn ar-btn--primary ar-result-insights-btn"
                onClick={() => navigate("/hubpage")}
              >
                View Insights
              </button>
            </div>
          )}

          {runError && (
            <div className="ar-result ar-result--error">
              <strong>Error:</strong> {runError}
            </div>
          )}
        </div>

        {showAiConsentModal && (
          <div className="upload-consent-overlay" role="dialog" aria-modal="true" aria-label="AI consent required">
            <div className="upload-consent-modal">
              <h3 className="upload-consent-title">AI consent required</h3>
              <p className="upload-consent-text">
                To use AI analysis, project content may be sent to our configured LLM provider.
                Please confirm you have permission to share this data.
              </p>
              <div className="upload-consent-actions">
                <button type="button" className="upload-clear-btn" onClick={handleCancelAiConsent}>
                  Cancel
                </button>
                <button type="button" className="upload-select-btn" onClick={handleAcceptAiConsent}>
                  I understand, continue with AI
                </button>
              </div>
            </div>
          </div>
        )}

        {similarityModalData && (
          <div className="upload-consent-overlay" role="dialog" aria-modal="true" aria-label="Similarity detected">
            <div className="upload-consent-modal upload-similarity-modal">
              <h3 className="upload-consent-title">⚠️ Similar Project Detected</h3>
              <p className="upload-similarity-project-name">
                <strong>{similarityModalData.projectName}</strong> is similar to an existing project:
              </p>
              <div className="upload-similarity-match">
                <strong>"{similarityModalData.similarity.matched_project_name}"</strong>
              </div>
              <div className="upload-similarity-metrics">
                <div className="upload-similarity-metric">
                  <span className="upload-similarity-metric-label">Jaccard Similarity:</span>
                  <span className="upload-similarity-metric-value">
                    {similarityModalData.similarity.jaccard_similarity.toFixed(1)}%
                  </span>
                </div>
                <div className="upload-similarity-metric">
                  <span className="upload-similarity-metric-label">Containment Ratio:</span>
                  <span className="upload-similarity-metric-value">
                    {similarityModalData.similarity.containment_ratio.toFixed(1)}%
                  </span>
                </div>
                <div className="upload-similarity-metric">
                  <span className="upload-similarity-metric-label">Match Reason:</span>
                  <span className="upload-similarity-metric-value">
                    {similarityModalData.similarity.match_reason}
                  </span>
                </div>
              </div>
              {similarityModalData.existingDecision ? (
                <>
                  <p className="upload-similarity-current-decision">
                    Current decision: <strong>{similarityModalData.existingDecision === "create_new" ? "Create New Project" : `Update "${similarityModalData.similarity.matched_project_name}"`}</strong>
                  </p>
                  <p className="upload-similarity-question">Change to a different option?</p>
                </>
              ) : (
                <p className="upload-similarity-question">What would you like to do?</p>
              )}
              <div className="upload-consent-actions">
                <button
                  type="button"
                  className={`upload-clear-btn ${similarityModalData.existingDecision === "create_new" ? "btn--selected" : ""}`}
                  onClick={() => handleSimilarityDecision("create_new")}
                >
                  Create New Project
                </button>
                <button
                  type="button"
                  className={`upload-select-btn ${similarityModalData.existingDecision === "update_existing" ? "btn--selected" : ""}`}
                  onClick={() => handleSimilarityDecision("update_existing")}
                >
                  Update "{similarityModalData.similarity.matched_project_name}"
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadPage;
