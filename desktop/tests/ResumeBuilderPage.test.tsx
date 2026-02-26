import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ResumeBuilderPage } from '../src/pages/ResumeBuilderPage';
import * as resumeApi from '../src/api/resume';
import type { ResumeListItem } from '../src/api/resume';
import type { Resume } from '../src/api/resume_types';
import { jest, test, describe, beforeEach } from '@jest/globals';

const mockNavigate = jest.fn();
const mockSearchParams = new URLSearchParams();
const mockSetSearchParams = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useSearchParams: () => [mockSearchParams, mockSetSearchParams],
}));

jest.mock('../src/api/resume', () => ({
  getResumes: jest.fn(),
  buildResume: jest.fn(),
  getResumeById: jest.fn(),
  previewResume: jest.fn(),
  deleteResume: jest.fn(),
  deleteProjectFromResume: jest.fn(),
  downloadResumePDF: jest.fn(),
  downloadResumeTeX: jest.fn(),
  saveNewResume: jest.fn(),
  updateResume: jest.fn(),
}));

jest.mock('../src/pages/ResumeManager/ResumeSidebar', () => ({
  ResumeSidebar: ({ resumeList, activeIndex, onSelect, onTailorNew, onDelete, onEdit, sidebarOpen, onToggleSidebar }: {
    resumeList: { id: number | null; name: string; is_master: boolean }[];
    activeIndex: number;
    onSelect: (i: number) => void;
    onTailorNew?: () => void;
    onDelete?: (id: number) => void;
    onEdit?: () => void;
    sidebarOpen: boolean;
    onToggleSidebar: () => void;
  }) => (
    <aside data-testid="resume-sidebar" data-open={sidebarOpen}>
      <h2>Your Résumés</h2>
      {resumeList.map((r, i) => (
        <div key={i}>
          <button onClick={() => onSelect(i)} data-active={i === activeIndex}>
            {r.name}
          </button>
          {!r.is_master && r.id != null && i === activeIndex && onEdit && (
            <button type="button" aria-label="Edit resume" data-testid={`edit-resume-${r.id}`} onClick={() => onEdit()}>
              Edit
            </button>
          )}
          {r.id !== null && r.id !== 1 && onDelete && (
            <button 
              data-testid={`delete-resume-${r.id}`}
              onClick={() => {
                if (window.confirm(`Are you sure you want to delete "${r.name || 'this resume'}"?`)) {
                  onDelete(r.id);
                }
              }}
            >
              Delete
            </button>
          )}
        </div>
      ))}
      <button type="button" aria-label={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'} onClick={onToggleSidebar} />
      <button type="button" onClick={onTailorNew}>Tailor New Resume</button>
    </aside>
  ),
}));

jest.mock('../src/pages/ResumeManager/ResumePreview', () => ({
  ResumePreview: ({ resume, isEditing, onProjectDelete }: { resume: any; isEditing?: boolean; onProjectDelete?: (id: string) => void }) => {
    const firstProjectWithId = resume?.projects?.find((p: any) => p.project_id);
    return (
      <div data-testid="resume-preview">
        <span data-testid="resume-name">{resume.name}</span>
        <span data-testid="resume-email">{resume.email}</span>
        {isEditing && onProjectDelete && firstProjectWithId && (
          <button
            type="button"
            aria-label="Remove project from resume"
            data-testid="remove-project-from-resume"
            onClick={() => {
              if (window.confirm('Remove this project from the resume?')) {
                onProjectDelete(firstProjectWithId.project_id);
              }
            }}
          >
            Remove project
          </button>
        )}
      </div>
    );
  },
}));

const mockGetResumes = resumeApi.getResumes as ReturnType<typeof jest.fn>;
const mockBuildResume = resumeApi.buildResume as ReturnType<typeof jest.fn>;
const mockGetResumeById = resumeApi.getResumeById as ReturnType<typeof jest.fn>;
const mockPreviewResume = resumeApi.previewResume as ReturnType<typeof jest.fn>;
const mockDeleteResume = resumeApi.deleteResume as ReturnType<typeof jest.fn>;
const mockDeleteProjectFromResume = resumeApi.deleteProjectFromResume as ReturnType<typeof jest.fn>;
const mockDownloadResumePDF = resumeApi.downloadResumePDF as ReturnType<typeof jest.fn>;
const mockDownloadResumeTeX = resumeApi.downloadResumeTeX as ReturnType<typeof jest.fn>;
const mockSaveNewResume = resumeApi.saveNewResume as ReturnType<typeof jest.fn>;
const mockUpdateResume = resumeApi.updateResume as ReturnType<typeof jest.fn>;

const mockResumeList: ResumeListItem[] = [
  { id: null, name: 'Master Resume', is_master: true },
  { id: 2, name: 'Saved Resume', is_master: false },
];

const mockMasterResume: Resume = {
  name: 'John Doe',
  email: 'john@example.com',
  links: [{ label: 'GitHub', url: 'https://github.com/johndoe' }],
  education: [{
    school: 'University of Example',
    degree: 'BSc Computer Science',
    dates: 'Sept 2020 – May 2024',
    gpa: '3.8'
  }],
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
  education: [{
    school: 'University of Example',
    degree: 'BSc Computer Science',
    dates: 'Sept 2020 – May 2024'
  }],
  skills: { Skills: ['JavaScript', 'TypeScript', 'Node.js'] },
  projects: [
    {
      project_id: 'proj-saved-1',
      title: 'Saved Project',
      dates: 'Apr 2024 – Jun 2024',
      skills: ['React', 'Node.js'],
      bullets: ['Created dashboard', 'Integrated APIs']
    }
  ]
};

const mockPreviewResumeData: Resume = {
  name: 'John Doe',
  email: 'john@example.com',
  links: [{ label: 'GitHub', url: 'https://github.com/johndoe' }],
  education: [{
    school: 'University of Example',
    degree: 'BSc Computer Science',
    dates: 'Sept 2020 – May 2024'
  }],
  skills: { Skills: ['Python', 'Django', 'PostgreSQL'] },
  projects: [
    {
      title: 'Preview Project',
      dates: 'Jul 2024 – Sep 2024',
      skills: ['Python', 'Django'],
      bullets: ['Preview bullet 1', 'Preview bullet 2']
    }
  ]
};

describe('ResumeBuilderPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
    mockSearchParams.delete('project_ids');
    mockGetResumes.mockResolvedValue(mockResumeList);
    mockBuildResume.mockResolvedValue(mockMasterResume);
    mockGetResumeById.mockResolvedValue(mockSavedResume);
    mockPreviewResume.mockResolvedValue(mockPreviewResumeData);
    mockDownloadResumePDF.mockResolvedValue(undefined);
    mockDownloadResumeTeX.mockResolvedValue(undefined);
    mockSaveNewResume.mockResolvedValue({ id: 3 });
    mockUpdateResume.mockResolvedValue(undefined);
    mockDeleteProjectFromResume.mockResolvedValue({ success: true, message: 'Project removed' });
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

  test('clicking Tailor New Resume navigates to project selection page', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const tailorButton = screen.getByText('Tailor New Resume');
    fireEvent.click(tailorButton);

    expect(mockNavigate).toHaveBeenCalledWith('/projectselectionpage');
  });

  test('enters preview mode when project_ids are in URL', async () => {
    mockSearchParams.append('project_ids', 'proj1');
    mockSearchParams.append('project_ids', 'proj2');

    render(<ResumeBuilderPage />);

    await waitFor(() => {
      expect(mockPreviewResume).toHaveBeenCalledWith(['proj1', 'proj2']);
    });

    await screen.findByText('Preview Resume (Unsaved)');
    expect(screen.getByText('Master Resume')).toBeDefined();
    expect(screen.getByText('Saved Resume')).toBeDefined();
  });

  test('preview resume is injected at position 0, active, and displays correct content', async () => {
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');

    // Check position and active state
    const sidebar = screen.getByTestId('resume-sidebar');
    const buttons = sidebar.querySelectorAll('button');
    const resumeButtons = Array.from(buttons).filter(btn => 
      btn.textContent && !btn.textContent.includes('sidebar') && !btn.textContent.includes('Tailor')
    );

    expect(resumeButtons[0].textContent).toBe('Preview Resume (Unsaved)');
    expect(resumeButtons[0].getAttribute('data-active')).toBe('true');

    // Check content displays correctly
    await waitFor(() => {
      expect(screen.getByTestId('resume-preview')).toBeDefined();
    });

    expect(screen.getByTestId('resume-name').textContent).toBe('John Doe');
    expect(screen.getByTestId('resume-email').textContent).toBe('john@example.com');
  });

  test('clicking preview resume in preview mode does nothing', async () => {
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');

    const previewButton = screen.getByText('Preview Resume (Unsaved)');
    expect(previewButton.getAttribute('data-active')).toBe('true');

    fireEvent.click(previewButton);

    // Should still be active and no navigation
    expect(previewButton.getAttribute('data-active')).toBe('true');
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('clicking saved resume in preview mode exits preview and loads saved resume', async () => {
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    // Should navigate to clear URL params
    expect(mockNavigate).toHaveBeenCalledWith('/resumebuilderpage', { replace: true });

    // Should load the saved resume
    await waitFor(() => {
      expect(mockGetResumeById).toHaveBeenCalledWith(2);
    });
  });

  test('does not load saved resumes when in preview mode', async () => {
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');

    await waitFor(() => {
      expect(mockPreviewResume).toHaveBeenCalled();
    });

    // Should not call buildResume or getResumeById in preview mode
    expect(mockBuildResume).not.toHaveBeenCalled();
    expect(mockGetResumeById).not.toHaveBeenCalled();
  });

  test('deleting a resume calls deleteResume API and refreshes the list', async () => {
    const updatedList: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
    ];

    mockDeleteResume.mockResolvedValue({ success: true, message: 'Resume deleted' });
    window.confirm = jest.fn(() => true);

    render(<ResumeBuilderPage />);

    await screen.findByText('Saved Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Setup mock to return updated list on second call
    mockGetResumes.mockResolvedValueOnce(updatedList);

    // Click delete on resume with id=2
    const deleteButton = screen.getByTestId('delete-resume-2');
    fireEvent.click(deleteButton);

    // Verify confirmation was shown
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete "Saved Resume"?');

    // Wait for deleteResume to be called
    await waitFor(() => {
      expect(mockDeleteResume).toHaveBeenCalledWith(2);
    });

    // Wait for resume list to be refreshed
    await waitFor(() => {
      expect(mockGetResumes).toHaveBeenCalledTimes(2);
    });
  });

  test('deleting a resume does not call API when user cancels confirmation', async () => {
    window.confirm = jest.fn(() => false);

    render(<ResumeBuilderPage />);

    await screen.findByText('Saved Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const deleteButton = screen.getByTestId('delete-resume-2');
    fireEvent.click(deleteButton);

    // Verify confirmation was shown
    expect(window.confirm).toHaveBeenCalled();

    // Verify deleteResume was NOT called
    expect(mockDeleteResume).not.toHaveBeenCalled();
  });

  test('deleting a resume handles API errors gracefully', async () => {
    mockDeleteResume.mockRejectedValue(new Error('Failed to delete'));
    window.confirm = jest.fn(() => true);
    window.alert = jest.fn();
    const consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});

    render(<ResumeBuilderPage />);

    await screen.findByText('Saved Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const deleteButton = screen.getByTestId('delete-resume-2');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockDeleteResume).toHaveBeenCalledWith(2);
    });

    // Verify error alert was shown
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to delete resume. Please try again.');
    });

    consoleErrorMock.mockRestore();
  });

  test('removing a project from resume calls deleteProjectFromResume and refreshes content', async () => {
    window.confirm = jest.fn(() => true);

    render(<ResumeBuilderPage />);

    await screen.findByText('Saved Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalledWith(2));

    const editButton = screen.getByTestId('edit-resume-2');
    fireEvent.click(editButton);

    const removeProjectButton = screen.getByTestId('remove-project-from-resume');
    fireEvent.click(removeProjectButton);

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalledWith('Remove this project from the resume?');
      expect(mockDeleteProjectFromResume).toHaveBeenCalledWith(2, 'proj-saved-1');
    });

    await waitFor(() => {
      expect(mockGetResumeById).toHaveBeenCalledTimes(2);
      expect(mockGetResumeById).toHaveBeenLastCalledWith(2);
    });
  });

  test('deleting the active resume switches to first available resume', async () => {
    const updatedList: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
    ];

    mockDeleteResume.mockResolvedValue({ success: true, message: 'Resume deleted' });
    window.confirm = jest.fn(() => true);

  });

  // Download functionality tests
  test('download button renders and shows dropdown menu on click', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    expect(screen.getByText('Download as PDF')).toBeDefined();
    expect(screen.getByText('Download as TeX')).toBeDefined();
  });

  test('downloads PDF for master resume with correct params', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click PDF option
    const pdfOption = screen.getByText('Download as PDF');
    fireEvent.click(pdfOption);

    await waitFor(() => {
      expect(mockDownloadResumePDF).toHaveBeenCalledWith({
        filename: 'Master Resume'
      });
    });
  });

  test('downloads PDF for saved resume with resume ID', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Switch to saved resume
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click PDF option
    const pdfOption = screen.getByText('Download as PDF');
    fireEvent.click(pdfOption);

    await waitFor(() => {
      expect(mockDownloadResumePDF).toHaveBeenCalledWith({
        resumeId: 2,
        filename: 'Saved Resume'
      });
    });
  });

  test('downloads PDF in preview mode with project IDs', async () => {
    mockSearchParams.append('project_ids', 'proj1');
    mockSearchParams.append('project_ids', 'proj2');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click PDF option
    const pdfOption = screen.getByText('Download as PDF');
    fireEvent.click(pdfOption);

    await waitFor(() => {
      expect(mockDownloadResumePDF).toHaveBeenCalledWith({
        projectIds: ['proj1', 'proj2'],
        filename: 'Preview Resume (Unsaved)'
      });
    });
  });

  test('downloads TeX for master resume with correct params', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click TeX option
    const texOption = screen.getByText('Download as TeX');
    fireEvent.click(texOption);

    await waitFor(() => {
      expect(mockDownloadResumeTeX).toHaveBeenCalledWith({
        filename: 'Master Resume'
      });
    });
  });

  test('downloads TeX for saved resume with resume ID', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Switch to saved resume
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click TeX option
    const texOption = screen.getByText('Download as TeX');
    fireEvent.click(texOption);

    await waitFor(() => {
      expect(mockDownloadResumeTeX).toHaveBeenCalledWith({
        resumeId: 2,
        filename: 'Saved Resume'
      });
    });
  });

  test('downloads TeX in preview mode with project IDs', async () => {
    mockSearchParams.append('project_ids', 'proj1');
    mockSearchParams.append('project_ids', 'proj2');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click TeX option
    const texOption = screen.getByText('Download as TeX');
    fireEvent.click(texOption);

    await waitFor(() => {
      expect(mockDownloadResumeTeX).toHaveBeenCalledWith({
        projectIds: ['proj1', 'proj2'],
        filename: 'Preview Resume (Unsaved)'
      });
    });
  });

  test('closes dropdown menu after selecting download option', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Select the saved resume (index 1)
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => {
      expect(mockGetResumeById).toHaveBeenCalledWith(2);
    });

    // Setup mock to return updated list after deletion
    const updatedList: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
    ];
    mockGetResumes.mockResolvedValueOnce(updatedList);

    // Delete the active saved resume
    const deleteButton = screen.getByTestId('delete-resume-2');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockDeleteResume).toHaveBeenCalledWith(2);
    });

    // Wait for list refresh
    await waitFor(() => {
      expect(mockGetResumes).toHaveBeenCalledTimes(2);
    });
  });

  test('delete button appears for saved resumes but not for master', async () => {
    const listWithMultiple: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
      { id: 2, name: 'Saved Resume 1', is_master: false },
      { id: 3, name: 'Saved Resume 2', is_master: false },
    ];
    mockGetResumes.mockResolvedValue(listWithMultiple);

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Should have delete buttons for id=2 and id=3, but not for master
    expect(screen.getByTestId('delete-resume-2')).toBeDefined();
    expect(screen.getByTestId('delete-resume-3')).toBeDefined();
    expect(screen.queryByTestId('delete-resume-null')).toBeNull();
  });

  test('closes dropdown menu when clicking outside', async () => {
    const { container } = render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    expect(screen.getByText('Download as PDF')).toBeDefined();

    // Click outside the dropdown
    fireEvent.mouseDown(container);

    await waitFor(() => {
      expect(screen.queryByText('Download as PDF')).toBeNull();
    });
  });

  test('disables download button and shows "Downloading..." during download', async () => {
    // Make download promise hang so we can check the state during download
    let resolveDownload: () => void;
    const downloadPromise = new Promise<void>((resolve) => {
      resolveDownload = resolve;
    });
    mockDownloadResumePDF.mockReturnValue(downloadPromise);

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click PDF option
    const pdfOption = screen.getByText('Download as PDF');
    fireEvent.click(pdfOption);

    // Button should show "Downloading..." and be disabled
    await waitFor(() => {
      const button = screen.getByText('Downloading...');
      expect(button).toBeDefined();
      expect(button.hasAttribute('disabled')).toBe(true);
    });

    // Resolve the download
    resolveDownload!();

    // Button should return to normal
    await waitFor(() => {
      expect(screen.getByText('Download')).toBeDefined();
    });
  });

  test('handles download error gracefully and shows alert', async () => {
    mockDownloadResumePDF.mockRejectedValue(new Error('Network error'));
    
    // Mock console.error to suppress expected error output
    const consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // Mock window.alert
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Open dropdown
    const downloadButton = screen.getByText('Download');
    fireEvent.click(downloadButton);

    // Click PDF option
    const pdfOption = screen.getByText('Download as PDF');
    fireEvent.click(pdfOption);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith('Failed to download resume. Please try again.');
    });

    // Button should be enabled again
    const finalButton = screen.getByText('Download');
    expect(finalButton.hasAttribute('disabled')).toBe(false);

    consoleErrorMock.mockRestore();
    alertMock.mockRestore();
  });

  // Save functionality tests  
  test('clicking save in modal saves new resume and exits preview mode', async () => {
    mockSearchParams.append('project_ids', 'proj1');
    mockSearchParams.append('project_ids', 'proj2');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    // Open modal
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Save Résumé version as:')).toBeDefined();
    });

    // Change name
    const input = screen.getByPlaceholderText('Enter resume name...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Frontend Resume' } });

    // Click save in modal - find by class to ensure we get the modal button
    const modalSaveButton = document.querySelector('.modal-save-btn') as HTMLButtonElement;
    fireEvent.click(modalSaveButton);

    // Should call saveNewResume with correct params
    await waitFor(() => {
      expect(mockSaveNewResume).toHaveBeenCalledWith('Frontend Resume', ['proj1', 'proj2']);
    });

    // Should reload resume list
    await waitFor(() => {
      expect(mockGetResumes).toHaveBeenCalledTimes(2); // Once on mount, once after save
    });

    // Should navigate to exit preview mode
    expect(mockNavigate).toHaveBeenCalledWith('/resumebuilderpage', { replace: true });
  });

  test('clicking save on existing resume updates it directly without modal', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Switch to saved resume
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());

    // Click save button
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    // Should call updateResume with resume id and payload (payload may be empty if no edits)
    await waitFor(() => {
      expect(mockUpdateResume).toHaveBeenCalledWith(2, expect.any(Object));
      const payload = mockUpdateResume.mock.calls[0][1];
      if (payload.projects?.length) {
        expect(payload.projects[0].project_id).toBe('proj-saved-1');
        expect(payload.projects[0].project_name).toBe('Saved Project');
      }
    });

    // Modal should not appear
    expect(screen.queryByText('Save Résumé version as:')).toBeNull();
  });

  test('save button shows Saving... and is disabled during save operation', async () => {
    let resolveUpdate: () => void;
    const updatePromise = new Promise<void>((resolve) => {
      resolveUpdate = resolve;
    });
    mockUpdateResume.mockReturnValue(updatePromise);

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Switch to saved resume
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());

    // Click save button
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    // Button should show "Saving..." and be disabled
    await waitFor(() => {
      const button = screen.getByRole('button', { name: 'Saving...' });
      expect(button).toBeDefined();
      expect(button.hasAttribute('disabled')).toBe(true);
    });

    // Resolve the save
    resolveUpdate!();

    // Button should return to normal
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Save' })).toBeDefined();
    });
  });

  test('handles save error gracefully for existing resume', async () => {
    mockUpdateResume.mockRejectedValue(new Error('Network error'));
    const consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');
    await waitFor(() => expect(mockBuildResume).toHaveBeenCalled());

    // Switch to saved resume
    const savedButton = screen.getByText('Saved Resume');
    fireEvent.click(savedButton);

    await waitFor(() => expect(mockGetResumeById).toHaveBeenCalled());

    // Click save button
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith('Failed to update resume. Please try again.');
    });

    // Button should be enabled again
    const finalButton = screen.getByRole('button', { name: 'Save' });
    expect(finalButton.hasAttribute('disabled')).toBe(false);

    consoleErrorMock.mockRestore();
    alertMock.mockRestore();
  });

  test('handles save error gracefully for new resume', async () => {
    mockSaveNewResume.mockRejectedValue(new Error('Network error'));
    const consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    // Open modal
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Save Résumé version as:')).toBeDefined();
    });

    // Click save in modal
    const modalSaveButton = document.querySelector('.modal-save-btn') as HTMLButtonElement;
    fireEvent.click(modalSaveButton);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith('Failed to save resume. Please try again.');
    });

    // Modal should still be open
    expect(screen.getByText('Save Résumé version as:')).toBeDefined();

    consoleErrorMock.mockRestore();
    alertMock.mockRestore();
  });

  test('does not save if resume name is empty', async () => {
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
    mockSearchParams.append('project_ids', 'proj1');

    render(<ResumeBuilderPage />);

    await screen.findByText('Preview Resume (Unsaved)');
    await waitFor(() => expect(mockPreviewResume).toHaveBeenCalled());

    // Open modal
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Save Résumé version as:')).toBeDefined();
    });

    // Clear the input
    const input = screen.getByPlaceholderText('Enter resume name...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '   ' } });

    // Click save in modal
    const modalSaveButton = document.querySelector('.modal-save-btn') as HTMLButtonElement;
    fireEvent.click(modalSaveButton);

    // Should show alert
    expect(alertMock).toHaveBeenCalledWith('Please enter a resume name');

    // Should not call save API
    expect(mockSaveNewResume).not.toHaveBeenCalled();

    alertMock.mockRestore();
  });
});
