import { useEffect, useState } from "react";
import { Resume } from "../api/resume_types";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import { ResumePreview } from "./ResumeManager/ResumePreview";
import "./ResumeManager/ResumeManager.css";
import { buildResume } from "../api/resume";

export function ResumeBuilderPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
  buildResume().then((r) => setResumes([r]));
}, []);

  const active = resumes[activeIndex];

  return (
    <div className="page page--resume-builder">
      <div className="card card--sidebar">
        <ResumeSidebar
          resumes={resumes}
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
