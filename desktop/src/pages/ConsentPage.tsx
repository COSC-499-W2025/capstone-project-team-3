import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ConsentPage.css";
import "../styles/Notification.css";

export function ConsentPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [consentText, setConsentText] = useState("");
  const [detailedInfo, setDetailedInfo] = useState("");
  const [messages, setMessages] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/privacy-consent")
      .then((res) => res.json())
      .then((data) => {
        if (data.has_consent) {
          fetch("http://localhost:8000/api/privacy-consent/text")
            .then((res) => res.json())
            .then((textData) => {
              setNotification(textData.already_provided_message);
              setTimeout(() => navigate("/uploadpage"), 2000);
            });
        } else {
          fetch("http://localhost:8000/api/privacy-consent/text")
            .then((res) => res.json())
            .then((textData) => {
              setConsentText(textData.consent_message);
              setDetailedInfo(textData.detailed_info);
              setMessages(textData);
              setLoading(false);
            });
        }
      })
      .catch((err) => {
        console.error("Failed to load consent:", err);
        setLoading(false);
      });
  }, [navigate]);

  const handleSubmit = async (accepted: boolean) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/privacy-consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accepted }),
      });
      
      if (response.ok) {
        const message = accepted ? messages.granted_message : messages.declined_message;
        setNotification(message);
        setTimeout(() => navigate(accepted ? "/uploadpage" : "/"), 2000);
      }
    } catch (error) {
      console.error("Failed to submit consent:", error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="consent-container">
        <div className="consent-frame">Loading...</div>
      </div>
    );
  }

  return (
    <div className="consent-container">
      {notification && (
        <div className="notification">
          <pre>{notification}</pre>
        </div>
      )}
      
      <div className="consent-frame">
        <div className="consent-content">
          <pre>{showDetails ? detailedInfo : consentText}</pre>
        </div>

        <div className="consent-actions">
          {!showDetails ? (
            <>
              <button onClick={() => handleSubmit(false)} disabled={loading}>
                Decline
              </button>
              <button onClick={() => setShowDetails(true)} disabled={loading}>
                More
              </button>
              <button onClick={() => handleSubmit(true)} disabled={loading}>
                Accept
              </button>
            </>
          ) : (
            <button onClick={() => setShowDetails(false)} disabled={loading}>
              Back
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConsentPage;
