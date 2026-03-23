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
  test('renders Check Job Match title', async () => {
    render(<ATSScoringPage />);
    const headings = screen.getAllByText('Check Job Match');
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

  test('renders job description textarea', async () => {
    render(<ATSScoringPage />);
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/Paste the full job description here/i)).toBeDefined()
    );
  });

  test('renders resume dropdown with master option after resumes load', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalledTimes(1));
    await waitFor(() => {
      expect(screen.getByText('Master Resume (all projects)')).toBeDefined();
      expect(screen.getByText('Backend Resume')).toBeDefined();
    });
  });

  // -----------------------------------------------------------------------
  // Calculate button state
  // -----------------------------------------------------------------------
  test('Check Job Match Score button is disabled when job description is too short', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    const btn = screen.getByRole('button', { name: /Check Job Match Score/i });
    expect(btn.hasAttribute('disabled')).toBe(true);
  });

  test('Check Job Match Score button is enabled with sufficient job description', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    expect(screen.getByRole('button', { name: /Check Job Match Score/i }).hasAttribute('disabled')).toBe(false);
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
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalledWith(LONG_JD, null, 'local'));
  });

  test('calls scoreATS with selected resume id when non-master resume is chosen', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(screen.getByRole('combobox'), { target: { value: '2' } });
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalledWith(LONG_JD, 2, 'local'));
  });

  test('shows match level badge after successful scoring', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(screen.getByText('High Match')).toBeDefined());
  });

  test('shows Keyword & Skills Analysis section after scoring when keywords are returned', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
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
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(screen.getByText('Server error')).toBeDefined());
  });

  // -----------------------------------------------------------------------
  // Keyword pill cap (Fix 3)
  // -----------------------------------------------------------------------
  test('merged keyword section is capped at 20 matched pills', async () => {
    // 25 keywords and 25 skills → merged set deduped then capped at 20
    const manyKeywords = Array.from({ length: 25 }, (_, i) => `keyword${i}`);
    const manySkills = Array.from({ length: 25 }, (_, i) => `skill${i}`);
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
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));

    await waitFor(() => {
      const matchedPills = container.querySelectorAll('.ats-keyword-matched');
      // Merged section capped at 20
      expect(matchedPills.length).toBeLessThanOrEqual(20);
      expect(matchedPills.length).toBeGreaterThan(0);
    });
  });

  // -----------------------------------------------------------------------
  // History tab
  // -----------------------------------------------------------------------
  test('history tab shows "No history yet" when empty', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    expect(screen.getByText(/Run your first job match score/i)).toBeDefined();
  });

  test('history entry is added after successful scoring', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
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
      expect(screen.getByText(/Run your first job match score/i)).toBeDefined()
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

  // -----------------------------------------------------------------------
  // Empty state (no resumes / DB wiped)
  // -----------------------------------------------------------------------
  test('shows empty state with upload CTA when no resumes exist', async () => {
    mockGetResumes.mockResolvedValue([]);
    render(<ATSScoringPage />);
    await waitFor(() =>
      expect(screen.getByText(/No resume available/i)).toBeDefined()
    );
    expect(screen.getByRole('button', { name: /Upload Projects/i })).toBeDefined();
    expect(screen.queryByPlaceholderText(/Paste the full job description here/i)).toBeNull();
  });

  test('clears localStorage history when no resumes are returned', async () => {
    localStorage.setItem('ats_history', JSON.stringify([makeHistoryEntry()]));
    mockGetResumes.mockResolvedValue([]);
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() =>
      expect(localStorage.getItem('ats_history')).toBeNull()
    );
  });

  // -----------------------------------------------------------------------
  // Local vs AI mode toggle
  // -----------------------------------------------------------------------
  test('renders Local and AI mode toggle buttons', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /^Local$/i })).toBeDefined();
      expect(screen.getByRole('button', { name: /^AI$/i })).toBeDefined();
    });
  });

  test('AI disclaimer is hidden when mode is Local', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByRole('button', { name: /^Local$/i })).toBeDefined());
    expect(screen.queryByText(/your job description will be sent/i)).toBeNull();
  });

  test('AI disclaimer appears when AI mode is selected', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByRole('button', { name: /^AI$/i })).toBeDefined());
    fireEvent.click(screen.getByRole('button', { name: /^AI$/i }));
    await waitFor(() =>
      expect(screen.getByText(/your job description will be sent/i)).toBeDefined()
    );
  });

  test('scoreATS is called with analysis_mode=local by default', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/Paste the full job description here/i)).toBeDefined()
    );
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalled());
    const [, , calledMode] = mockScoreATS.mock.calls[0] as [string, number | null, string];
    expect(calledMode).toBe('local');
  });

  test('scoreATS is called with analysis_mode=ai when AI mode selected', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByRole('button', { name: /^AI$/i })).toBeDefined());
    fireEvent.click(screen.getByRole('button', { name: /^AI$/i }));
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalled());
    const [, , calledMode] = mockScoreATS.mock.calls[0] as [string, number | null, string];
    expect(calledMode).toBe('ai');
  });

  test('history entry stores the analysis mode', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() => expect(screen.getByRole('button', { name: /^AI$/i })).toBeDefined());
    fireEvent.click(screen.getByRole('button', { name: /^AI$/i }));
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Check Job Match Score/i }));
    await waitFor(() => expect(mockScoreATS).toHaveBeenCalled());
    await waitFor(() => {
      const stored = JSON.parse(localStorage.getItem('ats_history') ?? '[]');
      expect(stored.length).toBeGreaterThan(0);
      expect(stored[0].analysisMode).toBe('ai');
    });
  });

  // -----------------------------------------------------------------------
  // Per-entry history deletion
  // -----------------------------------------------------------------------
  test('Remove button deletes only the target history entry', async () => {
    const entry1 = makeHistoryEntry({ id: 'entry-1', resumeName: 'Resume A' });
    const entry2 = makeHistoryEntry({ id: 'entry-2', resumeName: 'Resume B' });
    localStorage.setItem('ats_history', JSON.stringify([entry1, entry2]));

    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('tab', { name: /History/i }));
    await waitFor(() => expect(screen.getAllByText('Remove').length).toBe(2));

    fireEvent.click(screen.getAllByText('Remove')[0]);

    await waitFor(() => {
      expect(screen.getAllByText('Remove').length).toBe(1);
      const stored = JSON.parse(localStorage.getItem('ats_history') ?? '[]');
      expect(stored.length).toBe(1);
    });
  });

  // -----------------------------------------------------------------------
  // Score All Resumes button
  // -----------------------------------------------------------------------
  test('Score All Resumes button is visible when 2+ resumes are available', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Score All Resumes/i })).toBeDefined()
    );
  });

  test('Score All Resumes button is hidden when only one resume exists', async () => {
    mockGetResumes.mockResolvedValue([
      { id: null, name: 'Master Resume', is_master: true },
    ]);
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.queryByRole('button', { name: /Score All Resumes/i })).toBeNull()
    );
  });

  test('Score All Resumes calls scoreATS for each resume', async () => {
    render(<ATSScoringPage />);
    await waitFor(() => expect(mockGetResumes).toHaveBeenCalled());
    fireEvent.change(
      screen.getByPlaceholderText(/Paste the full job description here/i),
      { target: { value: LONG_JD } }
    );
    fireEvent.click(screen.getByRole('button', { name: /Score All Resumes/i }));

    await waitFor(() =>
      // One call per resume in MOCK_RESUME_LIST (master + Backend Resume = 2)
      expect(mockScoreATS).toHaveBeenCalledTimes(2)
    );
  });
});
