import { Skills } from "../../../api/resume_types";
import { useRef, useEffect } from "react";

export function SkillsSection({ 
  skills, 
  isEditing = false, 
  onChange 
}: { 
  skills: Skills;
  isEditing?: boolean;
  onChange?: (skills: Skills) => void;
}) {
  const contentRef = useRef<HTMLParagraphElement>(null);
  const skipSyncRef = useRef(false);

  const skillsText = skills.Skills.join(", ");

  useEffect(() => {
    if (skipSyncRef.current) {
      skipSyncRef.current = false;
      return;
    }
    if (contentRef.current && isEditing) {
      if (contentRef.current.textContent !== skillsText) {
        contentRef.current.textContent = skillsText;
      }
    }
  }, [skillsText, isEditing]);

  const handleBlur = () => {
    if (onChange && contentRef.current) {
      skipSyncRef.current = true;
      const text = contentRef.current.textContent || "";
      const newSkills = text
        .split(",")
        .map(s => s.trim())
        .filter(s => s.length > 0);
      onChange({ Skills: newSkills });
    }
  };

  const handleInput = () => {
    if (onChange && contentRef.current) {
      skipSyncRef.current = true;
      const text = contentRef.current.textContent || "";
      const newSkills = text
        .split(",")
        .map(s => s.trim())
        .filter(s => s.length > 0);
      onChange({ Skills: newSkills });
    }
  };

  return (
    <section className="resume-preview__section">
      <h2 className="resume-preview__heading">Skills</h2>
      <div className="resume-preview__skills-row">
        <span className="resume-preview__skills-label">Skills:</span>
        {isEditing ? (
          <p 
            key="skills-edit"
            ref={contentRef}
            className="resume-preview__skills-list"
            contentEditable={true}
            onBlur={handleBlur}
            onInput={handleInput}
            suppressContentEditableWarning={true}
            data-placeholder="Enter skills separated by commas..."
          />
        ) : (
          <p key="skills-display" className="resume-preview__skills-list">
            {skills.Skills.map((s, i) => (
              <span key={i}>
                <span className="resume-preview__skill-inline">{s}</span>
                {i < skills.Skills.length - 1 ? ", " : ""}
              </span>
            ))}
          </p>
        )}
      </div>
    </section>
  );
}
