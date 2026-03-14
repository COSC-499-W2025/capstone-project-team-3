/**
 * Main app navigation: path and display label for the sidebar.
 * Order here defines the order of links in the bar.
 */
export const mainNavItems: { path: string; label: string }[] = [
  { path: "/hubpage", label: "Dashboard" },
  { path: "/uploadpage", label: "Upload" },
  { path: "/datamanagementpage", label: "Projects" },
  { path: "/resumebuilderpage", label: "Resume" },
  { path: "/portfoliopage", label: "Portfolio" },
];

/**
 * Footer links (e.g. Settings). Icon is chosen in NavBar by path.
 */
export const footerNavItems: { path: string; label: string }[] = [
  { path: "/settingspage", label: "Settings" },
];
