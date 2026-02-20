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
  
  // Convert skills array to comma-separated string
  const skillsText = skills.Skills.join(", ");

  useEffect(() => {
    // Always update the contenteditable element when skills prop changes
    // This ensures proper sync when switching resumes
    if (contentRef.current && isEditing) {
      // Only update if the current text is different to avoid cursor issues
      if (contentRef.current.textContent !== skillsText) {
        contentRef.current.textContent = skillsText;
      }
    }
  }, [skillsText, isEditing]);

  const handleBlur = () => {
    if (onChange && contentRef.current) {
      const text = contentRef.current.textContent || "";
      // Parse comma-separated text back into array
      const newSkills = text
        .split(",")
        .map(s => s.trim())
        .filter(s => s.length > 0);
      onChange({ Skills: newSkills });
    }
  };

  const handleInput = () => {
    // Optional: update state on every keystroke for live updates
    if (onChange && contentRef.current) {
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
            key={skillsText} // Force remount when skills change to prevent duplication
            ref={contentRef}
            className="resume-preview__skills-list"
            contentEditable={true}
            onBlur={handleBlur}
            onInput={handleInput}
            suppressContentEditableWarning={true}
            data-placeholder="Enter skills separated by commas..."
          />
        ) : (
          <p className="resume-preview__skills-list">
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
