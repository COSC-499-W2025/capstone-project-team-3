import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserPreferencePage from '../src/pages/UserPreferencePage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as userPreferencesApi from '../src/api/userPreferences';
import * as learningApi from '../src/api/learning';

// Mock the API module
jest.mock('../src/api/userPreferences');
jest.mock('../src/api/learning', () => ({
  ...jest.requireActual<typeof import('../src/api/learning')>('../src/api/learning'),
  getLearningRecommendations: jest.fn(),
}));

jest.mock('../src/api/projects', () => ({
  getProjects: jest.fn().mockResolvedValue([
    {
      id: 'p1',
      name: 'Demo Project',
      score: 0.75,
      skills: ['Python'],
      date_added: '2024-01-01',
    },
  ]),
}));

const mockGetUserPreferences = userPreferencesApi.getUserPreferences as jest.MockedFunction<typeof userPreferencesApi.getUserPreferences>;
const mockUploadProfilePicture = userPreferencesApi.uploadProfilePicture as jest.MockedFunction<typeof userPreferencesApi.uploadProfilePicture>;
const mockDeleteProfilePicture = userPreferencesApi.deleteProfilePicture as jest.MockedFunction<typeof userPreferencesApi.deleteProfilePicture>;
const mockGetProfilePictureUrl = userPreferencesApi.getProfilePictureUrl as jest.MockedFunction<typeof userPreferencesApi.getProfilePictureUrl>;
const mockGetLearningRecommendations = learningApi.getLearningRecommendations as jest.MockedFunction<
  typeof learningApi.getLearningRecommendations
>;

beforeEach(() => {
  jest.clearAllMocks();
  // Mock API to return empty preferences so component renders
  mockGetUserPreferences.mockResolvedValue({
    name: '',
    email: '',
    github_user: '',
    linkedin: null,
    education: '',
    industry: '',
    job_title: '',
    education_details: null,
    profile_picture_path: null,
    personal_summary: null,
  });
  mockGetProfilePictureUrl.mockReturnValue('http://localhost:8000/api/user-preferences/profile-picture');
  mockGetLearningRecommendations.mockResolvedValue({
    based_on_resume: [
      {
        id: 'c1',
        title: 'Starter course',
        description: 'Short description',
        url: 'https://example.com/s',
        thumbnail_url: 'https://example.com/t.png',
        provider: 'Example',
        tags: ['python'],
        level: 'starter',
        pricing: 'free',
      },
    ],
    next_steps: [
      {
        id: 'c2',
        title: 'Advanced course',
        description: 'Next step description',
        url: 'https://example.com/a',
        thumbnail_url: 'https://example.com/t2.png',
        provider: 'Example',
        tags: ['system-design'],
        level: 'advanced',
        pricing: 'paid',
      },
    ],
  });
});

async function openProfileEditMode() {
  await waitFor(() => {
    expect(screen.getByRole('button', { name: /^edit profile$/i })).toBeInTheDocument();
  });
  fireEvent.click(screen.getByRole('button', { name: /^edit profile$/i }));
  await waitFor(() => {
    expect(screen.getByText(/Save Profile/i)).toBeInTheDocument();
  });
}

test('renders user preference page with title', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const title = screen.getByText(/Your profile/i);
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
    expect(screen.getByText(/Educational background/i)).toBeDefined();
    expect(screen.getByText(/Industry/i)).toBeDefined();
  });
});

test('renders all input fields', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    expect(screen.getByText(/Full name/i)).toBeDefined();
    expect(screen.getByText(/Email/i)).toBeDefined();
    expect(screen.getByText(/GitHub username/i)).toBeDefined();
    expect(screen.getByText(/LinkedIn profile/i)).toBeDefined();
    expect(screen.getByText(/Job Title \(Aspiring or Current\)/i)).toBeDefined();
    expect(screen.getByText(/Industry/i)).toBeDefined();
  });
});

test('renders Edit profile in view mode and Save Profile after entering edit mode', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByRole('button', { name: /^edit profile$/i })).toBeInTheDocument();
  });
  await openProfileEditMode();
  expect(screen.getByText(/Save Profile/i)).toBeInTheDocument();
});

test('renders add education button', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
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

  await openProfileEditMode();
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

  await openProfileEditMode();
  await waitFor(() => {
    const formSections = container.querySelectorAll('.form-section');
    expect(formSections.length).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// Profile picture section
// ---------------------------------------------------------------------------

test('renders profile picture section', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const section = container.querySelector('.profile-picture-section');
    expect(section).not.toBeNull();
  });
});

test('shows Upload Photo button when no picture is set', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    expect(screen.getByText(/Upload Photo/i)).toBeDefined();
  });
});

test('shows placeholder avatar when no picture is set', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const placeholder = container.querySelector('.profile-picture-placeholder');
    expect(placeholder).not.toBeNull();
    const img = container.querySelector('.profile-picture-img');
    expect(img).toBeNull();
  });
});

test('shows profile picture image when profile_picture_path is set', async () => {
  mockGetUserPreferences.mockResolvedValue({
    name: 'Jane',
    email: 'jane@example.com',
    github_user: 'jane',
    linkedin: null,
    education: "Bachelor's",
    industry: 'Technology',
    job_title: 'Developer',
    education_details: null,
    profile_picture_path: 'data/thumbnails/profile_picture.png',
  });

  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    const img = container.querySelector('.profile-picture-img') as HTMLImageElement | null;
    expect(img).not.toBeNull();
    expect(img?.src).toContain('user-preferences/profile-picture');
  });
});

test('shows Change Photo and Remove buttons when picture is loaded', async () => {
  mockGetUserPreferences.mockResolvedValue({
    name: 'Jane',
    email: 'jane@example.com',
    github_user: 'jane',
    linkedin: null,
    education: "Bachelor's",
    industry: 'Technology',
    job_title: 'Developer',
    education_details: null,
    profile_picture_path: 'data/thumbnails/profile_picture.png',
  });

  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    expect(screen.getByText(/Change Photo/i)).toBeDefined();
    expect(screen.getByText(/Remove/i)).toBeDefined();
  });
});

test('Remove button calls deleteProfilePicture and clears image', async () => {
  mockGetUserPreferences.mockResolvedValue({
    name: 'Jane',
    email: 'jane@example.com',
    github_user: 'jane',
    linkedin: null,
    education: "Bachelor's",
    industry: 'Technology',
    job_title: 'Developer',
    education_details: null,
    profile_picture_path: 'data/thumbnails/profile_picture.png',
  });
  mockDeleteProfilePicture.mockResolvedValue({ status: 'ok', message: 'Profile picture removed' });

  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => screen.getByText(/Remove/i));

  fireEvent.click(screen.getByText(/Remove/i));

  await waitFor(() => {
    expect(mockDeleteProfilePicture).toHaveBeenCalledTimes(1);
    // After removal, placeholder should be shown and img should be gone
    const img = container.querySelector('.profile-picture-img');
    expect(img).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Personal summary textarea tests
// ---------------------------------------------------------------------------

test('renders Professional Summary textarea field', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    expect(screen.getByText(/Professional Summary/i)).toBeDefined();
  });
});

test('pre-populates personal summary textarea from API response', async () => {
  mockGetUserPreferences.mockResolvedValue({
    name: 'Jane',
    email: 'jane@example.com',
    github_user: 'jane',
    linkedin: null,
    education: "Bachelor's",
    industry: 'Technology',
    job_title: 'Developer',
    education_details: null,
    profile_picture_path: null,
    personal_summary: 'Experienced developer passionate about clean code.',
  });

  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    const textarea = container.querySelector('textarea') as HTMLTextAreaElement | null;
    expect(textarea).not.toBeNull();
    expect(textarea?.value).toBe('Experienced developer passionate about clean code.');
  });
});

test('personal summary textarea is empty when personal_summary is null', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => {
    const textarea = container.querySelector('textarea') as HTMLTextAreaElement | null;
    expect(textarea).not.toBeNull();
    expect(textarea?.value).toBe('');
  });
});

test('personal summary textarea accepts user input', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await openProfileEditMode();
  await waitFor(() => screen.getByText(/Professional Summary/i));

  const textarea = container.querySelector('textarea') as HTMLTextAreaElement;
  fireEvent.change(textarea, { target: { value: 'New summary text.' } });

  expect(textarea.value).toBe('New summary text.');
});

test('Learning tab loads recommendations and shows both sections', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByRole('tab', { name: /^Learning$/i })).toBeDefined();
  });

  fireEvent.click(screen.getByRole('tab', { name: /^Learning$/i }));

  await waitFor(() => {
    expect(mockGetLearningRecommendations).toHaveBeenCalled();
  });

  await waitFor(() => {
    expect(screen.getByText(/Based on your data/i)).toBeDefined();
    expect(screen.getByText(/Next steps/i)).toBeDefined();
    expect(screen.getByText(/Starter course/i)).toBeDefined();
    expect(screen.getByText(/Advanced course/i)).toBeDefined();
  });
});
