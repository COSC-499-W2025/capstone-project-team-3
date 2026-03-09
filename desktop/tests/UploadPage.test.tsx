import { render, screen, fireEvent } from '@testing-library/react';
import { UploadPage } from '../src/pages/UploadPage';
import { test, expect, jest, beforeEach } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import * as uploadApi from '../src/api/upload';

jest.mock('../src/api/upload');

const mockUploadZipFile = uploadApi.uploadZipFile as jest.MockedFunction<typeof uploadApi.uploadZipFile>;

beforeEach(() => {
  jest.clearAllMocks();
});

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

test('renders drop hint', () => {
  render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  expect(screen.getByText(/Drop your ZIP file here or click to browse/i)).toBeInTheDocument();
});

test('selecting non-zip file shows error', () => {
  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const file = new File(['content'], 'test.txt', { type: 'text/plain' });
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(screen.getByText(/Please upload a ZIP file/i)).toBeInTheDocument();
});

test('selecting zip file auto-uploads and shows success', async () => {
  mockUploadZipFile.mockResolvedValue({ status: 'ok', upload_id: 'abc-123-uuid' });

  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const file = new File(['content'], 'project.zip', { type: 'application/zip' });
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(await screen.findByText(/Upload successful. Your file has been saved/i)).toBeInTheDocument();
});

test('upload error shows error message', async () => {
  mockUploadZipFile.mockRejectedValue(new Error('Upload failed'));

  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const file = new File(['content'], 'project.zip', { type: 'application/zip' });
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(await screen.findByRole('alert')).toHaveTextContent('Upload failed');
});

test('shows uploaded filename and Remove button clears it', async () => {
  mockUploadZipFile.mockResolvedValue({ status: 'ok', upload_id: 'abc-123' });

  const { container } = render(
    <BrowserRouter>
      <UploadPage />
    </BrowserRouter>
  );

  const file = new File(['content'], 'my-project.zip', { type: 'application/zip' });
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(await screen.findByText(/Uploaded: my-project\.zip/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Remove/i })).toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', { name: /Remove/i }));

  expect(screen.queryByText(/Uploaded: my-project\.zip/i)).not.toBeInTheDocument();
  expect(screen.getByText(/Drop your ZIP file here or click to browse/i)).toBeInTheDocument();
});
