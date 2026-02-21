/**
 * Portfolio API Client
 */

import { API_BASE_URL } from "../config/api";

export interface Project {
  id: number;
  name: string;
  score: number;
  score_overridden?: boolean;
  score_overridden_value?: number;
  start_date?: string;
  end_date?: string;
  technical_keywords?: string[];
  summary?: string;
  contribution_details?: string;
  // Add other project fields as needed
}

export interface PortfolioData {
  overview_stats: {
    total_projects: number;
    avg_score: number;
    total_skills: number;
    total_languages: number;
    total_lines: number;
    date_range: string;
  };
  top_projects: Project[];
  graphs: {
    language_distribution: { [key: string]: number };
    complexity_distribution: {
      distribution: {
        small: number;
        medium: number;
        large: number;
      };
    };
    score_distribution: {
      distribution: {
        excellent: number;
        good: number;
        fair: number;
        poor: number;
      };
    };
    monthly_activity: { [key: string]: number };
    top_skills: { [key: string]: number };
  };
  project_type_analysis: {
    github: { count: number };
    local: { count: number };
  };
  github_projects: Project[];
  local_projects: Project[];
}

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE_URL}/api/projects`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch projects: " + res.statusText);
  }

  return res.json();
}

export async function getPortfolio(projectIds?: Array<number | string>): Promise<PortfolioData> {
  const url = new URL(`${API_BASE_URL}/api/portfolio`);
  
  if (projectIds && projectIds.length > 0) {
    url.searchParams.append('project_ids', projectIds.join(','));
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch portfolio: " + res.statusText);
  }

  return res.json();
}