import { useState } from "react";
import { callEndpoint } from "../api/template";

/**
 * TEMPLATE PAGE
 * Copy this file and rename for your new page.
 */

export function TemplatePage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setError(null);
    try {
      const data = await callEndpoint({ /* example payload */ });
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>New Page</h1>
      <button onClick={handleRun}>Run</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default TemplatePage;
