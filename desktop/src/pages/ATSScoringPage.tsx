import { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getResumes, type ResumeListItem } from "../api/resume";
import { scoreATS, type ATSScoreResult, type ATSBreakdown } from "../api/ats";
import "../styles/ATSScoringPage.css";

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------
interface ATSHistoryEntry {
  id: string;
  timestamp: string;
  resumeId: number | null;
  resumeName: string;
  jobDescriptionPreview: string;
  jobDescription: string;
  score: number;
  matchLevel: string;
  experienceMonths: number;
  breakdown: ATSBreakdown;
  matchedKeywords: string[];
  missingKeywords: string[];
  tips: string[];
  analysisMode?: "local" | "ai";
}

const HISTORY_KEY = "ats_history";
const SESSION_KEY = "ats_session";
const MAX_HISTORY = 20;

function loadHistory(): ATSHistoryEntry[] {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveHistory(entries: ATSHistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(entries.slice(0, MAX_HISTORY)));
}

function pushHistory(entry: ATSHistoryEntry) {
  const prev = loadHistory();
  saveHistory([entry, ...prev]);
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------
function ScoreRing({ score }: { score: number }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score >= 70 ? "#2ecc71" : score >= 40 ? "#f39c12" : "#e74c3c";

  return (
    <svg className="ats-score-ring" viewBox="0 0 128 128" aria-label={`Job match score: ${score} out of 100`}>
      <circle className="ats-score-ring-bg" cx="64" cy="64" r={radius} strokeWidth="10" fill="none" />
      <circle
        className="ats-score-ring-fill"
        cx="64" cy="64" r={radius}
        strokeWidth="10" fill="none"
        stroke={color}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 64 64)"
      />
      <text className="ats-score-ring-text" x="64" y="60" textAnchor="middle" dy="0.35em">{score}</text>
      <text className="ats-score-ring-label" x="64" y="82" textAnchor="middle">/ 100</text>
    </svg>
  );
}

function BreakdownBar({ label, value, description }: { label: string; value: number; description: string }) {
  const color = value >= 70 ? "#2ecc71" : value >= 40 ? "#f39c12" : "#e74c3c";
  return (
    <div className="ats-breakdown-item">
      <div className="ats-breakdown-header">
        <span className="ats-breakdown-label">{label}</span>
        <span className="ats-breakdown-value">{value}%</span>
      </div>
      <div className="ats-breakdown-bar-track">
        <div className="ats-breakdown-bar-fill" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
      <p className="ats-breakdown-desc">{description}</p>
    </div>
  );
}

function KeywordPill({ word, matched }: { word: string; matched: boolean }) {
  return (
    <span className={`ats-keyword-pill ${matched ? "ats-keyword-matched" : "ats-keyword-missing"}`}>
      {matched ? "✓" : "✗"} {word}
    </span>
  );
}

function ScoreBadge({ score, matchLevel }: { score: number; matchLevel: string }) {
  const color = matchLevel === "High" ? "#2ecc71" : matchLevel === "Medium" ? "#f39c12" : "#e74c3c";
  return (
    <span className="ats-history-score-badge" style={{ backgroundColor: color }}>
      {score} · {matchLevel}
    </span>
  );
}

function ModePill({ mode }: { mode?: "local" | "ai" }) {
  if (!mode) return null;
  return (
    <span className={`ats-mode-pill ats-mode-pill--${mode}`}>
      {mode === "ai" ? "AI" : "Local"}
    </span>
  );
}

function HistoryCard({ entry, onRestore, onDelete }: {
  entry: ATSHistoryEntry;
  onRestore: (e: ATSHistoryEntry) => void;
  onDelete: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [jdExpanded, setJdExpanded] = useState(false);
  const date = new Date(entry.timestamp).toLocaleString(undefined, {
    month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit",
  });

  return (
    <div className="ats-history-card">
      <div className="ats-history-card-header">
        <div className="ats-history-card-meta">
          <ScoreBadge score={entry.score} matchLevel={entry.matchLevel} />
          <ModePill mode={entry.analysisMode} />
          <span className="ats-history-resume-name">{entry.resumeName}</span>
          <span className="ats-history-date">{date}</span>
        </div>
        <div className="ats-history-card-actions">
          <button
            type="button"
            className="ats-history-action-btn"
            onClick={() => onRestore(entry)}
            title="Restore this session"
          >
            Restore
          </button>
          <button
            type="button"
            className="ats-history-action-btn ats-history-toggle-btn"
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? "Hide" : "Details"}
          </button>
          <button
            type="button"
            className="ats-history-action-btn ats-history-delete-btn"
            onClick={() => onDelete(entry.id)}
            title="Remove this entry"
          >
            Remove
          </button>
        </div>
      </div>

      <p className={`ats-history-jd-preview ${jdExpanded ? "" : "ats-history-jd-preview--collapsed"}`}>
        {entry.jobDescription}
      </p>
      <button
        type="button"
        className="ats-history-jd-toggle"
        onClick={() => setJdExpanded((v) => !v)}
      >
        {jdExpanded ? "Show less" : "Show full job description"}
      </button>

      {expanded && (
        <div className="ats-history-details">
          {(entry.matchedKeywords.length > 0 || entry.missingKeywords.length > 0) && (
            <>
              {entry.matchedKeywords.length > 0 && (
                <div className="ats-keyword-group">
                  <p className="ats-keyword-group-label ats-matched-label">
                    Matched ({entry.matchedKeywords.length})
                  </p>
                  <div className="ats-keyword-list">
                    {entry.matchedKeywords.map((kw) => <KeywordPill key={kw} word={kw} matched />)}
                  </div>
                </div>
              )}
              {entry.missingKeywords.length > 0 && (
                <div className="ats-keyword-group">
                  <p className="ats-keyword-group-label ats-missing-label">
                    To Add ({entry.missingKeywords.length})
                  </p>
                  <div className="ats-keyword-list">
                    {entry.missingKeywords.map((kw) => <KeywordPill key={kw} word={kw} matched={false} />)}
                  </div>
                </div>
              )}
            </>
          )}
          {entry.tips.length > 0 && (
            <ul className="ats-history-tips">
              {entry.tips.map((tip, i) => <li key={i}>{tip}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export function ATSScoringPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<"score" | "history">("score");

  // --- session state (persisted) ---
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumesLoading, setResumesLoading] = useState(true);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysisMode, setAnalysisMode] = useState<"local" | "ai">("local");
  const [scoring, setScoring] = useState(false);
  const [result, setResult] = useState<ATSScoreResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- history state ---
  const [history, setHistory] = useState<ATSHistoryEntry[]>(loadHistory);

  // --- score-all state ---
  interface AllResult { resumeId: number | null; resumeName: string; result: ATSScoreResult }
  const [allResults, setAllResults] = useState<AllResult[]>([]);
  const [scoringAll, setScoringAll] = useState(false);
  const [inputView, setInputView] = useState<"form" | "comparison">("form");

  // --- empty-resume guard ---
  // Tracks which resumeId (null = master) last returned EMPTY_RESUME
  const [emptyResumeId, setEmptyResumeId] = useState<number | null | undefined>(undefined);

  // Restore session from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      if (raw) {
        const { jobDescription: jd, selectedResumeId: rid, result: r, analysisMode: am } = JSON.parse(raw);
        if (jd) setJobDescription(jd);
        if (rid !== undefined) setSelectedResumeId(rid);
        if (r) setResult(r);
        if (am === "local" || am === "ai") setAnalysisMode(am);
      }
    } catch {
      // ignore
    }
  }, []);

  // Persist session to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ jobDescription, selectedResumeId, result, analysisMode }));
    } catch {
      // ignore
    }
  }, [jobDescription, selectedResumeId, result, analysisMode]);

  const loadResumes = useCallback(async () => {
    setResumesLoading(true);
    try {
      const list = await getResumes();
      setResumes(list);

      if (list.length === 0) {
        // No resumes means the DB was wiped — clear stale localStorage data
        localStorage.removeItem(SESSION_KEY);
        localStorage.removeItem(HISTORY_KEY);
        setHistory([]);
        setJobDescription("");
        setResult(null);
        setSelectedResumeId(null);
        return;
      }

      // Only resumes that actually have content are selectable.
      // Use ?? 1 so resumes with unknown project_count (old API) are treated as scorable.
      const scorable = list.filter((r) => (r.project_count ?? 1) > 0);
      const hasScorable = scorable.length > 0;
      const scorableMaster = scorable.find((r) => r.is_master);

      // Clear a stale result when all projects have been deleted
      if (!hasScorable) setResult(null);

      setSelectedResumeId((prev) => {
        if (prev === null) {
          // Was using master resume — keep if it has content, else pick first scorable
          if (scorableMaster) return null;
          return scorable.find((r) => !r.is_master && r.id !== null)?.id ?? null;
        }
        // Was using a specific saved resume — keep if it still exists AND has content
        const match = list.find((r) => r.id === prev);
        if (match && (match.project_count ?? 1) > 0) return prev;
        // Resume gone or empty — fall back to master if scorable, else first scorable
        if (!hasScorable) return null;
        if (scorableMaster) return null;
        return scorable.find((r) => !r.is_master && r.id !== null)?.id ?? null;
      });
    } catch {
      // keep current selection on error
    } finally {
      setResumesLoading(false);
    }
  }, []);

  useEffect(() => {
    loadResumes();
  }, [loadResumes, location.key]);

  const resumeNameFor = (id: number | null) => {
    if (id === null) return resumes.find((r) => r.is_master)?.name ?? "Master Resume";
    return resumes.find((r) => r.id === id)?.name ?? `Resume ${id}`;
  };

  const handleScore = useCallback(async () => {
    if (!jobDescription.trim()) return;
    setError(null);
    setResult(null);
    setScoring(true);
    try {
      const res = await scoreATS(jobDescription, selectedResumeId, analysisMode);
      setResult(res);

      // Persist to history
      const entry: ATSHistoryEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        resumeId: selectedResumeId,
        resumeName: resumeNameFor(selectedResumeId),
        jobDescriptionPreview: jobDescription.slice(0, 120),
        jobDescription,
        score: res.score,
        matchLevel: res.match_level,
        experienceMonths: res.experience_months,
        breakdown: res.breakdown,
        matchedKeywords: res.matched_keywords.slice(0, 20),
        missingKeywords: res.missing_keywords.slice(0, 20),
        tips: res.tips,
        analysisMode,
      };
      pushHistory(entry);
      setHistory(loadHistory());
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to calculate job match score";
      if (msg === "EMPTY_RESUME") {
        setEmptyResumeId(selectedResumeId);
      } else {
        setError(msg);
      }
    } finally {
      setScoring(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobDescription, selectedResumeId, analysisMode, resumes]);

  const handleRestoreHistory = (entry: ATSHistoryEntry) => {
    setJobDescription(entry.jobDescription);
    setSelectedResumeId(entry.resumeId);
    setAnalysisMode(entry.analysisMode ?? "local");
    setResult({
      score: entry.score,
      match_level: entry.matchLevel,
      experience_months: entry.experienceMonths,
      breakdown: entry.breakdown,
      matched_keywords: entry.matchedKeywords,
      missing_keywords: entry.missingKeywords,
      matched_skills: [],
      missing_skills: [],
      tips: entry.tips,
    });
    setActiveTab("score");
  };

  const handleClearHistory = () => {
    localStorage.removeItem(HISTORY_KEY);
    setHistory([]);
  };

  const handleDeleteHistoryEntry = (id: string) => {
    const updated = history.filter((e) => e.id !== id);
    saveHistory(updated);
    setHistory(updated);
  };

  const handleScoreAll = useCallback(async () => {
    if (!jobDescription.trim() || resumes.length === 0) return;
    setScoringAll(true);
    setAllResults([]);
    setError(null);
    try {
      const results: AllResult[] = [];
      for (const resume of resumes) {
        // Skip resumes with no projects — they have nothing to score
        if ((resume.project_count ?? 1) === 0) continue;
        const rid = resume.is_master ? null : (resume.id ?? null);
        const res = await scoreATS(jobDescription, rid, analysisMode);
        results.push({ resumeId: rid, resumeName: resume.name, result: res });
      }
      results.sort((a, b) => b.result.score - a.result.score);
      setAllResults(results);
      setInputView("comparison");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to score all resumes";
      setError(
        msg === "EMPTY_RESUME"
          ? "One of your resumes has no content. Add projects before scoring."
          : msg
      );
    } finally {
      setScoringAll(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobDescription, analysisMode, resumes]);

  const mergedMatched = result
    ? [...new Set([...result.matched_keywords, ...result.matched_skills])].slice(0, 20)
    : [];
  const mergedMissing = result
    ? [...new Set([...result.missing_keywords, ...result.missing_skills])].slice(0, 20)
    : [];

  // Show the "no content" warning either if the API returned EMPTY_RESUME for
  // this resume, OR if the resume list already tells us it has 0 projects.
  // NOTE: selectedResumeId is null for the master resume, but the master resume
  // has id=1 in the list — so we look it up via is_master when id is null.
  const selectedResumeItem = selectedResumeId === null
    ? (resumes.find(r => r.is_master) ?? null)
    : (resumes.find(r => r.id === selectedResumeId) ?? null);
  const currentResumeIsEmpty =
    (emptyResumeId !== undefined && emptyResumeId === selectedResumeId) ||
    (selectedResumeItem !== null && (selectedResumeItem.project_count ?? 1) === 0);

  // Resumes that actually have content and can be scored.
  // ?? 1 treats unknown project_count (old API) as "has content" to avoid false empties.
  const scorableResumes = resumes.filter(r => (r.project_count ?? 1) > 0);

  // True when SKILL_ANALYSIS is empty — no projects have been uploaded at all
  const masterResume = resumes.find(r => r.is_master);
  const systemHasNoProjects = !masterResume || (masterResume.project_count ?? 1) === 0;

  const matchLevelColor =
    result?.match_level === "High" ? "#2ecc71"
    : result?.match_level === "Medium" ? "#f39c12"
    : "#e74c3c";

  const experienceLabel = (months: number) => {
    if (months === 0) return null;
    if (months < 12) return `${months} month${months !== 1 ? "s" : ""} of project experience`;
    const years = Math.floor(months / 12);
    const rem = months % 12;
    return rem > 0
      ? `${years} yr${years !== 1 ? "s" : ""} ${rem} mo of project experience`
      : `${years} year${years !== 1 ? "s" : ""} of project experience`;
  };

  const breakdownDescriptions: Record<string, string> = {
    keyword_coverage: "How many job description keywords appear in your resume.",
    skills_match: "How well the required tools and technologies from the job description match your resume.",
    content_richness: "How well your resume bullet points cover the required topics.",
  };

  const breakdownLabels: Record<string, string> = {
    keyword_coverage: "Keyword Coverage",
    skills_match: "Skills Match",
    content_richness: "Content Richness",
  };

  return (
    <div className="ats-container">
      {/* Breadcrumb */}
      <div className="page-home-nav" aria-label="Page navigation">
        <button type="button" className="page-home-link" onClick={() => navigate("/hubpage")}>
          Home
        </button>
        <span className="page-home-separator">›</span>
        <span className="page-home-current">Check Job Match</span>
      </div>

      <h1 className="ats-title">Check Job Match</h1>
      <p className="ats-description">
        Paste a job description and choose a resume to see how well your skills and experience match the role.
      </p>

      {/* Page tabs */}
      <div className="ats-tabs" role="tablist">
        <button
          role="tab"
          type="button"
          className={`ats-tab ${activeTab === "score" ? "ats-tab--active" : ""}`}
          aria-selected={activeTab === "score"}
          onClick={() => setActiveTab("score")}
        >
          Score
        </button>
        <button
          role="tab"
          type="button"
          className={`ats-tab ${activeTab === "history" ? "ats-tab--active" : ""}`}
          aria-selected={activeTab === "history"}
          onClick={() => setActiveTab("history")}
        >
          History {history.length > 0 && <span className="ats-tab-count">{history.length}</span>}
        </button>
      </div>

      {/* ================================================================
          EMPTY STATE — no resumes (DB wiped / no projects uploaded yet)
      ================================================================ */}
      {!resumesLoading && resumes.length === 0 && (
        <div className="ats-empty-state">
          <div className="ats-empty-icon" aria-hidden="true">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <circle cx="12" cy="12" r="6" />
              <circle cx="12" cy="12" r="2" />
            </svg>
          </div>
          <h2 className="ats-empty-title">No resume available</h2>
          <p className="ats-empty-body">
            Upload projects first so a resume can be generated, then come back to check your job match score.
          </p>
          <button
            type="button"
            className="ats-empty-btn"
            onClick={() => navigate("/uploadpage")}
          >
            Upload Projects
          </button>
        </div>
      )}

      {/* ================================================================
          SCORE TAB
      ================================================================ */}
      {activeTab === "score" && resumes.length > 0 && (
        <div className="ats-layout">

          {/* ---- Left panel — form OR comparison view ---- */}
          <div className="ats-input-panel">

            {inputView === "comparison" && allResults.length > 0 ? (
              /* ---- Comparison view ---- */
              <div className="ats-comparison-view">
                <div className="ats-comparison-view-header">
                  <h2 className="ats-section-title">All Resumes</h2>
                  <button
                    type="button"
                    className="ats-history-action-btn"
                    onClick={() => { setInputView("form"); setAllResults([]); }}
                  >
                    New Analysis
                  </button>
                </div>
                <p className="ats-comparison-view-hint">
                  Click <strong>Load Details</strong> to view a resume's full breakdown.
                </p>
                <div className="ats-comparison-list">
                  {allResults.map((ar, idx) => {
                    const color = ar.result.match_level === "High" ? "#2ecc71"
                      : ar.result.match_level === "Medium" ? "#f39c12" : "#e74c3c";
                    return (
                      <div key={ar.resumeId ?? "master"} className="ats-comparison-row">
                        <span className="ats-comparison-rank">#{idx + 1}</span>
                        <span className="ats-comparison-name">{ar.resumeName}</span>
                        <span className="ats-history-score-badge" style={{ backgroundColor: color }}>
                          {ar.result.score} · {ar.result.match_level}
                        </span>
                        <button
                          type="button"
                          className="ats-history-action-btn"
                          onClick={() => {
                            setSelectedResumeId(ar.resumeId);
                            setResult(ar.result);
                          }}
                        >
                          Details
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              /* ---- Form view ---- */
              <>
                <div className="ats-field">
                  <label htmlFor="ats-resume-select" className="ats-label">Resume</label>
                  {resumesLoading ? (
                    <p className="ats-loading-small">Loading resumes…</p>
                  ) : (
                    <select
                      id="ats-resume-select"
                      className="ats-select"
                      value={selectedResumeId === null ? "" : selectedResumeId}
                      disabled={scorableResumes.length === 0}
                      onChange={(e) => {
                        const val = e.target.value;
                        setSelectedResumeId(val === "" ? null : Number(val));
                        setResult(null);
                        setEmptyResumeId(undefined);
                      }}
                    >
                      {scorableResumes.length === 0 ? (
                        <option value="" disabled>No resumes found</option>
                      ) : (
                        <>
                          {resumes.some((r) => r.is_master && (r.project_count ?? 1) > 0) && (
                            <option value="">Master Resume (all projects)</option>
                          )}
                          {resumes
                            .filter((r) => !r.is_master && r.id !== null && (r.project_count ?? 1) > 0)
                            .map((r) => (
                              <option key={r.id} value={r.id!}>{r.name}</option>
                            ))}
                        </>
                      )}
                    </select>
                  )}
                </div>

                <div className="ats-field">
                  <label className="ats-label">Scoring Mode</label>
                  <div className="ats-mode-toggle" role="group" aria-label="Scoring mode">
                    <button
                      type="button"
                      className={`ats-mode-btn${analysisMode === "local" ? " ats-mode-btn--active" : ""}`}
                      onClick={() => { setAnalysisMode("local"); setResult(null); }}
                    >
                      Local
                    </button>
                    <button
                      type="button"
                      className={`ats-mode-btn${analysisMode === "ai" ? " ats-mode-btn--active" : ""}`}
                      onClick={() => { setAnalysisMode("ai"); setResult(null); }}
                    >
                      AI
                    </button>
                  </div>
                  {analysisMode === "ai" && (
                    <p className="ats-ai-disclaimer">
                      AI mode: your job description will be sent to the configured LLM provider for keyword extraction.
                    </p>
                  )}
                </div>

                <div className="ats-field">
                  <label htmlFor="ats-jd-textarea" className="ats-label">Job Description</label>
                  <textarea
                    id="ats-jd-textarea"
                    className="ats-textarea"
                    placeholder="Paste the full job description here…"
                    value={jobDescription}
                    onChange={(e) => {
                      setJobDescription(e.target.value);
                      setResult(null);
                    }}
                    rows={14}
                  />
                  <p className="ats-char-count">
                    {jobDescription.trim().split(/\s+/).filter(Boolean).length} words
                  </p>
                </div>

                <button
                  type="button"
                  className="ats-score-btn"
                  onClick={handleScore}
                  disabled={scoring || scoringAll || currentResumeIsEmpty || jobDescription.trim().length < 10}
                >
                  {scoring ? "Analyzing…" : "Check Job Match Score"}
                </button>

                {scorableResumes.length > 1 && (
                  <button
                    type="button"
                    className="ats-score-btn ats-score-btn--secondary"
                    onClick={handleScoreAll}
                    disabled={scoring || scoringAll || jobDescription.trim().length < 10}
                  >
                    {scoringAll ? "Scoring all resumes…" : "Score All Resumes"}
                  </button>
                )}

                {error && <div className="ats-error" role="alert">{error}</div>}
              </>
            )}
          </div>

          {/* ---- Results panel ---- */}
          <div className="ats-results-panel">
            {!result && !scoring && !scoringAll && (
              <div className="ats-placeholder frame">
                <div className="ats-placeholder-icon" aria-hidden>
                  <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                    {systemHasNoProjects || currentResumeIsEmpty ? (
                      <>
                        <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2z" />
                        <path d="M12 8v4m0 4h.01" />
                      </>
                    ) : (
                      <>
                        <path d="M9 11l3 3L22 4" />
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                      </>
                    )}
                  </svg>
                </div>
                {systemHasNoProjects ? (
                  <p className="ats-placeholder-text">
                    Upload projects for insights.
                  </p>
                ) : currentResumeIsEmpty ? (
                  <p className="ats-placeholder-text">
                    Add projects or experience to this resume to score it.
                  </p>
                ) : (
                  <p className="ats-placeholder-text">
                    Your job match score and keyword analysis will appear here.
                  </p>
                )}
              </div>
            )}

            {(scoring || scoringAll) && (
              <div className="ats-placeholder frame">
                <div className="ats-spinner" aria-label="Analyzing" />
                <p className="ats-placeholder-text">
                  {scoringAll ? "Scoring all resumes…" : "Analyzing your resume…"}
                </p>
              </div>
            )}

            {result && !scoring && !scoringAll && (
              <>
                {/* Score hero */}
                <div className="ats-score-hero frame">
                  <ScoreRing score={result.score} />
                  <div className="ats-score-info">
                    <span className="ats-match-level-badge" style={{ backgroundColor: matchLevelColor }}>
                      {result.match_level} Match
                    </span>
                    <p className="ats-score-sublabel">Job Match Score</p>
                    {experienceLabel(result.experience_months) && (
                      <p className="ats-experience-pill">
                        {experienceLabel(result.experience_months)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Breakdown */}
                <div className="ats-section frame">
                  <h2 className="ats-section-title">Score Breakdown</h2>
                  {Object.entries(result.breakdown).map(([key, val]) => (
                    <BreakdownBar
                      key={key}
                      label={breakdownLabels[key] ?? key}
                      value={val}
                      description={breakdownDescriptions[key] ?? ""}
                    />
                  ))}
                </div>

                {/* Keyword & Skills Analysis */}
                {(mergedMatched.length > 0 || mergedMissing.length > 0) && (
                  <div className="ats-section frame">
                    <h2 className="ats-section-title">Keyword &amp; Skills Analysis</h2>
                    {mergedMatched.length > 0 && (
                      <div className="ats-keyword-group">
                        <p className="ats-keyword-group-label ats-matched-label">
                          Matched ({mergedMatched.length})
                        </p>
                        <div className="ats-keyword-list">
                          {mergedMatched.map((kw) => <KeywordPill key={kw} word={kw} matched />)}
                        </div>
                      </div>
                    )}
                    {mergedMissing.length > 0 && (
                      <div className="ats-keyword-group">
                        <p className="ats-keyword-group-label ats-missing-label">
                          To Add ({mergedMissing.length})
                        </p>
                        <div className="ats-keyword-list">
                          {mergedMissing.map((kw) => <KeywordPill key={kw} word={kw} matched={false} />)}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Tips */}
                {result.tips.length > 0 && (
                  <div className="ats-section frame ats-tips-section">
                    <h2 className="ats-section-title">Improvement Tips</h2>
                    <ul className="ats-tips-list">
                      {result.tips.map((tip, i) => (
                        <li key={i} className="ats-tip-item">{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* ================================================================
          HISTORY TAB
      ================================================================ */}
      {activeTab === "history" && resumes.length > 0 && (
        <div className="ats-history-panel">
          <div className="ats-history-toolbar">
            <p className="ats-history-count">
              {history.length === 0 ? "No history yet." : `${history.length} saved score${history.length !== 1 ? "s" : ""}`}
            </p>
            {history.length > 0 && (
              <button type="button" className="ats-clear-history-btn" onClick={handleClearHistory}>
                Clear History
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="ats-history-empty">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" aria-hidden>
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              <p>Run your first job match score to see it here.</p>
            </div>
          ) : (
            <div className="ats-history-list">
              {history.map((entry) => (
                <HistoryCard key={entry.id} entry={entry} onRestore={handleRestoreHistory} onDelete={handleDeleteHistoryEntry} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ATSScoringPage;
