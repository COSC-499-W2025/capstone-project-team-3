import { Resume } from "../../../api/resume_types";

export function HeaderSection({
  resume,
  variant,
}: {
  resume: Resume;
  variant?: "default" | "latex";
}) {
  if (variant === "latex") {
    const links = resume.links ?? [];
    return (
      <header className="resume-preview__header">
        <h1 className="resume-preview__name">{resume.name}</h1>
        <p className="resume-preview__contact">{resume.email}</p>
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

  return (
    <header className="mb-6">
      <h1 className="text-2xl font-bold">{resume.name}</h1>
      <p>{resume.email}</p>
    </header>
  );
}
