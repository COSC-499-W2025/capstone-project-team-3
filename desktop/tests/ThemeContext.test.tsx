import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../src/context/ThemeContext';
import { jest, test, expect, beforeEach, describe } from '@jest/globals';
import '@testing-library/jest-dom';

function TestConsumer() {
  const { fontSize, increaseFontSize, decreaseFontSize } = useTheme();
  return (
    <div>
      <span data-testid="fontSize">{fontSize}</span>
      <button onClick={increaseFontSize} data-testid="increase">Increase</button>
      <button onClick={decreaseFontSize} data-testid="decrease">Decrease</button>
    </div>
  );
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute('data-font-size');
});

describe('ThemeProvider font size', () => {
  test('provides default fontSize of default', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    expect(screen.getByTestId('fontSize')).toHaveTextContent('default');
  });

  test('loads saved fontSize from localStorage', () => {
    localStorage.setItem('fontSize', 'large');
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    expect(screen.getByTestId('fontSize')).toHaveTextContent('large');
  });

  test('ignores invalid fontSize in localStorage', () => {
    localStorage.setItem('fontSize', 'huge');
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    expect(screen.getByTestId('fontSize')).toHaveTextContent('default');
  });

  test('sets data-font-size attribute on html element', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    expect(document.documentElement.getAttribute('data-font-size')).toBe('default');
  });

  test('increaseFontSize moves from default to large', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('increase'));
    expect(screen.getByTestId('fontSize')).toHaveTextContent('large');
  });

  test('increaseFontSize clamps at x-large', () => {
    localStorage.setItem('fontSize', 'x-large');
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('increase'));
    expect(screen.getByTestId('fontSize')).toHaveTextContent('x-large');
  });

  test('decreaseFontSize moves from default to small', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('decrease'));
    expect(screen.getByTestId('fontSize')).toHaveTextContent('small');
  });

  test('decreaseFontSize clamps at small', () => {
    localStorage.setItem('fontSize', 'small');
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('decrease'));
    expect(screen.getByTestId('fontSize')).toHaveTextContent('small');
  });

  test('fontSize changes persist to localStorage', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('increase'));
    expect(localStorage.getItem('fontSize')).toBe('large');
  });

  test('fontSize changes update data-font-size attribute', () => {
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByTestId('increase'));
    expect(document.documentElement.getAttribute('data-font-size')).toBe('large');
  });

  test('full font size cycle up and back down', () => {
    localStorage.setItem('fontSize', 'small');
    render(<ThemeProvider><TestConsumer /></ThemeProvider>);

    fireEvent.click(screen.getByTestId('increase')); // small -> default
    expect(screen.getByTestId('fontSize')).toHaveTextContent('default');

    fireEvent.click(screen.getByTestId('increase')); // default -> large
    expect(screen.getByTestId('fontSize')).toHaveTextContent('large');

    fireEvent.click(screen.getByTestId('increase')); // large -> x-large
    expect(screen.getByTestId('fontSize')).toHaveTextContent('x-large');

    fireEvent.click(screen.getByTestId('decrease')); // x-large -> large
    expect(screen.getByTestId('fontSize')).toHaveTextContent('large');

    fireEvent.click(screen.getByTestId('decrease')); // large -> default
    expect(screen.getByTestId('fontSize')).toHaveTextContent('default');

    fireEvent.click(screen.getByTestId('decrease')); // default -> small
    expect(screen.getByTestId('fontSize')).toHaveTextContent('small');
  });
});
