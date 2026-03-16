import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { UploadPage } from "../src/pages/UploadPage";
import { test, expect, jest, beforeEach, afterEach } from "@jest/globals";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import * as uploadApi from "../src/api/upload";

jest.mock("../src/api/upload");

const mockUploadZipFile = uploadApi.uploadZipFile as jest.MockedFunction<
  typeof uploadApi.uploadZipFile
>;

const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;

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

    const similaritySelect = screen.getByLabelText(
      /Similarity action for proj-a/i,
    ) as HTMLSelectElement;
    expect(similaritySelect).toBeInTheDocument();
    expect(similaritySelect.value).toBe("create_new");
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

    expect(await screen.findByText(/Analysis complete/i)).toBeInTheDocument();
    expect(screen.getByText(/No file selected/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Upload a ZIP to load projects for configuration/i),
    ).toBeInTheDocument();
  });
});
