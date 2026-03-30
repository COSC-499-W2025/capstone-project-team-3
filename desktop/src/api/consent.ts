import { getApiBaseUrl } from "../config/api";

export interface ConsentStatus {
  has_consent: boolean;
}

/**
 * Fetch consent status from the backend.
 * Returns { has_consent } on success; throws Error with backend detail or a fallback message on failure.
 */
export async function getConsentStatus(): Promise<ConsentStatus> {
  const res = await fetch(`${getApiBaseUrl()}/api/privacy-consent`);

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = data.detail ?? res.statusText;
    throw new Error(message || "Request failed");
  }

  const data = await res.json();
  return { has_consent: data.has_consent };
}
