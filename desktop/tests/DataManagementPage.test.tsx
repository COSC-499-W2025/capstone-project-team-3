import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataManagementPage } from '../src/pages/DataManagementPage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as chronologicalApi from '../src/api/chronological';
import * as projectsApi from '../src/api/projects';

jest.mock('../src/api/chronological');
jest.mock('../src/api/projects');

const mockGetChronologicalProjects = chronologicalApi.getChronologicalProjects as jest.MockedFunction<
  typeof chronologicalApi.getChronologicalProjects
>;
const mockGetProjectSkills = chronologicalApi.getProjectSkills as jest.MockedFunction<
  typeof chronologicalApi.getProjectSkills
>;
const mockUpdateProjectDates = chronologicalApi.updateProjectDates as jest.MockedFunction<
  typeof chronologicalApi.updateProjectDates
>;
const mockUpdateSkillDate = chronologicalApi.updateSkillDate as jest.MockedFunction<
  typeof chronologicalApi.updateSkillDate
>;
const mockDeleteProject = projectsApi.deleteProject as jest.MockedFunction<
  typeof projectsApi.deleteProject
>;

const mockProjects: chronologicalApi.ChronologicalProject[] = [
  {
    project_signature: 'sig-1',
    name: 'Project Alpha',
    path: '/path/alpha',
    created_at: '2026-01-15T10:30:00Z',
    last_modified: '2026-02-01T14:20:00Z',
  },
  {
    project_signature: 'sig-2',
    name: 'Project Beta',
    path: '/path/beta',
    created_at: '2025-12-20T09:15:00Z',
    last_modified: '2026-01-10T11:00:00Z',
  },
];

const mockSkills: chronologicalApi.ChronologicalSkill[] = [
  { id: 1, skill: 'Python', source: 'code', date: '2026-01-15' },
  { id: 2, skill: 'React', source: 'code', date: '2026-02-01' },
];

beforeEach(() => {
  jest.clearAllMocks();
  mockGetChronologicalProjects.mockResolvedValue(mockProjects);
  mockGetProjectSkills.mockResolvedValue(mockSkills);
  mockUpdateProjectDates.mockResolvedValue(mockProjects[0]);
  mockUpdateSkillDate.mockResolvedValue({ ...mockSkills[0], date: '2026-01-20' });
  mockDeleteProject.mockResolvedValue({
    status: 'ok',
    message: "Project 'Project Alpha' deleted successfully",
    project_signature: 'sig-1',
  });
});

test('renders data management page with title', async () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const title = await screen.findByText(/Data Management/i);
  expect(title).toBeInTheDocument();
});

test('renders description after load', async () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const description = await screen.findByText(/View and edit chronological information/i);
  expect(description).toBeInTheDocument();
});

test('title is in container', async () => {
  const { container } = render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const title = await screen.findByText(/Data Management/i);
  expect(title.parentElement?.classList.contains('data-management-container')).toBe(true);
});

test('renders loading state initially', () => {
  mockGetChronologicalProjects.mockReturnValue(new Promise(() => {}));

  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  expect(screen.getByText(/Loading projects/i)).toBeInTheDocument();
});

test('renders error state when API fails', async () => {
  mockGetChronologicalProjects.mockRejectedValue(new Error('Network error'));

  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const errorText = await screen.findByText(/Error: Network error/i);
  expect(errorText).toBeInTheDocument();
});

test('renders empty state when no projects', async () => {
  mockGetChronologicalProjects.mockResolvedValue([]);

  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const emptyText = await screen.findByText(/No projects found/i);
  expect(emptyText).toBeInTheDocument();
});

test('renders projects list with names and dates', async () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  expect(await screen.findByText('Project Alpha')).toBeInTheDocument();
  expect(await screen.findByText('Project Beta')).toBeInTheDocument();
  expect(screen.getByText('Project Name')).toBeInTheDocument();
  expect(screen.getByText('Created')).toBeInTheDocument();
  expect(screen.getByText('Last Modified')).toBeInTheDocument();
  expect(screen.getByText('15-01-2026')).toBeInTheDocument();
  expect(screen.getByText('01-02-2026')).toBeInTheDocument();
  expect(screen.getByText('20-12-2025')).toBeInTheDocument();
  expect(screen.getByText('10-01-2026')).toBeInTheDocument();
});

test('expand project shows skills', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const expandButtons = screen.getAllByRole('button', { name: /expand skills/i });
  await user.click(expandButtons[0]);

  expect(mockGetProjectSkills).toHaveBeenCalledWith('sig-1');
  expect(await screen.findByText('Skills')).toBeInTheDocument();
  expect(await screen.findByText('Python')).toBeInTheDocument();
  expect(await screen.findByText('React')).toBeInTheDocument();
});

test('shows date format error when invalid date entered', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const createdBtn = screen.getAllByText('15-01-2026')[0];
  await user.click(createdBtn);

  const input = screen.getByPlaceholderText('dd-mm-yyyy');
  await user.clear(input);
  await user.type(input, 'invalid-date');
  await user.tab();

  expect(await screen.findByText(/Invalid date format. Use dd-mm-yyyy/i)).toBeInTheDocument();
});

test('shows error when last modified is before or equal to date created', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  // Project Alpha: created 15-01-2026, last_modified 01-02-2026
  // Click Last Modified (01-02-2026) and change to 10-01-2026 (before created)
  const lastModifiedBtn = screen.getAllByText('01-02-2026')[0];
  await user.click(lastModifiedBtn);

  const input = screen.getByPlaceholderText('dd-mm-yyyy');
  await user.clear(input);
  await user.type(input, '10-01-2026');
  await user.tab();

  expect(await screen.findByText(/Last modified must be after date created/i)).toBeInTheDocument();
  expect(mockUpdateProjectDates).not.toHaveBeenCalled();
});

test('shows error when skill date is outside project date range', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const expandButtons = screen.getAllByRole('button', { name: /expand skills/i });
  await user.click(expandButtons[0]);

  await screen.findByText('Python');
  // Project Alpha: created 15-01-2026, last_modified 01-02-2026
  // Index 0 = project created, index 1 = Python skill date
  const skillDateBtns = screen.getAllByText('15-01-2026');
  await user.click(skillDateBtns[1]);

  const input = screen.getByPlaceholderText('dd-mm-yyyy');
  await user.clear(input);
  await user.type(input, '01-01-2026');
  await user.tab();

  expect(await screen.findByText(/Skill date must be within the project's date range/i)).toBeInTheDocument();
  expect(mockUpdateSkillDate).not.toHaveBeenCalled();
});

test('Refresh button fetches projects', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const refreshBtn = screen.getByRole('button', { name: /refresh/i });
  await user.click(refreshBtn);

  expect(mockGetChronologicalProjects).toHaveBeenCalledTimes(2);
});

test('each project row has a trash/delete button', async () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
  // One delete button per project
  expect(deleteButtons.length).toBeGreaterThanOrEqual(2);
});

test('clicking trash button opens first confirmation modal', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const deleteBtn = screen.getByRole('button', { name: /delete project alpha/i });
  await user.click(deleteBtn);

  expect(await screen.findByText(/Are you sure you want to delete/i)).toBeInTheDocument();
  expect(screen.getAllByText(/Project Alpha/)[0]).toBeInTheDocument();
});

test('cancel on first confirmation modal dismisses it', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  await user.click(screen.getByRole('button', { name: /delete project alpha/i }));
  await screen.findByText(/Are you sure you want to delete/i);
  await user.click(screen.getByRole('button', { name: /cancel/i }));

  expect(screen.queryByText(/Are you sure you want to delete/i)).not.toBeInTheDocument();
});

test('confirming first step advances to type-confirmation step', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  await user.click(screen.getByRole('button', { name: /delete project alpha/i }));
  await screen.findByText(/Are you sure you want to delete/i);
  await user.click(screen.getByRole('button', { name: /yes, delete/i }));

  expect(await screen.findByText(/To confirm, type/i)).toBeInTheDocument();
});

test('Delete Project button is disabled until correct text is typed', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  await user.click(screen.getByRole('button', { name: /delete project alpha/i }));
  await user.click(await screen.findByRole('button', { name: /yes, delete/i }));
  await screen.findByText(/To confirm, type/i);

  const confirmBtn = screen.getByRole('button', { name: 'Delete Project' });
  expect(confirmBtn).toBeDisabled();

  const input = screen.getByRole('textbox', { name: /type project name to confirm/i });
  // Type something wrong first — button should stay disabled
  await user.type(input, 'wrong text');
  expect(confirmBtn).toBeDisabled();

  // Clear and type the correct confirmation string — button should become enabled
  await user.clear(input);
  await user.type(input, 'project alphasig-');
  expect(confirmBtn).not.toBeDisabled();
});

test('typing correct confirmation enables and submits deletion', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  await user.click(screen.getByRole('button', { name: /delete project alpha/i }));
  await user.click(await screen.findByRole('button', { name: /yes, delete/i }));
  await screen.findByText(/To confirm, type/i);

  const input = screen.getByRole('textbox', { name: /type project name to confirm/i });
  // project name lowercase + first 4 chars of signature "sig-1" → "sig-"
  await user.type(input, 'project alphasig-');

  const confirmBtn = screen.getByRole('button', { name: 'Delete Project' });
  await user.click(confirmBtn);

  expect(mockDeleteProject).toHaveBeenCalledWith('sig-1');
  // Project Alpha is removed from the list
  await screen.findByText('Project Beta');
  expect(screen.queryByText('Project Alpha')).not.toBeInTheDocument();
});
