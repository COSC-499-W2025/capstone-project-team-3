import { API_BASE_URL } from "../config/api";

export async function getHealth() {
    // Check if the backend (current Python logic) is accessible 
  const res = await fetch(`${API_BASE_URL}/health`);

  if (!res.ok) {
    throw new Error("Backend not reachable");
  }

  return res.json();
}
