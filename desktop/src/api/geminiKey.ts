import { API_BASE_URL } from "../config/api";

export interface GeminiKeyStatus {
  configured: boolean;
  valid: boolean;
  masked_suffix: string | null;
}

/**
 * Current Gemini key status for the local backend (never includes the full key).
 */
export async function getGeminiKeyStatus(): Promise<GeminiKeyStatus> {
  const res = await fetch(`${API_BASE_URL}/api/gemini-key/status`);

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = (data as { detail?: string }).detail ?? res.statusText;
    throw new Error(message || "Request failed");
  }

  return res.json() as Promise<GeminiKeyStatus>;
}

export async function saveGeminiApiKey(api_key: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/gemini-key`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = (data as { detail?: string }).detail ?? res.statusText;
    throw new Error(typeof message === "string" ? message : "Invalid API key");
  }
}

export async function deleteGeminiApiKey(): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/gemini-key`, { method: "DELETE" });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = (data as { detail?: string }).detail ?? res.statusText;
    throw new Error(message || "Request failed");
  }
}
