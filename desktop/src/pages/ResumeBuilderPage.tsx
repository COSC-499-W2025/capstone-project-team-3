import { useEffect, useState } from "react";
import { Resume } from "../api/resume_types";
import { ResumeSidebar } from "./ResumeManager/ResumeSidebar";
import { ResumePreview } from "./ResumeManager/ResumePreview";
import "./ResumeManager/ResumeManager.css";
import { buildResume } from "../api/resume";

export function ResumeBuilderPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
  buildResume().then((r) => setResumes([r]));
}, []);

  const active = resumes[activeIndex];

  return (
    <div className="page">
      <div className="container">
        <div className="grid">
          <div className="card">
            {active && <ResumePreview resume={active} />}
          </div>
          <div className="card">
            <ResumeSidebar
              resumes={resumes}
              activeIndex={activeIndex}
              onSelect={setActiveIndex}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeBuilderPage;
