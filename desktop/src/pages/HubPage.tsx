import { useNavigate } from "react-router-dom";
import "../styles/HubPage.css";

/**
 * Hub Page - Central navigation page with buttons
 * to Resume Builder, Portfolio, and Data Management.
 */
export function HubPage() {
  const navigate = useNavigate();

  const cards = [
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
