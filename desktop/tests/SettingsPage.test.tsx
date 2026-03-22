import { render, screen, fireEvent } from '@testing-library/react';
import { SettingsPage } from '../src/pages/SettingsPage';
import { jest, test, expect, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

// Mock useNavigate
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual<typeof import('react-router-dom')>('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

beforeEach(() => {
  mockNavigate.mockClear();
});

test('renders settings page with title', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const title = screen.getByText('Settings');
  expect(title).toBeDefined();
});

test('renders settings page with subtitle', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByText(/What would you like to manage/i)).toBeInTheDocument();
});

test('renders three settings cards', () => {
  const { container } = render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const cards = container.querySelectorAll('.settings-card');
  expect(cards.length).toBe(3);
});

test('renders Profile card', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Profile')).toBeInTheDocument();
  expect(screen.getByText(/Update your personal information and job preferences/i)).toBeInTheDocument();
});

test('renders Privacy card', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Privacy')).toBeInTheDocument();
  expect(screen.getByText(/Review and manage your data consent settings/i)).toBeInTheDocument();
});

test('renders Gemini API key card', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Gemini API key')).toBeInTheDocument();
  expect(
    screen.getByText(/Add your Google Gemini key for AI analysis, or review setup instructions/i),
  ).toBeInTheDocument();
});

test('navigates to user preference page on Profile card click', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Profile');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/userpreferencepage');
});

test('navigates to consent page on Privacy card click', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Privacy');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/consentpage');
});

test('navigates to Gemini API key page on Gemini card click', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Gemini API key');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/geminiapikeypage');
});

test('renders back button', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByLabelText('Back to Hub')).toBeInTheDocument();
});

test('navigates back to hub page on back button click', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  const backBtn = screen.getByLabelText('Back to Hub');
  fireEvent.click(backBtn);
  expect(mockNavigate).toHaveBeenCalledWith(-1);
});

test('each settings card has an accessible aria-label', () => {
  render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );

  expect(screen.getByLabelText('Go to Profile')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Privacy')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Gemini API key')).toBeInTheDocument();
});
