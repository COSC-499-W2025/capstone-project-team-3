import { Skills } from "../../../api/resume_types";

export function SkillsSection({ skills }: { skills: Skills }) {
  return (
    <section className="resume-preview__section">
      <h2 className="resume-preview__heading">Skills</h2>
      <div className="resume-preview__skills-row">
        <span className="resume-preview__skills-label">Skills:</span>
        <p className="resume-preview__skills-list">
          {skills.Skills.map((s, i) => (
            <span key={i}>
              <span className="resume-preview__skill-inline">{s}</span>
              {i < skills.Skills.length - 1 ? ", " : ""}
            </span>
          ))}
        </p>
      </div>
    </section>
  );
}
