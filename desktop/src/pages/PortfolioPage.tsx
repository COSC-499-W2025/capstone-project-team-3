import React, { useEffect, useMemo, useRef, useState } from "react";
import { API_BASE_URL } from "../config/api";
import "../styles/PortfolioPage.css";
import Chart from "chart.js/auto";

interface Project {
  id: string | number;
  name?: string;
  title?: string;
  score?: number;
  rank?: number;
  score_overridden?: boolean;
  score_overridden_value?: number;
  dates?: string;
  start_date?: string;
  end_date?: string;
  type?: string;
  summary?: string;
  thumbnail_url?: string;
  skills?: string[];
  technical_keywords?: string[];
  metrics?: {
    total_lines?: number;
    total_commits?: number;
    test_files_changed?: number;
    functions?: number;
    classes?: number;
    components?: number;
    completeness_score?: number;
    word_count?: number;
    development_patterns?: { project_evolution?: string[] };
    technical_keywords?: string[];
    complexity_analysis?: {
      maintainability_score?: { overall_score?: number };
    };
    commit_patterns?: { commit_frequency?: { development_intensity?: string } };
    contribution_activity?: { doc_type_counts?: Record<string, number> };
  };
}

interface PortfolioData {
  overview?: {
    total_projects?: number;
    avg_score?: number;
    total_skills?: number;
    total_languages?: number;
    total_lines?: number;
  };
  graphs?: {
    language_distribution?: Record<string, number>;
    complexity_distribution?: { distribution?: Record<string, number> };
    score_distribution?: { distribution?: Record<string, number> };
    monthly_activity?: Record<string, number>;
    top_skills?: Record<string, number>;
  };
  project_type_analysis?: {
    github?: { count?: number };
    local?: { count?: number };
  };
  projects?: Project[];
}

const getDisplayScore = (project: Project): number => {
  if (project.score_overridden && project.score_overridden_value != null)
    return Number(project.score_overridden_value) || 0;
  if (project.score != null) return Number(project.score) || 0;
  return Number(project.rank) || 0;
};

const projectName = (p: Project): string =>
  p.name || p.title || `Project ${p.id}`;

const sidebarProjectName = (p: Project): string => p.name || "";

const projectDates = (p: Project): string => {
  if (p.dates) return p.dates;
  const start = p.start_date ? new Date(p.start_date).toLocaleDateString() : "";
  const end = p.end_date ? new Date(p.end_date).toLocaleDateString() : "";
  return `${start}${start && end ? " - " : ""}${end}`;
};

const shouldTruncateSummary = (summary: string): boolean => {
  const wordCount = summary.split(/\s+/).filter(Boolean).length;
  const charCount = summary.length;
  return wordCount > 25 || charCount > 150;
};

function PieChart({ data }: { data?: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const labels = Object.keys(data || {});
  const values = Object.values(data || {}).map((v) => Number(v) || 0);

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    chartRef.current = new Chart(ctx, {
      type: "pie",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: [
              "#2d3748",
              "#4a5568",
              "#718096",
              "#a0aec0",
              "#48bb78",
              "#ed8936",
              "#667eea",
              "#764ba2",
              "#f687b3",
              "#9f7aea",
              "#38b2ac",
              "#68d391",
            ],
            borderColor: "#ffffff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "#4a5568",
              font: { size: 12 },
              padding: 15,
              usePointStyle: true,
            },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(data || {})]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} />;
}

function BarChart({ data }: { data?: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const labels = Object.keys(data || {});
  const values = Object.values(data || {}).map((v) => Number(v) || 0);

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: "#2d3748",
            borderColor: "#4a5568",
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 } },
          },
          x: {
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 } },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(data || {})]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} />;
}

function HorizontalBarChart({ data }: { data?: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const ordered = Object.entries(data || {}).slice(0, 8);
  const labels = ordered.map(([k]) => k);
  const values = ordered.map(([, v]) => Number(v) || 0);

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: "#4a5568",
            borderColor: "#2d3748",
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 } },
          },
          y: {
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 } },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(data || {})]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} />;
}

function LineChart({ data }: { data?: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const sortedData = Object.entries(data || {}).sort((a, b) =>
    a[0].localeCompare(b[0]),
  );
  const labels = sortedData.map(([month]) => month);
  const values = sortedData.map(([, value]) => Number(value) || 0);

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    chartRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Activity",
            data: values,
            borderColor: "#2d3748",
            backgroundColor: "rgba(45, 55, 72, 0.1)",
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointBackgroundColor: "#2d3748",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            pointRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 }, stepSize: 0.5 },
            title: {
              display: true,
              text: "Activity Level",
              color: "#4a5568",
              font: { size: 12, weight: "bold" },
            },
          },
          x: {
            grid: { color: "#e2e8f0" },
            ticks: { color: "#4a5568", font: { size: 11 } },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(data || {})]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} />;
}

function ProjectCard({
  project,
  rank,
  onReload,
}: {
  project: Project;
  rank: number;
  onReload: () => Promise<void>;
}) {
  const [showFullSummary, setShowFullSummary] = useState(false);
  const summary = project.summary || "";
  const title = projectName(project);
  const dates = projectDates(project);
  const score = getDisplayScore(project).toFixed(2);

  const skills = project.skills || project.technical_keywords || [];
  const metrics = project.metrics || {};
  const rankLabel =
    ["🥇", "🥈", "🥉", "4th", "5th", "6th"][rank - 1] || `${rank}th`;
  const maintainabilityScore = metrics.complexity_analysis
    ?.maintainability_score
    ? `${metrics.complexity_analysis.maintainability_score.overall_score || 0}/100`
    : "N/A";
  const developmentIntensity =
    metrics.commit_patterns?.commit_frequency?.development_intensity || "N/A";
  const docTypes = metrics.contribution_activity?.doc_type_counts || {};
  const isGithubProject =
    (project.type || "").toLowerCase() === "github" ||
    (metrics.total_commits || 0) > 0;
  const docTypesDisplay =
    Object.entries(docTypes)
      .map(([type, count]) => `${type}: ${count}`)
      .join(", ") || "N/A";

  const uploadThumbnail = async () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = async (e: Event) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file.");
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert(
          "Image file is too large. Please select an image smaller than 5MB.",
        );
        return;
      }
      const form = new FormData();
      form.append("project_id", String(project.id));
      form.append("image", file);
      const res = await fetch(
        `${API_BASE_URL}/api/portfolio/project/thumbnail`,
        {
          method: "POST",
          body: form,
          headers: {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            Pragma: "no-cache",
          },
        },
      );
      if (!res.ok) {
        alert("Failed to upload thumbnail");
        return;
      }
      await onReload();
      alert("Thumbnail uploaded successfully!");
    };
    input.click();
  };

  const notifyEditableField = () => {
    alert("This will be implemented.");
  };

  return (
    <div className="project-card" style={{ position: "relative" }}>
      <div
        className="thumbnail-button-section"
        style={{ position: "absolute", top: 16, right: 16, zIndex: 10 }}
      >
        <button className="upload-thumbnail-btn" onClick={uploadThumbnail}>
          {project.thumbnail_url ? "Change Thumbnail" : "Add Thumbnail"}
        </button>
      </div>
      <div className="project-rank">{rankLabel} Place</div>
      <div
        className="project-title editable-field"
        style={{ paddingRight: 140 }}
        onClick={notifyEditableField}
      >
        {title}
      </div>
      <div
        className="project-score-display editable-field"
        onClick={notifyEditableField}
      >
        <>
          {Number(score).toFixed(2)}
          {project.score_overridden ? (
            <span style={{ color: "var(--warning)", fontSize: "0.8em" }}>
              {" "}
              (Override)
            </span>
          ) : null}
        </>
      </div>
      <div
        className="project-dates editable-field"
        onClick={notifyEditableField}
      >
        {dates}
      </div>
      {project.thumbnail_url && (
        <div
          className="thumbnail-display"
          style={{ margin: "16px 0", textAlign: "center" }}
        >
          <img
            src={`${project.thumbnail_url}?cb=${Date.now()}`}
            alt="Project thumbnail"
            className="project-thumbnail"
          />
        </div>
      )}
      <div className="project-summary">
        <h4>📝 Project Summary</h4>
        <div className="summary-content">
          <p
            className={`summary-text ${!showFullSummary && shouldTruncateSummary(summary) ? "truncated" : ""} editable-field`}
            onClick={notifyEditableField}
          >
            {summary}
          </p>
          {shouldTruncateSummary(summary) && (
            <button
              className="show-more-btn"
              onClick={() => setShowFullSummary((v) => !v)}
            >
              {showFullSummary ? "Show Less" : "Show More"}
            </button>
          )}
        </div>
      </div>
      <div className="project-metrics">
        <div className="metric-item">
          <span className="metric-label">Lines of Code:</span>
          <span className="metric-value">
            {(metrics.total_lines || 0).toLocaleString()}
          </span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Commits:</span>
          <span className="metric-value">{metrics.total_commits || "N/A"}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Type:</span>
          <span className="metric-value">{project.type || "Unknown"}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Test Files:</span>
          <span className="metric-value">
            {metrics.test_files_changed || 0}
          </span>
        </div>
        {!isGithubProject ? (
          <>
            <div className="metric-item">
              <span className="metric-label">Functions:</span>
              <span className="metric-value">{metrics.functions || 0}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Classes:</span>
              <span className="metric-value">{metrics.classes || 0}</span>
            </div>
          </>
        ) : null}
        <div className="metric-item">
          <span className="metric-label">Maintainability:</span>
          <span className="metric-value">{maintainabilityScore}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Dev Intensity:</span>
          <span className="metric-value">{developmentIntensity}</span>
        </div>
        {metrics.completeness_score ? (
          <div className="metric-item">
            <span className="metric-label">Completeness:</span>
            <span className="metric-value">{metrics.completeness_score}%</span>
          </div>
        ) : null}
        {metrics.completeness_score ? (
          <div className="metric-item">
            <span className="metric-label">Word Count:</span>
            <span className="metric-value">
              {(metrics.word_count || 0).toLocaleString()}
            </span>
          </div>
        ) : null}
      </div>
      {docTypesDisplay !== "N/A" ? (
        <div className="contribution-details">
          <h4>📊 Document Types</h4>
          <p>{docTypesDisplay}</p>
        </div>
      ) : null}
      <div className="project-skills-display">
        {skills.slice(0, 8).map((s) => (
          <span key={s} className="project-skill-tag">
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

const PortfolioPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<
    Set<string | number>
  >(new Set());
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);

  const loadPortfolio = async (selectedIds?: Array<string | number>) => {
    const query =
      selectedIds &&
      selectedIds.length > 0 &&
      selectedIds.length < allProjects.length
        ? `?project_ids=${selectedIds.join(",")}`
        : "";
    const res = await fetch(`${API_BASE_URL}/api/portfolio${query}`);
    if (!res.ok)
      throw new Error(`Failed to fetch portfolio: ${res.statusText}`);
    setPortfolio((await res.json()) as PortfolioData);
  };

  const loadAll = async () => {
    try {
      setLoading(true);
      setError(null);
      const projectsRes = await fetch(`${API_BASE_URL}/api/projects`);
      if (!projectsRes.ok)
        throw new Error(`Failed to fetch projects: ${projectsRes.statusText}`);
      const projects = (await projectsRes.json()) as Project[];
      setAllProjects(projects);
      setSelectedProjects(new Set(projects.map((p) => p.id)));
      const portRes = await fetch(`${API_BASE_URL}/api/portfolio`);
      if (!portRes.ok)
        throw new Error(`Failed to fetch portfolio: ${portRes.statusText}`);
      setPortfolio((await portRes.json()) as PortfolioData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAll();
  }, []);

  const toggleProject = async (id: string | number) => {
    const next = new Set(selectedProjects);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedProjects(next);
    try {
      await loadPortfolio(Array.from(next));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to filter projects");
    }
  };

  const toggleAllProjects = async () => {
    const allIds = allProjects.map((p) => p.id);
    const allSelected =
      allIds.length > 0 && selectedProjects.size === allIds.length;
    const next = allSelected ? new Set<string>() : new Set(allIds);
    setSelectedProjects(next);
    try {
      await loadPortfolio(Array.from(next));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to filter projects");
    }
  };

  const displayedProjects = useMemo(() => {
    const src = (
      portfolio?.projects?.length ? portfolio.projects : allProjects
    ).slice();
    return src
      .sort((a, b) => getDisplayScore(b) - getDisplayScore(a))
      .slice(0, 6);
  }, [portfolio?.projects, allProjects]);

  const graphs = portfolio?.graphs || {};
  const complexity = {
    "Small (<1000)": graphs.complexity_distribution?.distribution?.small || 0,
    "Medium (1000-3000)":
      graphs.complexity_distribution?.distribution?.medium || 0,
    "Large (>3000)": graphs.complexity_distribution?.distribution?.large || 0,
  };
  const scoreDist = {
    "Excellent (90-100%)":
      graphs.score_distribution?.distribution?.excellent || 0,
    "Good (80-89%)": graphs.score_distribution?.distribution?.good || 0,
    "Fair (70-79%)": graphs.score_distribution?.distribution?.fair || 0,
    "Poor (<70%)": graphs.score_distribution?.distribution?.poor || 0,
  };
  const projectType = {
    "GitHub Projects": portfolio?.project_type_analysis?.github?.count || 0,
    "Local Projects": portfolio?.project_type_analysis?.local?.count || 0,
  };

  const analysis = useMemo(() => {
    const projects = portfolio?.projects || [];
    let totalTestFiles = 0;
    let totalFunctions = 0;
    let totalClasses = 0;
    let totalComponents = 0;
    let githubProjects = 0;
    let localProjects = 0;
    let totalCompleteness = 0;
    let totalWords = 0;
    const developmentPatterns = new Set<string>();
    const docTypes: Record<string, number> = {};

    projects.forEach((project) => {
      const metrics = project.metrics || {};
      totalTestFiles += metrics.test_files_changed || 0;
      totalFunctions += metrics.functions || 0;
      totalClasses += metrics.classes || 0;
      totalComponents += metrics.components || 0;
      if (project.type === "GitHub") githubProjects += 1;
      else localProjects += 1;
      if (metrics.completeness_score)
        totalCompleteness += metrics.completeness_score;
      if (metrics.word_count) totalWords += metrics.word_count;
      (metrics.development_patterns?.project_evolution || []).forEach(
        (pattern) => developmentPatterns.add(pattern),
      );
      Object.entries(
        metrics.contribution_activity?.doc_type_counts || {},
      ).forEach(([type, count]) => {
        docTypes[type] = (docTypes[type] || 0) + Number(count || 0);
      });
    });

    const avgCompleteness =
      projects.length > 0
        ? (totalCompleteness / projects.length).toFixed(1)
        : "0.0";

    return {
      totalTestFiles,
      totalFunctions,
      totalClasses,
      totalComponents,
      githubProjects,
      localProjects,
      avgCompleteness,
      totalWords,
      developmentPatterns: Array.from(developmentPatterns),
      docTypes,
    };
  }, [portfolio?.projects]);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner"></div>Loading portfolio data...
      </div>
    );
  if (error)
    return (
      <div
        className="loading"
        style={{ color: "var(--danger)", flexDirection: "column" }}
      >
        <div>{error}</div>
        <button
          className="select-all-btn"
          onClick={() => void loadAll()}
          style={{ marginTop: 12, width: 180 }}
        >
          Retry
        </button>
      </div>
    );

  return (
    <div className="portfolio-layout">
      <div className="sidebar">
        <h2>📋 Project Selection</h2>
        <div className="project-selection">
          <button
            className="select-all-btn"
            onClick={() => void toggleAllProjects()}
          >
            {allProjects.length > 0 &&
            selectedProjects.size === allProjects.length
              ? "Deselect All"
              : "Select All"}
          </button>
          <div id="projectList">
            {allProjects.map((p) => {
              const checked = selectedProjects.has(p.id);
              const tags = (p.skills || []).slice(0, 3);
              return (
                <div
                  key={String(p.id)}
                  className={`project-item ${checked ? "selected" : ""}`}
                  onClick={() => void toggleProject(p.id)}
                >
                  <input
                    className="project-checkbox"
                    type="checkbox"
                    checked={checked}
                    onClick={(e) => e.stopPropagation()}
                    readOnly
                  />
                  <div className="project-name">{sidebarProjectName(p)}</div>
                  <div className="project-score">
                    Score: {getDisplayScore(p).toFixed(2)}
                  </div>
                  <div className="project-skills">
                    {tags.map((t) => (
                      <span key={t} className="skill-tag">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <div className="main-content">
        <div className="dashboard-header">
          <h1>🎯 Portfolio Dashboard</h1>
          <p className="dashboard-subtitle">
            Comprehensive analysis of your development work
          </p>
        </div>
        <div className="overview-cards" id="overviewCards">
          <div className="overview-card">
            <div className="overview-card-value">
              {portfolio?.overview?.total_projects ?? allProjects.length}
            </div>
            <div className="overview-card-label">Total Projects</div>
          </div>
          <div className="overview-card">
            <div className="overview-card-value">
              {Number(portfolio?.overview?.avg_score || 0).toFixed(2)}
            </div>
            <div className="overview-card-label">Average Score</div>
          </div>
          <div className="overview-card">
            <div className="overview-card-value">
              {portfolio?.overview?.total_skills ?? 0}
            </div>
            <div className="overview-card-label">Total Skills</div>
          </div>
          <div className="overview-card">
            <div className="overview-card-value">
              {portfolio?.overview?.total_languages ?? 0}
            </div>
            <div className="overview-card-label">Languages Used</div>
          </div>
          <div className="overview-card">
            <div className="overview-card-value">
              {(portfolio?.overview?.total_lines || 0).toLocaleString()}
            </div>
            <div className="overview-card-label">Lines of Code</div>
          </div>
        </div>
        <div className="graph-grid">
          <div className="graph-card">
            <h3>📊 Language Distribution</h3>
            <div className="chart-container">
              <PieChart data={graphs.language_distribution} />
            </div>
          </div>
          <div className="graph-card">
            <h3>📈 Project Complexity</h3>
            <div className="chart-container">
              <BarChart data={complexity} />
            </div>
          </div>
          <div className="graph-card">
            <h3>🏆 Score Distribution</h3>
            <div className="chart-container">
              <BarChart data={scoreDist} />
            </div>
          </div>
          <div className="graph-card">
            <h3>📅 Monthly Activity</h3>
            <div className="chart-container">
              <LineChart data={graphs.monthly_activity} />
            </div>
          </div>
          <div className="graph-card">
            <h3>🛠️ Top Skills</h3>
            <div className="chart-container small">
              <HorizontalBarChart data={graphs.top_skills} />
            </div>
          </div>
          <div className="graph-card">
            <h3>⚖️ GitHub vs Local</h3>
            <div className="chart-container small">
              <BarChart data={projectType} />
            </div>
          </div>
        </div>
        <div className="projects-section">
          <h2 className="section-title">🏆 Top Ranked Projects</h2>
          <div className="top-projects" id="topProjects">
            {displayedProjects.length ? (
              displayedProjects.map((p, idx) => (
                <ProjectCard
                  key={String(p.id)}
                  project={p}
                  rank={idx + 1}
                  onReload={loadAll}
                />
              ))
            ) : (
              <div style={{ color: "var(--text-muted)" }}>
                No projects selected
              </div>
            )}
          </div>
        </div>
        <div className="analysis-section">
          <h2 className="section-title">🔍 Detailed Analysis Insights</h2>
          <div className="analysis-grid" id="detailedAnalysis">
            {(portfolio?.projects || []).length === 0 ? (
              <div style={{ color: "var(--text-muted)" }}>
                No projects selected
              </div>
            ) : (
              <>
                <div className="analysis-card">
                  <h4>🧪 Testing & Quality</h4>
                  <div className="analysis-item">
                    <span className="analysis-label">Total Test Files:</span>{" "}
                    <span className="analysis-value">
                      {analysis.totalTestFiles}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Functions Created:</span>{" "}
                    <span className="analysis-value">
                      {analysis.totalFunctions}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Classes Created:</span>{" "}
                    <span className="analysis-value">
                      {analysis.totalClasses}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Components Built:</span>{" "}
                    <span className="analysis-value">
                      {analysis.totalComponents}
                    </span>
                  </div>
                </div>
                <div className="analysis-card">
                  <h4>📊 Project Distribution</h4>
                  <div className="analysis-item">
                    <span className="analysis-label">GitHub Projects:</span>{" "}
                    <span className="analysis-value">
                      {analysis.githubProjects}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Local Projects:</span>{" "}
                    <span className="analysis-value">
                      {analysis.localProjects}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Avg Completeness:</span>{" "}
                    <span className="analysis-value">
                      {analysis.avgCompleteness}%
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Total Words:</span>{" "}
                    <span className="analysis-value">
                      {analysis.totalWords.toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="analysis-card">
                  <h4>🚀 Development Patterns</h4>
                  <div className="analysis-item">
                    <span className="analysis-label">Evolution Patterns:</span>
                  </div>
                  {analysis.developmentPatterns.map((pattern) => (
                    <div key={pattern} className="keyword-tags">
                      <span className="keyword-tag">{pattern}</span>
                    </div>
                  ))}
                </div>
                <div className="analysis-card">
                  <h4>📝 Document Types</h4>
                  {Object.entries(analysis.docTypes).map(([type, count]) => (
                    <div key={type} className="analysis-item">
                      <span className="analysis-label">{type}:</span>{" "}
                      <span className="analysis-value">{count}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
        <div className="scoring-formula-section">
          <h2 className="section-title">📐 Project Scoring Methodology</h2>
          <div className="formula-grid">
            <div className="formula-card">
              <div className="formula-header">
                <span className="formula-icon">🔗</span>
                <div>
                  <div className="formula-title">GitHub Project Scoring</div>
                  <div className="formula-subtitle">
                    For projects with Git history and collaboration metrics
                  </div>
                </div>
              </div>
              <div className="formula-content">
                <div className="formula-label">📐 Calculation Formula</div>
                <div className="formula-text">{`Score = 0.30 × min(commits/50, 1)
      + 0.30 × min(days/30, 1)
      + 0.20 × min(lines/5000, 1)
      + 0.15 × min(code_files/20, 1)
      + 0.05 × min(test_files/8, 1)`}</div>
              </div>
            </div>
            <div className="formula-card">
              <div className="formula-header">
                <span className="formula-icon">💻</span>
                <div>
                  <div className="formula-title">Local Project Scoring</div>
                  <div className="formula-subtitle">
                    For projects without Git history, focusing on structure and
                    quality
                  </div>
                </div>
              </div>
              <div className="formula-content">
                <div className="formula-label">📐 Calculation Formula</div>
                <div className="formula-text">{`Score = 0.20 × min(files/40, 1)
      + 0.15 × min(lines/5000, 1)
      + 0.20 × min(code_files/30, 1)
      + 0.15 × min(test_files/10, 1)
      + 0.30 × min(maintainability/100, 1)`}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioPage;
