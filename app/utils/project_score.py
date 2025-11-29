from typing import List, Dict, Any

def _compute_contribution_percentages(
    code_metrics: List[Dict[str, Any]],
    non_code_metrics: List[Dict[str, Any]],
    words_per_code_line: float = 7.0
) -> Dict[str, float]:
    """
    Compute percentage of code contribution vs non-code contribution
    by converting non-code word count into documentation line equivalents.
    
    Returns:
        {
          "code_percentage": float,
          "non_code_percentage": float
        }
    """
    
    # Sum totals
    total_code_lines = sum(m.get("code_lines_added", 0) for m in code_metrics)
    total_words = sum(m.get("word_count", 0) for m in non_code_metrics)

    # Convert words → doc line equivalents
    doc_line_equiv = total_words / words_per_code_line if words_per_code_line > 0 else total_words

    total = total_code_lines + doc_line_equiv
    if total == 0:
        return {
            "code_percentage": 0.0,
            "non_code_percentage": 0.0
        }

    return {
        "code_percentage": total_code_lines / total,
        "non_code_percentage": doc_line_equiv / total
    }
