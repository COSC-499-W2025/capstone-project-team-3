import "../styles/UploadPage.css";

/**
 * Upload Page - Project upload interface
 */
export function UploadPage() {
  return (
    <div className="upload-container">
      <h1 className="upload-title">Upload Project to analyse</h1>
      <div className="upload-frame">
        <div className="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
