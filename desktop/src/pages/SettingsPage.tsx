import { useNavigate } from "react-router-dom";
import "../styles/SettingsPage.css";

/**
 * Settings Page - Intermediate page offering navigation to
 * Profile (User Preferences) and Privacy (Consent) pages.
 */
export function SettingsPage() {
  const navigate = useNavigate();

  const cards = [
    {
      title: "Profile",
      description: "Update your personal information and job preferences.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" />
        </svg>
      ),
      path: "/userpreferencepage",
    },
    {
      title: "Privacy",
      description: "Review and manage your data consent settings.",
      icon: (
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
      path: "/consentpage",
    },
  ];

  return (
    <div className="page-container flex-column settings-container">
      <button
        className="settings-back-btn"
        onClick={() => navigate(-1)}
        aria-label="Back to Hub"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Back
      </button>

      <h1 className="settings-title">Settings</h1>
      <p className="settings-subtitle">What would you like to manage?</p>

      <div className="settings-cards">
        {cards.map((card) => (
          <button
            key={card.path}
            className="frame settings-card text-center"
            onClick={() => navigate(card.path)}
            aria-label={`Go to ${card.title}`}
          >
            <div className="flex-center settings-card-icon">{card.icon}</div>
            <h2 className="settings-card-title">{card.title}</h2>
            <p className="settings-card-description">{card.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

export default SettingsPage;
