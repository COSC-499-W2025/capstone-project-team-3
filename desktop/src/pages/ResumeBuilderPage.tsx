import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Resume, Skills, Project } from "../api/resume_types";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import { ResumePreview } from "./ResumeManager/ResumePreview";
import "../styles/ResumeManager.css";
import {
  getResumes,
  buildResume,
  getResumeById,
  previewResume,
  deleteResume,
  deleteProjectFromResume,
  addProjectsToResume,
  downloadResumePDF,
  downloadResumeTeX,
  saveNewResume,
  updateResume,
  type ResumeListItem,
} from "../api/resume";
import { getProjects, type Project as ApiProject } from "../api/projects";

/** Convert YYYY-MM to YYYY-MM-01 for backend fromisoformat. */
function toISOStartOfMonth(ym: string): string {
  if (!/^\d{4}-\d{2}$/.test(ym)) return ym;
  return `${ym}-01`;
}

export function ResumeBuilderPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  // const [resumes, setResumes] = useState<Resume[]>([]);
  const [baseResumeList, setBaseResumeList] = useState<ResumeListItem[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeContent, setActiveContent] = useState<Resume | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [previewProjectIds, setPreviewProjectIds] = useState<string[]>([]);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveResumeName, setSaveResumeName] = useState("");
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedSections, setEditedSections] = useState<Set<string>>(new Set());
  const [hasProjects, setHasProjects] = useState(true); // assume true until we fetch
  const [showAddProjectModal, setShowAddProjectModal] = useState(false);
  const [addProjectModalProjects, setAddProjectModalProjects] = useState<ApiProject[]>([]);
  const [addProjectModalSelected, setAddProjectModalSelected] = useState<Set<string>>(new Set());
  const [addProjectModalLoading, setAddProjectModalLoading] = useState(false);
  const [addProjectModalSubmitting, setAddProjectModalSubmitting] = useState(false);
  const [addProjectModalError, setAddProjectModalError] = useState<string | null>(null);

  // Computed: inject preview resume into sidebar if in preview mode
  const isPreviewMode = previewProjectIds.length > 0;
  const resumeList: ResumeListItem[] = isPreviewMode
    ? [
        { id: null, name: "Preview Resume (Unsaved)", is_master: false },
        ...baseResumeList,
      ]
    : baseResumeList;

  // Check if current resume is master
  const currentResume = resumeList[activeIndex];
  const isMasterResume = currentResume?.is_master || currentResume?.id === 1;
  const showSaveButton = !isMasterResume;

  // When there are no projects, sidebar hides master resume; visible list is only non-master
  const visibleResumeList = hasProjects
    ? resumeList
    : resumeList.filter((r) => !(r.is_master || r.id === 1));
  const showEmptyState = visibleResumeList.length === 0;

  // When master is hidden (no projects), default selection to the first resume in the sidebar
  useEffect(() => {
    if (hasProjects || visibleResumeList.length === 0) return;
    const selected = resumeList[activeIndex];
    const isSelectedMaster = selected?.is_master || selected?.id === 1;
    if (isSelectedMaster) {
      const firstVisibleIndex = resumeList.findIndex((r) => !(r.is_master || r.id === 1));
      if (firstVisibleIndex >= 0) setActiveIndex(firstVisibleIndex);
    }
  }, [hasProjects, visibleResumeList.length, resumeList, activeIndex]);

  // Load sidebar items
  useEffect(() => {
    getResumes().then(setBaseResumeList);
  }, []);

  // Load project count to show/hide master resume and enable/disable Tailor button
  useEffect(() => {
    getProjects()
      .then((projects) => setHasProjects(projects.length > 0))
      .catch(() => setHasProjects(false));
  }, []);

  // Check for preview mode (project_ids in URL)
  useEffect(() => {
    const projectIds = searchParams.getAll('project_ids');
    if (projectIds.length > 0) {
      setPreviewProjectIds(projectIds);
      setActiveIndex(0); // Preview is always first in the list
      previewResume(projectIds).then(setActiveContent);
    } else {
      setPreviewProjectIds([]);
    }
  }, [searchParams]);

  // Load projects when Add Project modal opens
  useEffect(() => {
    if (!showAddProjectModal) return;
    setAddProjectModalError(null);
    setAddProjectModalSelected(new Set());
    setAddProjectModalLoading(true);
    getProjects()
      .then(setAddProjectModalProjects)
      .catch((err) => setAddProjectModalError(err instanceof Error ? err.message : "Failed to load projects"))
      .finally(() => setAddProjectModalLoading(false));
  }, [showAddProjectModal]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.dropdown')) {
        setShowDownloadMenu(false);
      }
    };

    if (showDownloadMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showDownloadMenu]);

  // Load content whenever selection changes (only if not in preview mode)
  useEffect(() => {
    if (isPreviewMode) return; // Don't load from sidebar in preview mode
    if (baseResumeList.length === 0) return;
    const selected = baseResumeList[activeIndex];
    if (!selected) return;

    if (selected.is_master || selected.id === 1) {
      buildResume().then(setActiveContent);
    } else if (selected.id != null) {
      getResumeById(selected.id).then(setActiveContent);
    }
  }, [baseResumeList, activeIndex, isPreviewMode]);

  const handleEditResume = () => {
    setIsEditing(true);
    setEditedSections(new Set()); // Clear edited sections when entering edit mode
  };

  const handleSectionChange = (section: "skills" | "projects", data: Skills | Project[]) => {
    setActiveContent(prev => (prev ? { ...prev, [section]: data } : prev));
    setEditedSections(prev => new Set(prev).add(section));
  };

  const handleSelectResume = (index: number) => {
    // Exit edit mode when switching resumes
    setIsEditing(false);
    setEditedSections(new Set()); // Clear edited sections when switching
    
    // If selecting the preview resume (index 0 in preview mode), do nothing
    if (isPreviewMode && index === 0) {
      return;
    }

    // If selecting a saved resume while in preview mode, exit preview
    if (isPreviewMode && index > 0) {
      // Clear URL params to exit preview mode
      navigate('/resumebuilderpage', { replace: true });
      // Adjust index since preview is injected at position 0
      const adjustedIndex = index - 1;
      setActiveIndex(adjustedIndex);
      
      const selected = baseResumeList[adjustedIndex];
      if (selected) {
        if (selected.is_master || selected.id === 1) {
          buildResume().then(setActiveContent);
        } else if (selected.id != null) {
          getResumeById(selected.id).then(setActiveContent);
        }
      }
    } else {
      // Normal selection when not in preview mode
      if (index !== activeIndex) {
        setActiveContent(null); // Don’t show previous resume while new one loads
      }
      // Normal selection when not in preview mode
      setActiveIndex(index);
    }
  };

  const handleDeleteResume = async (resumeId: number) => {
    try {
      await deleteResume(resumeId);
      // Refresh the resume list after deletion
      const updatedList = await getResumes();
      setBaseResumeList(updatedList);
      // Reset to first resume if current one was deleted
      if (activeIndex >= updatedList.length) {
        setActiveIndex(Math.max(0, updatedList.length - 1));
      }
    } catch (error) {
      console.error('Failed to delete resume:', error);
      alert('Failed to delete resume. Please try again.');
    }
  };

  const handleProjectDelete = async (projectId: string) => {
    const resumeId = currentResume?.id;
    if (resumeId == null || isMasterResume) return;
    try {
      await deleteProjectFromResume(resumeId, projectId);
      const updated = await getResumeById(resumeId);
      setActiveContent(updated);
    } catch (error) {
      console.error('Failed to remove project from resume:', error);
      alert('Failed to remove project from resume. Please try again.');
    }
  };

  const handleDownload = async (format: 'pdf' | 'tex') => {
    try {
      setDownloading(true);
      setShowDownloadMenu(false);
      
      const currentResume = resumeList[activeIndex];
      const filename = currentResume?.name || 'resume';
      
      // Build params based on current mode
      let params: { projectIds?: string[], resumeId?: number, filename: string } | undefined;
      
      if (isPreviewMode) {
        // Preview mode: use project IDs
        params = { projectIds: previewProjectIds, filename };
      } else if (currentResume?.id && !currentResume.is_master) {
        // Saved resume: use resume ID
        params = { resumeId: currentResume.id, filename };
      } else {
        // Master resume: no special params, just filename
        params = { filename };
      }
      
      if (format === 'pdf') {
        await downloadResumePDF(params);
      } else {
        await downloadResumeTeX(params);
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download resume. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const handleOpenSaveModal = () => {
    if (isPreviewMode) {
      // Generate default name for preview resume
      const timestamp = Math.floor(Math.random() * 10000000);
      setSaveResumeName(`Resume - ${timestamp}`);
      setShowSaveModal(true);
    } else {
      // For existing saved resumes, update directly
      handleUpdateExistingResume();
    }
  };

  const handleUpdateExistingResume = async () => {
    if (!activeContent || !currentResume?.id) return;
    try {
      setSaving(true);
      
      // Build payload with only edited sections
      const payload: { skills?: string[], projects?: any[] } = {};
      
      if (editedSections.has('skills')) {
        // Transform { Skills: [...] } to [...]
        payload.skills = activeContent.skills.Skills;
      }
      
      // If projects were edited, include them
      // (For now, only skills are editable, but this is future-ready)
      if (editedSections.has('projects')) {
        payload.projects = activeContent.projects.map((project, index) => {
          if (!project.project_id) {
            throw new Error(
              "Cannot save project edits: project_id missing. Reload the resume and try again."
            );
          }
          const start = project.start_date ? toISOStartOfMonth(project.start_date) : undefined;
          const end = project.end_date ? toISOStartOfMonth(project.end_date) : undefined;
          return {
            project_id: project.project_id,
            project_name: project.title,
            ...(start && { start_date: start }),
            ...(end && { end_date: end }),
            skills: project.skills,
            bullets: project.bullets,
            display_order: index + 1
          };
        });
      }
      
      await updateResume(currentResume.id, payload);
      setIsEditing(false); // Exit edit mode after save
      setEditedSections(new Set()); // Clear edited sections
    } catch (error) {
      console.error('Failed to update resume:', error);
      alert('Failed to update resume. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveResume = async () => {
    if (!saveResumeName.trim()) {
      alert('Please enter a resume name');
      return;
    }

    try {
      setSaving(true);
      const result = await saveNewResume(saveResumeName, previewProjectIds);
      // console.log('Resume saved with ID:', result.resume_id);
      
      // Reload resume list
      const updatedList = await getResumes();
      setBaseResumeList(updatedList);
      
      // Exit preview mode and navigate to the newly saved resume
      navigate('/resumebuilderpage', { replace: true });
      
      // Find the index of the newly saved resume
      const newIndex = updatedList.findIndex(r => r.id === result.resume_id);
      if (newIndex !== -1) {
        setActiveIndex(newIndex);
      }
      
      setShowSaveModal(false);
      setSaveResumeName("");
    } catch (error) {
      console.error('Failed to save resume:', error);
      alert('Failed to save resume. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSaveModal = () => {
    setShowSaveModal(false);
    setSaveResumeName("");
  };

  const handleCloseAddProjectModal = () => {
    setShowAddProjectModal(false);
    setAddProjectModalError(null);
    setAddProjectModalSelected(new Set());
  };

  const toggleAddProjectSelection = (projectId: string) => {
    setAddProjectModalSelected((prev) => {
      const next = new Set(prev);
      if (next.has(projectId)) next.delete(projectId);
      else next.add(projectId);
      return next;
    });
  };

  const handleAddProjectsToResume = async () => {
    const resumeId = currentResume?.id;
    if (resumeId == null || isMasterResume) return;
    const ids = Array.from(addProjectModalSelected);
    if (ids.length === 0) return;
    try {
      setAddProjectModalSubmitting(true);
      setAddProjectModalError(null);
      await addProjectsToResume(resumeId, ids);
      const updated = await getResumeById(resumeId);
      setActiveContent(updated);
      setEditedSections((prev) => new Set(prev).add("projects"));
      handleCloseAddProjectModal();
    } catch (error) {
      setAddProjectModalError(error instanceof Error ? error.message : "Failed to add projects");
    } finally {
      setAddProjectModalSubmitting(false);
    }
  };

  const currentResumeProjectIds = new Set(
    (activeContent?.projects ?? []).map((p) => p.project_id).filter(Boolean) as string[]
  );
  const addProjectModalAvailable = addProjectModalProjects.filter(
    (p) => !currentResumeProjectIds.has(p.id)
  );

  return (
    <div className="page page--resume-builder">
      {/* Header with download button */}
      <div className="resume-builder__header">
        <div className="resume-builder__nav">
          <button 
            className="nav-link" 
            onClick={() => navigate('/hubpage')}
          >
            Home
          </button>
          <span className="nav-separator">&gt;</span>
          <span className="nav-current">Résumé</span>
        </div>
        <div className="resume-builder__actions">
          {showSaveButton && (
            <button 
              className="btn btn--secondary" 
              onClick={handleOpenSaveModal}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          )}
          <button
            className="btn btn--ats"
            onClick={() => navigate('/atsscoringpage')}
            title="Check ATS compatibility score for this resume"
          >
            ATS Score
          </button>
          <div className="dropdown">
            <button 
              className="btn btn--primary"
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              disabled={downloading}
            >
              {downloading ? 'Downloading...' : 'Download'}
              <span className="dropdown-arrow">▼</span>
            </button>
            {showDownloadMenu && (
              <div className="dropdown-menu">
                <button 
                  className="dropdown-item"
                  onClick={() => handleDownload('pdf')}
                >
                  Download as PDF
                </button>
                <button 
                  className="dropdown-item"
                  onClick={() => handleDownload('tex')}
                >
                  Download as TeX
                </button>

              </div>
            )}
          </div>
        </div>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={handleCloseSaveModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Save Résumé version as:</h2>
            <input
              type="text"
              className="modal-input"
              value={saveResumeName}
              onChange={(e) => setSaveResumeName(e.target.value)}
              placeholder="Enter resume name..."
              autoFocus
            />
            <button 
              className="btn btn--primary modal-save-btn" 
              onClick={handleSaveResume}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      )}

      {/* Add Project Modal */}
      {showAddProjectModal && (
        <div className="modal-overlay" onClick={handleCloseAddProjectModal}>
          <div
            className="modal-content modal-content--add-project"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="modal-title">Add a project</h2>
            <p className="modal-subtitle">
              Choose which projects to add to this resume.
            </p>
            {addProjectModalError && (
              <p className="modal-error" role="alert">
                {addProjectModalError}
              </p>
            )}
            {addProjectModalLoading ? (
              <p className="modal-loading">Loading projects...</p>
            ) : (
              <>
                <div className="modal-table-wrap">
                  <table className="projects-table modal-projects-table">
                    <thead>
                      <tr className="table-header">
                        <th>Project Name</th>
                        <th>Skills</th>
                        <th>Date Added</th>
                      </tr>
                    </thead>
                    <tbody>
                      {addProjectModalAvailable.map((project) => (
                        <tr
                          key={project.id}
                          className="project-row"
                          onClick={() => toggleAddProjectSelection(project.id)}
                        >
                          <td onClick={(e) => e.stopPropagation()}>
                            <label className="project-checkbox-label">
                              <input
                                type="checkbox"
                                checked={addProjectModalSelected.has(project.id)}
                                onChange={() => toggleAddProjectSelection(project.id)}
                                className="project-checkbox"
                              />
                              <span>{project.name}</span>
                            </label>
                          </td>
                          <td>
                            {(project.skills ?? []).slice(0, 3).join(", ")}
                            {(project.skills ?? []).length > 3 && ", ..."}
                          </td>
                          <td>
                            {new Date(project.date_added).toLocaleDateString("en-GB", {
                              day: "2-digit",
                              month: "2-digit",
                              year: "numeric",
                            }).replace(/\//g, "-")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {addProjectModalAvailable.length === 0 && !addProjectModalLoading && (
                  <p className="modal-empty">No other projects to add. All your projects are already on this resume.</p>
                )}
                <div className="modal-actions">
                  <button
                    type="button"
                    className="btn btn--secondary"
                    onClick={handleCloseAddProjectModal}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn--primary"
                    onClick={handleAddProjectsToResume}
                    disabled={addProjectModalSubmitting || addProjectModalSelected.size === 0}
                  >
                    {addProjectModalSubmitting ? "Adding..." : "Add to resume"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="resume-builder__content">
        <div className="card card--sidebar">
          <ResumeSidebar
            resumeList={resumeList}
            activeIndex={activeIndex}
            onTailorNew={() => navigate('/projectselectionpage')}
            onSelect={handleSelectResume}
            onDelete={handleDeleteResume}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen((v) => !v)}
            onEdit={handleEditResume}
            hasProjects={hasProjects}
          />
        </div>
        <div className="resume-builder__main">
          <div className="container">
            <div className="card">
              {showEmptyState ? (
                <div className="resume-builder__empty-state">
                  <p className="resume-builder__empty-state-title">No projects to include on resume</p>
                  <p className="resume-builder__empty-state-message">
                    Upload a project to get started, then tailor a new resume from the sidebar.
                  </p>
                </div>
              ) : (
                activeContent && (
                  <ResumePreview
                    resume={activeContent}
                    isEditing={isEditing}
                    onSectionChange={handleSectionChange}
                    onProjectDelete={!isMasterResume && currentResume?.id != null ? handleProjectDelete : undefined}
                    onAddProjectClick={
                      isEditing && !isMasterResume && currentResume?.id != null
                        ? () => setShowAddProjectModal(true)
                        : undefined
                    }
                  />
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeBuilderPage;