import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config/api";
import "../styles/JobMatchPage.css";

interface JobMatchResult {
  status: string;
  match_score: number;
  experience_level_hint: string;
  extracted_job_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  required_skills: string[];
  preferred_skills: string[];
  strengths: string[];
}

interface ProfilePostingResult {
  status: string;
  profile: {
    target_level: string;
    country: string;
    major: string;
    graduation_year: number | null;
    top_skills: string[];
    saved_skills?: string[];
    industry: string;
    job_title: string;
  };
  linkedin_search_links: Array<{
    label: string;
    url: string;
  }>;
}

export default function JobMatchPage() {
  const navigate = useNavigate();
  const [workTypes, setWorkTypes] = useState<Array<"onsite" | "remote" | "hybrid">>([
    "onsite",
    "remote",
    "hybrid",
  ]);
  const [easyApplyOnly, setEasyApplyOnly] = useState(true);
  const [postedWithinDays, setPostedWithinDays] = useState<1 | 7 | 30>(7);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [skillsSearchTerm, setSkillsSearchTerm] = useState("");

  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileResult, setProfileResult] = useState<ProfilePostingResult | null>(
    null,
  );
  const profileRequestIdRef = useRef(0);

  const [jobDescription, setJobDescription] = useState("");
  const [jobMatchLoading, setJobMatchLoading] = useState(false);
  const [jobMatchError, setJobMatchError] = useState<string | null>(null);
  const [jobMatchResult, setJobMatchResult] = useState<JobMatchResult | null>(
    null,
  );

  const loadProfilePostings = useCallback(async () => {
    const requestId = profileRequestIdRef.current + 1;
    profileRequestIdRef.current = requestId;
    try {
      setProfileLoading(true);
      setProfileError(null);
      const query = new URLSearchParams({
        top_k: "12",
        work_types: workTypes.join(","),
        selected_skills: selectedSkills.join(","),
        easy_apply: String(easyApplyOnly),
        posted_within_days: String(postedWithinDays),
      });
      const res = await fetch(`${API_BASE_URL}/api/job-match/profile-postings?${query.toString()}`);
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Failed to fetch LinkedIn search links");
      }
      const payload = (await res.json()) as ProfilePostingResult;
      if (profileRequestIdRef.current === requestId) {
        setProfileResult(payload);
      }
    } catch (e) {
      if (profileRequestIdRef.current === requestId) {
        setProfileError(
          e instanceof Error ? e.message : "Failed to load LinkedIn search links",
        );
      }
    } finally {
      if (profileRequestIdRef.current === requestId) {
        setProfileLoading(false);
      }
    }
  }, [workTypes, selectedSkills, easyApplyOnly, postedWithinDays]);

  useEffect(() => {
    void loadProfilePostings();
  }, [loadProfilePostings]);

  const savedSkills = profileResult?.profile.saved_skills || profileResult?.profile.top_skills || [];
  const filteredSkills = useMemo(() => {
    const term = skillsSearchTerm.trim().toLowerCase();
    if (!term) {
      return savedSkills;
    }
    return savedSkills.filter((skill) => skill.toLowerCase().includes(term));
  }, [savedSkills, skillsSearchTerm]);

  const toggleWorkType = (type: "onsite" | "remote" | "hybrid") => {
    setWorkTypes((prev) => {
      if (prev.includes(type)) {
        return prev.filter((item) => item !== type);
      }
      return [...prev, type];
    });
  };

  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) => {
      if (prev.includes(skill)) {
        return prev.filter((item) => item !== skill);
      }
      return [...prev, skill];
    });
  };

  const runJobMatchSimulation = async () => {
    const trimmed = jobDescription.trim();
    if (trimmed.length < 20) {
      setJobMatchError(
        "Paste a fuller job description (at least 20 characters).",
      );
      return;
    }

    try {
      setJobMatchLoading(true);
      setJobMatchError(null);
      const res = await fetch(`${API_BASE_URL}/api/job-match/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: trimmed, top_k: 5 }),
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Failed to run job match simulation");
      }

      setJobMatchResult((await res.json()) as JobMatchResult);
    } catch (e) {
      setJobMatchError(
        e instanceof Error ? e.message : "Failed to run job match simulation",
      );
    } finally {
      setJobMatchLoading(false);
    }
  };

  return (
    <div className="job-match-page">
      <div className="job-match-page-header">
        <div className="page-home-nav" aria-label="Page navigation">
          <button
            type="button"
            className="page-home-link"
            onClick={() => navigate("/hubpage")}
          >
            Home
          </button>
          <span className="page-home-separator">›</span>
          <span className="page-home-current">Job Match</span>
        </div>
        <h1>Job Match</h1>
        <p>
          Discover relevant opportunities using configurable LinkedIn filters,
          then evaluate fit against a specific role description.
        </p>
      </div>

      <div className="job-match-content-grid">
        <div className="job-match-main-grid">
          <section className="job-match-page-card job-section-panel job-live-section job-live-section-primary">
            <div className="job-card-header">
              <div>
                <span className="job-step-label">Step 1</span>
                <h3 className="job-card-title">Set Search Filters</h3>
                <p className="job-section-note">
                  Configure filters and pick which saved skills should shape link keywords.
                </p>
              </div>
            </div>

            {profileError ? (
              <p className="job-match-error">{profileError}</p>
            ) : null}

            <div className="job-linkedin-preferences" aria-label="LinkedIn filter preferences">
              <div className="job-linkedin-pref-group">
                <span className="job-match-subtitle">Work Type</span>
                <button
                  type="button"
                  className={`job-filter-chip ${workTypes.includes("onsite") ? "active" : ""}`}
                  onClick={() => toggleWorkType("onsite")}
                >
                  On-site
                </button>
                <button
                  type="button"
                  className={`job-filter-chip ${workTypes.includes("remote") ? "active" : ""}`}
                  onClick={() => toggleWorkType("remote")}
                >
                  Remote
                </button>
                <button
                  type="button"
                  className={`job-filter-chip ${workTypes.includes("hybrid") ? "active" : ""}`}
                  onClick={() => toggleWorkType("hybrid")}
                >
                  Hybrid
                </button>
              </div>

              <div className="job-linkedin-pref-group">
                <span className="job-match-subtitle">Posted</span>
                <div className="job-filter-select-wrap">
                  <select
                    className="job-filter-select"
                    value={postedWithinDays}
                    onChange={(e) => setPostedWithinDays(Number(e.target.value) as 1 | 7 | 30)}
                  >
                    <option value={1}>Last 24 hours</option>
                    <option value={7}>Last 7 days</option>
                    <option value={30}>Last 30 days</option>
                  </select>
                </div>
                <label className="job-filter-toggle">
                  <input
                    type="checkbox"
                    checked={easyApplyOnly}
                    onChange={(e) => setEasyApplyOnly(e.target.checked)}
                  />
                  Easy Apply
                </label>
              </div>

              <div className="job-linkedin-pref-group job-linkedin-pref-group-skills">
                <span className="job-match-subtitle">Skills in Search</span>
                <div className="job-skills-picker">
                  <div className="job-skills-picker-toolbar">
                    <input
                      type="text"
                      className="job-filter-select"
                      placeholder="Search saved skills..."
                      value={skillsSearchTerm}
                      onChange={(e) => setSkillsSearchTerm(e.target.value)}
                    />
                    <span className="job-match-muted">
                      {selectedSkills.length} selected · {savedSkills.length} saved
                    </span>
                  </div>
                  <div className="job-skills-picker-list" aria-label="Saved skills">
                    {savedSkills.length === 0 ? (
                      <span className="job-match-muted">No saved skills available yet.</span>
                    ) : filteredSkills.length === 0 ? (
                      <span className="job-match-muted">No skills match your search.</span>
                    ) : (
                      filteredSkills.map((skill) => (
                        <button
                          key={`skill-${skill}`}
                          type="button"
                          className={`job-filter-chip ${selectedSkills.includes(skill) ? "active" : ""}`}
                          onClick={() => toggleSkill(skill)}
                        >
                          {skill}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="job-match-page-card job-section-panel job-links-section">
            <div className="job-card-header job-card-header-compact">
              <div>
                <span className="job-step-label">Step 2</span>
                <h3 className="job-card-title">Open Search Links</h3>
                <p className="job-section-note">
                  Launch a link in a new tab to continue directly in LinkedIn.
                </p>
              </div>
            </div>

            {(profileResult?.linkedin_search_links || []).length > 0 ? (
              <div className="job-linkedin-links">
                {profileResult.linkedin_search_links.slice(0, 5).map((link) => (
                  <a
                    key={`li-${link.label}`}
                    className="job-linkedin-link"
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <span>{link.label}</span>
                  </a>
                ))}
              </div>
            ) : null}

            {(profileResult?.linkedin_search_links || []).length === 0 && !profileLoading ? (
              <div className="job-linkedin-links">
                <p className="job-match-muted">
                  No links available yet. Refresh after setting your filters.
                </p>
              </div>
            ) : null}
          </section>

        <section className="job-match-page-card job-section-panel job-match-bottom">
          <span className="job-step-label">Step 3</span>
          <h3 className="job-card-title">Match a Specific Job Description</h3>
          <p className="job-section-note">
            Paste a role description to compare required skills with your portfolio.
          </p>
          <label className="job-match-label" htmlFor="jobMatchTextarea">
            Paste a job description
          </label>
          <textarea
            id="jobMatchTextarea"
            className="job-match-textarea"
            placeholder="Paste a specific posting to calculate match score and skill gaps..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
          <div className="job-match-actions">
          <button
            className="job-match-btn"
            onClick={() => void runJobMatchSimulation()}
            disabled={jobMatchLoading}
          >
            {jobMatchLoading ? "Analyzing..." : "Run Match Simulation"}
          </button>
          {jobMatchError ? (
            <span className="job-match-error">{jobMatchError}</span>
          ) : null}
          </div>

          {jobMatchResult ? (
            <div className="job-match-results">
            <div className="job-match-kpis">
              <div className="job-match-kpi">
                <span>Match Score</span>
                <strong>{jobMatchResult.match_score}%</strong>
              </div>
              <div className="job-match-kpi">
                <span>Suggested Level</span>
                <strong>{jobMatchResult.experience_level_hint}</strong>
              </div>
            </div>

            <div className="job-match-chip-row">
              <span className="job-match-subtitle">Matched Skills</span>
              {(jobMatchResult.matched_skills || []).length > 0 ? (
                jobMatchResult.matched_skills.map((skill) => (
                  <span key={`matched-${skill}`} className="job-match-chip matched">
                    {skill}
                  </span>
                ))
              ) : (
                <span className="job-match-muted">No direct matches yet</span>
              )}
            </div>

            <div className="job-match-chip-row">
              <span className="job-match-subtitle">Missing Skills</span>
              {(jobMatchResult.missing_skills || []).length > 0 ? (
                jobMatchResult.missing_skills.map((skill) => (
                  <span key={`missing-${skill}`} className="job-match-chip missing">
                    {skill}
                  </span>
                ))
              ) : (
                <span className="job-match-muted">No major gaps detected</span>
              )}
            </div>
            </div>
          ) : null}
        </section>
        </div>
      </div>
    </div>
  );
}