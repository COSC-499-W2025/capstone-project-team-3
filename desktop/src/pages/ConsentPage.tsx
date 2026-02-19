import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ConsentPage.css";
import "../styles/Notification.css";

export function ConsentPage() {
  const navigate = useNavigate();
  const [consentText, setConsentText] = useState("");
  const [detailedInfo, setDetailedInfo] = useState("");
  const [messages, setMessages] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    console.log("Fetching consent status...");
    fetch("http://localhost:8000/api/privacy-consent")
      .then((res) => res.json())
      .then((data) => {
        console.log("Consent status:", data);
        if (data.has_consent) {
          fetch("http://localhost:8000/api/privacy-consent/text")
            .then((res) => res.json())
            .then((textData) => {
              console.log("Already consented, showing notification");
              setNotification(textData.already_provided_message);
              setTimeout(() => navigate("/uploadpage"), 2000);
            });
        } else {
          fetch("http://localhost:8000/api/privacy-consent/text")
            .then((res) => res.json())
            .then((textData) => {
              console.log("Consent text loaded:", textData);
              setConsentText(textData.consent_message);
              setDetailedInfo(textData.detailed_info);
              setMessages(textData);
            });
        }
      })
      .catch((err) => console.error("Failed to load consent:", err));
  }, [navigate]);

  const handleSubmit = async (accepted: boolean) => {
    console.log("handleSubmit called with accepted:", accepted);
    console.log("messages:", messages);
    if (!messages) return;
    try {
      console.log("Sending POST request...");
      const response = await fetch("http://localhost:8000/api/privacy-consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accepted }),
      });
      
      console.log("Response status:", response.status);
      if (response.ok) {
        const message = accepted ? messages.granted_message : messages.declined_message;
        console.log("Setting notification:", message);
        setNotification(message);
        setTimeout(() => navigate(accepted ? "/uploadpage" : "/"), 2000);
      }
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
