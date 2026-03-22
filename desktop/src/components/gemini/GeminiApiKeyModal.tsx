import { GeminiApiKeyForm } from "./GeminiApiKeyForm";
import "../../styles/GeminiApiKey.css";

export interface GeminiApiKeyModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export function GeminiApiKeyModal({ open, onClose, onSaved }: GeminiApiKeyModalProps) {
  if (!open) return null;

  return (
    <div className="gemini-key-overlay" role="dialog" aria-modal="true" aria-labelledby="gemini-key-modal-title">
      <div className="gemini-key-modal">
        <button type="button" className="gemini-key-modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>
        <h3 id="gemini-key-modal-title" className="gemini-key-modal-title">
          Add Gemini API key
        </h3>
        <GeminiApiKeyForm
          compact
          onSaved={() => {
            onSaved();
            onClose();
          }}
        />
      </div>
    </div>
  );
}
