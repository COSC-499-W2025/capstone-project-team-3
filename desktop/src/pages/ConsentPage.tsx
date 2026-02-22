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
        
        if (data.has_consent) {
          console.log("Already consented, showing notification");
          setNotification(textData.already_provided_message);
          setTimeout(() => navigate("/uploadpage"), 2000);
        } else {
          console.log("Consent text loaded:", textData);
          setConsentText(textData.consent_message);
          setDetailedInfo(textData.detailed_info);
          setMessages(textData);
        }
      } catch (err) {
        console.error("Failed to load consent:", err);
      }
    };
    
    fetchConsentStatus();
  }, [navigate]);

  const handleSubmit = async (accepted: boolean) => {
    console.log("handleSubmit called with accepted:", accepted);
    console.log("messages:", messages);
    if (!messages) return;
    try {
      console.log("Sending POST request...");
      const response = await fetch(`${API_BASE_URL}/api/privacy-consent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accepted }),
      });
      
      console.log("Response status:", response.status);
      if (!response.ok) throw new Error(await response.text());
      
      const message = accepted ? messages.granted_message : messages.declined_message;
      console.log("Setting notification:", message);
      setNotification(message);
      setTimeout(() => navigate(accepted ? "/uploadpage" : "/"), 2000);
    } catch (error) {
      console.error("Failed to submit consent:", error);
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
          <pre>{showDetails ? detailedInfo : consentText}</pre>
        </div>

        <div className="consent-actions">
          {!showDetails ? (
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
