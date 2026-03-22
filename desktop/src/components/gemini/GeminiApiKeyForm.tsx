import { useState } from "react";
import { deleteGeminiApiKey, saveGeminiApiKey } from "../../api/geminiKey";
import "../../styles/GeminiApiKey.css";

const AI_STUDIO_URL = "https://aistudio.google.com/app/apikey";

export interface GeminiApiKeyFormProps {
  onSaved?: () => void;
  /** Tighter layout for use inside a modal */
  compact?: boolean;
  showRemove?: boolean;
  /** When true, full-page intro copy is omitted (parent page supplies it). */
  hidePageIntro?: boolean;
  /**
   * When set, failed save (e.g. invalid format) is reported here instead of inline under the form.
   * Also suppresses success/error text below the buttons (parent shows Current status).
   */
  onSaveFormatRejected?: (message: string) => void;
  /** Failed remove — reported to parent when using external status (same as onSaveFormatRejected). */
  onRemoveFailed?: (message: string) => void;
  /** Called when the user edits the key or starts a new save attempt — clear parent status hints. */
  onClearFormatRejection?: () => void;
}

export function GeminiApiKeyForm({
  onSaved,
  compact,
  showRemove,
  hidePageIntro,
  onSaveFormatRejected,
  onRemoveFailed,
  onClearFormatRejection,
}: GeminiApiKeyFormProps) {
  const statusFromParent = Boolean(onSaveFormatRejected);
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    onClearFormatRejection?.();
    setBusy(true);
    try {
      await saveGeminiApiKey(value.trim());
      if (!statusFromParent) {
        setSuccessMessage("Saved. AI analysis can use this key now.");
      }
      setValue("");
      onSaved?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Save failed";
      if (onSaveFormatRejected) {
        onSaveFormatRejected(msg);
      } else {
        setError(msg);
      }
    } finally {
      setBusy(false);
    }
  };

  const handleRemove = async () => {
    setError(null);
    setSuccessMessage(null);
    onClearFormatRejection?.();
    setBusy(true);
    try {
      await deleteGeminiApiKey();
      if (!statusFromParent) {
        setSuccessMessage("Saved key removed from this app.");
      }
      onSaved?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Remove failed";
      if (onRemoveFailed) {
        onRemoveFailed(msg);
      } else {
        setError(msg);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <form
      className={`gemini-key-form${compact ? " gemini-key-form--compact" : ""}`}
      onSubmit={handleSubmit}
    >
      {!compact && !hidePageIntro && (
        <>
          <p>
            AI analysis uses Google Gemini. Create an API key in Google AI Studio, copy the key
            (it usually starts with <code>AIza</code>), and paste it below.
          </p>
          <p>
            <a href={AI_STUDIO_URL} target="_blank" rel="noopener noreferrer">
              Open Google AI Studio — API keys
            </a>
          </p>
        </>
      )}
      {compact && (
        <p>
          Paste the key from{" "}
          <a href={AI_STUDIO_URL} target="_blank" rel="noopener noreferrer">
            Google AI Studio
          </a>
          . Keys typically start with <code>AIza</code>.
        </p>
      )}
      {compact && !statusFromParent && error && (
        <div
          className="gemini-key-status-card gemini-key-status-card--warning gemini-key-form-feedback-card"
          role="alert"
        >
          <div className="gemini-key-status-card-label">Current status</div>
          <p className="gemini-key-status-card-msg">
            <strong>Not saved.</strong> {error} Typical Gemini keys start with <code>AIza</code>.
          </p>
        </div>
      )}
      {compact && !statusFromParent && successMessage && (
        <div
          className="gemini-key-status-card gemini-key-status-card--success gemini-key-form-feedback-card"
          role="status"
        >
          <div className="gemini-key-status-card-label">Current status</div>
          <p className="gemini-key-status-card-msg">{successMessage}</p>
        </div>
      )}
      <label className="gemini-key-label" htmlFor="gemini-api-key-input">
        API key
        <input
          id="gemini-api-key-input"
          className="gemini-key-input"
          type="password"
          autoComplete="off"
          spellCheck={false}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            onClearFormatRejection?.();
          }}
          placeholder="Paste your Gemini API key"
        />
      </label>
      <div className="gemini-key-actions">
        <button type="submit" className="gemini-key-btn gemini-key-btn--primary" disabled={busy || !value.trim()}>
          Save key
        </button>
        {showRemove && (
          <button
            type="button"
            className="gemini-key-btn gemini-key-btn--ghost"
            disabled={busy}
            onClick={handleRemove}
          >
            Remove saved key
          </button>
        )}
      </div>
      {!statusFromParent && !compact && error && (
        <p className="gemini-key-error" role="alert">
          {error}
        </p>
      )}
      {!statusFromParent && !compact && successMessage && (
        <p className="gemini-key-success" role="status">
          {successMessage}
        </p>
      )}
    </form>
  );
}
