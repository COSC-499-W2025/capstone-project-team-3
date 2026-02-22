import { Education } from "../../../api/resume_types";

export function EducationSection({ education }: { education: Education[] }) {
  return (
    <section className="resume-preview__section">
      <h2 className="resume-preview__heading">Education</h2>
      {education.map((edu, index) => (
        <div key={index} className="resume-preview__education-entry">
          <div className="resume-preview__education-row">
            <span className="resume-preview__education-school">{edu.school}</span>
            {edu.dates != null && edu.dates !== "" && (
              <span className="resume-preview__education-dates">{edu.dates}</span>
            )}
          </div>
          <p className="resume-preview__education-degree">
            {edu.degree}
            {edu.gpa != null && edu.gpa !== "" && (
              <span className="resume-preview__education-gpa"> | GPA: {edu.gpa}</span>
            )}
          </p>
        </div>
      ))}
    </section>
  );
}
