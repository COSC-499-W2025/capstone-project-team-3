import { useState } from "react";
import { ResumeListItem } from "../../api/resume";
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
  onEdit,
  hasProjects = true
}: {
  resumeList: ResumeListItem[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onTailorNew?: () => void;
  onDelete?: (id: number) => void;
  sidebarOpen?: boolean;
  onToggleSidebar?: () => void;
  onEdit?: () => void;
  hasProjects?: boolean;
}) => {
  const [openMenuIndex, setOpenMenuIndex] = useState<number | null>(null);

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
          <img src="/thumbnail_icon.svg" alt="" className="resume-sidebar__header-icon" width={30} height={30} />
        </button>
      </div>
      <hr className="resume-sidebar__divider" />

      <div className="resume-sidebar__content">
        <ul className="resume-sidebar__list">
        {displayList.map((r, displayI) => {
          const fullIndex = displayIndices[displayI];
          return (
          <li key={fullIndex}>
            <div
              role="button"
              tabIndex={0}
              onClick={() => onSelect(fullIndex)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(fullIndex);
                }
              }}
              className={`resume-sidebar__item ${displayI === activeDisplayIndex ? "resume-sidebar__item--active" : ""}`}
            >
              <span className="resume-sidebar__item-label">{r.name || `Resume - ${displayI + 1}`}</span>
              <span className="resume-sidebar__actions">
                {!r.is_master && r.id != null && (
                  <button 
                    type="button" 
                    className="resume-sidebar__icon-btn" 
                    aria-label="Edit resume" 
                    onClick={(e) => { 
                      e.stopPropagation();
                      if (fullIndex === activeIndex && onEdit) {
                        onEdit();
                      }
                    }}
                  >
                    <img src="/edit_icon.svg" alt="" width={20} height={20} />
                  </button>
                )}
                {r.id !== null && r.id !== 1 && onDelete && (
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
                      <img src="/more_icon.svg" alt="" width={18} height={18} />
                    </button>
                    {openMenuIndex === fullIndex && (
                      <div className="resume-sidebar__dropdown">
                        <button
                          type="button"
                          aria-label="Delete resume"
                          className="resume-sidebar__dropdown-item resume-sidebar__dropdown-item--danger"
                          onClick={(e) => {
                            e.stopPropagation();
                            setOpenMenuIndex(null);
                            if (r.id != null && window.confirm(`Are you sure you want to delete "${r.name || 'this resume'}"?`)) {
                              onDelete(r.id);
                            }
                          }}
                        >
                          Delete Resume
                        </button>
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
