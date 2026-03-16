export const METRIC_LABELS: Record<string, string> = {
  total_commits: "Total Commits",
  duration_days: "Project Duration",
  total_lines: "Lines of Code",
  code_files_changed: "Code Files",
  test_files_changed: "Test Files",
  total_files: "Total Files",
  maintainability_score: "Maintainability",
  completeness_score: "Documentation Completeness",
};

export const METRIC_DESCRIPTIONS: Record<string, string> = {
  total_commits: "Number of git commits in the project history",
  duration_days: "Time span from first to last commit",
  total_lines: "Total lines of code across all source files",
  code_files_changed: "Number of source code files modified",
  test_files_changed: "Number of test files present",
  total_files: "Total number of files in the project",
  maintainability_score: "Code maintainability index (0–100)",
  completeness_score: "Documentation completeness ratio",
};
