import { useEffect, useState } from "react";
import { Resume } from "../api/resume_types";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import { ResumePreview } from "./ResumeManager/ResumePreview";
import "../styles/ResumeManager.css";
import { getResumes, buildResume, getResumeById, type ResumeListItem } from "../api/resume";

export function ResumeBuilderPage() {
  // const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeList, setResumeList] = useState<ResumeListItem[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeContent, setActiveContent] = useState<Resume | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load sidebar items
  useEffect(() => {
    getResumes().then(setResumeList);
  }, []);

  // Load content whenever selection changes
  useEffect(() => {
    if (resumeList.length === 0) return;
    const selected = resumeList[activeIndex];
    if (!selected) return;

    if (selected.is_master || selected.id === 1) {
      buildResume().then(setActiveContent);
    } else if (selected.id != null) {
      getResumeById(selected.id).then(setActiveContent);
    }
  }, [resumeList, activeIndex]);

  return (
    <div className="page page--resume-builder">
      <div className="card card--sidebar">
        <ResumeSidebar
          resumeList={resumeList}
          activeIndex={activeIndex}
          onSelect={setActiveIndex}
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
  );
}

export default ResumeBuilderPage;
