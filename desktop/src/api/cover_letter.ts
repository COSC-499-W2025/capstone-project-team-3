import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export const MOTIVATION_OPTIONS = [
  { key: "strong_company_culture", label: "Strong Company Culture" },
  { key: "personal_growth", label: "Personal Growth & Career Advancement" },
  { key: "meaningful_work", label: "Meaningful Work / Company Mission" },
  { key: "reputation_stability", label: "Reputation & Stability" },
  { key: "innovation", label: "Innovation & Cutting-Edge Technology" },
  { key: "work_life_balance", label: "Work-Life Balance" },
  { key: "social_impact", label: "Social Impact" },
  { key: "compensation", label: "Competitive Compensation & Benefits" },
  { key: "team_collaboration", label: "Collaborative Team Environment" },
  { key: "learning_opportunities", label: "Learning & Development Opportunities" },
] as const;

export type MotivationKey = (typeof MOTIVATION_OPTIONS)[number]["key"];
export type GenerationMode = "ai" | "local";

export interface CoverLetterRequest {
  resume_id: number;
  job_title: string;
  company: string;
  job_description: string;
  /** Preset motivation keys plus any custom free-text values */
  motivations: string[];
  mode: GenerationMode;
}

/**
 * Returned by /generate — letter content ready to preview, not yet saved to DB.
 * Has no `id` or `created_at` until explicitly saved via saveCoverLetter().
 */
export interface CoverLetterDraft {
  resume_id: number;
  job_title: string;
  company: string;
  job_description: string;
  motivations: string[];
  content: string;
  generation_mode: GenerationMode;
}

export interface CoverLetterResponse {
  id: number;
  resume_id: number;
  job_title: string;
  company: string;
  job_description: string;
  motivations: string[];
  content: string;
  generation_mode: GenerationMode;
  created_at: string;
}

export interface CoverLetterSummary {
  id: number;
  resume_id: number;
  job_title: string;
  company: string;
  generation_mode: GenerationMode;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body?.detail != null) {
      if (typeof body.detail === "string") return body.detail;
      if (Array.isArray(body.detail))
        return body.detail.map((d: { msg?: string }) => d?.msg ?? String(d)).join("; ");
    }
  } catch {
    // ignore
  }
  return "Request failed: " + res.statusText;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/** Generate a cover letter preview — does not yet persist to DB. */
export async function generateCoverLetter(
  request: CoverLetterRequest
): Promise<CoverLetterDraft> {
  const res = await fetch(`${API_BASE}/api/cover-letter/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/**
 * Persist a cover letter draft (or edited content) to the database.
 * Returns the saved record with its assigned `id` and `created_at` timestamp.
 * Only letters saved via this call will appear in history.
 */
export async function saveCoverLetter(
  draft: CoverLetterDraft
): Promise<CoverLetterResponse> {
  const res = await fetch(`${API_BASE}/api/cover-letter/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_id: draft.resume_id,
      job_title: draft.job_title,
      company: draft.company,
      job_description: draft.job_description,
      motivations: draft.motivations,
      content: draft.content,
      generation_mode: draft.generation_mode,
    }),
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** List all saved cover letters (summary only). */
export async function listCoverLetters(): Promise<CoverLetterSummary[]> {
  const res = await fetch(`${API_BASE}/api/cover-letter`);
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** Retrieve a single cover letter with full content. */
export async function getCoverLetter(id: number): Promise<CoverLetterResponse> {
  const res = await fetch(`${API_BASE}/api/cover-letter/${id}`);
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** Delete a cover letter by id. */
export async function deleteCoverLetter(
  id: number
): Promise<{ success: boolean; deleted_id: number }> {
  const res = await fetch(`${API_BASE}/api/cover-letter/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** Save edited content back to the server. */
export async function updateCoverLetter(
  id: number,
  content: string
): Promise<CoverLetterResponse> {
  const res = await fetch(`${API_BASE}/api/cover-letter/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** Return the URL for downloading a cover letter as PDF. */
export function coverLetterPdfUrl(id: number): string {
  return `${API_BASE}/api/cover-letter/${id}/pdf`;
}

/**
 * Fetch the PDF for a cover letter and trigger a browser download.
 * Throws an Error if the server cannot
 * produce a PDF (e.g. pdflatex not installed).
 */
export async function downloadCoverLetterPdf(id: number, filename?: string): Promise<void> {
  const res = await fetch(coverLetterPdfUrl(id));
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename ?? `cover_letter_${id}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
