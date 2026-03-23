import { Resume } from "../../../api/resume_types";

interface HeaderSectionProps {
  resume: Resume;
  isEditing?: boolean;
  onChange?: (summary: string) => void;
}

export function HeaderSection({ resume, isEditing = false, onChange }: HeaderSectionProps) {
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
      {isEditing ? (
        <div className="resume-preview__summary-edit">
          <div className="resume-preview__heading">Professional Summary</div>
          <textarea
            className="resume-preview__summary-textarea"
            value={resume.personal_summary ?? ""}
            onChange={(e) => onChange?.(e.target.value)}
            placeholder="Add a personal summary..."
            rows={3}
            maxLength={500}
          />
          <span className="resume-preview__summary-hint">
            {(resume.personal_summary ?? "").length}/500
          </span>
        </div>
      ) : (
        resume.personal_summary && (
          <div className="resume-preview__summary-block">
            <div className="resume-preview__heading">Professional Summary</div>
            <p className="resume-preview__summary">{resume.personal_summary}</p>
          </div>
        )
      )}
    </header>
  );
}
