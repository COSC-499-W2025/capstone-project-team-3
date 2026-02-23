import { render, screen } from '@testing-library/react';
import { ResumePreview } from '../src/pages/ResumeManager/ResumePreview';
import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import '@testing-library/jest-dom';
import type { Resume } from '../src/api/resume_types';

// Mock CSS import
jest.mock('../src/styles/ResumePreview.css', () => ({}));

describe('ResumePreview', () => {
  const mockResume: Resume = {
    name: 'John Doe',
    email: 'john@example.com',
    links: [
      { label: 'GitHub', url: 'https://github.com/johndoe' }
    ],
    education: [{
      school: 'University of Example',
      degree: 'Bachelor of Science in Computer Science',
      dates: 'Sept 2020 – May 2024',
      gpa: '3.8'
    }],
    skills: {
      Skills: ['Python', 'JavaScript', 'React', 'Node.js', 'SQL']
    },
    projects: [
      {
        title: 'E-commerce Website',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['React', 'Node.js', 'MongoDB'],
        bullets: [
          'Built full-stack web application',
          'Implemented payment processing',
          'Deployed to AWS'
        ]
      },
      {
        title: 'Data Analytics Dashboard',
        dates: 'Apr 2024 – Jun 2024',
        skills: ['Python', 'Pandas', 'Matplotlib'],
        bullets: [
          'Created data visualization tool',
          'Processed large datasets'
        ]
      }
    ]
  };

  beforeEach(() => {
    // Mock offsetHeight for layout calculations
    Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
      configurable: true,
      value: 100,
    });
  });

  test('renders resume preview with all sections', () => {
    render(<ResumePreview resume={mockResume} />);

    // Check header section
    expect(screen.getAllByText('John Doe').length).toBeGreaterThan(0);
    expect(screen.getAllByText('john@example.com').length).toBeGreaterThan(0);

    // Check education section
    expect(screen.getAllByText('Education').length).toBeGreaterThan(0);
    expect(screen.getAllByText('University of Example').length).toBeGreaterThan(0);

    // Check skills section
    expect(screen.getAllByText('Skills').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Python').length).toBeGreaterThan(0);

    // Check projects section
    expect(screen.getAllByText('E-commerce Website').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Data Analytics Dashboard').length).toBeGreaterThan(0);
  });

  test('renders minimal resume', () => {
    const minimalResume: Resume = {
      name: 'Test User',
      email: 'test@example.com',
      links: [],
      education: [{
        school: 'Test School',
        degree: 'Test Degree'
      }],
      skills: {
        Skills: ['Python']
      },
      projects: []
    };

    render(<ResumePreview resume={minimalResume} />);

    expect(screen.getAllByText('Test User').length).toBeGreaterThan(0);
    expect(screen.getAllByText('test@example.com').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Test School').length).toBeGreaterThan(0);
  });

  test('renders resume with no projects', () => {
    const noProjectsResume: Resume = {
      ...mockResume,
      projects: []
    };

    render(<ResumePreview resume={noProjectsResume} />);

    expect(screen.getAllByText('John Doe').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Education').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Skills').length).toBeGreaterThan(0);
  });

  test('renders resume with single project', () => {
    const singleProjectResume: Resume = {
      ...mockResume,
      projects: [mockResume.projects[0]]
    };

    render(<ResumePreview resume={singleProjectResume} />);

    expect(screen.getAllByText('E-commerce Website').length).toBeGreaterThan(0);
    expect(screen.queryAllByText('Data Analytics Dashboard').length).toBe(0);
  });

  test('renders with empty skills array', () => {
    const emptySkillsResume: Resume = {
      ...mockResume,
      skills: { Skills: [] }
    };

    render(<ResumePreview resume={emptySkillsResume} />);

    expect(screen.getAllByText('John Doe').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Skills').length).toBeGreaterThan(0);
  });

  test('renders with undefined projects array', () => {
    const noProjectsResume = {
      ...mockResume,
      projects: undefined as any
    };

    render(<ResumePreview resume={noProjectsResume} />);

    expect(screen.getAllByText('John Doe').length).toBeGreaterThan(0);
    // Should handle undefined projects gracefully
  });

  test('header appears only on first page', () => {
    const { container } = render(<ResumePreview resume={mockResume} />);

    // In the measure container, header should appear once
    const measureContainer = container.querySelector('.resume-preview__measure');
    const headerInMeasure = measureContainer?.querySelectorAll('.resume-preview__header');
    expect(headerInMeasure?.length).toBe(1);
  });

  test('renders links in header', () => {
    render(<ResumePreview resume={mockResume} />);

    expect(screen.getAllByText('GitHub').length).toBeGreaterThan(0);
  });

  test('handles projects with different bullet counts', () => {
    const resume: Resume = {
      ...mockResume,
      projects: [
        {
          title: 'Project 1',
          dates: 'Jan 2024',
          skills: ['Python'],
          bullets: ['Bullet 1']
        },
        {
          title: 'Project 2',
          dates: 'Feb 2024',
          skills: ['JavaScript'],
          bullets: ['Bullet A', 'Bullet B', 'Bullet C', 'Bullet D']
        }
      ]
    };

    render(<ResumePreview resume={resume} />);

    expect(screen.getAllByText('Bullet 1').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bullet A').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bullet D').length).toBeGreaterThan(0);
  });

  test('renders with very long project list', () => {
    const manyProjects = Array.from({ length: 10 }, (_, i) => ({
      title: `Project ${i + 1}`,
      dates: `Jan 202${i}`,
      skills: ['Python', 'JavaScript'],
      bullets: ['Did something', 'Did something else']
    }));

    const longResume: Resume = {
      ...mockResume,
      projects: manyProjects
    };

    render(<ResumePreview resume={longResume} />);

    expect(screen.getAllByText('Project 1').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Project 10').length).toBeGreaterThan(0);
  });

  test('renders in edit mode with projects and onSectionChange without crashing', () => {
    const resumeWithId: Resume = {
      ...mockResume,
      projects: [
        {
          ...mockResume.projects[0],
          project_id: 'sig-123',
          title: 'E-commerce Website',
          dates: 'Jan 2024 – Mar 2024',
          skills: ['React', 'Node.js'],
          bullets: ['Built app']
        }
      ]
    };
    const onSectionChange = jest.fn();

    render(
      <ResumePreview
        resume={resumeWithId}
        isEditing={true}
        onSectionChange={onSectionChange}
      />
    );

    expect(screen.getAllByText('E-commerce Website').length).toBeGreaterThan(0);
  });
});
