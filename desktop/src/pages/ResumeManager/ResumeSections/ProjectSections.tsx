import { useRef, useEffect, useState } from "react";
import { Project } from "../../../api/resume_types";

const MONTH_ABBREV = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "YYYY-MM" -> "Jan 2024" */
function formatMonthYear(ym: string): string {
  if (!ym || !/^\d{4}-\d{2}$/.test(ym)) return "";
  const [y, m] = ym.split("-").map(Number);
  return `${MONTH_ABBREV[m - 1]} ${y}`;
}

/** "Jan 2024" or "Jan 2024 – Mar 2024" -> { start?: "YYYY-MM", end?: "YYYY-MM" } */
function parseDisplayDates(dates: string): { start?: string; end?: string } {
  if (!dates?.trim()) return {};
  const parts = dates.split(" – ").map((p) => p.trim());
  const result: { start?: string; end?: string } = {};
  if (parts[0]) {
    const m = MONTH_ABBREV.indexOf(parts[0].slice(0, 3));
    const y = parts[0].slice(-4);
    if (m >= 0 && /^\d{4}$/.test(y)) result.start = `${y}-${String(m + 1).padStart(2, "0")}`;
  }
  if (parts[1]) {
    const m = MONTH_ABBREV.indexOf(parts[1].slice(0, 3));
    const y = parts[1].slice(-4);
    if (m >= 0 && /^\d{4}$/.test(y)) result.end = `${y}-${String(m + 1).padStart(2, "0")}`;
  }
  return result;
}

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
  onProjectDelete,
  projectStartIndex = 0,
}: {
  projects: Project[];
  showHeading?: boolean;
  isEditing?: boolean;
  /** Called with (globalIndexInResume, updatedProject) when a project is edited. */
  onProjectChange?: (globalIndex: number, project: Project) => void;
  /** Called with project_id when user removes the project from the resume (saved resumes only). */
  onProjectDelete?: (projectId: string) => void;
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
            onDelete={onProjectDelete}
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
  onDelete,
}: {
  project: Project;
  isEditing: boolean;
  onChange: (project: Project) => void;
  onDelete?: (projectId: string) => void;
}) {
  const skills = projectSkills(project);
  const bullets = projectBullets(project);
  const skillsText = skills.join(", ");
  const bulletsText = bullets.join("\n");

  const titleRef = useRef<HTMLParagraphElement>(null);
  const skillsRef = useRef<HTMLSpanElement>(null);
  const bulletsRef = useRef<HTMLDivElement>(null);

  const parsed = parseDisplayDates(project.dates);
  const [startMonth, setStartMonth] = useState<string>(() => project.start_date ?? parsed.start ?? "");
  const [endMonth, setEndMonth] = useState<string>(() => project.end_date ?? parsed.end ?? "");

  useEffect(() => {
    const next = parseDisplayDates(project.dates);
    setStartMonth((prev) => project.start_date ?? next.start ?? prev);
    setEndMonth((prev) => project.end_date ?? next.end ?? prev);
  }, [project.start_date, project.end_date, project.dates]);

  const syncRefs = () => {
    if (!isEditing) return;
    if (titleRef.current && titleRef.current.textContent !== project.title) {
      titleRef.current.textContent = project.title;
    }
    if (skillsRef.current && skillsRef.current.textContent !== skillsText) {
      skillsRef.current.textContent = skillsText;
    }
    if (bulletsRef.current && bulletsRef.current.textContent !== bulletsText) {
      bulletsRef.current.textContent = bulletsText;
    }
  };

  useEffect(syncRefs, [isEditing, project.title, project.dates, skillsText, bulletsText]);

  const emitDatesChange = (start: string, end: string) => {
    const datesDisplay = start || end
      ? [formatMonthYear(start), formatMonthYear(end)].filter(Boolean).join(" – ") || "Start – End"
      : "";
    onChange({
      ...project,
      dates: datesDisplay,
      start_date: start || undefined,
      end_date: end || undefined,
    });
  };

  /** Read bullets as lines; innerText so Enter (br/div) becomes newline. */
  const getBulletsText = (): string =>
    (bulletsRef.current?.innerText ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  const commit = (overrides?: Partial<Project>) => {
    const rawTitle = titleRef.current?.textContent?.trim() ?? "";
    if (!rawTitle) {
      alert("A project name can never be empty.");
      if (titleRef.current) titleRef.current.textContent = project.title;
      const rawBullets = getBulletsText();
      onChange({
        ...project,
        title: project.title,
        dates: startMonth || endMonth
          ? [formatMonthYear(startMonth), formatMonthYear(endMonth)].filter(Boolean).join(" – ")
          : project.dates,
        start_date: startMonth || undefined,
        end_date: endMonth || undefined,
        skills: (skillsRef.current?.textContent ?? "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        bullets: rawBullets
          .split("\n")
          .map((b) => b.trim())
          .filter(Boolean),
        ...overrides,
      });
      return;
    }
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
    const datesDisplay =
      startMonth || endMonth
        ? [formatMonthYear(startMonth), formatMonthYear(endMonth)].filter(Boolean).join(" – ") || ""
        : "";
    onChange({
      ...project,
      title: rawTitle,
      dates: datesDisplay,
      start_date: startMonth || undefined,
      end_date: endMonth || undefined,
      skills: newSkills,
      bullets: newBullets,
      ...overrides,
    });
  };

  if (isEditing) {
    const canDelete = onDelete && project.project_id;
    return (
      <div key="project-edit" className="resume-preview__project">
        <div className="resume-preview__project-header">
          <p
            ref={titleRef}
            className="resume-preview__project-title"
            contentEditable
            suppressContentEditableWarning
            onBlur={() => commit()}
            data-placeholder="Project title"
          />
          <div className="resume-preview__project-header-right">
            <div className="resume-preview__project-dates-edit">
              <div className="resume-preview__project-date-wrap">
                <input
                  type="month"
                  className="resume-preview__project-date-input"
                  aria-label="Start (month and year)"
                  value={startMonth}
                  onChange={(e) => {
                    const v = e.target.value;
                    setStartMonth(v);
                    emitDatesChange(v, endMonth);
                  }}
                  onBlur={() => commit()}
                />
                {!startMonth && (
                  <span className="resume-preview__project-date-placeholder" aria-hidden>
                    Start
                  </span>
                )}
              </div>
              <span className="resume-preview__project-dates-sep"> – </span>
              <div className="resume-preview__project-date-wrap">
                <input
                  type="month"
                  className="resume-preview__project-date-input"
                  aria-label="End (month and year)"
                  value={endMonth}
                  onChange={(e) => {
                    const v = e.target.value;
                    setEndMonth(v);
                    emitDatesChange(startMonth, v);
                  }}
                  onBlur={() => commit()}
                />
                {!endMonth && (
                  <span className="resume-preview__project-date-placeholder" aria-hidden>
                    End
                  </span>
                )}
              </div>
            </div>
            {canDelete && (
              <button
                type="button"
                className="resume-preview__project-delete-btn"
                aria-label="Remove project from resume"
                onClick={() => {
                  if (window.confirm("Remove this project from the resume?")) {
                    onDelete(project.project_id!);
                  }
                }}
              >
                ×
              </button>
            )}
          </div>
        </div>
        <p className="resume-preview__project-skills">
          Skills:{" "}
          <span
            ref={skillsRef}
            contentEditable
            suppressContentEditableWarning
            onBlur={() => commit()}
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
            onBlur={() => commit()}
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
