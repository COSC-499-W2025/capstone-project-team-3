import { render, screen } from '@testing-library/react';
import { DataManagementPage } from '../src/pages/DataManagementPage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as chronologicalApi from '../src/api/chronological';

jest.mock('../src/api/chronological');

const mockGetChronologicalProjects = chronologicalApi.getChronologicalProjects as jest.MockedFunction<
  typeof chronologicalApi.getChronologicalProjects
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

beforeEach(() => {
  jest.clearAllMocks();
  mockGetChronologicalProjects.mockResolvedValue(mockProjects);
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
