export interface Project {
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