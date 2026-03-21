import type { Resume, Skills, Award, WorkExperience } from "./resume_types";
import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

/** Parse error body (e.g. FastAPI detail) when available; fallback to statusText. */
async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body?.detail != null) {
      if (typeof body.detail === "string") return body.detail;
      if (Array.isArray(body.detail)) return body.detail.map((d: { msg?: string }) => d?.msg ?? String(d)).join("; ");
    }
    if (body && typeof body.message === "string") return body.message;
  } catch {
    // ignore non-JSON or read errors
  }
  return "Request failed: " + res.statusText;
}

export interface ResumeListItem {
  id: number | null; // null for preview resumes
  name: string;
  is_master: boolean;
}

// Fetch list of all saved resumes
export async function getResumes(): Promise<ResumeListItem[]> {
  const res = await fetch(`${API_BASE}/resume_names`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  const data = await res.json();
  return data.resumes ?? [];
}

// Build master resume with all projects
export async function buildResume(): Promise<Resume> {
  const res = await fetch(`${API_BASE}/resume`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}

// Generate preview resume with selected projects only
export async function previewResume(projectIds: string[]): Promise<Resume> {
  const params = projectIds.map(id => `project_ids=${id}`).join('&');
  const res = await fetch(`${API_BASE}/resume?${params}`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}

// Fetch saved resume by ID (includes edits from RESUME_PROJECT table)
export async function getResumeById(id: number): Promise<Resume> {
  const res = await fetch(`${API_BASE}/resume/${id}`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}

export async function deleteResume(id: number): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/resume/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json();
}

/** Remove a project from a saved resume (does not delete the project from the project list). */
export async function deleteProjectFromResume(
  resumeId: number,
  projectId: string
): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/resume/${resumeId}/project/${encodeURIComponent(projectId)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}

/** Add projects to an existing saved resume (only non-master resumes). */
export async function addProjectsToResume(
  resumeId: number,
  projectIds: string[]
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/resume/${resumeId}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_ids: projectIds }),
  });
  if (!res.ok) {
    const message = await parseErrorDetail(res);
    throw new Error(message);
  }
  return res.json();
}
// Save new resume with selected projects
export async function saveNewResume(
  name: string,
  projectIds: string[],
  skills?: Skills,
  awards?: Award[],
  work_experience?: WorkExperience[]
): Promise<{ resume_id: number }> {
  const res = await fetch(`${API_BASE}/resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      project_ids: projectIds,
      ...(skills ? { skills } : {}),
      ...(awards !== undefined ? { awards } : {}),
      ...(work_experience !== undefined ? { work_experience } : {}),
    }),
  });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<{ resume_id: number }>;
}

// Update existing saved resume with partial edits
export async function updateResume(
  id: number, 
  payload: { skills?: Skills; projects?: unknown[]; awards?: Award[]; work_experience?: WorkExperience[] }
): Promise<void> {
  const res = await fetch(`${API_BASE}/resume/${id}/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
}

// Download resume as PDF: resumeId for saved resumes, projectIds for preview, or neither for master
export async function downloadResumePDF(params?: { projectIds?: string[], resumeId?: number, filename?: string }): Promise<void> {
  // Validate parameters
  if (params?.resumeId !== undefined && params?.projectIds && params.projectIds.length > 0) {
    throw new Error("Cannot specify both resumeId and projectIds");
  }

  const queryParams = new URLSearchParams();
  
  // Priority: resume_id > project_ids > master resume
  if (params?.resumeId !== undefined) {
    queryParams.append('resume_id', params.resumeId.toString());
  } else if (params?.projectIds) {
    params.projectIds.forEach(id => queryParams.append('project_ids', id));
  }
  
  const queryString = queryParams.toString();
  const url = queryString ? `${API_BASE}/resume/export/pdf?${queryString}` : `${API_BASE}/resume/export/pdf`;
  
  const res = await fetch(url, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  
  // Trigger browser download
  const blob = await res.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = params?.filename ? `${params.filename}.pdf` : 'resume.pdf'; //uses the name from the sidebar (name of resume stored)
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}

// Download resume as TeX: resumeId for saved resumes, projectIds for preview, or neither for master
export async function downloadResumeTeX(params?: { projectIds?: string[], resumeId?: number, filename?: string }): Promise<void> {
  // Validate parameters
  if (params?.resumeId !== undefined && params?.projectIds && params.projectIds.length > 0) {
    throw new Error("Cannot specify both resumeId and projectIds");
  }
  
  const queryParams = new URLSearchParams();
  
  // Priority: resume_id > project_ids > master resume
  if (params?.resumeId !== undefined) {
    queryParams.append('resume_id', params.resumeId.toString());
  } else if (params?.projectIds) {
    params.projectIds.forEach(id => queryParams.append('project_ids', id));
  }
  
  const queryString = queryParams.toString();
  const url = queryString ? `${API_BASE}/resume/export/tex?${queryString}` : `${API_BASE}/resume/export/tex`;
  
  const res = await fetch(url, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  
  // Trigger browser download
  const blob = await res.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = params?.filename ? `${params.filename}.tex` : 'resume.tex'; //uses the name from the sidebar (name of resume stored)
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}
