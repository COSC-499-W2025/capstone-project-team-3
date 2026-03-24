/**
 * API Configuration
 *
 * - Development: defaults to http://127.0.0.1:8000 (avoids some "Failed to fetch" cases where
 *   `localhost` resolves to IPv6 ::1 but the API is only listening on IPv4).
 * - Override anytime: `VITE_API_BASE_URL=http://localhost:8000` in `.env` / `.env.local`.
 * - Production: set `VITE_API_BASE_URL` at build time, or update the fallback below.
 *
 * Note: This file is mocked in tests (see tests/__mocks__/config/api.ts)
 */

const isDevelopment = import.meta.env.DEV;
const fromEnv = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();

export const API_BASE_URL = (() => {
  if (fromEnv) {
    return fromEnv.replace(/\/$/, "");
  }
  if (isDevelopment) {
    return "http://127.0.0.1:8000";
  }
  return "https://your-production-api.com";
})();
