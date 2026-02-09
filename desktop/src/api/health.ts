export async function getHealth() {
    // Check if the backend (current Python logic) is accessible 
  const res = await fetch("http://localhost:8000/health");

  if (!res.ok) {
    throw new Error("Backend not reachable");
  }

  return res.json();
}
