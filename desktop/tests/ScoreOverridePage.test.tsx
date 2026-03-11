import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, jest, test } from "@jest/globals";
import "@testing-library/jest-dom";
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
    exclude_metrics: ["total_lines"],
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
        },
        subtotal: 0.102,
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
    render(<ScoreOverridePage />);

    await screen.findByText("Score Override");
    await selectProject();

    await screen.findByRole("heading", { name: "Score Preview" });
    expect(mockGetScoreBreakdown).toHaveBeenCalledWith("sig_alpha_project/hash");
    expect(screen.getByText("Total Commits", { selector: ".sor-metric-name" })).toBeInTheDocument();
  });

  test("toggles a metric and requests preview update", async () => {
    render(<ScoreOverridePage />);
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    const commitsCheckbox = getMetricCheckbox("Total Commits");
    await act(async () => {
      fireEvent.click(commitsCheckbox);
    });

    await waitFor(() =>
      expect(mockPreviewScoreOverride).toHaveBeenCalledWith(
        "sig_alpha_project/hash",
        expect.arrayContaining(["total_lines", "total_commits"])
      )
    );
    expect(await screen.findByText("+12.0%")).toBeInTheDocument();
  });

  test("applies override and refreshes breakdown", async () => {
    render(<ScoreOverridePage />);
    await selectProject();
    await screen.findByRole("heading", { name: "Score Preview" });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Apply Override" }));
    });

    await waitFor(() =>
      expect(mockApplyScoreOverride).toHaveBeenCalledWith("sig_alpha_project/hash", ["total_lines"])
    );
    await waitFor(() => expect(mockGetScoreBreakdown).toHaveBeenCalledTimes(2));
    expect(await screen.findByText("Score override applied successfully")).toBeInTheDocument();
  });

  test("clears override and refreshes breakdown", async () => {
    render(<ScoreOverridePage />);
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
    render(<ScoreOverridePage />);
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
        ["total_lines"]
      )
    );
  });
});
