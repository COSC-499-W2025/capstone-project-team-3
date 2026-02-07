import { Resume } from "../../../api/resume_types";

export function HeaderSection({ resume }: { resume: Resume }) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-bold">{resume.name}</h1>
      <p>{resume.email}</p>
    </header>
  );
}
