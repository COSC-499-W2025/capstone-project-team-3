import { render, screen, fireEvent } from '@testing-library/react';
import { TemplatePage } from '../src/pages/TemplatePage';
import { jest, test, expect } from '@jest/globals';
import '@testing-library/jest-dom';

// Mock API
jest.mock('../src/api/template', () => ({
  callEndpoint: jest.fn(() => Promise.resolve({ result: 'ok' })),
}));

test('renders template page and fetches data', async () => {
  render(<TemplatePage />);

  const button = screen.getByText(/run/i);
  expect(button).toBeDefined();

  fireEvent.click(button);

  const result = await screen.findByText(/ok/i);
  expect(result).toBeDefined();
});
