import { Project } from "../../../api/resume_types";

export function ProjectsSection({ projects} : {projects:Project[] }) {
  return (
    <section>
      <h2 className="border-b font-semibold mb-2">Projects</h2>

      {projects.map((p, i) => (
        <div key={i} className="mb-3">
          <strong>{p.title}</strong>
          <ul className="list-disc ml-5">
            {p.bullets.map((b, j) => (
              <li key={j}>{b}</li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
