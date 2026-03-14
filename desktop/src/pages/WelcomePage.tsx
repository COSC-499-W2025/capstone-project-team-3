import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getConsentStatus } from "../api/consent";
import "../styles/WelcomePage.css";
import "../styles/Notification.css";

/**
 * Welcome/Landing Page - First page users see
 */
export function WelcomePage() {
  const navigate = useNavigate();
  const [consentError, setConsentError] = useState<string | null>(null);
  const [hasConsent, setHasConsent] = useState<boolean | null>(null);

  // On mount, check if the user has already given consent.
  // If so, treat them as a returning user and, after a short
  // splash delay, send them straight to the hub page.
  useEffect(() => {
    let isCancelled = false;

    const checkConsentAndMaybeRedirect = async () => {
      try {
        const { has_consent } = await getConsentStatus();
        if (!isCancelled) setHasConsent(has_consent);
        if (!has_consent) return;

        // Returning user – after ~3s of the home animation, go to hub
        setTimeout(() => {
          if (!isCancelled) navigate("/hubpage");
        }, 3000);
      } catch (err) {
        if (!isCancelled) {
          const message = err instanceof Error ? err.message : "Something went wrong. You can continue by clicking the screen.";
          setConsentError(message);
        }
      }
    };

    checkConsentAndMaybeRedirect();

    return () => {
      isCancelled = true;
    };
  }, [navigate]);

  const handleClick = () => {
    if (hasConsent === true) {
      navigate("/hubpage");
    } else {
      navigate("/consentpage");
    }
  };

  return (
    <div className="welcome-container" onClick={handleClick}>
      {consentError && (
        <div
          className="notification error"
          role="alert"
          onClick={(e) => e.stopPropagation()}
        >
          <pre>{consentError}</pre>
          <button
            type="button"
            className="welcome-toast-dismiss"
            onClick={(e) => {
              e.stopPropagation();
              setConsentError(null);
            }}
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      )}
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
