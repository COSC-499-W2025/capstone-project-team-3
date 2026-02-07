import { Resume } from "../../api/resume_types";

export const ResumeSidebar = ({ resumes, activeIndex, onSelect }: {
  resumes: Resume[]; // or unknown[]
  activeIndex: number;
  onSelect: (index: number) => void;
}) => {
  return (
    <aside className="w-72 border-r bg-gray-50">
      <h2 className="px-4 py-3 font-semibold">Your Résumés</h2>

      {resumes.map((r, i) => (
        <button
          key={i}
          onClick={() => onSelect(i)}
          className={`w-full px-4 py-3 text-left ${
            i === activeIndex ? "bg-gray-200" : ""
          }`}
        >
          {r.name || `Resume ${i + 1}`}
        </button>
      ))}

      <button className="m-4 w-[calc(100%-2rem)] bg-blue-600 text-white py-2">
        Tailor New Resume
      </button>
    </aside>
  );
};
