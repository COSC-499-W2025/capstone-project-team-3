import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResumeSidebar } from '../src/pages/ResumeManager/ResumeSidebar';
import type { ResumeListItem } from '../src/api/resume';
import { jest, test, expect, describe, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';

const defaultResumeList: ResumeListItem[] = [
  { id: null, name: 'Master Resume', is_master: true },
  { id: 2, name: 'Software Engineer Resume', is_master: false },
  { id: 3, name: 'Data Analyst Resume', is_master: false },
];

const defaultProps = {
  resumeList: defaultResumeList,
  activeIndex: 0,
  onSelect: jest.fn(),
};

function renderSidebar(overrides = {}) {
  return render(
    <ResumeSidebar
      {...defaultProps}
      {...overrides}
    />
  );
}

describe('ResumeSidebar', () => {
  beforeEach(() => {
    defaultProps.onSelect.mockClear();
  });

  test('shows title and all resume names', () => {
    renderSidebar();

    expect(screen.getByText('Your Résumés')).toBeDefined();
    defaultResumeList.forEach(({ name }) => {
      expect(screen.getByText(name)).toBeDefined();
    });
  });

  test('clicking a resume row calls onSelect with its index', () => {
    renderSidebar();

    fireEvent.click(screen.getByText('Software Engineer Resume'));

    expect(defaultProps.onSelect).toHaveBeenCalledWith(1);
  });

  test('active row has active class; others do not', () => {
    const { container } = renderSidebar({ activeIndex: 1 });

    const rows = container.querySelectorAll('.resume-sidebar__item');
    expect(rows[1].classList.contains('resume-sidebar__item--active')).toBe(true);
    expect(rows[0].classList.contains('resume-sidebar__item--active')).toBe(false);
  });

  test('clicking Tailor New Resume calls onTailorNew', () => {
    const onTailorNew = jest.fn();
    renderSidebar({ onTailorNew });

    fireEvent.click(screen.getByText('Tailor New Resume'));

    expect(onTailorNew).toHaveBeenCalledTimes(1);
  });

  test('empty name shows fallback "Resume - {index}"', () => {
    const list: ResumeListItem[] = [
      { id: 1, name: '', is_master: true },
      { id: 2, name: 'Custom Name', is_master: false },
    ];
    renderSidebar({ resumeList: list });

    expect(screen.getByText('Resume - 1')).toBeDefined();
    expect(screen.getByText('Custom Name')).toBeDefined();
  });

  test('toggle button calls onToggleSidebar; sidebar class reflects open/closed', () => {
    const onToggleSidebar = jest.fn();
    const { container, rerender } = renderSidebar({
      sidebarOpen: true,
      onToggleSidebar,
    });

    expect(container.querySelector('.resume-sidebar')?.classList.contains('resume-sidebar--open')).toBe(true);
    fireEvent.click(screen.getByLabelText('Hide sidebar'));
    expect(onToggleSidebar).toHaveBeenCalledTimes(1);

    rerender(
      <ResumeSidebar {...defaultProps} sidebarOpen={false} />
    );
    expect(container.querySelector('.resume-sidebar')?.classList.contains('resume-sidebar--closed')).toBe(true);
  });

  test('clicking edit or more options does not trigger row selection', () => {
    renderSidebar({ onEdit: jest.fn() });

    fireEvent.click(screen.getAllByLabelText('Edit resume')[0]);
    expect(defaultProps.onSelect).not.toHaveBeenCalled();

    fireEvent.click(screen.getAllByLabelText('More options')[0]);
    expect(defaultProps.onSelect).not.toHaveBeenCalled();
  });

  test('does not show Edit button for master resume', () => {
    renderSidebar({ onEdit: jest.fn() });

    const editButtons = screen.getAllByLabelText('Edit resume');
    // Only 2 non-master resumes, so only 2 Edit buttons
    expect(editButtons).toHaveLength(2);
    // Master Resume row (first) has no Edit button
    const firstRow = screen.getByText('Master Resume').closest('.resume-sidebar__item');
    expect(firstRow?.querySelector('[aria-label="Edit resume"]')).toBeNull();
  });
});
