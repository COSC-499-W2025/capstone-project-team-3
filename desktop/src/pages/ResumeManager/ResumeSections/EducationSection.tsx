import { Education } from "../../../api/resume_types";

export function EducationSection({ education } : {education : Education}) {
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
