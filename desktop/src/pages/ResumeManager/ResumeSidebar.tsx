import { Resume } from "../../api/resume_types";
import "./ResumeSidebar.css";

export const ResumeSidebar = ({
  resumes,
  activeIndex,
  onSelect,
  onTailorNew,
  sidebarOpen = true,
  onToggleSidebar
}: {
  resumes: Resume[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onTailorNew?: () => void;
  sidebarOpen?: boolean;
  onToggleSidebar?: () => void;
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
        {resumes.map((r, i) => (
          <li key={i}>
            <button
              type="button"
              onClick={() => onSelect(i)}
              className={`resume-sidebar__item ${i === activeIndex ? "resume-sidebar__item--active" : ""}`}
            >
              <span className="resume-sidebar__item-label">{r.name || `Resume - ${i + 1}`}</span>
              <span className="resume-sidebar__actions">
                <button type="button" className="resume-sidebar__icon-btn" aria-label="Edit resume" onClick={(e) => { e.stopPropagation(); }}>
                  <img src="/edit_icon.svg" alt="" width={20} height={20} />
                </button>
                <button type="button" className="resume-sidebar__icon-btn" aria-label="More options" onClick={(e) => { e.stopPropagation(); }}>
                  <img src="/more_icon.svg" alt="" width={18} height={18} />
                </button>
              </span>
            </button>
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
