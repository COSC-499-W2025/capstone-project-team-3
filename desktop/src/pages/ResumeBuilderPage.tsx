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
  downloadResumePDF, 
  downloadResumeTeX, 
  saveNewResume, 
  updateResume, 
  type ResumeListItem 
} from "../api/resume";

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

  // Load sidebar items
  useEffect(() => {
    getResumes().then(setBaseResumeList);
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

  return (
    <div className="page page--resume-builder">
      {/* Header with download button */}
      <div className="resume-builder__header">
        <div className="resume-builder__nav">
          <button 
            className="nav-link" 
            onClick={() => navigate('/')}
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
          />
        </div>
        <div className="resume-builder__main">
          <div className="container">
            <div className="card">
              {activeContent && (
                <ResumePreview 
                  resume={activeContent}
                  isEditing={isEditing}
                  onSectionChange={handleSectionChange}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeBuilderPage;