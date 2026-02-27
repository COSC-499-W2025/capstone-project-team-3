import { useLayoutEffect, useRef, useState } from "react";
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
import { Resume, Skills, Project } from "../../api/resume_types";
import { EducationSection } from "./ResumeSections/EducationSection";
import { HeaderSection } from "./ResumeSections/HeaderSection";
import { ProjectsSection } from "./ResumeSections/ProjectSections";
import { SkillsSection } from "./ResumeSections/SkillsSection";
import "../../styles/ResumePreview.css";

/** Callback for section-only edits: parent merges into state. */
export type OnSectionChange = (section: "skills" | "projects", data: Skills | Project[]) => void;

const PAGE_HEIGHT_PX = 1056; // A4-like proportion at 96dpi
const PAGE_GAP_PX = 32; // Space between pages
const CONTENT_PADDING_TOP = 40;
const CONTENT_PADDING_BOTTOM = 40;
const PAGE_CONTENT_HEIGHT = PAGE_HEIGHT_PX - CONTENT_PADDING_TOP - CONTENT_PADDING_BOTTOM;

/** Assign each section to a page so content doesn't break mid-section. Header only on page 1. */
function assignSectionsToPages(sectionHeights: number[]): number[] {
  if (sectionHeights.length === 0) return [];
  const out: number[] = [];
  let page = 0;
  let used = 0;
  for (const h of sectionHeights) {
    if (used + h > PAGE_CONTENT_HEIGHT && used > 0) {
      page += 1;
      used = 0;
    }
    out.push(page);
    used += h;
  }
  return out;
}

export function ResumePreview({
  resume,
  isEditing = false,
  onSectionChange,
  onProjectDelete,
}: {
  resume: Resume;
  isEditing?: boolean;
  onSectionChange?: OnSectionChange;
  /** When provided, an X button is shown per project in edit mode to remove the project from the resume (saved resumes only). */
  onProjectDelete?: (projectId: string) => void;
}) {
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [sectionHeights, setSectionHeights] = useState<number[]>([]);
  const [sectionToPage, setSectionToPage] = useState<number[]>([]);

  const projects = resume.projects ?? [];
  const sectionCount = 3 + projects.length; // header, education, skills, then one per project

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
    const refs = sectionRefs.current;
    const heights: number[] = [];
    for (let i = 0; i < sectionCount; i++) {
      const el = refs[i];
      heights.push(el ? el.offsetHeight : 0);
    }
    setSectionHeights(heights);
  }, [resume, sectionCount]);

  useLayoutEffect(() => {
    if (sectionHeights.length === 0) return;
    setSectionToPage(assignSectionsToPages(sectionHeights));
  }, [sectionHeights]);

  const pageCount =
    sectionToPage.length > 0 ? Math.max(1, 1 + Math.max(...sectionToPage)) : 1;
  const scrollHeight =
    pageCount * PAGE_HEIGHT_PX + (pageCount > 1 ? (pageCount - 1) * PAGE_GAP_PX : 0);

  const setSectionRef = (i: number) => (el: HTMLDivElement | null) => {
    sectionRefs.current[i] = el;
  };

  return (
    <main className="resume-preview">
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
          {projects.map((_, i) => (
            <div key={i} ref={setSectionRef(3 + i)}>
              <ProjectsSection
                projects={[projects[i]]}
                showHeading={i === 0}
              />
            </div>
          ))}
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
            style={{ top: i * (PAGE_HEIGHT_PX + PAGE_GAP_PX) }}
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
                  const projectSectionIndices = sectionIndices.filter((si) => si >= 3);
                  const projectIndices = projectSectionIndices.map((si) => si - 3);
                  const pageProjects = projectIndices
                    .filter((i) => i >= 0 && i < projects.length)
                    .map((i) => projects[i]);

                  return (
                    <div
                      key={pageIndex}
                      className="resume-preview__page-content"
                      style={{
                        top: pageIndex * (PAGE_HEIGHT_PX + PAGE_GAP_PX),
                        height: PAGE_HEIGHT_PX,
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
                        {pageProjects.length > 0 && (
                          <ProjectsSection
                            projects={pageProjects}
                            showHeading={sectionIndices.includes(3)}
                            isEditing={isEditing}
                            onProjectChange={handleProjectChange}
                            onProjectDelete={onProjectDelete}
                            projectStartIndex={projectIndices[0]}
                            enableSortable
                          />
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
              const projectSectionIndices = sectionIndices.filter((si) => si >= 3);
              const projectIndices = projectSectionIndices.map((si) => si - 3);
              const pageProjects = projectIndices
                .filter((i) => i >= 0 && i < projects.length)
                .map((i) => projects[i]);

              return (
                <div
                  key={pageIndex}
                  className="resume-preview__page-content"
                  style={{
                    top: pageIndex * (PAGE_HEIGHT_PX + PAGE_GAP_PX),
                    height: PAGE_HEIGHT_PX,
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
                    {pageProjects.length > 0 && (
                      <ProjectsSection
                        projects={pageProjects}
                        showHeading={sectionIndices.includes(3)}
                        isEditing={isEditing}
                        onProjectChange={handleProjectChange}
                        onProjectDelete={onProjectDelete}
                        projectStartIndex={projectIndices[0]}
                      />
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
