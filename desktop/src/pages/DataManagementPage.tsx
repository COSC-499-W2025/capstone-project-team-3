import React, { useState, useEffect, useCallback } from "react";
import {
  getChronologicalProjects,
  getProjectSkills,
  updateProjectDates,
  updateSkillDate,
  type ChronologicalProject,
  type ChronologicalSkill,
} from "../api/chronological";
import { deleteProject } from "../api/projects";
import "../styles/DataManagementPage.css";
import trashIcon from "../assets/delete-24.png";

/** Format date as dd-mm-yyyy. Uses string parse for YYYY-MM-DD to avoid timezone shift. */
function formatDate(value: string): string {
  if (!value) return "—";
  const v = value.trim();
  const isoMatch = v.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) return `${isoMatch[3]}-${isoMatch[2]}-${isoMatch[1]}`;
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

/** Display skill source as "Technical skill" or "Soft skill". */
function formatSkillSource(source: string): string {
  const s = (source || "").toLowerCase();
  if (s === "code" || s === "technical_skill") return "Technical skill";
  if (s === "non-code" || s === "non-technical" || s === "soft_skill") return "Soft skill";
  return source || "—";
}

/** Parse dd-mm-yyyy to yyyy-mm-dd for API. Returns null if invalid. */
function parseDdMmYyyyToIso(str: string): string | null {
  const m = str.trim().match(/^(\d{1,2})-(\d{1,2})-(\d{4})$/);
  if (!m) return null;
  const [, d, mo, y] = m;
  const day = d.padStart(2, "0");
  const month = mo.padStart(2, "0");
  const year = y;
  if (parseInt(month, 10) > 12 || parseInt(day, 10) > 31) return null;
  return `${year}-${month}-${day}`;
}

interface ProjectWithSkills extends ChronologicalProject {
  skills?: ChronologicalSkill[];
  expanded?: boolean;
}

/**
 * Data Management Page - View and edit chronological information
 * for projects and skills uploaded to the app.
 */
export function DataManagementPage() {
  const [projects, setProjects] = useState<ProjectWithSkills[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<{
    type: "project_created" | "project_modified" | "skill_date";
    projectSig?: string;
    skillId?: number;
    value: string; // dd-mm-yyyy display value
  } | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteModal, setDeleteModal] = useState<{
    project: ProjectWithSkills;
    step: "confirm" | "type";
    typed: string;
  } | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchProjects = useCallback(() => {
    setLoading(true);
    setError(null);
    getChronologicalProjects()
      .then((data) => {
        setProjects(data.map((p) => ({ ...p, skills: undefined, expanded: false })));
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load projects");
        setLoading(false);
      });
  }, []);

  const fetchSkills = useCallback(async (signature: string) => {
    const skills = await getProjectSkills(signature);
    setProjects((prev) =>
      prev.map((p) =>
        p.project_signature === signature ? { ...p, skills } : p
      )
    );
  }, []);

  const toggleExpand = useCallback(
    (signature: string) => {
      setProjects((prev) =>
        prev.map((p) => {
          if (p.project_signature !== signature) return p;
          const nextExpanded = !p.expanded;
          if (nextExpanded && !p.skills) {
            fetchSkills(signature);
          }
          return { ...p, expanded: nextExpanded };
        })
      );
    },
    [fetchSkills]
  );

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleUpdateProjectDates = async (
    sig: string,
    created_at: string,
    last_modified: string
  ) => {
    setSaving(true);
    try {
      await updateProjectDates(sig, { created_at, last_modified });
      setProjects((prev) =>
        prev.map((p) =>
          p.project_signature === sig ? { ...p, created_at, last_modified } : p
        )
      );
      setEditing(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateSkillDate = async (skillId: number, date: string) => {
    setSaving(true);
    try {
      await updateSkillDate(skillId, { date });
      setProjects((prev) =>
        prev.map((p) => ({
          ...p,
          skills: p.skills?.map((s) =>
            s.id === skillId ? { ...s, date } : s
          ),
        }))
      );
      setEditing(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteConfirmed = async () => {
    if (!deleteModal) return;
    const { project } = deleteModal;
    const expectedName = project.name.toLowerCase();
    const sigPrefix = (project.project_signature || "").slice(0, 4);
    if (deleteModal.typed.trim().toLowerCase() !== `${expectedName}${sigPrefix}`) {
      alert("Confirmation did not match. Deletion cancelled.");
      return;
    }
    setDeleting(true);
    try {
      await deleteProject(project.project_signature);
      setProjects((prev) => prev.filter((p) => p.project_signature !== project.project_signature));
      setDeleteModal(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to delete project");
    } finally {
      setDeleting(false);
    }
  };

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
      <p className="data-management-description">
        View and edit chronological information for projects and skills uploaded to the app.
      </p>

      <div className="data-management-projects">
        <div className="data-management-section-header">
          <h2 className="data-management-section-title">Projects</h2>
          <button
            type="button"
            className="data-management-refresh"
            onClick={fetchProjects}
            disabled={loading || saving}
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
                  <th className="data-management-col-expand" />
                  <th>Project Name</th>
                  <th>Created</th>
                  <th>Last Modified</th>
                  <th className="data-management-col-delete" />
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <React.Fragment key={p.project_signature}>
                    <tr
                      key={p.project_signature}
                      className="data-management-project-row"
                    >
                      <td className="data-management-col-expand">
                        <button
                          type="button"
                          className="data-management-expand-btn"
                          onClick={() => toggleExpand(p.project_signature)}
                          aria-label={p.expanded ? "Collapse" : "Expand skills"}
                        >
                          {p.expanded ? "▼" : "▶"}
                        </button>
                      </td>
                      <td>{p.name || p.project_signature || "—"}</td>
                      <td>
                        {editing?.type === "project_created" &&
                        editing?.projectSig === p.project_signature ? (
                          <input
                            type="text"
                            className="data-management-edit-input"
                            value={editing.value}
                            onChange={(e) =>
                              setEditing((prev) =>
                                prev ? { ...prev, value: e.target.value } : null
                              )
                            }
                            placeholder="dd-mm-yyyy"
                            autoFocus
                            onBlur={() => {
                              const iso = parseDdMmYyyyToIso(editing.value);
                              if (iso) {
                                handleUpdateProjectDates(
                                  p.project_signature,
                                  iso,
                                  p.last_modified
                                );
                              }
                              setEditing(null);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                const iso = parseDdMmYyyyToIso(editing.value);
                                if (iso) {
                                  handleUpdateProjectDates(
                                    p.project_signature,
                                    iso,
                                    p.last_modified
                                  );
                                }
                                setEditing(null);
                              }
                              if (e.key === "Escape") setEditing(null);
                            }}
                          />
                        ) : (
                          <button
                            type="button"
                            className="data-management-editable"
                            onClick={() =>
                              setEditing({
                                type: "project_created",
                                projectSig: p.project_signature,
                                value: formatDate(p.created_at) === "—" ? "" : formatDate(p.created_at),
                              })
                            }
                          >
                            {formatDate(p.created_at)}
                          </button>
                        )}
                      </td>
                      <td>
                        {editing?.type === "project_modified" &&
                        editing?.projectSig === p.project_signature ? (
                          <input
                            type="text"
                            className="data-management-edit-input"
                            value={editing.value}
                            onChange={(e) =>
                              setEditing((prev) =>
                                prev ? { ...prev, value: e.target.value } : null
                              )
                            }
                            placeholder="dd-mm-yyyy"
                            autoFocus
                            onBlur={() => {
                              const iso = parseDdMmYyyyToIso(editing.value);
                              if (iso) {
                                handleUpdateProjectDates(
                                  p.project_signature,
                                  p.created_at,
                                  iso
                                );
                              }
                              setEditing(null);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                const iso = parseDdMmYyyyToIso(editing.value);
                                if (iso) {
                                  handleUpdateProjectDates(
                                    p.project_signature,
                                    p.created_at,
                                    iso
                                  );
                                }
                                setEditing(null);
                              }
                              if (e.key === "Escape") setEditing(null);
                            }}
                          />
                        ) : (
                          <button
                            type="button"
                            className="data-management-editable"
                            onClick={() =>
                              setEditing({
                                type: "project_modified",
                                projectSig: p.project_signature,
                                value: formatDate(p.last_modified) === "—" ? "" : formatDate(p.last_modified),
                              })
                            }
                          >
                            {formatDate(p.last_modified)}
                          </button>
                        )}
                      </td>
                      <td className="data-management-col-delete">
                        <button
                          type="button"
                          className="data-management-trash-btn"
                          aria-label={`Delete ${p.name || "project"}`}
                          title="Delete project"
                          disabled={saving || deleting}
                          onClick={() =>
                            setDeleteModal({ project: p, step: "confirm", typed: "" })
                          }
                        >
                        <img
                            src={trashIcon}
                            alt=""
                            aria-hidden="true"
                            className="data-management-trash-icon"
                          />
                        </button>
                      </td>
                    </tr>
                    {p.expanded && (
                      <tr key={`${p.project_signature}-skills`} className="data-management-skills-row">
                        <td colSpan={5} className="data-management-skills-cell">
                          <div className="data-management-skills">
                            <h3 className="data-management-skills-title">Skills</h3>
                            {p.skills === undefined ? (
                              <div className="data-management-loading">Loading skills...</div>
                            ) : p.skills.length === 0 ? (
                              <p className="data-management-skills-empty">
                                No skills.
                              </p>
                            ) : (
                              <table className="data-management-skills-table">
                                <thead>
                                  <tr>
                                    <th>Skill</th>
                                    <th>Source</th>
                                    <th>Date</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {p.skills.map((s) => (
                                    <tr key={s.id}>
                                      <td>{s.skill}</td>
                                      <td>{formatSkillSource(s.source)}</td>
                                      <td>
                                        {editing?.type === "skill_date" &&
                                        editing?.skillId === s.id ? (
                                          <input
                                            type="text"
                                            className="data-management-edit-input"
                                            value={editing.value}
                                            onChange={(e) =>
                                              setEditing((prev) =>
                                                prev ? { ...prev, value: e.target.value } : null
                                              )
                                            }
                                            placeholder="dd-mm-yyyy"
                                            autoFocus
                                            onBlur={() => {
                                              const iso = parseDdMmYyyyToIso(editing.value);
                                              if (iso) {
                                                handleUpdateSkillDate(s.id, iso);
                                              }
                                              setEditing(null);
                                            }}
                                            onKeyDown={(e) => {
                                              if (e.key === "Enter") {
                                                const iso = parseDdMmYyyyToIso(editing.value);
                                                if (iso) {
                                                  handleUpdateSkillDate(s.id, iso);
                                                }
                                                setEditing(null);
                                              }
                                              if (e.key === "Escape") setEditing(null);
                                            }}
                                          />
                                        ) : (
                                          <button
                                            type="button"
                                            className="data-management-editable"
                                            onClick={() =>
                                              setEditing({
                                                type: "skill_date",
                                                skillId: s.id,
                                                value: formatDate(s.date) === "—" ? "" : formatDate(s.date),
                                              })
                                            }
                                          >
                                            {formatDate(s.date)}
                                          </button>
                                        )}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {deleteModal && (
        <div className="data-management-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="delete-modal-title">
          <div className="data-management-modal">
            {deleteModal.step === "confirm" ? (
              <>
                <h2 id="delete-modal-title" className="data-management-modal-title">Delete Project</h2>
                <p className="data-management-modal-body">
                  Are you sure you want to delete{" "}
                  <strong>{deleteModal.project.name || deleteModal.project.project_signature}</strong>?
                  <br />
                  <span className="data-management-modal-warning">
                    This will permanently remove all insights for this project and cannot be undone.
                  </span>
                </p>
                <div className="data-management-modal-actions">
                  <button
                    type="button"
                    className="data-management-modal-cancel"
                    onClick={() => setDeleteModal(null)}
                    disabled={deleting}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="data-management-modal-confirm-danger"
                    onClick={() => setDeleteModal((prev) => prev ? { ...prev, step: "type" } : null)}
                    disabled={deleting}
                  >
                    Yes, Delete
                  </button>
                </div>
              </>
            ) : (
              <>
                <h2 id="delete-modal-title" className="data-management-modal-title">Confirm Deletion</h2>
                <p className="data-management-modal-body">
                  To confirm, type{" "}
                  <strong>
                    {deleteModal.project.name.toLowerCase()}
                    {(deleteModal.project.project_signature || "").slice(0, 4)}
                  </strong>{" "}
                  below:
                </p>
                <input
                  type="text"
                  className="data-management-edit-input data-management-modal-input"
                  value={deleteModal.typed}
                  onChange={(e) =>
                    setDeleteModal((prev) => prev ? { ...prev, typed: e.target.value } : null)
                  }
                  placeholder={`${deleteModal.project.name.toLowerCase()}${(deleteModal.project.project_signature || "").slice(0, 4)}`}
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleDeleteConfirmed();
                    if (e.key === "Escape") setDeleteModal(null);
                  }}
                  aria-label="Type project name to confirm deletion"
                />
                <div className="data-management-modal-actions">
                  <button
                    type="button"
                    className="data-management-modal-cancel"
                    onClick={() => setDeleteModal(null)}
                    disabled={deleting}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="data-management-modal-confirm-danger"
                    onClick={handleDeleteConfirmed}
                    disabled={
                      deleting ||
                      deleteModal.typed.trim().toLowerCase() !==
                        `${deleteModal.project.name.toLowerCase()}${(deleteModal.project.project_signature || "").slice(0, 4)}`
                    }
                  >
                    {deleting ? "Deleting…" : "Delete Project"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default DataManagementPage;
