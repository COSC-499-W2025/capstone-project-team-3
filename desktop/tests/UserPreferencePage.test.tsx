import { render, screen, waitFor } from '@testing-library/react';
import UserPreferencePage from '../src/pages/UserPreferencePage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as userPreferencesApi from '../src/api/userPreferences';

// Mock the API module
jest.mock('../src/api/userPreferences');

const mockGetUserPreferences = userPreferencesApi.getUserPreferences as jest.MockedFunction<typeof userPreferencesApi.getUserPreferences>;

beforeEach(() => {
  // Mock API to return empty preferences so component renders
  mockGetUserPreferences.mockResolvedValue({
    name: '',
    email: '',
    github_user: '',
    education: '',
    industry: '',
    job_title: '',
    education_details: null,
  });
});

test('renders user preference page with title', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const title = screen.getByText(/Build your Profile/i);
    expect(title).toBeDefined();
  });
});

test('renders all form sections', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Full name/i)).toBeDefined();
    expect(screen.getByText(/Educational Background/i)).toBeDefined();
    expect(screen.getByText(/Industry/i)).toBeDefined();
  });
});

test('renders all input fields', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Full name/i)).toBeDefined();
    expect(screen.getByText(/Email/i)).toBeDefined();
    expect(screen.getByText(/GitHub username/i)).toBeDefined();
    expect(screen.getByText(/LinkedIn profile/i)).toBeDefined();
    expect(screen.getByText(/Job Title \(Aspiring or Current\)/i)).toBeDefined();
    expect(screen.getByText(/Industry/i)).toBeDefined();
  });
});

test('renders save button', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const saveButton = screen.getByText(/Save Profile/i);
    expect(saveButton).toBeDefined();
  });
});

test('renders add education button', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const addButton = container.querySelector('.btn-add');
    expect(addButton).toBeDefined();
  });
});

test('renders industry buttons', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Technology/i)).toBeDefined();
    expect(screen.getByText(/Healthcare/i)).toBeDefined();
    expect(screen.getByText(/Finance/i)).toBeDefined();
  });
});

test('renders form structure', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const formSections = container.querySelectorAll('.form-section');
    expect(formSections.length).toBeGreaterThan(0);
  });
});
