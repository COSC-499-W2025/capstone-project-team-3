import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Resume } from "../api/resume_types";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import { ResumePreview } from "./ResumeManager/ResumePreview";
import "../styles/ResumeManager.css";
import { getResumes, buildResume, getResumeById, previewResume, deleteResume, type ResumeListItem } from "../api/resume";

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

  // Computed: inject preview resume into sidebar if in preview mode
  const isPreviewMode = previewProjectIds.length > 0;
  const resumeList: ResumeListItem[] = isPreviewMode
    ? [
        { id: null, name: "Preview Resume (Unsaved)", is_master: false },
        ...baseResumeList,
      ]
    : baseResumeList;

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

  const handleSelectResume = (index: number) => {
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
  const handleDownload = async (format: 'pdf' | 'tex') => {
    try {
      setDownloading(true);
      setShowDownloadMenu(false);
      
      const currentResume = resumeList[activeIndex];
      const filename = currentResume?.name || 'resume';
      
      // TODO: Connect to backend download functionality
      console.log(`Download ${format.toUpperCase()} requested for: ${filename}`);
      
      // Simulate download delay
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download resume. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="page page--resume-builder">
      <div className="card card--sidebar">
        <ResumeSidebar
          resumeList={resumeList}
          activeIndex={activeIndex}
          onTailorNew={() => navigate('/projectselectionpage')}
          onSelect={handleSelectResume}
          onDelete={handleDeleteResume}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen((v) => !v)}
        />
      {/* Header with download button */}
      <div className="resume-builder__header">
        <div className="resume-builder__nav">
          {/* Placeholder for future navigation */}
        </div>
        <div className="resume-builder__actions">
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

      <div className="resume-builder__content">
        <div className="card card--sidebar">
          <ResumeSidebar
            resumeList={resumeList}
            activeIndex={activeIndex}
            onTailorNew={() => navigate('/projectselectionpage')}
            onSelect={handleSelectResume}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen((v) => !v)}
          />
        </div>
        <div className="resume-builder__main">
          <div className="container">
            <div className="card">
              {activeContent && <ResumePreview resume={activeContent} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeBuilderPage;