import { useRef, useEffect } from "react";
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
  isEditing = false,
  onProjectChange,
  projectStartIndex = 0,
}: {
  projects: Project[];
  showHeading?: boolean;
  isEditing?: boolean;
  /** Called with (globalIndexInResume, updatedProject) when a project is edited. */
  onProjectChange?: (globalIndex: number, project: Project) => void;
  /** Index of the first project in this section within resume.projects (for multi-page). */
  projectStartIndex?: number;
}) {
  const emitProjectChange = (localIndex: number, updated: Project) => {
    onProjectChange?.(projectStartIndex + localIndex, updated);
  };

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
        const globalKey = projectStartIndex + i;

        return (
          <ProjectBlock
            key={globalKey}
            project={p}
            isEditing={isEditing}
            onChange={(updated) => emitProjectChange(i, updated)}
          />
        );
      })}
    </section>
  );
}

function ProjectBlock({
  project,
  isEditing,
  onChange,
}: {
  project: Project;
  isEditing: boolean;
  onChange: (project: Project) => void;
}) {
  const skills = projectSkills(project);
  const bullets = projectBullets(project);
  const skillsText = skills.join(", ");
  const bulletsText = bullets.join("\n");

  const titleRef = useRef<HTMLParagraphElement>(null);
  const datesRef = useRef<HTMLSpanElement>(null);
  const skillsRef = useRef<HTMLSpanElement>(null);
  const bulletsRef = useRef<HTMLDivElement>(null);

  const syncRefs = () => {
    if (!isEditing) return;
    if (titleRef.current && titleRef.current.textContent !== project.title) {
      titleRef.current.textContent = project.title;
    }
    if (datesRef.current && datesRef.current.textContent !== project.dates) {
      datesRef.current.textContent = project.dates;
    }
    if (skillsRef.current && skillsRef.current.textContent !== skillsText) {
      skillsRef.current.textContent = skillsText;
    }
    if (bulletsRef.current && bulletsRef.current.textContent !== bulletsText) {
      bulletsRef.current.textContent = bulletsText;
    }
  };

  useEffect(syncRefs, [isEditing, project.title, project.dates, skillsText, bulletsText]);

  /** Read bullets as lines; innerText so Enter (br/div) becomes newline. */
  const getBulletsText = (): string =>
    (bulletsRef.current?.innerText ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  const commit = () => {
    const rawTitle = titleRef.current?.textContent?.trim() ?? "";
    if (!rawTitle) {
      alert("A project name can never be empty.");
      if (titleRef.current) titleRef.current.textContent = project.title;
      const rawBullets = getBulletsText();
      onChange({
        ...project,
        title: project.title,
        dates: datesRef.current?.textContent?.trim() ?? project.dates,
        skills: (skillsRef.current?.textContent ?? "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        bullets: rawBullets
          .split("\n")
          .map((b) => b.trim())
          .filter(Boolean),
      });
      return;
    }
    const dates = datesRef.current?.textContent?.trim() ?? project.dates;
    const rawSkills = skillsRef.current?.textContent ?? "";
    const newSkills = rawSkills
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const rawBullets = getBulletsText();
    const newBullets = rawBullets
      .split("\n")
      .map((b) => b.trim())
      .filter(Boolean);
    onChange({ ...project, title: rawTitle, dates, skills: newSkills, bullets: newBullets });
  };

  if (isEditing) {
    return (
      <div key="project-edit" className="resume-preview__project">
        <div className="resume-preview__project-header">
          <p
            ref={titleRef}
            className="resume-preview__project-title"
            contentEditable
            suppressContentEditableWarning
            onBlur={commit}
            data-placeholder="Project title"
          />
          <span
            ref={datesRef}
            className="resume-preview__project-dates"
            contentEditable
            suppressContentEditableWarning
            onBlur={commit}
            data-placeholder="Start – End"
          />
        </div>
        <p className="resume-preview__project-skills">
          Skills:{" "}
          <span
            ref={skillsRef}
            contentEditable
            suppressContentEditableWarning
            onBlur={commit}
            className="resume-preview__skills-edit-inline"
            data-placeholder="Skill1, Skill2"
          />
        </p>
        <div className="resume-preview__project-bullets-edit-wrapper">
          <span className="resume-preview__project-bullets-hint">One bullet per line.</span>
          <div
            ref={bulletsRef}
            className="resume-preview__project-bullets-edit"
            contentEditable
            suppressContentEditableWarning
            onBlur={commit}
            data-placeholder="Bullet one&#10;Bullet two"
            aria-description="One bullet per line"
          />
        </div>
      </div>
    );
  }

  return (
    <div key="project-display" className="resume-preview__project">
      <div className="resume-preview__project-header">
        <p className="resume-preview__project-title">{project.title}</p>
        <span className="resume-preview__project-dates">{project.dates}</span>
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
}
