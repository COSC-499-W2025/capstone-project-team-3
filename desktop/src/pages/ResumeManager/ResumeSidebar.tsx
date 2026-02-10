import { Resume } from "../../api/resume_types";
import "./ResumeSidebar.css";

export const ResumeSidebar = ({
  resumes,
  activeIndex,
  onSelect,
  onTailorNew,
  dataBadgeIndices = [0, 2],
}: {
  resumes: Resume[];
  activeIndex: number;
  onSelect: (index: number) => void;
  onTailorNew?: () => void;
  dataBadgeIndices?: number[];
}) => {
  const showDataBadge = (index: number) => dataBadgeIndices.includes(index);

  return (
    <aside className="resume-sidebar">
      <div className="resume-sidebar__header">
        <h2 className="resume-sidebar__title">Your Resumés</h2>
        <img src="/thumbnail_icon.svg" alt="" className="resume-sidebar__header-icon" width={20} height={20} />
      </div>
      <hr className="resume-sidebar__divider" />

      <ul className="resume-sidebar__list">
        {resumes.map((r, i) => (
          <li key={i}>
            <button
              type="button"
              onClick={() => onSelect(i)}
              className={`resume-sidebar__item ${i === activeIndex ? "resume-sidebar__item--active" : ""}`}
            >
              <span className="resume-sidebar__item-label">{r.name || `Resume - ${i + 1}`}</span>
              {showDataBadge(i) && <span className="resume-sidebar__badge" aria-label="Has data">D</span>}
              <span className="resume-sidebar__actions">
                <button type="button" className="resume-sidebar__icon-btn" aria-label="Edit resume" onClick={(e) => { e.stopPropagation(); }}>
                  <img src="/edit_icon.svg" alt="" width={18} height={18} />
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
    </aside>
  );
};
