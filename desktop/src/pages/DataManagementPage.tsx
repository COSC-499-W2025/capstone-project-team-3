import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
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
import { deleteProject } from "../api/projects";
import { ERROR_TIMEOUT } from "../constants/uiTiming";
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

/** Normalize date string to YYYY-MM-DD for comparison. Handles ISO timestamps (2026-01-15T10:30:00Z) and date-only (2026-01-15). */
function normalizeToDateOnly(value: string): string {
  if (!value) return value;
  const m = value.trim().match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${m[1]}-${m[2]}-${m[3]}` : value;
}

const DATE_FORMAT_ERR = "Invalid date format. Use dd-mm-yyyy (e.g. 25-12-2024).";
const MODIFIED_BEFORE_CREATED_ERR = "Last modified must be after date created.";
const SKILL_OUTSIDE_RANGE_ERR = "Skill date must be within the project's date range (created to last modified).";

interface ProjectWithSkills extends ChronologicalProject {
  skills?: ChronologicalSkill[];
  expanded?: boolean;
}

/**
 * Data Management Page - View and edit chronological information
 * for projects and skills uploaded to the app.
 */
export function DataManagementPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectWithSkills[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<{
    type: "project_created" | "project_modified" | "project_name" | "skill_date" | "skill_name";
    projectSig?: string;
    skillId?: number;
    value: string; // dd-mm-yyyy or skill name or project name
  } | null>(null);
  const [addingSkill, setAddingSkill] = useState<{
    projectSig: string;
    skill: string;
    source: "" | "code" | "non-technical";
    date: string; // dd-mm-yyyy or empty
  } | null>(null);
  const [saving, setSaving] = useState(false);
  const [deleteModal, setDeleteModal] = useState<{
    project: ProjectWithSkills;
    step: "confirm" | "type";
    typed: string;
  } | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteSkillModal, setDeleteSkillModal] = useState<{
    skillId: number;
    skillName: string;
    projectSig: string;
  } | null>(null);
  const [deletingSkill, setDeletingSkill] = useState(false);
  const [dateError, setDateError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Auto-dismiss error banners after ERROR_TIMEOUT
  useEffect(() => {
    if (!dateError) return;
    const t = setTimeout(() => setDateError(null), ERROR_TIMEOUT);
    return () => clearTimeout(t);
  }, [dateError]);

  useEffect(() => {
    if (!saveError) return;
    const t = setTimeout(() => setSaveError(null), ERROR_TIMEOUT);
    return () => clearTimeout(t);
  }, [saveError]);

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
    setDateError(null);
    const createdNorm = normalizeToDateOnly(created_at);
    const modifiedNorm = normalizeToDateOnly(last_modified);
    if (createdNorm >= modifiedNorm) {
      setDateError(MODIFIED_BEFORE_CREATED_ERR);
      return;
    }
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
      setSaveError(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateProjectName = async (projectSig: string, name: string) => {
    if (!name.trim()) {
      setSaveError("Project name cannot be empty");
      return;
    }
    setSaving(true);
    try {
      await updateProjectName(projectSig, name.trim());
      setProjects((prev) =>
        prev.map((p) =>
          p.project_signature === projectSig ? { ...p, name: name.trim() } : p
        )
      );
      setEditing(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to update project name");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateSkillDate = async (
    skillId: number,
    date: string,
    projectSig: string
  ) => {
    setDateError(null);
    const proj = projects.find((p) => p.project_signature === projectSig);
    if (proj) {
      const dateNorm = normalizeToDateOnly(date);
      const createdNorm = normalizeToDateOnly(proj.created_at);
      const modifiedNorm = normalizeToDateOnly(proj.last_modified);
      if (dateNorm < createdNorm || dateNorm > modifiedNorm) {
        setDateError(SKILL_OUTSIDE_RANGE_ERR);
        return;
      }
    }
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
      setSaveError(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateSkillName = async (skillId: number, skill: string) => {
    if (!skill.trim()) {
      setSaveError("Skill name cannot be empty");
      return;
    }
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
      setSaveError(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveSkillDate = async (skillId: number, _projectSig: string) => {
    setSaving(true);
    try {
      await updateSkillDate(skillId, { date: "" });
      setProjects((prev) =>
        prev.map((p) => ({
          ...p,
          skills: p.skills?.map((s) =>
            s.id === skillId ? { ...s, date: "" } : s
          ),
        }))
      );
      setEditing(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const handleAddSkill = async (projectSig: string) => {
    const add = addingSkill;
    if (!add || add.projectSig !== projectSig) return;
    if (!add.skill.trim()) {
      setSaveError("Skill name cannot be empty");
      return;
    }
    if (!add.source || (add.source !== "code" && add.source !== "non-technical")) {
      setSaveError("Please select a skill type");
      return;
    }
    const proj = projects.find((p) => p.project_signature === projectSig);
    if (!proj) return;
    let dateIso = add.date.trim() ? parseDdMmYyyyToIso(add.date) : null;
    if (!dateIso) {
      const firstSkillDate = proj.skills?.length
        ? (proj.skills[0]?.date || "").match(/^\d{4}-\d{2}-\d{2}/)?.[0]
        : null;
      dateIso = firstSkillDate || proj.created_at?.match(/^\d{4}-\d{2}-\d{2}/)?.[0] || "";
    }
    if (dateIso && proj) {
      const dateNorm = normalizeToDateOnly(dateIso);
      const createdNorm = normalizeToDateOnly(proj.created_at);
      const modifiedNorm = normalizeToDateOnly(proj.last_modified);
      if (dateNorm < createdNorm || dateNorm > modifiedNorm) {
        setDateError(SKILL_OUTSIDE_RANGE_ERR);
        return;
      }
    }
    setDateError(null);
    setSaving(true);
    try {
      await addSkill(projectSig, {
        skill: add.skill.trim(),
        source: add.source,
        date: dateIso || "",
      });
      const skills = await getProjectSkills(projectSig);
      setProjects((prev) =>
        prev.map((p) =>
          p.project_signature === projectSig ? { ...p, skills } : p
        )
      );
      setAddingSkill(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to add skill");
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
      setSaveError("Confirmation did not match. Deletion cancelled.");
      return;
    }
    setDeleting(true);
    try {
      await deleteProject(project.project_signature);
      setProjects((prev) => prev.filter((p) => p.project_signature !== project.project_signature));
      setDeleteModal(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to delete project");
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteSkillConfirmed = async () => {
    if (!deleteSkillModal) return;
    const { skillId, projectSig } = deleteSkillModal;
    setDeletingSkill(true);
    try {
      await deleteSkill(skillId);
      const skills = await getProjectSkills(projectSig);
      setProjects((prev) =>
        prev.map((p) =>
          p.project_signature === projectSig ? { ...p, skills } : p
        )
      );
      setDeleteSkillModal(null);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Failed to delete skill");
    } finally {
      setDeletingSkill(false);
    }
  };

  if (loading) {
    return (
      <div className="data-management-container">
        <div className="page-home-nav" aria-label="Page navigation">
          <button
            type="button"
            className="page-home-link"
            onClick={() => navigate("/hubpage")}
          >
            Home
          </button>
          <span className="page-home-separator">›</span>
          <span className="page-home-current">Projects</span>
        </div>
        <h1 className="data-management-title">Data Management</h1>
        <div className="data-management-loading">Loading projects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-management-container">
        <div className="page-home-nav" aria-label="Page navigation">
          <button
            type="button"
            className="page-home-link"
            onClick={() => navigate("/hubpage")}
          >
            Home
          </button>
          <span className="page-home-separator">›</span>
          <span className="page-home-current">Projects</span>
        </div>
        <h1 className="data-management-title">Data Management</h1>
        <div className="data-management-error" role="alert">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="data-management-container">
      <div className="page-home-nav" aria-label="Page navigation">
        <button
          type="button"
          className="page-home-link"
          onClick={() => navigate("/hubpage")}
        >
          Home
        </button>
        <span className="page-home-separator">›</span>
        <span className="page-home-current">Projects</span>
      </div>
      <h1 className="data-management-title">Data Management</h1>
      <p className="data-management-description">
        Edit project names, dates, and skills for all uploaded projects. Changes you make here are saved to the database and will appear in your Resume and Portfolio across the app. Click any project name, date, or skill to edit inline.
      </p>

      {dateError && (
        <div className="data-management-date-error" role="alert">
          {dateError}
        </div>
      )}

      {saveError && (
        <div className="data-management-save-error" role="alert">
          {saveError}
        </div>
      )}

      <div className="data-management-projects">
        <div className="data-management-section-header">
          <h2 className="data-management-section-title">
            Projects{projects.length > 0 && (
              <span className="data-management-count"> ({projects.length})</span>
            )}
          </h2>
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
            <p>No projects uploaded yet.</p>
            <button
              type="button"
              className="data-management-upload-btn"
              onClick={() => navigate("/uploadpage")}
            >
              Upload Projects
            </button>
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
                      <td className="data-management-col-project-name">
                        {editing?.type === "project_name" &&
                        editing?.projectSig === p.project_signature ? (
                          <input
                            type="text"
                            className="data-management-edit-input data-management-edit-input-full"
                            value={editing.value}
                            onChange={(e) =>
                              setEditing((prev) =>
                                prev ? { ...prev, value: e.target.value } : null
                              )
                            }
                            placeholder="Project name"
                            autoFocus
                            onBlur={() => {
                              if (editing.value.trim()) {
                                handleUpdateProjectName(p.project_signature, editing.value);
                              }
                              setEditing(null);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                if (editing.value.trim()) {
                                  handleUpdateProjectName(p.project_signature, editing.value);
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
                            onClick={() => {
                              setDateError(null);
                              setEditing({
                                type: "project_name",
                                projectSig: p.project_signature,
                                value: p.name || p.project_signature || "",
                              });
                            }}
                          >
                            {p.name || p.project_signature || "—"}
                          </button>
                        )}
                      </td>
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
                              } else if (editing.value.trim()) {
                                setDateError(DATE_FORMAT_ERR);
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
                                } else if (editing.value.trim()) {
                                  setDateError(DATE_FORMAT_ERR);
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
                            onClick={() => {
                              setDateError(null);
                              setEditing({
                                type: "project_created",
                                projectSig: p.project_signature,
                                value: formatDate(p.created_at) === "—" ? "" : formatDate(p.created_at),
                              });
                            }}
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
                              } else if (editing.value.trim()) {
                                setDateError(DATE_FORMAT_ERR);
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
                                } else if (editing.value.trim()) {
                                  setDateError(DATE_FORMAT_ERR);
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
                            onClick={() => {
                              setDateError(null);
                              setEditing({
                                type: "project_modified",
                                projectSig: p.project_signature,
                                value: formatDate(p.last_modified) === "—" ? "" : formatDate(p.last_modified),
                              });
                            }}
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
                            ) : (
                              <>
                                {p.skills.length === 0 && addingSkill?.projectSig !== p.project_signature ? (
                                  <p className="data-management-skills-empty">No skills.</p>
                                ) : null}
                                {p.skills.length > 0 ? (
                                <div className="data-management-skills-table-wrap">
                                <table className="data-management-skills-table">
                                  <thead>
                                    <tr>
                                      <th className="data-management-col-skill">Skill</th>
                                      <th className="data-management-col-source">Source</th>
                                      <th className="data-management-col-date">Date</th>
                                      <th className="data-management-skill-delete-col" aria-label="Remove skill" />
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {p.skills.map((s) => (
                                      <tr key={s.id}>
                                        <td className="data-management-col-skill">
                                          {editing?.type === "skill_name" &&
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
                                              placeholder="Skill name"
                                              autoFocus
                                              onBlur={() => {
                                                if (editing.value.trim()) {
                                                  handleUpdateSkillName(s.id, editing.value);
                                                }
                                                setEditing(null);
                                              }}
                                              onKeyDown={(e) => {
                                                if (e.key === "Enter") {
                                                  if (editing.value.trim()) {
                                                    handleUpdateSkillName(s.id, editing.value);
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
                                              onClick={() => {
                                                setDateError(null);
                                                setEditing({
                                                  type: "skill_name",
                                                  skillId: s.id,
                                                  value: s.skill || "",
                                                });
                                              }}
                                            >
                                              {s.skill || "—"}
                                            </button>
                                          )}
                                        </td>
                                        <td className="data-management-col-source">{formatSkillSource(s.source)}</td>
                                        <td className="data-management-col-date">
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
                                                  handleUpdateSkillDate(s.id, iso, p.project_signature);
                                                } else if (editing.value.trim()) {
                                                  setDateError(DATE_FORMAT_ERR);
                                                } else {
                                                  handleRemoveSkillDate(s.id, p.project_signature);
                                                }
                                                setEditing(null);
                                              }}
                                              onKeyDown={(e) => {
                                                if (e.key === "Enter") {
                                                  const iso = parseDdMmYyyyToIso(editing.value);
                                                  if (iso) {
                                                    handleUpdateSkillDate(s.id, iso, p.project_signature);
                                                  } else if (editing.value.trim()) {
                                                    setDateError(DATE_FORMAT_ERR);
                                                  } else {
                                                    handleRemoveSkillDate(s.id, p.project_signature);
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
                                              onClick={() => {
                                                setDateError(null);
                                                setEditing({
                                                  type: "skill_date",
                                                  skillId: s.id,
                                                  value: formatDate(s.date) === "—" ? "" : formatDate(s.date),
                                                });
                                              }}
                                            >
                                              {formatDate(s.date) || "—"}
                                            </button>
                                          )}
                                        </td>
                                        <td className="data-management-skill-delete-col">
                                          <button
                                            type="button"
                                            className="data-management-skill-delete-btn"
                                            onClick={() =>
                                              setDeleteSkillModal({
                                                skillId: s.id,
                                                skillName: s.skill || "this skill",
                                                projectSig: p.project_signature,
                                              })
                                            }
                                            disabled={saving || deletingSkill}
                                            title="Remove skill"
                                            aria-label={`Remove ${s.skill || "skill"}`}
                                          >
                                            ×
                                          </button>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                                </div>
                                ) : null}
                                {addingSkill?.projectSig === p.project_signature ? (
                                  <div className="data-management-add-skill">
                                    <input
                                      type="text"
                                      className="data-management-edit-input"
                                      placeholder="Skill name"
                                      value={addingSkill.skill}
                                      onChange={(e) =>
                                        setAddingSkill((prev) =>
                                          prev ? { ...prev, skill: e.target.value } : null
                                        )
                                      }
                                    />
                                    <select
                                      className="data-management-edit-input"
                                      value={addingSkill.source}
                                      onChange={(e) =>
                                        setAddingSkill((prev) =>
                                          prev
                                            ? { ...prev, source: e.target.value as "" | "code" | "non-technical" }
                                            : null
                                        )
                                      }
                                    >
                                      <option value="">Select</option>
                                      <option value="code">Technical skill</option>
                                      <option value="non-technical">Soft skill</option>
                                    </select>
                                    <input
                                      type="text"
                                      className="data-management-edit-input"
                                      placeholder="dd-mm-yyyy"
                                      value={addingSkill.date}
                                      onChange={(e) =>
                                        setAddingSkill((prev) =>
                                          prev ? { ...prev, date: e.target.value } : null
                                        )
                                      }
                                    />
                                    <button
                                      type="button"
                                      className="data-management-add-skill-btn"
                                      onClick={() => handleAddSkill(p.project_signature)}
                                      disabled={saving || !addingSkill.skill.trim() || !addingSkill.source}
                                    >
                                      Add
                                    </button>
                                    <button
                                      type="button"
                                      className="data-management-cancel-btn"
                                      onClick={() => setAddingSkill(null)}
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                ) : (
                                  <button
                                    type="button"
                                    className="data-management-add-skill-btn"
                                    onClick={() =>
                                      setAddingSkill({
                                        projectSig: p.project_signature,
                                        skill: "",
                                        source: "",
                                        date: "",
                                      })
                                    }
                                    disabled={saving}
                                  >
                                    + Add skill
                                  </button>
                                )}
                              </>
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

      {deleteSkillModal && (
        <div className="data-management-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="delete-skill-modal-title">
          <div className="data-management-modal data-management-modal-sm">
            <h2 id="delete-skill-modal-title" className="data-management-modal-title">Delete Skill</h2>
            <p className="data-management-modal-body">
              Are you sure you want to delete <strong>{deleteSkillModal.skillName}</strong>?
            </p>
            <div className="data-management-modal-actions">
              <button
                type="button"
                className="data-management-modal-cancel"
                onClick={() => setDeleteSkillModal(null)}
                disabled={deletingSkill}
              >
                Cancel
              </button>
              <button
                type="button"
                className="data-management-modal-confirm-danger"
                onClick={handleDeleteSkillConfirmed}
                disabled={deletingSkill}
              >
                {deletingSkill ? "Deleting…" : "Yes, Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

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
