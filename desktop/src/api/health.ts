import { getApiBaseUrl } from "../config/api";

export async function getHealth() {
    // Check if the backend (current Python logic) is accessible 
  const res = await fetch(`${getApiBaseUrl()}/health`);

  if (!res.ok) {
    throw new Error("Backend not reachable");
  }

  return res.json();
}
