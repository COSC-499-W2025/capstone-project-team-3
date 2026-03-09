import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

interface ErrorPayload {
  detail?: string;
}

async function buildRequestError(res: Response): Promise<Error> {
  let detail = res.statusText || `HTTP ${res.status}`;
  try {
    const body = (await res.json()) as ErrorPayload;
    if (typeof body?.detail === "string" && body.detail.trim().length > 0) {
      detail = body.detail;
    }
  } catch {
    // Ignore JSON parse errors and fallback to status text.
  }
  return new Error(`Request failed (${res.status}): ${detail}`);
}

function encodeProjectId(projectId: string): string {
  return encodeURIComponent(projectId);
}

export interface Project {
  id: string;
  name: string;
  score: number;
  score_original?: number;
  score_overridden?: boolean;
  score_overridden_value?: number | null;
  score_override_exclusions?: string[];
  skills: string[];
  date_added: string;
}

export interface ScoreBreakdownMetric {
  raw: number;
  cap: number;
  normalized: number;
  weight: number;
  contribution: number;
}

export interface ScoreBreakdown {
  project_signature: string;
  name: string;
  score: number;
  score_original: number;
  score_overridden: boolean;
  score_overridden_value: number | null;
  exclude_metrics: string[];
  breakdown: {
    code: {
      type: "git" | "non_git";
      metrics: Record<string, ScoreBreakdownMetric>;
      subtotal: number;
    };
    non_code: {
      metrics: Record<string, ScoreBreakdownMetric>;
      subtotal: number;
    };
    blend: {
      code_percentage: number;
      non_code_percentage: number;
      code_lines: number;
      doc_word_count: number;
      doc_line_equiv: number;
    };
    final_score: number;
  };
}

export interface OverridePreview {
  project_signature: string;
  name: string;
  exclude_metrics: string[];
  current_score: number;
  score_original: number;
  preview_score: number;
  breakdown: ScoreBreakdown["breakdown"];
}

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/api/projects`, { method: "GET" });
  if (!res.ok) throw await buildRequestError(res);
  return res.json();
}

export async function getScoreBreakdown(projectId: string): Promise<ScoreBreakdown> {
  const encodedProjectId = encodeProjectId(projectId);
  const res = await fetch(`${API_BASE}/api/projects/${encodedProjectId}/score-breakdown`);
  if (!res.ok) throw await buildRequestError(res);
  return res.json();
}

export async function previewScoreOverride(
  projectId: string,
  excludeMetrics: string[]
): Promise<OverridePreview> {
  const encodedProjectId = encodeProjectId(projectId);
  const res = await fetch(`${API_BASE}/api/projects/${encodedProjectId}/score-override/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exclude_metrics: excludeMetrics }),
  });
  if (!res.ok) throw await buildRequestError(res);
  return res.json();
}

export async function applyScoreOverride(
  projectId: string,
  excludeMetrics: string[]
): Promise<ScoreBreakdown> {
  const encodedProjectId = encodeProjectId(projectId);
  const res = await fetch(`${API_BASE}/api/projects/${encodedProjectId}/score-override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ exclude_metrics: excludeMetrics }),
  });
  if (!res.ok) throw await buildRequestError(res);
  return res.json();
}

export async function clearScoreOverride(projectId: string): Promise<void> {
  const encodedProjectId = encodeProjectId(projectId);
  const res = await fetch(`${API_BASE}/api/projects/${encodedProjectId}/score-override/clear`, {
    method: "POST",
  });
  if (!res.ok) throw await buildRequestError(res);
}
