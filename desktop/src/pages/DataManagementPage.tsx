import React, { useState, useEffect, useCallback } from "react";
import {
  getChronologicalProjects,
  getProjectSkills,
  updateProjectDates,
  updateProjectName,
  updateSkillDate,
  updateSkillName,
  addSkill,
  deleteSkill,
  type ChronologicalProject,
  type ChronologicalSkill,
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

/** Convert YYYY-MM-DD or ISO string to YYYY-MM-DD for date inputs */
function toDateInputValue(value: string): string {
  if (!value) return "";
  try {
    const d = new Date(value);
    return d.toISOString().slice(0, 10);
  } catch {
    return value.slice(0, 10) || "";
  }
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
    type: "project_name" | "project_created" | "project_modified" | "skill_name" | "skill_date";
    projectSig?: string;
    skillId?: number;
  } | null>(null);
  const [addSkillFor, setAddSkillFor] = useState<string | null>(null);
  const [newSkill, setNewSkill] = useState({ skill: "", date: "", source: "code" as "code" | "non-code" });
  const [saving, setSaving] = useState(false);

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

  const handleUpdateProjectName = async (sig: string, name: string) => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      await updateProjectName(sig, name.trim());
      setProjects((prev) =>
        prev.map((p) =>
          p.project_signature === sig ? { ...p, name: name.trim() } : p
        )
      );
      setEditing(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

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

  const handleUpdateSkillName = async (skillId: number, skill: string) => {
    if (!skill.trim()) return;
    setSaving(true);
    try {
      await updateSkillName(skillId, { skill: skill.trim() });
      setProjects((prev) =>
        prev.map((p) => ({
          ...p,
          skills: p.skills?.map((s) =>
            s.id === skillId ? { ...s, skill: skill.trim() } : s
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

  const handleAddSkill = async (sig: string) => {
    if (!newSkill.skill.trim() || !newSkill.date) return;
    setSaving(true);
    try {
      await addSkill(sig, {
        skill: newSkill.skill.trim(),
        source: newSkill.source,
        date: newSkill.date,
      });
      await fetchSkills(sig);
      setAddSkillFor(null);
      setNewSkill({ skill: "", date: "", source: "code" });
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to add skill");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSkill = async (skillId: number, sig: string) => {
    if (!confirm("Delete this skill?")) return;
    setSaving(true);
    try {
      await deleteSkill(skillId);
      await fetchSkills(sig);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to delete");
    } finally {
      setSaving(false);
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
                      <td>
                        {editing?.type === "project_name" &&
                        editing?.projectSig === p.project_signature ? (
                          <input
                            type="text"
                            className="data-management-edit-input"
                            defaultValue={p.name || p.project_signature}
                            autoFocus
                            onBlur={(e) =>
                              handleUpdateProjectName(
                                p.project_signature,
                                e.target.value
                              )
                            }
                            onKeyDown={(e) => {
                              if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                handleUpdateProjectName(
                                  p.project_signature,
                                  e.currentTarget.value
                                );
                                e.currentTarget.blur();
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
                                type: "project_name",
                                projectSig: p.project_signature,
                              })
                            }
                          >
                            {p.name || p.project_signature || "—"}
                          </button>
                        )}
                      </td>
                      <td>
                        {editing?.type === "project_created" &&
                        editing?.projectSig === p.project_signature ? (
                          <input
                            type="date"
                            className="data-management-edit-input"
                            defaultValue={toDateInputValue(p.created_at)}
                            autoFocus
                            onBlur={(e) =>
                              handleUpdateProjectDates(
                                p.project_signature,
                                e.target.value,
                                p.last_modified
                              )
                            }
                            onKeyDown={(e) => {
                              if (e.key === "Enter" && e.currentTarget.value) {
                                handleUpdateProjectDates(
                                  p.project_signature,
                                  e.currentTarget.value,
                                  p.last_modified
                                );
                                e.currentTarget.blur();
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
                            type="date"
                            className="data-management-edit-input"
                            defaultValue={toDateInputValue(p.last_modified)}
                            autoFocus
                            onBlur={(e) =>
                              handleUpdateProjectDates(
                                p.project_signature,
                                p.created_at,
                                e.target.value
                              )
                            }
                            onKeyDown={(e) => {
                              if (e.key === "Enter" && e.currentTarget.value) {
                                handleUpdateProjectDates(
                                  p.project_signature,
                                  p.created_at,
                                  e.currentTarget.value
                                );
                                e.currentTarget.blur();
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
                              })
                            }
                          >
                            {formatDate(p.last_modified)}
                          </button>
                        )}
                      </td>
                    </tr>
                    {p.expanded && (
                      <tr key={`${p.project_signature}-skills`} className="data-management-skills-row">
                        <td colSpan={4} className="data-management-skills-cell">
                          <div className="data-management-skills">
                            <h3 className="data-management-skills-title">Skills</h3>
                            {p.skills === undefined ? (
                              <div className="data-management-loading">Loading skills...</div>
                            ) : p.skills.length === 0 ? (
                              <p className="data-management-skills-empty">
                                No skills. Add one below.
                              </p>
                            ) : (
                              <table className="data-management-skills-table">
                                <thead>
                                  <tr>
                                    <th>Skill</th>
                                    <th>Source</th>
                                    <th>Date</th>
                                    <th />
                                  </tr>
                                </thead>
                                <tbody>
                                  {p.skills.map((s) => (
                                    <tr key={s.id}>
                                      <td>
                                        {editing?.type === "skill_name" &&
                                        editing?.skillId === s.id ? (
                                          <input
                                            type="text"
                                            className="data-management-edit-input"
                                            defaultValue={s.skill}
                                            autoFocus
                                            onBlur={(e) =>
                                              handleUpdateSkillName(
                                                s.id,
                                                e.target.value
                                              )
                                            }
                                            onKeyDown={(e) => {
                                              if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                                handleUpdateSkillName(
                                                  s.id,
                                                  e.currentTarget.value
                                                );
                                                e.currentTarget.blur();
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
                                                type: "skill_name",
                                                skillId: s.id,
                                              })
                                            }
                                          >
                                            {s.skill}
                                          </button>
                                        )}
                                      </td>
                                      <td>{s.source}</td>
                                      <td>
                                        {editing?.type === "skill_date" &&
                                        editing?.skillId === s.id ? (
                                          <input
                                            type="date"
                                            className="data-management-edit-input"
                                            defaultValue={toDateInputValue(s.date)}
                                            autoFocus
                                            onBlur={(e) =>
                                              handleUpdateSkillDate(
                                                s.id,
                                                e.target.value
                                              )
                                            }
                                            onKeyDown={(e) => {
                                              if (e.key === "Enter" && e.currentTarget.value) {
                                                handleUpdateSkillDate(
                                                  s.id,
                                                  e.currentTarget.value
                                                );
                                                e.currentTarget.blur();
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
                                              })
                                            }
                                          >
                                            {formatDate(s.date)}
                                          </button>
                                        )}
                                      </td>
                                      <td>
                                        <button
                                          type="button"
                                          className="data-management-delete-btn"
                                          onClick={() =>
                                            handleDeleteSkill(s.id, p.project_signature)
                                          }
                                          disabled={saving}
                                          aria-label="Delete skill"
                                        >
                                          Delete
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                            {addSkillFor === p.project_signature ? (
                              <div className="data-management-add-skill">
                                <input
                                  type="text"
                                  placeholder="Skill name"
                                  value={newSkill.skill}
                                  onChange={(e) =>
                                    setNewSkill((prev) => ({
                                      ...prev,
                                      skill: e.target.value,
                                    }))
                                  }
                                  className="data-management-edit-input"
                                />
                                <input
                                  type="date"
                                  value={newSkill.date}
                                  onChange={(e) =>
                                    setNewSkill((prev) => ({
                                      ...prev,
                                      date: e.target.value,
                                    }))
                                  }
                                  className="data-management-edit-input"
                                />
                                <select
                                  value={newSkill.source}
                                  onChange={(e) =>
                                    setNewSkill((prev) => ({
                                      ...prev,
                                      source: e.target.value as "code" | "non-code",
                                    }))
                                  }
                                  className="data-management-edit-input"
                                >
                                  <option value="code">code</option>
                                  <option value="non-code">non-code</option>
                                </select>
                                <button
                                  type="button"
                                  className="data-management-refresh"
                                  onClick={() =>
                                    handleAddSkill(p.project_signature)
                                  }
                                  disabled={saving || !newSkill.skill.trim() || !newSkill.date}
                                >
                                  Add
                                </button>
                                <button
                                  type="button"
                                  className="data-management-cancel-btn"
                                  onClick={() => {
                                    setAddSkillFor(null);
                                    setNewSkill({ skill: "", date: "", source: "code" });
                                  }}
                                >
                                  Cancel
                                </button>
                              </div>
                            ) : (
                              <button
                                type="button"
                                className="data-management-add-skill-btn"
                                onClick={() => setAddSkillFor(p.project_signature)}
                              >
                                + Add skill
                              </button>
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
    </div>
  );
}

export default DataManagementPage;
