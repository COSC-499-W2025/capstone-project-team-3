import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config/api";
import "../styles/PortfolioPage.css";
import Chart from "chart.js/auto";

/** Returns true whenever <html data-theme="dark"> is set, and re-renders on change. */
function useIsDarkMode(): boolean {
  const [isDark, setIsDark] = useState(
    () => document.documentElement.getAttribute("data-theme") === "dark",
  );
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.getAttribute("data-theme") === "dark");
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);
  return isDark;
}

interface Project {
  id: string | number;
  name?: string;
  title?: string;
  score?: number;
  rank?: number;
  score_overridden?: boolean;
  score_overridden_value?: number;
  score_override_exclusions?: string[];
  dates?: string;
  start_date?: string;
  end_date?: string;
  created_at?: string;
  last_modified?: string;
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
    roles?: string[];
    development_patterns?: { project_evolution?: string[] };
    technical_keywords?: string[];
    complexity_analysis?: {
      maintainability_score?: { overall_score?: number };
    };
    commit_patterns?: { commit_frequency?: { development_intensity?: string } };
    contribution_activity?: { doc_type_counts?: Record<string, number> };
  };
}

interface UserInfo {
  name?: string;
  email?: string;
  links?: Array<{ label: string; url: string }>;
  education?: string;
  job_title?: string;
  education_details?: string | null;
  github_user?: string | null;
  industry?: string | null;
  personal_summary?: string | null;
  profile_picture_path?: string | null;
}

interface PortfolioData {
  user?: UserInfo;
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
    daily_activity?: Record<string, number>;
    top_skills?: Record<string, number>;
  };
  project_type_analysis?: {
    github?: { count?: number };
    local?: { count?: number };
  };
  projects?: Project[];
  collaboration_network?: {
    nodes: Array<{
      id: string;
      name: string;
      commits: number;
      is_primary: boolean;
      projects: string[];
    }>;
    edges: Array<{
      source: string;
      target: string;
      projects: string[];
      weight: number;
      is_peer?: boolean;
    }>;
  };
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

const formatMetricName = (metricName: string): string =>
  metricName
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const formatScorePercent = (score: number): string =>
  `${Math.round(Math.max(0, Math.min(1, score)) * 100)}%`;

interface ScoreSignal {
  label: string;
  value: string;
  tone: "strong" | "moderate" | "limited";
  explanation: string;
}

const getSignalTone = (
  value: number,
  strongThreshold: number,
  moderateThreshold: number,
): ScoreSignal["tone"] => {
  if (value >= strongThreshold) return "strong";
  if (value >= moderateThreshold) return "moderate";
  return "limited";
};

const getProjectDurationDays = (project: Project): number | null => {
  const startValue = project.created_at || project.start_date;
  const endValue = project.last_modified || project.end_date;
  if (!startValue || !endValue) return null;

  const start = new Date(startValue);
  const end = new Date(endValue);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return null;

  const diffMs = end.getTime() - start.getTime();
  if (diffMs < 0) return null;
  return Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));
};

const getProjectScoreSignals = (project: Project): ScoreSignal[] => {
  const metrics = project.metrics || {};
  const isGithubProject =
    (project.type || "").toLowerCase() === "github" ||
    (metrics.total_commits || 0) > 0;
  const durationDays = getProjectDurationDays(project);
  const signals: ScoreSignal[] = [];

  if (isGithubProject && typeof metrics.total_commits === "number") {
    const tone = getSignalTone(metrics.total_commits, 25, 8);
    signals.push({
      label: "Repository Activity",
      value: `${metrics.total_commits} commits`,
      tone,
      explanation:
        tone === "strong"
          ? "The repository shows sustained iteration and visible delivery history."
          : tone === "moderate"
            ? "There is meaningful commit history, though the activity footprint is moderate."
            : "Limited commit history is visible, so activity contributes less to this score.",
    });
  }

  if (durationDays != null) {
    const tone = getSignalTone(durationDays, 30, 7);
    signals.push({
      label: "Project Duration",
      value: `${durationDays} days`,
      tone,
      explanation:
        tone === "strong"
          ? "The project appears to have been developed over a sustained period of time."
          : tone === "moderate"
            ? "The project has a meaningful active window, but not a long-lived history."
            : "The visible timeline is short, so duration contributes less to the score.",
    });
  }

  if (typeof metrics.total_lines === "number") {
    const tone = getSignalTone(metrics.total_lines, 2500, 750);
    signals.push({
      label: "Codebase Scope",
      value: `${metrics.total_lines.toLocaleString()} LOC`,
      tone,
      explanation:
        tone === "strong"
          ? "The project has substantial implementation depth and visible code volume."
          : tone === "moderate"
            ? "The project shows moderate implementation scope."
            : "The visible code footprint is lighter, so scope contributes less to the score.",
    });
  }

  if (typeof metrics.test_files_changed === "number") {
    const tone = getSignalTone(metrics.test_files_changed, 5, 1);
    signals.push({
      label: "Testing Evidence",
      value: `${metrics.test_files_changed} test files`,
      tone,
      explanation:
        tone === "strong"
          ? "Testing is clearly represented in the repository and helps strengthen confidence."
          : tone === "moderate"
            ? "Some testing evidence is present, though it is not yet a standout strength."
            : "There is limited visible testing evidence in the portfolio data.",
    });
  }

  const maintainability =
    metrics.complexity_analysis?.maintainability_score?.overall_score;
  if (typeof maintainability === "number") {
    const tone = getSignalTone(maintainability, 75, 55);
    signals.push({
      label: "Maintainability",
      value: `${Math.round(maintainability)}/100`,
      tone,
      explanation:
        tone === "strong"
          ? "Code quality signals appear healthy and support a stronger overall score."
          : tone === "moderate"
            ? "Maintainability is reasonable, but there is still room to improve structure or complexity."
            : "Maintainability is currently limiting the visible score profile.",
    });
  }

  if (typeof metrics.completeness_score === "number") {
    const tone = getSignalTone(metrics.completeness_score, 75, 40);
    signals.push({
      label: "Documentation",
      value: `${Math.round(metrics.completeness_score)}%`,
      tone,
      explanation:
        tone === "strong"
          ? "Documentation is a visible strength and improves portfolio readability."
          : tone === "moderate"
            ? "Some documentation support is present, but it is not yet a standout signal."
            : "Documentation completeness is limited in the current portfolio data.",
    });
  }

  return signals.slice(0, 4);
};

const shouldTruncateSummary = (summary: string): boolean => {
  const wordCount = summary.split(/\s+/).filter(Boolean).length;
  const charCount = summary.length;
  return wordCount > 25 || charCount > 150;
};

// ── Profile hero helpers ─────────────────────────────────────────
function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2)
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return (parts[0]?.[0] || "?").toUpperCase();
}

function getAvatarBackground(name: string): string {
  let hash = 0;
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) >>> 0;
  const h1 = hash % 360;
  const h2 = (h1 + 48) % 360;
  return `linear-gradient(135deg, hsl(${h1},52%,32%), hsl(${h2},52%,26%))`;
}

function UserProfileCard({ user }: { user: UserInfo }) {
  const name = user.name || "Portfolio Owner";
  const initials = getInitials(name);
  const avatarBg = getAvatarBackground(name);

  // Build the profile picture URL if a path is stored
  const profilePictureUrl = user.profile_picture_path
    ? `${API_BASE_URL}/api/user-preferences/profile-picture`
    : null;

  // education_details arrives as a JSON string from the API
  let bestEdu: { institution?: string; degree?: string } | null = null;
  if (user.education_details) {
    try {
      const parsed = JSON.parse(user.education_details as string) as Array<{
        institution?: string;
        degree?: string;
      }>;
      if (Array.isArray(parsed) && parsed.length > 0)
        bestEdu = parsed[parsed.length - 1];
    } catch {
      /* fall back to plain education string */
    }
  }

  const educationLine = bestEdu
    ? [bestEdu.degree, bestEdu.institution ? `— ${bestEdu.institution}` : ""]
        .filter(Boolean)
        .join(" ")
    : user.education || "";

  const githubLink = user.links?.find((l) => l.label === "GitHub");
  const linkedinLink = user.links?.find((l) => l.label === "LinkedIn");
  const hasContacts = !!(githubLink || user.email || linkedinLink);

  return (
    <div className="profile-hero">
      {profilePictureUrl ? (
        <img
          src={profilePictureUrl}
          alt={name}
          className="profile-avatar profile-avatar--photo"
          style={{ objectFit: "cover", background: avatarBg }}
        />
      ) : (
        <div className="profile-avatar" style={{ background: avatarBg }}>
          {initials}
        </div>
      )}

      <div className="profile-info">
        <div className="profile-name">{name}</div>
        <div className="profile-title-row">
          {user.job_title && (
            <span className="profile-job-title">{user.job_title}</span>
          )}
          {user.job_title && user.industry && (
            <span className="profile-title-sep">·</span>
          )}
          {user.industry && (
            <span className="profile-industry-chip">{user.industry}</span>
          )}
        </div>
        {educationLine && (
          <div className="profile-education">
            <span className="profile-edu-icon">🎓</span>
            {educationLine}
          </div>
        )}
        {user.personal_summary && (
          <p className="profile-personal-summary">{user.personal_summary}</p>
        )}
      </div>

      {hasContacts && (
        <div className="profile-contacts">
          {githubLink && (
            <a
              href={githubLink.url}
              target="_blank"
              rel="noopener noreferrer"
              className="profile-contact-link"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58v-2.03c-3.34.72-4.04-1.61-4.04-1.61-.54-1.38-1.33-1.74-1.33-1.74-1.08-.74.08-.73.08-.73 1.2.08 1.83 1.23 1.83 1.23 1.07 1.83 2.8 1.3 3.49 1 .1-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3-.54-1.52.11-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 3-.4 11.5 11.5 0 0 1 3 .4c2.28-1.55 3.29-1.23 3.29-1.23.65 1.66.24 2.88.12 3.18.77.84 1.23 1.91 1.23 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.82 1.1.82 2.22v3.29c0 .32.22.7.83.58C20.57 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z" />
              </svg>
              {user.github_user || "GitHub"}
            </a>
          )}
          {user.email && (
            <a href={`mailto:${user.email}`} className="profile-contact-link">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <polyline points="2,4 12,13 22,4" />
              </svg>
              {user.email}
            </a>
          )}
          {linkedinLink && (
            <a
              href={linkedinLink.url}
              target="_blank"
              rel="noopener noreferrer"
              className="profile-contact-link"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
              LinkedIn
            </a>
          )}
        </div>
      )}
    </div>
  );
}

function PieChart({
  data,
  canvasId,
}: {
  data?: Record<string, number>;
  canvasId?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const labels = Object.keys(data || {});
  const values = Object.values(data || {}).map((v) => Number(v) || 0);
  const isDark = useIsDarkMode();

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const textColor = isDark ? "#ffffff" : "#4a5568";

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
            borderColor: isDark ? "#1a2535" : "#ffffff",
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
              color: textColor,
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
  }, [labels, values, isDark]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} id={canvasId} />;
}

function BarChart({
  data,
  canvasId,
}: {
  data?: Record<string, number>;
  canvasId?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const labels = Object.keys(data || {});
  const values = Object.values(data || {}).map((v) => Number(v) || 0);
  const isDark = useIsDarkMode();

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const textColor = isDark ? "#ffffff" : "#4a5568";
    const gridColor = isDark ? "#2d3f52" : "#e2e8f0";

    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: isDark ? "#5fa3bc" : "#2d3748",
            borderColor: isDark ? "#3a7a96" : "#4a5568",
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
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } },
          },
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } },
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
  }, [labels, values, isDark]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} id={canvasId} />;
}

function HorizontalBarChart({
  data,
  canvasId,
}: {
  data?: Record<string, number>;
  canvasId?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const ordered = Object.entries(data || {}).slice(0, 8);
  const labels = ordered.map(([k]) => k);
  const values = ordered.map(([, v]) => Number(v) || 0);
  const isDark = useIsDarkMode();

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const textColor = isDark ? "#ffffff" : "#4a5568";
    const gridColor = isDark ? "#2d3f52" : "#e2e8f0";

    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: isDark ? "#5fa3bc" : "#4a5568",
            borderColor: isDark ? "#3a7a96" : "#2d3748",
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
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } },
          },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } },
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
  }, [labels, values, isDark]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} id={canvasId} />;
}

function LineChart({
  data,
  canvasId,
}: {
  data?: Record<string, number>;
  canvasId?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const sortedData = Object.entries(data || {}).sort((a, b) =>
    a[0].localeCompare(b[0]),
  );
  const labels = sortedData.map(([month]) => month);
  const values = sortedData.map(([, value]) => Number(value) || 0);
  const isDark = useIsDarkMode();

  useEffect(() => {
    if (!canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const textColor = isDark ? "#ffffff" : "#4a5568";
    const gridColor = isDark ? "#2d3f52" : "#e2e8f0";
    const lineColor = isDark ? "#5fa3bc" : "#2d3748";

    chartRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Activity",
            data: values,
            borderColor: lineColor,
            backgroundColor: isDark ? "rgba(95, 163, 188, 0.15)" : "rgba(45, 55, 72, 0.1)",
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointBackgroundColor: lineColor,
            pointBorderColor: isDark ? "#1a2535" : "#ffffff",
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
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 }, stepSize: 0.5 },
            title: {
              display: true,
              text: "Activity Level",
              color: textColor,
              font: { size: 12, weight: "bold" },
            },
          },
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } },
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
  }, [labels, values, isDark]);

  if (!labels.length) return <div className="loading">No data available</div>;
  return <canvas ref={canvasRef} id={canvasId} />;
}

interface HeatmapCell {
  key: string;
  date: Date;
  value: number;
  level: 0 | 1 | 2 | 3 | 4;
}

interface HeatmapModel {
  weeks: HeatmapCell[][];
  monthLabels: Array<{ label: string; col: number }>;
  yearLabels: Array<{ label: string; col: number }>;
  maxValue: number;
  totalSignal: number;
  activeDays: number;
  busiestDay: HeatmapCell | null;
}

const HEATMAP_CELL_STEP = 16;

const toDateKey = (date: Date): string => date.toISOString().slice(0, 10);

const parseDateLike = (value?: string): Date | null => {
  if (!value) return null;
  const match = value.trim().match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!match) return null;
  const date = new Date(`${match[1]}-${match[2]}-${match[3]}T00:00:00`);
  if (Number.isNaN(date.getTime())) return null;
  return date;
};

const monthShort = (date: Date): string =>
  date.toLocaleDateString(undefined, { month: "short" });

const formatHeatmapDate = (date: Date): string =>
  date.toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

const formatHeatmapHighlightDate = (date: Date): string =>
  date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

const buildHeatmapModel = (
  dailyActivity: Record<string, number> | undefined,
  monthlyActivity: Record<string, number> | undefined,
  projects: Project[] | undefined,
): HeatmapModel => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Find the earliest date across projects, daily activity, and monthly activity
  let earliest: Date | null = null;
  const consider = (d: Date | null) => {
    if (d && (!earliest || d < earliest)) earliest = d;
  };

  (projects || []).forEach((p) => {
    consider(parseDateLike(p.created_at || p.start_date));
    consider(parseDateLike(p.last_modified || p.end_date));
  });

  // Also consider daily activity dates so the calendar range covers them
  Object.keys(dailyActivity || {}).forEach((dayKey) => {
    consider(parseDateLike(dayKey));
  });

  // Also consider monthly activity dates
  Object.keys(monthlyActivity || {}).forEach((monthKey) => {
    const m = monthKey.match(/^(\d{4})-(\d{2})/);
    if (m) consider(new Date(Number(m[1]), Number(m[2]) - 1, 1));
  });

  // Start from Jan 1 of the earliest project year, but always show at least a full year
  const currentYear = today.getFullYear();
  let startYear = currentYear - 1; // default: at least one full year back

  if (earliest) {
    const earliestYear = earliest.getFullYear();
    if (earliestYear < startYear) startYear = earliestYear;
  }

  const start = new Date(startYear, 0, 1); // Jan 1 of the start year

  const calendarStart = new Date(start);
  calendarStart.setDate(calendarStart.getDate() - calendarStart.getDay());

  const dayScores = new Map<string, number>();
  const endBound = new Date(today);

  const addSignal = (date: Date, score: number) => {
    if (date < calendarStart || date > endBound) return;
    const key = toDateKey(date);
    dayScores.set(key, (dayScores.get(key) || 0) + score);
  };

  const hasDailyActivity = Object.keys(dailyActivity || {}).length > 0;

  if (hasDailyActivity) {
    Object.entries(dailyActivity || {}).forEach(([dayKey, rawValue]) => {
      const value = Number(rawValue) || 0;
      if (value <= 0) return;
      const date = parseDateLike(dayKey);
      if (!date) return;
      addSignal(date, value);
    });
  } else {
    (projects || []).forEach((project) => {
      const createdAt = parseDateLike(project.created_at || project.start_date);
      const lastModified = parseDateLike(
        project.last_modified || project.end_date,
      );

      if (createdAt) addSignal(createdAt, 1.25);
      if (lastModified) {
        const isSameAsCreate =
          createdAt && toDateKey(createdAt) === toDateKey(lastModified);
        addSignal(lastModified, isSameAsCreate ? 0.5 : 1);
      }
    });

    Object.entries(monthlyActivity || {}).forEach(([monthKey, rawValue]) => {
      const value = Number(rawValue) || 0;
      if (value <= 0) return;

      const monthMatch = monthKey.match(/^(\d{4})-(\d{2})/);
      if (!monthMatch) return;

      const year = Number(monthMatch[1]);
      const monthIndex = Number(monthMatch[2]) - 1;
      if (Number.isNaN(year) || Number.isNaN(monthIndex)) return;

      const monthEnd = new Date(year, monthIndex + 1, 0);
      const daysInMonth = monthEnd.getDate();
      if (daysInMonth <= 0) return;

      const dailySignal = (value / daysInMonth) * 0.35;
      for (let day = 1; day <= daysInMonth; day += 1) {
        const date = new Date(year, monthIndex, day);
        addSignal(date, dailySignal);
      }
    });
  }

  const allDays: Date[] = [];
  for (
    const cursor = new Date(calendarStart);
    cursor <= endBound;
    cursor.setDate(cursor.getDate() + 1)
  ) {
    allDays.push(new Date(cursor));
  }

  const values = allDays.map((date) => dayScores.get(toDateKey(date)) || 0);
  const maxValue = Math.max(0, ...values);

  const levelFor = (value: number): 0 | 1 | 2 | 3 | 4 => {
    if (value <= 0 || maxValue <= 0) return 0;
    const ratio = value / maxValue;
    if (ratio <= 0.25) return 1;
    if (ratio <= 0.5) return 2;
    if (ratio <= 0.75) return 3;
    return 4;
  };

  const cells: HeatmapCell[] = allDays.map((date) => {
    const key = toDateKey(date);
    const value = dayScores.get(key) || 0;
    return {
      key,
      date,
      value,
      level: levelFor(value),
    };
  });

  const weeks: HeatmapCell[][] = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }

  const monthLabels: Array<{ label: string; col: number }> = [];
  let lastLabel = "";
  weeks.forEach((week, col) => {
    const firstDay = week[0];
    if (!firstDay) return;
    const label = monthShort(firstDay.date);
    if (label !== lastLabel && firstDay.date.getDate() <= 7) {
      monthLabels.push({ label, col });
      lastLabel = label;
    }
  });

  const yearLabels: Array<{ label: string; col: number }> = [];
  let lastYear = -1;
  weeks.forEach((week, col) => {
    const firstDay = week[0];
    if (!firstDay) return;
    const y = firstDay.date.getFullYear();
    if (y !== lastYear) {
      // Skip a partial trailing week from the previous year at the start
      if (yearLabels.length === 0 && col === 0 && firstDay.date.getMonth() === 11) {
        lastYear = y;
        return;
      }
      yearLabels.push({ label: String(y), col });
      lastYear = y;
    }
  });

  const activeCells = cells.filter((cell) => cell.value > 0);
  const activeDays = activeCells.length;
  const totalSignal = cells.reduce((sum, cell) => sum + cell.value, 0);
  const busiestDay =
    activeCells.length > 0
      ? activeCells.reduce((best, current) =>
          current.value > best.value ? current : best,
        )
      : null;

  return {
    weeks,
    monthLabels,
    yearLabels,
    maxValue,
    totalSignal,
    activeDays,
    busiestDay,
  };
};

function ActivityHeatmap({
  dailyActivity,
  monthlyActivity,
  projects,
}: {
  dailyActivity?: Record<string, number>;
  monthlyActivity?: Record<string, number>;
  projects?: Project[];
}) {
  const model = useMemo(
    () => buildHeatmapModel(dailyActivity, monthlyActivity, projects),
    [dailyActivity, monthlyActivity, projects],
  );

  const calendarWidth = model.weeks.length * HEATMAP_CELL_STEP;
  const totalWeeks = model.weeks.length;

  return (
    <div className="activity-heatmap-card">
      <div className="activity-heatmap-summary">
        <div className="activity-heatmap-kpi">
          <span className="activity-heatmap-kpi-label">Active Days</span>
          <strong>{model.activeDays}</strong>
        </div>
        <div className="activity-heatmap-kpi">
          <span className="activity-heatmap-kpi-label">Peak Signal</span>
          <strong>{model.maxValue.toFixed(2)}</strong>
        </div>
        <div className="activity-heatmap-kpi">
          <span className="activity-heatmap-kpi-label">Total Signal</span>
          <strong>{model.totalSignal.toFixed(1)}</strong>
        </div>
      </div>

      <div className="activity-heatmap-calendar-wrap">
        <div className="activity-heatmap-weekdays" aria-hidden>
          <span>Sun</span>
          <span></span>
          <span>Tue</span>
          <span></span>
          <span>Thu</span>
          <span></span>
          <span>Sat</span>
        </div>

        <div className="activity-heatmap-scroll">
          {model.yearLabels.length > 1 && (
            <div
              className="activity-heatmap-years"
              style={{ width: `${calendarWidth}px` }}
              aria-hidden
            >
              {model.yearLabels.map((yr) => (
                <span
                  key={`yr-${yr.label}`}
                  className="activity-heatmap-year"
                  style={{ left: `${yr.col * HEATMAP_CELL_STEP}px` }}
                >
                  {yr.label}
                </span>
              ))}
            </div>
          )}

          <div
            className="activity-heatmap-months"
            style={{ width: `${calendarWidth}px` }}
            aria-hidden
          >
            {model.monthLabels.map((month) => (
              <span
                key={`${month.label}-${month.col}`}
                className="activity-heatmap-month"
                style={{ left: `${month.col * HEATMAP_CELL_STEP}px` }}
              >
                {month.label}
              </span>
            ))}
          </div>

          <div
            className="activity-heatmap-grid"
            style={{ width: `${calendarWidth}px` }}
          >
            {model.weeks.map((week, weekIndex) => (
              <div key={`week-${weekIndex}`} className="activity-heatmap-week">
                {week.map((cell) => (
                  <div
                    key={cell.key}
                    className={`activity-cell activity-cell-level-${cell.level} ${
                      weekIndex <= 10
                        ? "activity-cell-tooltip-right"
                        : weekIndex >= totalWeeks - 11
                          ? "activity-cell-tooltip-left"
                          : "activity-cell-tooltip-center"
                    }`}
                    data-tooltip={`${formatHeatmapDate(cell.date)} · ${cell.value.toFixed(2)} activity signal`}
                    aria-label={`${formatHeatmapDate(cell.date)} with activity signal ${cell.value.toFixed(2)}`}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="activity-heatmap-footer">
        <span className="activity-heatmap-highlight">
          {model.busiestDay
            ? `Peak activity date: ${formatHeatmapHighlightDate(model.busiestDay.date)}`
            : "No activity yet"}
        </span>
        <div className="activity-heatmap-legend" aria-hidden>
          <span>Less</span>
          <i className="activity-cell activity-cell-level-0" />
          <i className="activity-cell activity-cell-level-1" />
          <i className="activity-cell activity-cell-level-2" />
          <i className="activity-cell activity-cell-level-3" />
          <i className="activity-cell activity-cell-level-4" />
          <span>More</span>
        </div>
      </div>
    </div>
  );
}

/* ─── Collaboration Network Graph ─── */

interface NetworkNode {
  id: string;
  name: string;
  commits: number;
  is_primary: boolean;
  projects: string[];
  // layout state
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx: number | null; // fixed x (when dragging)
  fy: number | null; // fixed y (when dragging)
}

interface NetworkEdge {
  source: string;
  target: string;
  projects: string[];
  weight: number;
  is_peer?: boolean;
}

type NetworkMode = "star" | "full";

/* Colour palette for collaborator nodes */
const NODE_COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#f97316",
  "#eab308", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6",
];

/* Theme palettes for canvas rendering */
const GRAPH_THEMES = {
  dark: {
    primaryGrad0: "#334155",
    primaryGrad1: "#0f172a",
    primaryLabel: "#fff",
    primaryLabelDim: "rgba(255,255,255,0.4)",
    labelBg: "rgba(30,41,59,0.7)",
    labelBgDim: "rgba(30,41,59,0.3)",
    labelText: "#e2e8f0",
    labelTextDim: "rgba(255,255,255,0.3)",
    badgeBg: (a: number) => `rgba(30,41,59,${a})`,
    badgeStroke: (hi: boolean) => hi ? "rgba(99,102,241,0.6)" : "rgba(99,102,241,0.2)",
    badgeText: (hi: boolean) => hi ? "#fff" : "rgba(255,255,255,0.7)",
    gloss: "rgba(255,255,255,0.13)",
    commitBadge: "rgba(255,255,255,0.9)",
    ringHighlight: "#fff",
  },
  light: {
    primaryGrad0: "#e2e8f0",
    primaryGrad1: "#94a3b8",
    primaryLabel: "#1e293b",
    primaryLabelDim: "rgba(30,41,59,0.35)",
    labelBg: "rgba(255,255,255,0.85)",
    labelBgDim: "rgba(255,255,255,0.4)",
    labelText: "#334155",
    labelTextDim: "rgba(51,65,85,0.35)",
    badgeBg: (a: number) => `rgba(255,255,255,${a})`,
    badgeStroke: (hi: boolean) => hi ? "rgba(99,102,241,0.7)" : "rgba(99,102,241,0.25)",
    badgeText: (hi: boolean) => hi ? "#1e293b" : "rgba(30,41,59,0.6)",
    gloss: "rgba(255,255,255,0.25)",
    commitBadge: "#1e293b",
    ringHighlight: "#1e293b",
  },
} as const;

type GraphThemeMode = keyof typeof GRAPH_THEMES;

function CollaborationNetwork({
  network,
}: {
  network?: PortfolioData["collaboration_network"];
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const nodesRef = useRef<NetworkNode[]>([]);
  const edgesRef = useRef<NetworkEdge[]>([]);
  const animRef = useRef<number>(0);
  const dragRef = useRef<{
    node: NetworkNode | null;
    offsetX: number;
    offsetY: number;
    active: boolean;
    hasMoved: boolean;
  }>({ node: null, offsetX: 0, offsetY: 0, active: false, hasMoved: false });
  const hoveredRef = useRef<NetworkNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<NetworkNode | null>(null);
  const sizeRef = useRef({ w: 800, h: 480 });
  const scaleRef = useRef(1);

  /* ---- Theme toggle ---- */
  const [graphTheme, setGraphTheme] = useState<GraphThemeMode>("dark");
  const themeRef = useRef<GraphThemeMode>("dark");
  useEffect(() => { themeRef.current = graphTheme; }, [graphTheme]);

  /* ---- Network mode toggle (star = default, full = peer connections) ---- */
  const [networkMode, setNetworkMode] = useState<NetworkMode>("star");
  const networkModeRef = useRef<NetworkMode>("star");
  useEffect(() => { networkModeRef.current = networkMode; }, [networkMode]);

  /* ---- Helpers ---- */
  const nodeRadius = (n: NetworkNode) => {
    const s = scaleRef.current;
    if (n.is_primary) return 32 * s;
    if (networkModeRef.current === "full") {
      // In full network mode, size by project breadth (not commits)
      const projCount = n.projects.length;
      return (16 + Math.min(projCount, 8) * 2.5) * s;
    }
    return (14 + Math.min(n.commits, 80) * 0.18) * s;
  };

  const nodeColor = (n: NetworkNode, i: number) =>
    n.is_primary
      ? (themeRef.current === "dark" ? "#1e293b" : "#cbd5e1")
      : NODE_COLORS[i % NODE_COLORS.length];

  const hitTest = (mx: number, my: number): NetworkNode | null => {
    for (let i = nodesRef.current.length - 1; i >= 0; i--) {
      const n = nodesRef.current[i];
      const r = nodeRadius(n) + 4;
      if ((n.x - mx) ** 2 + (n.y - my) ** 2 <= r * r) return n;
    }
    return null;
  };

  /* ---- Dynamic sizing via ResizeObserver ---- */
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const w = Math.floor(entry.contentRect.width);
        if (w > 100) {
          sizeRef.current.w = w;
          sizeRef.current.h = Math.max(420, Math.min(580, Math.floor(w * 0.50)));
        }
      }
    });
    ro.observe(container);
    // Initialise immediately
    const w = container.clientWidth;
    if (w > 100) {
      sizeRef.current.w = w;
      sizeRef.current.h = Math.max(420, Math.min(580, Math.floor(w * 0.50)));
    }
    return () => ro.disconnect();
  }, []);

  /* ---- Physics simulation (runs every frame) ---- */
  const simulate = useCallback(() => {
    const nds = nodesRef.current;
    const allEds = edgesRef.current;
    const mode = networkModeRef.current;
    const eds = mode === "star" ? allEds.filter(e => !e.is_peer) : allEds;
    const W = sizeRef.current.w;
    const H = sizeRef.current.h;
    const cx = W / 2;
    const cy = H / 2;
    // Dynamic scale: bigger canvas + fewer nodes → larger visuals
    const rawDimScale = Math.min(W, H) / 480;
    const nodeAdj = Math.max(0.8, Math.min(1.5, 8 / Math.max(nds.length, 1)));
    const sizeScale = Math.max(0.9, Math.min(1.7, rawDimScale * nodeAdj));
    scaleRef.current = sizeScale;
    const isFull = mode === "full";
    const repulsion = (isFull ? 28000 : 12000) * sizeScale;
    const attraction = isFull ? 0.001 : 0.003;
    const centerPull = isFull ? 0.004 : 0.008;
    const damping = 0.82;

    for (let i = 0; i < nds.length; i++) {
      for (let j = i + 1; j < nds.length; j++) {
        const dx = nds[j].x - nds[i].x;
        const dy = nds[j].y - nds[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nds[i].vx -= fx;
        nds[i].vy -= fy;
        nds[j].vx += fx;
        nds[j].vy += fy;
      }
    }

    const nodeMap = new Map(nds.map((n) => [n.id, n]));
    for (const edge of eds) {
      const s = nodeMap.get(edge.source);
      const t = nodeMap.get(edge.target);
      if (!s || !t) continue;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const idealLen = (isFull ? (edge.is_peer ? 350 : 280) : 220) * sizeScale;
      const displacement = dist - idealLen;
      const force = displacement * attraction * (1 + edge.weight * (isFull ? 0.1 : 0.3));
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx;
      s.vy += fy;
      t.vx -= fx;
      t.vy -= fy;
    }

    for (const n of nds) {
      n.vx += (cx - n.x) * centerPull;
      n.vy += (cy - n.y) * centerPull;
    }

    // Node-node overlap repulsion — push overlapping nodes apart hard
    for (let i = 0; i < nds.length; i++) {
      for (let j = i + 1; j < nds.length; j++) {
        const ri = nodeRadius(nds[i]);
        const rj = nodeRadius(nds[j]);
        const minDist = ri + rj + (isFull ? 60 : 30) * sizeScale; // min gap between node edges
        const dx = nds[j].x - nds[i].x;
        const dy = nds[j].y - nds[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        if (dist < minDist) {
          const push = (minDist - dist) * 0.15;
          const px = (dx / dist) * push;
          const py = (dy / dist) * push;
          nds[i].vx -= px;
          nds[i].vy -= py;
          nds[j].vx += px;
          nds[j].vy += py;
        }
      }
    }

    const pad = 60;
    for (const n of nds) {
      if (n.fx !== null && n.fy !== null) {
        n.x = n.fx;
        n.y = n.fy;
        n.vx = 0;
        n.vy = 0;
      } else {
        n.vx *= damping;
        n.vy *= damping;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(pad, Math.min(W - pad, n.x));
        n.y = Math.max(pad, Math.min(H - pad, n.y));
      }
    }
  }, []);

  /* ---- Draw frame ---- */
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const th = GRAPH_THEMES[themeRef.current];

    const W = sizeRef.current.w;
    const H = sizeRef.current.h;
    const sc = scaleRef.current;
    const dpr = window.devicePixelRatio || 1;
    if (canvas.width !== W * dpr || canvas.height !== H * dpr) {
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = W + "px";
      canvas.style.height = H + "px";
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const nds = nodesRef.current;
    const allEds = edgesRef.current;
    const mode = networkModeRef.current;
    const eds = mode === "star" ? allEds.filter(e => !e.is_peer) : allEds;
    const nodeMap = new Map(nds.map((n) => [n.id, n]));
    const hovered = hoveredRef.current;
    const dragging = dragRef.current.active;

    // -- Edges --
    for (const edge of eds) {
      const s = nodeMap.get(edge.source);
      const t = nodeMap.get(edge.target);
      if (!s || !t) continue;

      const isHighlighted =
        hovered && (hovered.id === edge.source || hovered.id === edge.target);

      const grad = ctx.createLinearGradient(s.x, s.y, t.x, t.y);
      const sIdx = nds.indexOf(s);
      const tIdx = nds.indexOf(t);
      const isPeer = !!edge.is_peer;
      const alpha = isHighlighted ? 0.65 : hovered ? (isPeer ? 0.03 : 0.06) : isPeer ? 0.09 : 0.15 + edge.weight * 0.04;
      grad.addColorStop(0, hexWithAlpha(nodeColor(s, sIdx), alpha));
      grad.addColorStop(1, hexWithAlpha(nodeColor(t, tIdx), alpha));

      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = isHighlighted
        ? 2.5 + edge.weight * 0.5
        : isPeer ? 0.5 + edge.weight * 0.15 : 0.8 + edge.weight * 0.25;
      // Peer edges get a dashed style to distinguish from primary connections
      if (edge.is_peer) {
        ctx.setLineDash([6 * sc, 4 * sc]);
      } else {
        ctx.setLineDash([]);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Only show shared-project count badge on hovered edges
      if (isHighlighted) {
        const mx = (s.x + t.x) / 2;
        const my = (s.y + t.y) / 2;
        const badgeAlpha = 0.92;
        ctx.fillStyle = th.badgeBg(badgeAlpha);
        ctx.beginPath();
        ctx.arc(mx, my, Math.round(9 * sc), 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = th.badgeStroke(true);
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = th.badgeText(true);
        ctx.font = `bold ${Math.round(8 * sc)}px Inter, system-ui, sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(String(edge.projects.length), mx, my);
      }
    }

    // -- Nodes --
    // Build set of node IDs connected to the hovered node
    const connectedIds = new Set<string>();
    if (hovered) {
      connectedIds.add(hovered.id);
      for (const edge of eds) {
        if (edge.source === hovered.id) connectedIds.add(edge.target);
        if (edge.target === hovered.id) connectedIds.add(edge.source);
      }
    }

    nds.forEach((node, i) => {
      const r = nodeRadius(node);
      const color = nodeColor(node, i);
      const isHovered = hovered?.id === node.id;
      const isConnected = connectedIds.has(node.id);
      const dim = hovered && !isHovered && !isConnected && !dragging;

      // Glow (hovered, connected, or primary)
      if (isHovered || isConnected || node.is_primary) {
        const glowStrength = (isHovered ? 10 : isConnected ? 8 : 6) * sc;
        ctx.beginPath();
        ctx.arc(node.x, node.y, r + glowStrength, 0, Math.PI * 2);
        const glow = ctx.createRadialGradient(
          node.x, node.y, r * 0.5,
          node.x, node.y, r + glowStrength + 4
        );
        const glowAlpha = isHovered ? 0.35 : isConnected ? 0.28 : 0.18;
        glow.addColorStop(0, hexWithAlpha(color, glowAlpha));
        glow.addColorStop(1, hexWithAlpha(color, 0));
        ctx.fillStyle = glow;
        ctx.fill();
      }

      // Node body
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
      const bodyGrad = ctx.createRadialGradient(
        node.x - r * 0.3, node.y - r * 0.3, r * 0.1,
        node.x, node.y, r
      );
      if (node.is_primary) {
        bodyGrad.addColorStop(0, th.primaryGrad0);
        bodyGrad.addColorStop(1, th.primaryGrad1);
      } else {
        bodyGrad.addColorStop(0, lighten(color, 20));
        bodyGrad.addColorStop(1, color);
      }
      ctx.fillStyle = dim ? hexWithAlpha(color, 0.35) : bodyGrad;
      ctx.fill();

      // Ring
      ctx.strokeStyle = dim
        ? hexWithAlpha(color, 0.2)
        : isHovered
          ? th.ringHighlight
          : isConnected
            ? hexWithAlpha(th.ringHighlight, 0.7)
            : hexWithAlpha(lighten(color, 30), 0.6);
      ctx.lineWidth = isHovered ? 2.5 : isConnected ? 2.2 : node.is_primary ? 2 : 1.5;
      ctx.stroke();

      // Inner highlight (glossy effect)
      if (!dim) {
        ctx.beginPath();
        ctx.arc(node.x - r * 0.2, node.y - r * 0.25, r * 0.45, 0, Math.PI * 2);
        ctx.fillStyle = th.gloss;
        ctx.fill();
      }

      // Label
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      if (node.is_primary) {
        // Auto-shrink label to fit inside the node
        const maxW = r * 1.7;
        let fontSize = Math.round(11 * sc);
        let label = node.name.length > 16 ? node.name.slice(0, 15) + "…" : node.name;
        ctx.font = `bold ${fontSize}px Inter, system-ui, sans-serif`;
        while (ctx.measureText(label).width > maxW && fontSize > Math.max(6, Math.round(7 * sc))) {
          fontSize--;
          ctx.font = `bold ${fontSize}px Inter, system-ui, sans-serif`;
        }
        if (ctx.measureText(label).width > maxW) {
          // Still too wide — truncate more aggressively
          while (label.length > 3 && ctx.measureText(label + "…").width > maxW) {
            label = label.slice(0, -1).replace(/…$/, "");
          }
          label = label + "…";
        }
        ctx.fillStyle = dim ? th.primaryLabelDim : th.primaryLabel;
        ctx.fillText(label, node.x, node.y);
      } else {
        const label = node.name.length > 16 ? node.name.slice(0, 15) + "…" : node.name;
        ctx.font = `500 ${Math.round(9 * sc)}px Inter, system-ui, sans-serif`;
        const labelY = node.y + r + Math.round(13 * sc);
        const metrics = ctx.measureText(label);
        const lw = metrics.width + 8 * sc;
        ctx.fillStyle = dim ? th.labelBgDim : th.labelBg;
        ctx.beginPath();
        ctx.roundRect(node.x - lw / 2, labelY - Math.round(7 * sc), lw, Math.round(14 * sc), 4);
        ctx.fill();
        ctx.fillStyle = dim ? th.labelTextDim : th.labelText;
        ctx.fillText(label, node.x, labelY);
      }

      // Commit count badge (star mode) or project count badge (full mode)
      if (r >= 14 && !node.is_primary && !dim) {
        ctx.font = `bold ${Math.round(8 * sc)}px Inter, system-ui, sans-serif`;
        ctx.fillStyle = th.commitBadge;
        const badgeValue = mode === "full" ? String(node.projects.length) : String(node.commits);
        ctx.fillText(badgeValue, node.x, node.y);
      }
    });

  }, []);

  /* ---- Animation loop (physics always on) ---- */
  useEffect(() => {
    if (!network || network.nodes.length === 0) return;

    const W = sizeRef.current.w;
    const H = sizeRef.current.h;
    const cx = W / 2;
    const cy = H / 2;

    const nodes: NetworkNode[] = network.nodes.map((n, i) => {
      const angle = (2 * Math.PI * i) / network.nodes.length;
      const spread = Math.min(W, H) * 0.42;
      const radius = n.is_primary ? 0 : spread + Math.random() * 80;
      return {
        ...n,
        x: cx + Math.cos(angle) * radius + (Math.random() - 0.5) * 30,
        y: cy + Math.sin(angle) * radius + (Math.random() - 0.5) * 30,
        vx: 0,
        vy: 0,
        fx: null,
        fy: null,
      };
    });
    nodesRef.current = nodes;
    edgesRef.current = network.edges;

    const tick = () => {
      simulate();
      draw();
      animRef.current = requestAnimationFrame(tick);
    };
    animRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animRef.current);
  }, [network, simulate, draw]);

  /* ---- Mouse handlers for drag & hover ---- */
  const getCanvasCoords = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);
    const node = hitTest(x, y);
    if (node) {
      dragRef.current = {
        node,
        offsetX: x - node.x,
        offsetY: y - node.y,
        active: true,
        hasMoved: false,
      };
      node.fx = node.x;
      node.fy = node.y;
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);
    const drag = dragRef.current;

    if (drag.active && drag.node) {
      drag.hasMoved = true;
      drag.node.fx = x - drag.offsetX;
      drag.node.fy = y - drag.offsetY;
      drag.node.x = drag.node.fx;
      drag.node.y = drag.node.fy;
    }

    const found = hitTest(x, y);
    hoveredRef.current = found;
    if (found !== hoveredNode) setHoveredNode(found);

    const canvas = canvasRef.current;
    if (canvas) {
      canvas.style.cursor = drag.active ? "grabbing" : found ? "grab" : "default";
    }
  };

  const handleMouseUp = () => {
    const drag = dragRef.current;
    if (drag.node) {
      drag.node.fx = null;
      drag.node.fy = null;
    }
    dragRef.current = { node: null, offsetX: 0, offsetY: 0, active: false, hasMoved: false };
  };

  const handleMouseLeave = () => {
    handleMouseUp();
    hoveredRef.current = null;
    setHoveredNode(null);
    if (canvasRef.current) canvasRef.current.style.cursor = "default";
  };

  if (!network || network.nodes.length <= 1) {
    return (
      <div className="network-empty">
        <p>No collaboration data detected yet.</p>
        <p className="network-empty-hint">
          Make sure your project&apos;s <strong>.git</strong> history is included when you upload a ZIP.
          If you downloaded the ZIP from GitHub, it won&apos;t contain git history &mdash; zip your local clone instead.
          Already-analyzed projects will pick up collaborators automatically on next portfolio load.
        </p>
      </div>
    );
  }

  return (
    <div className="network-graph-container" data-graph-theme={graphTheme}>
      <div className={`network-canvas-wrap ${graphTheme === "light" ? "network-canvas-wrap--light" : ""}`} ref={containerRef}>
        <div className="network-toolbar">
          <div className={`network-mode-radio ${graphTheme === "light" ? "network-mode-radio--light" : ""}`}>
            <button
              className={`network-mode-radio-btn ${graphTheme === "dark" ? "network-mode-radio-btn--active" : ""}`}
              onClick={() => setGraphTheme("dark")}
              title="Dark theme"
            >
              🌙 Dark
            </button>
            <button
              className={`network-mode-radio-btn ${graphTheme === "light" ? "network-mode-radio-btn--active" : ""}`}
              onClick={() => setGraphTheme("light")}
              title="Light theme"
            >
              ☀️ Light
            </button>
          </div>
          <div className={`network-mode-radio ${graphTheme === "light" ? "network-mode-radio--light" : ""}`}>
            <button
              className={`network-mode-radio-btn ${networkMode === "star" ? "network-mode-radio-btn--active" : ""}`}
              onClick={() => { setNetworkMode("star"); setHoveredNode(null); }}
              title="Star view — connections to you only. Node size = commit count."
            >
              ⭐ Star
            </button>
            <button
              className={`network-mode-radio-btn ${networkMode === "full" ? "network-mode-radio-btn--active" : ""}`}
              onClick={() => { setNetworkMode("full"); setHoveredNode(null); }}
              title="Full network — collaborators connected if they share projects. Node size = project breadth."
            >
              🕸️ Network
            </button>
          </div>
        </div>
        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
        />
      </div>
      {/* Info panel below the canvas — never covers the graph */}
      <div className={`network-info-panel ${graphTheme === "light" ? "network-info-panel--light" : ""} ${hoveredNode ? "network-info-panel--active" : ""}`}>
        {hoveredNode ? (
          <>
            <div className="network-info-name">{hoveredNode.name}</div>
            <div className="network-info-commits">
              {networkMode === "full"
                ? `${hoveredNode.projects.length} project${hoveredNode.projects.length !== 1 ? "s" : ""}`
                : `${hoveredNode.commits.toLocaleString()} commits`}
            </div>
            <div className="network-info-projects">
              {hoveredNode.projects.map((p) => (
                <span key={p} className="network-info-project-tag">{p}</span>
              ))}
            </div>
          </>
        ) : (
          <div className="network-info-hint">
            <span className="network-info-hint-icon">👆</span>
            Hover for details &middot; Drag to rearrange &middot; {networkMode === "full" ? "Node size = project breadth" : "Node size = commit count"}
          </div>
        )}
      </div>
      <div className="network-legend">
        <div className="network-stat">
          <span className="network-stat-value">{network.nodes.length}</span>
          <span className="network-stat-label">Contributors</span>
        </div>
        <div className="network-stat">
          <span className="network-stat-value">
            {networkMode === "star"
              ? network.edges.filter(e => !e.is_peer).length
              : network.edges.length}
          </span>
          <span className="network-stat-label">Connections</span>
        </div>
        <div className="network-stat">
          <span className="network-stat-value">
            {networkMode === "full"
              ? network.edges.filter(e => e.is_peer).length
              : network.nodes.reduce((s, n) => s + n.commits, 0).toLocaleString()}
          </span>
          <span className="network-stat-label">
            {networkMode === "full" ? "Peer Links" : "Total Commits"}
          </span>
        </div>
      </div>
    </div>
  );
}

/* Canvas color helpers */
function hexWithAlpha(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function lighten(hex: string, amount: number): string {
  const r = Math.min(255, parseInt(hex.slice(1, 3), 16) + amount);
  const g = Math.min(255, parseInt(hex.slice(3, 5), 16) + amount);
  const b = Math.min(255, parseInt(hex.slice(5, 7), 16) + amount);
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

interface EditState {
  field: "name" | "score" | "dates" | "summary";
  value: string;
  createdAt?: string;
  lastModified?: string;
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
  const navigate = useNavigate();
  const [showFullSummary, setShowFullSummary] = useState(false);
  const [editing, setEditing] = useState<EditState | null>(null);
  const [saving, setSaving] = useState(false);

  const summary = project.summary || "";
  const title = projectName(project);
  const dates = projectDates(project);
  const displayScore = getDisplayScore(project);

  const skills = project.skills || project.technical_keywords || [];
  const metrics = project.metrics || {};
  const scoreSignals = getProjectScoreSignals(project);

  const roles = Array.isArray(metrics.roles)
    ? (metrics.roles as string[]).filter(
        (r) => typeof r === "string" && r.trim().length > 0,
      )
    : [];
  const visibleRoles = roles.slice(0, 3);
  const hiddenRolesCount = Math.max(0, roles.length - visibleRoles.length);

  const scoreOverrideExclusions = Array.isArray(
    project.score_override_exclusions,
  )
    ? project.score_override_exclusions.filter(
        (m) => typeof m === "string" && m.trim().length > 0,
      )
    : [];
  const hasEquationOverride =
    project.score_overridden && scoreOverrideExclusions.length > 0;
  const formattedExclusions = scoreOverrideExclusions.map(formatMetricName);
  const visibleExclusions = formattedExclusions.slice(0, 4);
  const hiddenExclusionsCount = Math.max(
    0,
    formattedExclusions.length - visibleExclusions.length,
  );

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
  const scoreConfigurationSummary = hasEquationOverride
    ? `Adjusted scoring is active for this project. The current score excludes ${formattedExclusions.join(", ")} to better match the project context.`
    : project.score_overridden
      ? "This project is using an adjusted score instead of the default portfolio calculation."
      : "This project is currently using the default portfolio scoring calculation.";
  const scoreExplanationIntro = isGithubProject
    ? "This score summarizes visible evidence from repository activity, implementation scope, testing, maintainability, and documentation."
    : "This score summarizes visible evidence from implementation scope, maintainability, testing, and documentation.";

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

  const startEdit = (field: EditState["field"]) => {
    if (field === "summary") {
      setEditing({ field, value: summary });
    } else if (field === "name") {
      setEditing({ field, value: title });
    } else if (field === "score") {
      setEditing({ field, value: Math.round(getDisplayScore(project) * 100).toString() });
    } else if (field === "dates") {
      setEditing({
        field,
        value: "",
        createdAt: project.created_at || "",
        lastModified: project.last_modified || "",
      });
    }
  };

  const cancelEdit = () => setEditing(null);

  const saveEdit = async () => {
    if (!editing) return;
    setSaving(true);
    try {
      const editData: Record<string, unknown> = {
        project_signature: project.id,
      };
      if (editing.field === "summary") {
        editData.project_summary = editing.value;
      } else if (editing.field === "name") {
        if (!editing.value.trim()) {
          alert("Project name cannot be empty!");
          setSaving(false);
          return;
        }
        editData.project_name = editing.value.trim();
      } else if (editing.field === "score") {
        const parsed = Number(editing.value);
        if (Number.isNaN(parsed) || parsed < 0 || parsed > 100) {
          alert("Score must be a number between 0 and 100.");
          setSaving(false);
          return;
        }
        editData.score_overridden_value = parsed / 100;
      } else if (editing.field === "dates") {
        if (editing.createdAt) editData.created_at = editing.createdAt;
        if (editing.lastModified) editData.last_modified = editing.lastModified;
      }

      const res = await fetch(`${API_BASE_URL}/api/portfolio/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ edits: [editData] }),
      });
      if (!res.ok) {
        const err = (await res.json()) as { detail?: string };
        throw new Error(err.detail || "Failed to save edit");
      }
      setEditing(null);
      await onReload();
    } catch (e) {
      alert(
        `Failed to save: ${e instanceof Error ? e.message : "Unknown error"}`,
      );
    } finally {
      setSaving(false);
    }
  };

  const EditButtons = () => (
    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
      <button
        className="save-edit-btn"
        onClick={() => void saveEdit()}
        disabled={saving}
      >
        {saving ? "Saving..." : "Save"}
      </button>
      <button
        className="cancel-edit-btn"
        onClick={cancelEdit}
        disabled={saving}
      >
        Cancel
      </button>
    </div>
  );

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

      {/* Project title — editable */}
      {editing?.field === "name" ? (
        <div
          className="editable-field active"
          style={{ marginBottom: 12, paddingRight: 140 }}
        >
          <input
            type="text"
            value={editing.value}
            autoFocus
            onChange={(e) => setEditing({ ...editing, value: e.target.value })}
            onKeyDown={(e) => {
              if (e.key === "Enter") void saveEdit();
              if (e.key === "Escape") cancelEdit();
            }}
            style={{
              width: "100%",
              padding: "6px",
              border: "2px solid var(--accent)",
              borderRadius: 4,
              fontFamily: "inherit",
              fontSize: "inherit",
            }}
          />
          <EditButtons />
        </div>
      ) : (
        <div
          className="project-title editable-field"
          style={{ paddingRight: 140 }}
          onClick={() => startEdit("name")}
          title="Click to edit"
        >
          {title}
        </div>
      )}

      {/* Score row — editable */}
      <div className="project-score-row">
        <div className="project-score-main">
          {editing?.field === "score" ? (
            <div className="editable-field active">
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={editing.value}
                autoFocus
                onChange={(e) =>
                  setEditing({ ...editing, value: e.target.value })
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") void saveEdit();
                  if (e.key === "Escape") cancelEdit();
                }}
                style={{
                  width: 110,
                  padding: "4px 6px",
                  border: "2px solid var(--accent)",
                  borderRadius: 4,
                  fontSize: "1.4em",
                  fontWeight: 700,
                }}
              />
              <EditButtons />
            </div>
          ) : (
            <div
              className="project-score-display editable-field"
              onClick={() => startEdit("score")}
              title="Click to edit score"
            >
              {formatScorePercent(displayScore)}
            </div>
          )}
          {project.score_overridden ? (
            <span className="project-score-badge">Overridden</span>
          ) : null}
        </div>
        <button
          type="button"
          className="score-configure-btn portfolio-owner-only"
          onClick={() =>
            navigate(
              `/scoreoverridepage?project=${encodeURIComponent(String(project.id))}&from=portfoliopage`,
            )
          }
        >
          Configure score
        </button>
      </div>

      {/* Score exclusion chips */}
      {hasEquationOverride ? (
        <div className="project-score-config-inline">
          <span className="score-config-label">Excluded Metrics:</span>
          <div className="score-exclusion-chips-inline">
            {visibleExclusions.map((m) => (
              <span key={m} className="score-exclusion-chip">
                {m}
              </span>
            ))}
            {hiddenExclusionsCount > 0 ? (
              <span className="score-exclusion-chip">
                +{hiddenExclusionsCount} more
              </span>
            ) : null}
          </div>
        </div>
      ) : null}
      <details className="project-score-explainer">
        <summary className="project-score-explainer-toggle">
          Why this score?
        </summary>
        <div className="project-score-explainer-content">
          <p className="project-score-explainer-intro">
            {scoreExplanationIntro}
          </p>
          <p className="project-score-explainer-status">
            {scoreConfigurationSummary}
          </p>
          {scoreSignals.length > 0 ? (
            <div className="project-score-signal-list">
              {scoreSignals.map((signal) => (
                <div key={signal.label} className="project-score-signal">
                  <div className="project-score-signal-header">
                    <span className="project-score-signal-name">
                      {signal.label}
                    </span>
                    <span
                      className={`project-score-signal-value project-score-signal-value-${signal.tone}`}
                    >
                      {signal.value}
                    </span>
                  </div>
                  <p className="project-score-signal-copy">
                    {signal.explanation}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="project-score-explainer-note">
              Detailed scoring inputs are limited for this project, so the score
              should be read as a high-level summary only.
            </p>
          )}
          <p className="project-score-explainer-footnote">
            This summary highlights the clearest visible signals in the
            portfolio. The complete scoring formulas are shown in the
            methodology section below.
          </p>
        </div>
      </details>

      {/* Dates — editable */}
      {editing?.field === "dates" ? (
        <div className="editable-field active" style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <label style={{ fontSize: 12, color: "var(--text-secondary)" }}>
              Created:
            </label>
            <input
              type="date"
              value={editing.createdAt || ""}
              onChange={(e) =>
                setEditing({ ...editing, createdAt: e.target.value })
              }
              style={{
                padding: "6px",
                border: "2px solid var(--accent)",
                borderRadius: 4,
              }}
            />
            <label style={{ fontSize: 12, color: "var(--text-secondary)" }}>
              Last Modified:
            </label>
            <input
              type="date"
              value={editing.lastModified || ""}
              onChange={(e) =>
                setEditing({ ...editing, lastModified: e.target.value })
              }
              style={{
                padding: "6px",
                border: "2px solid var(--accent)",
                borderRadius: 4,
              }}
            />
          </div>
          <EditButtons />
        </div>
      ) : (
        <div
          className="project-dates editable-field"
          onClick={() => startEdit("dates")}
          title="Click to edit dates"
        >
          {dates}
        </div>
      )}

      {/* Roles strip */}
      {roles.length > 0 ? (
        <div className="project-role-strip">
          <span className="project-role-label">Roles</span>
          <div className="project-role-inline-tags">
            {visibleRoles.map((role) => (
              <span key={role} className="project-role-tag">
                {role}
              </span>
            ))}
            {hiddenRolesCount > 0 ? (
              <span className="project-role-tag">+{hiddenRolesCount}</span>
            ) : null}
          </div>
        </div>
      ) : null}

      {/* Thumbnail image */}
      {project.thumbnail_url && (
        <div
          className="thumbnail-display"
          style={{ margin: "16px 0", textAlign: "center" }}
        >
          <img
            src={`${API_BASE_URL}${project.thumbnail_url}?cb=${Date.now()}`}
            alt="Project thumbnail"
            className="project-thumbnail"
            crossOrigin="anonymous"
          />
        </div>
      )}

      {/* Summary — editable */}
      <div className="project-summary">
        <h4>📝 Project Summary</h4>
        <div className="summary-content">
          {editing?.field === "summary" ? (
            <div>
              <textarea
                value={editing.value}
                autoFocus
                onChange={(e) =>
                  setEditing({ ...editing, value: e.target.value })
                }
                style={{
                  width: "100%",
                  minHeight: 100,
                  padding: 8,
                  border: "2px solid var(--accent)",
                  borderRadius: 4,
                  fontFamily: "inherit",
                  fontSize: "inherit",
                  resize: "vertical",
                }}
              />
              <EditButtons />
            </div>
          ) : (
            <>
              <p
                className={`summary-text ${!showFullSummary && shouldTruncateSummary(summary) ? "truncated" : ""} editable-field`}
                onClick={() => startEdit("summary")}
                style={
                  !summary
                    ? { color: "var(--text-muted)", fontStyle: "italic" }
                    : {}
                }
              >
                {summary || "Click to add a project summary..."}
              </p>
              {shouldTruncateSummary(summary) && (
                <button
                  className="show-more-btn"
                  onClick={() => setShowFullSummary((v) => !v)}
                >
                  {showFullSummary ? "Show Less" : "Show More"}
                </button>
              )}
            </>
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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<
    Set<string | number>
  >(new Set());
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);

  const loadPortfolio = async (selectedIds?: Array<string | number>) => {
    if (!selectedIds || selectedIds.length === 0) {
      setPortfolio(null);
      return;
    }
    const query =
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

  const downloadPortfolioInteractiveHTML = async () => {
    try {
      const mainContent = document.querySelector(".main-content");
      if (!mainContent) throw new Error("Main content not found");
      if (!portfolio) throw new Error("Portfolio data is not loaded yet");

      const mainClone = mainContent.cloneNode(true) as HTMLElement;
      mainClone
        .querySelectorAll(".dashboard-actions")
        .forEach((el) => el.remove());
      mainClone
        .querySelectorAll(".portfolio-owner-only")
        .forEach((el) => el.remove());
      mainClone
        .querySelectorAll(".page-home-nav")
        .forEach((el) => el.remove());

      // Wire up Show More buttons for the static HTML export
      mainClone
        .querySelectorAll(".show-more-btn")
        .forEach((btn) => {
          btn.setAttribute("onclick", "window.toggleSummary(this)");
        });

      // Remove edit-related attributes that don't apply in exported HTML
      mainClone
        .querySelectorAll(".editable-field")
        .forEach((el) => {
          el.removeAttribute("title");
          el.classList.remove("editable-field");
        });

      // Remove thumbnail upload buttons from exported HTML
      mainClone
        .querySelectorAll(".thumbnail-button-section")
        .forEach((el) => el.remove());

      // Inline thumbnails as data URLs for offline export
      const thumbnailImages = Array.from(
        mainClone.querySelectorAll("img.project-thumbnail"),
      ) as HTMLImageElement[];
      await Promise.allSettled(
        thumbnailImages.map(async (img) => {
          const src = (img.getAttribute("src") || "").split("?")[0];
          if (!src || src.startsWith("data:")) return;
          try {
            const response = await fetch(src, {
              credentials: "same-origin",
              cache: "no-store",
            });
            if (!response.ok) return;
            const blob = await response.blob();
            const dataUrl = await new Promise<string>((resolve, reject) => {
              const reader = new FileReader();
              reader.onloadend = () => resolve(reader.result as string);
              reader.onerror = () =>
                reject(new Error("Failed to read thumbnail"));
              reader.readAsDataURL(blob);
            });
            img.setAttribute("src", dataUrl);
            img.removeAttribute("crossorigin");
          } catch (_) {
            // skip thumbnail if fetch fails
          }
        }),
      );

      // Extract all CSS from loaded stylesheets
      let baseCss = "";
      for (const sheet of Array.from(document.styleSheets)) {
        try {
          for (const rule of Array.from(sheet.cssRules || [])) {
            baseCss += rule.cssText + "\n";
          }
        } catch (_) {
          // cross-origin stylesheets are skipped
        }
      }

      // Prepare the network canvas wrap for interactive JS in the export
      const cloneCanvasWrap = mainClone.querySelector(".network-canvas-wrap");
      if (cloneCanvasWrap) {
        // Remove the React canvas — we'll recreate it via JS in the export
        const cloneCanvas = cloneCanvasWrap.querySelector("canvas");
        if (cloneCanvas) cloneCanvas.remove();
        // Remove the existing toolbar — we'll recreate it in the export script
        const cloneToolbar = cloneCanvasWrap.querySelector(".network-toolbar");
        if (cloneToolbar) cloneToolbar.remove();
        // Add a placeholder div that the export script will target
        const placeholder = document.createElement("div");
        placeholder.id = "networkGraphTarget";
        placeholder.style.width = "100%";
        placeholder.style.minHeight = "400px";
        placeholder.style.borderRadius = "12px";
        placeholder.style.background = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)";
        placeholder.style.border = "1px solid rgba(99, 102, 241, 0.15)";
        placeholder.style.position = "relative";
        cloneCanvasWrap.appendChild(placeholder);
      }

      const exportCss = `
        body { background: var(--primary-bg) !important; margin: 0 !important; }
        .container, .portfolio-layout { display: block !important; height: auto !important; background: transparent !important; }
        .main-content { max-width: 1500px; margin: 0 auto; padding: 32px; overflow: visible !important; }
        .graph-card, .overview-card, .project-card, .analysis-card, .formula-card { break-inside: avoid; }
      `;

      const exportData = JSON.stringify(portfolio).replace(/<\//g, "<\\/");

      const interactiveScript = `
(function() {
  var data = window.__PORTFOLIO_EXPORT_DATA;
  if (!data || typeof Chart === 'undefined') return;

  window.toggleSummary = function(button) {
    var sc = button.closest('.summary-content');
    if (!sc) return;
    var st = sc.querySelector('.summary-text');
    if (!st) return;
    if (!st.classList.contains('truncated')) { st.classList.add('truncated'); button.textContent = 'Show More'; }
    else { st.classList.remove('truncated'); button.textContent = 'Show Less'; }
  };

  function pie(id, d) {
    var c = document.getElementById(id); if (!c) return;
    new Chart(c.getContext('2d'), { type: 'pie', data: { labels: Object.keys(d||{}), datasets: [{ data: Object.values(d||{}), backgroundColor: ['#2d3748','#4a5568','#718096','#a0aec0','#48bb78','#ed8936','#667eea','#764ba2','#f687b3','#9f7aea','#38b2ac','#68d391'], borderColor: '#fff', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#4a5568', font: { size: 12 }, padding: 15, usePointStyle: true } } } } });
  }
  function bar(id, d) {
    var c = document.getElementById(id); if (!c) return;
    new Chart(c.getContext('2d'), { type: 'bar', data: { labels: Object.keys(d||{}), datasets: [{ data: Object.values(d||{}), backgroundColor: '#2d3748', borderColor: '#4a5568', borderWidth: 1, borderRadius: 4 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 } } }, x: { grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 } } } } } });
  }
  function hbar(id, d) {
    var c = document.getElementById(id); if (!c) return;
    new Chart(c.getContext('2d'), { type: 'bar', data: { labels: Object.keys(d||{}), datasets: [{ data: Object.values(d||{}), backgroundColor: '#4a5568', borderColor: '#2d3748', borderWidth: 1, borderRadius: 4 }] }, options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 } } }, y: { grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 } } } } } });
  }
  function line(id, d) {
    var c = document.getElementById(id); if (!c) return;
    var s = Object.entries(d||{}).sort(); new Chart(c.getContext('2d'), { type: 'line', data: { labels: s.map(function(e){return e[0];}), datasets: [{ label: 'Activity', data: s.map(function(e){return e[1];}), borderColor: '#2d3748', backgroundColor: 'rgba(45,55,72,0.1)', fill: true, tension: 0.4, borderWidth: 3, pointBackgroundColor: '#2d3748', pointBorderColor: '#fff', pointBorderWidth: 2, pointRadius: 5 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 }, stepSize: 0.5 }, title: { display: true, text: 'Activity Level', color: '#4a5568', font: { size: 12, weight: 'bold' } } }, x: { grid: { color: '#e2e8f0' }, ticks: { color: '#4a5568', font: { size: 11 } } } } } });
  }

  var g = data.graphs || {};
  pie('languageChart', g.language_distribution || {});
  bar('complexityChart', { 'Small (<1000)': (g.complexity_distribution||{}).distribution?.small||0, 'Medium (1000-3000)': (g.complexity_distribution||{}).distribution?.medium||0, 'Large (>3000)': (g.complexity_distribution||{}).distribution?.large||0 });
  bar('scoreChart', { 'Excellent (90-100%)': (g.score_distribution||{}).distribution?.excellent||0, 'Good (80-89%)': (g.score_distribution||{}).distribution?.good||0, 'Fair (70-79%)': (g.score_distribution||{}).distribution?.fair||0, 'Poor (<70%)': (g.score_distribution||{}).distribution?.poor||0 });
  line('activityChart', g.monthly_activity || {});
  hbar('skillsChart', g.top_skills || {});
  var t = data.project_type_analysis || {};
  bar('projectTypeChart', { 'GitHub Projects': (t.github||{}).count||0, 'Local Projects': (t.local||{}).count||0 });
})();
      `;

      const networkData = portfolio?.collaboration_network
        ? JSON.stringify(portfolio.collaboration_network).replace(/<\//g, "<\\/")
        : "null";

      const activeGraphTheme = document.querySelector('.network-graph-container[data-graph-theme]')?.getAttribute('data-graph-theme') || 'dark';

      const networkScript = `
(function() {
  var NET = ${networkData};
  if (!NET || !NET.nodes || NET.nodes.length <= 1) return;
  var target = document.getElementById('networkGraphTarget');
  if (!target) return;

  var COLORS = ["#6366f1","#8b5cf6","#ec4899","#f43f5e","#f97316","#eab308","#22c55e","#14b8a6","#06b6d4","#3b82f6"];
  var THEME_KEY = '${activeGraphTheme}';
  var THEMES = {
    dark: {
      primaryGrad0:'#334155', primaryGrad1:'#0f172a', primaryLabel:'#fff', primaryLabelDim:'rgba(255,255,255,0.4)',
      labelBg:'rgba(30,41,59,0.7)', labelBgDim:'rgba(30,41,59,0.3)', labelText:'#e2e8f0', labelTextDim:'rgba(255,255,255,0.3)',
      gloss:'rgba(255,255,255,0.13)', commitBadge:'rgba(255,255,255,0.9)', ringHi:'#fff',
      canvasBg:'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', canvasShadow:'inset 0 1px 30px rgba(0,0,0,0.3)',
      badgeBg:function(a){return 'rgba(30,41,59,'+a+')';},
      badgeStroke:function(hi){return hi?'rgba(99,102,241,0.6)':'rgba(99,102,241,0.2)';},
      badgeText:function(hi){return hi?'#fff':'rgba(255,255,255,0.7)';},
      nodeColorPrimary:'#1e293b',
      panelBg:'#1e293b', panelBorder:'#334155', panelActiveBg:'#0f172a',
      infoName:'#f1f5f9', infoCommits:'#a78bfa', infoTag:'#38bdf8',
      infoTagBg:'rgba(56,189,248,0.1)', infoTagBorder:'rgba(56,189,248,0.2)', infoHint:'#e2e8f0',
      toggleBg:'rgba(30,41,59,0.7)', toggleBorder:'rgba(99,102,241,0.25)', toggleText:'#e2e8f0',
      toggleHoverBg:'rgba(99,102,241,0.25)', toggleActiveBg:'rgba(99,102,241,0.35)', toggleActiveBorder:'rgba(99,102,241,0.65)'
    },
    light: {
      primaryGrad0:'#e2e8f0', primaryGrad1:'#94a3b8', primaryLabel:'#1e293b', primaryLabelDim:'rgba(30,41,59,0.35)',
      labelBg:'rgba(255,255,255,0.85)', labelBgDim:'rgba(255,255,255,0.4)', labelText:'#334155', labelTextDim:'rgba(51,65,85,0.35)',
      gloss:'rgba(255,255,255,0.25)', commitBadge:'#1e293b', ringHi:'#1e293b',
      canvasBg:'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)', canvasShadow:'inset 0 1px 30px rgba(0,0,0,0.04)',
      badgeBg:function(a){return 'rgba(255,255,255,'+a+')';},
      badgeStroke:function(hi){return hi?'rgba(99,102,241,0.7)':'rgba(99,102,241,0.25)';},
      badgeText:function(hi){return hi?'#1e293b':'rgba(30,41,59,0.6)';},
      nodeColorPrimary:'#cbd5e1',
      panelBg:'#f1f5f9', panelBorder:'#cbd5e1', panelActiveBg:'#e2e8f0',
      infoName:'#1e293b', infoCommits:'#7c3aed', infoTag:'#0284c7',
      infoTagBg:'rgba(2,132,199,0.1)', infoTagBorder:'rgba(2,132,199,0.2)', infoHint:'#475569',
      toggleBg:'rgba(255,255,255,0.8)', toggleBorder:'rgba(99,102,241,0.2)', toggleText:'#334155',
      toggleHoverBg:'rgba(255,255,255,0.95)', toggleActiveBg:'rgba(99,102,241,0.15)', toggleActiveBorder:'rgba(99,102,241,0.5)'
    }
  };
  var T = THEMES[THEME_KEY] || THEMES.dark;

  /* Helpers */
  function ha(h,a){var r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16);return 'rgba('+r+','+g+','+b+','+a+')';}
  function lt(h,n){var r=Math.min(255,parseInt(h.slice(1,3),16)+n),g=Math.min(255,parseInt(h.slice(3,5),16)+n),b=Math.min(255,parseInt(h.slice(5,7),16)+n);return '#'+r.toString(16).padStart(2,'0')+g.toString(16).padStart(2,'0')+b.toString(16).padStart(2,'0');}
  function nc(n,i){return n.is_primary?T.nodeColorPrimary:COLORS[i%COLORS.length];}

  /* State */
  var mode = 'star'; /* 'star' or 'full' */
  var sc = 1;

  function nr(n) {
    if (n.is_primary) return 32 * sc;
    if (mode === 'full') {
      var pc = n.projects.length;
      return (16 + Math.min(pc, 8) * 2.5) * sc;
    }
    return (14 + Math.min(n.commits, 80) * 0.18) * sc;
  }

  function activeEdges() {
    return mode === 'star' ? NET.edges.filter(function(e){return !e.is_peer;}) : NET.edges;
  }

  /* Canvas setup */
  target.style.position = 'relative';
  var canvas = document.createElement('canvas');
  canvas.style.width='100%'; canvas.style.borderRadius='12px'; canvas.style.display='block'; canvas.style.cursor='default';
  canvas.style.background=T.canvasBg; canvas.style.boxShadow=T.canvasShadow; canvas.style.userSelect='none';
  target.appendChild(canvas);

  /* Toolbar */
  var toolbar = document.createElement('div');
  toolbar.style.cssText='position:absolute;top:10px;right:10px;z-index:10;display:flex;gap:6px;align-items:center;';
  target.appendChild(toolbar);

  var btnBase = 'height:30px;padding:0 10px;border:none;background:transparent;font-size:12px;font-weight:500;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px;white-space:nowrap;transition:background 0.2s,color 0.2s;';
  var radioStyle = 'display:flex;border-radius:8px;border:1px solid '+T.toggleBorder+';background:'+T.toggleBg+';backdrop-filter:blur(4px);overflow:hidden;';
  var inactiveColor = THEME_KEY === 'dark' ? 'rgba(226,232,240,0.6)' : 'rgba(51,65,85,0.5)';
  var activeColor = THEME_KEY === 'dark' ? '#fff' : '#1e293b';

  /* Mode radio */
  var modeRadio = document.createElement('div');
  modeRadio.style.cssText = radioStyle;
  toolbar.appendChild(modeRadio);

  var starBtn = document.createElement('button');
  starBtn.textContent = '\\u2B50 Star';
  starBtn.style.cssText = btnBase + 'border-right:1px solid '+T.toggleBorder+';';
  modeRadio.appendChild(starBtn);

  var netBtn = document.createElement('button');
  netBtn.textContent = '\\ud83d\\udd78\\ufe0f Network';
  netBtn.style.cssText = btnBase;
  modeRadio.appendChild(netBtn);

  function updateRadio() {
    starBtn.style.background = mode === 'star' ? T.toggleActiveBg : 'transparent';
    starBtn.style.color = mode === 'star' ? activeColor : inactiveColor;
    starBtn.style.fontWeight = mode === 'star' ? '600' : '500';
    netBtn.style.background = mode === 'full' ? T.toggleActiveBg : 'transparent';
    netBtn.style.color = mode === 'full' ? activeColor : inactiveColor;
    netBtn.style.fontWeight = mode === 'full' ? '600' : '500';
  }
  updateRadio();

  starBtn.addEventListener('click', function() { mode = 'star'; updateRadio(); updateLegend(); updateInfo(hovered); });
  netBtn.addEventListener('click', function() { mode = 'full'; updateRadio(); updateLegend(); updateInfo(hovered); });

  var W = target.clientWidth, H = Math.max(400, Math.floor(target.clientWidth * 0.48));
  var dpr = window.devicePixelRatio || 1;
  canvas.width = W * dpr; canvas.height = H * dpr; canvas.style.height = H + 'px';
  var ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  var cx = W / 2, cy = H / 2;

  /* Compute scale */
  function computeScale() {
    var raw = Math.min(W, H) / 480;
    var adj = Math.max(0.8, Math.min(1.5, 8 / Math.max(NET.nodes.length, 1)));
    sc = Math.max(0.9, Math.min(1.7, raw * adj));
  }
  computeScale();

  /* Nodes init */
  var nodes = NET.nodes.map(function(n, i) {
    var a = (2 * Math.PI * i) / NET.nodes.length;
    var spread = Math.min(W, H) * 0.42;
    var r = n.is_primary ? 0 : spread + Math.random() * 80;
    return { id:n.id, name:n.name, commits:n.commits, is_primary:n.is_primary, projects:n.projects,
      x:cx+Math.cos(a)*r+(Math.random()-0.5)*30, y:cy+Math.sin(a)*r+(Math.random()-0.5)*30,
      vx:0, vy:0, fx:null, fy:null };
  });

  var hovered = null, drag = { node:null, ox:0, oy:0, active:false };
  var infoPanel = target.closest('.network-graph-container').querySelector('.network-info-panel');

  /* Legend updates */
  var legendContainer = target.closest('.network-graph-container').querySelector('.network-legend');
  function updateLegend() {
    if (!legendContainer) return;
    var eds = activeEdges();
    var peerCount = NET.edges.filter(function(e){return e.is_peer;}).length;
    var totalCommits = NET.nodes.reduce(function(s,n){return s+n.commits;},0);
    var stats = legendContainer.querySelectorAll('.network-stat');
    if (stats.length >= 3) {
      stats[1].querySelector('.network-stat-value').textContent = eds.length;
      if (mode === 'full') {
        stats[2].querySelector('.network-stat-value').textContent = peerCount;
        stats[2].querySelector('.network-stat-label').textContent = 'Peer Links';
      } else {
        stats[2].querySelector('.network-stat-value').textContent = totalCommits.toLocaleString();
        stats[2].querySelector('.network-stat-label').textContent = 'Total Commits';
      }
    }
  }

  function hitTest(mx,my){for(var i=nodes.length-1;i>=0;i--){var n=nodes[i],r=nr(n)+4;if((n.x-mx)*(n.x-mx)+(n.y-my)*(n.y-my)<=r*r)return n;}return null;}

  /* Physics */
  function simulate() {
    var isFull = mode === 'full';
    var eds = activeEdges();
    computeScale();
    var repulsion = (isFull ? 28000 : 12000) * sc;
    var attraction = isFull ? 0.001 : 0.003;
    var centerPull = isFull ? 0.004 : 0.008;
    var damping = 0.82;

    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var dx = nodes[j].x - nodes[i].x, dy = nodes[j].y - nodes[i].y;
        var d = Math.sqrt(dx*dx + dy*dy) || 1;
        var f = repulsion / (d * d);
        var fx = dx/d*f, fy = dy/d*f;
        nodes[i].vx -= fx; nodes[i].vy -= fy;
        nodes[j].vx += fx; nodes[j].vy += fy;
      }
    }

    var nm = {}; nodes.forEach(function(n){ nm[n.id] = n; });
    eds.forEach(function(e) {
      var s = nm[e.source], t = nm[e.target]; if (!s||!t) return;
      var dx = t.x-s.x, dy = t.y-s.y, dist = Math.sqrt(dx*dx+dy*dy) || 1;
      var idealLen = (isFull ? (e.is_peer ? 350 : 280) : 220) * sc;
      var disp = dist - idealLen;
      var f = disp * attraction * (1 + e.weight * (isFull ? 0.1 : 0.3));
      var fx = dx/dist*f, fy = dy/dist*f;
      s.vx += fx; s.vy += fy; t.vx -= fx; t.vy -= fy;
    });

    nodes.forEach(function(n){ n.vx += (cx-n.x)*centerPull; n.vy += (cy-n.y)*centerPull; });

    /* Overlap repulsion */
    var minGap = (isFull ? 60 : 30) * sc;
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var ri = nr(nodes[i]), rj = nr(nodes[j]);
        var minD = ri + rj + minGap;
        var dx = nodes[j].x - nodes[i].x, dy = nodes[j].y - nodes[i].y;
        var dist = Math.sqrt(dx*dx+dy*dy) || 1;
        if (dist < minD) {
          var push = (minD - dist) * 0.15;
          var px = dx/dist*push, py = dy/dist*push;
          nodes[i].vx -= px; nodes[i].vy -= py;
          nodes[j].vx += px; nodes[j].vy += py;
        }
      }
    }

    var pad = 60;
    nodes.forEach(function(n) {
      if (n.fx !== null) { n.x=n.fx; n.y=n.fy; n.vx=0; n.vy=0; }
      else { n.vx*=damping; n.vy*=damping; n.x+=n.vx; n.y+=n.vy;
        n.x=Math.max(pad,Math.min(W-pad,n.x)); n.y=Math.max(pad,Math.min(H-pad,n.y)); }
    });
  }

  /* Draw */
  function draw() {
    ctx.clearRect(0, 0, W, H);
    var eds = activeEdges();
    var nm = {}; nodes.forEach(function(n){ nm[n.id] = n; });
    var connSet = {};
    if (hovered) { connSet[hovered.id] = true; eds.forEach(function(e){ if(e.source===hovered.id||e.target===hovered.id){connSet[e.source]=true;connSet[e.target]=true;} }); }

    /* Edges */
    eds.forEach(function(e) {
      var s = nm[e.source], t = nm[e.target]; if (!s||!t) return;
      var hi = hovered && (hovered.id===e.source || hovered.id===e.target);
      var isPeer = !!e.is_peer;
      var si = nodes.indexOf(s), ti = nodes.indexOf(t);
      var al = hi ? 0.65 : hovered ? (isPeer ? 0.03 : 0.06) : isPeer ? 0.09 : 0.15 + e.weight * 0.04;
      var grad = ctx.createLinearGradient(s.x,s.y,t.x,t.y);
      grad.addColorStop(0, ha(nc(s,si), al)); grad.addColorStop(1, ha(nc(t,ti), al));
      ctx.beginPath(); ctx.moveTo(s.x,s.y); ctx.lineTo(t.x,t.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = hi ? 2.5+e.weight*0.5 : isPeer ? 0.5+e.weight*0.15 : 0.8+e.weight*0.25;
      if (isPeer) { ctx.setLineDash([6*sc, 4*sc]); } else { ctx.setLineDash([]); }
      ctx.stroke(); ctx.setLineDash([]);

      /* Badge on hovered edges only */
      if (hi) {
        var mx2 = (s.x+t.x)/2, my2 = (s.y+t.y)/2;
        ctx.fillStyle = T.badgeBg(0.92); ctx.beginPath(); ctx.arc(mx2,my2,Math.round(9*sc),0,Math.PI*2); ctx.fill();
        ctx.strokeStyle = T.badgeStroke(true); ctx.lineWidth = 1; ctx.stroke();
        ctx.fillStyle = T.badgeText(true); ctx.font = 'bold '+Math.round(8*sc)+'px Inter,system-ui,sans-serif';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(e.projects.length), mx2, my2);
      }
    });

    /* Nodes */
    nodes.forEach(function(node, i) {
      var r = nr(node), col = nc(node, i);
      var isH = hovered && hovered.id === node.id;
      var isConn = hovered && connSet[node.id];
      var dim = hovered && !isH && !isConn && !drag.active;

      if (isH || isConn || node.is_primary) {
        var gs = (isH ? 10 : isConn ? 8 : 6) * sc;
        ctx.beginPath(); ctx.arc(node.x, node.y, r+gs, 0, Math.PI*2);
        var gl = ctx.createRadialGradient(node.x,node.y,r*0.5,node.x,node.y,r+gs+4);
        gl.addColorStop(0, ha(col, isH?0.35:isConn?0.28:0.18)); gl.addColorStop(1, ha(col, 0));
        ctx.fillStyle = gl; ctx.fill();
      }

      ctx.beginPath(); ctx.arc(node.x,node.y,r,0,Math.PI*2);
      var bg = ctx.createRadialGradient(node.x-r*0.3,node.y-r*0.3,r*0.1,node.x,node.y,r);
      if (node.is_primary) { bg.addColorStop(0,T.primaryGrad0); bg.addColorStop(1,T.primaryGrad1); }
      else { bg.addColorStop(0, lt(col,20)); bg.addColorStop(1, col); }
      ctx.fillStyle = dim ? ha(col,0.35) : bg; ctx.fill();
      ctx.strokeStyle = dim ? ha(col,0.2) : isH ? T.ringHi : isConn ? ha(T.ringHi,0.7) : ha(lt(col,30),0.6);
      ctx.lineWidth = isH ? 2.5 : isConn ? 2.2 : node.is_primary ? 2 : 1.5; ctx.stroke();

      if (!dim) { ctx.beginPath(); ctx.arc(node.x-r*0.2,node.y-r*0.25,r*0.45,0,Math.PI*2); ctx.fillStyle=T.gloss; ctx.fill(); }

      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (node.is_primary) {
        var maxW = r*1.7; var fs = Math.round(11*sc);
        var lbl = node.name.length>16 ? node.name.slice(0,15)+'\\u2026' : node.name;
        ctx.font = 'bold '+fs+'px Inter,system-ui,sans-serif';
        while (ctx.measureText(lbl).width > maxW && fs > Math.max(6, Math.round(7*sc))) { fs--; ctx.font='bold '+fs+'px Inter,system-ui,sans-serif'; }
        ctx.fillStyle = dim ? T.primaryLabelDim : T.primaryLabel;
        ctx.fillText(lbl, node.x, node.y);
      } else {
        var lbl = node.name.length>16 ? node.name.slice(0,15)+'\\u2026' : node.name;
        ctx.font = '500 '+Math.round(9*sc)+'px Inter,system-ui,sans-serif';
        var ly = node.y + r + Math.round(13*sc);
        var m = ctx.measureText(lbl); var lw = m.width + 8*sc;
        ctx.fillStyle = dim ? T.labelBgDim : T.labelBg;
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(node.x-lw/2,ly-Math.round(7*sc),lw,Math.round(14*sc),4);
        else ctx.rect(node.x-lw/2,ly-Math.round(7*sc),lw,Math.round(14*sc));
        ctx.fill();
        ctx.fillStyle = dim ? T.labelTextDim : T.labelText;
        ctx.fillText(lbl, node.x, ly);
      }

      /* Badge inside node */
      if (r >= 14 && !node.is_primary && !dim) {
        ctx.font = 'bold '+Math.round(8*sc)+'px Inter,system-ui,sans-serif';
        ctx.fillStyle = T.commitBadge;
        var val = mode === 'full' ? String(node.projects.length) : String(node.commits);
        ctx.fillText(val, node.x, node.y);
      }
    });
  }

  function updateInfo(n) {
    if (!infoPanel) return;
    if (n) {
      infoPanel.className = 'network-info-panel network-info-panel--active';
      infoPanel.style.background = T.panelActiveBg; infoPanel.style.borderColor = 'rgba(99,102,241,0.35)';
      var commitLabel = mode === 'full'
        ? n.projects.length + ' project' + (n.projects.length !== 1 ? 's' : '')
        : n.commits.toLocaleString() + ' commits';
      var h = '<div class="network-info-name" style="color:'+T.infoName+'">'+n.name+'</div>';
      h += '<div class="network-info-commits" style="color:'+T.infoCommits+'">'+commitLabel+'</div>';
      h += '<div class="network-info-projects">';
      n.projects.forEach(function(p){ h += '<span class="network-info-project-tag" style="color:'+T.infoTag+';background:'+T.infoTagBg+';border-color:'+T.infoTagBorder+'">'+p+'</span>'; });
      h += '</div>'; infoPanel.innerHTML = h;
    } else {
      infoPanel.className = 'network-info-panel';
      infoPanel.style.background = T.panelBg; infoPanel.style.borderColor = T.panelBorder;
      var hint = 'Hover for details \\u00b7 Drag to rearrange \\u00b7 ' + (mode === 'full' ? 'Node size = project breadth' : 'Node size = commit count');
      infoPanel.innerHTML = '<div class="network-info-hint" style="color:'+T.infoHint+'"><span class="network-info-hint-icon">\\ud83d\\udc46</span>'+hint+'</div>';
    }
  }

  function tick() { simulate(); draw(); requestAnimationFrame(tick); }
  updateInfo(null); updateLegend();
  requestAnimationFrame(tick);

  canvas.addEventListener('mousedown', function(e) {
    var r = canvas.getBoundingClientRect(); var mx = e.clientX-r.left, my = e.clientY-r.top;
    var n = hitTest(mx,my);
    if (n) { drag = {node:n, ox:mx-n.x, oy:my-n.y, active:true}; n.fx=n.x; n.fy=n.y; }
  });
  canvas.addEventListener('mousemove', function(e) {
    var r = canvas.getBoundingClientRect(); var mx = e.clientX-r.left, my = e.clientY-r.top;
    if (drag.active && drag.node) { drag.node.fx=mx-drag.ox; drag.node.fy=my-drag.oy; drag.node.x=drag.node.fx; drag.node.y=drag.node.fy; }
    var f = hitTest(mx,my); if (f !== hovered) { hovered = f; updateInfo(f); }
    canvas.style.cursor = drag.active ? 'grabbing' : f ? 'grab' : 'default';
  });
  canvas.addEventListener('mouseup', function() { if(drag.node){drag.node.fx=null;drag.node.fy=null;} drag={node:null,ox:0,oy:0,active:false}; });
  canvas.addEventListener('mouseleave', function() { if(drag.node){drag.node.fx=null;drag.node.fy=null;} drag={node:null,ox:0,oy:0,active:false}; hovered=null; updateInfo(null); canvas.style.cursor='default'; });

  window.addEventListener('resize', function() {
    W=target.clientWidth; H=Math.max(400,Math.floor(W*0.48)); cx=W/2; cy=H/2;
    canvas.width=W*dpr; canvas.height=H*dpr; canvas.style.height=H+'px';
    ctx.setTransform(dpr,0,0,dpr,0,0); computeScale();
  });
})();
      `;

      const exportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Portfolio Dashboard</title>
  <style>${baseCss}\n${exportCss}</style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
${mainClone.outerHTML}
<script>window.__PORTFOLIO_EXPORT_DATA = ${exportData};</script>
<script>${interactiveScript}</script>
<script>${networkScript}</script>
</body>
</html>`;

      const blob = new Blob([exportHtml], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const timestamp = new Date()
        .toISOString()
        .slice(0, 19)
        .replace(/[T:]/g, "-");
      a.href = url;
      a.download = `portfolio-interactive-${timestamp}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to export portfolio HTML:", err);
      alert("Failed to download interactive portfolio HTML. Please try again.");
    }
  };

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
    const src = (portfolio?.projects || []).slice();
    return src
      .sort((a, b) => getDisplayScore(b) - getDisplayScore(a))
      .slice(0, 6);
  }, [portfolio?.projects]);

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
    let totalCommits = 0;
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
      totalCommits += metrics.total_commits || 0;
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
      totalCommits,
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
        <div className="sidebar-header">
          <div className="sidebar-title-row">
            <h2>Projects</h2>
            <span className="sidebar-count">
              {selectedProjects.size}/{allProjects.length}
            </span>
          </div>
          <button
            className="select-all-btn"
            onClick={() => void toggleAllProjects()}
          >
            {allProjects.length > 0 &&
            selectedProjects.size === allProjects.length
              ? "Deselect All"
              : "Select All"}
          </button>
        </div>
        <div className="project-list">
          {allProjects.length === 0 ? (
            <div className="project-list-empty">
              No projects found
            </div>
          ) : (
            allProjects.map((p) => {
              const checked = selectedProjects.has(p.id);
              const score = getDisplayScore(p);
              const scoreClass =
                score >= 0.7
                  ? "score-high"
                  : score >= 0.4
                    ? "score-mid"
                    : "score-low";
              return (
                <div
                  key={String(p.id)}
                  className={`project-item ${checked ? "selected" : ""}`}
                  onClick={() => void toggleProject(p.id)}
                  title={sidebarProjectName(p)}
                >
                  <span className="project-check">✓</span>
                  <span className="project-name">{sidebarProjectName(p)}</span>
                  <span className={`project-score ${scoreClass}`}>
                    {formatScorePercent(score)}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
      <div className="main-content">
        <div className="dashboard-header">
          <div className="dashboard-header-text">
            <div className="page-home-nav" aria-label="Page navigation">
              <button
                type="button"
                className="page-home-link"
                onClick={() => navigate("/hubpage")}
              >
                Home
              </button>
              <span className="page-home-separator">›</span>
              <span className="page-home-current">Portfolio</span>
            </div>
            <h1>🎯 Portfolio Dashboard</h1>
            <p className="dashboard-subtitle">
              Comprehensive analysis of your development work
            </p>
          </div>
          <div className="dashboard-actions">
            <button
              className="download-html-btn"
              onClick={() => void downloadPortfolioInteractiveHTML()}
              disabled={selectedProjects.size === 0}
            >
              ⚡ Download Interactive HTML
            </button>
          </div>
        </div>

        {portfolio?.user && <UserProfileCard user={portfolio.user} />}

        <div className="overview-cards" id="overviewCards">
          <div className="overview-card">
            <div className="overview-card-value">
              {portfolio?.overview?.total_projects ?? 0}
            </div>
            <div className="overview-card-label">Total Projects</div>
          </div>
          <div className="overview-card">
            <div className="overview-card-value">
              {formatScorePercent(Number(portfolio?.overview?.avg_score || 0))}
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
              <PieChart
                data={graphs.language_distribution}
                canvasId="languageChart"
              />
            </div>
          </div>
          <div className="graph-card">
            <h3>📈 Project Complexity</h3>
            <div className="chart-container">
              <BarChart data={complexity} canvasId="complexityChart" />
            </div>
          </div>
          <div className="graph-card">
            <h3>🏆 Score Distribution</h3>
            <div className="chart-container">
              <BarChart data={scoreDist} canvasId="scoreChart" />
            </div>
          </div>
          <div className="graph-card">
            <h3>📅 Monthly Activity</h3>
            <div className="chart-container">
              <LineChart
                data={graphs.monthly_activity}
                canvasId="activityChart"
              />
            </div>
          </div>
          <div className="graph-card">
            <h3>🛠️ Top Skills</h3>
            <div className="chart-container small">
              <HorizontalBarChart
                data={graphs.top_skills}
                canvasId="skillsChart"
              />
            </div>
          </div>
          <div className="graph-card">
            <h3>⚖️ GitHub vs Local</h3>
            <div className="chart-container small">
              <BarChart data={projectType} canvasId="projectTypeChart" />
            </div>
          </div>
        </div>

        <div className="activity-heatmap-section">
          <h2 className="section-title">🔥 Activity Heatmap</h2>
          <ActivityHeatmap
            dailyActivity={graphs.daily_activity}
            monthlyActivity={graphs.monthly_activity}
            projects={portfolio?.projects}
          />
        </div>

        <div className="network-section">
          <h2 className="section-title">🤝 Collaboration Network</h2>
          <CollaborationNetwork
            network={portfolio?.collaboration_network}
          />
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
                  {analysis.githubProjects > 0 && (
                    <div className="analysis-item">
                      <span className="analysis-label">Total Commits:</span>{" "}
                      <span className="analysis-value">
                        {analysis.totalCommits.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {analysis.localProjects > 0 && (
                    <>
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
                    </>
                  )}
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
