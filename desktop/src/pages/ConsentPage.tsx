import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config/api";
import "../styles/ConsentPage.css";
import "../styles/Notification.css";

type ConsentTextResponse = {
  consent_message: string;
  detailed_info: string;
  granted_message: string;
  declined_message: string;
  already_provided_message: string;
};

export function ConsentPage() {
  const navigate = useNavigate();
  const [consentText, setConsentText] = useState("");
  const [detailedInfo, setDetailedInfo] = useState("");
  const [messages, setMessages] = useState<ConsentTextResponse | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);
  const [hasConsent, setHasConsent] = useState(false);
  const [consentTimestamp, setConsentTimestamp] = useState<string | null>(null);

  useEffect(() => {
    const fetchConsentStatus = async () => {
      try {
        console.log("Fetching consent status...");
        const res = await fetch(`${API_BASE_URL}/api/privacy-consent`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        
        console.log("Consent status:", data);
        const textRes = await fetch(`${API_BASE_URL}/api/privacy-consent/text`);
        if (!textRes.ok) throw new Error(await textRes.text());
        const textData: ConsentTextResponse = await textRes.json();
        
        setMessages(textData);
        setConsentText(textData.consent_message);
        setDetailedInfo(textData.detailed_info);
        setHasConsent(data.has_consent);
        setConsentTimestamp(data.timestamp);
      } catch (err) {
        console.error("Failed to load consent:", err);
      }
    };
    
    fetchConsentStatus();
  }, [navigate]);

  const handleSubmit = async (accepted: boolean) => {
    if (!messages) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/privacy-consent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accepted }),
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const message = accepted ? messages.granted_message : messages.declined_message;
      setNotification(message);
      setTimeout(() => navigate(accepted ? "/uploadpage" : "/"), 2000);
    } catch (error) {
      console.error("Failed to submit consent:", error);
    }
  };

  const handleRevoke = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/privacy-consent`, {
        method: "DELETE",
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      setNotification("Consent withdrawn successfully");
      setTimeout(() => navigate("/"), 2000);
    } catch (error) {
      console.error("Failed to revoke consent:", error);
    }
  };

  return (
    <div className="consent-container">
      {notification && (
        <div className="notification">
          <pre>{notification}</pre>
        </div>
      )}
      
      <div className="consent-frame">
        <div className="consent-content">
          {hasConsent ? (
            <pre>
              {messages?.already_provided_message}
              {consentTimestamp && `\n\nConsent provided on: ${new Date(consentTimestamp).toLocaleString()}`}
            </pre>
          ) : (
            <pre>{showDetails ? detailedInfo : consentText}</pre>
          )}
        </div>

        <div className="consent-actions">
          {hasConsent ? (
            <>
              <button onClick={() => navigate("/uploadpage")}>
                Continue
              </button>
              <button onClick={handleRevoke}>
                Revoke Consent
              </button>
            </>
          ) : !showDetails ? (
            <>
              <button onClick={() => handleSubmit(false)} disabled={!messages}>
                Decline
              </button>
              <button onClick={() => setShowDetails(true)} disabled={!messages}>
                More
              </button>
              <button onClick={() => handleSubmit(true)} disabled={!messages}>
                Accept
              </button>
            </>
          ) : (
            <button onClick={() => setShowDetails(false)}>
              Back
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConsentPage;
