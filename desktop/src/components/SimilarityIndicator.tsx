interface SimilarityIndicatorProps {
  similarity: {
    jaccard_similarity: number;
    containment_ratio: number;
    matched_project_name: string;
    match_reason: string;
  } | null;
  projectName: string;
}

export function SimilarityIndicator({ similarity, projectName }: SimilarityIndicatorProps) {
  if (!similarity) {
    return (
      <div className="similarity-indicator similarity-indicator--none" title="No similar projects found">
        <svg className="similarity-circle" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="16" fill="none" stroke="#e5e7eb" strokeWidth="3" />
          <text x="18" y="22" textAnchor="middle" fontSize="10" fill="#6b7280">NEW</text>
        </svg>
      </div>
    );
  }

  const score = similarity.jaccard_similarity;
  const circumference = 2 * Math.PI * 16;
  const offset = circumference - (score / 100) * circumference;

  let colorClass = "similarity-indicator--low";
  let strokeColor = "#10b981";
  
  if (score >= 70) {
    colorClass = "similarity-indicator--high";
    strokeColor = "#ef4444";
  } else if (score >= 30) {
    colorClass = "similarity-indicator--medium";
    strokeColor = "#f59e0b";
  }

  const tooltipText = `${projectName} is ${score.toFixed(1)}% similar to "${similarity.matched_project_name}"\n\nJaccard Similarity: ${similarity.jaccard_similarity.toFixed(1)}%\nContainment Ratio: ${similarity.containment_ratio.toFixed(1)}%\nMatch Reason: ${similarity.match_reason}`;

  return (
    <div className={`similarity-indicator ${colorClass}`} title={tooltipText}>
      <svg className="similarity-circle" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="16" fill="none" stroke="#e5e7eb" strokeWidth="3" />
        <circle
          cx="18"
          cy="18"
          r="16"
          fill="none"
          stroke={strokeColor}
          strokeWidth="3"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 18 18)"
        />
        <text x="18" y="22" textAnchor="middle" fontSize="9" fontWeight="600" fill={strokeColor}>
          {Math.round(score)}%
        </text>
      </svg>
    </div>
  );
}
