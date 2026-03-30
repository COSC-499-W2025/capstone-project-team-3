import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getApiBaseUrl } from "../config/api";
import "../styles/ConsentPage.css";
import "../styles/Notification.css";

type ConsentTextResponse = {
  consent_message: string;
  detailed_info: string;
  granted_message: string;
  declined_message: string;
  already_provided_message: string;
};

/**
 * Strips CLI-style decorations (=== borders, "type yes/no" prompts,
 * "Press Enter" lines) from the raw consent strings so we can render
 * clean HTML instead of a <pre> block.
 */
function stripCliChrome(text: string): string {
  return text
    .replace(/^=+$/gm, "")                          // ====== lines
    .replace(/^Please type .*/gm, "")                // "Please type 'yes'…"
    .replace(/^For more details.*/gm, "")            // "For more details…"
    .replace(/^Press Enter.*/gm, "")                 // "Press Enter…"
    .replace(/^Use '--clear-data'.*/gm,              // CLI-specific hint
      "Use the data-management page to remove all stored information.")
    .trim();
}

/**
 * Turns the cleaned text into an array of "blocks".
 * Each block is either a heading (all-caps line), a list (lines starting
 * with "- " or "1. "), or a paragraph (everything else).
 */
type Block =
  | { kind: "heading"; text: string }
  | { kind: "list"; items: string[] }
  | { kind: "paragraph"; text: string };

function parseBlocks(raw: string): Block[] {
  const cleaned = stripCliChrome(raw);
  const lines = cleaned.split("\n");
  const blocks: Block[] = [];
  let listBuf: string[] = [];
  let skippedFirstHeading = false;

  const flushList = () => {
    if (listBuf.length) {
      blocks.push({ kind: "list", items: [...listBuf] });
      listBuf = [];
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      continue;
    }

    // Numbered list item  ("1. Foo")
    const numMatch = trimmed.match(/^\d+\.\s+(.+)/);
    if (numMatch) {
      listBuf.push(numMatch[1]);
      continue;
    }

    // Dash list item  ("- Foo")
    if (trimmed.startsWith("- ")) {
      listBuf.push(trimmed.slice(2));
      continue;
    }

    flushList();

    // ALL-CAPS line → heading  (e.g. "DATA COLLECTION:")
    // Skip the very first one — it's already rendered as the page <h2> title.
    if (/^[A-Z][A-Z\s:\-]+$/.test(trimmed)) {
      if (!skippedFirstHeading) {
        skippedFirstHeading = true;
        continue;
      }
      blocks.push({ kind: "heading", text: trimmed.replace(/:$/, "") });
      continue;
    }

    // Everything else → paragraph
    blocks.push({ kind: "paragraph", text: trimmed });
  }
  flushList();
  return blocks;
}

/** Render an array of Blocks as JSX */
function RenderBlocks({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks.map((b, i) => {
        switch (b.kind) {
          case "heading":
            return <h3 key={i} className="consent-section-heading">{b.text}</h3>;
          case "list":
            return (
              <ul key={i} className="consent-list">
                {b.items.map((item, j) => <li key={j}>{item}</li>)}
              </ul>
            );
          case "paragraph":
            return <p key={i} className="consent-paragraph">{b.text}</p>;
        }
      })}
    </>
  );
}

export function ConsentPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ConsentTextResponse | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);
  const [hasConsent, setHasConsent] = useState(false);
  const [consentTimestamp, setConsentTimestamp] = useState<string | null>(null);

  useEffect(() => {
    const fetchConsentStatus = async () => {
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/privacy-consent`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();

        const textRes = await fetch(`${getApiBaseUrl()}/api/privacy-consent/text`);
        if (!textRes.ok) throw new Error(await textRes.text());
        const textData: ConsentTextResponse = await textRes.json();

        setMessages(textData);
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
      const response = await fetch(`${getApiBaseUrl()}/api/privacy-consent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accepted }),
      });

      if (!response.ok) throw new Error(await response.text());

      const message = accepted
        ? messages.granted_message
        : messages.declined_message;
      setNotification(message);
      setTimeout(() => navigate(accepted ? "/userpreferencepage" : "/"), 2000);
    } catch (error) {
      console.error("Failed to submit consent:", error);
    }
  };

  const handleRevoke = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/privacy-consent`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error(await response.text());

      setNotification("Consent withdrawn successfully");
      setTimeout(() => navigate("/"), 2000);
    } catch (error) {
      console.error("Failed to revoke consent:", error);
    }
  };

  /* ── Derive the title from the first ALL-CAPS line in consent_message ── */
  const consentTitle = messages?.consent_message
    .split("\n")
    .map((l) => l.trim())
    .find((l) => /^[A-Z][A-Z\s\-]+$/.test(l) && !l.startsWith("="))
    ?? "Consent Agreement";

  const detailedTitle = messages?.detailed_info
    .split("\n")
    .map((l) => l.trim())
    .find((l) => /^[A-Z][A-Z\s]+$/.test(l) && !l.startsWith("="))
    ?? "Privacy Details";

  return (
    <div className="consent-container">
      <button
        type="button"
        className="project-selection__back consent-back"
        onClick={() => navigate(-1)}
      >
        <span className="project-selection__back-chevron" aria-hidden>
          ‹
        </span>
        Back
      </button>
      {notification && (
        <div className="notification">
          <p>{notification}</p>
        </div>
      )}

      <div className="consent-frame">
        <div className="consent-content">
          {hasConsent ? (
            <>
              <h2 className="consent-title">Consent Previously Provided</h2>
              <p className="consent-paragraph">
                {stripCliChrome(messages?.already_provided_message ?? "")}
              </p>
              {consentTimestamp && (
                <p className="consent-timestamp">
                  Consent provided on:{" "}
                  <strong>{new Date(consentTimestamp).toLocaleString()}</strong>
                </p>
              )}
            </>
          ) : showDetails ? (
            <>
              <h2 className="consent-title">{detailedTitle}</h2>
              <RenderBlocks blocks={parseBlocks(messages?.detailed_info ?? "")} />
            </>
          ) : (
            <>
              <h2 className="consent-title">{consentTitle}</h2>
              <RenderBlocks blocks={parseBlocks(messages?.consent_message ?? "")} />
            </>
          )}
        </div>

        <div className="consent-actions">
          {hasConsent ? (
            <>
              <button onClick={() => navigate("/userpreferencepage")}>Continue</button>
              <button className="btn-outline" onClick={handleRevoke}>
                Revoke Consent
              </button>
            </>
          ) : !showDetails ? (
            <>
              <button
                className="btn-outline"
                onClick={() => handleSubmit(false)}
                disabled={!messages}
              >
                Decline
              </button>
              <button
                className="btn-secondary"
                onClick={() => setShowDetails(true)}
                disabled={!messages}
              >
                More Info
              </button>
              <button onClick={() => handleSubmit(true)} disabled={!messages}>
                Accept
              </button>
            </>
          ) : (
            <button onClick={() => setShowDetails(false)}>Back</button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConsentPage;
