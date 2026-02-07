import { Resume } from "../../api/resume_types";
import { EducationSection } from "./ResumeSections/EducationSection";
import { HeaderSection } from "./ResumeSections/HeaderSection";
import { ProjectsSection } from "./ResumeSections/ProjectSections";
import { SkillsSection } from "./ResumeSections/SkillsSection";

export function ResumePreview({ resume }: { resume: Resume }) {
  return (
    <main className="flex-1 bg-gray-100 overflow-auto flex justify-center">
      <div className="bg-white w-[816px] min-h-[1056px] p-12 font-serif text-sm shadow">
        <HeaderSection resume={resume} />
        <EducationSection education={resume.education} />
        <SkillsSection skills={resume.skills} />
        <ProjectsSection projects={resume.projects} />
      </div>
    </main>
  );
}
