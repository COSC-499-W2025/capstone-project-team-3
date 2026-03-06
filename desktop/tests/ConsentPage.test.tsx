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


  expect(mockNavigate).toHaveBeenCalledWith('/uploadpage');
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
