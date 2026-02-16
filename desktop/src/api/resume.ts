import type { Resume } from "./resume_types";
import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

export interface ResumeListItem {
  id: number | null;
  name: string;
  is_master: boolean;
}

export async function getResumes(): Promise<ResumeListItem[]> {
  const res = await fetch(`${API_BASE}/resume_names`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  const data = await res.json();
  return data.resumes ?? [];
}

export async function buildResume(): Promise<Resume> {
  const res = await fetch(`${API_BASE}/resume`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}

export async function previewResume(projectIds: string[]): Promise<Resume> {
  const params = projectIds.map(id => `project_ids=${id}`).join('&');
  const res = await fetch(`${API_BASE}/resume?${params}`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}

export async function getResumeById(id: number): Promise<Resume> {
  const res = await fetch(`${API_BASE}/resume/${id}`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json() as Promise<Resume>;
}
