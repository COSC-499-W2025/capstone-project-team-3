import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

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
