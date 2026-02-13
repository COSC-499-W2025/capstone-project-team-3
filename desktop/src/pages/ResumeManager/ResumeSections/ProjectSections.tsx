import { Project } from "../../../api/resume_types";

/** Backend may send skills as string (master resume) or array (saved resume). Normalize to array. */
function projectSkills(p: { skills?: string[] | string }): string[] {
  const raw = p.skills;
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "string") return raw.split(",").map((s: string) => s.trim()).filter(Boolean);
  return [];
}

/** Backend may omit or send non-array bullets. Normalize to array. */
function projectBullets(p: Project): string[] {
  if (Array.isArray(p.bullets)) return p.bullets;
  return [];
}

export function ProjectsSection({
  projects,
  showHeading = true,
}: {
  projects: Project[];
  showHeading?: boolean;
}) {
  return (
    <section className="resume-preview__section">
      {showHeading && (
        <h2 className="resume-preview__heading resume-preview__heading--projects">
          Projects / Experience
        </h2>
      )}
      {projects.map((p, i) => {
        const skills = projectSkills(p);
        const bullets = projectBullets(p);
        return (
          <div key={i} className="resume-preview__project">
            <div className="resume-preview__project-header">
              <p className="resume-preview__project-title">{p.title}</p>
              <span className="resume-preview__project-dates">{p.dates}</span>
            </div>
            <p className="resume-preview__project-skills">
              Skills:{" "}
              {skills.map((s, j) => (
                <span key={j}>
                  <span className="resume-preview__skill-inline">{s}</span>
                  {j < skills.length - 1 ? ", " : ""}
                </span>
              ))}
            </p>
            <ul className="resume-preview__project-bullets">
              {bullets.map((b, j) => (
                <li key={j}>{b}</li>
              ))}
            </ul>
          </div>
        );
      })}
    </section>
  );
}
