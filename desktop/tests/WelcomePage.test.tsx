import { render, screen, fireEvent, act } from '@testing-library/react';
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

test('returning user: auto-redirects to hub after delay and click goes to hub', async () => {
  mockFetch.mockResolvedValue({
    ok: true,
    json: async () => ({ has_consent: true }),
  });

  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });

  const container = screen.getByText(/Welcome to your Big Picture/i).closest('.welcome-container');
  if (container) fireEvent.click(container);
  expect(mockNavigate).toHaveBeenCalledWith('/hubpage');

  await jest.runAllTimersAsync();
  expect(mockNavigate).toHaveBeenLastCalledWith('/hubpage');
});

test('first-time user: does not auto-redirect to hub and click goes to consent page', async () => {
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

  const container = screen.getByText(/Welcome to your Big Picture/i).closest('.welcome-container');
  if (container) fireEvent.click(container);
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

test('when consent API fails, does not redirect to hub', async () => {
  mockFetch.mockRejectedValue(new Error('Network error'));

  await act(async () => {
    render(
      <BrowserRouter>
        <WelcomePage />
      </BrowserRouter>
    );
    await Promise.resolve();
    await Promise.resolve();
  });

  expect(mockNavigate).not.toHaveBeenCalled();
});
