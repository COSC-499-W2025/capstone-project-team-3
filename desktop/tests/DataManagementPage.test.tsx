import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataManagementPage } from '../src/pages/DataManagementPage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as chronologicalApi from '../src/api/chronological';

jest.mock('../src/api/chronological');

const mockGetChronologicalProjects = chronologicalApi.getChronologicalProjects as jest.MockedFunction<
  typeof chronologicalApi.getChronologicalProjects
>;
const mockGetProjectSkills = chronologicalApi.getProjectSkills as jest.MockedFunction<
  typeof chronologicalApi.getProjectSkills
>;
const mockUpdateProjectName = chronologicalApi.updateProjectName as jest.MockedFunction<
  typeof chronologicalApi.updateProjectName
>;
const mockUpdateProjectDates = chronologicalApi.updateProjectDates as jest.MockedFunction<
  typeof chronologicalApi.updateProjectDates
>;
const mockUpdateSkillDate = chronologicalApi.updateSkillDate as jest.MockedFunction<
  typeof chronologicalApi.updateSkillDate
>;
const mockUpdateSkillName = chronologicalApi.updateSkillName as jest.MockedFunction<
  typeof chronologicalApi.updateSkillName
>;
const mockAddSkill = chronologicalApi.addSkill as jest.MockedFunction<
  typeof chronologicalApi.addSkill
>;
const mockDeleteSkill = chronologicalApi.deleteSkill as jest.MockedFunction<
  typeof chronologicalApi.deleteSkill
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
  mockUpdateProjectName.mockResolvedValue({ ...mockProjects[0], name: 'Updated Name' });
  mockUpdateProjectDates.mockResolvedValue(mockProjects[0]);
  mockUpdateSkillDate.mockResolvedValue({ ...mockSkills[0], date: '2026-01-20' });
  mockUpdateSkillName.mockResolvedValue({ ...mockSkills[0], skill: 'TypeScript' });
  mockAddSkill.mockResolvedValue({ message: 'Skill added', skill: 'Go', source: 'code', date: '2026-02-10' });
  mockDeleteSkill.mockResolvedValue(undefined);
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

test('add skill form appears when Add skill clicked', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  await screen.findByText('Project Alpha');
  const expandButtons = screen.getAllByRole('button', { name: /expand skills/i });
  await user.click(expandButtons[0]);
  await screen.findByText('Skills');

  const addSkillBtn = screen.getByRole('button', { name: /add skill/i });
  await user.click(addSkillBtn);

  expect(screen.getByPlaceholderText('Skill name')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
});

test('editing project name calls updateProjectName', async () => {
  const user = userEvent.setup();
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const projectName = await screen.findByText('Project Alpha');
  await user.click(projectName);

  const input = screen.getByDisplayValue('Project Alpha');
  await user.clear(input);
  await user.type(input, 'My Renamed Project');
  input.blur();

  await waitFor(() => {
    expect(mockUpdateProjectName).toHaveBeenCalledWith('sig-1', 'My Renamed Project');
  });
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
