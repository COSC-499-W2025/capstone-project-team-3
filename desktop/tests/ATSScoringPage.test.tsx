import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ATSScoringPage } from '../src/pages/ATSScoringPage';
import * as atsApi from '../src/api/ats';
import * as resumeApi from '../src/api/resume';
import { jest, test, describe, beforeEach, afterEach } from '@jest/globals';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual<typeof import('react-router-dom')>('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

jest.mock('../src/api/ats', () => ({
  scoreATS: jest.fn(),
}));

jest.mock('../src/api/resume', () => ({
  getResumes: jest.fn(),
}));

const mockScoreATS = atsApi.scoreATS as ReturnType<typeof jest.fn>;
const mockGetResumes = resumeApi.getResumes as ReturnType<typeof jest.fn>;

const MOCK_RESUME_LIST = [
  { id: null, name: 'Master Resume', is_master: true },
  { id: 2, name: 'Backend Resume', is_master: false },
];

const MOCK_ATS_RESULT = {
  score: 75,
  match_level: 'High',
  experience_months: 6,
  breakdown: { keyword_coverage: 80, skills_match: 70, content_richness: 64 },
  matched_keywords: ['python', 'react'],
  missing_keywords: ['kubernetes'],
  matched_skills: ['python'],
  missing_skills: ['kubernetes'],
  tips: ['Add more skills from the job description.'],
};

const LONG_JD =
  'We are looking for a software engineer with Python and React experience. ' +
  'Must have 3 or more years with Docker and AWS cloud infrastructure.';

function makeHistoryEntry(overrides = {}) {
  return {
    id: '1234',
    timestamp: new Date().toISOString(),
    resumeId: 2,
    resumeName: 'Backend Resume',
    jobDescriptionPreview: 'Looking for Python developer',
    jobDescription: 'Looking for Python developer with 3 years of backend experience.',
    score: 82,
    matchLevel: 'High',
    experienceMonths: 8,
    breakdown: { keyword_coverage: 85, skills_match: 80, content_richness: 72 },
    matchedKeywords: ['python', 'api'],
    missingKeywords: ['kubernetes'],
    tips: ['Mirror exact wording from the job description.'],
    ...overrides,
  };
}

describe('ATSScoringPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
    localStorage.clear();
    mockGetResumes.mockResolvedValue(MOCK_RESUME_LIST);
    mockScoreATS.mockResolvedValue(MOCK_ATS_RESULT);
  });

  afterEach(() => {
    localStorage.clear();
  });

  // -----------------------------------------------------------------------
  // Rendering
  // -----------------------------------------------------------------------
  test('renders ATS Scoring title', async () => {
    render(<ATSScoringPage />);
    const headings = screen.getAllByText('ATS Scoring');
    expect(headings.length).toBeGreaterThan(0);
  });

  test('renders page description', async () => {
    render(<ATSScoringPage />);
    expect(screen.getByText(/Paste a job description/i)).toBeDefined();
  });

  test('renders Score and History tabs', () => {
    render(<ATSScoringPage />);
    expect(screen.getByRole('tab', { name: 'Score' })).toBeDefined();
    expect(screen.getByRole('tab', { name: /History/i })).toBeDefined();
  });

  test('renders job description textarea', () => {
    render(<ATSScoringPage />);
    expect(screen.getByPlaceholderText(/Paste the full job description here/i)).toBeDefined();
  });

  test('renders resume dropdown with master option after resumes load', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalledTimes(1));
    await waitFor(() => {
      expect(screen.getByText('Master Resume (all projects)')).toBeDefined();
      expect(screen.getByText('Backend Resume')).toBeDefined();
    });
  });

  test('renders Manage Resumes link', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    expect(screen.getByText(/Manage Resumes/i)).toBeDefined();
  });

  // -----------------------------------------------------------------------
  // Calculate button state
  // -----------------------------------------------------------------------
  test('Calculate ATS Score button is disabled when job description is too short', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    const btn = screen.getByRole('button', { name: /Calculate ATS Score/i });
    expect(btn.hasAttribute('disabled')).toBe(true);
  });

  test('Calculate ATS Score button is enabled with sufficient job description', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    expect(screen.getByRole('button', { name: /Calculate ATS Score/i }).hasAttribute('disabled')).toBe(false);
  });

  // -----------------------------------------------------------------------
  // Manage Resumes navigation link (Fix 2)
  // -----------------------------------------------------------------------
  test('Manage Resumes link navigates to /resumebuilderpage', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.click(screen.getByText(/Manage Resumes/i));
    expect(mockNavigate).toHaveBeenCalledWith('/resumebuilderpage');
  });

  // -----------------------------------------------------------------------
  // Scoring
  // -----------------------------------------------------------------------
  test('calls scoreATS with job description and null resume id for master resume', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalledWith(LONG_JD, null));
  });

  test('calls scoreATS with selected resume id when non-master resume is chosen', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(screen.getByRole('combobox'), { target: { value: '2' } });
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalledWith(LONG_JD, 2));
  });

  test('shows match level badge after successful scoring', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => expect(screen.getByText('High Match')).toBeDefined());
  });

  test('shows Keyword & Skills Analysis section after scoring', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => {
      expect(screen.getByText(/Keyword.*Skills Analysis/i)).toBeDefined();
    });
  });

  test('shows error message when scoreATS fails', async () => {
    mockScoreATS.mockRejectedValue(new Error('Server error'));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => expect(screen.getByText('Server error')).toBeDefined());
  });

  // -----------------------------------------------------------------------
  // Keyword pill cap (Fix 3)
  // -----------------------------------------------------------------------
  test('keyword pills are capped at 20 matched even when API returns more combined items', async () => {
    // 15 unique keywords + 15 unique skills = 30 items → should be capped to 20
    const manyKeywords = Array.from({ length: 15 }, (_, i) => `keyword${i}`);
    const manySkills = Array.from({ length: 15 }, (_, i) => `skill${i}`);
    mockScoreATS.mockResolvedValue({
      ...MOCK_ATS_RESULT,
      matched_keywords: manyKeywords,
      missing_keywords: [],
      matched_skills: manySkills,
      missing_skills: [],
    });

    const { container } = render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));

    await waitFor(() => {
      const matchedPills = container.querySelectorAll('.ats-keyword-matched');
      expect(matchedPills.length).toBeLessThanOrEqual(20);
    });
  });

  // -----------------------------------------------------------------------
  // History tab
  // -----------------------------------------------------------------------
  test('history tab shows "No history yet" when empty', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    expect(screen.getByText(/Run your first ATS score/i)).toBeDefined();
  });

  test('history entry is added after successful scoring', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Calculate ATS Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalled());
    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getByText('1 saved score')).toBeDefined());
  });

  test('history tab shows count badge on tab when there are entries', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry()]));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    // The count badge "1" should appear inside the History tab
    const historyTab = screen.getByRole('tab', { name: /History/i });
    expect(historyTab.textContent).toContain('1');
  });

  // -----------------------------------------------------------------------
  // Restore from history (Fix 1)
  // -----------------------------------------------------------------------
  test('restore from history restores job description without re-running scoring', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry()]));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getByText('Restore')).toBeDefined());
    fireEvent.click(screen.getByText('Restore'));

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(
        /Paste the full job description here/i
      ) as HTMLTextAreaElement;
      expect(textarea.value).toBe('Looking for Python developer with 3 years of backend experience.');
    });
    expect(mockScoreATS).not.toHaveBeenCalled();
  });

  test('restore from history shows prior score result immediately', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry()]));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getByText('Restore')).toBeDefined());
    fireEvent.click(screen.getByText('Restore'));

    await waitFor(() => expect(screen.getByText('High Match')).toBeDefined());
  });

  test('restore from history selects the stored resume id', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry({ resumeId: 2 })]));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getByText('Restore')).toBeDefined());
    fireEvent.click(screen.getByText('Restore'));

    await waitFor(() => {
      const select = screen.getByRole('combobox') as HTMLSelectElement;
      expect(select.value).toBe('2');
    });
  });

  // -----------------------------------------------------------------------
  // Clear history
  // -----------------------------------------------------------------------
  test('Clear History button removes all history entries', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry()]));
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getByText('Clear History')).toBeDefined());
    fireEvent.click(screen.getByText('Clear History'));

    await waitFor(() =>
      expect(screen.getByText(/Run your first ATS score/i)).toBeDefined()
    );
  });

  // -----------------------------------------------------------------------
  // Master resume conditional display (Fix 4)
  // -----------------------------------------------------------------------
  test('master resume option is shown when is_master resume exists in list', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.getByText('Master Resume (all projects)')).toBeDefined()
    );
  });

  test('master resume option is hidden when no is_master resume in fetched list', async () => {
    mockGetResumes.mockResolvedValue([
      { id: 2, name: 'Backend Resume', is_master: false },
    ]);
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => {
      expect(screen.queryByText('Master Resume (all projects)')).toBeNull();
      expect(screen.getByText('Backend Resume')).toBeDefined();
    });
  });

  test('selects first non-master resume by default when master resume does not exist', async () => {
    mockGetResumes.mockResolvedValue([
      { id: 2, name: 'Backend Resume', is_master: false },
      { id: 3, name: 'Frontend Resume', is_master: false },
    ]);
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => {
      const select = screen.getByRole('combobox') as HTMLSelectElement;
      expect(select.value).toBe('2');
    });
  });
});
