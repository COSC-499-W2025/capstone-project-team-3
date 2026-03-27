/**
 * API Configuration
 *
 * - Development: defaults to http://127.0.0.1:8000 (avoids some "Failed to fetch" cases where
 *   `localhost` resolves to IPv6 ::1 but the API is only listening on IPv4).
 * - Override anytime: `VITE_API_BASE_URL=http://localhost:8000` in `.env` / `.env.local`.
 *   Use the server origin only — do not include `/api` (paths in client code already add `/api/...`).
 * - Production: set `VITE_API_BASE_URL` at build time, or update the fallback below.
 *
 * Note: This file is mocked in tests (see tests/__mocks__/config/api.ts)
 */

function normalizeApiOrigin(raw: string): string {
  let s = raw.trim().replace(/\/+$/, "");
  // Avoid http://host:8000/api + /api/... → /api/api/... (404 on learning and other routes)
  if (s.toLowerCase().endsWith("/api")) {
    s = s.slice(0, -4).replace(/\/+$/, "");
  }
  return s;
}

const isDevelopment = import.meta.env.DEV;
const fromEnv = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();

export const API_BASE_URL = (() => {
  if (fromEnv) {
    return normalizeApiOrigin(fromEnv);
  }
  if (isDevelopment) {
    return "http://127.0.0.1:8000";
  }
  return "https://your-production-api.com";
})();
