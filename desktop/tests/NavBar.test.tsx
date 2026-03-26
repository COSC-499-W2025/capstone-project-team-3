import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect, jest } from '@jest/globals';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { NavBar } from '../src/NavBar';

// ── Theme Mock
const mockToggleTheme = jest.fn();
const mockIncreaseFontSize = jest.fn();
const mockDecreaseFontSize = jest.fn();
let mockTheme = 'light';
let mockFontSize = 'default';

jest.mock('../src/context/ThemeContext', () => ({
  useTheme: () => ({ 
    theme: mockTheme, 
    toggleTheme: mockToggleTheme,
    fontSize: mockFontSize,
    increaseFontSize: mockIncreaseFontSize,
    decreaseFontSize: mockDecreaseFontSize
  }),
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

  // ── Text Size Toggle Tests
  test('renders text size toggle button', () => {
    renderNavBar();
    const textSizeToggle = screen.getByRole('button', { name: /adjust text size/i });
    expect(textSizeToggle).toBeInTheDocument();
    expect(textSizeToggle).toHaveAttribute('aria-expanded', 'false');
  });

  test('clicking text size toggle expands controls', () => {
    renderNavBar();
    const textSizeToggle = screen.getByRole('button', { name: /adjust text size/i });
    
    expect(screen.queryByRole('button', { name: /decrease text size/i })).not.toBeInTheDocument();
    
    fireEvent.click(textSizeToggle);
    
    expect(textSizeToggle).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('button', { name: /decrease text size/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /increase text size/i })).toBeInTheDocument();
  });

  test('clicking text size toggle again collapses controls', () => {
    renderNavBar();
    const textSizeToggle = screen.getByRole('button', { name: /adjust text size/i });
    
    fireEvent.click(textSizeToggle);
    expect(screen.getByRole('button', { name: /decrease text size/i })).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole('button', { name: /hide text size controls/i }));
    expect(screen.queryByRole('button', { name: /decrease text size/i })).not.toBeInTheDocument();
  });

  test('decrease text size button calls decreaseFontSize', () => {
    mockDecreaseFontSize.mockClear();
    renderNavBar();
    
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    fireEvent.click(screen.getByRole('button', { name: /decrease text size/i }));
    
    expect(mockDecreaseFontSize).toHaveBeenCalledTimes(1);
  });

  test('increase text size button calls increaseFontSize', () => {
    mockIncreaseFontSize.mockClear();
    renderNavBar();
    
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    fireEvent.click(screen.getByRole('button', { name: /increase text size/i }));
    
    expect(mockIncreaseFontSize).toHaveBeenCalledTimes(1);
  });

  test('displays correct text size label for default size', () => {
    mockFontSize = 'default';
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    expect(screen.getByText('M')).toBeInTheDocument();
  });

  test('displays correct text size label for small size', () => {
    mockFontSize = 'small';
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    expect(screen.getByText('S')).toBeInTheDocument();
  });

  test('displays correct text size label for large size', () => {
    mockFontSize = 'large';
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    expect(screen.getByText('L')).toBeInTheDocument();
  });

  test('displays correct text size label for x-large size', () => {
    mockFontSize = 'x-large';
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    expect(screen.getByText('XL')).toBeInTheDocument();
  });

  // ── Accessibility: aria semantics
  test('text size toggle has aria-controls pointing to controls', () => {
    renderNavBar();
    const toggle = screen.getByRole('button', { name: /adjust text size/i });
    expect(toggle).toHaveAttribute('aria-controls', 'text-size-controls');
  });

  test('expanded controls have role group and aria-label', () => {
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    const group = screen.getByRole('group', { name: /text size controls/i });
    expect(group).toBeInTheDocument();
  });

  test('size label has aria-live for screen reader announcements', () => {
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    const label = screen.getByLabelText(/text size:/i);
    expect(label).toHaveAttribute('aria-live', 'polite');
  });

  // ── Keyboard navigation
  test('text size toggle is focusable', () => {
    renderNavBar();
    const toggle = screen.getByRole('button', { name: /adjust text size/i });
    toggle.focus();
    expect(document.activeElement).toBe(toggle);
  });

  test('increase button is focusable when expanded', () => {
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    const btn = screen.getByRole('button', { name: /increase text size/i });
    btn.focus();
    expect(document.activeElement).toBe(btn);
  });

  test('decrease button is focusable when expanded', () => {
    renderNavBar();
    fireEvent.click(screen.getByRole('button', { name: /adjust text size/i }));
    const btn = screen.getByRole('button', { name: /decrease text size/i });
    btn.focus();
    expect(document.activeElement).toBe(btn);
  });

  test('increase button responds to Enter key', async () => {
    const user = userEvent.setup();
    mockIncreaseFontSize.mockClear();
    renderNavBar();
    await user.click(screen.getByRole('button', { name: /adjust text size/i }));
    await user.keyboard('{Tab}{Tab}');
    await user.keyboard('{Enter}');
    expect(mockIncreaseFontSize).toHaveBeenCalledTimes(1);
  });

  test('decrease button responds to Enter key', async () => {
    const user = userEvent.setup();
    mockDecreaseFontSize.mockClear();
    renderNavBar();
    await user.click(screen.getByRole('button', { name: /adjust text size/i }));
    await user.keyboard('{Tab}');
    await user.keyboard('{Enter}');
    expect(mockDecreaseFontSize).toHaveBeenCalledTimes(1);
  });
});
