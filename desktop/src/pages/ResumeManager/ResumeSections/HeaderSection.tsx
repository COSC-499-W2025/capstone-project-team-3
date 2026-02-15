import { Resume } from "../../../api/resume_types";

export function HeaderSection({ resume }: { resume: Resume }) {
  const links = resume.links ?? [];
  return (
    <header className="resume-preview__header">
      <h1 className="resume-preview__name">{resume.name}</h1>
      <p className="resume-preview__contact">
        <a href={`mailto:${resume.email}`}>{resume.email}</a>
      </p>
      {links.length > 0 && (
        <p className="resume-preview__links">
          {links.map((link, i) => (
            <a key={i} href={link.url} target="_blank" rel="noopener noreferrer">
              {link.label}
            </a>
          ))}
        </p>
      )}
    </header>
  );
}
