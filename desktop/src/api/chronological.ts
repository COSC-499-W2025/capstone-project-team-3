import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ChronologicalProject {
  project_signature: string;
  name: string;
  path: string;
  created_at: string;
  last_modified: string;
}

export interface ChronologicalSkill {
  id: number;
  skill: string;
  source: string;
  date: string;
}

export interface UpdateProjectDatesPayload {
  created_at: string;
  last_modified: string;
}

export interface AddSkillPayload {
  skill: string;
  source: "code" | "non-code";
  date: string;
}

export interface UpdateSkillDatePayload {
  date: string;
}

export interface UpdateSkillNamePayload {
  skill: string;
}

// ---------------------------------------------------------------------------
// Project endpoints
// ---------------------------------------------------------------------------

/**
 * Fetch all projects with their date information (created_at, last_modified).
 */
export async function getChronologicalProjects(): Promise<ChronologicalProject[]> {
  const res = await fetch(`${API_BASE}/api/chronological/projects`, {
    method: "GET",
  });
  if (!res.ok) throw new Error("Failed to fetch projects: " + res.statusText);
  return res.json();
}

/**
 * Fetch a single project's date information by signature.
 */
export async function getChronologicalProject(
  signature: string
): Promise<ChronologicalProject> {
  const res = await fetch(
    `${API_BASE}/api/chronological/projects/${encodeURIComponent(signature)}`,
    { method: "GET" }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Project not found");
    throw new Error("Failed to fetch project: " + res.statusText);
  }
  return res.json();
}

/**
 * Update the created_at and last_modified dates of a project.
 * Accepts dates in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format.
 */
export async function updateProjectDates(
  signature: string,
  payload: UpdateProjectDatesPayload
): Promise<ChronologicalProject> {
  const res = await fetch(
    `${API_BASE}/api/chronological/projects/${encodeURIComponent(signature)}/dates`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Project not found");
    throw new Error("Failed to update project dates: " + res.statusText);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Skill endpoints (per project)
// ---------------------------------------------------------------------------

/**
 * Fetch all skills for a project, ordered chronologically by date.
 */
export async function getProjectSkills(
  signature: string
): Promise<ChronologicalSkill[]> {
  const res = await fetch(
    `${API_BASE}/api/chronological/projects/${encodeURIComponent(signature)}/skills`,
    { method: "GET" }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Project not found");
    throw new Error("Failed to fetch skills: " + res.statusText);
  }
  return res.json();
}

/**
 * Add a new skill with a date to a project.
 */
export async function addSkill(
  signature: string,
  payload: AddSkillPayload
): Promise<{ message: string; skill: string; source: string; date: string }> {
  const res = await fetch(
    `${API_BASE}/api/chronological/projects/${encodeURIComponent(signature)}/skills`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Project not found");
    if (res.status === 400) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Invalid request");
    }
    throw new Error("Failed to add skill: " + res.statusText);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Skill endpoints (by skill ID)
// ---------------------------------------------------------------------------

/**
 * Update the date of a specific skill entry.
 */
export async function updateSkillDate(
  skillId: number,
  payload: UpdateSkillDatePayload
): Promise<ChronologicalSkill> {
  const res = await fetch(
    `${API_BASE}/api/chronological/skills/${skillId}/date`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Skill not found");
    throw new Error("Failed to update skill date: " + res.statusText);
  }
  return res.json();
}

/**
 * Rename a skill entry.
 */
export async function updateSkillName(
  skillId: number,
  payload: UpdateSkillNamePayload
): Promise<ChronologicalSkill> {
  const res = await fetch(
    `${API_BASE}/api/chronological/skills/${skillId}/name`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Skill not found");
    if (res.status === 400) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Invalid request");
    }
    throw new Error("Failed to update skill name: " + res.statusText);
  }
  return res.json();
}

/**
 * Delete a skill entry by ID.
 */
export async function deleteSkill(skillId: number): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/chronological/skills/${skillId}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error("Skill not found");
    throw new Error("Failed to delete skill: " + res.statusText);
  }
}
