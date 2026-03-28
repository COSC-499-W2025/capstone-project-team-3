import { useNavigate } from "react-router-dom";
import "../styles/HubPage.css";

/**
 * Hub Page - Central navigation page with buttons
 * to Resume Builder, Portfolio, Data Management, and Learnings.
 */
export function HubPage() {
  const navigate = useNavigate();

  const cards = [
    {
      title: "Upload File",
      description: "Upload and analyze your project files.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      ),
      path: "/uploadpage",
    },
    {
      title: "Resume Builder",
      description: "Build and tailor your resume from analyzed projects.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
      path: "/resumebuilderpage",
    },
    {
      title: "Portfolio",
      description: "View your portfolio with charts and insights.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
      ),
      path: "/portfoliopage",
    },
    {
      title: "Data Management",
      description: "Review and edit project dates, skills, and metadata.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
        </svg>
      ),
      path: "/datamanagementpage",
    },
    {
      title: "Check Job Match",
      description: "Check how well your resume matches a job description.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M9 11l3 3L22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
      ),
      path: "/atsscoringpage",
    },
    {
      title: "Learnings",
      description: "Course recommendations based on your profile and analyzed projects.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          <line x1="12" y1="6" x2="12" y2="12" />
          <line x1="9" y1="9" x2="15" y2="9" />
        </svg>
      ),
      path: "/userpreferencepage?tab=learning",
    },
  ];

  return (
    <div className="page-container flex-column hub-container">
      <h1 className="hub-title">Where would you like to go?</h1>

      <div className="hub-cards">
        {cards.map((card) => (
          <button
            key={card.path}
            className="frame hub-card text-center"
            onClick={() => navigate(card.path)}
            aria-label={`Go to ${card.title}`}
          >
            <div className="flex-center hub-card-icon">{card.icon}</div>
            <h2 className="hub-card-title">{card.title}</h2>
            <p className="hub-card-description">{card.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

export default HubPage;
