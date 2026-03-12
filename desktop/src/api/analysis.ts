import { API_BASE_URL } from "../config/api";

export interface RunAnalysisPayload {
  upload_id: string;
  default_analysis_type?: "local" | "ai";
  similarity_action?: "create_new" | "update_existing";
  cleanup_zip?: boolean;
  cleanup_extracted?: boolean;
  scan_only?: boolean;
}

export interface ProjectAnalysisResult {
  project_name: string;
  project_path: string;
  project_signature: string | null;
  requested_analysis_type: "local" | "ai";
  effective_analysis_type: "local" | "ai";
  status: "analyzed" | "skipped" | "failed";
  reason: string | null;
}

export interface RunAnalysisResponse {
  status: string;
  upload_id: string;
  total_projects: number;
  analyzed_projects: number;
  skipped_projects: number;
  failed_projects: number;
  results: ProjectAnalysisResult[];
}

/**
 * Run analysis on an uploaded ZIP file.
 * Extracts projects and populates the database so they appear in Data Management.
 */
export async function runAnalysis(
  payload: RunAnalysisPayload
): Promise<RunAnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      upload_id: payload.upload_id,
      default_analysis_type: payload.default_analysis_type ?? "local",
      similarity_action: payload.similarity_action ?? "create_new",
      cleanup_zip: payload.cleanup_zip ?? false,
      cleanup_extracted: payload.cleanup_extracted ?? false,
      scan_only: payload.scan_only ?? false,
    }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = data.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d: { msg?: string }) => d.msg ?? String(d)).join("; ")
      : typeof detail === "string"
        ? detail
        : res.statusText;
    throw new Error(msg || "Analysis failed");
  }

  return res.json();
}
