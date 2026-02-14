const API_BASE = "http://localhost:8000";

export interface Project {
  id: string;
  name: string;
  score: number;
  skills: string[];
  date_added: string;
}

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/api/projects`, { method: "GET" });
  if (!res.ok) throw new Error("Request failed: " + res.statusText);
  return res.json();
}
