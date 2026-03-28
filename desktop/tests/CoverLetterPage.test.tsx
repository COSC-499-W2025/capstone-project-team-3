import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import { jest, describe, test, expect, beforeEach } from "@jest/globals";
import CoverLetterPage from "../src/pages/CoverLetterPage";
import * as resumeApi from "../src/api/resume";
import * as clApi from "../src/api/cover_letter";
import * as geminiApi from "../src/api/geminiKey";
import type { ResumeListItem } from "../src/api/resume";
import type { CoverLetterResponse, CoverLetterSummary } from "../src/api/cover_letter";
import type { GeminiKeyStatus } from "../src/api/geminiKey";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

jest.mock("../src/api/resume", () => ({ getResumes: jest.fn() }));

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

jest.mock("../src/api/geminiKey", () => ({ getGeminiKeyStatus: jest.fn() }));

jest.mock("../src/components/gemini/GeminiApiKeyModal", () => ({
  GeminiApiKeyModal: ({ open }: { open: boolean }) =>
    open ? <div data-testid="gemini-key-modal">Gemini Modal</div> : null,
}));

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const FAKE_RESUMES: ResumeListItem[] = [
  { id: 1, name: "Master Resume", is_master: true },
  { id: 2, name: "Backend Resume", is_master: false },
];

const GEMINI_VALID: GeminiKeyStatus = { configured: true, valid: true, masked_suffix: "abc123" };
const GEMINI_INVALID: GeminiKeyStatus = { configured: false, valid: false, masked_suffix: null };

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
  { id: 10, resume_id: 2, job_title: "Backend Engineer", company: "Acme Corp", generation_mode: "local", created_at: "2026-03-21T10:00:00" },
  { id: 11, resume_id: 2, job_title: "Full Stack Dev", company: "Beta Ltd", generation_mode: "ai", created_at: "2026-03-20T09:00:00" },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderPage() {
  return render(<BrowserRouter><CoverLetterPage /></BrowserRouter>);
}

/** Fill all required generate-form fields so the generate button is enabled. */
async function fillForm() {
  await waitFor(() => screen.getByTestId("cl-resume-select"));
  fireEvent.change(screen.getByTestId("cl-resume-select"), { target: { value: "2" } });
  fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "Backend Engineer" } });
  fireEvent.change(screen.getByTestId("cl-company"), { target: { value: "Acme Corp" } });
  fireEvent.change(screen.getByTestId("cl-job-description"), { target: { value: "Build scalable APIs for the platform." } });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("CoverLetterPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
    (resumeApi.getResumes as jest.MockedFunction<typeof resumeApi.getResumes>).mockResolvedValue(FAKE_RESUMES);
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>).mockResolvedValue([]);
    (geminiApi.getGeminiKeyStatus as jest.MockedFunction<typeof geminiApi.getGeminiKeyStatus>).mockResolvedValue(GEMINI_VALID);
  });

  // ── Basic rendering ────────────────────────────────────────────────

  test("renders page title and all three tabs", () => {
    renderPage();
    expect(screen.getByText("Cover Letter Generator")).toBeInTheDocument();
    expect(screen.getByTestId("cl-tab-generate")).toHaveAttribute("aria-current", "page");
    expect(screen.getByTestId("cl-tab-preview")).toBeInTheDocument();
    expect(screen.getByTestId("cl-tab-history")).toBeInTheDocument();
  });

  // ── Master resume excluded ─────────────────────────────────────────

  test("master resume is excluded from the resume dropdown", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));
    expect(screen.queryByText("Master Resume")).not.toBeInTheDocument();
    expect(screen.getByText("Backend Resume")).toBeInTheDocument();
  });

  // ── AI consent modal ───────────────────────────────────────────────

  test("clicking AI mode opens the consent modal without switching mode", () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    expect(screen.getByTestId("cl-ai-consent-modal")).toBeInTheDocument();
    expect(screen.getByTestId("cl-mode-local")).toHaveAttribute("aria-pressed", "true");
  });

  test("cancelling consent leaves mode as local and closes modal", () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-cancel"));
    expect(screen.queryByTestId("cl-ai-consent-modal")).not.toBeInTheDocument();
    expect(screen.getByTestId("cl-mode-local")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("cl-mode-ai")).toHaveAttribute("aria-pressed", "false");
  });

  test("accepting consent switches to AI mode and shows confirmation", () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-accept"));
    expect(screen.queryByTestId("cl-ai-consent-modal")).not.toBeInTheDocument();
    expect(screen.getByTestId("cl-mode-ai")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("cl-ai-consent-status")).toBeInTheDocument();
  });

  test("consent modal is not shown again once consent is accepted", () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-accept"));
    fireEvent.click(screen.getByTestId("cl-mode-local"));
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    expect(screen.queryByTestId("cl-ai-consent-modal")).not.toBeInTheDocument();
  });

  // ── API key warning ────────────────────────────────────────────────

  test("no key warning shown when key is valid and AI mode is selected", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-accept"));
    expect(screen.queryByTestId("cl-ai-key-missing")).not.toBeInTheDocument();
  });

  test("key warning shown when AI mode is selected and key is missing", async () => {
    (geminiApi.getGeminiKeyStatus as jest.MockedFunction<typeof geminiApi.getGeminiKeyStatus>).mockResolvedValue(GEMINI_INVALID);
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-accept"));
    await waitFor(() => expect(screen.getByTestId("cl-ai-key-missing")).toBeInTheDocument());
    expect(screen.getByText(/No valid Gemini API key/i)).toBeInTheDocument();
  });

  test("'Add API key' button opens the Gemini key modal", async () => {
    (geminiApi.getGeminiKeyStatus as jest.MockedFunction<typeof geminiApi.getGeminiKeyStatus>).mockResolvedValue(GEMINI_INVALID);
    renderPage();
    fireEvent.click(screen.getByTestId("cl-mode-ai"));
    fireEvent.click(screen.getByTestId("cl-ai-consent-accept"));
    await waitFor(() => screen.getByTestId("cl-ai-key-missing"));
    fireEvent.click(screen.getByRole("button", { name: /add api key/i }));
    expect(screen.getByTestId("gemini-key-modal")).toBeInTheDocument();
  });

  // ── Draft persistence (sessionStorage) ────────────────────────────

  test("form fields are restored from sessionStorage on mount", async () => {
    sessionStorage.setItem("cl-generate-draft", JSON.stringify({
      resumeId: 2, jobTitle: "Saved Title", company: "Saved Corp",
      jobDescription: "Saved description.", motivations: [], customMotivation: "", mode: "local",
    }));
    renderPage();
    await waitFor(() => screen.getByTestId("cl-job-title"));
    expect((screen.getByTestId("cl-job-title") as HTMLInputElement).value).toBe("Saved Title");
    expect((screen.getByTestId("cl-company") as HTMLInputElement).value).toBe("Saved Corp");
    expect((screen.getByTestId("cl-job-description") as HTMLTextAreaElement).value).toBe("Saved description.");
  });

  test("form fields are written to sessionStorage on change", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-job-title"));
    fireEvent.change(screen.getByTestId("cl-job-title"), { target: { value: "New Title" } });
    const stored = JSON.parse(sessionStorage.getItem("cl-generate-draft") ?? "{}");
    expect(stored.jobTitle).toBe("New Title");
  });

  // ── Generation flow ────────────────────────────────────────────────

  test("generate button disabled until all fields filled", async () => {
    renderPage();
    await waitFor(() => screen.getByTestId("cl-resume-select"));
    expect(screen.getByTestId("cl-generate-btn")).toBeDisabled();
    await fillForm();
    expect(screen.getByTestId("cl-generate-btn")).not.toBeDisabled();
  });

  test("shows error when generation fails", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockRejectedValue(new Error("Server error"));
    renderPage();
    await fillForm();
    fireEvent.click(screen.getByTestId("cl-generate-btn"));
    await waitFor(() => expect(screen.getByTestId("cl-error")).toHaveTextContent("Server error"));
  });

  test("switches to preview tab after successful generation", async () => {
    (clApi.generateCoverLetter as jest.MockedFunction<typeof clApi.generateCoverLetter>)
      .mockResolvedValue(FAKE_COVER_LETTER);
    renderPage();
    await fillForm();
    fireEvent.click(screen.getByTestId("cl-generate-btn"));
    await waitFor(() =>
      expect(screen.getByTestId("cl-tab-preview")).toHaveAttribute("aria-current", "page")
    );
  });

  // ── History tab ────────────────────────────────────────────────────

  test("history tab shows empty state when no letters saved", async () => {
    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));
    await waitFor(() => expect(screen.getByTestId("cl-history-empty")).toBeInTheDocument());
  });

  test("history tab shows saved letter cards", async () => {
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>)
      .mockResolvedValue(FAKE_HISTORY);
    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));
    await waitFor(() => expect(screen.getAllByTestId("cl-history-card")).toHaveLength(2));
  });

  test("deleting a history entry removes its card", async () => {
    (clApi.listCoverLetters as jest.MockedFunction<typeof clApi.listCoverLetters>)
      .mockResolvedValue(FAKE_HISTORY);
    (clApi.deleteCoverLetter as jest.MockedFunction<typeof clApi.deleteCoverLetter>)
      .mockResolvedValue({ success: true, deleted_id: 10 });
    window.confirm = jest.fn(() => true) as typeof window.confirm;

    renderPage();
    fireEvent.click(screen.getByTestId("cl-tab-history"));
    await waitFor(() => screen.getAllByTestId("cl-history-card"));
    fireEvent.click(screen.getAllByRole("button", { name: /delete cover letter/i })[0]);
    await waitFor(() => expect(screen.getAllByTestId("cl-history-card")).toHaveLength(1));
  });
});
