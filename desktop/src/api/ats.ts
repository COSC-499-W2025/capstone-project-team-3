import { getApiBaseUrl } from "../config/api";

export interface ATSBreakdown {
  keyword_coverage: number;
  skills_match: number;
  content_richness: number;
}

export interface ATSScoreResult {
  score: number;
  match_level: string;
  experience_months: number;
  breakdown: ATSBreakdown;
  matched_keywords: string[];
  missing_keywords: string[];
  matched_skills: string[];
  missing_skills: string[];
  tips: string[];
}

export async function scoreATS(
  jobDescription: string,
  resumeId: number | null,
  analysisMode: "local" | "ai" = "local"
): Promise<ATSScoreResult> {
  const res = await fetch(`${getApiBaseUrl()}/api/ats/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_description: jobDescription,
      resume_id: resumeId,
      analysis_mode: analysisMode,
    }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to calculate job match score");
  }
  return res.json();
}
