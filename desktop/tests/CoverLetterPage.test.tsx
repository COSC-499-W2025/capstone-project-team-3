import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import { jest, describe, test, expect, beforeEach } from "@jest/globals";
import CoverLetterPage from "../src/pages/CoverLetterPage";
import * as resumeApi from "../src/api/resume";
import * as clApi from "../src/api/cover_letter";
import type { ResumeListItem } from "../src/api/resume";
import type {
  CoverLetterResponse,
  CoverLetterSummary,
} from "../src/api/cover_letter";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

jest.mock("../src/api/resume", () => ({
  getResumes: jest.fn(),
}));

jest.mock("../src/api/cover_letter", () => ({
  generateCoverLetter: jest.fn(),
  listCoverLetters: jest.fn(),
  deleteCoverLetter: jest.fn(),
  getCoverLetter: jest.fn(),
  coverLetterPdfUrl: (id: number) => `http://localhost:8000/api/cover-letter/${id}/pdf`,
  MOTIVATION_OPTIONS: [
    { key: "strong_company_culture", label: "Strong Company Culture" },
    { key: "personal_growth", label: "Personal Growth & Career Advancement" },
    { key: "meaningful_work", label: "Meaningful Work" },
    { key: "reputation_stability", label: "Reputation & Stability" },
  ],
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const FAKE_RESUMES: ResumeListItem[] = [
  { id: 1, name: "Master Resume", is_master: true },
  { id: 2, name: "Backend Resume", is_master: false },
];

const FAKE_COVER_LETTER: CoverLetterResponse = {
  id: 10,
  resume_id: 2,
  job_title: "Backend Engineer",
  company: "Acme Corp",
  job_description: "Build scalable APIs.",
  motivations: ["meaningful_work"],
  content: "Dear Hiring Manager, this is a great letter.",
  generation_mode: "local",
  created_at: "2026-03-21T10:00:00",
};

const FAKE_HISTORY: CoverLetterSummary[] = [
  {
    id: 10,
    resume_id: 2,
    job_title: "Backend Engineer",
    company: "Acme Corp",
    generation_mode: "local",
    created_at: "2026-03-21T10:00:00",
  },
  {
    id: 11,
    resume_id: 2,
    job_title: "Full Stack Dev",
    company: "Beta Ltd",
    generation_mode: "ai",
    created_at: "2026-03-20T09:00:00",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage() {
  return render(
    <BrowserRouter>
      <CoverLetterPage />
    </BrowserRouter>
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("CoverLetterPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (resumeApi.getResumes as jest.MockedFunction<typeof resumeApi.getResumes>).mockResolvedValue(FAKE_RESUMES);
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>).mockResolvedValue([]);
  });

  // ── Rendering ─────────────────────────────────────────────────────

  test("renders page title", async () => {
    renderPage();
    expect(screen.getByText("Cover Letter Generator")).toBeInTheDocument();
  });

  test("renders all three tabs", async () => {
    renderPage();
    expect(screen.getByTestId("cl-tab-generate")).toBeInTheDocument();
    expect(screen.getByTestId("cl-tab-preview")).toBeInTheDocument();
    expect(screen.getByTestId("cl-tab-history")).toBeInTheDocument();
  });

  test("generate tab is active by default", () => {
    renderPage();
    const tab = screen.getByTestId("cl-tab-generate");
    expect(tab).toHaveAttribute("aria-current", "page");
  });

  // ── Generate tab ───────────────────────────────────────────────────

  test("shows resume dropdown with options after load", async () => {
    renderPage();
    await waitFor(() => {
      const select = screen.getByTestId("cl-resume-select");
      expect(select).toBeInTheDocument();
    });
    expect(screen.getByText("Master Resume")).toBeInTheDocument();
    expect(screen.getByText("Backend Resume")).toBeInTheDocument();
  });

  test("shows warning when no resumes are available", async () => {
    (resumeApi.getResumes as jest.MockedFunction<typeof resumeApi.getResumes>).mockResolvedValue([]);
    renderPage();
    await waitFor(() => {
      expect(
        screen.getByText(/no saved resumes found/i)
      ).toBeInTheDocument();
    });
  });

  test("generate button is disabled when fields are empty", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));
    const btn = screen.getByTestId("cl-generate-btn");
    expect(btn).toBeDisabled();
  });

  test("generate button enables when all required fields are filled", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));

    fireEvent.change(screen.getByTestId("cl-resume-select"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByTestId("cl-job-title"), {
      target: { value: "Engineer" },
    });
    fireEvent.change(screen.getByTestId("cl-company"), {
      target: { value: "Corp" },
    });
    fireEvent.change(screen.getByTestId("cl-job-description"), {
      target: { value: "Build amazing APIs for the platform." },
    });

    expect(screen.getByTestId("cl-generate-btn")).not.toBeDisabled();
  });

  test("renders all four motivation chips", async () => {
    renderPage();
    expect(screen.getByTestId("cl-motivation-strong_company_culture")).toBeInTheDocument();
    expect(screen.getByTestId("cl-motivation-personal_growth")).toBeInTheDocument();
    expect(screen.getByTestId("cl-motivation-meaningful_work")).toBeInTheDocument();
    expect(screen.getByTestId("cl-motivation-reputation_stability")).toBeInTheDocument();
  });

  test("toggling a motivation chip marks it selected", async () => {
    renderPage();
    const chip = screen.getByTestId("cl-motivation-meaningful_work");
    expect(chip).toHaveAttribute("aria-pressed", "false");
    fireEvent.click(chip);
    expect(chip).toHaveAttribute("aria-pressed", "true");
    // click again to deselect
    fireEvent.click(chip);
    expect(chip).toHaveAttribute("aria-pressed", "false");
  });

  test("mode cards: local selected by default", async () => {
    renderPage();
    expect(screen.getByTestId("cl-mode-local")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("cl-mode-ai")).toHaveAttribute("aria-pressed", "false");
  });

  test("clicking AI mode selects it", async () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    expect(screen.getByTestId("cl-mode-ai")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("cl-mode-local")).toHaveAttribute("aria-pressed", "false");
  });

  // ── Generation flow ────────────────────────────────────────────────

  test("shows error when generation fails", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockRejectedValue(new Error("Server error"));

    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));

    fireEvent.change(screen.getByTestId("cl-resume-select"), { target: { value: "2" } });
    fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "Engineer" } });
    fireEvent.change(screen.getByTestId("cl-company"), { target: { value: "Corp" } });
    fireEvent.change(screen.getByTestId("cl-job-description"), { target: { value: "Build APIs for the platform." } });

    fireEvent.click(screen.getByTestId("cl-generate-btn"));

    await waitFor(() => {
      expect(screen.getByTestId("cl-error")).toBeInTheDocument();
    });
    expect(screen.getByTestId("cl-error")).toHaveTextContent("Server error");
  });

  test("switches to preview tab after successful generation", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockResolvedValue(FAKE_COVER_LETTER);

    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));

    fireEvent.change(screen.getByTestId("cl-resume-select"), { target: { value: "2" } });
    fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "Backend Engineer" } });
    fireEvent.change(screen.getByTestId("cl-company"), { target: { value: "Acme Corp" } });
    fireEvent.change(screen.getByTestId("cl-job-description"), { target: { value: "Build scalable APIs for the platform." } });

    fireEvent.click(screen.getByTestId("cl-generate-btn"));

    await waitFor(() => {
      expect(screen.getByTestId("cl-tab-preview")).toHaveAttribute("aria-current", "page");
    });
  });

  // ── Preview tab ────────────────────────────────────────────────────

  test("preview tab shows placeholder when no letter generated", async () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-preview"));
    expect(screen.getByText(/no cover letter to preview/i)).toBeInTheDocument();
  });

  test("preview shows letter content after generation", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockResolvedValue(FAKE_COVER_LETTER);

    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));

    fireEvent.change(screen.getByTestId("cl-resume-select"), { target: { value: "2" } });
    fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "Backend Engineer" } });
    fireEvent.change(screen.getByTestId("cl-company"), { target: { value: "Acme Corp" } });
    fireEvent.change(screen.getByTestId("cl-job-description"), { target: { value: "Build scalable APIs for the platform." } });
    fireEvent.click(screen.getByTestId("cl-generate-btn"));

    await waitFor(() => screen.getByTestId("cl-preview-content"));
    expect(screen.getByTestId("cl-preview-content")).toHaveTextContent(
      "Dear Hiring Manager"
    );
  });

  test("regenerate button switches back to generate tab", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockResolvedValue(FAKE_COVER_LETTER);

    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));

    fireEvent.change(screen.getByTestId("cl-resume-select"), { target: { value: "2" } });
    fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "Engineer" } });
    fireEvent.change(screen.getByTestId("cl-company"), { target: { value: "Corp" } });
    fireEvent.change(screen.getByTestId("cl-job-description"), { target: { value: "Build scalable APIs for the platform." } });
    fireEvent.click(screen.getByTestId("cl-generate-btn"));

    await waitFor(() => screen.getByTestId("cl-regenerate-btn"));
    fireEvent.click(screen.getByTestId("cl-regenerate-btn"));

    expect(screen.getByTestId("cl-tab-generate")).toHaveAttribute("aria-current", "page");
  });

  // ── History tab ────────────────────────────────────────────────────

  test("history tab shows empty state when no letters saved", async () => {
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>).mockResolvedValue([]);

    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));

    await waitFor(() => {
      expect(screen.getByTestId("cl-history-empty")).toBeInTheDocument();
    });
  });

  test("history tab shows saved letters", async () => {
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>)
      .mockResolvedValue(FAKE_HISTORY);

    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));

    await waitFor(() => {
      expect(screen.getAllByTestId("cl-history-card")).toHaveLength(2);
    });
    expect(screen.getByText(/Backend Engineer/)).toBeInTheDocument();
    expect(screen.getByText(/Full Stack Dev/)).toBeInTheDocument();
  });

  test("deleting a history entry calls API and removes card", async () => {
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>)
      .mockResolvedValue(FAKE_HISTORY);
    (clApi.deleteCoverLetter as jest.MockedFunction<typeof clApi.deleteCoverLetter>)
      .mockResolvedValue({ success: true, deleted_id: 10 });

    window.confirm = jest.fn(() => true) as typeof window.confirm;

    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));

    await waitFor(() => screen.getAllByTestId("cl-history-card"));

    const deleteButtons = screen.getAllByRole("button", { name: /delete cover letter/i });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getAllByTestId("cl-history-card")).toHaveLength(1);
    });
  });
});
