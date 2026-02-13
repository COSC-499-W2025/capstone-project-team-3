import { Education } from "../../../api/resume_types";

export function EducationSection({
  education,
  variant,
}: {
  education: Education;
  variant?: "default" | "latex";
}) {
  if (variant === "latex") {
    return (
      <section className="resume-preview__section">
        <h2 className="resume-preview__heading">Education</h2>
        <div className="resume-preview__education-row">
          <span className="resume-preview__education-school">{education.school}</span>
          {education.dates != null && education.dates !== "" && (
            <span className="resume-preview__education-dates">{education.dates}</span>
          )}
        </div>
        <p className="resume-preview__education-degree">{education.degree}</p>
        {education.gpa != null && education.gpa !== "" && (
          <p className="resume-preview__education-gpa">GPA: {education.gpa}</p>
        )}
      </section>
    );
  }

  return (
    <section className="mb-4">
      <h2 className="border-b font-semibold mb-2">Education</h2>
      <div>
        <strong>{education.school}</strong>
        <div>{education.degree}</div>
      </div>
    </section>
  );
}
