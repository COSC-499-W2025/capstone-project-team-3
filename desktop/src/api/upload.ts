import { API_BASE_URL } from "../config/api";

export interface UploadResponse {
  status: string;
  upload_id: string;
}

/**
 * Upload a ZIP file to the backend.
 * Reuses existing POST /upload-file endpoint - only .zip files are accepted.
 */
export async function uploadZipFile(file: File): Promise<UploadResponse> {
  if (!file.name.toLowerCase().endsWith(".zip")) {
    throw new Error("Please upload a ZIP file. Only .zip files are allowed.");
  }

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/upload-file`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Upload failed");
  }

  return res.json();
}
