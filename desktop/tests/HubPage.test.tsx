import { render, screen, fireEvent } from '@testing-library/react';
import { HubPage } from '../src/pages/HubPage';
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

test('renders hub page with title', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Where would you like to go/i);
  expect(title).toBeDefined();
});

test('renders six navigation cards', () => {
  const { container } = render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const cards = container.querySelectorAll('.hub-card');
  expect(cards.length).toBe(6);
});

test('renders Upload File card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Upload File')).toBeInTheDocument();
  expect(screen.getByText(/Upload and analyze your project files/i)).toBeInTheDocument();
});

test('renders Resume Builder card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Resume Builder')).toBeInTheDocument();
  expect(screen.getByText(/Build and tailor your resume/i)).toBeInTheDocument();
});

test('renders Portfolio card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Portfolio')).toBeInTheDocument();
  expect(screen.getByText(/View your portfolio with charts/i)).toBeInTheDocument();
});

test('renders Data Management card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Data Management')).toBeInTheDocument();
  expect(screen.getByText(/Review and edit project dates/i)).toBeInTheDocument();
});

test('renders Check Job Match card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Check Job Match')).toBeInTheDocument();
  expect(screen.getByText(/Check how well your resume matches a job description/i)).toBeInTheDocument();
});

test('renders Learnings card', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByText('Learnings')).toBeInTheDocument();
  expect(screen.getByText(/Course recommendations based on your profile/i)).toBeInTheDocument();
});

test('navigates to upload page on card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Upload File');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/uploadpage');
});

test('navigates to resume builder on card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Resume Builder');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/resumebuilderpage');
});

test('navigates to portfolio on card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Portfolio');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/portfoliopage');
});

test('navigates to data management on card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Data Management');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/datamanagementpage');
});

test('navigates to profile learning tab on Learnings card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Learnings');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/userpreferencepage?tab=learning');
});

test('navigates to ATS scoring on card click', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  const card = screen.getByLabelText('Go to Check Job Match');
  fireEvent.click(card);
  expect(mockNavigate).toHaveBeenCalledWith('/atsscoringpage');
});

test('each card has an accessible aria-label', () => {
  render(
    <BrowserRouter>
      <HubPage />
    </BrowserRouter>
  );

  expect(screen.getByLabelText('Go to Upload File')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Resume Builder')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Portfolio')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Data Management')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Check Job Match')).toBeInTheDocument();
  expect(screen.getByLabelText('Go to Learnings')).toBeInTheDocument();
});
