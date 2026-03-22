import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getGeminiKeyStatus } from "../api/geminiKey";
import { GeminiApiKeyForm } from "../components/gemini/GeminiApiKeyForm";
import "../styles/GeminiApiKey.css";

const AI_STUDIO_KEYS_URL = "https://aistudio.google.com/app/apikey";

/**
 * Full-page Gemini API key setup with instructions and optional remove.
 */
export function GeminiApiKeyPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<Awaited<ReturnType<typeof getGeminiKeyStatus>> | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  /** Last save rejected by the server (e.g. wrong key shape) — shown in Current status until cleared. */
  const [saveFormatRejection, setSaveFormatRejection] = useState<string | null>(null);
  const [removeFailure, setRemoveFailure] = useState<string | null>(null);

  const refresh = useCallback(() => {
    getGeminiKeyStatus()
      .then(setStatus)
      .catch((e) => setLoadError(e instanceof Error ? e.message : "Could not load status"));
  }, []);

  const handleSaved = useCallback(() => {
    setSaveFormatRejection(null);
    setRemoveFailure(null);
    refresh();
  }, [refresh]);

  const clearFormStatusHints = useCallback(() => {
    setSaveFormatRejection(null);
    setRemoveFailure(null);
  }, []);

  useEffect(() => {
    setLoadError(null);
    refresh();
  }, [refresh]);

  const serverVariant = status
    ? status.valid
      ? "success"
      : status.configured
        ? "warning"
        : "neutral"
    : null;

  const statusVariant =
    saveFormatRejection || removeFailure ? "warning" : serverVariant;
  const showStatusCard = Boolean(
    saveFormatRejection || removeFailure || (status && serverVariant),
  );

  return (
    <div className="page-container flex-column settings-container">
      <button
        type="button"
        className="settings-back-btn"
        onClick={() => navigate(-1)}
        aria-label="Back"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Back
      </button>

      <div className="gemini-key-page">
        <h1 className="gemini-key-page-title">Gemini API key</h1>
        <p className="gemini-key-page-lead">
          Add your Google Gemini API key so AI-powered analysis can run.
        </p>

        <p className="gemini-key-page-studio">
          <a
            className="gemini-key-page-studio-link"
            href={AI_STUDIO_KEYS_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Google AI Studio — API keys
          </a>
        </p>

        <ol className="gemini-key-steps">
          <li>Sign in with your Google account if prompted.</li>
          <li>Create a new API key, or reuse an existing one.</li>
          <li>Copy the key, then paste it in the form below and click Save key.</li>
        </ol>

        {loadError && (
          <p className="gemini-key-error" role="alert">
            {loadError}
          </p>
        )}

        {showStatusCard && statusVariant && (
          <div
            className={`gemini-key-status-card gemini-key-status-card--${statusVariant}`}
            role="status"
            aria-live="polite"
          >
            <div className="gemini-key-status-card-label">Current status</div>
            {saveFormatRejection ? (
              <p className="gemini-key-status-card-msg">
                <strong>Not saved.</strong> {saveFormatRejection} Typical Gemini keys start with{" "}
                <code>AIza</code>. Adjust the key and choose Save key again.
              </p>
            ) : removeFailure ? (
              <p className="gemini-key-status-card-msg">
                <strong>Remove failed.</strong> {removeFailure} Try again or check your connection.
              </p>
            ) : status?.valid ? (
              <p className="gemini-key-status-card-msg">
                <strong>Ready.</strong> A valid Gemini API key is saved
                {status.masked_suffix ? ` (${status.masked_suffix})` : ""}. AI analysis can use it.
              </p>
            ) : status?.configured ? (
              <p className="gemini-key-status-card-msg">
                <strong>Needs attention.</strong> A key is stored, but it does not match the expected
                format. Replace it using the form below.
              </p>
            ) : (
              <p className="gemini-key-status-card-msg">
                <strong>Not configured.</strong> No API key is saved yet. Add one below to enable AI
                analysis.
              </p>
            )}
          </div>
        )}

        <h2 className="gemini-key-page-form-heading">Save your key</h2>
        <GeminiApiKeyForm
          hidePageIntro
          showRemove={Boolean(status?.configured)}
          onSaved={handleSaved}
          onSaveFormatRejected={setSaveFormatRejection}
          onRemoveFailed={setRemoveFailure}
          onClearFormatRejection={clearFormStatusHints}
        />
      </div>
    </div>
  );
}

export default GeminiApiKeyPage;
