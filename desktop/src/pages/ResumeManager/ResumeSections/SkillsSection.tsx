import { Skills } from "../../../api/resume_types";
import { useEffect, useRef } from "react";

export function SkillsSection({ 
  skills, 
  isEditing = false, 
  onChange 
}: { 
  skills: Skills;
  isEditing?: boolean;
  onChange?: (skills: Skills) => void;
}) {
  const proficientRef = useRef<HTMLParagraphElement>(null);
  const familiarRef = useRef<HTMLParagraphElement>(null);
  const skipSyncProRef = useRef(false);
  const skipSyncFamRef = useRef(false);

  const proficientText = skills.Proficient.join(", ");
  const familiarText = skills.Familiar.join(", ");

  const parseCommaSkills = (text: string): string[] =>
    text
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

  const commitProficient = () => {
    if (!onChange || !proficientRef.current) return;
    skipSyncProRef.current = true;
    const text = proficientRef.current.textContent || "";
    const newProficient = parseCommaSkills(text);
    onChange({ Proficient: newProficient, Familiar: skills.Familiar });
  };

  const commitFamiliar = () => {
    if (!onChange || !familiarRef.current) return;
    skipSyncFamRef.current = true;
    const text = familiarRef.current.textContent || "";
    const newFamiliar = parseCommaSkills(text);
    onChange({ Proficient: skills.Proficient, Familiar: newFamiliar });
  };

  useEffect(() => {
    if (!isEditing || !proficientRef.current) return;
    if (skipSyncProRef.current) {
      skipSyncProRef.current = false;
      return;
    }
    if (proficientRef.current.textContent !== proficientText) {
      proficientRef.current.textContent = proficientText;
    }
  }, [proficientText, isEditing]);

  useEffect(() => {
    if (!isEditing || !familiarRef.current) return;
    if (skipSyncFamRef.current) {
      skipSyncFamRef.current = false;
      return;
    }
    if (familiarRef.current.textContent !== familiarText) {
      familiarRef.current.textContent = familiarText;
    }
  }, [familiarText, isEditing]);

  const renderInlineSkills = (items: string[]) =>
    items.map((s, i) => (
      <span key={i}>
        <span className="resume-preview__skill-inline">{s}</span>
        {i < items.length - 1 ? ", " : ""}
      </span>
    ));

  return (
    <section className="resume-preview__section">
      <h2 className="resume-preview__heading">Skills</h2>
      <div className="resume-preview__skills-row">
        {isEditing ? (
          <div className="resume-preview__skills-editors">
            <div className="resume-preview__skills-bucket-row">
              <span className="resume-preview__skills-bucket-label">Proficient:</span>
              <p
                key="skills-edit-proficient"
                ref={proficientRef}
                className="resume-preview__skills-list resume-preview__skills-editor resume-preview__skills-bucket-items"
                contentEditable={true}
                onBlur={commitProficient}
                onInput={commitProficient}
                suppressContentEditableWarning={true}
                data-placeholder="Enter Proficient skills separated by commas..."
              />
            </div>
            <div className="resume-preview__skills-bucket-row">
              <span className="resume-preview__skills-bucket-label">Familiar:</span>
              <p
                key="skills-edit-familiar"
                ref={familiarRef}
                className="resume-preview__skills-list resume-preview__skills-editor resume-preview__skills-bucket-items"
                contentEditable={true}
                onBlur={commitFamiliar}
                onInput={commitFamiliar}
                suppressContentEditableWarning={true}
                data-placeholder="Enter Familiar skills separated by commas..."
              />
            </div>
          </div>
        ) : (
          <div key="skills-display" className="resume-preview__skills-list">
            {skills.Proficient.length > 0 && (
              <div className="resume-preview__skills-bucket-row">
                <span className="resume-preview__skills-bucket-label">Proficient:</span>
                <span className="resume-preview__skills-bucket-items">
                  {renderInlineSkills(skills.Proficient)}
                </span>
              </div>
            )}
            {skills.Familiar.length > 0 && (
              <div className="resume-preview__skills-bucket-row">
                <span className="resume-preview__skills-bucket-label">Familiar:</span>
                <span className="resume-preview__skills-bucket-items">
                  {renderInlineSkills(skills.Familiar)}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
