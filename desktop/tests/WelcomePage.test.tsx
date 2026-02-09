import { render, screen, fireEvent } from '@testing-library/react';
import { WelcomePage } from '../src/pages/WelcomePage';
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

test('renders welcome page with title', () => {
  render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Welcome to your Big Picture/i);
  expect(title).toBeDefined();
});

test('navigates to upload page on click', () => {
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

  expect(mockNavigate).toHaveBeenCalledWith('/uploadpage');
});

test('renders nested frame structure', () => {
  const { container } = render(
    <BrowserRouter>
      <WelcomePage />
    </BrowserRouter>
  );

  const frames = container.querySelectorAll('.welcome-frame');
  expect(frames.length).toBe(4);
});
