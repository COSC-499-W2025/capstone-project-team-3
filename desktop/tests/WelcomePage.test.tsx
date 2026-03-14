import { render, screen, fireEvent } from '@testing-library/react';
import { WelcomePage } from '../src/pages/WelcomePage';
import { jest, test, expect, beforeEach, afterEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

const mockNavigate = jest.fn();
const mockFetch = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual<typeof import('react-router-dom')>('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

beforeEach(() => {
  mockNavigate.mockClear();
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({ ok: false }); // default: no consent, no redirect
  global.fetch = mockFetch;
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

test('renders welcome page with title', () => {
  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Welcome to your Big Picture/i);
  expect(title).toBeDefined();
});

test('navigates to consent page on click', () => {
  mockFetch.mockResolvedValue({ ok: false }); // no consent, so no auto-redirect

  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  const container = screen.getByText(/Welcome to your Big Picture/i).closest('.welcome-container');
  expect(container).toBeDefined();

  if (container) {
    fireEvent.click(container);
  }

  expect(mockNavigate).toHaveBeenCalledWith('/consentpage');
});

test('renders nested frame structure', () => {
  mockFetch.mockResolvedValue({ ok: false });

  const { container } = render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  const frames = container.querySelectorAll('.welcome-frame');
  expect(frames.length).toBe(4);
});

test('returning user: when API returns has_consent true, navigates to hub after delay', async () => {
  mockFetch.mockResolvedValue({
    ok: true,
    json: async () => ({ has_consent: true }),
  });

  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  expect(mockNavigate).not.toHaveBeenCalled();

  await jest.runAllTimersAsync();

  expect(mockNavigate).toHaveBeenCalledWith('/hubpage');
});

test('first-time user: when API returns has_consent false, does not redirect to hub', async () => {
  mockFetch.mockResolvedValue({
    ok: true,
    json: async () => ({ has_consent: false }),
  });

  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  await jest.runAllTimersAsync();

  expect(mockNavigate).not.toHaveBeenCalled();
});

test('when consent API fails, does not redirect to hub', async () => {
  mockFetch.mockRejectedValue(new Error('Network error'));

  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  await jest.runAllTimersAsync();

  expect(mockNavigate).not.toHaveBeenCalled();
});
