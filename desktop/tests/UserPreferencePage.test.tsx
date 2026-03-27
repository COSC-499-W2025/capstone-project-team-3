import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import UserPreferencePage from '../src/pages/UserPreferencePage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as userPreferencesApi from '../src/api/userPreferences';
import * as consentApi from '../src/api/consent';
import * as learningApi from '../src/api/learning';

// Mock the API modules
jest.mock('../src/api/userPreferences');
jest.mock('../src/api/consent');

const mockGetConsentStatus = consentApi.getConsentStatus as jest.MockedFunction<typeof consentApi.getConsentStatus>;
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
const mockSaveUserPreferences = userPreferencesApi.saveUserPreferences as jest.MockedFunction<typeof userPreferencesApi.saveUserPreferences>;
const mockUploadProfilePicture = userPreferencesApi.uploadProfilePicture as jest.MockedFunction<typeof userPreferencesApi.uploadProfilePicture>;
const mockDeleteProfilePicture = userPreferencesApi.deleteProfilePicture as jest.MockedFunction<typeof userPreferencesApi.deleteProfilePicture>;
const mockGetProfilePictureUrl = userPreferencesApi.getProfilePictureUrl as jest.MockedFunction<typeof userPreferencesApi.getProfilePictureUrl>;
const mockGetAllInstitutions = userPreferencesApi.getAllInstitutions as jest.MockedFunction<typeof userPreferencesApi.getAllInstitutions>;
const mockGetLearningRecommendations = learningApi.getLearningRecommendations as jest.MockedFunction<
  typeof learningApi.getLearningRecommendations
>;

beforeEach(() => {
  jest.clearAllMocks();
  mockGetConsentStatus.mockResolvedValue({ has_consent: true });
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
  mockSaveUserPreferences.mockResolvedValue({ status: 'ok', message: 'Saved' });
  mockGetProfilePictureUrl.mockReturnValue('http://localhost:8000/api/user-preferences/profile-picture');
  mockGetAllInstitutions.mockResolvedValue({ institutions: [], status: 'ok', count: 0 });
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

// ---------------------------------------------------------------------------
// Required field indicators
// ---------------------------------------------------------------------------

test('displays asterisks on required fields', async () => {
  const { container } = render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  const indicators = container.querySelectorAll('.required-indicator');
  // Legend + Full Name, Email, Job Title, Industry = 5 asterisks
  expect(indicators.length).toBe(5);
});

test('displays required fields legend', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => {
    expect(screen.getByText(/Fields marked with/i)).toBeDefined();
  });
});

test('required inputs have aria-required attribute', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  const fullName = screen.getByPlaceholderText('Enter your full name');
  const email = screen.getByPlaceholderText('your.email@example.com');
  const jobTitle = screen.getByPlaceholderText('e.g., Software Engineer, Data Scientist');

  expect(fullName.getAttribute('aria-required')).toBe('true');
  expect(email.getAttribute('aria-required')).toBe('true');
  expect(jobTitle.getAttribute('aria-required')).toBe('true');
});

test('required inputs have native required attribute', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  const fullName = screen.getByPlaceholderText('Enter your full name');
  const email = screen.getByPlaceholderText('your.email@example.com');
  const jobTitle = screen.getByPlaceholderText('e.g., Software Engineer, Data Scientist');

  expect(fullName).toHaveAttribute('required');
  expect(email).toHaveAttribute('required');
  expect(jobTitle).toHaveAttribute('required');
});

// ---------------------------------------------------------------------------
// Profile form validation on save
// ---------------------------------------------------------------------------

test('shows validation errors when saving with empty required fields', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(screen.getByText('Full name is required.')).toBeDefined();
    expect(screen.getByText('Email is required.')).toBeDefined();
    expect(screen.getByText('Job title is required.')).toBeDefined();
    expect(screen.getByText('Please select an industry.')).toBeDefined();
  });

  // Should NOT have called the API
  expect(mockSaveUserPreferences).not.toHaveBeenCalled();
});

test('shows email format error for invalid email', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  fireEvent.change(screen.getByPlaceholderText('Enter your full name'), { target: { value: 'Jane Doe' } });
  fireEvent.change(screen.getByPlaceholderText('your.email@example.com'), { target: { value: 'not-an-email' } });
  fireEvent.change(screen.getByPlaceholderText('e.g., Software Engineer, Data Scientist'), { target: { value: 'Developer' } });
  fireEvent.click(screen.getByText('Technology'));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(screen.getByText('Please enter a valid email address.')).toBeDefined();
  });

  expect(mockSaveUserPreferences).not.toHaveBeenCalled();
});

test('shows LinkedIn URL format error for invalid URL', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  fireEvent.change(screen.getByPlaceholderText('Enter your full name'), { target: { value: 'Jane Doe' } });
  fireEvent.change(screen.getByPlaceholderText('your.email@example.com'), { target: { value: 'jane@example.com' } });
  fireEvent.change(screen.getByPlaceholderText('e.g., Software Engineer, Data Scientist'), { target: { value: 'Developer' } });
  fireEvent.change(screen.getByPlaceholderText('https://linkedin.com/in/your-profile'), { target: { value: 'not-a-url' } });
  fireEvent.click(screen.getByText('Technology'));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(screen.getByText(/Please enter a valid URL/i)).toBeDefined();
  });

  expect(mockSaveUserPreferences).not.toHaveBeenCalled();
});

test('accepts valid LinkedIn URL and saves successfully', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  fireEvent.change(screen.getByPlaceholderText('Enter your full name'), { target: { value: 'Jane Doe' } });
  fireEvent.change(screen.getByPlaceholderText('your.email@example.com'), { target: { value: 'jane@example.com' } });
  fireEvent.change(screen.getByPlaceholderText('e.g., Software Engineer, Data Scientist'), { target: { value: 'Developer' } });
  fireEvent.change(screen.getByPlaceholderText('https://linkedin.com/in/your-profile'), { target: { value: 'https://linkedin.com/in/janedoe' } });
  fireEvent.click(screen.getByText('Technology'));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(mockSaveUserPreferences).toHaveBeenCalledTimes(1);
  });
});

test('blocks profile save when an existing education entry is invalid', async () => {
  mockGetUserPreferences.mockResolvedValueOnce({
    name: 'Jane Doe',
    email: 'jane@example.com',
    github_user: '',
    linkedin: null,
    education: "Bachelor's",
    industry: 'Technology',
    job_title: 'Developer',
    education_details: [
      {
        institution: 'MIT',
        degree: 'B.S. Computer Science',
        start_date: '2024-06-01',
        end_date: '2023-01-01',
        gpa: 4.5,
      },
    ],
    profile_picture_path: null,
    personal_summary: null,
  });

  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText('MIT'));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(screen.getByText(/MIT: GPA must be between 0 and 4\.33\./i)).toBeDefined();
  });

  expect(mockSaveUserPreferences).not.toHaveBeenCalled();
});

test('clears field error when user starts typing', async () => {
test('Learning tab loads recommendations and shows both sections', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  // Trigger validation errors
  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    expect(screen.getByText('Full name is required.')).toBeDefined();
  });

  // Start typing in the full name field
  fireEvent.change(screen.getByPlaceholderText('Enter your full name'), { target: { value: 'J' } });

  // The full name error should be cleared
  expect(screen.queryByText('Full name is required.')).toBeNull();
});

test('adds input-error class to invalid fields', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Save Profile/i));

  fireEvent.click(screen.getByText(/Save Profile/i));

  await waitFor(() => {
    const fullNameInput = screen.getByPlaceholderText('Enter your full name');
    expect(fullNameInput.className).toContain('input-error');
  });
});

// ---------------------------------------------------------------------------
// Education card validation — GPA
// ---------------------------------------------------------------------------

test('shows error when GPA is not a number', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  // Add an education entry
  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. MIT'));

  fireEvent.change(screen.getByPlaceholderText('e.g. 3.8'), { target: { value: 'abc' } });

  // Click the Save button inside the education card
  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(screen.getByText('GPA must be a number.')).toBeDefined();
  });
});

test('shows error when GPA is out of range', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. MIT'));

  fireEvent.change(screen.getByPlaceholderText('e.g. 3.8'), { target: { value: '5.0' } });

  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(screen.getByText('GPA must be between 0 and 4.33.')).toBeDefined();
  });
});

test('accepts valid GPA value', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. MIT'));

  fireEvent.change(screen.getByPlaceholderText('e.g. MIT'), { target: { value: 'MIT' } });
  fireEvent.change(screen.getByPlaceholderText('e.g. 3.8'), { target: { value: '3.8' } });

  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    // Should show the saved card view, not the editing view
    expect(screen.getByText('MIT')).toBeDefined();
    expect(screen.getByText('GPA: 3.8')).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// Education card validation — End date before start date
// ---------------------------------------------------------------------------

test('shows error when end date is before start date', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. MIT'));

  // Set start date after end date
  const dateInputs = document.querySelectorAll('input[type="month"]');
  fireEvent.change(dateInputs[0], { target: { value: '2024-06' } }); // start
  fireEvent.change(dateInputs[1], { target: { value: '2023-01' } }); // end (before start)

  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(screen.getByText('End date must be after start date.')).toBeDefined();
  });
});

test('clears end date error when start date changes', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. MIT'));

  const dateInputs = document.querySelectorAll('input[type="month"]');
  fireEvent.change(dateInputs[0], { target: { value: '2024-06' } });
  fireEvent.change(dateInputs[1], { target: { value: '2023-01' } });
  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(screen.getByText('End date must be after start date.')).toBeDefined();
  });

  fireEvent.change(dateInputs[0], { target: { value: '2022-06' } });

  await waitFor(() => {
    expect(screen.queryByText('End date must be after start date.')).toBeNull();
  });
});

test('clears education card errors on cancel', async () => {
  render(
    <BrowserRouter>
      <UserPreferencePage />
    </BrowserRouter>
  );

  await waitFor(() => screen.getByText(/Build your Profile/i));

  fireEvent.click(screen.getByText('Add your first education entry'));

  await waitFor(() => screen.getByPlaceholderText('e.g. 3.8'));

  // Trigger GPA error
  fireEvent.change(screen.getByPlaceholderText('e.g. 3.8'), { target: { value: 'bad' } });
  fireEvent.click(screen.getByText('Save'));

  await waitFor(() => {
    expect(screen.getByText('GPA must be a number.')).toBeDefined();
  });

  // Cancel should remove the card (new entry with no institution)
  fireEvent.click(screen.getByText('Cancel'));

  expect(screen.queryByText('GPA must be a number.')).toBeNull();
});
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
