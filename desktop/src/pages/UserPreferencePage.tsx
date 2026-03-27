import { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/UserPreferencePage.css';
import '../styles/Notification.css';
import '../styles/ProjectSelectionPage.css';
import { 
  getUserPreferences, 
  saveUserPreferences,
  notifyUserPreferencesUpdated,
  uploadProfilePicture,
  deleteProfilePicture,
  getProfilePictureUrl,
  getAllInstitutions,
  type UserPreferences, 
  type EducationDetail,
  type Institution 
} from '../api/userPreferences';
import { getConsentStatus } from '../api/consent';
import {
  getLearningRecommendations,
  learningThumbnailSrc,
  type LearningCourse,
  type LearningRecommendationsResponse,
} from '../api/learning';
import { getProjects } from '../api/projects';

const INDUSTRIES = [
  "Technology",
  "Healthcare",
  "Finance",
  "Education",
  "Manufacturing",
  "Retail",
  "Hospitality",
  "Transportation",
] as const;

// Frontend representation of education entry
export interface EducationEntry {
  id: string;
  institution: string;
  degree: string;
  startDate: string;
  endDate: string;
  gpa: string;
}

// Frontend representation of profile data
export interface ProfileData {
  fullName: string;
  email: string;
  github: string;
  linkedin: string;
  jobTitle: string;
  industry: typeof INDUSTRIES[number] | null;
  personalSummary: string;
  educationEntries: EducationEntry[];
}

// Simple SVG Icon Components
const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const PencilIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
  </svg>
);

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  </svg>
);

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const XIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

function createEmptyEntry(): EducationEntry {
  return {
    id: crypto.randomUUID(),
    institution: "",
    degree: "",
    startDate: "",
    endDate: "",
    gpa: "",
  };
}

// Helper functions to convert between frontend and backend formats
function convertToFrontend(backendData: UserPreferences): ProfileData {
  const educationEntries: EducationEntry[] = (backendData.education_details || []).map(detail => ({
    id: crypto.randomUUID(), // Generate ID for frontend
    institution: detail.institution,
    degree: detail.degree,
    startDate: detail.start_date ? convertDateToMonthFormat(detail.start_date) : "",
    endDate: detail.end_date ? convertDateToMonthFormat(detail.end_date) : "",
    gpa: detail.gpa ? String(detail.gpa) : "",
  }));

  return {
    fullName: backendData.name || "",
    email: backendData.email || "",
    github: backendData.github_user || "",
    linkedin: backendData.linkedin || "",
    jobTitle: backendData.job_title || "",
    industry: backendData.industry as typeof INDUSTRIES[number] || null,
    personalSummary: backendData.personal_summary || "",
    educationEntries,
  };
}

function convertToBackend(frontendData: ProfileData): UserPreferences {
  const educationDetails: EducationDetail[] = frontendData.educationEntries
    .filter(entry => entry.institution || entry.degree) // Only include entries with at least institution or degree
    .map(entry => {
      const detail: EducationDetail = {
        institution: entry.institution || "",
        degree: entry.degree || "",
        start_date: entry.startDate ? convertMonthFormatToDate(entry.startDate) : "",
      };

      // Only add end_date if it has a value
      if (entry.endDate) {
        detail.end_date = convertMonthFormatToDate(entry.endDate);
      }

      // Only add gpa if it has a value and is a valid number
      if (entry.gpa !== "" && !isNaN(parseFloat(entry.gpa))) {
        detail.gpa = parseFloat(entry.gpa);
      }

      return detail;
    });

  return {
    name: frontendData.fullName,
    email: frontendData.email,
    github_user: frontendData.github,
    linkedin: frontendData.linkedin || null,
    education: frontendData.educationEntries[0]?.degree || "", // Use first degree as main education level
    industry: frontendData.industry || "",
    job_title: frontendData.jobTitle || "",
    personal_summary: frontendData.personalSummary || null,
    education_details: educationDetails.length > 0 ? educationDetails : null,
  };
}

function cloneProfileData(data: ProfileData): ProfileData {
  return {
    ...data,
    educationEntries: data.educationEntries.map((e) => ({ ...e })),
  };
}

function formatMonthLabel(monthStr: string): string {
  if (!monthStr) return "";
  const parts = monthStr.split("-");
  if (parts.length < 2) return monthStr;
  const date = new Date(Number(parts[0]), Number(parts[1]) - 1);
  return date.toLocaleDateString("en-US", { year: "numeric", month: "short" });
}

// Convert "2024-01" to "2024-01-01" format
function convertMonthFormatToDate(monthStr: string): string {
  return monthStr ? `${monthStr}-01` : "";
}

// Convert "2024-01-01" to "2024-01" format
function convertDateToMonthFormat(dateStr: string): string {
  if (!dateStr) return "";
  const parts = dateStr.split('-');
  return `${parts[0]}-${parts[1]}`;
}

// Module-level cache: loaded once, shared across all InstitutionAutocomplete instances
// This means re-opening the modal or adding a second education entry won't re-fetch
let institutionCache: Institution[] | null = null;
let institutionCachePromise: Promise<Institution[]> | null = null;

async function loadAllInstitutions(): Promise<Institution[]> {
  if (institutionCache) return institutionCache;
  // Deduplicate concurrent calls — if a fetch is already in-flight, reuse it
  if (!institutionCachePromise) {
    institutionCachePromise = getAllInstitutions()
      .then((res) => {
        // getAllInstitutions returns { institutions: string[] } from the /list endpoint
        // Normalise to Institution[] shape
        const raw = res.institutions as unknown as (string | Institution)[];
        institutionCache = raw.map((item) =>
          typeof item === "string" ? { name: item } : item
        );
        return institutionCache;
      })
      .catch((err) => {
        console.error("Failed to load institution list:", err);
        institutionCachePromise = null; // Allow retry on next focus
        return [];
      });
  }
  return institutionCachePromise;
}

// Client-side filter: returns institutions whose name contains the query (case-insensitive)
// Prioritises names that START WITH the query so they appear first
function filterInstitutions(all: Institution[], query: string): Institution[] {
  if (!query.trim()) return all;
  const lower = query.toLowerCase();
  const startsWith: Institution[] = [];
  const contains: Institution[] = [];
  for (const inst of all) {
    const name = inst.name.toLowerCase();
    if (name.startsWith(lower)) startsWith.push(inst);
    else if (name.includes(lower)) contains.push(inst);
  }
  return [...startsWith, ...contains];
}

// Institution Autocomplete Component
interface InstitutionAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

function InstitutionAutocomplete({ value, onChange, placeholder, autoFocus }: InstitutionAutocompleteProps) {
  const [searchTerm, setSearchTerm] = useState(value);
  const [allInstitutions, setAllInstitutions] = useState<Institution[]>(institutionCache ?? []);
  const [suggestions, setSuggestions] = useState<Institution[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Sync value prop → searchTerm when parent updates externally
  useEffect(() => {
    setSearchTerm(value);
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && listRef.current) {
      const item = listRef.current.children[highlightedIndex] as HTMLElement;
      item?.scrollIntoView({ block: 'nearest' });
    }
  }, [highlightedIndex]);

  const openWithAll = async () => {
    // If already loaded, show immediately
    if (institutionCache) {
      const filtered = filterInstitutions(institutionCache, searchTerm);
      setSuggestions(filtered);
      setIsOpen(true);
      setHighlightedIndex(-1);
      return;
    }
    // Otherwise fetch (first focus only)
    setLoading(true);
    const all = await loadAllInstitutions();
    setAllInstitutions(all);
    const filtered = filterInstitutions(all, searchTerm);
    setSuggestions(filtered);
    setIsOpen(true);
    setHighlightedIndex(-1);
    setLoading(false);
  };

  const handleFocus = () => {
    openWithAll();
  };

  const handleInputChange = (newValue: string) => {
    setSearchTerm(newValue);
    onChange(newValue);
    setHighlightedIndex(-1);

    const pool = institutionCache ?? allInstitutions;
    if (pool.length > 0) {
      // Instant client-side filter — no network call needed
      setSuggestions(filterInstitutions(pool, newValue));
      setIsOpen(true);
    } else {
      // Cache not ready yet (very fast typer) — open will arrive when fetch resolves
      openWithAll();
    }
  };

  const handleSelect = (institution: Institution) => {
    setSearchTerm(institution.name);
    onChange(institution.name);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && highlightedIndex >= 0) {
      e.preventDefault();
      handleSelect(suggestions[highlightedIndex]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  // Highlight matching substring in the name
  const highlightMatch = (name: string, query: string) => {
    if (!query.trim()) return <>{name}</>;
    const idx = name.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return <>{name}</>;
    return (
      <>
        {name.slice(0, idx)}
        <strong className="autocomplete-highlight">{name.slice(idx, idx + query.length)}</strong>
        {name.slice(idx + query.length)}
      </>
    );
  };

  return (
    <div className="autocomplete-wrapper" ref={wrapperRef}>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => handleInputChange(e.target.value)}
        onFocus={handleFocus}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="input-field"
        autoFocus={autoFocus}
        autoComplete="off"
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      />
      {loading && <div className="autocomplete-loading">Loading institutions...</div>}
      {isOpen && suggestions.length > 0 && (
        <div className="autocomplete-dropdown" role="listbox" ref={listRef}>
          {suggestions.map((institution, index) => (
            <div
              key={institution.name}
              className={`autocomplete-item${index === highlightedIndex ? ' highlighted' : ''}`}
              role="option"
              aria-selected={index === highlightedIndex}
              onMouseDown={(e) => {
                // Use mousedown so it fires before onBlur closes the dropdown
                e.preventDefault();
                handleSelect(institution);
              }}
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              <div className="institution-name">
                {highlightMatch(institution.name, searchTerm)}
              </div>
            </div>
          ))}
        </div>
      )}
      {isOpen && !loading && suggestions.length === 0 && (
        <div className="autocomplete-dropdown">
          <div className="autocomplete-empty">No institutions found — you can still type your institution name</div>
        </div>
      )}
    </div>
  );
}

interface EducationCardProps {
  entry: EducationEntry;
  onSave: (updated: EducationEntry) => void;
  onDelete: () => void;
  isNew?: boolean;
}

function EducationCard({ entry, onSave, onDelete, isNew }: EducationCardProps) {
  const [editing, setEditing] = useState(isNew ?? false);
  const [draft, setDraft] = useState<EducationEntry>(entry);

  const handleSave = () => {
    onSave(draft);
    setEditing(false);
  };

  const handleCancel = () => {
    if (isNew && !entry.institution) {
      onDelete();
      return;
    }
    setDraft(entry);
    setEditing(false);
  };

  const formatDate = (d: string) => {
    if (!d) return "";
    const [year, month] = d.split("-");
    const date = new Date(Number(year), Number(month) - 1);
    return date.toLocaleDateString("en-US", { year: "numeric", month: "short" });
  };

  if (editing) {
    return (
      <div className="education-card editing">
        <div className="form-field">
          <label className="field-label">Institution</label>
          <InstitutionAutocomplete
            value={draft.institution}
            onChange={(value) => setDraft({ ...draft, institution: value })}
            placeholder="e.g. MIT"
            autoFocus
          />
        </div>

        <div className="form-field">
          <label className="field-label">Degree</label>
          <input
            type="text"
            value={draft.degree}
            onChange={(e) => setDraft({ ...draft, degree: e.target.value })}
            placeholder="e.g. B.S. Computer Science"
            className="input-field"
          />
        </div>


        <div className="date-row">
          <div className="form-field">
            <label className="field-label">Start Date</label>
            <input
              type="month"
              value={draft.startDate}
              onChange={(e) => setDraft({ ...draft, startDate: e.target.value })}
              className="input-field"
            />
          </div>
          <div className="form-field">
            <label className="field-label">End Date</label>
            <input
              type="month"
              value={draft.endDate}
              onChange={(e) => setDraft({ ...draft, endDate: e.target.value })}
              className="input-field"
            />
          </div>
        </div>

        <div className="form-field gpa-field">
          <label className="field-label">GPA</label>
          <input
            type="text"
            value={draft.gpa}
            onChange={(e) => setDraft({ ...draft, gpa: e.target.value })}
            placeholder="e.g. 3.8"
            className="input-field"
          />
        </div>

        <div className="card-actions">
          <button type="button" onClick={handleSave} className="btn btn-primary">
            <CheckIcon />
            Save
          </button>
          <button type="button" onClick={handleCancel} className="btn btn-secondary">
            <XIcon />
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="education-card">
      <div className="card-content">
        <p className="card-title">
          {entry.institution || "Untitled Institution"}
        </p>
        <p className="card-subtitle">
          {entry.degree || "No degree specified"}
        </p>
        <p className="card-meta">
          {formatDate(entry.startDate)}
          {entry.startDate && entry.endDate ? " - " : ""}
          {formatDate(entry.endDate)}
          {entry.gpa && (
            <span className="gpa-badge">GPA: {entry.gpa}</span>
          )}
        </p>
      </div>
      <div className="card-buttons">
        <button
          type="button"
          onClick={() => setEditing(true)}
          className="icon-btn"
          aria-label="Edit education entry"
        >
          <PencilIcon />
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="icon-btn delete-btn"
          aria-label="Delete education entry"
        >
          <TrashIcon />
        </button>
      </div>
    </div>
  );
}

function ProfileFieldReadonly({ label, value }: { label: string; value: string }) {
  const display = value?.trim() ? value : "—";
  return (
    <div className="profile-view-field">
      <span className="profile-view-field__label">{label}</span>
      <p className="profile-view-field__value">{display}</p>
    </div>
  );
}

function LearningCourseCard({ course }: { course: LearningCourse }) {
  const imgSrc = learningThumbnailSrc(course.thumbnail_url);
  const pricingLabel = course.pricing === 'free' ? 'Free' : 'Paid';
  return (
    <article className="learning-course-card">
      <div className="learning-course-card__thumb-wrap">
        {imgSrc ? (
          <img
            src={imgSrc}
            alt=""
            loading="lazy"
            className="learning-course-card__thumb"
          />
        ) : (
          <div className="learning-course-card__thumb-placeholder" aria-hidden />
        )}
      </div>
      <div className="learning-course-card__body">
        <div className="learning-course-card__meta">
          <span
            className={`learning-course-card__badge learning-course-card__badge--${course.pricing}`}
          >
            {pricingLabel}
          </span>
          <span className="learning-course-card__provider">{course.provider}</span>
        </div>
        <h3 className="learning-course-card__title">{course.title}</h3>
        <p className="learning-course-card__desc">{course.description}</p>
        <a
          href={course.url}
          target="_blank"
          rel="noopener noreferrer"
          className="learning-course-card__cta"
        >
          Open course
        </a>
      </div>
    </article>
  );
}

type ProfileMainTab = 'profile' | 'learning';

type LearningBlockedReason = 'first-time' | 'no-projects';

export default function UserPreferencePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pictureUploading, setPictureUploading] = useState(false);
  const [pictureError, setPictureError] = useState<string | null>(null);
  const [profilePicture, setProfilePicture] = useState<string | null>(null);

  const [profileData, setProfileData] = useState<ProfileData>({
    fullName: "",
    email: "",
    github: "",
    linkedin: "",
    jobTitle: "",
    industry: null,
    personalSummary: "",
    educationEntries: [],
  });

  const [newEntryId, setNewEntryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  // True when no preferences exist yet (first-time user arriving from consent flow)
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(false);

  const [mainTab, setMainTab] = useState<ProfileMainTab>('profile');
  const [learningLoading, setLearningLoading] = useState(false);
  const [learningError, setLearningError] = useState<string | null>(null);
  const [learningData, setLearningData] = useState<LearningRecommendationsResponse | null>(null);
  const [learningBlocked, setLearningBlocked] = useState<LearningBlockedReason | null>(null);

  /** Saved snapshot for cancel + view mode; returning users start in view mode (not editing). */
  const [lastSavedProfileData, setLastSavedProfileData] = useState<ProfileData | null>(null);
  const [savedPictureDisplayUrl, setSavedPictureDisplayUrl] = useState<string | null>(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  // Load user preferences on component mount
  useEffect(() => {
    loadUserPreferences();
  }, []);

  // Deep link from dashboard: /userpreferencepage?tab=learning
  useEffect(() => {
    if (searchParams.get('tab') === 'learning') {
      setMainTab('learning');
      const next = new URLSearchParams(searchParams);
      next.delete('tab');
      setSearchParams(next, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    if (mainTab !== 'learning') return;
    if (loading) return;

    let cancelled = false;
    setLearningError(null);
    setLearningData(null);
    setLearningBlocked(null);

    const run = async () => {
      if (isFirstTimeUser) {
        setLearningLoading(false);
        setLearningBlocked('first-time');
        return;
      }

      setLearningLoading(true);
      try {
        const projects = await getProjects();
        if (cancelled) return;
        if (projects.length === 0) {
          setLearningBlocked('no-projects');
          setLearningLoading(false);
          return;
        }
        const data = await getLearningRecommendations();
        if (!cancelled) setLearningData(data);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Could not load recommendations.';
        if (!cancelled) {
          setLearningError(msg);
          setLearningData(null);
        }
      } finally {
        if (!cancelled) setLearningLoading(false);
      }
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [mainTab, loading, isFirstTimeUser]);

  const loadUserPreferences = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use consent status as the authoritative "first-time user" signal.
      // A user who has consented but not yet saved preferences is first-time.
      // A user who has consented AND has saved preferences is returning.
      // consentChecked tracks whether the lookup actually succeeded — if it
      // failed we cannot safely derive first-time status from it.
      let hasConsent = false;
      let consentChecked = false;
      try {
        const consentStatus = await getConsentStatus();
        hasConsent = consentStatus.has_consent;
        consentChecked = true;
      } catch {
        // Consent check failed — we'll fall back to a safe default below.
      }

      try {
        const backendData = await getUserPreferences();
        const frontendData = convertToFrontend(backendData);
        setProfileData(frontendData);
        setLastSavedProfileData(cloneProfileData(frontendData));
        // Load profile picture — if a path is stored in the DB, use the API endpoint as img src
        if (backendData.profile_picture_path) {
          const pic = `${getProfilePictureUrl()}?t=${Date.now()}`;
          setProfilePicture(pic);
          setSavedPictureDisplayUrl(pic);
        } else {
          setProfilePicture(null);
          setSavedPictureDisplayUrl(null);
        }
        // Has saved preferences → definitely a returning user (view mode, not editing)
        setIsFirstTimeUser(false);
        setIsEditingProfile(false);
      } catch (err: any) {
        // Only treat a 404 (no preferences saved yet) as a first-time situation.
        // Any other error (500, network failure, etc.) is a real error.
        const is404 = err?.message?.includes("No user preferences found");
        if (is404) {
          if (consentChecked) {
            // Consent lookup succeeded — use it as the source of truth.
            setIsFirstTimeUser(hasConsent);
          } else {
            // Consent lookup failed — we can't be sure, so default to first-time
            // (safer: first-timers go to /uploadpage which is always valid).
            setIsFirstTimeUser(true);
          }
          setLastSavedProfileData(null);
          setSavedPictureDisplayUrl(null);
          setIsEditingProfile(true);
          // No error banner for a missing-preferences 404 — blank form is expected.
        } else {
          // Real error (500, network, etc.) — show edit form so they can retry after refresh.
          setError("Could not load your preferences. Please try again.");
          setIsEditingProfile(true);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof ProfileData, value: string | null) => {
    setProfileData({ ...profileData, [field]: value });
  };

  const addEducation = () => {
    const entry = createEmptyEntry();
    setNewEntryId(entry.id);
    setProfileData({
      ...profileData,
      educationEntries: [...profileData.educationEntries, entry],
    });
  };

  const updateEducation = (updated: EducationEntry) => {
    setNewEntryId(null);
    setProfileData({
      ...profileData,
      educationEntries: profileData.educationEntries.map((e) =>
        e.id === updated.id ? updated : e
      ),
    });
  };

  const deleteEducation = (id: string) => {
    setNewEntryId(null);
    setProfileData({
      ...profileData,
      educationEntries: profileData.educationEntries.filter((e) => e.id !== id),
    });
  };

  const handlePictureFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPictureError(null);
    setPictureUploading(true);
    try {
      await uploadProfilePicture(file);
      // Cache the URL so the browser fetches the new file from the server
      setProfilePicture(`${getProfilePictureUrl()}?t=${Date.now()}`);
    } catch (err: any) {
      setPictureError(err?.message ?? "Failed to upload picture. Please try again.");
    } finally {
      setPictureUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleRemovePicture = async () => {
    setPictureError(null);
    setPictureUploading(true);
    try {
      await deleteProfilePicture();
      setProfilePicture(null);
    } catch (err: any) {
      setPictureError(err?.message ?? "Failed to remove picture.");
    } finally {
      setPictureUploading(false);
    }
  };

  const handleCancelEdit = () => {
    if (lastSavedProfileData) {
      setProfileData(cloneProfileData(lastSavedProfileData));
    }
    setProfilePicture(savedPictureDisplayUrl);
    setNewEntryId(null);
    setError(null);
    setPictureError(null);
    setIsEditingProfile(false);
  };

  const handleSave = async () => {
    const wasFirstTime = isFirstTimeUser;
    try {
      setSaving(true);
      setError(null);

      const backendData = convertToBackend(profileData);
      await saveUserPreferences(backendData);
      notifyUserPreferencesUpdated();

      setLastSavedProfileData(cloneProfileData(profileData));
      setSavedPictureDisplayUrl(profilePicture);
      setIsFirstTimeUser(false);
      setIsEditingProfile(false);
      setShowSuccess(true);

      if (wasFirstTime) {
        setTimeout(() => {
          navigate("/uploadpage");
        }, 2000);
      } else {
        setTimeout(() => setShowSuccess(false), 2800);
      }
    } catch (err: any) {
      console.error("Failed to save user preferences:", err);
      const errorMessage = err?.message || "Failed to save your preferences. Please try again.";
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="user-preference-page">
        <div className="preference-container">
          <div className="loading-state">Loading your preferences...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-preference-page">
      <div className="preference-container">
        <button
          type="button"
          className="project-selection__back"
          onClick={() => navigate(-1)}
        >
          <span className="project-selection__back-chevron" aria-hidden>
            ‹
          </span>
          Back
        </button>
        <h1 className="page-title">
          {mainTab === 'learning'
            ? 'Learning recommendations'
            : isFirstTimeUser
              ? 'Build your Profile'
              : isEditingProfile
                ? 'Edit your profile'
                : 'Your profile'}
        </h1>

        <div className="profile-page-tabs" role="tablist" aria-label="Profile sections">
          <button
            type="button"
            role="tab"
            id="tab-profile"
            aria-selected={mainTab === 'profile'}
            aria-controls="profile-panel"
            className={`profile-page-tab${mainTab === 'profile' ? ' profile-page-tab--active' : ''}`}
            onClick={() => setMainTab('profile')}
          >
            Profile
          </button>
          <button
            type="button"
            role="tab"
            id="tab-learning"
            aria-selected={mainTab === 'learning'}
            aria-controls="learning-panel"
            className={`profile-page-tab${mainTab === 'learning' ? ' profile-page-tab--active' : ''}`}
            onClick={() => setMainTab('learning')}
          >
            Learning
          </button>
        </div>

        {mainTab === 'learning' && (
          <div
            id="learning-panel"
            role="tabpanel"
            aria-labelledby="tab-learning"
            className="learning-recommendations-panel"
          >
            {learningBlocked === 'first-time' && !learningLoading && (
              <div className="learning-recommendations-placeholder" role="status">
                <p className="learning-recommendations-placeholder__title">Upload projects to get recommendations</p>
                <p className="learning-recommendations-placeholder__text">
                  Learning suggestions use skills and experience from analyzed projects. Finish setting up your
                  profile, then upload at least one project so we can match courses to you.
                </p>
                <button type="button" className="btn btn-primary learning-recommendations-placeholder__cta" onClick={() => navigate('/uploadpage')}>
                  Upload projects
                </button>
              </div>
            )}
            {learningBlocked === 'no-projects' && !learningLoading && (
              <div className="learning-recommendations-placeholder" role="status">
                <p className="learning-recommendations-placeholder__title">No projects found!</p>
                <p className="learning-recommendations-placeholder__text">
                  Upload projects to get insights on recommended courses for yourself!
                </p>
                <button type="button" className="btn btn-primary learning-recommendations-placeholder__cta" onClick={() => navigate('/uploadpage')}>
                  Upload projects
                </button>
              </div>
            )}
            {!learningBlocked && (
            <p className="learning-recommendations-disclosure">
              Suggestions are generated from your saved profile and master resume data (skills, projects,
              summary, job title, and industry). Course links open external sites in a new tab.
            </p>
            )}
            {learningLoading && (
              <div className="learning-recommendations-state">Loading recommendations…</div>
            )}
            {learningError && !learningLoading && (
              <div className="error-message learning-recommendations-error" role="alert">
                {learningError}
              </div>
            )}
            {!learningLoading && !learningError && !learningBlocked && learningData && (
              <>
                <section className="learning-recommendations-section" aria-labelledby="learning-based-heading">
                  <h2 id="learning-based-heading" className="learning-recommendations-heading">
                    Based on your data
                  </h2>
                  <div className="learning-course-grid">
                    {learningData.based_on_resume.map((c) => (
                      <LearningCourseCard key={c.id} course={c} />
                    ))}
                  </div>
                </section>
                <section className="learning-recommendations-section" aria-labelledby="learning-next-heading">
                  <h2 id="learning-next-heading" className="learning-recommendations-heading">
                    Next steps
                  </h2>
                  <div className="learning-course-grid">
                    {learningData.next_steps.map((c) => (
                      <LearningCourseCard key={c.id} course={c} />
                    ))}
                  </div>
                </section>
              </>
            )}
          </div>
        )}

        {mainTab === 'profile' && (
          <div id="profile-panel" role="tabpanel" aria-labelledby="tab-profile">
            {showSuccess && (
              <div className="notification success" role="status">
                <p>Profile saved successfully!</p>
              </div>
            )}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {!isEditingProfile && !isFirstTimeUser ? (
              <>
                <div className="profile-picture-section profile-picture-section--readonly">
                  <div className="profile-picture-avatar profile-picture-avatar--readonly">
                    {profilePicture ? (
                      <img src={profilePicture} alt="" className="profile-picture-img" />
                    ) : (
                      <div className="profile-picture-placeholder">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>

                <div className="profile-view-section">
                  <ProfileFieldReadonly label="Full name" value={profileData.fullName} />
                  <ProfileFieldReadonly label="Email" value={profileData.email} />
                  <ProfileFieldReadonly label="GitHub username" value={profileData.github} />
                  <ProfileFieldReadonly label="LinkedIn profile" value={profileData.linkedin} />
                  <ProfileFieldReadonly label="Job title" value={profileData.jobTitle} />
                  <div className="profile-view-field">
                    <span className="profile-view-field__label">Professional summary</span>
                    <p className="profile-view-field__value profile-view-field__value--multiline">
                      {profileData.personalSummary?.trim() ? profileData.personalSummary : "—"}
                    </p>
                  </div>
                  <div className="profile-view-field">
                    <span className="profile-view-field__label">Educational background</span>
                    {profileData.educationEntries.length === 0 ? (
                      <p className="profile-view-field__value">No education entries saved.</p>
                    ) : (
                      <div className="profile-view-education-list">
                        {profileData.educationEntries.map((entry) => (
                          <div key={entry.id} className="profile-view-education-card">
                            <p className="profile-view-education-card__school">{entry.institution || "—"}</p>
                            <p className="profile-view-education-card__degree">{entry.degree || "—"}</p>
                            <p className="profile-view-education-card__dates">
                              {entry.startDate || entry.endDate
                                ? [formatMonthLabel(entry.startDate), formatMonthLabel(entry.endDate)]
                                    .filter(Boolean)
                                    .join(" – ") || "—"
                                : "—"}
                            </p>
                            {entry.gpa ? (
                              <p className="profile-view-education-card__gpa">GPA: {entry.gpa}</p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <ProfileFieldReadonly label="Industry" value={profileData.industry ?? ""} />
                </div>

                <div className="save-section">
                  <button
                    type="button"
                    className="btn btn-save"
                    onClick={() => {
                      setError(null);
                      setPictureError(null);
                      setIsEditingProfile(true);
                    }}
                  >
                    Edit profile
                  </button>
                </div>
              </>
            ) : (
              <>
        <div className="profile-picture-section">
          <div
            className="profile-picture-avatar"
            onClick={() => !pictureUploading && fileInputRef.current?.click()}
            title={profilePicture ? "Click to change photo" : "Click to upload photo"}
          >
            {profilePicture ? (
              <img src={profilePicture} alt="Profile" className="profile-picture-img" />
            ) : (
              <div className="profile-picture-placeholder">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            )}
            <div className="profile-picture-overlay">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                <circle cx="12" cy="13" r="4" />
              </svg>
            </div>
          </div>
          <div className="profile-picture-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={pictureUploading}
            >
              {pictureUploading ? "Uploading..." : profilePicture ? "Change Photo" : "Upload Photo"}
            </button>
            {profilePicture && (
              <button
                type="button"
                className="btn btn-danger-outline"
                onClick={handleRemovePicture}
                disabled={pictureUploading}
              >
                Remove
              </button>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            style={{ display: "none" }}
            onChange={handlePictureFileChange}
          />
          {pictureError && <p className="profile-picture-error">{pictureError}</p>}
        </div>

        <div className="form-section">
          {/* Full Name */}
          <div className="form-field">
            <label className="field-label" htmlFor="fullName">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              value={profileData.fullName}
              onChange={(e) => updateField("fullName", e.target.value)}
              className="input-field"
              placeholder="Enter your full name"
            />
          </div>

          {/* Email */}
          <div className="form-field">
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={profileData.email}
              onChange={(e) => updateField("email", e.target.value)}
              className="input-field"
              placeholder="your.email@example.com"
            />
          </div>

          {/* GitHub Username */}
          <div className="form-field">
            <label className="field-label" htmlFor="github">
              GitHub username (optional)
            </label>
            <input
              id="github"
              type="text"
              value={profileData.github}
              onChange={(e) => updateField("github", e.target.value)}
              className="input-field"
              placeholder="your-github-username"
            />
          </div>

          {/* LinkedIn Profile */}
          <div className="form-field">
            <label className="field-label" htmlFor="linkedin">
              LinkedIn profile (optional)
            </label>
            <input
              id="linkedin"
              type="text"
              value={profileData.linkedin}
              onChange={(e) => updateField("linkedin", e.target.value)}
              className="input-field"
              placeholder="linkedin.com/in/your-profile"
            />
          </div>

          {/* Job Title */}
          <div className="form-field">
            <label className="field-label" htmlFor="jobTitle">
              Job Title (Aspiring or Current)
            </label>
            <input
              id="jobTitle"
              type="text"
              value={profileData.jobTitle}
              onChange={(e) => updateField("jobTitle", e.target.value)}
              className="input-field"
              placeholder="e.g., Software Engineer, Data Scientist"
            />
          </div>

          {/* Personal Summary */}
          <div className="form-field">
            <label className="field-label" htmlFor="personalSummary">
              Professional Summary (optional)
            </label>
            <textarea
              id="personalSummary"
              value={profileData.personalSummary}
              onChange={(e) => updateField("personalSummary", e.target.value)}
              className="input-field textarea-field"
              placeholder="Write a brief professional summary that will appear on your resume..."
              rows={4}
              maxLength={500}
            />
            <span className="field-hint">
              {profileData.personalSummary.length}/500 characters
            </span>
          </div>

          {/* Educational Background */}
          <div className="education-section">
            <div className="section-header">
              <label className="field-label">Educational Background</label>
              <button type="button" onClick={addEducation} className="btn btn-add">
                <PlusIcon />
                Add
              </button>
            </div>

            {profileData.educationEntries.length === 0 && (
              <button type="button" onClick={addEducation} className="empty-state">
                <PlusIcon />
                <p>Add your first education entry</p>
              </button>
            )}

            <div className="education-list">
              {profileData.educationEntries.map((entry) => (
                <EducationCard
                  key={entry.id}
                  entry={entry}
                  isNew={entry.id === newEntryId}
                  onSave={updateEducation}
                  onDelete={() => deleteEducation(entry.id)}
                />
              ))}
            </div>
          </div>

          {/* Industry */}
          <div className="form-field">
            <label className="field-label">Industry</label>
            <div className="industry-buttons">
              {INDUSTRIES.map((industry) => (
                <button
                  key={industry}
                  type="button"
                  onClick={() =>
                    updateField("industry", profileData.industry === industry ? null : industry)
                  }
                  className={`industry-btn ${
                    profileData.industry === industry ? "selected" : ""
                  }`}
                >
                  {industry}
                </button>
              ))}
            </div>
          </div>

          {/* Save / Cancel */}
          <div className={`save-section${!isFirstTimeUser ? " save-section--with-cancel" : ""}`}>
            {!isFirstTimeUser && (
              <button type="button" className="btn btn-secondary" onClick={handleCancelEdit} disabled={saving}>
                Cancel
              </button>
            )}
            <button
              type="button"
              onClick={handleSave}
              className="btn btn-save"
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </div>
        </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}