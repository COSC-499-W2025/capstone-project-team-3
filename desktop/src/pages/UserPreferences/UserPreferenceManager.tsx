import { useState, useEffect } from "react";
import { getUserPreferences, saveUserPreferences, searchInstitutions } from "../../api/userPreferences";
import type { UserPreferences, EducationDetail, Institution } from "../../api/userPreferences_types";
import "./UserPreferenceManager.css";

export const UserPreferenceManager = () => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    name: "",
    email: "",
    github_user: "",
    education: "Bachelor's",
    industry: "",
    job_title: "",
    education_details: [],
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Institution search
  const [institutionQuery, setInstitutionQuery] = useState("");
  const [institutionResults, setInstitutionResults] = useState<Institution[]>([]);
  const [showInstitutionDropdown, setShowInstitutionDropdown] = useState(false);
  const [searchingInstitutions, setSearchingInstitutions] = useState(false);

  // Load user preferences on mount
  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getUserPreferences();
      setPreferences(data);
      setIsEditing(false);
    } catch (err) {
      if (err instanceof Error && err.message.includes("No user preferences found")) {
        // First time user - enable editing mode
        setIsEditing(true);
      } else {
        setError(err instanceof Error ? err.message : "Failed to load preferences");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      await saveUserPreferences(preferences);
      
      setSuccessMessage("Preferences saved successfully!");
      setIsEditing(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    loadPreferences(); // Reload original data
    setIsEditing(false);
    setError(null);
  };

  const handleInputChange = (field: keyof UserPreferences, value: string) => {
    setPreferences((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAddEducation = () => {
    const newEducation: EducationDetail = {
      institution: "",
      degree: "",
      program: "",
      start_date: "",
      end_date: null,
      gpa: null,
    };
    
    setPreferences((prev) => ({
      ...prev,
      education_details: [...(prev.education_details || []), newEducation],
    }));
  };

  const handleRemoveEducation = (index: number) => {
    setPreferences((prev) => ({
      ...prev,
      education_details: prev.education_details?.filter((_, i) => i !== index) || [],
    }));
  };

  const handleEducationDetailChange = (
    index: number,
    field: keyof EducationDetail,
    value: string | number | null
  ) => {
    setPreferences((prev) => {
      const updatedDetails = [...(prev.education_details || [])];
      updatedDetails[index] = {
        ...updatedDetails[index],
        [field]: value,
      };
      return {
        ...prev,
        education_details: updatedDetails,
      };
    });
  };

  // Institution search with debouncing
  useEffect(() => {
    if (institutionQuery.length < 2) {
      setInstitutionResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setSearchingInstitutions(true);
        const response = await searchInstitutions(institutionQuery, 20, true);
        setInstitutionResults(response.institutions);
        setShowInstitutionDropdown(true);
      } catch (err) {
        console.error("Failed to search institutions:", err);
      } finally {
        setSearchingInstitutions(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [institutionQuery]);

  const handleSelectInstitution = (institutionName: string, eduIndex: number) => {
    handleEducationDetailChange(eduIndex, "institution", institutionName);
    setInstitutionQuery("");
    setShowInstitutionDropdown(false);
  };

  if (loading) {
    return (
      <div className="user-pref-container">
        <div className="user-pref-loading">Loading preferences...</div>
      </div>
    );
  }

  return (
    <div className="user-pref-container">
      <div className="user-pref-header">
        <h1 className="user-pref-title">User Preferences</h1>
        {!isEditing && (
          <button
            type="button"
            className="user-pref-btn user-pref-btn--edit"
            onClick={() => setIsEditing(true)}
          >
            ✏️ Edit Profile
          </button>
        )}
      </div>

      {error && (
        <div className="user-pref-alert user-pref-alert--error">
          ❌ {error}
        </div>
      )}

      {successMessage && (
        <div className="user-pref-alert user-pref-alert--success">
          ✅ {successMessage}
        </div>
      )}

      <div className="user-pref-form">
        {/* Basic Information Section */}
        <section className="user-pref-section">
          <h2 className="user-pref-section-title">Basic Information</h2>
          
          <div className="user-pref-field">
            <label className="user-pref-label">Name</label>
            {isEditing ? (
              <input
                type="text"
                className="user-pref-input"
                value={preferences.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter your full name"
              />
            ) : (
              <div className="user-pref-value">{preferences.name || "—"}</div>
            )}
          </div>

          <div className="user-pref-field">
            <label className="user-pref-label">Email</label>
            {isEditing ? (
              <input
                type="email"
                className="user-pref-input"
                value={preferences.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                placeholder="your.email@example.com"
              />
            ) : (
              <div className="user-pref-value">{preferences.email || "—"}</div>
            )}
          </div>

          <div className="user-pref-field">
            <label className="user-pref-label">GitHub Username</label>
            {isEditing ? (
              <input
                type="text"
                className="user-pref-input"
                value={preferences.github_user}
                onChange={(e) => handleInputChange("github_user", e.target.value)}
                placeholder="your-github-username"
              />
            ) : (
              <div className="user-pref-value">{preferences.github_user || "—"}</div>
            )}
          </div>
        </section>

        {/* Professional Information Section */}
        <section className="user-pref-section">
          <h2 className="user-pref-section-title">Professional Information</h2>

          <div className="user-pref-field">
            <label className="user-pref-label">Education Level</label>
            {isEditing ? (
              <select
                className="user-pref-select"
                value={preferences.education}
                onChange={(e) => handleInputChange("education", e.target.value)}
              >
                <option value="High School">High School</option>
                <option value="Associate's">Associate's</option>
                <option value="Bachelor's">Bachelor's</option>
                <option value="Master's">Master's</option>
                <option value="PhD">PhD</option>
                <option value="Other">Other</option>
              </select>
            ) : (
              <div className="user-pref-value">{preferences.education || "—"}</div>
            )}
          </div>

          <div className="user-pref-field">
            <label className="user-pref-label">Industry</label>
            {isEditing ? (
              <input
                type="text"
                className="user-pref-input"
                value={preferences.industry}
                onChange={(e) => handleInputChange("industry", e.target.value)}
                placeholder="e.g., Software Development, Finance, Healthcare"
              />
            ) : (
              <div className="user-pref-value">{preferences.industry || "—"}</div>
            )}
          </div>

          <div className="user-pref-field">
            <label className="user-pref-label">Job Title</label>
            {isEditing ? (
              <input
                type="text"
                className="user-pref-input"
                value={preferences.job_title}
                onChange={(e) => handleInputChange("job_title", e.target.value)}
                placeholder="e.g., Software Engineer, Data Analyst"
              />
            ) : (
              <div className="user-pref-value">{preferences.job_title || "—"}</div>
            )}
          </div>
        </section>

        {/* Education Details Section */}
        <section className="user-pref-section">
          <div className="user-pref-section-header">
            <h2 className="user-pref-section-title">Education History</h2>
            {isEditing && (
              <button
                type="button"
                className="user-pref-btn user-pref-btn--add"
                onClick={handleAddEducation}
              >
                + Add Education
              </button>
            )}
          </div>

          {preferences.education_details && preferences.education_details.length > 0 ? (
            preferences.education_details.map((edu, index) => (
              <div key={index} className="user-pref-edu-card">
                {isEditing && (
                  <button
                    type="button"
                    className="user-pref-edu-remove"
                    onClick={() => handleRemoveEducation(index)}
                    aria-label="Remove education entry"
                  >
                    ✕
                  </button>
                )}

                <div className="user-pref-edu-grid">
                  <div className="user-pref-field">
                    <label className="user-pref-label">Institution</label>
                    {isEditing ? (
                      <div className="user-pref-autocomplete">
                        <input
                          type="text"
                          className="user-pref-input"
                          value={edu.institution}
                          onChange={(e) => {
                            handleEducationDetailChange(index, "institution", e.target.value);
                            setInstitutionQuery(e.target.value);
                          }}
                          onFocus={() => {
                            if (edu.institution.length >= 2) {
                              setInstitutionQuery(edu.institution);
                            }
                          }}
                          placeholder="Search for institution..."
                        />
                        {showInstitutionDropdown && institutionResults.length > 0 && (
                          <div className="user-pref-dropdown">
                            {searchingInstitutions && (
                              <div className="user-pref-dropdown-item user-pref-dropdown-loading">
                                Searching...
                              </div>
                            )}
                            {institutionResults.map((inst, i) => (
                              <button
                                key={i}
                                type="button"
                                className="user-pref-dropdown-item"
                                onClick={() => handleSelectInstitution(inst.name, index)}
                              >
                                {inst.name}
                                {inst.province && <span className="user-pref-dropdown-meta"> — {inst.province}</span>}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="user-pref-value">{edu.institution || "—"}</div>
                    )}
                  </div>

                  <div className="user-pref-field">
                    <label className="user-pref-label">Degree</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="user-pref-input"
                        value={edu.degree}
                        onChange={(e) => handleEducationDetailChange(index, "degree", e.target.value)}
                        placeholder="e.g., Bachelor of Science"
                      />
                    ) : (
                      <div className="user-pref-value">{edu.degree || "—"}</div>
                    )}
                  </div>

                  <div className="user-pref-field">
                    <label className="user-pref-label">Program/Major</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="user-pref-input"
                        value={edu.program}
                        onChange={(e) => handleEducationDetailChange(index, "program", e.target.value)}
                        placeholder="e.g., Computer Science"
                      />
                    ) : (
                      <div className="user-pref-value">{edu.program || "—"}</div>
                    )}
                  </div>

                  <div className="user-pref-field">
                    <label className="user-pref-label">Start Date</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="user-pref-input"
                        value={edu.start_date}
                        onChange={(e) => handleEducationDetailChange(index, "start_date", e.target.value)}
                        placeholder="YYYY or YYYY-MM-DD"
                      />
                    ) : (
                      <div className="user-pref-value">{edu.start_date || "—"}</div>
                    )}
                  </div>

                  <div className="user-pref-field">
                    <label className="user-pref-label">End Date</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="user-pref-input"
                        value={edu.end_date || ""}
                        onChange={(e) => handleEducationDetailChange(index, "end_date", e.target.value || null)}
                        placeholder="YYYY or YYYY-MM-DD (leave empty if ongoing)"
                      />
                    ) : (
                      <div className="user-pref-value">{edu.end_date || "Ongoing"}</div>
                    )}
                  </div>

                  <div className="user-pref-field">
                    <label className="user-pref-label">GPA (optional)</label>
                    {isEditing ? (
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="4.0"
                        className="user-pref-input"
                        value={edu.gpa || ""}
                        onChange={(e) => handleEducationDetailChange(index, "gpa", e.target.value ? parseFloat(e.target.value) : null)}
                        placeholder="0.0 - 4.0"
                      />
                    ) : (
                      <div className="user-pref-value">{edu.gpa ? `${edu.gpa} / 4.0` : "—"}</div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="user-pref-empty">
              No education details added yet.
              {isEditing && " Click 'Add Education' to get started."}
            </div>
          )}
        </section>

        {/* Action Buttons */}
        {isEditing && (
          <div className="user-pref-actions">
            <button
              type="button"
              className="user-pref-btn user-pref-btn--cancel"
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="button"
              className="user-pref-btn user-pref-btn--save"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
