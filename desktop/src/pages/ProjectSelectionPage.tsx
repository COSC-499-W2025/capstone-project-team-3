import { useState, useEffect } from "react";
import { getProjects, type Project } from "../api/projects";
import "../styles/ProjectSelectionPage.css";

function ProjectSelectionPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProjects()
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const toggleProject = (projectId: string) => {
    const newSelected = new Set(selectedProjects);
    if (newSelected.has(projectId)) {
      newSelected.delete(projectId);
    } else {
      newSelected.add(projectId);
    }
    setSelectedProjects(newSelected);
  };

  const handleGenerateResume = () => {
    const selectedIds = Array.from(selectedProjects);
    console.log("Generating resume with projects:", selectedIds);
    // TODO: Implement resume generation with selected projects
  };

  if (loading) {
    return (
      <div className="loading-state">
        Loading projects...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="project-selection-container">
      <h1 className="page-title">
        Select Projects for Resume
      </h1>
      <p className="page-subtitle">
        Choose which projects should contribute to your resume.
      </p>

      <div className="table-container">
        <table className="projects-table">
          <thead>
            <tr className="table-header">
              <th>
                Project Name
              </th>
              <th>
                Skills
              </th>
              <th>
                Date Added
              </th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr
                key={project.id}
                className="project-row"
              >
                <td>
                  <label className="project-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedProjects.has(project.id)}
                      onChange={() => toggleProject(project.id)}
                      className="project-checkbox"
                    />
                    <span>
                      {project.name}
                    </span>
                  </label>
                </td>
                <td>
                  {project.skills.join(", ")}
                  {project.skills.length > 3 && ", ..."}
                </td>
                <td>
                  {new Date(project.date_added).toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                  }).replace(/\//g, '-')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {projects.length === 0 && (
          <div className="empty-state">
            No projects found. Add some projects to get started!
          </div>
        )}
      </div>

      <div className="button-container">
        <button
          onClick={handleGenerateResume}
          disabled={selectedProjects.size === 0}
          className="generate-button"
        >
          Generate Resume
        </button>
      </div>
    </div>
  );
}

export default ProjectSelectionPage;
