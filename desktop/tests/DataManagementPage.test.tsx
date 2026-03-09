import { render, screen } from '@testing-library/react';
import { DataManagementPage } from '../src/pages/DataManagementPage';
import { test, expect } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

test('renders data management page with title', () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Data Management/i);
  expect(title).toBeInTheDocument();
});

test('renders description', () => {
  render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const description = screen.getByText(/View and edit chronological information/i);
  expect(description).toBeInTheDocument();
});

test('title is in container', () => {
  const { container } = render(
    <BrowserRouter>
      <DataManagementPage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Data Management/i);
  expect(title.parentElement?.classList.contains('data-management-container')).toBe(true);
});
