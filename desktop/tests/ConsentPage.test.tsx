import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ConsentPage } from '../src/pages/ConsentPage';
import { jest, test, expect, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

// Mock useNavigate
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual<typeof import('react-router-dom')>('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock fetch API
const mockFetch = jest.fn() as jest.Mock;
(globalThis as unknown as { fetch: jest.Mock }).fetch = mockFetch;

const mockConsentTextResponse = {
  consent_message: 'Test consent message',
  detailed_info: 'Test detailed info',
  granted_message: 'Consent granted',
  declined_message: 'Consent declined',
  already_provided_message: 'You have already provided consent',
};

const mockConsentStatusNoConsent = {
  has_consent: false,
  timestamp: null,
};

const mockConsentStatusWithConsent = {
  has_consent: true,
  timestamp: '2026-03-06T12:00:00Z',
};

beforeEach(() => {
  mockNavigate.mockClear();
  mockFetch.mockClear();
});

const setupFetchMocks = (hasConsent: boolean) => {
  mockFetch.mockImplementation((...args: unknown[]) => {
    const url = args[0] as string;
    const urlString = url.toString();
    if (urlString.includes('/api/privacy-consent/text')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentTextResponse),
        text: () => Promise.resolve(JSON.stringify(mockConsentTextResponse)),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(hasConsent ? mockConsentStatusWithConsent : mockConsentStatusNoConsent),
        text: () => Promise.resolve(JSON.stringify(hasConsent ? mockConsentStatusWithConsent : mockConsentStatusNoConsent)),
      } as Response);
    }
    return Promise.reject(new Error('Unknown URL'));
  });
};

test('renders consent page container', async () => {
  setupFetchMocks(false);
  
  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const consentContainer = container.querySelector('.consent-container');
    expect(consentContainer).toBeDefined();
  });
});

test('renders consent frame', async () => {
  setupFetchMocks(false);
  
  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const frame = container.querySelector('.consent-frame');
    expect(frame).toBeDefined();
  });
});

test('renders consent content area', async () => {
  setupFetchMocks(false);
  
  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const content = container.querySelector('.consent-content');
    expect(content).toBeDefined();
  });
});

test('renders consent actions area', async () => {
  setupFetchMocks(false);
  
  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const actions = container.querySelector('.consent-actions');
    expect(actions).toBeDefined();
  });
});

test('displays consent message when no consent', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const consentMessage = screen.getByText(/Test consent message/i);
    expect(consentMessage).toBeDefined();
  });
});

test('renders Accept, Decline, and More buttons when no consent', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Accept/i)).toBeDefined();
    expect(screen.getByText(/Decline/i)).toBeDefined();
    expect(screen.getByText(/More/i)).toBeDefined();
  });
});

test('shows detailed info when More button is clicked', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/More/i)).toBeDefined();
  });

  const moreButton = screen.getByText(/More/i);
  fireEvent.click(moreButton);

  await waitFor(() => {
    expect(screen.getByText(/Test detailed info/i)).toBeDefined();
  });
});

test('shows Back button when viewing detailed info', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/More/i)).toBeDefined();
  });

  const moreButton = screen.getByText(/More/i);
  fireEvent.click(moreButton);

  await waitFor(() => {
    expect(screen.queryByText(/Back/i)).toBeDefined();
  }, { timeout: 3000 });
});

test('renders Continue and Revoke buttons when consent exists', async () => {
  setupFetchMocks(true);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Continue/i)).toBeDefined();
    expect(screen.getByText(/Revoke Consent/i)).toBeDefined();
  });
});

test('displays already provided message when consent exists', async () => {
  setupFetchMocks(true);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const alreadyProvidedMessage = screen.getByText(/You have already provided consent/i);
    expect(alreadyProvidedMessage).toBeDefined();
  });
});

test('displays consent timestamp when consent exists', async () => {
  setupFetchMocks(true);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const timestampText = screen.getByText(/Consent provided on/i);
    expect(timestampText).toBeDefined();
  });
});

test('Continue button navigates to upload page', async () => {
  setupFetchMocks(true);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Continue/i)).toBeDefined();
  });

  const continueButton = screen.getByText(/Continue/i);
  fireEvent.click(continueButton);


  expect(mockNavigate).toHaveBeenCalledWith('/userpreferencepage');
});

test('Accept button is clickable', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Accept/i)).toBeDefined();
  });

  const acceptButton = screen.getByText(/Accept/i);
  expect(acceptButton).toBeDefined();
  fireEvent.click(acceptButton);
});

test('Decline button is clickable', async () => {
  setupFetchMocks(false);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Decline/i)).toBeDefined();
  });

  const declineButton = screen.getByText(/Decline/i);
  expect(declineButton).toBeDefined();
  fireEvent.click(declineButton);
});

test('Revoke button is clickable when consent exists', async () => {
  setupFetchMocks(true);
  
  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Revoke Consent/i)).toBeDefined();
  });

  const revokeButton = screen.getByText(/Revoke Consent/i);
  fireEvent.click(revokeButton);
});

// --- Negative / Error-case tests ---

test('buttons remain disabled when consent status fetch fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
  mockFetch.mockImplementation(() => {
    return Promise.resolve({
      ok: false,
      text: () => Promise.resolve('Internal Server Error'),
    } as Response);
  });

  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  // Wait for the failed fetch to complete
  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalled();
  });

  // Consent action buttons should be disabled since messages never loaded (Back stays enabled)
  expect(screen.getByRole('button', { name: 'Accept' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Decline' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'More Info' })).toBeDisabled();

  consoleSpy.mockRestore();
});

test('buttons remain disabled when consent text fetch fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
  mockFetch.mockImplementation((...args: unknown[]) => {
    const url = args[0] as string;
    const urlString = url.toString();
    // Status endpoint succeeds
    if (urlString.includes('/api/privacy-consent/text')) {
      return Promise.resolve({
        ok: false,
        text: () => Promise.resolve('Text endpoint error'),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentStatusNoConsent),
        text: () => Promise.resolve(JSON.stringify(mockConsentStatusNoConsent)),
      } as Response);
    }
    return Promise.reject(new Error('Unknown URL'));
  });

  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalled();
  });

  // Consent action buttons should be disabled since messages never loaded
  expect(screen.getByRole('button', { name: 'Accept' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Decline' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'More Info' })).toBeDisabled();

  consoleSpy.mockRestore();
});

test('network error on initial fetch keeps buttons disabled', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
  mockFetch.mockImplementation(() => {
    return Promise.reject(new Error('Network error'));
  });

  render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalled();
  });

  // Consent action buttons should be disabled when fetch fails
  expect(screen.getByRole('button', { name: 'Accept' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Decline' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'More Info' })).toBeDisabled();

  consoleSpy.mockRestore();
});

test('no notification shown when accept POST fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});

  mockFetch.mockImplementation((...args: unknown[]) => {
    const url = args[0] as string;
    const options = args[1] as RequestInit | undefined;
    const urlString = url.toString();
    if (urlString.includes('/api/privacy-consent') && options?.method === 'POST') {
      return Promise.resolve({
        ok: false,
        text: () => Promise.resolve('Submit failed'),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent/text')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentTextResponse),
        text: () => Promise.resolve(JSON.stringify(mockConsentTextResponse)),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentStatusNoConsent),
        text: () => Promise.resolve(JSON.stringify(mockConsentStatusNoConsent)),
      } as Response);
    }
    return Promise.reject(new Error('Unknown URL'));
  });

  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  // Wait for messages to load so buttons become enabled
  await waitFor(() => {
    const acceptBtn = screen.getByText(/Accept/i);
    expect(acceptBtn.getAttribute('disabled')).toBeNull();
  });

  fireEvent.click(screen.getByText(/Accept/i));

  // Wait for the POST error to be logged
  await waitFor(() => {
    const errorCalls = consoleSpy.mock.calls.map((call) => call[0]);
    expect(errorCalls).toContain('Failed to submit consent:');
  });

  // No notification should appear on error
  const notification = container.querySelector('.notification');
  expect(notification).toBeNull();

  consoleSpy.mockRestore();
  consoleLogSpy.mockRestore();
});

test('no notification shown when revoke DELETE fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

  mockFetch.mockImplementation((...args: unknown[]) => {
    const url = args[0] as string;
    const options = args[1] as RequestInit | undefined;
    const urlString = url.toString();
    if (urlString.includes('/api/privacy-consent') && options?.method === 'DELETE') {
      return Promise.resolve({
        ok: false,
        text: () => Promise.resolve('Delete failed'),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent/text')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentTextResponse),
        text: () => Promise.resolve(JSON.stringify(mockConsentTextResponse)),
      } as Response);
    }
    if (urlString.includes('/api/privacy-consent')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConsentStatusWithConsent),
        text: () => Promise.resolve(JSON.stringify(mockConsentStatusWithConsent)),
      } as Response);
    }
    return Promise.reject(new Error('Unknown URL'));
  });

  const { container } = render(
    <BrowserRouter>
      <ConsentPage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Revoke Consent/i)).toBeDefined();
  });

  fireEvent.click(screen.getByText(/Revoke Consent/i));

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith('Failed to revoke consent:', expect.anything());
  });

  // No notification should appear on error
  const notification = container.querySelector('.notification');
  expect(notification).toBeNull();

  consoleSpy.mockRestore();
});

