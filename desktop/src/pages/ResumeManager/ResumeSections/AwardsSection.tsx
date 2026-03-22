import { Award } from "../../../api/resume_types";

const MONTH_ABBREV = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function formatMonthYear(value?: string): string {
  if (!value) return "";
  // Accept "YYYY-MM" or "YYYY-MM-01"
  if (/^\d{4}-\d{2}$/.test(value)) {
    const [yStr, mStr] = value.split("-");
    const y = Number(yStr);
    const m = Number(mStr);
    if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) return "";
    return `${MONTH_ABBREV[m - 1]} ${y}`;
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [yStr, mStr] = value.split("-").slice(0, 2);
    const y = Number(yStr);
    const m = Number(mStr);
    if (!Number.isFinite(y) || !Number.isFinite(m) || m < 1 || m > 12) return "";
    return `${MONTH_ABBREV[m - 1]} ${y}`;
  }
  return "";
}

function normalizeDetails(details?: string[] | undefined): string[] {
  if (!details) return [];
  return details.map((d) => String(d)).filter((d) => d.trim().length > 0);
}

function detailsTextToList(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.replace(/\r/g, ""));
}

function normalizeDateForInput(value?: string): string {
  if (!value) return "";
  if (/^\d{4}-\d{2}$/.test(value)) return value;
  // Convert YYYY-MM-01 -> YYYY-MM
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.slice(0, 7);
  return "";
}

export function AwardsSection({
  awards,
  isEditing = false,
  onChange,
}: {
  awards: Award[];
  isEditing?: boolean;
  onChange?: (awards: Award[]) => void;
}) {
  const updateAward = (index: number, patch: Partial<Award>) => {
    const next = awards.map((a, i) => (i === index ? { ...a, ...patch } : a));
    onChange?.(next);
  };

  const addAward = () => {
    const next = [
      ...awards,
      { title: "", issuer: "", date: "", details: [] } as Award,
    ];
    onChange?.(next);
  };

  const removeAward = (index: number) => {
    const next = awards.filter((_, i) => i !== index);
    onChange?.(next);
  };

  return (
    <section className="resume-preview__section">
      <div className="resume-preview__heading-row">
        <h2 className="resume-preview__heading">Awards & Honours</h2>
        {isEditing && (
          <button
            type="button"
            onClick={addAward}
            className="resume-preview__add-project-btn"
          >
            Add an award
          </button>
        )}
      </div>

      {awards.length === 0 && !isEditing && (
        <p style={{ margin: "4px 0 0 0", fontStyle: "italic", color: "#666" }}>
          No awards added.
        </p>
      )}

      {awards.length === 0 && isEditing && (
        <p style={{ margin: "4px 0 0 0", fontStyle: "italic", color: "#666" }}>
          Add your awards & honours below.
        </p>
      )}

      {awards.map((award, index) => {
        const formattedDate = formatMonthYear(award.date);
        const issuer = award.issuer?.trim() ?? "";
        const detailsList = normalizeDetails(award.details);
        const detailsText = (award.details ?? []).map((d) => String(d)).join("\n");

        return (
          <div key={index} style={{ marginTop: 8 }}>
            {isEditing ? (
              <div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <input
                    type="text"
                    value={award.title}
                    placeholder="Award title (required)"
                    style={{ flex: 1, fontFamily: "inherit", fontSize: "11pt" }}
                    onChange={(e) => updateAward(index, { title: e.target.value })}
                  />
                  <div className="resume-preview__project-header-right">
                    <button
                      type="button"
                      aria-label="Remove award"
                      onClick={() => removeAward(index)}
                      className="resume-preview__project-delete-btn"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 6 }}>
                  <input
                    type="text"
                    value={award.issuer ?? ""}
                    placeholder="Issuer / organization"
                    style={{ flex: 1, fontFamily: "inherit", fontSize: "11pt" }}
                    onChange={(e) => updateAward(index, { issuer: e.target.value })}
                  />

                  <input
                    type="month"
                    value={normalizeDateForInput(award.date)}
                    aria-label="Award date (month-year)"
                    style={{ fontFamily: "inherit", fontSize: "11pt" }}
                    onChange={(e) => updateAward(index, { date: e.target.value })}
                  />
                </div>

                <div style={{ marginTop: 6 }}>
                  <textarea
                    value={detailsText}
                    placeholder={"Award details (one per line)"}
                    style={{
                      width: "100%",
                      minHeight: 44,
                      fontFamily: "inherit",
                      fontSize: "11pt",
                      resize: "vertical",
                      padding: 4,
                      borderRadius: 4,
                      border: "1px solid #ccc",
                      background: "transparent",
                    }}
                    onChange={(e) =>
                      updateAward(index, { details: detailsTextToList(e.target.value) })
                    }
                  />
                </div>
              </div>
            ) : (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline" }}>
                  <div style={{ fontWeight: 700 }}>{award.title}</div>
                  {formattedDate && <div style={{ color: "#333" }}>{formattedDate}</div>}
                </div>

                {issuer && (
                  <div style={{ marginTop: 2, color: "#333" }}>{issuer}</div>
                )}

                {detailsList.length > 0 && (
                  <ul className="resume-preview__project-bullets resume-preview__award-bullets" style={{ marginTop: 6 }}>
                    {detailsList.map((d, i) => (
                      <li key={i} style={{ marginBottom: 2 }}>
                        {d}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

