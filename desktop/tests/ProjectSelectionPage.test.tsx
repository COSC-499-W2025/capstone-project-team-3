import { render, screen, fireEvent } from '@testing-library/react';
import { test, jest, beforeEach, describe } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import ProjectSelectionPage from '../src/pages/ProjectSelectionPage';
import * as projectsApi from '../src/api/projects';

// Mock the projects API
jest.mock('../src/api/projects');

const mockGetProjects = projectsApi.getProjects as jest.MockedFunction<typeof projectsApi.getProjects>;

const mockProjects: projectsApi.Project[] = [
  {
    id: '1',
    name: 'Project Alpha',
    score: 85,
    skills: ['React', 'TypeScript', 'Node.js'],
    date_added: '2026-01-15T10:30:00Z',
  },
  {
    id: '2',
    name: 'Project Beta',
    score: 92,
    skills: ['Python', 'Django', 'PostgreSQL', 'Docker'],
    date_added: '2026-02-01T14:20:00Z',
  },
  {
    id: '3',
    name: 'Project Gamma',
    score: 78,
    skills: ['Java', 'Spring Boot'],
    date_added: '2025-12-20T09:15:00Z',
  },
];

describe('ProjectSelectionPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    console.log = jest.fn(); // Mock console.log
    mockGetProjects.mockImplementation(() => Promise.resolve(mockProjects));
  });

  test('renders loading state initially', () => {
    mockGetProjects.mockReturnValue(new Promise(() => {})); // Never resolves

    render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Loading projects.../i)).toBeInTheDocument();
  });

  test('renders error state when API call fails', async () => {
    mockGetProjects.mockRejectedValue(new Error('Network error'));

    render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    const errorText = await screen.findByText(/Error: Network error/i);
    expect(errorText).toBeInTheDocument();
  });

  test('renders page content after loading: title, headers, projects with skills and dates', async () => {
    render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for page to load by finding the title
    const title = await screen.findByText(/Select Projects for Resume/i);
    expect(title).toBeInTheDocument();

    // Page shell
    expect(screen.getByText(/Choose which projects should contribute to your resume/i)).toBeInTheDocument();
    expect(screen.getByText('Project Name')).toBeInTheDocument();
    expect(screen.getByText('Skills')).toBeInTheDocument();
    expect(screen.getByText('Date Added')).toBeInTheDocument();

    // Project names
    expect(screen.getByText('Project Alpha')).toBeInTheDocument();
    expect(screen.getByText('Project Beta')).toBeInTheDocument();
    expect(screen.getByText('Project Gamma')).toBeInTheDocument();

    // Skills (Project Beta has 4 skills, should show only first 3 + ellipsis)
    expect(screen.getByText(/React, TypeScript, Node.js/i)).toBeInTheDocument();
    expect(screen.getByText(/Python, Django, PostgreSQL, \.\.\./i)).toBeInTheDocument();
    expect(screen.getByText(/Java, Spring Boot/i)).toBeInTheDocument();

    // Dates
    expect(screen.getByText('15-01-2026')).toBeInTheDocument();
    expect(screen.getByText('01-02-2026')).toBeInTheDocument();
    expect(screen.getByText('20-12-2025')).toBeInTheDocument();
  });

  test('renders 3 checkboxes, all initially unchecked', async () => {
    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for content to load
    await screen.findByText('Project Alpha');

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    expect(checkboxes.length).toBe(3);
    checkboxes.forEach((checkbox) => {
      expect(checkbox).not.toBeChecked();
    });
  });

  test('toggling project selection updates checkbox state and button enabled state', async () => {
    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for content to load
    await screen.findByText('Project Alpha');

    const button = screen.getByText('Generate Resume');
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    const firstCheckbox = checkboxes[0] as HTMLInputElement;

    // Initially: checkbox unchecked, button disabled
    expect(firstCheckbox).not.toBeChecked();
    expect(button).toBeDisabled();

    // After checking: checkbox checked, button enabled
    fireEvent.click(firstCheckbox);
    expect(firstCheckbox).toBeChecked();
    expect(button).not.toBeDisabled();

    // After unchecking: checkbox unchecked, button disabled
    fireEvent.click(firstCheckbox);
    expect(firstCheckbox).not.toBeChecked();
    expect(button).toBeDisabled();
  });

  test('can select multiple projects', async () => {
    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for content to load
    await screen.findByText('Project Alpha');

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[1]);

    expect(checkboxes[0]).toBeChecked();
    expect(checkboxes[1]).toBeChecked();
    expect(checkboxes[2]).not.toBeChecked();
  });

  test('generate resume button logs selected project IDs', async () => {
    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for content to load
    await screen.findByText('Project Alpha');

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[2]);

    const button = screen.getByText('Generate Resume');
    fireEvent.click(button);

    expect(console.log).toHaveBeenCalledWith(
      'Generating resume with projects:',
      expect.arrayContaining(['1', '3'])
    );
  });

  test('when no projects: shows empty message and table with headers', async () => {
    mockGetProjects.mockResolvedValue([]);

    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for empty message to appear
    const emptyMessage = await screen.findByText(/No projects found. Add some projects to get started!/i);
    expect(emptyMessage).toBeInTheDocument();

    // Table and headers still present
    const table = container.querySelector('.projects-table');
    expect(table).toBeInTheDocument();
    expect(screen.getByText('Project Name')).toBeInTheDocument();
    expect(screen.getByText('Skills')).toBeInTheDocument();
    expect(screen.getByText('Date Added')).toBeInTheDocument();
  });

  test('renders with correct layout: CSS classes and 3 project rows', async () => {
    const { container } = render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for content to load
    await screen.findByText('Project Alpha');

    // CSS classes
    expect(container.querySelector('.project-selection-container')).toBeInTheDocument();
    expect(container.querySelector('.page-title')).toBeInTheDocument();
    expect(container.querySelector('.page-subtitle')).toBeInTheDocument();
    expect(container.querySelector('.table-container')).toBeInTheDocument();
    expect(container.querySelector('.projects-table')).toBeInTheDocument();
    expect(container.querySelector('.button-container')).toBeInTheDocument();
    expect(container.querySelector('.generate-button')).toBeInTheDocument();

    // Project rows
    const rows = container.querySelectorAll('.project-row');
    expect(rows.length).toBe(3);
  });

  test('handles single project with many skills', async () => {
    const projectWithManySkills: projectsApi.Project[] = [{
      id: '1',
      name: 'Multi-skill Project',
      score: 90,
      skills: ['React', 'TypeScript', 'Node.js', 'Express', 'MongoDB'],
      date_added: '2026-01-01T00:00:00Z',
    }];

    mockGetProjects.mockResolvedValue(projectWithManySkills);

    render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for project name to appear
    await screen.findByText('Multi-skill Project');

    // Should show only first 3 skills + ellipsis (not Express or MongoDB)
    expect(screen.getByText(/React, TypeScript, Node\.js, \.\.\./i)).toBeInTheDocument();
    expect(screen.queryByText(/Express/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/MongoDB/i)).not.toBeInTheDocument();
  });

  test('project with exactly 3 skills shows no ellipsis', async () => {
    const projectWithThreeSkills: projectsApi.Project[] = [{
      id: '1',
      name: 'Three Skill Project',
      score: 85,
      skills: ['React', 'TypeScript', 'Node.js'],
      date_added: '2026-01-01T00:00:00Z',
    }];

    mockGetProjects.mockResolvedValue(projectWithThreeSkills);

    render(
      <BrowserRouter>
        <ProjectSelectionPage />
      </BrowserRouter>
    );

    // Wait for project name to appear
    await screen.findByText('Three Skill Project');

    // Should show all 3 skills without ellipsis
    const skillsCell = screen.getByText(/React, TypeScript, Node\.js/i);
    expect(skillsCell).toBeInTheDocument();
    expect(skillsCell.textContent).toBe('React, TypeScript, Node.js');
    expect(skillsCell.textContent).not.toContain('...');
  });


});
