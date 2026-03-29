/**
 * API Configuration
 *
 * - Electron (packaged): after `initApiBaseUrlFromElectron()`, uses the URL read from the
 *   spawned sidecar (`SIDECAR_LISTENING` → main process → IPC), so the port can differ from 8000.
 * - Development / browser: defaults to http://127.0.0.1:8000 unless `VITE_API_BASE_URL` is set.
 * - Override: `VITE_API_BASE_URL` in `.env` / `.env.local` (origin only, no trailing `/api`).
 * - Deployed web: set `VITE_API_BASE_URL` at build time.
 *
 * Note: mocked in tests (see tests/__mocks__/config/api.ts)
 */

function normalizeApiOrigin(raw: string): string {
  let s = raw.trim().replace(/\/+$/, "");
  if (s.toLowerCase().endsWith("/api")) {
    s = s.slice(0, -4).replace(/\/+$/, "");
  }
  return s;
}

const fromEnv = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();

/** Set when running under Electron and main process spawned the sidecar. */
let electronManagedOrigin: string | null = null;

/**
 * Call once before rendering (see main.tsx). Resolves IPC from Electron when available.
 */
export async function initApiBaseUrlFromElectron(): Promise<void> {
  const w = window as Window & {
    projectInsights?: { getBackendApiOrigin(): Promise<string | null> };
  };
  if (!w.projectInsights?.getBackendApiOrigin) {
    return;
  }
  try {
    const o = await w.projectInsights.getBackendApiOrigin();
    if (o) {
      electronManagedOrigin = normalizeApiOrigin(o);
    }
  } catch {
    /* keep static fallback */
  }
}

export function getApiBaseUrl(): string {
  if (electronManagedOrigin) {
    return electronManagedOrigin;
  }
  if (fromEnv) {
    return normalizeApiOrigin(fromEnv);
  }
  return "http://127.0.0.1:8000";
}
