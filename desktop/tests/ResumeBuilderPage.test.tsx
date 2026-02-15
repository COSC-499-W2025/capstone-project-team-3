import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResumeBuilderPage } from '../src/pages/ResumeBuilderPage';
import * as resumeApi from '../src/api/resume';
import type { ResumeListItem } from '../src/api/resume';
import { jest, test, expect, describe, beforeEach } from '@jest/globals';

jest.mock('../src/api/resume', () => ({
  getResumes: jest.fn(),
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

const mockGetResumes = resumeApi.getResumes as ReturnType<typeof jest.fn>;

const mockResumeList: ResumeListItem[] = [
  { id: null, name: 'Master Resume', is_master: true },
  { id: 2, name: 'Saved Resume', is_master: false },
];

describe('ResumeBuilderPage', () => {
  beforeEach(() => {
    mockGetResumes.mockResolvedValue(mockResumeList);
  });

  test('fetches resume list on mount', async () => {
    render(<ResumeBuilderPage />);

    expect(mockGetResumes).toHaveBeenCalledTimes(1);
    await screen.findByText('Master Resume');
    expect(screen.getByText('Saved Resume')).toBeDefined();
  });

  test('sidebar receives list from getResumes and shows Tailor New Resume button', async () => {
    render(<ResumeBuilderPage />);

    expect(screen.getByText('Your Résumés')).toBeDefined();
    await screen.findByText('Master Resume');
    expect(screen.getByText('Saved Resume')).toBeDefined();
    expect(screen.getByText('Tailor New Resume')).toBeDefined();
  });

  test('clicking a resume updates selection (activeIndex)', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');

    const masterButton = screen.getByText('Master Resume');
    const savedButton = screen.getByText('Saved Resume');
    expect(masterButton.getAttribute('data-active')).toBe('true');
    expect(savedButton.getAttribute('data-active')).toBe('false');

    fireEvent.click(savedButton);

    expect(masterButton.getAttribute('data-active')).toBe('false');
    expect(savedButton.getAttribute('data-active')).toBe('true');
  });

  test('toggle sidebar updates sidebar open state', async () => {
    render(<ResumeBuilderPage />);

    await screen.findByText('Master Resume');

    const hideButton = screen.getByLabelText('Hide sidebar');
    fireEvent.click(hideButton);

    expect(screen.getByLabelText('Show sidebar')).toBeDefined();
  });
});
