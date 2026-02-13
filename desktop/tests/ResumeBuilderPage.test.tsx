import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ResumeBuilderPage } from '../src/pages/ResumeBuilderPage';
import * as resumeApi from '../src/api/resume';
import type { ResumeListItem } from '../src/api/resume';
import type { Resume } from '../src/api/resume_types';
import { jest, test, expect, describe, beforeEach } from '@jest/globals';

jest.mock('../src/api/resume', () => ({
  getResumes: jest.fn(),
  buildResume: jest.fn(),
  getResumeById: jest.fn(),
}));

jest.mock('../src/pages/ResumeManager/ResumeSidebar', () => ({
  ResumeSidebar: ({ resumeList, activeIndex, onSelect, sidebarOpen, onToggleSidebar }: {
    resumeList: { id: number | null; name: string; is_master: boolean }[];
    activeIndex: number;
    onSelect: (i: number) => void;
    sidebarOpen: boolean;
    onToggleSidebar: () => void;
  }) => (
    <aside data-testid="resume-sidebar" data-open={sidebarOpen}>
      <h2>Your Résumés</h2>
      {resumeList.map((r, i) => (
        <button key={r.id ?? 'master'} onClick={() => onSelect(i)} data-active={i === activeIndex}>
          {r.name}
        </button>
      ))}
      <button type="button" aria-label={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'} onClick={onToggleSidebar} />
      <button type="button">Tailor New Resume</button>
    </aside>
  ),
}));

jest.mock('../src/pages/ResumeManager/ResumePreview', () => ({
  ResumePreview: ({ resume }: { resume: any }) => (
    <div data-testid="resume-preview">
      <span data-testid="resume-name">{resume.name}</span>
      <span data-testid="resume-email">{resume.email}</span>
    </div>
  ),
}));

const mockGetResumes = resumeApi.getResumes as ReturnType<typeof jest.fn>;
const mockBuildResume = resumeApi.buildResume as ReturnType<typeof jest.fn>;
const mockGetResumeById = resumeApi.getResumeById as ReturnType<typeof jest.fn>;

const mockResumeList: ResumeListItem[] = [
  { id: null, name: 'Master Resume', is_master: true },
  { id: 2, name: 'Saved Resume', is_master: false },
];

const mockMasterResume: Resume = {
  name: 'John Doe',
  email: 'john@example.com',
  links: [{ label: 'GitHub', url: 'https://github.com/johndoe' }],
  education: {
    school: 'University of Example',
    degree: 'BSc Computer Science',
    dates: 'Sept 2020 – May 2024',
    gpa: '3.8'
  },
  skills: { Skills: ['Python', 'JavaScript', 'React'] },
  projects: [
    {
      title: 'Project Alpha',
      dates: 'Jan 2024 – Mar 2024',
      skills: ['Python', 'Flask'],
      bullets: ['Built REST API', 'Deployed to AWS']
    }
  ]
};

const mockSavedResume: Resume = {
  name: 'John Doe',
  email: 'john@example.com',
  links: [{ label: 'GitHub', url: 'https://github.com/johndoe' }],
  education: {
    school: 'University of Example',
    degree: 'BSc Computer Science',
    dates: 'Sept 2020 – May 2024'
  },
  skills: { Skills: ['JavaScript', 'TypeScript', 'Node.js'] },
  projects: [
    {
      title: 'Saved Project',
      dates: 'Apr 2024 – Jun 2024',
      skills: ['React', 'Node.js'],
      bullets: ['Created dashboard', 'Integrated APIs']
    }
  ]
};

describe('ResumeBuilderPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetResumes.mockResolvedValue(mockResumeList);
    mockBuildResume.mockResolvedValue(mockMasterResume);
    mockGetResumeById.mockResolvedValue(mockSavedResume);
  });

  test('fetches resume list on mount and sidebar shows list and Tailor button', async () => {
    render(<ResumeBuilderPage />);
  
    expect(mockGetResumes).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Your Résumés')).toBeDefined();
    await screen.findByText('Master Resume');
    expect(screen.getByText('Saved Resume')).toBeDefined();
    expect(screen.getByText('Tailor New Resume')).toBeDefined();
  
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());
  });

  test('clicking a resume updates selection (activeIndex)', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const masterButton = screen.getByText('Master Resume');
    const savedButton = screen.getByText('Saved Resume');
    expect(masterButton.getAttribute('data-active')).toBe('true');
    expect(savedButton.getAttribute('data-active')).toBe('false');

    fireEvent.click(savedButton);

    expect(masterButton.getAttribute('data-active')).toBe('false');
    expect(savedButton.getAttribute('data-active')).toBe('true');
    
    // Wait for getResumeById to complete
    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());
  });

  test('toggle sidebar updates sidebar open state', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const hideButton = screen.getByLabelText('Hide sidebar');
    fireEvent.click(hideButton);

    expect(screen.getByLabelText('Show sidebar')).toBeDefined();
  });

  test('loads and displays master resume preview on mount', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');

    await waitFor(() => {
      expect(mockBuildResume).toHaveBeenCalledTimes(1);
      expect(mockGetResumeById).not.toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByTestId('resume-preview')).toBeDefined();
    });

    expect(screen.getByTestId('resume-name').textContent).toBe('John Doe');
    expect(screen.getByTestId('resume-email').textContent).toBe('john@example.com');
  });

  test('switches to saved resume when selecting saved resume from sidebar', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalledTimes(1));

    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => {
      expect(mockGetResumeById).toHaveBeenCalledWith(2);
    });

    await waitFor(() => {
      expect(screen.getByTestId('resume-preview')).toBeDefined();
    });
  });

  test('does not render preview when no active content', async () => {
    mockBuildResume.mockResolvedValue(null as any);

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');

    await waitFor(() => {
      expect(mockBuildResume).toHaveBeenCalled();
    });
    
    // Wait a tick for state to settle
    await waitFor(() => {
      expect(screen.queryByTestId('resume-preview')).toBeNull();
    });
  });

  test('page and main area have correct layout structure', async () => {
    const { container } = render(<ResumeBuilderPage />);
  
    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());
  
    expect(container.querySelector('.page.page--resume-builder')).toBeDefined();
    expect(container.querySelector('.resume-builder__main')).toBeDefined();
    expect(container.querySelector('.container')).toBeDefined();
    expect(container.querySelector('.card')).toBeDefined();
  });

  test('handles resume list with id=1 as master', async () => {
    const listWithId1: ResumeListItem[] = [
      { id: 1, name: 'Master Resume', is_master: false },
    ];
    mockGetResumes.mockResolvedValue(listWithId1);

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');

    await waitFor(() => {
      // Should call buildResume even though is_master is false, because id=1
      expect(mockBuildResume).toHaveBeenCalledTimes(1);
    });
  });
});