import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config/api";
import "../styles/WelcomePage.css";

/**
 * Welcome/Landing Page - First page users see
 */
export function WelcomePage() {
  const navigate = useNavigate();

  // On mount, check if the user has already given consent.
  // If so, treat them as a returning user and, after a short
  // splash delay, send them straight to the hub page.
  useEffect(() => {
    let isCancelled = false;

    const checkConsentAndMaybeRedirect = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/privacy-consent`);
        if (!res.ok) return;

        const data = await res.json();
        if (!data.has_consent) return; // first-time user, stay on home

        // Returning user – after ~2s of the home animation, go to hub
        setTimeout(() => {
          if (!isCancelled) {
            navigate("/hubpage");
          }
        }, 3000);
      } catch {
        // On error, do nothing – user can proceed manually
      }
    };

    checkConsentAndMaybeRedirect();

    return () => {
      isCancelled = true;
    };
  }, [navigate]);

  const handleClick = () => {
    navigate("/consentpage");
  };

  return (
    <div className="welcome-container" onClick={handleClick}>
      <div className="welcome-frame welcome-frame-1">
        <div className="welcome-frame welcome-frame-2">
          <div className="welcome-frame welcome-frame-3">
            <div className="welcome-frame welcome-frame-4">
              <h1 className="welcome-title">Welcome to your Big Picture</h1>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WelcomePage;
