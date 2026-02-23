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

  test('clicking edit or delete does not trigger row selection', () => {
    const onDelete = jest.fn();
    renderSidebar({ onEdit: jest.fn(), onDelete });

    fireEvent.click(screen.getAllByLabelText('Edit resume')[0]);
    expect(defaultProps.onSelect).not.toHaveBeenCalled();

    const deleteButtons = screen.getAllByLabelText('Delete resume');
    window.confirm = jest.fn(() => false); // Cancel delete to avoid triggering onDelete
    fireEvent.click(deleteButtons[0]);
    expect(defaultProps.onSelect).not.toHaveBeenCalled();
  });

  test('does not show Edit button for master resume', () => {
    renderSidebar({ onEdit: jest.fn(), onDelete: jest.fn() });

    const editButtons = screen.getAllByLabelText('Edit resume');
    // Only 2 saved resumes (id != null), so only 2 Edit buttons
    expect(editButtons).toHaveLength(2);
    // Master Resume row (first) has no Edit button
    const firstRow = screen.getByText('Master Resume').closest('.resume-sidebar__item');
    expect(firstRow?.querySelector('[aria-label="Edit resume"]')).toBeNull();
  });

  test('does not show Edit button for preview resume (id null)', () => {
    const listWithPreview: ResumeListItem[] = [
      { id: null, name: 'Preview Resume (Unsaved)', is_master: false },
      { id: 2, name: 'Saved Resume', is_master: false },
    ];
    renderSidebar({ resumeList: listWithPreview, onEdit: jest.fn(), onDelete: jest.fn() });

    // Only the saved resume (id 2) has Edit button
    const editButtons = screen.getAllByLabelText('Edit resume');
    expect(editButtons).toHaveLength(1);
    const previewRow = screen.getByText('Preview Resume (Unsaved)').closest('.resume-sidebar__item');
    expect(previewRow?.querySelector('[aria-label="Edit resume"]')).toBeNull();
  });

  test('delete button only shows for non-master resumes (id > 1)', () => {
    const onDelete = jest.fn();
    renderSidebar({ onDelete });

    const deleteButtons = screen.queryAllByLabelText('Delete resume');
    // Should have 2 delete buttons (for id=2 and id=3, not for id=null)
    expect(deleteButtons.length).toBe(2);
  });

  test('master resume does not have delete button', () => {
    const list: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
      { id: 1, name: 'Resume with id=1', is_master: false },
    ];
    const onDelete = jest.fn();
    renderSidebar({ resumeList: list, onDelete });

    // Neither master (id=null) nor id=1 should have delete button
    const deleteButtons = screen.queryAllByLabelText('Delete resume');
    expect(deleteButtons.length).toBe(0);
  });

  test('clicking delete button shows confirmation dialog', () => {
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => true);
    renderSidebar({ onDelete });

    const deleteButtons = screen.getAllByLabelText('Delete resume');
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete "Software Engineer Resume"?');
  });

  test('clicking delete calls onDelete when user confirms', () => {
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => true);
    renderSidebar({ onDelete });

    const deleteButtons = screen.getAllByLabelText('Delete resume');
    fireEvent.click(deleteButtons[0]); // Delete second resume (id=2)

    expect(window.confirm).toHaveBeenCalled();
    expect(onDelete).toHaveBeenCalledWith(2);
  });

  test('clicking delete does not call onDelete when user cancels', () => {
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => false);
    renderSidebar({ onDelete });

    const deleteButtons = screen.getAllByLabelText('Delete resume');
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  test('delete button uses resume name in confirmation or fallback text', () => {
    const list: ResumeListItem[] = [
      { id: null, name: 'Master Resume', is_master: true },
      { id: 2, name: '', is_master: false }, // Empty name
    ];
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => false);
    renderSidebar({ resumeList: list, onDelete });

    const deleteButton = screen.getByLabelText('Delete resume');
    fireEvent.click(deleteButton);

    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete "this resume"?');
  });

  test('no delete buttons appear when onDelete is not provided', () => {
    renderSidebar({ onDelete: undefined });

    const deleteButtons = screen.queryAllByLabelText('Delete resume');
    expect(deleteButtons.length).toBe(0);
  });
});
