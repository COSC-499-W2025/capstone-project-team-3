import { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { mainNavItems, footerNavItems } from "./navigation";
import { getResumes } from "./api/resume";
import { useTheme } from "./context/ThemeContext";
import "./styles/NavBar.css";

const navIcons: Record<string, React.ReactNode> = {
  "/hubpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  ),
  "/resumebuilderpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  ),
  "/portfoliopage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  ),
  "/uploadpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  ),
  "/datamanagementpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
    </svg>
  ),
  "/userpreferencepage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  ),
  "/atsscoringpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  ),
  "/coverletterpage": (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
};

const settingsIcon = (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

export function NavBar() {
  const [collapsed, setCollapsed] = useState(false);
   const [hasMasterResume, setHasMasterResume] = useState(true);
   const { theme, toggleTheme, fontSize, increaseFontSize, decreaseFontSize } = useTheme();
   const [fontSizeExpanded, setFontSizeExpanded] = useState(false);

  useEffect(() => {
    getResumes()
      .then((resumes) => {
        const masterHasContent = resumes.some((r) => r.is_master);
        setHasMasterResume(masterHasContent);
      })
      .catch(() => setHasMasterResume(true));
  }, []);

  return (
    <aside
      className={`app-sidebar ${collapsed ? "app-sidebar--collapsed" : ""}`}
      aria-label="Main navigation"
    >
      <div className="app-sidebar__head">
        <NavLink to="/hubpage" className="app-sidebar__brand" title="Insights">
          <span className="app-sidebar__brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          </span>
          {!collapsed && <span className="app-sidebar__brand-text">Insights</span>}
        </NavLink>
      </div>

      <nav className="app-sidebar__links">
        {mainNavItems.map(({ path, label }) => {
          const isATS = path === "/atsscoringpage";
          const disabled = isATS && !hasMasterResume;

          if (disabled) {
            return (
              <span
                key={path}
                className="app-sidebar__link app-sidebar__link--disabled"
                title="Upload projects to generate a resume for Job Match"
              >
                <span className="app-sidebar__link-icon">{navIcons[path]}</span>
                {!collapsed && <span className="app-sidebar__link-label">{label}</span>}
              </span>
            );
          }

          return (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `app-sidebar__link ${isActive ? "app-sidebar__link--active" : ""}`
              }
              title={collapsed ? label : undefined}
            >
              <span className="app-sidebar__link-icon">{navIcons[path]}</span>
              {!collapsed && <span className="app-sidebar__link-label">{label}</span>}
            </NavLink>
          );
        })}
      </nav>

      <div className="app-sidebar__footer">
        <div className="app-sidebar__footer-row">
          {footerNavItems.map(({ path, label }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `app-sidebar__profile ${isActive ? "app-sidebar__profile--active" : ""}`
              }
              title={label}
            >
              <span className="app-sidebar__link-icon">{path === "/settingspage" ? settingsIcon : navIcons[path]}</span>
            </NavLink>
          ))}
          {/* Text size toggle - expandable */}
          <div className="app-sidebar__text-size-wrapper">
            <button
              type="button"
              className={`app-sidebar__toggle app-sidebar__text-size-toggle ${fontSizeExpanded ? "app-sidebar__text-size-toggle--expanded" : ""}`}
              onClick={() => setFontSizeExpanded(!fontSizeExpanded)}
              title={fontSizeExpanded ? "Hide text size controls" : "Adjust text size"}
              aria-label={fontSizeExpanded ? "Hide text size controls" : "Adjust text size"}
              aria-expanded={fontSizeExpanded}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <polyline points="4 7 4 4 20 4 20 7" />
                <line x1="9" y1="20" x2="15" y2="20" />
                <line x1="12" y1="4" x2="12" y2="20" />
              </svg>
            </button>
            {fontSizeExpanded && (
              <div className="app-sidebar__text-size-controls">
                <button
                  type="button"
                  className="app-sidebar__text-size-btn"
                  onClick={decreaseFontSize}
                  title="Decrease text size"
                  aria-label="Decrease text size"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
                <span className="app-sidebar__text-size-label">{fontSize === "small" ? "S" : fontSize === "default" ? "M" : fontSize === "large" ? "L" : "XL"}</span>
                <button
                  type="button"
                  className="app-sidebar__text-size-btn"
                  onClick={increaseFontSize}
                  title="Increase text size"
                  aria-label="Increase text size"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
              </div>
            )}
          </div>
          {/* Dark / light mode toggle */}
          <button
            type="button"
            className="app-sidebar__toggle"
            onClick={toggleTheme}
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {theme === "dark" ? (
              /* Sun icon — shown in dark mode to switch to light */
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden
              >
                <circle cx="12" cy="12" r="5" />
                <line x1="12" y1="1" x2="12" y2="3" />
                <line x1="12" y1="21" x2="12" y2="23" />
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                <line x1="1" y1="12" x2="3" y2="12" />
                <line x1="21" y1="12" x2="23" y2="12" />
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
              </svg>
            ) : (
              /* Moon icon — shown in light mode to switch to dark */
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden
              >
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
          <button
            type="button"
            className="app-sidebar__toggle"
            onClick={() => setCollapsed((c) => !c)}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!collapsed}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {/* Arrow + vertical bar: →| when collapsed (expand outwards), |← when expanded (collapse inwards) */}
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.25"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`app-sidebar__toggle-icon ${collapsed ? "app-sidebar__toggle-icon--expand" : "app-sidebar__toggle-icon--collapse"}`}
              aria-hidden
            >
              <path d="M5 12h6" />
              <path d="M11 8l4 4-4 4" />
              <line x1="19" y1="6" x2="19" y2="18" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
}

export default NavBar;
