import { useState, useEffect, useRef, useCallback } from "react";
import { ResumeListItem } from "../../api/resume";
import thumbnailIconUrl from "../../assets/resume-sidebar/thumbnail_icon.svg?url";
import editIconUrl from "../../assets/resume-sidebar/edit_icon.svg?url";
import moreIconUrl from "../../assets/resume-sidebar/more_icon.svg?url";
import "../../styles/ResumeSidebar.css";

function isMasterItem(r: ResumeListItem): boolean {
  return Boolean(r.is_master || r.id === 1);
}

export const ResumeSidebar = ({
  resumeList,
  activeIndex,
  onSelect,
  onTailorNew,
  onDelete,
  sidebarOpen = true,
  onToggleSidebar,
  onEditResume,
  onDuplicateResume,
  onRenameResume,
  hasProjects = true
}: {
  resumeList: ResumeListItem[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onTailorNew?: () => void;
  onDelete?: (id: number) => void;
  sidebarOpen?: boolean;
  onToggleSidebar?: () => void;
  onEditResume?: (index: number) => void;
  onDuplicateResume?: (id: number) => void;
  onRenameResume?: (id: number, newName: string) => Promise<void>;
  hasProjects?: boolean;
}) => {
  const [openMenuIndex, setOpenMenuIndex] = useState<number | null>(null);
  const [renamingResumeId, setRenamingResumeId] = useState<number | null>(null);
  const [renameDraft, setRenameDraft] = useState("");
  const renamingResumeIdRef = useRef<number | null>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    renamingResumeIdRef.current = renamingResumeId;
  }, [renamingResumeId]);

  useEffect(() => {
    if (renamingResumeId != null) {
      renameInputRef.current?.focus();
      renameInputRef.current?.select();
    }
  }, [renamingResumeId]);

  const cancelInlineRename = useCallback(() => {
    renamingResumeIdRef.current = null;
    setRenamingResumeId(null);
    setRenameDraft("");
  }, []);

  const commitInlineRename = useCallback(async () => {
    const id = renamingResumeIdRef.current;
    if (id == null || !onRenameResume) return;

    const trimmed = (renameInputRef.current?.value ?? "").trim();
    if (!trimmed) {
      cancelInlineRename();
      return;
    }

    const currentRow = resumeList.find((x) => x.id === id);
    const previous = (currentRow?.name ?? "").trim();
    if (trimmed === previous) {
      cancelInlineRename();
      return;
    }

    try {
      await onRenameResume(id, trimmed);
      cancelInlineRename();
    } catch {
      renameInputRef.current?.focus();
    }
  }, [cancelInlineRename, onRenameResume, resumeList]);

  // When there are no projects, hide the master resume from the sidebar
  const displayIndices = hasProjects
    ? resumeList.map((_, i) => i)
    : resumeList.map((_, i) => i).filter((i) => !isMasterItem(resumeList[i]));
  const displayList = displayIndices.map((i) => resumeList[i]);
  const activeDisplayIndex = displayIndices.indexOf(activeIndex);

  return (
    <aside className={`resume-sidebar ${sidebarOpen ? "resume-sidebar--open" : "resume-sidebar--closed"}`}>
      <div className="resume-sidebar__header">
        <h2 className="resume-sidebar__title">Your Résumés</h2>
        <button
          type="button"
          className="resume-sidebar__header-icon-btn"
          onClick={onToggleSidebar}
          aria-label={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
        >
          <img src={thumbnailIconUrl} alt="" className="resume-sidebar__header-icon" width={30} height={30} />
        </button>
      </div>
      <hr className="resume-sidebar__divider" />

      <div className="resume-sidebar__content">
        <ul className="resume-sidebar__list">
        {displayList.map((r, displayI) => {
          const fullIndex = displayIndices[displayI];
          const master = isMasterItem(r);
          const showOverflow =
            r.id != null &&
            ((master && onDuplicateResume) ||
              (!master && !!(onDuplicateResume || onRenameResume || onDelete)));

          return (
          <li key={fullIndex}>
            <div
              role="button"
              tabIndex={0}
              onClick={() => {
                if (r.id != null && renamingResumeId === r.id) return;
                onSelect(fullIndex);
              }}
              onKeyDown={(e) => {
                if (renamingResumeId === r.id) return;
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(fullIndex);
                }
              }}
              className={`resume-sidebar__item ${displayI === activeDisplayIndex ? "resume-sidebar__item--active" : ""}`}
            >
              {r.id != null && renamingResumeId === r.id ? (
                <input
                  ref={renameInputRef}
                  type="text"
                  className="resume-sidebar__item-rename-input"
                  value={renameDraft}
                  aria-label="Resume name"
                  onChange={(e) => setRenameDraft(e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  onKeyDown={(e) => {
                    e.stopPropagation();
                    if (e.key === "Enter") {
                      e.preventDefault();
                      void commitInlineRename();
                    }
                    if (e.key === "Escape") {
                      e.preventDefault();
                      cancelInlineRename();
                    }
                  }}
                  onBlur={() => {
                    window.setTimeout(() => {
                      if (renamingResumeIdRef.current !== r.id) return;
                      void commitInlineRename();
                    }, 0);
                  }}
                />
              ) : (
                <span className="resume-sidebar__item-label">{r.name || `Resume - ${displayI + 1}`}</span>
              )}
              <span className="resume-sidebar__actions">
                {!master && r.id != null && (
                  <button 
                    type="button" 
                    className="resume-sidebar__icon-btn" 
                    aria-label="Edit resume" 
                    onClick={(e) => { 
                      e.stopPropagation();
                      onEditResume?.(fullIndex);
                    }}
                  >
                    <img src={editIconUrl} alt="" width={20} height={20} />
                  </button>
                )}
                {showOverflow && (
                  <div className="resume-sidebar__menu-wrapper">
                    <button 
                      type="button" 
                      className="resume-sidebar__icon-btn" 
                      aria-label="More actions" 
                      onClick={(e) => { 
                        e.stopPropagation();
                        setOpenMenuIndex(openMenuIndex === fullIndex ? null : fullIndex);
                      }}
                    >
                      <img src={moreIconUrl} alt="" width={18} height={18} />
                    </button>
                    {openMenuIndex === fullIndex && (
                      <div className="resume-sidebar__dropdown">
                        {onDuplicateResume && r.id != null && (
                          <button
                            type="button"
                            aria-label="Duplicate resume"
                            className="resume-sidebar__dropdown-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuIndex(null);
                              const rid = r.id;
                              if (rid != null) onDuplicateResume(rid);
                            }}
                          >
                            Duplicate Resume
                          </button>
                        )}
                        {!master && onRenameResume && r.id != null && (
                          <button
                            type="button"
                            aria-label="Rename resume"
                            className="resume-sidebar__dropdown-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuIndex(null);
                              renamingResumeIdRef.current = r.id;
                              setRenamingResumeId(r.id);
                              setRenameDraft(r.name || "");
                            }}
                          >
                            Rename
                          </button>
                        )}
                        {!master && onDelete && r.id != null && (
                          <button
                            type="button"
                            aria-label="Delete resume"
                            className="resume-sidebar__dropdown-item resume-sidebar__dropdown-item--danger"
                            onClick={(e) => {
                              e.stopPropagation();
                              setOpenMenuIndex(null);
                              const rid = r.id;
                              if (rid != null && window.confirm(`Are you sure you want to delete "${r.name || 'this resume'}"?`)) {
                                onDelete(rid);
                              }
                            }}
                          >
                            Delete Resume
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </span>
            </div>
          </li>
          );
        })}
      </ul>

        <button
          type="button"
          className={`resume-sidebar__tailor-btn ${!hasProjects ? "resume-sidebar__tailor-btn--disabled" : ""}`}
          onClick={hasProjects ? onTailorNew : undefined}
          title={!hasProjects ? "You need to upload a project" : undefined}
          disabled={!hasProjects}
        >
          Tailor New Resume
        </button>
      </div>
    </aside>
  );
};
