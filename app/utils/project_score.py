from typing import Dict, Any

def _norm_with_cap(value: float, cap: float) -> float:
    """Simple 0–1 normalization with an upper cap."""
    if cap <= 0:
        return 0.0
    if value <= 0:
        return 0.0
    return min(value / cap, 1.0)

def _compute_git_code_score(git_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a simplified Git-based code score (0–1) using 5 metrics:
      1. total_commits         → 30%
      2. duration_days         → 30%
      3. total_lines           → 20%
      4. code_files_changed    → 15%
      5. test_files_changed    → 5%
    """

    # Extract metrics
    total_commits      = git_code_metrics.get("total_commits", 0)
    duration_days      = git_code_metrics.get("duration_days", 0)
    total_lines        = git_code_metrics.get("total_lines", 0)
    code_files_changed = git_code_metrics.get("code_files_changed", 0)
    test_files_changed = git_code_metrics.get("test_files_changed", 0)

    # Caps (saturation thresholds for a final-year CS project)
    commits_cap            = 50
    duration_cap           = 30
    total_lines_cap        = 5000
    code_files_changed_cap = 20
    test_files_changed_cap = 8

    # Normalize
    s_commits      = _norm_with_cap(total_commits,      commits_cap)
    s_duration     = _norm_with_cap(duration_days,      duration_cap)
    s_lines        = _norm_with_cap(total_lines,        total_lines_cap)
    s_code_files   = _norm_with_cap(code_files_changed, code_files_changed_cap)
    s_test_files   = _norm_with_cap(test_files_changed, test_files_changed_cap)

    # Weights
    code_score = (
        0.30 * s_commits +
        0.30 * s_duration +
        0.20 * s_lines +
        0.15 * s_code_files +
        0.05 * s_test_files
    )

    return code_score

def _compute_non_code_score(non_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a non-code score from completeness_score.
    Expected range: [0, 1].
    If completeness_score is out of this range, clamp it.
    """

    completeness = non_code_metrics.get("completeness_score", 0.0)

    # If someone accidentally passes 0–100, convert to 0–1
    if completeness > 1.0:
        completeness /= 100.0

    # Clamp to valid range
    completeness = max(0.0, min(completeness, 1.0))

    return completeness

def _compute_non_git_code_score(non_git_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a code contribution score (0–1) for a non-Git project.
    Uses structural + complexity-based metrics.
    Higher complexity = higher contribution.
    """

    # Extract raw values
    total_files          = non_git_code_metrics.get("total_files", 0)
    total_lines          = non_git_code_metrics.get("total_lines", 0)
    code_files_changed   = non_git_code_metrics.get("code_files_changed", 0)
    test_files_changed   = non_git_code_metrics.get("test_files_changed", 0)

    maint = non_git_code_metrics["complexity_analysis"]["maintainability_score"]
    overall_score      = maint.get("overall_score", 0)
    average_complexity = maint.get("average_complexity", 0)

    # Caps
    total_files_cap        = 40
    total_lines_cap        = 5000
    code_files_changed_cap = 30
    test_files_changed_cap = 10
    overall_score_cap      = 100
    average_complexity_cap = 30

    # Normalize using shared function
    s_files        = _norm_with_cap(total_files, total_files_cap)
    s_lines        = _norm_with_cap(total_lines, total_lines_cap)
    s_code_files   = _norm_with_cap(code_files_changed, code_files_changed_cap)
    s_test_files   = _norm_with_cap(test_files_changed, test_files_changed_cap)
    s_overall      = _norm_with_cap(overall_score, overall_score_cap)
    s_complexity   = _norm_with_cap(average_complexity, average_complexity_cap)

    # Weights (sum to 1.0)
    score = (
        0.15 * s_files +
        0.20 * s_lines +
        0.20 * s_code_files +
        0.10 * s_test_files +
        0.20 * s_overall +
        0.15 * s_complexity
    )

    return score

def _compute_contribution_percentages_single_project(
    code_metrics: Dict[str, Any],
    git_code_metrics: Dict[str, Any],
    non_code_metrics: Dict[str, Any],
) -> Dict[str, float]:
    """
    Compute percentage of code vs non-code contribution for a project.
    
    Logic:
      - If Git project → use git_code_metrics["total_lines"]
      - If Non-Git project → use code_metrics["total_lines"]
      - Convert non-code word count to documentation-line equivalents
      - Compute percentage split: code vs non-code
    """

    # Determine project type
    is_git_project = bool(git_code_metrics)

    # Select appropriate code line source
    if is_git_project:
        code_lines = git_code_metrics.get("total_lines", 0)
    else:
        code_lines = code_metrics.get("total_lines", 0)

    # Extract total non-code words
    total_words = non_code_metrics.get("word_count", 0)

    # Convert documentation words → code line equivalents
    words_per_code_line = 7.0  # industry-baseline conversion
    doc_line_equiv = (total_words / words_per_code_line
                      if words_per_code_line > 0 else total_words)

    # Avoid div-by-zero issues
    total = code_lines + doc_line_equiv
    if total == 0:
        return {
            "code_percentage": 0.0,
            "non_code_percentage": 0.0
        }

    # Return normalized percentages
    return {
        "code_percentage": code_lines / total,
        "non_code_percentage": doc_line_equiv / total
    }



def compute_overall_project_contribution_score(
    code_metrics: Dict[str, Any],
    git_code_metrics: Dict[str, Any],
    non_code_metrics: Dict[str, Any],
) -> float:
    """
    Compute final contribution score for a project.
    
    Steps:
        1. Determine if project is Git or Non-Git.
        2. Compute code_score from the appropriate source.
        3. Compute non_code_score from completeness.
        4. Compute code vs non-code percentages (effort ratio).
        5. Final blended score:
               final = code_score * code_percentage
                     + non_code_score * non_code_percentage
                     
    Returns:
        A single float between 0 and 1.
    """

    # 1. Detect project type
    is_git_project = bool(git_code_metrics)

    # 2. Compute code score
    if is_git_project:
        code_score = _compute_git_code_score(git_code_metrics)
    else:
        code_score = _compute_non_git_code_score(code_metrics)

    # 3. Compute non-code score
    non_code_score = _compute_non_code_score(non_code_metrics)

    # 4. Compute code vs non-code percentages (effort ratios)
    percentages = _compute_contribution_percentages_single_project(
        code_metrics=code_metrics,
        git_code_metrics=git_code_metrics,
        non_code_metrics=non_code_metrics,
    )

    code_percentage     = percentages["code_percentage"]
    non_code_percentage = percentages["non_code_percentage"]

    # 5. Final blended score
    final_score = (
        code_score * code_percentage +
        non_code_score * non_code_percentage
    )

    return final_score
