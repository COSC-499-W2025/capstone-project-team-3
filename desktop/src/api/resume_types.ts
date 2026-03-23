export interface Project {
  /** Optional because the resume API never returns it; only the frontend may set it when resolving for save. */
  project_id?: string;
  title: string;
  dates: string;
  /** ISO date (YYYY-MM-DD or YYYY-MM-01) for save payload; backend expects this format. */
  start_date?: string;
  /** ISO date (YYYY-MM-DD or YYYY-MM-01) for save payload; backend expects this format. */
  end_date?: string;
  skills: string[];
  bullets: string[];
}

export interface Education{
    school: string;
    degree: string;
    dates?: string;
    gpa?: string;
}

export interface Award {
    title: string;
    issuer?: string;
    /**
     * Month-year in YYYY-MM (recommended) or ISO-like YYYY-MM-01.
     * Renderers handle both.
     */
    date?: string;
    details?: string[];
}

export interface WorkExperience {
    role: string;
    company?: string;
    /** Month-year in YYYY-MM (recommended) or ISO-like YYYY-MM-01. */
    start_date?: string;
    /** Month-year in YYYY-MM (recommended) or ISO-like YYYY-MM-01. */
    end_date?: string;
    details?: string[];
}

export interface Skills{
    Proficient: string[];
    Familiar: string[];
}

export interface Link {
  label: string;
  url: string;
}

export interface Resume {
  name: string;
  email: string;
  links: Link[];

  education: Education[];

  awards: Award[];

  work_experience?: WorkExperience[];

  skills: Skills;

  projects: Project[];

  personal_summary?: string | null;
}
