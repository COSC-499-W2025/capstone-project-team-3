import { useState, useEffect, useCallback } from "react";
import { getResumes, type ResumeListItem } from "../api/resume";
import {
  generateCoverLetter,
  listCoverLetters,
  deleteCoverLetter,
  updateCoverLetter,
  coverLetterPdfUrl,
  MOTIVATION_OPTIONS,
  type CoverLetterResponse,
  type CoverLetterSummary,
  type GenerationMode,
} from "../api/cover_letter";
import "../styles/CoverLetterPage.css";

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StepHeader({ step, title }: { step: number; title: string }) {
  return (
    <div className="cl-step-header">
      <span className="cl-step-badge">{step}</span>
      <h2 className="cl-step-title">{title}</h2>
    </div>
  );
}

function ModeBadge({ mode }: { mode: GenerationMode }) {
  return (
    <span className={`cl-badge cl-badge--${mode}`}>
      {mode === "ai" ? "🤖 AI Generated" : "📄 Local Template"}
    </span>
  );
}

// ---------------------------------------------------------------------------
// History card
// ---------------------------------------------------------------------------

function HistoryCard({
  entry,
  onView,
  onDelete,
}: {
  entry: CoverLetterSummary;
  onView: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const date = new Date(entry.created_at).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="cl-history-card" data-testid="cl-history-card">
      <div className="cl-history-card-info">
        <span className="cl-history-card-title">
          {entry.job_title} — {entry.company}
        </span>
        <span className="cl-history-card-sub">
          <ModeBadge mode={entry.generation_mode} /> &nbsp;·&nbsp; {date}
        </span>
      </div>
      <div className="cl-history-card-actions">
        <button
          className="cl-btn cl-btn--secondary"
          onClick={() => onView(entry.id)}
        >
          View
        </button>
        <a
          className="cl-btn cl-btn--secondary"
          href={coverLetterPdfUrl(entry.id)}
          download
        >
          PDF
        </a>
        <button
          className="cl-btn cl-btn--danger"
          onClick={() => onDelete(entry.id)}
          aria-label={`Delete cover letter for ${entry.job_title} at ${entry.company}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Generate tab
// ---------------------------------------------------------------------------

interface GenerateTabProps {
  resumes: ResumeListItem[];
  onGenerated: (cl: CoverLetterResponse) => void;
}

function GenerateTab({ resumes, onGenerated }: GenerateTabProps) {
  const [resumeId, setResumeId] = useState<number | "">("");
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [motivations, setMotivations] = useState<string[]>([]);
  const [customMotivation, setCustomMotivation] = useState("");
  const [mode, setMode] = useState<GenerationMode>("local");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const savedResumes = resumes.filter((r) => r.id !== null);

  function toggleMotivation(key: string) {
    setMotivations((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  }

  async function handleGenerate() {
    if (!resumeId || !jobTitle.trim() || !company.trim() || !jobDescription.trim()) {
      setError("Please fill in all required fields and select a resume.");
      return;
    }
    setError(null);
    setLoading(true);
    // Combine preset keys + trimmed custom motivation (if provided)
    const allMotivations = customMotivation.trim()
      ? [...motivations, customMotivation.trim()]
      : motivations;
    try {
      const result = await generateCoverLetter({
        resume_id: resumeId as number,
        job_title: jobTitle.trim(),
        company: company.trim(),
        job_description: jobDescription.trim(),
        motivations: allMotivations,
        mode,
      });
      onGenerated(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const canGenerate =
    resumeId !== "" && jobTitle.trim() && company.trim() && jobDescription.trim();

  return (
    <div className="cl-card">
      {/* Step 1 — Resume */}
      <section>
        <StepHeader step={1} title="Select a Saved Resume" />
        <div className="cl-field">
          <label className="cl-label" htmlFor="cl-resume-select">
            Resume <span aria-hidden>*</span>
          </label>
          <select
            id="cl-resume-select"
            className="cl-select"
            value={resumeId}
            onChange={(e) =>
              setResumeId(e.target.value === "" ? "" : Number(e.target.value))
            }
            data-testid="cl-resume-select"
          >
            <option value="">— Choose a resume —</option>
            {savedResumes.map((r) => (
              <option key={r.id} value={r.id!}>
                {r.name}
              </option>
            ))}
          </select>
          {savedResumes.length === 0 && (
            <p className="cl-error" role="alert">
              No saved resumes found. Please create a resume first on the Resume
              page.
            </p>
          )}
        </div>
      </section>

      {/* Step 2 — Job details */}
      <section>
        <StepHeader step={2} title="Job Details" />
        <div className="cl-row">
          <div className="cl-field">
            <label className="cl-label" htmlFor="cl-job-title">
              Role Title <span aria-hidden>*</span>
            </label>
            <input
              id="cl-job-title"
              className="cl-input"
              type="text"
              placeholder="e.g. Backend Engineer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              data-testid="cl-job-title"
            />
          </div>
          <div className="cl-field">
            <label className="cl-label" htmlFor="cl-company">
              Company <span aria-hidden>*</span>
            </label>
            <input
              id="cl-company"
              className="cl-input"
              type="text"
              placeholder="e.g. Acme Corp"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              data-testid="cl-company"
            />
          </div>
        </div>
        <div className="cl-field" style={{ marginTop: "1rem" }}>
          <label className="cl-label" htmlFor="cl-jd">
            Job Description <span aria-hidden>*</span>
          </label>
          <textarea
            id="cl-jd"
            className="cl-textarea"
            placeholder="Paste the full job description here…"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            data-testid="cl-job-description"
          />
        </div>
      </section>

      {/* Step 3 — Motivations */}
      <section>
        <StepHeader step={3} title="Why This Role? (Optional)" />
        <div className="cl-motivation-grid" role="group" aria-label="Motivations">
          {MOTIVATION_OPTIONS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              className={`cl-motivation-chip${
                motivations.includes(key) ? " cl-motivation-chip--selected" : ""
              }`}
              onClick={() => toggleMotivation(key)}
              aria-pressed={motivations.includes(key)}
              data-testid={`cl-motivation-${key}`}
            >
              {motivations.includes(key) ? "✓ " : ""}
              {label}
            </button>
          ))}
        </div>
        <div className="cl-field" style={{ marginTop: "0.75rem" }}>
          <label className="cl-label" htmlFor="cl-custom-motivation">
            Custom motivation (optional)
          </label>
          <input
            id="cl-custom-motivation"
            className="cl-input"
            type="text"
            placeholder="e.g. the team's focus on open-source contributions"
            value={customMotivation}
            onChange={(e) => setCustomMotivation(e.target.value)}
            data-testid="cl-custom-motivation"
          />
        </div>
      </section>

      {/* Step 4 — Generation mode */}
      <section>
        <StepHeader step={4} title="Generation Mode" />
        <div className="cl-mode-grid">
          <button
            type="button"
            className={`cl-mode-card${mode === "local" ? " cl-mode-card--selected" : ""}`}
            onClick={() => setMode("local")}
            aria-pressed={mode === "local"}
            data-testid="cl-mode-local"
          >
            <span className="cl-mode-card-title">📄 Local Template</span>
            <p className="cl-mode-card-desc">
              Fast, offline generation. Works without an API key.
            </p>
          </button>
          <button
            type="button"
            className={`cl-mode-card${mode === "ai" ? " cl-mode-card--selected" : ""}`}
            onClick={() => setMode("ai")}
            aria-pressed={mode === "ai"}
            data-testid="cl-mode-ai"
          >
            <span className="cl-mode-card-title">🤖 AI Generated</span>
            <p className="cl-mode-card-desc">
              Uses Gemini to write a tailored, personalised letter. Requires an
              API key.
            </p>
          </button>
        </div>
      </section>

      {error && (
        <p className="cl-error" role="alert" data-testid="cl-error">
          {error}
        </p>
      )}

      <div className="cl-actions">
        <button
          className="cl-btn cl-btn--primary"
          onClick={handleGenerate}
          disabled={!canGenerate || loading}
          data-testid="cl-generate-btn"
        >
          {loading && <span className="cl-spinner" aria-hidden />}
          {loading ? "Generating…" : "Generate Cover Letter"}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Preview tab
// ---------------------------------------------------------------------------

interface PreviewTabProps {
  coverLetter: CoverLetterResponse;
  onRegenerate: () => void;
  onSaved: (updated: CoverLetterResponse) => void;
}

function PreviewTab({ coverLetter, onRegenerate, onSaved }: PreviewTabProps) {
  const [editedContent, setEditedContent] = useState(coverLetter.content);
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Sync if a new letter is loaded into this tab
  useEffect(() => {
    setEditedContent(coverLetter.content);
    setIsDirty(false);
    setSaveError(null);
  }, [coverLetter.id, coverLetter.content]);

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setEditedContent(e.target.value);
    setIsDirty(e.target.value !== coverLetter.content);
    setSaveError(null);
  }

  async function handleSave() {
    setSaving(true);
    setSaveError(null);
    try {
      const updated = await updateCoverLetter(coverLetter.id, editedContent);
      setIsDirty(false);
      onSaved(updated);
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Save failed. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  function handleDiscard() {
    setEditedContent(coverLetter.content);
    setIsDirty(false);
    setSaveError(null);
  }

  return (
    <div className="cl-card">
      <div className="cl-preview-header">
        <div>
          <h2 className="cl-step-title">
            {coverLetter.job_title} — {coverLetter.company}
          </h2>
          <div className="cl-preview-meta" style={{ marginTop: "0.35rem" }}>
            <ModeBadge mode={coverLetter.generation_mode} />
            {isDirty && (
              <span className="cl-unsaved-badge" data-testid="cl-unsaved-badge">
                &nbsp;· Unsaved changes
              </span>
            )}
          </div>
        </div>
        <div className="cl-preview-actions">
          <button
            className="cl-btn cl-btn--secondary"
            onClick={onRegenerate}
            data-testid="cl-regenerate-btn"
          >
            ↺ Regenerate
          </button>
          <a
            className="cl-btn cl-btn--primary"
            href={coverLetterPdfUrl(coverLetter.id)}
            download
            data-testid="cl-download-btn"
          >
            ⬇ Download PDF
          </a>
        </div>
      </div>

      <textarea
        className="cl-preview-editor"
        value={editedContent}
        onChange={handleChange}
        data-testid="cl-preview-content"
        aria-label="Cover letter content — edit directly"
        spellCheck
      />

      {saveError && (
        <p className="cl-error" role="alert" data-testid="cl-save-error">
          {saveError}
        </p>
      )}

      {isDirty && (
        <div className="cl-actions cl-actions--edit">
          <button
            className="cl-btn cl-btn--secondary"
            onClick={handleDiscard}
            disabled={saving}
            data-testid="cl-discard-btn"
          >
            Discard changes
          </button>
          <button
            className="cl-btn cl-btn--primary"
            onClick={handleSave}
            disabled={saving || !editedContent.trim()}
            data-testid="cl-save-btn"
          >
            {saving && <span className="cl-spinner" aria-hidden />}
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// History tab
// ---------------------------------------------------------------------------

interface HistoryTabProps {
  history: CoverLetterSummary[];
  loading: boolean;
  error: string | null;
  onView: (id: number) => void;
  onDelete: (id: number) => void;
  onRefresh: () => void;
}

function HistoryTab({
  history,
  loading,
  error,
  onView,
  onDelete,
  onRefresh,
}: HistoryTabProps) {
  if (loading) {
    return (
      <div className="cl-card">
        <p className="cl-history-empty">Loading history…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cl-card">
        <p className="cl-error" role="alert">
          {error}
        </p>
        <div className="cl-actions">
          <button className="cl-btn cl-btn--secondary" onClick={onRefresh}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="cl-card">
      {history.length === 0 ? (
        <p className="cl-history-empty" data-testid="cl-history-empty">
          No cover letters saved yet. Generate one to get started!
        </p>
      ) : (
        <div className="cl-history-list">
          {history.map((entry) => (
            <HistoryCard
              key={entry.id}
              entry={entry}
              onView={onView}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

type Tab = "generate" | "preview" | "history";

export default function CoverLetterPage() {
  const [activeTab, setActiveTab] = useState<Tab>("generate");
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [generatedLetter, setGeneratedLetter] =
    useState<CoverLetterResponse | null>(null);
  const [history, setHistory] = useState<CoverLetterSummary[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Load resumes on mount
  useEffect(() => {
    getResumes()
      .then(setResumes)
      .catch(() => setResumes([]));
  }, []);

  // Load history whenever the history tab is activated
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const data = await listCoverLetters();
      setHistory(data);
    } catch (e: unknown) {
      setHistoryError(
        e instanceof Error ? e.message : "Failed to load history."
      );
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === "history") loadHistory();
  }, [activeTab, loadHistory]);

  function handleGenerated(cl: CoverLetterResponse) {
    setGeneratedLetter(cl);
    setActiveTab("preview");
  }

  function handleView(id: number) {
    const found = history.find((h) => h.id === id);
    if (!found) return;
    // Fetch full content then switch to preview
    import("../api/cover_letter")
      .then(({ getCoverLetter }) => getCoverLetter(id))
      .then((full) => {
        setGeneratedLetter(full);
        setActiveTab("preview");
      })
      .catch(() => {});
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this cover letter?")) return;
    try {
      await deleteCoverLetter(id);
      setHistory((prev) => prev.filter((h) => h.id !== id));
      if (generatedLetter?.id === id) setGeneratedLetter(null);
    } catch {
      // keep history as-is on failure
    }
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "generate", label: "Generate" },
    {
      key: "preview",
      label: generatedLetter ? "Preview" : "Preview",
    },
    { key: "history", label: `History${history.length > 0 ? ` (${history.length})` : ""}` },
  ];

  return (
    <div className="cl-container">
      <h1 className="cl-title">Cover Letter Generator</h1>
      <p className="cl-description">
        Create a tailored cover letter from your resume, projects and skills.
        Choose AI or local generation.
      </p>

      <nav className="cl-tabs" aria-label="Cover letter sections">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            className={`cl-tab${activeTab === key ? " cl-tab--active" : ""}`}
            onClick={() => setActiveTab(key)}
            aria-current={activeTab === key ? "page" : undefined}
            data-testid={`cl-tab-${key}`}
          >
            {label}
          </button>
        ))}
      </nav>

      {activeTab === "generate" && (
        <GenerateTab resumes={resumes} onGenerated={handleGenerated} />
      )}

      {activeTab === "preview" &&
        (generatedLetter ? (
          <PreviewTab
            coverLetter={generatedLetter}
            onRegenerate={() => setActiveTab("generate")}
            onSaved={(updated) => setGeneratedLetter(updated)}
          />
        ) : (
          <div className="cl-card">
            <p className="cl-history-empty">
              No cover letter to preview yet. Generate one first!
            </p>
            <div className="cl-actions">
              <button
                className="cl-btn cl-btn--primary"
                onClick={() => setActiveTab("generate")}
              >
                Go to Generate
              </button>
            </div>
          </div>
        ))}

      {activeTab === "history" && (
        <HistoryTab
          history={history}
          loading={historyLoading}
          error={historyError}
          onView={handleView}
          onDelete={handleDelete}
          onRefresh={loadHistory}
        />
      )}
    </div>
  );
}
