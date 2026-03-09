import { useState, useEffect } from "react";
import {
  getChronologicalProjects,
  type ChronologicalProject,
} from "../api/chronological";
import "../styles/DataManagementPage.css";

function formatDate(value: string): string {
  if (!value) return "—";
  try {
    const d = new Date(value);
    return d.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).replace(/\//g, "-");
  } catch {
    return value;
  }
}

/**
 * Data Management Page - View and edit chronological information
 * for projects and skills uploaded to the app.
 */
export function DataManagementPage() {
  const [projects, setProjects] = useState<ChronologicalProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = () => {
    setLoading(true);
    setError(null);
    getChronologicalProjects()
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load projects");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  if (loading) {
    return (
      <div className="data-management-container">
        <h1 className="data-management-title">Data Management</h1>
        <div className="data-management-loading">Loading projects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-management-container">
        <h1 className="data-management-title">Data Management</h1>
        <div className="data-management-error" role="alert">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="data-management-container">
      <h1 className="data-management-title">Data Management</h1>

      <div className="data-management-projects">
        <div className="data-management-section-header">
          <h2 className="data-management-section-title">Projects</h2>
          <button
            type="button"
            className="data-management-refresh"
            onClick={fetchProjects}
            disabled={loading}
          >
            Refresh
          </button>
        </div>
        {projects.length === 0 ? (
          <div className="data-management-empty">
            No projects found. Upload a ZIP file to add projects.
          </div>
        ) : (
          <div className="data-management-table-wrap">
            <table className="data-management-table">
              <thead>
                <tr>
                  <th>Project Name</th>
                  <th>Created</th>
                  <th>Last Modified</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.project_signature}>
                    <td>{p.name || p.project_signature}</td>
                    <td>{formatDate(p.created_at)}</td>
                    <td>{formatDate(p.last_modified)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default DataManagementPage;
