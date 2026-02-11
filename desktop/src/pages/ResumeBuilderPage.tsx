import { useEffect, useState } from "react";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import "./ResumeManager/ResumeManager.css";
import { getResumes, type ResumeListItem } from "../api/resume";

export function ResumeBuilderPage() {
  const [resumeList, setResumeList] = useState<ResumeListItem[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
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
    </div>
  );
}

export default ResumeBuilderPage;
