export async function buildResume() {
  const res = await fetch("http://localhost:8000/resume", {
    method: "GET"
  });

  if (!res.ok) {
    throw new Error("Request failed: " + res.statusText);
  }

  return res.json();
}