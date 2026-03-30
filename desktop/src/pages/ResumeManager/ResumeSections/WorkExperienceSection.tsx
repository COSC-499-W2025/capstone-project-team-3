import { useMemo, type ReactNode } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { WorkExperience } from "../../../api/resume_types";

const MONTH_ABBREV = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function formatMonthYear(value?: string): string {
  if (!value) return "";
  // Accept "YYYY-MM" (recommended) or "YYYY-MM-01" (ISO-like).
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

function normalizeDateForInput(value?: string): string {
  if (!value) return "";
  if (/^\d{4}-\d{2}$/.test(value)) return value;
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value.slice(0, 7); // YYYY-MM
  const prefix = value.match(/^(\d{4}-\d{2})/);
  return prefix ? prefix[1] : "";
}

function detailsTextToList(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.replace(/\r/g, ""));
}

function normalizeDetails(details?: string[]): string[] {
  if (!details) return [];
  return details.map((d) => String(d)).filter((d) => d.trim().length > 0);
}

function SortableWorkExperienceRow({
  sortableId,
  children,
}: {
  sortableId?: string;
  children: (dragHandle: ReactNode) => ReactNode;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: sortableId ?? "__we_sortable_disabled__",
    disabled: sortableId === undefined,
  });
  const style =
    sortableId !== undefined
      ? {
          transform: CSS.Transform.toString(transform),
          transition,
          opacity: isDragging ? 0.5 : 1,
          marginTop: 10,
        }
      : { marginTop: 10 };

  const dragHandle =
    sortableId !== undefined ? (
      <span
        className="resume-preview__project-drag-handle"
        aria-label="Drag to reorder work experience"
        {...attributes}
        {...listeners}
      >
        ⋮⋮
      </span>
    ) : null;

  return (
    <div ref={setNodeRef} style={style}>
      {children(dragHandle)}
    </div>
  );
}

export function WorkExperienceSection({
  workExperience,
  isEditing = false,
  onChange,
  enableSortable = false,
}: {
  workExperience: WorkExperience[];
  isEditing?: boolean;
  onChange?: (workExperience: WorkExperience[]) => void;
  /** When true and isEditing, each entry shows a drag handle for reordering. */
  enableSortable?: boolean;
}) {
  const entries = workExperience ?? [];

  const addEntry = () => {
    const next: WorkExperience[] = [
      ...entries,
      {
        role: "",
        company: "",
        start_date: "",
        end_date: "",
        details: [],
      },
    ];
    onChange?.(next);
  };

  const updateEntry = (index: number, patch: Partial<WorkExperience>) => {
    const next = entries.map((e, i) => (i === index ? { ...e, ...patch } : e));
    onChange?.(next);
  };

  const removeEntry = (index: number) => {
    const next = entries.filter((_, i) => i !== index);
    onChange?.(next);
  };

  const emptyStateMessage = useMemo(() => {
    if (isEditing) return "Add your work experience entries below.";
    return "No work experience added.";
  }, [isEditing]);

  return (
    <section className="resume-preview__section">
      <div className="resume-preview__heading-row">
        <h2 className="resume-preview__heading">Work Experience</h2>
        {isEditing && (
          <button
            type="button"
            onClick={addEntry}
            className="resume-preview__add-project-btn"
          >
            Add a role
          </button>
        )}
      </div>

      {entries.length === 0 && (
        <p style={{ margin: "4px 0 0 0", fontStyle: "italic", color: "#666" }}>{emptyStateMessage}</p>
      )}

      {entries.map((entry, index) => {
        const detailsList = normalizeDetails(entry.details);
        const detailsText = (entry.details ?? []).map((d) => String(d)).join("\n");
        const dateStart = formatMonthYear(entry.start_date);
        const dateEnd = formatMonthYear(entry.end_date);
        const dateRange = [dateStart, dateEnd].filter(Boolean).join(" – ");
        const sortableId = enableSortable && isEditing ? `work-${index}` : undefined;

        return (
          <SortableWorkExperienceRow key={index} sortableId={sortableId}>
            {(dragHandle) => (
              isEditing ? (
              <div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  {dragHandle}
                  <input
                    type="text"
                    value={entry.company ?? ""}
                    placeholder="Company / organization"
                    style={{ flex: 1, fontFamily: "inherit", fontSize: "11pt" }}
                    onChange={(e) => updateEntry(index, { company: e.target.value })}
                  />
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", marginTop: 6 }}>
                  <input
                    type="text"
                    value={entry.role}
                    placeholder="Role title (required)"
                    style={{ flex: 1, fontFamily: "inherit", fontSize: "11pt" }}
                    onChange={(e) => updateEntry(index, { role: e.target.value })}
                  />
                  <div className="resume-preview__project-header-right">
                    <div className="resume-preview__project-dates-edit">
                      <div className="resume-preview__project-date-wrap">
                        <input
                          type="month"
                          className="resume-preview__project-date-input"
                          aria-label="Start (month and year)"
                          value={normalizeDateForInput(entry.start_date)}
                          onChange={(e) => updateEntry(index, { start_date: e.target.value })}
                        />
                        {!normalizeDateForInput(entry.start_date) && (
                          <span className="resume-preview__project-date-placeholder" aria-hidden>
                            Start
                          </span>
                        )}
                      </div>

                      <span className="resume-preview__project-dates-sep"> – </span>

                      <div className="resume-preview__project-date-wrap">
                        <input
                          type="month"
                          className="resume-preview__project-date-input"
                          aria-label="End (month and year)"
                          value={normalizeDateForInput(entry.end_date)}
                          onChange={(e) => updateEntry(index, { end_date: e.target.value })}
                        />
                        {!normalizeDateForInput(entry.end_date) && (
                          <span className="resume-preview__project-date-placeholder" aria-hidden>
                            End
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      aria-label="Remove work experience entry"
                      onClick={() => removeEntry(index)}
                      className="resume-preview__project-delete-btn"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div className="resume-preview__project-bullets-edit-wrapper" style={{ marginTop: 6 }}>
                  <span className="resume-preview__project-bullets-hint">One bullet per line.</span>
                  <textarea
                    value={detailsText}
                    placeholder={"Responsibility one\nResponsibility two"}
                    className="resume-preview__project-bullets-edit"
                    style={{
                      width: "100%",
                      minHeight: 54,
                      fontFamily: "inherit",
                      fontSize: "11pt",
                      resize: "vertical",
                      padding: 4,
                      borderRadius: 4,
                      border: "1px solid #ccc",
                      background: "transparent",
                    }}
                    onChange={(e) => updateEntry(index, { details: detailsTextToList(e.target.value) })}
                  />
                </div>
              </div>
            ) : (
              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    alignItems: "baseline",
                  }}
                >
                  <div style={{ fontWeight: 700 }}>
                    {entry.company ? `${entry.company} | ${entry.role}` : entry.role}
                  </div>
                  {dateRange && <div style={{ color: "#333" }}>{dateRange}</div>}
                </div>

                {detailsList.length > 0 && (
                  <ul className="resume-preview__project-bullets resume-preview__work-bullets" style={{ marginTop: 4 }}>
                    {detailsList.map((d, i) => (
                      <li key={i} style={{ marginBottom: 2 }}>
                        {d}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )
            )}
          </SortableWorkExperienceRow>
        );
      })}
    </section>
  );
}

