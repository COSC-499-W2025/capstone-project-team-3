// Mock for API config in tests
export async function initApiBaseUrlFromElectron(): Promise<void> {}

export function getApiBaseUrl(): string {
  return 'http://localhost:8000'
}
