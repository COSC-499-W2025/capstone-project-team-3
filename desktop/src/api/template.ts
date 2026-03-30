/**
 * TEMPLATE API CLIENT
 * Copy this file and rename for your endpoint.
 */

import { getApiBaseUrl } from "../config/api";

export async function callEndpoint(payload: any) {
  const res = await fetch(`${getApiBaseUrl()}/ENDPOINT_HERE`, {
    method: "POST", // or "GET" if applicable
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Request failed: " + res.statusText);
  }

  return res.json();
}
