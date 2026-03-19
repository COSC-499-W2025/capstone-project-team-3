import { useLayoutEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import {
  DndContext,
  DragEndEvent,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { arrayMove } from "@dnd-kit/sortable";
import { Resume, Skills, Project, Award, WorkExperience } from "../../api/resume_types";
import { EducationSection } from "./ResumeSections/EducationSection";
import { HeaderSection } from "./ResumeSections/HeaderSection";
import { ProjectsSection } from "./ResumeSections/ProjectSections";
import { SkillsSection } from "./ResumeSections/SkillsSection";
import { AwardsSection } from "./ResumeSections/AwardsSection";
import { WorkExperienceSection } from "./ResumeSections/WorkExperienceSection";
import "../../styles/ResumePreview.css";

/** Callback for section-only edits: parent merges into state. */
export type OnSectionChange = (
  section: "skills" | "projects" | "awards" | "work_experience",
  data: Skills | Project[] | Award[] | WorkExperience[],
) => void;

const PAGE_HEIGHT_PX = 1056; // A4-like proportion at 96dpi
const PAGE_GAP_PX = 32; // Space between pages
const EDIT_MODE_PAGE_GAP_PX = 96; // Extra vertical breathing room while editing
const CONTENT_PADDING_TOP = 40;
const CONTENT_PADDING_BOTTOM = 40;
const EDIT_MODE_PAGE_HEIGHT_DELTA_PX = 220;

/** Assign each section to a page so content doesn't break mid-section. Header only on page 1. */
function assignSectionsToPages(
  sectionHeights: number[],
  pageContentHeightPx: number,
): number[] {
  if (sectionHeights.length === 0) return [];
  const out: number[] = [];
  let page = 0;
  let used = 0;
  for (const h of sectionHeights) {
    if (used + h > pageContentHeightPx && used > 0) {
      page += 1;
      used = 0;
    }
    out.push(page);
    used += h;
  }
  return out;
}

export type ResumePreviewProps = {
  resume: Resume;
  isEditing?: boolean;
  onSectionChange?: OnSectionChange;
  /** When provided, an X button is shown per project in edit mode to remove the project from the resume (saved resumes only). */
  onProjectDelete?: (projectId: string) => void;
  /** When provided and in edit mode, "Add a project" is shown in the Projects section header (saved resumes only). */
  onAddProjectClick?: () => void;
  /** Show awards section (not the add button). */
  showAwards?: boolean;
  /** When true and in edit mode, show an "Add awards" control if the section is hidden. */
  allowAddAwards?: boolean;
  /** Show work experience section (not the add picker). */
  showWorkExperience?: boolean;
  /** When true and in edit mode, allow adding work experience via the add picker. */
  allowAddWorkExperience?: boolean;
};

export function ResumePreview({
  resume,
  isEditing = false,
  onSectionChange,
  onProjectDelete,
  onAddProjectClick,
  showAwards = false,
  allowAddAwards = false,
  showWorkExperience = false,
  allowAddWorkExperience = false,
}: ResumePreviewProps) {
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [sectionHeights, setSectionHeights] = useState<number[]>([]);
  const [sectionToPage, setSectionToPage] = useState<number[]>([]);
  const [showAddSectionMenu, setShowAddSectionMenu] = useState(false);

  const pageHeightPx = isEditing ? PAGE_HEIGHT_PX + EDIT_MODE_PAGE_HEIGHT_DELTA_PX : PAGE_HEIGHT_PX;
  const pageGapPx = isEditing ? EDIT_MODE_PAGE_GAP_PX : PAGE_GAP_PX;
  const pageContentHeightPx =
    pageHeightPx - CONTENT_PADDING_TOP - CONTENT_PADDING_BOTTOM;

  const projects = resume.projects ?? [];
  const workExperienceAreaVisible = showWorkExperience;
  const workExperienceSectionIndex = workExperienceAreaVisible ? 3 : -1;

  const firstProjectSectionIndex = workExperienceAreaVisible ? 4 : 3;
  const lastProjectSectionIndexExclusive = firstProjectSectionIndex + projects.length;

  // Awards are rendered only when explicitly requested (not as an "add placeholder" area).
  const awardsAreaVisible = showAwards;
  const awardsSectionIndex = awardsAreaVisible ? lastProjectSectionIndexExclusive : -1;

  const handleSkillsChange = (skills: Skills) => {
    onSectionChange?.("skills", skills);
  };

  const handleProjectChange = (globalIndex: number, project: Project) => {
    const newProjects = [...projects];
    if (globalIndex >= 0 && globalIndex < newProjects.length) {
      newProjects[globalIndex] = { ...newProjects[globalIndex], ...project };
      onSectionChange?.("projects", newProjects);
    }
  };

  const handleAwardsChange = (awards: Award[]) => {
    onSectionChange?.("awards", awards);
  };

  const handleWorkExperienceChange = (workExperience: WorkExperience[]) => {
    onSectionChange?.("work_experience", workExperience);
  };

  const seedEmptyAward = () => {
    const emptyAward: Award = {
      title: "",
      issuer: "",
      date: "",
      details: [],
    };
    onSectionChange?.("awards", [emptyAward]);
  };

  const seedEmptyWorkExperience = () => {
    const emptyWorkExperience: WorkExperience = {
      role: "",
      company: "",
      start_date: "",
      end_date: "",
      details: [],
    };
    onSectionChange?.("work_experience", [emptyWorkExperience]);
  };

  const canAddAwards = isEditing && allowAddAwards && !showAwards;
  const canAddWorkExperience = isEditing && allowAddWorkExperience && !showWorkExperience;

  const canShowAddSectionFooter = canAddAwards || canAddWorkExperience;

  // Footer is an extra "section" so it lands on the last page.
  const footerSectionIndex = canShowAddSectionFooter
    ? awardsAreaVisible
      ? awardsSectionIndex + 1
      : lastProjectSectionIndexExclusive
    : -1;

  const sectionCount =
    3 +
    (workExperienceAreaVisible ? 1 : 0) +
    projects.length +
    (awardsAreaVisible ? 1 : 0) +
    (canShowAddSectionFooter ? 1 : 0); // header, education, skills, work exp, projects, awards, footer

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const from = Number(active.id);
    const to = Number(over.id);
    if (Number.isNaN(from) || Number.isNaN(to) || from < 0 || to < 0 || from >= projects.length || to >= projects.length) return;
    const newProjects = arrayMove(projects, from, to);
    onSectionChange?.("projects", newProjects);
  };

  const sortableProjectIds = projects.map((_, i) => i);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor)
  );

  useLayoutEffect(() => {
    // Re-measure on the next frame too, since some newly mounted form controls
    // (e.g. textareas/inputs) can affect layout after the initial render.
    const measure = () => {
      const refs = sectionRefs.current;
      const heights: number[] = [];
      for (let i = 0; i < sectionCount; i++) {
        const el = refs[i];
        heights.push(el ? el.offsetHeight : 0);
      }
      setSectionHeights(heights);
    };

    measure();
    const raf = requestAnimationFrame(measure);
    return () => cancelAnimationFrame(raf);
  }, [
    resume,
    sectionCount,
    isEditing,
    showAwards,
    allowAddAwards,
    showWorkExperience,
    allowAddWorkExperience,
    showAddSectionMenu,
  ]);


  useLayoutEffect(() => {
    if (sectionHeights.length === 0) return;
    setSectionToPage(assignSectionsToPages(sectionHeights, pageContentHeightPx));
  }, [sectionHeights, pageContentHeightPx]);

  const pageCount =
    sectionToPage.length > 0 ? Math.max(1, 1 + Math.max(...sectionToPage)) : 1;
  const scrollHeight =
    pageCount * pageHeightPx + (pageCount > 1 ? (pageCount - 1) * pageGapPx : 0);

  const setSectionRef = (i: number) => (el: HTMLDivElement | null) => {
    sectionRefs.current[i] = el;
  };

  return (
    <main
      className={`resume-preview${isEditing ? " resume-preview--editing" : ""}`}
      style={
        {
          // Controls the height of page placeholders and page content.
          // Keep A4 proportions in non-edit mode; extend only in edit mode.
          ["--resume-page-height"]: `${pageHeightPx}px`,
        } as unknown as CSSProperties
      }
    >
      {/* Hidden measure container: same structure so section heights are accurate */}
      <div
        className="resume-preview__measure"
        aria-hidden
      >
        <div className="resume-preview__content">
          <div ref={setSectionRef(0)}>
            <HeaderSection resume={resume} />
          </div>
          <div ref={setSectionRef(1)}>
            <EducationSection education={resume.education} />
          </div>
          <div ref={setSectionRef(2)}>
            <SkillsSection 
              skills={resume.skills}
              isEditing={isEditing}
              onChange={handleSkillsChange}
            />
          </div>
          {showWorkExperience && (
            <div ref={setSectionRef(workExperienceSectionIndex)}>
              <WorkExperienceSection
                workExperience={resume.work_experience ?? []}
                isEditing={isEditing}
                onChange={handleWorkExperienceChange}
              />
            </div>
          )}

          {projects.map((_, i) => (
            <div key={i} ref={setSectionRef(firstProjectSectionIndex + i)}>
              <ProjectsSection
                projects={[projects[i]]}
                showHeading={i === 0}
              />
            </div>
          ))}

          {awardsAreaVisible && (
            <div ref={setSectionRef(awardsSectionIndex)}>
              <AwardsSection awards={resume.awards ?? []} isEditing={isEditing} onChange={handleAwardsChange} />
            </div>
          )}

          {canShowAddSectionFooter && (
            <div ref={setSectionRef(footerSectionIndex)}>
              <div className="resume-preview__add-section-footer">
                <button
                  type="button"
                  className="resume-preview__add-section-btn"
                  onClick={() => setShowAddSectionMenu((v) => !v)}
                >
                  <span className="resume-preview__add-section-plus" aria-hidden>
                    +
                  </span>
                  <span> Add section</span>
                </button>

                {showAddSectionMenu && (
                  <div className="resume-preview__add-section-menu">
                    {canAddAwards && (
                      <button
                        type="button"
                        className="resume-preview__add-section-option"
                        onClick={() => {
                          seedEmptyAward();
                          setShowAddSectionMenu(false);
                        }}
                      >
                        Awards & honours
                      </button>
                    )}
                    {canAddWorkExperience && (
                      <button
                        type="button"
                        className="resume-preview__add-section-option"
                        onClick={() => {
                          seedEmptyWorkExperience();
                          setShowAddSectionMenu(false);
                        }}
                      >
                        Work experience
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </div>

      <div
        className="resume-preview__scroll"
        style={{ minHeight: PAGE_HEIGHT_PX, height: scrollHeight }}
      >
        {Array.from({ length: pageCount }, (_, i) => (
          <div
            key={i}
            className="resume-preview__page"
            style={{ top: i * (pageHeightPx + pageGapPx) }}
            aria-hidden
          />
        ))}

        {sectionToPage.length > 0 &&
          (isEditing ? (
            <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
              <SortableContext
                items={sortableProjectIds}
                strategy={verticalListSortingStrategy}
              >
                {Array.from({ length: pageCount }, (_, pageIndex) => {
                  const sectionIndices = sectionToPage
                    .map((p, si) => (p === pageIndex ? si : -1))
                    .filter((si) => si >= 0);
                  if (sectionIndices.length === 0) return null;

                  const hasHeader = sectionIndices.includes(0);
                  const hasEducation = sectionIndices.includes(1);
                  const hasSkills = sectionIndices.includes(2);
                  const hasWorkExperienceArea =
                    workExperienceAreaVisible && sectionIndices.includes(workExperienceSectionIndex);
                  const hasFooter =
                    footerSectionIndex >= 0 && sectionIndices.includes(footerSectionIndex);
                  const hasAwardsArea =
                    awardsAreaVisible && sectionIndices.includes(awardsSectionIndex);
                  const projectSectionIndices = sectionIndices.filter(
                    (si) => si >= firstProjectSectionIndex && si < lastProjectSectionIndexExclusive,
                  );
                  const projectIndices = projectSectionIndices.map((si) => si - firstProjectSectionIndex);
                  const pageProjects = projectIndices
                    .filter((i) => i >= 0 && i < projects.length)
                    .map((i) => projects[i]);

                  return (
                    <div
                      key={pageIndex}
                      className="resume-preview__page-content"
                      style={{
                        top: pageIndex * (pageHeightPx + pageGapPx),
                        height: pageHeightPx,
                      }}
                    >
                      <div className="resume-preview__content">
                        {hasHeader && <HeaderSection resume={resume} />}
                        {hasEducation && (
                          <EducationSection education={resume.education} />
                        )}
                        {hasSkills && (
                          <SkillsSection
                            skills={resume.skills}
                            isEditing={isEditing}
                            onChange={handleSkillsChange}
                          />
                        )}
                        {hasWorkExperienceArea && (
                          <WorkExperienceSection
                            workExperience={resume.work_experience ?? []}
                            isEditing={isEditing}
                            onChange={handleWorkExperienceChange}
                          />
                        )}
                        {pageProjects.length > 0 && (
                          <ProjectsSection
                            projects={pageProjects}
                            showHeading={sectionIndices.includes(firstProjectSectionIndex)}
                            isEditing={isEditing}
                            onProjectChange={handleProjectChange}
                            onProjectDelete={onProjectDelete}
                            onAddProjectClick={sectionIndices.includes(firstProjectSectionIndex) ? onAddProjectClick : undefined}
                            projectStartIndex={projectIndices[0]}
                            enableSortable
                          />
                        )}
                        {hasAwardsArea && (
                          <div className="resume-preview__awards-wrapper">
                            <AwardsSection
                              awards={resume.awards ?? []}
                              isEditing={isEditing}
                              onChange={handleAwardsChange}
                            />
                          </div>
                        )}
                        {hasFooter && (
                          <div className="resume-preview__add-section-footer resume-preview__add-section-footer--page">
                            <button
                              type="button"
                              className="resume-preview__add-section-btn"
                              onClick={() => setShowAddSectionMenu((v) => !v)}
                            >
                              <span className="resume-preview__add-section-plus" aria-hidden>
                                +
                              </span>
                              <span>Add section</span>
                            </button>
                            {showAddSectionMenu && (
                              <div className="resume-preview__add-section-menu">
                                {canAddAwards && (
                                  <button
                                    type="button"
                                    className="resume-preview__add-section-option"
                                    onClick={() => {
                                      seedEmptyAward();
                                      setShowAddSectionMenu(false);
                                    }}
                                  >
                                    Awards & honours
                                  </button>
                                )}
                                {canAddWorkExperience && (
                                  <button
                                    type="button"
                                    className="resume-preview__add-section-option"
                                    onClick={() => {
                                      seedEmptyWorkExperience();
                                      setShowAddSectionMenu(false);
                                    }}
                                  >
                                    Work experience
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </SortableContext>
            </DndContext>
          ) : (
            Array.from({ length: pageCount }, (_, pageIndex) => {
              const sectionIndices = sectionToPage
                .map((p, si) => (p === pageIndex ? si : -1))
                .filter((si) => si >= 0);
              if (sectionIndices.length === 0) return null;

              const hasHeader = sectionIndices.includes(0);
              const hasEducation = sectionIndices.includes(1);
              const hasSkills = sectionIndices.includes(2);
              const hasWorkExperienceArea =
                workExperienceAreaVisible && sectionIndices.includes(workExperienceSectionIndex);
              const hasAwardsArea =
                awardsAreaVisible && sectionIndices.includes(awardsSectionIndex);
              const projectSectionIndices = sectionIndices.filter(
                (si) => si >= firstProjectSectionIndex && si < lastProjectSectionIndexExclusive,
              );
              const projectIndices = projectSectionIndices.map((si) => si - firstProjectSectionIndex);
              const pageProjects = projectIndices
                .filter((i) => i >= 0 && i < projects.length)
                .map((i) => projects[i]);

              return (
                <div
                  key={pageIndex}
                  className="resume-preview__page-content"
                  style={{
                    top: pageIndex * (pageHeightPx + pageGapPx),
                    height: pageHeightPx,
                  }}
                >
                  <div className="resume-preview__content">
                    {hasHeader && <HeaderSection resume={resume} />}
                    {hasEducation && (
                      <EducationSection education={resume.education} />
                    )}
                    {hasSkills && (
                      <SkillsSection
                        skills={resume.skills}
                        isEditing={isEditing}
                        onChange={handleSkillsChange}
                      />
                    )}
                    {hasWorkExperienceArea && (
                      <WorkExperienceSection
                        workExperience={resume.work_experience ?? []}
                        isEditing={isEditing}
                        onChange={handleWorkExperienceChange}
                      />
                    )}
                    {pageProjects.length > 0 && (
                      <ProjectsSection
                        projects={pageProjects}
                        showHeading={sectionIndices.includes(firstProjectSectionIndex)}
                        isEditing={isEditing}
                        onProjectChange={handleProjectChange}
                        onProjectDelete={onProjectDelete}
                        onAddProjectClick={sectionIndices.includes(firstProjectSectionIndex) ? onAddProjectClick : undefined}
                        projectStartIndex={projectIndices[0]}
                      />
                    )}
                    {hasAwardsArea && (
                      <div className="resume-preview__awards-wrapper">
                        <AwardsSection
                          awards={resume.awards ?? []}
                          isEditing={isEditing}
                          onChange={handleAwardsChange}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )) }
      </div>
    </main>
  );
}
