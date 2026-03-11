import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadZipFile } from "../api/upload";
import "../styles/UploadPage.css";

/**
 * Upload Page - Project upload interface
 * Select or drop a ZIP file to auto-upload. File is stored in app/uploads.
 */
export function UploadPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    setUploadedFileName(null);

    try {
      const result = await uploadZipFile(file);
      setSuccess(true);
      setUploadedFileName(file.name);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      navigate("/analysisrunnerpage", {
        state: { uploadId: result.upload_id },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedFileName(null);
    setSuccess(false);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const ZIP_ERROR = "Please upload a ZIP file. Only .zip files are allowed.";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError(ZIP_ERROR);
      e.target.value = "";
      return;
    }

    uploadFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (loading) return;
    const file = e.dataTransfer.files?.[0];
    if (file && file.name.toLowerCase().endsWith(".zip")) {
      setError(null);
      uploadFile(file);
    } else if (file) {
      setError(ZIP_ERROR);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = loading ? "none" : "copy";
  };

  const handleZoneClick = () => {
    if (!loading) fileInputRef.current?.click();
  };

  return (
    <div className="upload-container">
      <h1 className="upload-title">Upload Project to analyse</h1>
      <div
        className={`upload-frame${loading ? " upload-frame--loading" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleZoneClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) =>
          e.key === "Enter" && !loading && fileInputRef.current?.click()
        }
        aria-label="Drop or click to select ZIP file"
      >
        <div className="upload-content">
          <div className="upload-icon">
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          {uploadedFileName ? (
            <>
              <p className="upload-uploaded">Uploaded: {uploadedFileName}</p>
              <button
                type="button"
                className="upload-remove-button"
                onClick={handleRemove}
                aria-label="Remove uploaded file"
              >
                Remove
              </button>
            </>
          ) : (
            <p className="upload-hint">
              {loading
                ? "Uploading…"
                : "Drop your ZIP file here or click to browse"}
            </p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={handleFileChange}
            className="upload-file-input"
            aria-label="Select ZIP file"
            disabled={loading}
          />
        </div>
      </div>

      {error && (
        <div className="upload-error" role="alert">
          {error}
        </div>
      )}

      {success && !loading && (
        <div className="upload-success">
          <p>Upload successful. Your file has been saved.</p>
        </div>
      )}
    </div>
  );
}

export default UploadPage;
