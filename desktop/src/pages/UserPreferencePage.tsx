import { useState, useEffect, useRef } from 'react';
import '../styles/UserPreferencePage.css';
import { 
  getUserPreferences, 
  saveUserPreferences,
  getAllInstitutions,
  type UserPreferences, 
  type EducationDetail,
  type Institution 
} from '../api/userPreferences';

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
    linkedin: "", // LinkedIn not in backend yet TBD
    jobTitle: backendData.job_title || "",
    industry: backendData.industry as typeof INDUSTRIES[number] || null,
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
      if (entry.gpa && !isNaN(parseFloat(entry.gpa))) {
        detail.gpa = parseFloat(entry.gpa);
      }

      return detail;
    });

  return {
    name: frontendData.fullName,
    email: frontendData.email,
    github_user: frontendData.github,
    education: frontendData.educationEntries[0]?.degree || "", // Use first degree as main education level
    industry: frontendData.industry || "",
    job_title: frontendData.jobTitle || "",
    education_details: educationDetails.length > 0 ? educationDetails : null,
  };
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

export default function UserPreferencePage() {
  const [profileData, setProfileData] = useState<ProfileData>({
    fullName: "",
    email: "",
    github: "",
    linkedin: "",
    jobTitle: "",
    industry: null,
    educationEntries: [],
  });

  const [newEntryId, setNewEntryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load user preferences on component mount
  useEffect(() => {
    loadUserPreferences();
  }, []);

  const loadUserPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const backendData = await getUserPreferences();
      const frontendData = convertToFrontend(backendData);
      setProfileData(frontendData);
    } catch (err) {
      console.error("Failed to load user preferences:", err);
      setError("Could not load your preferences. Starting with a blank form.");
      // Continue with empty form
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

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const backendData = convertToBackend(profileData);
      console.log("Sending data to backend:", JSON.stringify(backendData, null, 2));
      
      await saveUserPreferences(backendData);
      
      alert("Profile saved successfully!");
    } catch (err: any) {
      console.error("Failed to save user preferences:", err);
      const errorMessage = err?.message || "Failed to save your preferences. Please try again.";
      setError(errorMessage);
      alert(`Failed to save profile: ${errorMessage}`);
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
        <h1 className="page-title">Build your Profile</h1>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

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

          {/* Save Button */}
          <div className="save-section">
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
      </div>
    </div>
  );
}