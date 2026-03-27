import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";
type FontSize = "small" | "default" | "large" | "x-large";

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
  fontSize: FontSize;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "light",
  toggleTheme: () => {},
  fontSize: "default",
  increaseFontSize: () => {},
  decreaseFontSize: () => {},
});

/**
 * Reads the saved theme from localStorage (default: "light"),
 * applies it as a `data-theme` attribute on <html>, and exposes
 * `theme` + `toggleTheme` to any descendant via `useTheme()`.
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("theme");
    return saved === "dark" ? "dark" : "light";
  });

  const [fontSize, setFontSize] = useState<FontSize>(() => {
    const saved = localStorage.getItem("fontSize");
    return (saved === "small" || saved === "default" || saved === "large" || saved === "x-large") 
      ? saved as FontSize 
      : "default";
  });

  // Sync the data-theme attribute on <html> whenever theme changes
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Sync the data-font-size attribute on <html> whenever font size changes
  useEffect(() => {
    document.documentElement.setAttribute("data-font-size", fontSize);
    localStorage.setItem("fontSize", fontSize);
  }, [fontSize]);

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  function increaseFontSize() {
    setFontSize((prev) => {
      const order: FontSize[] = ["small", "default", "large", "x-large"];
      const currentIndex = order.indexOf(prev);
      return order[Math.min(currentIndex + 1, order.length - 1)];
    });
  }

  function decreaseFontSize() {
    setFontSize((prev) => {
      const order: FontSize[] = ["small", "default", "large", "x-large"];
      const currentIndex = order.indexOf(prev);
      return order[Math.max(currentIndex - 1, 0)];
    });
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, fontSize, increaseFontSize, decreaseFontSize }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  return useContext(ThemeContext);
}
