/**
 * API Configuration
 * 
 * Automatically uses localhost in development and production URL in builds.
 * No environment variables needed.
 * 
 * Note: This file is mocked in tests (see tests/__mocks__/config/api.ts)
 */

const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'                    // Development
  : 'https://your-production-api.com';         // Production - UPDATE THIS WHEN WE HAVE A PROD LINK
