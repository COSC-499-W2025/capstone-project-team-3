export interface Project {
  /** Optional because the resume API never returns it; only the frontend may set it when resolving for save. */
  project_id?: string;
  title: string;
  dates: string;
  skills: string[];
  bullets: string[];
}

export interface Education{
    school: string;
    degree: string;
    dates?: string;
    gpa?: string;
}

export interface Skills{
    Skills: string[];
}

export interface Link {
  label: string;
  url: string;
}

export interface Resume {
  name: string;
  email: string;
  links: Link[];

  education: Education;

  skills: Skills;

  projects: Project[];
}

