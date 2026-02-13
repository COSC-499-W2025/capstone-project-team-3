import { Skills } from "../../../api/resume_types";

export function SkillsSection({
  skills,
  variant,
}: {
  skills: Skills;
  variant?: "default" | "latex";
}) {
  if (variant === "latex") {
    return (
      <section className="resume-preview__section">
        <h2 className="resume-preview__heading">Skills</h2>
        <p className="resume-preview__skills-label">Skills:</p>
        <p className="resume-preview__skills-list">
          {skills.Skills.map((s, i) => (
            <span key={i}>
              <span className="resume-preview__skill-inline">{s}</span>
              {i < skills.Skills.length - 1 ? ", " : ""}
            </span>
          ))}
        </p>
      </section>
    );
  }

  return (
    <section className="mb-4">
      <h2 className="border-b font-semibold mb-2">Skills</h2>
      <p>{skills.Skills.join(", ")}</p>
    </section>
  );
}
