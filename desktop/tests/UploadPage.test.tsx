import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { UploadPage } from "../src/pages/UploadPage";
import { test, expect, jest, beforeEach, afterEach } from "@jest/globals";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import * as uploadApi from "../src/api/upload";

jest.mock("../src/api/upload");
jest.mock("../src/api/geminiKey", () => ({
  getGeminiKeyStatus: jest.fn().mockResolvedValue({
    configured: true,
    valid: true,
    masked_suffix: null,
  }),
}));

const mockUploadZipFile = uploadApi.uploadZipFile as jest.MockedFunction<
  typeof uploadApi.uploadZipFile
>;

const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;

/** Pre-scan response: no exact match, no similar project → proceeds without modal. */
const scanProjectNoSimilarityResponse = {
  ok: true,
  json: async () => ({
    status: "ok",
    file_count: 5,
    eligible_file_count: 5,
    total_scanned_files: 5,
    similarity: null,
    reason: "no_match",
  }),
} as Response;

describe("UploadPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = mockFetch;
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("renders unified upload and analysis page", () => {
    render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    expect(screen.getByText(/Upload & Run Analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Choose ZIP file/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Upload a ZIP to load projects for configuration/i),
    ).toBeInTheDocument();
  });

  test("selecting non-zip file shows error", () => {
    const { container } = render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    const file = new File(["content"], "test.txt", { type: "text/plain" });
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText(/Please upload a ZIP file/i)).toBeInTheDocument();
  });

  test("uploading zip loads projects and enables per-project similarity selection", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        projects: [{ name: "proj-a", path: "/tmp/proj-a" }],
      }),
    } as Response);

    const { container } = render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    const file = new File(["content"], "project.zip", { type: "application/zip" });
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(await screen.findByText("project.zip")).toBeInTheDocument();
    expect(await screen.findByText("proj-a")).toBeInTheDocument();

    const analysisTypeSelect = screen.getByLabelText(
      /Analysis type for proj-a/i,
    ) as HTMLSelectElement;
    expect(analysisTypeSelect).toBeInTheDocument();
    expect(analysisTypeSelect.value).toBe("local");
  });

  test("selecting AI prompts consent modal and applies AI after acceptance", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "xyz-789" });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        projects: [{ name: "proj-a", path: "/tmp/proj-a" }],
      }),
    } as Response);

    const { container } = render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    const file = new File(["content"], "project.zip", { type: "application/zip" });
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });

    await screen.findByText("proj-a");

    const defaultModeSelect = screen.getByLabelText(/Default Analysis Type/i);
    fireEvent.change(defaultModeSelect, { target: { value: "ai" } });

    expect(await screen.findByText(/AI consent required/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /I understand, continue with AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/AI consent accepted for this upload session/i)).toBeInTheDocument();
    });

    expect((screen.getByLabelText(/Default Analysis Type/i) as HTMLSelectElement).value).toBe("ai");
  });

  test("Exclude Types column appears after project load", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ projects: [{ name: "proj-a", path: "/tmp/proj-a" }] }),
    } as Response);

    const { container } = render(<BrowserRouter><UploadPage /></BrowserRouter>);
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [new File(["x"], "p.zip", { type: "application/zip" })] } });

    await screen.findByText("proj-a");
    expect(screen.getByText(/Exclude Types/i)).toBeInTheDocument();
  });

  test("clicking exclude button opens file type panel with Markdown and README options", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ projects: [{ name: "proj-a", path: "/tmp/proj-a" }] }),
    } as Response);

    const { container } = render(<BrowserRouter><UploadPage /></BrowserRouter>);
    fireEvent.change(
      container.querySelector("input[type='file']") as HTMLInputElement,
      { target: { files: [new File(["x"], "p.zip", { type: "application/zip" })] } },
    );
    await screen.findByText("proj-a");

    fireEvent.click(screen.getByLabelText(/Exclude file types for proj-a/i));
    expect(await screen.findByLabelText(/Markdown/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/README files/i)).toBeInTheDocument();
  });

  test("checking file types sends project_exclude_extensions in analysis payload", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ projects: [{ name: "proj-a", path: "/tmp/proj-a" }] }),
      } as Response)
      .mockResolvedValueOnce(scanProjectNoSimilarityResponse)
      .mockResolvedValueOnce(scanProjectNoSimilarityResponse)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ analyzed_projects: 1, skipped_projects: 0, failed_projects: 0 }),
      } as Response);

    const { container } = render(<BrowserRouter><UploadPage /></BrowserRouter>);
    fireEvent.change(
      container.querySelector("input[type='file']") as HTMLInputElement,
      { target: { files: [new File(["x"], "p.zip", { type: "application/zip" })] } },
    );
    await screen.findByText("proj-a");

    fireEvent.click(screen.getByLabelText(/Exclude file types for proj-a/i));
    fireEvent.click(await screen.findByLabelText(/Markdown/i));
    fireEvent.click(screen.getByRole("button", { name: /Run Analysis/i }));

    await screen.findByText(/Analysis complete/i, { selector: ".ar-result strong" });
    const runCall = mockFetch.mock.calls.find((c) =>
      String(c[0]).includes("/api/analysis/run"),
    );
    expect(runCall).toBeDefined();
    const body = JSON.parse((runCall![1] as RequestInit).body as string);
    expect(body.project_exclude_extensions["/tmp/proj-a"]).toContain(".md");
  });

  test("result banner shows all-files-excluded note for affected projects", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ projects: [{ name: "proj-a", path: "/tmp/proj-a" }] }),
      } as Response)
      .mockResolvedValueOnce(scanProjectNoSimilarityResponse)
      .mockResolvedValueOnce(scanProjectNoSimilarityResponse)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          analyzed_projects: 0,
          skipped_projects: 1,
          failed_projects: 0,
          results: [
            { project_name: "proj-a", status: "skipped", reason: "all_files_excluded" },
          ],
        }),
      } as Response);

    const { container } = render(<BrowserRouter><UploadPage /></BrowserRouter>);
    fireEvent.change(
      container.querySelector("input[type='file']") as HTMLInputElement,
      { target: { files: [new File(["x"], "p.zip", { type: "application/zip" })] } },
    );
    await screen.findByText("proj-a");
    fireEvent.click(screen.getByRole("button", { name: /Run Analysis/i }));

    expect(
      await screen.findByText(/Analysis complete/i, { selector: ".ar-result strong" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/all files were excluded by your filters/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText("proj-a", { selector: ".ar-result-excluded-note strong" }),
    ).toBeInTheDocument();
  });

  test("similarity detected → modal → choose Update → project_similarity_actions included in run payload", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });

    const scanProjectSimilarityResponse = {
      ok: true,
      json: async () => ({
        status: "ok",
        file_count: 5,
        eligible_file_count: 5,
        total_scanned_files: 5,
        similarity: {
          jaccard_similarity: 75.5,
          containment_ratio: 82.3,
          matched_project_name: "Existing Project",
          match_reason: "high_overlap",
        },
        reason: "similar_match",
      }),
    } as Response;

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          projects: [{ name: "proj-a", path: "/tmp/proj-a" }],
        }),
      } as Response)
      .mockResolvedValueOnce(scanProjectSimilarityResponse)
      .mockResolvedValueOnce(scanProjectSimilarityResponse)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          analyzed_projects: 1,
          skipped_projects: 0,
          failed_projects: 0,
        }),
      } as Response);

    const { container } = render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    const file = new File(["content"], "project.zip", { type: "application/zip" });
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });

    await screen.findByText("proj-a");

    fireEvent.click(screen.getByRole("button", { name: /Run Analysis/i }));

    const modal = await screen.findByRole("dialog", { name: /Similarity detected/i });
    expect(modal).toBeInTheDocument();
    expect(within(modal).getByText(/Similar Project Detected/i)).toBeInTheDocument();
    expect(within(modal).getByText(/75\.5%/)).toBeInTheDocument();
    expect(within(modal).getByText(/82\.3%/)).toBeInTheDocument();

    fireEvent.click(
      within(modal).getByRole("button", { name: /Update "Existing Project"/i }),
    );

    await waitFor(() => {
      expect(
        mockFetch.mock.calls.some((c) => String(c[0]).includes("/api/analysis/run")),
      ).toBe(true);
    });

    const runCall = mockFetch.mock.calls.find((c) =>
      String(c[0]).includes("/api/analysis/run"),
    );
    const body = JSON.parse((runCall![1] as RequestInit).body as string);
    expect(body.project_similarity_actions["/tmp/proj-a"]).toBe("update_existing");
    expect(body.project_similarity_actions["proj-a"]).toBe("update_existing");
  });

  test("successful run clears upload form state to avoid stale upload_id reruns", async () => {
    mockUploadZipFile.mockResolvedValue({ status: "ok", upload_id: "abc-123" });

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          projects: [{ name: "proj-a", path: "/tmp/proj-a" }],
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: "ok",
          file_count: 5,
          eligible_file_count: 5,
          total_scanned_files: 5,
          similarity: null,
          reason: "no_match",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: "ok",
          file_count: 5,
          eligible_file_count: 5,
          total_scanned_files: 5,
          similarity: null,
          reason: "no_match",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          analyzed_projects: 1,
          skipped_projects: 0,
          failed_projects: 0,
        }),
      } as Response);

    const { container } = render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>,
    );

    const file = new File(["content"], "project.zip", { type: "application/zip" });
    const fileInput = container.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });

    await screen.findByText("proj-a");
    fireEvent.click(screen.getByRole("button", { name: /Run Analysis/i }));

    expect(await screen.findByText(/1 analyzed/i)).toBeInTheDocument();
    expect(screen.getByText("project.zip")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Analysis Complete/i })).toBeDisabled();
  });
});
