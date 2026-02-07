import { Skills } from "../../../api/resume_types";

export function SkillsSection({ skills }: {skills:Skills}) {
  return (
    <section className="mb-4">
      <h2 className="border-b font-semibold mb-2">Skills</h2>
      <p>{skills.Skills.join(", ")}</p>
    </section>
  );
}
