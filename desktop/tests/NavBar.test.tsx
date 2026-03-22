import { render, screen, fireEvent } from '@testing-library/react';
import { describe, test, expect, jest } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { NavBar } from '../src/NavBar';

// ── Theme Mock
const mockToggleTheme = jest.fn();
let mockTheme = 'light';

jest.mock('../src/context/ThemeContext', () => ({
  useTheme: () => ({ theme: mockTheme, toggleTheme: mockToggleTheme }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

function renderNavBar() {
  return render(
    <BrowserRouter>
      <NavBar />
    </BrowserRouter>
  );
}

describe('NavBar', () => {
  test('renders sidebar with brand Insights', () => {
    renderNavBar();
    const brand = screen.getByRole('link', { name: /insights/i });
    expect(brand).toBeInTheDocument();
    expect(brand).toHaveAttribute('href', '/hubpage');
  });

  test('renders all main nav links from config', () => {
    renderNavBar();
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /upload/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /projects/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /resume/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /portfolio/i })).toBeInTheDocument();
  });

  test('main nav links have correct hrefs', () => {
    renderNavBar();
    expect(screen.getByRole('link', { name: /dashboard/i })).toHaveAttribute('href', '/hubpage');
    expect(screen.getByRole('link', { name: /upload/i })).toHaveAttribute('href', '/uploadpage');
    expect(screen.getByRole('link', { name: /projects/i })).toHaveAttribute('href', '/datamanagementpage');
    expect(screen.getByRole('link', { name: /resume/i })).toHaveAttribute('href', '/resumebuilderpage');
    expect(screen.getByRole('link', { name: /portfolio/i })).toHaveAttribute('href', '/portfoliopage');
  });

  test('renders footer Settings link', () => {
    renderNavBar();
    const settingsLink = screen.getByRole('link', { name: /settings/i });
    expect(settingsLink).toBeInTheDocument();
    expect(settingsLink).toHaveAttribute('href', '/settingspage');
    expect(settingsLink).toHaveAttribute('title', 'Settings');
  });

  test('collapse button toggles sidebar collapsed state', () => {
    const { container } = renderNavBar();
    const aside = container.querySelector('.app-sidebar');
    expect(aside).not.toHaveClass('app-sidebar--collapsed');

    const collapseButton = screen.getByRole('button', { name: /collapse sidebar/i });
    expect(collapseButton).toHaveAttribute('aria-expanded', 'true');

    fireEvent.click(collapseButton);
    expect(aside).toHaveClass('app-sidebar--collapsed');
    expect(screen.getByRole('button', { name: /expand sidebar/i })).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(screen.getByRole('button', { name: /expand sidebar/i }));
    expect(aside).not.toHaveClass('app-sidebar--collapsed');
  });

  test('renders theme toggle button with moon icon in light mode', () => {
    mockTheme = 'light';
    renderNavBar();
    const toggleBtn = screen.getByRole('button', { name: /switch to dark mode/i });
    expect(toggleBtn).toBeInTheDocument();
  });

  test('clicking theme toggle calls toggleTheme', () => {
    mockTheme = 'light';
    mockToggleTheme.mockClear();
    renderNavBar();
    const toggleBtn = screen.getByRole('button', { name: /switch to dark mode/i });
    fireEvent.click(toggleBtn);
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  test('renders sun icon when theme is dark', () => {
    mockTheme = 'dark';
    renderNavBar();
    const toggleBtn = screen.getByRole('button', { name: /switch to light mode/i });
    expect(toggleBtn).toBeInTheDocument();
  });
});
