import { API_BASE_URL } from "../config/api";

const API_BASE = API_BASE_URL;

export interface EducationDetail {
  institution: string;
  degree: string;
  start_date: string; // Format: YYYY-MM-DD or YYYY
  end_date?: string | null; // Format: YYYY-MM-DD or YYYY, null if ongoing
  gpa?: number | null; // GPA on a 4.0 scale
}

export interface UserPreferences {
  name: string;
  email: string;
  github_user: string;
  linkedin?: string | null; // LinkedIn profile URL
  education: string; // e.g., "Bachelor's", "Master's", "PhD"
  industry: string;
  job_title: string;
  education_details?: EducationDetail[] | null;
  profile_picture?: string | null; //path stored in DB e.g. "data/thumbnails/profile_picture.png"
}

export interface Institution {
  name: string;
}

export interface InstitutionSearchResponse {
  status: string;
  count: number;
  institutions: Institution[];
}


/**
 * Fetch the latest user preferences from the backend
 */
export async function getUserPreferences(): Promise<UserPreferences> {
  const res = await fetch(`${API_BASE}/api/user-preferences`, { 
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }
  });
  
  if (!res.ok) {
    if (res.status === 404) {
      // No preferences found - return default empty preferences
      throw new Error("No user preferences found");
    }
    throw new Error("Failed to fetch user preferences: " + res.statusText);
  }
  
  const data = await res.json();
  
  // Parse education_details if it's a JSON string
  if (data.education_details && typeof data.education_details === 'string') {
    try {
      data.education_details = JSON.parse(data.education_details);
    } catch (e) {
      console.error("Failed to parse education_details:", e);
      data.education_details = null;
    }
  }
  
  return data as UserPreferences;
}

/**
 * Save or update user preferences
 */
export async function saveUserPreferences(preferences: UserPreferences): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/user-preferences`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(preferences),
  });
  
  if (!res.ok) {
    // Try to get detailed error message from response
    let errorDetail = res.statusText;
    try {
      const errorData = await res.json();
      errorDetail = errorData.detail || JSON.stringify(errorData);
    } catch (e) {
      // If response is not JSON, use statusText
    }
    throw new Error(`Failed to save user preferences (${res.status}): ${errorDetail}`);
  }
  
  return res.json();
}

/**
 * Search Canadian post-secondary institutions
 */
export async function searchInstitutions(
  query: string, 
  limit: number = 50,
  simple: boolean = true
): Promise<InstitutionSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    simple: simple.toString(),
  });
  
  const res = await fetch(`${API_BASE}/api/institutions/search?${params}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }
  });
  
  if (!res.ok) {
    throw new Error("Failed to search institutions: " + res.statusText);
  }
  
  return res.json();
}

/**
 * Get all Canadian institutions (for dropdown/autocomplete)
 */
export async function getAllInstitutions(): Promise<InstitutionSearchResponse> {
  const res = await fetch(`${API_BASE}/api/institutions/list`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }
  });
  
  if (!res.ok) {
    throw new Error("Failed to fetch institutions list: " + res.statusText);
  }
  
  return res.json();
}

/**
 * Returns the URL to fetch the profile picture directly from the backend.
 */
export function getProfilePictureUrl(): string {
  return `${API_BASE}/api/user-preferences/profile-picture`;
}

/**
 * Upload a profile picture saved to thumbnails/ on the server; only path is stored in DB.
 */
export async function uploadProfilePicture(file: File): Promise<{ status: string; message: string; path: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/user-preferences/profile-picture`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      detail = err.detail || detail;
    } catch { /* ignore */ }
    throw new Error(`Failed to upload profile picture (${res.status}): ${detail}`);
  }

  return res.json();
}

/**
 * Remove the stored profile picture
 */
export async function deleteProfilePicture(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/user-preferences/profile-picture`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error("Failed to delete profile picture: " + res.statusText);
  }

  return res.json();
}
