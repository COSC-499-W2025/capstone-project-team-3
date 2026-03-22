import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, jest, test } from "@jest/globals";
import "@testing-library/jest-dom";
import { MemoryRouter } from "react-router-dom";
import ScoreOverridePage from "../src/pages/ScoreOverridePage";
import * as projectsApi from "../src/api/projects";

jest.mock("../src/api/projects");

const mockGetProjects = projectsApi.getProjects as jest.MockedFunction<
  typeof projectsApi.getProjects
>;
const mockGetScoreBreakdown = projectsApi.getScoreBreakdown as jest.MockedFunction<
  typeof projectsApi.getScoreBreakdown
>;
const mockPreviewScoreOverride = projectsApi.previewScoreOverride as jest.MockedFunction<
  typeof projectsApi.previewScoreOverride
>;
const mockApplyScoreOverride = projectsApi.applyScoreOverride as jest.MockedFunction<
  typeof projectsApi.applyScoreOverride
>;
const mockClearScoreOverride = projectsApi.clearScoreOverride as jest.MockedFunction<
  typeof projectsApi.clearScoreOverride
>;

const mockProjects: projectsApi.Project[] = [
  {
    id: "sig_alpha_project/hash",
    name: "Alpha Project",
    score: 0.7,
    skills: ["TypeScript"],
    date_added: "2026-01-01T00:00:00Z",
  },
];

function makeBreakdown(
  overrides: Partial<projectsApi.ScoreBreakdown> = {}
): projectsApi.ScoreBreakdown {
  return {
    project_signature: "sig_alpha_project/hash",
    name: "Alpha Project",
    score: 0.7,
    score_original: 0.7,
    score_overridden: true,
    score_overridden_value: 0.7,
    exclude_metrics: [],
    breakdown: {
      code: {
        type: "git",
        metrics: {
          total_commits: {
            raw: 10,
            cap: 100,
            normalized: 0.1,
            weight: 0.3,
            contribution: 0.03,
          },
          total_lines: {
            raw: 1200,
            cap: 5000,
            normalized: 0.24,
            weight: 0.3,
            contribution: 0.072,
          },
          code_files_changed: {
            raw: 5,
            cap: 20,
            normalized: 0.25,
            weight: 0.2,
            contribution: 0.05,
          },
        },
        subtotal: 0.152,
      },
      non_code: {
        metrics: {},
        subtotal: 0,
      },
      blend: {
        code_percentage: 1,
        non_code_percentage: 0,
        code_lines: 1200,
        doc_word_count: 0,
        doc_line_equiv: 0,
      },
      final_score: 0.7,
    },
    ...overrides,
  };
}

async function selectProject(): Promise<void> {
  const projectSelect = await screen.findByRole("combobox", { name: /Select Project/i });
  await act(async () => {
    fireEvent.change(projectSelect, { target: { value: "sig_alpha_project/hash" } });
  });
}

function getMetricCheckbox(metricLabel: string): HTMLInputElement {
  const metricName = screen.getByText(metricLabel, { selector: ".sor-metric-name" });
  const row = metricName.closest(".sor-metric-row");
  if (!row) throw new Error(`Could not find metric row for ${metricLabel}`);
  const checkbox = row.querySelector('input[type="checkbox"]');
  if (!checkbox) throw new Error(`Could not find checkbox for ${metricLabel}`);
  return checkbox as HTMLInputElement;
}

function renderPage(initialPath = "/scoreoverridepage"): void {
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <ScoreOverridePage />
    </MemoryRouter>
  );
}

describe("ScoreOverridePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockGetProjects.mockResolvedValue(mockProjects);
    mockGetScoreBreakdown.mockResolvedValue(makeBreakdown());
    mockPreviewScoreOverride.mockResolvedValue({
      project_signature: "sig_alpha_project/hash",
      name: "Alpha Project",
      exclude_metrics: [],
      current_score: 0.7,
      score_original: 0.7,
      preview_score: 0.82,
      breakdown: makeBreakdown().breakdown,
    });
    mockApplyScoreOverride.mockResolvedValue(makeBreakdown({ score: 0.82 }));
    mockClearScoreOverride.mockResolvedValue(undefined);
  });

  test("loads score breakdown after project selection", async () => {
    renderPage();

    await screen.findByText("Score Override");
    await selectProject();

    await screen.findByRole("heading", { name: "Score Preview" });
    expect(mockGetScoreBreakdown).toHaveBeenCalledWith("sig_alpha_project/hash");
    expect(screen.getByText("Total Commits", { selector: ".sor-metric-name" })).toBeInTheDocument();
  });

  test("toggles a metric and requests preview update", async () => {
    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    const commitsCheckbox = getMetricCheckbox("Total Commits");
    await act(async () => {
      fireEvent.click(commitsCheckbox);
    });

    await waitFor(() =>
      expect(mockPreviewScoreOverride).toHaveBeenCalledWith(
        "sig_alpha_project/hash",
        expect.arrayContaining(["total_commits"])
      )
    );
    expect(await screen.findByText("+12.0%")).toBeInTheDocument();
  });

  test("applies override and refreshes breakdown", async () => {
    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Apply Override" }));
    });

    await waitFor(() =>
      expect(mockApplyScoreOverride).toHaveBeenCalledWith("sig_alpha_project/hash", [])
    );
    await waitFor(() => expect(mockGetScoreBreakdown).toHaveBeenCalledTimes(2));
    expect(await screen.findByText("Score override applied successfully")).toBeInTheDocument();
  });

  test("clears override and refreshes breakdown", async () => {
    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Clear Override" }));
    });

    await waitFor(() =>
      expect(mockClearScoreOverride).toHaveBeenCalledWith("sig_alpha_project/hash")
    );
    await waitFor(() => expect(mockGetScoreBreakdown).toHaveBeenCalledTimes(2));
    expect(
      await screen.findByText("Score override cleared — original score restored")
    ).toBeInTheDocument();
  });

  test("reset restores original exclusions and recalculates preview", async () => {
    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    const commitsCheckbox = getMetricCheckbox("Total Commits");
    await act(async () => {
      fireEvent.click(commitsCheckbox);
    });
    await waitFor(() => expect(mockPreviewScoreOverride).toHaveBeenCalledTimes(1));

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    });

    await waitFor(() =>
      expect(mockPreviewScoreOverride).toHaveBeenLastCalledWith(
        "sig_alpha_project/hash",
        []
      )
    );
  });

  test("preselects the requested project when opened from portfolio", async () => {
    renderPage("/scoreoverridepage?project=sig_alpha_project%2Fhash&from=portfoliopage");

    await waitFor(() =>
      expect(mockGetScoreBreakdown).toHaveBeenCalledWith("sig_alpha_project/hash")
    );
  });

  test("always shows back button regardless of entry path", async () => {
    renderPage();

    const backButton = await screen.findByRole("button", { name: /go back/i });
    expect(backButton).toBeInTheDocument();
    expect(backButton).toHaveTextContent("Back");
  });

  test("shows info banner when project has no code metrics", async () => {
    mockGetScoreBreakdown.mockResolvedValue(
      makeBreakdown({
        breakdown: {
          code: { type: "git", metrics: {}, subtotal: 0 },
          non_code: { metrics: {}, subtotal: 0 },
          blend: {
            code_percentage: 1,
            non_code_percentage: 0,
            code_lines: 0,
            doc_word_count: 0,
            doc_line_equiv: 0,
          },
          final_score: 0,
        },
      })
    );

    renderPage();
    await selectProject();

    expect(await screen.findByText("No code metrics available")).toBeInTheDocument();
    expect(
      screen.getByText(/does not have overrideable code metrics/i)
    ).toBeInTheDocument();
  });

  test("shows info banner when breakdown fails to load", async () => {
    mockGetScoreBreakdown.mockRejectedValue(new Error("Server error"));

    renderPage();
    await selectProject();

    expect(await screen.findByText("Unable to load score breakdown")).toBeInTheDocument();
  });

  test("shows saturation note when all remaining metrics are at max", async () => {
    mockGetScoreBreakdown.mockResolvedValue(
      makeBreakdown({
        exclude_metrics: [],
        breakdown: {
          code: {
            type: "git",
            metrics: {
              total_commits: {
                raw: 100,
                cap: 50,
                normalized: 1.0,
                weight: 0.5,
                contribution: 0.5,
              },
              total_lines: {
                raw: 10000,
                cap: 5000,
                normalized: 1.0,
                weight: 0.5,
                contribution: 0.5,
              },
            },
            subtotal: 1.0,
          },
          non_code: { metrics: {}, subtotal: 0 },
          blend: {
            code_percentage: 1,
            non_code_percentage: 0,
            code_lines: 10000,
            doc_word_count: 0,
            doc_line_equiv: 0,
          },
          final_score: 1.0,
        },
      })
    );

    mockPreviewScoreOverride.mockResolvedValue({
      project_signature: "sig_alpha_project/hash",
      name: "Alpha Project",
      exclude_metrics: ["total_lines"],
      current_score: 1.0,
      preview_score: 1.0,
      breakdown: makeBreakdown().breakdown,
    });

    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    const linesCheckbox = getMetricCheckbox("Lines of Code");
    await act(async () => {
      fireEvent.click(linesCheckbox);
    });

    expect(
      await screen.findByText(
        /all remaining metrics are at 100%/i
      )
    ).toBeInTheDocument();
  });

  test("prevents excluding the last remaining code metric", async () => {
    mockGetScoreBreakdown.mockResolvedValue(
      makeBreakdown({
        exclude_metrics: ["total_lines", "code_files_changed"],
      })
    );

    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    // total_lines and code_files_changed are already excluded, try to also exclude total_commits (the last one)
    const commitsCheckbox = getMetricCheckbox("Total Commits");
    await act(async () => {
      fireEvent.click(commitsCheckbox);
    });

    expect(
      await screen.findByText(/at least one code metric must remain/i)
    ).toBeInTheDocument();

    // Preview should NOT have been called for this toggle
    expect(mockPreviewScoreOverride).not.toHaveBeenCalled();
  });

  test("displays hint text about code metric rules and documentation metrics", async () => {
    renderPage();
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    expect(
      screen.getByText(/only code metrics can be excluded/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/at least one must remain included/i)
    ).toBeInTheDocument();
  });
});
