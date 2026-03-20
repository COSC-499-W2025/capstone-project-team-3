import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
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
  const hasContacts = !!(githubLink || user.email);

  return (
    <div className="profile-hero">
      <div className="profile-avatar" style={{ background: avatarBg }}>
        {initials}
      </div>

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
  }, [labels, values]);

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
  }, [labels, values]);

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
  }, [labels, values]);

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
  }, [labels, values]);

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

  const start = new Date(today);
  start.setDate(start.getDate() - 364);

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
                    className={`activity-cell activity-cell-level-${cell.level}`}
                    title={`${formatHeatmapDate(cell.date)} · ${cell.value.toFixed(2)} activity signal`}
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
      setEditing({ field, value: getDisplayScore(project).toFixed(2) });
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
        if (Number.isNaN(parsed) || parsed < 0 || parsed > 1) {
          alert("Score must be a number between 0 and 1.");
          setSaving(false);
          return;
        }
        editData.score_overridden_value = parsed;
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
                title="Click to edit"
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
                    Score: {formatScorePercent(getDisplayScore(p))}
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
            >
              ⚡ Download Interactive HTML
            </button>
          </div>
        </div>

        {portfolio?.user && <UserProfileCard user={portfolio.user} />}

        <div className="overview-cards" id="overviewCards">
          <div className="overview-card">
            <div className="overview-card-value">
              {portfolio?.overview?.total_projects ?? allProjects.length}
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
