/**
 * TEMPLATE API CLIENT
 * Copy this file and rename for your endpoint.
 */

export async function callEndpoint(payload: any) {
  const res = await fetch("http://localhost:8000/ENDPOINT_HERE", {
    method: "POST", // or "GET" if applicable
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Request failed: " + res.statusText);
  }

  return res.json();
}
