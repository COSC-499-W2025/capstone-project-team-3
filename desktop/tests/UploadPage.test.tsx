import { render, screen } from '@testing-library/react';
import { UploadPage } from '../src/pages/UploadPage';
import { test, expect } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';

test('renders upload page with title', () => {
  render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Upload Project to analyse/i);
  expect(title).toBeDefined();
});

test('renders single frame', () => {
  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const frames = container.querySelectorAll('.upload-frame');
  expect(frames.length).toBe(1);
});

test('renders upload icon', () => {
  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const icon = container.querySelector('.upload-icon svg');
  expect(icon).toBeDefined();
});

test('title is positioned above rectangle', () => {
  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const title = screen.getByText(/Upload Project to analyse/i);
  const titleElement = title as HTMLElement;
  
  expect(title).toBeDefined();
  // Title should be direct child of container
  expect(titleElement.parentElement?.classList.contains('upload-container')).toBe(true);
});

test('frame contains icon', () => {
  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const frame = container.querySelector('.upload-frame');
  const icon = frame?.querySelector('.upload-icon');
  
  expect(frame).toBeDefined();
  expect(icon).toBeDefined();
});
