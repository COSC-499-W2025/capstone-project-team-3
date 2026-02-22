import { ResumeListItem } from "../../api/resume";
import "../../styles/ResumeSidebar.css";

export const ResumeSidebar = ({
  resumeList,
  activeIndex,
  onSelect,
  onTailorNew,
  sidebarOpen = true,
  onToggleSidebar,
  onEdit
}: {
  resumeList: ResumeListItem[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onTailorNew?: () => void;
  sidebarOpen?: boolean;
  onToggleSidebar?: () => void;
  onEdit?: () => void;
}) => {
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
        {resumeList.map((r, i) => (
          <li key={i}>
            <div
              role="button"
              tabIndex={0}
              onClick={() => onSelect(i)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(i);
                }
              }}
              className={`resume-sidebar__item ${i === activeIndex ? "resume-sidebar__item--active" : ""}`}
            >
              <span className="resume-sidebar__item-label">{r.name || `Resume - ${i + 1}`}</span>
              <span className="resume-sidebar__actions">
                {!r.is_master && r.id != null && (
                  <button 
                    type="button" 
                    className="resume-sidebar__icon-btn" 
                    aria-label="Edit resume" 
                    onClick={(e) => { 
                      e.stopPropagation();
                      if (i === activeIndex && onEdit) {
                        onEdit();
                      }
                    }}
                  >
                    <img src="/edit_icon.svg" alt="" width={20} height={20} />
                  </button>
                )}
                <button type="button" className="resume-sidebar__icon-btn" aria-label="More options" onClick={(e) => { e.stopPropagation(); }}>
                  <img src="/more_icon.svg" alt="" width={18} height={18} />
                </button>
              </span>
            </div>
          </li>
        ))}
      </ul>

        <button type="button" className="resume-sidebar__tailor-btn" onClick={onTailorNew}>
          Tailor New Resume
        </button>
      </div>
    </aside>
  );
};
