import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
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
    <svg className="ats-score-ring" viewBox="0 0 128 128" aria-label={`ATS score: ${score} out of 100`}>
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

function HistoryCard({ entry, onRestore }: { entry: ATSHistoryEntry; onRestore: (e: ATSHistoryEntry) => void }) {
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
                Missing ({entry.missingKeywords.length})
              </p>
              <div className="ats-keyword-list">
                {entry.missingKeywords.map((kw) => <KeywordPill key={kw} word={kw} matched={false} />)}
              </div>
            </div>
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
  const [activeTab, setActiveTab] = useState<"score" | "history">("score");

  // --- session state (persisted) ---
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumesLoading, setResumesLoading] = useState(true);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [scoring, setScoring] = useState(false);
  const [result, setResult] = useState<ATSScoreResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- history state ---
  const [history, setHistory] = useState<ATSHistoryEntry[]>(loadHistory);

  // Restore session from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      if (raw) {
        const { jobDescription: jd, selectedResumeId: rid, result: r } = JSON.parse(raw);
        if (jd) setJobDescription(jd);
        if (rid !== undefined) setSelectedResumeId(rid);
        if (r) setResult(r);
      }
    } catch {
      // ignore
    }
  }, []);

  // Persist session to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ jobDescription, selectedResumeId, result }));
    } catch {
      // ignore
    }
  }, [jobDescription, selectedResumeId, result]);

  const loadResumes = useCallback(async () => {
    setResumesLoading(true);
    try {
      const list = await getResumes();
      setResumes(list);
      // If master resume doesn't exist and we're defaulting to it, switch to first available
      const hasMaster = list.some((r) => r.is_master);
      if (!hasMaster) {
        setSelectedResumeId((prev) => {
          if (prev !== null) return prev;
          const first = list.find((r) => !r.is_master && r.id !== null);
          return first?.id ?? null;
        });
      }
    } catch {
      // keep current selection on error
    } finally {
      setResumesLoading(false);
    }
  }, []);

  useEffect(() => {
    loadResumes();
  }, [loadResumes]);

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
      const res = await scoreATS(jobDescription, selectedResumeId);
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
        matchedKeywords: [...new Set([...res.matched_keywords, ...res.matched_skills])].slice(0, 20),
        missingKeywords: [...new Set([...res.missing_keywords, ...res.missing_skills])].slice(0, 20),
        tips: res.tips,
      };
      pushHistory(entry);
      setHistory(loadHistory());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to calculate ATS score");
    } finally {
      setScoring(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobDescription, selectedResumeId, resumes]);

  const handleRestoreHistory = (entry: ATSHistoryEntry) => {
    setJobDescription(entry.jobDescription);
    setSelectedResumeId(entry.resumeId);
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

  // Merged keyword+skills sets from current result, capped to 20 to match backend limit
  const mergedMatched = result
    ? [...new Set([...result.matched_keywords, ...result.matched_skills])].slice(0, 20)
    : [];
  const mergedMissing = result
    ? [...new Set([...result.missing_keywords, ...result.missing_skills])].slice(0, 20)
    : [];

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
    keyword_coverage: "How many job description keywords appear anywhere in your resume.",
    skills_match: "How many job description keywords match your listed skills.",
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
        <span className="page-home-current">ATS Scoring</span>
      </div>

      <h1 className="ats-title">ATS Scoring</h1>
      <p className="ats-description">
        Paste a job description and choose a resume to see how well it matches
        applicant tracking system requirements.
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
          SCORE TAB
      ================================================================ */}
      {activeTab === "score" && (
        <div className="ats-layout">
          {/* ---- Input panel ---- */}
          <div className="ats-input-panel frame">
            <div className="ats-field">
              <div className="ats-label-row">
                <label htmlFor="ats-resume-select" className="ats-label">Resume</label>
                <button
                  type="button"
                  className="ats-manage-resumes-link"
                  onClick={() => navigate("/resumebuilderpage")}
                >
                  Manage Resumes →
                </button>
              </div>
              {resumesLoading ? (
                <p className="ats-loading-small">Loading resumes…</p>
              ) : (
                <select
                  id="ats-resume-select"
                  className="ats-select"
                  value={selectedResumeId === null ? "" : selectedResumeId}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSelectedResumeId(val === "" ? null : Number(val));
                    setResult(null);
                  }}
                >
                  {resumes.some((r) => r.is_master) && (
                    <option value="">Master Resume (all projects)</option>
                  )}
                  {resumes
                    .filter((r) => !r.is_master && r.id !== null)
                    .map((r) => (
                      <option key={r.id} value={r.id!}>{r.name}</option>
                    ))}
                </select>
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
                rows={20}
              />
              <p className="ats-char-count">
                {jobDescription.trim().split(/\s+/).filter(Boolean).length} words
              </p>
            </div>

            <button
              type="button"
              className="ats-score-btn"
              onClick={handleScore}
              disabled={scoring || jobDescription.trim().length < 10}
            >
              {scoring ? "Analyzing…" : "Calculate ATS Score"}
            </button>

            {error && <div className="ats-error" role="alert">{error}</div>}
          </div>

          {/* ---- Results panel ---- */}
          <div className="ats-results-panel">
            {!result && !scoring && (
              <div className="ats-placeholder frame">
                <div className="ats-placeholder-icon" aria-hidden>
                  <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                    <path d="M9 11l3 3L22 4" />
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                  </svg>
                </div>
                <p className="ats-placeholder-text">
                  Your ATS score and keyword analysis will appear here.
                </p>
              </div>
            )}

            {scoring && (
              <div className="ats-placeholder frame">
                <div className="ats-spinner" aria-label="Analyzing" />
                <p className="ats-placeholder-text">Analyzing your resume…</p>
              </div>
            )}

            {result && !scoring && (
              <>
                {/* Score hero */}
                <div className="ats-score-hero frame">
                  <ScoreRing score={result.score} />
                  <div className="ats-score-info">
                    <span className="ats-match-level-badge" style={{ backgroundColor: matchLevelColor }}>
                      {result.match_level} Match
                    </span>
                    <p className="ats-score-sublabel">ATS Compatibility Score</p>
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

                {/* Merged keyword + skills section */}
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
              </>
            )}
          </div>
        </div>
      )}

      {/* ================================================================
          HISTORY TAB
      ================================================================ */}
      {activeTab === "history" && (
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
              <p>Run your first ATS score to see it here.</p>
            </div>
          ) : (
            <div className="ats-history-list">
              {history.map((entry) => (
                <HistoryCard key={entry.id} entry={entry} onRestore={handleRestoreHistory} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ATSScoringPage;
