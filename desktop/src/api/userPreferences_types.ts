export interface EducationDetail {
  institution: string;
  degree: string;
  program: string;
  start_date: string; // Format: YYYY-MM-DD or YYYY
  end_date?: string | null; // Format: YYYY-MM-DD or YYYY, null if ongoing
  gpa?: number | null; // GPA on a 4.0 scale
}

export interface UserPreferences {
  name: string;
  email: string;
  github_user: string;
  education: string; // e.g., "Bachelor's", "Master's", "PhD"
  industry: string;
  job_title: string;
  education_details?: EducationDetail[] | null;
}

// Do I need this?
export interface Institution {
  name: string;
  province?: string;
  city?: string;
  programs?: string[];
}

export interface InstitutionSearchResponse {
  status: string;
  count: number;
  institutions: Institution[];
}
