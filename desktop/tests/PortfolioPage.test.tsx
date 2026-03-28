import {
  render,
  screen,
  waitFor,
  fireEvent,
  act,
  within,
} from "@testing-library/react";
import { test, expect, jest, beforeEach, describe } from "@jest/globals";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import PortfolioPage from "../src/pages/PortfolioPage";

// chart.js uses canvas APIs not available in jsdom — stub it out
jest.mock("chart.js/auto", () => {
  return jest.fn().mockImplementation(() => ({
    destroy: jest.fn(),
    update: jest.fn(),
  }));
});

beforeEach(() => {
  Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
    configurable: true,
    writable: true,
    value: jest.fn(() => ({})),
  });
});

// --- fixtures ----------------------------------------------------------------

const MOCK_PROJECTS = [
  {
    id: "proj1",
    name: "My Awesome App",
    title: "My Awesome App",
    score: 0.91,
    score_overridden: false,
    score_overridden_value: null,
    score_override_exclusions: [],
    dates: "Jan 2024 – Mar 2024",
    type: "GitHub",
    summary: "A well-tested web application with FastAPI and React.",
    thumbnail_url: "/api/portfolio/project/thumbnail/proj1",
    skills: ["Python", "React", "FastAPI"],
    metrics: {
      total_lines: 3200,
      total_commits: 42,
      test_files_changed: 5,
      functions: 38,
      classes: 12,
      components: 9,
      roles: ["Full-Stack Developer", "API Engineer"],
      development_patterns: { project_evolution: ["Iterative", "Refactoring"] },
      technical_keywords: ["CI/CD", "REST"],
      complexity_analysis: { maintainability_score: { overall_score: 78 } },
      commit_patterns: { commit_frequency: { development_intensity: "High" } },
      contribution_activity: { doc_type_counts: { README: 2, Wiki: 1 } },
    },
  },
  {
    id: "proj2",
    name: "CLI Toolbox",
    title: "CLI Toolbox",
    score: 0.74,
    score_overridden: true,
    score_overridden_value: 0.85,
    score_override_exclusions: ["test_files"],
    dates: "Apr 2024 – Jun 2024",
    type: "Local",
    summary: "Command-line utilities for data processing.",
    thumbnail_url: null,
    skills: ["Python", "Click"],
    metrics: {
      total_lines: 1500,
      total_commits: 18,
      roles: ["Backend Developer"],
      development_patterns: { project_evolution: [] },
    },
  },
];

const MOCK_PORTFOLIO = {
  user: {
    name: "Jane Dev",
    email: "jane@example.com",
    github_user: "janedev",
    links: [{ label: "GitHub", url: "https://github.com/janedev" }],
    education: "UBC Computer Science",
    job_title: "Software Engineer",
  },
  overview: {
    total_projects: 2,
    avg_score: 0.83,
    total_skills: 5,
    total_languages: 3,
    total_lines: 4700,
  },
  projects: MOCK_PROJECTS,
  skills_timeline: [{ skill: "Python", first_used: "2024-01-10", year: 2024 }],
  project_type_analysis: {
    github: { count: 1, stats: { avg_score: 0.91 } },
    local: { count: 1, stats: { avg_score: 0.74 } },
  },
  graphs: {
    language_distribution: { Python: 2, TypeScript: 1 },
    complexity_distribution: {
      distribution: { small: 1, medium: 1, large: 0 },
    },
    score_distribution: {
      distribution: { excellent: 1, good: 1, fair: 0, poor: 0 },
    },
    daily_activity: { "2024-01-10": 2, "2024-01-11": 1, "2024-01-12": 3 },
    monthly_activity: { "2024-01": 2, "2024-02": 1, "2024-03": 3 },
    top_skills: { Python: 2, React: 1, FastAPI: 1 },
  },
  metadata: {
    generated_at: "2024-07-01T10:00:00",
    total_projects: 2,
    filtered: false,
    project_ids: ["proj1", "proj2"],
  },
};

// --- helpers -----------------------------------------------------------------

function setupFetchMock(
  overrides: { projects?: unknown; portfolio?: unknown } = {},
) {
  const projectsPayload = overrides.projects ?? MOCK_PROJECTS;
  const portfolioPayload = overrides.portfolio ?? MOCK_PORTFOLIO;

  const mockFetch = jest.fn((url: RequestInfo | URL) => {
    const urlStr = url.toString();
    if (urlStr.includes("/api/portfolio/project/thumbnail")) {
      return Promise.resolve({
        ok: false,
        statusText: "Not Found",
      } as Response);
    }
    if (urlStr.includes("/api/projects")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(projectsPayload),
      } as Response);
    }
    if (urlStr.includes("/api/portfolio")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(portfolioPayload),
      } as Response);
    }
    return Promise.resolve({ ok: false, statusText: "Not Found" } as Response);
  });

  global.fetch = mockFetch as typeof fetch;
  return mockFetch;
}

function renderPortfolio() {
  window.history.pushState({}, "", "/");
  return render(
    <BrowserRouter>
      <PortfolioPage />
    </BrowserRouter>,
  );
}

function readBlobAsText(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsText(blob);
  });
}

// --- tests -------------------------------------------------------------------

describe("PortfolioPage – initial loading state", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("shows loading spinner before data arrives", () => {
    renderPortfolio();
    expect(screen.getByText(/loading portfolio data/i)).toBeDefined();
  });
});

describe("PortfolioPage – error state", () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        statusText: "Internal Server Error",
      } as Response),
    ) as typeof fetch;
  });

  test("renders error message and Retry button when API fails", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch projects/i)).toBeDefined();
    });
    expect(screen.getByText(/retry/i)).toBeDefined();
  });
});

describe("PortfolioPage – successful load", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("renders the dashboard heading", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/portfolio dashboard/i)).toBeDefined();
    });
  });

  test("renders Download Interactive HTML button", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/download interactive html/i)).toBeDefined();
    });
  });

  test("renders overview statistics", async () => {
    renderPortfolio();
    await waitFor(() => {
      // Total projects label is unique in the overview grid
      expect(screen.getByText(/total projects/i)).toBeDefined();
      // Average score value
      expect(screen.getByText("83%")).toBeDefined();
    });
  });

  test("renders Projects heading in sidebar", async () => {
    renderPortfolio();
    await waitFor(() => {
      // Sidebar <h2> reads "Projects" (not "Project Selection")
      const h2 = document.querySelector(".sidebar h2");
      expect(h2?.textContent).toMatch(/projects/i);
    });
  });

  test("renders both project names in the sidebar", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getAllByText("My Awesome App").length).toBeGreaterThan(0);
      expect(screen.getAllByText("CLI Toolbox").length).toBeGreaterThan(0);
    });
  });

  test("renders Select All button", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/select all|deselect all/i)).toBeDefined();
    });
  });

  test("calls /api/projects and /api/portfolio on mount", async () => {
    const mockFetch = setupFetchMock();
    renderPortfolio();
    await waitFor(() => {
      expect(screen.queryByText(/loading portfolio data/i)).toBeNull();
    });
    const urls = mockFetch.mock.calls.map((c) => c[0]?.toString() ?? "");
    expect(urls.some((u) => u.includes("/api/projects"))).toBe(true);
    expect(urls.some((u) => u.includes("/api/portfolio"))).toBe(true);
  });
});

describe("PortfolioPage – project cards", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("renders project title in card", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getAllByText("My Awesome App").length).toBeGreaterThan(0);
    });
  });

  test("renders role tags for a project", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText("Full-Stack Developer")).toBeDefined();
      expect(screen.getByText("API Engineer")).toBeDefined();
    });
  });

  test("renders score exclusion chip for overridden project", async () => {
    renderPortfolio();
    await waitFor(() => {
      // Exclusion keys are formatted: underscores → spaces, Title Case
      expect(screen.getByText("Test Files")).toBeDefined();
    });
  });

  test("shows overridden score value instead of raw score", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getAllByText("85%").length).toBeGreaterThan(0);
    });
  });

  test("renders thumbnail image with full API_BASE_URL src", async () => {
    renderPortfolio();
    await waitFor(() => {
      const img = document.querySelector(
        "img.project-thumbnail",
      ) as HTMLImageElement | null;
      expect(img).not.toBeNull();
      expect(img?.src).toContain(
        "http://localhost:8000/api/portfolio/project/thumbnail/proj1",
      );
    });
  });

  test("does not render thumbnail container when thumbnail_url is null", async () => {
    renderPortfolio();
    await waitFor(() => {
      // Only one thumbnail img should exist (proj2 has no thumbnail)
      const imgs = document.querySelectorAll("img.project-thumbnail");
      expect(imgs.length).toBe(1);
    });
  });

  test("renders percentage score and expandable score explainer", async () => {
    renderPortfolio();

    await waitFor(() => {
      expect(screen.getAllByText("91%").length).toBeGreaterThan(0);
    });

    const explainers = screen.getAllByText("Why this score?");
    const firstExplainer = explainers[0].closest("details");
    expect(firstExplainer).not.toBeNull();
    expect(firstExplainer).not.toHaveAttribute("open");

    fireEvent.click(explainers[0]);

    expect(firstExplainer).toHaveAttribute("open");
    expect(
      within(firstExplainer as HTMLElement).getByText("Repository Activity"),
    ).toBeInTheDocument();
    expect(
      within(firstExplainer as HTMLElement).getByText("Testing Evidence"),
    ).toBeInTheDocument();
  });

  test("explains adjusted scoring for overridden projects", async () => {
    renderPortfolio();

    const explainers = await screen.findAllByText("Why this score?");
    fireEvent.click(explainers[1]);

    expect(
      screen.getByText(
        /adjusted scoring is active for this project\. the current score excludes test files/i,
      ),
    ).toBeInTheDocument();
  });

  test("navigates to score override page with project preselected", async () => {
    renderPortfolio();

    const configureButtons = await screen.findAllByRole("button", {
      name: /configure score/i,
    });

    fireEvent.click(configureButtons[0]);

    await waitFor(() => {
      expect(window.location.pathname).toBe("/scoreoverridepage");
      expect(window.location.search).toContain("project=proj1");
      expect(window.location.search).toContain("from=portfoliopage");
    });
  });

  test("omits owner-only configure controls from exported HTML", async () => {
    setupFetchMock();

    let exportedBlob: Blob | null = null;
    const originalCreateObjectURL = URL.createObjectURL;
    const originalRevokeObjectURL = URL.revokeObjectURL;
    const createObjectURLMock = jest.fn((blob: Blob) => {
      exportedBlob = blob;
      return "blob:mock-export";
    });
    const revokeObjectURLMock = jest.fn();

    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      writable: true,
      value: createObjectURLMock,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      writable: true,
      value: revokeObjectURLMock,
    });

    const anchorClickSpy = jest
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {});

    try {
      renderPortfolio();

      const downloadButton = await screen.findByText(
        /download interactive html/i,
      );
      await act(async () => {
        fireEvent.click(downloadButton);
      });

      expect(exportedBlob).not.toBeNull();
      const exportedHtml = await readBlobAsText(exportedBlob!);
      expect(exportedHtml).toContain("Why this score?");
      expect(exportedHtml).not.toContain("Configure score");
    } finally {
      anchorClickSpy.mockRestore();
      Object.defineProperty(URL, "createObjectURL", {
        configurable: true,
        writable: true,
        value: originalCreateObjectURL,
      });
      Object.defineProperty(URL, "revokeObjectURL", {
        configurable: true,
        writable: true,
        value: originalRevokeObjectURL,
      });
    }
  });
});

describe("PortfolioPage – project selection interaction", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("toggles to Deselect All when all projects are selected", async () => {
    renderPortfolio();
    await waitFor(() => {
      // Once loaded and all selected, button should say Deselect All
      expect(screen.getByText(/deselect all/i)).toBeDefined();
    });
  });

  test("re-fetches portfolio when Select All clicked after deselecting", async () => {
    const mockFetch = setupFetchMock();
    renderPortfolio();

    // Wait for initial load to complete
    await waitFor(() => {
      expect(screen.queryByText(/loading portfolio data/i)).toBeNull();
    });

    // Click Deselect All
    const toggleBtn = screen.getByText(/deselect all/i);
    await act(async () => {
      fireEvent.click(toggleBtn);
    });

    // Now click Select All
    const selectBtn = screen.getByText(/select all/i);
    await act(async () => {
      fireEvent.click(selectBtn);
    });

    // Should have fetched /api/portfolio at least twice
    const portfolioFetches = mockFetch.mock.calls.filter((c) =>
      c[0]?.toString().includes("/api/portfolio"),
    );
    expect(portfolioFetches.length).toBeGreaterThanOrEqual(2);
  });
});

describe("PortfolioPage – graph section", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("renders Language Distribution graph card", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/language distribution/i)).toBeDefined();
    });
  });

  test("renders Monthly Activity graph card", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/monthly activity/i)).toBeDefined();
    });
  });

  test("canvas elements have expected IDs for Chart.js re-init", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(document.getElementById("languageChart")).not.toBeNull();
      expect(document.getElementById("complexityChart")).not.toBeNull();
      expect(document.getElementById("scoreChart")).not.toBeNull();
      expect(document.getElementById("activityChart")).not.toBeNull();
      expect(document.getElementById("skillsChart")).not.toBeNull();
      expect(document.getElementById("projectTypeChart")).not.toBeNull();
    });
  });
});

describe("PortfolioPage – analysis section", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("renders Detailed Analysis Insights heading", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/detailed analysis insights/i)).toBeDefined();
    });
  });

  test("renders score calculation formula section", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(
        screen.getAllByText(/calculation formula/i).length,
      ).toBeGreaterThan(0);
    });
  });
});

describe("PortfolioPage – user profile card", () => {
  beforeEach(() => {
    setupFetchMock();
  });

  test("renders the user's full name", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getAllByText("Jane Dev").length).toBeGreaterThan(0);
    });
  });

  test("renders avatar initials derived from the user name", async () => {
    renderPortfolio();
    await waitFor(() => {
      // "Jane Dev" → initials "JD"
      expect(screen.getByText("JD")).toBeDefined();
    });
  });

  test("renders job title", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText("Software Engineer")).toBeDefined();
    });
  });

  test("renders education string", async () => {
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/UBC Computer Science/i)).toBeDefined();
    });
  });

  test("renders email as a mailto link", async () => {
    renderPortfolio();
    await waitFor(() => {
      const link = document.querySelector(
        'a[href="mailto:jane@example.com"]',
      ) as HTMLAnchorElement | null;
      expect(link).not.toBeNull();
      expect(link?.textContent).toContain("jane@example.com");
    });
  });

  test("renders GitHub contact link", async () => {
    renderPortfolio();
    await waitFor(() => {
      const link = document.querySelector(
        'a[href="https://github.com/janedev"]',
      ) as HTMLAnchorElement | null;
      expect(link).not.toBeNull();
    });
  });

  test("falls back to 'Portfolio Owner' when name is empty", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: { ...MOCK_PORTFOLIO.user, name: "" },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText("Portfolio Owner")).toBeDefined();
    });
  });

  test("hides contacts section when no email and no GitHub link", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: { ...MOCK_PORTFOLIO.user, email: "", links: [] },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(document.querySelector(".profile-contacts")).toBeNull();
    });
  });

  test("parses education_details JSON and prefers it over plain education", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: {
          ...MOCK_PORTFOLIO.user,
          education: "Ignored plain string",
          education_details: JSON.stringify([
            { degree: "BSc Computer Science", institution: "UBC" },
          ]),
        },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/BSc Computer Science/i)).toBeDefined();
      expect(screen.queryByText(/Ignored plain string/i)).toBeNull();
    });
  });

  test("renders personal summary when provided", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: {
          ...MOCK_PORTFOLIO.user,
          personal_summary: "Passionate about building great software.",
        },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(
        screen.getByText(/Passionate about building great software/i),
      ).toBeDefined();
    });
  });
});

// --- GitHub Pages publishing -------------------------------------------------

describe("PortfolioPage – GitHub Pages publish button visibility", () => {
  test("shows publish button when github_user is set", async () => {
    setupFetchMock(); // MOCK_PORTFOLIO has github_user: "janedev"
    renderPortfolio();
    await waitFor(() => {
      expect(screen.getByText(/publish to github pages/i)).toBeDefined();
    });
  });

  test("hides publish button when github_user is empty", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: { ...MOCK_PORTFOLIO.user, github_user: "" },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(screen.queryByText(/publish to github pages/i)).toBeNull();
    });
  });

  test("hides publish button when github_user is absent", async () => {
    setupFetchMock({
      portfolio: {
        ...MOCK_PORTFOLIO,
        user: { ...MOCK_PORTFOLIO.user, github_user: undefined },
      },
    });
    renderPortfolio();
    await waitFor(() => {
      expect(screen.queryByText(/publish to github pages/i)).toBeNull();
    });
  });

  test("publish button is hidden (not rendered) when no projects are selected", async () => {
    setupFetchMock();
    renderPortfolio();

    // Deselect all projects — button is conditionally rendered only when projects are selected
    await waitFor(() => screen.getByText(/deselect all/i));
    await act(async () => {
      fireEvent.click(screen.getByText(/deselect all/i));
    });

    await waitFor(() => {
      // Button is removed from DOM when selectedProjects.size === 0
      expect(document.querySelector(".publish-github-pages-btn")).toBeNull();
    });
  });
});

describe("PortfolioPage – GitHub Pages publish modal", () => {
  beforeEach(() => {
    setupFetchMock(); // github_user is "janedev"
  });

  async function openModal() {
    renderPortfolio();
    const btn = await screen.findByTitle(/publish your portfolio to github pages/i);
    await act(async () => { fireEvent.click(btn); });
    await waitFor(() => expect(document.querySelector(".github-pages-modal")).not.toBeNull());
  }

  test("opens modal when publish button is clicked", async () => {
    await openModal();
    expect(screen.getByText(/publish to github pages/i, { selector: "h2,h3" })).toBeDefined();
  });

  test("modal shows the correct github.io URL for the user", async () => {
    await openModal();
    expect(screen.getByText(/janedev\.github\.io/i)).toBeDefined();
  });

  test("modal closes when overlay is clicked", async () => {
    await openModal();
    const overlay = document.querySelector(".github-pages-modal-overlay");
    expect(overlay).not.toBeNull();
    await act(async () => {
      fireEvent.click(overlay!);
    });
    expect(document.querySelector(".github-pages-modal")).toBeNull();
  });

  test("shows error state when publish API returns an error", async () => {
    global.fetch = jest.fn((url: RequestInfo | URL) => {
      const urlStr = url.toString();
      if (urlStr.includes("/api/portfolio/publish-github-pages")) {
        return Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ detail: "Invalid token" }),
        } as Response);
      }
      if (urlStr.includes("/api/projects"))
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_PROJECTS) } as Response);
      if (urlStr.includes("/api/portfolio"))
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_PORTFOLIO) } as Response);
      return Promise.resolve({ ok: false } as Response);
    }) as typeof fetch;

    renderPortfolio();
    // Wait until the publish button is rendered, then click it
    const openBtn = await screen.findByTitle(/publish your portfolio to github pages/i);
    await act(async () => { fireEvent.click(openBtn); });

    // Modal should now be open — fill in the token
    await waitFor(() => expect(document.querySelector(".github-pages-modal__input")).not.toBeNull());
    fireEvent.change(document.querySelector(".github-pages-modal__input")!, { target: { value: "bad_token" } });

    await act(async () => {
      fireEvent.click(document.querySelector(".github-pages-modal__publish-btn")!);
    });
    await waitFor(() => {
      expect(document.querySelector(".github-pages-modal__error")).not.toBeNull();
    });
  });

  test("shows success state with URL when publish succeeds", async () => {
    global.fetch = jest.fn((url: RequestInfo | URL) => {
      const urlStr = url.toString();
      if (urlStr.includes("/api/portfolio/publish-github-pages")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: "ok",
            url: "https://janedev.github.io",
            repo: "https://github.com/janedev/janedev.github.io",
            username: "janedev",
          }),
        } as Response);
      }
      if (urlStr.includes("/api/projects"))
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_PROJECTS) } as Response);
      if (urlStr.includes("/api/portfolio"))
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_PORTFOLIO) } as Response);
      return Promise.resolve({ ok: false } as Response);
    }) as typeof fetch;

    renderPortfolio();
    // Wait until the publish button is rendered, then click it
    const openBtn = await screen.findByTitle(/publish your portfolio to github pages/i);
    await act(async () => { fireEvent.click(openBtn); });

    // Modal should now be open — fill in the token
    await waitFor(() => expect(document.querySelector(".github-pages-modal__input")).not.toBeNull());
    fireEvent.change(document.querySelector(".github-pages-modal__input")!, { target: { value: "ghp_valid" } });

    await act(async () => {
      fireEvent.click(document.querySelector(".github-pages-modal__publish-btn")!);
    });
    await waitFor(() => {
      expect(document.querySelector(".github-pages-modal__success")).not.toBeNull();
    });
  });
});
