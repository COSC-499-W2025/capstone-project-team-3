import { beforeEach, describe, expect, jest, test } from "@jest/globals";
import {
  applyScoreOverride,
  clearScoreOverride,
  getScoreBreakdown,
  previewScoreOverride,
} from "../src/api/projects";

function mockJsonResponse(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    statusText: "OK",
    json: async () => body,
  } as Response;
}

function mockErrorResponse(status: number, statusText: string, body?: unknown): Response {
  return {
    ok: false,
    status,
    statusText,
    json: async () => body,
  } as Response;
}

describe("projects API score-override endpoints", () => {
  let fetchMock: jest.Mock;

  beforeEach(() => {
    fetchMock = jest.fn();
    global.fetch = fetchMock as unknown as typeof fetch;
  });

  test("encodes project signature for score breakdown endpoint", async () => {
    fetchMock.mockResolvedValue(
      mockJsonResponse({
        project_signature: "sig_alpha_project/hash",
      }),
    );

    await getScoreBreakdown("sig_alpha_project/hash");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(
      "http://localhost:8000/api/projects/sig_alpha_project%2Fhash/score-breakdown",
    );
  });

  test("encodes project signature for preview/apply/clear endpoints", async () => {
    fetchMock
      .mockResolvedValueOnce(mockJsonResponse({ preview_score: 0.9 }))
      .mockResolvedValueOnce(mockJsonResponse({ score: 0.9 }))
      .mockResolvedValueOnce(mockJsonResponse({}));

    await previewScoreOverride("sig_alpha_project/hash", ["total_lines"]);
    await applyScoreOverride("sig_alpha_project/hash", ["total_lines"]);
    await clearScoreOverride("sig_alpha_project/hash");

    expect(fetchMock.mock.calls[0][0]).toBe(
      "http://localhost:8000/api/projects/sig_alpha_project%2Fhash/score-override/preview",
    );
    expect(fetchMock.mock.calls[1][0]).toBe(
      "http://localhost:8000/api/projects/sig_alpha_project%2Fhash/score-override",
    );
    expect(fetchMock.mock.calls[2][0]).toBe(
      "http://localhost:8000/api/projects/sig_alpha_project%2Fhash/score-override/clear",
    );
  });

  test("surfaces backend validation detail when override preview fails", async () => {
    fetchMock.mockResolvedValue(
      mockErrorResponse(400, "Bad Request", {
        detail: "Unknown code metric exclusions: unknown_metric",
      }),
    );

    await expect(
      previewScoreOverride("sig_alpha_project/hash", ["unknown_metric"]),
    ).rejects.toThrow("Unknown code metric exclusions: unknown_metric");
  });
});
