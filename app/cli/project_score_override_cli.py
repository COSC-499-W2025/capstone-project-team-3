from typing import Any, Dict, List

from app.utils.retrieve_insights_utils import get_projects_by_signatures
from app.utils.score_override_utils import (
    OverrideValidationError,
    ProjectNotFoundError,
    apply_project_score_override,
    clear_project_score_override,
    compute_project_breakdown,
    preview_project_score_override,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _humanize_metric_name(metric_name: str) -> str:
    return metric_name.replace("_", " ")


def format_project_score_display(project: Dict[str, Any]) -> str:
    """
    Format project score with override marker.
    """
    score = project.get("score", 0.0)
    marker = "*" if project.get("score_overridden") else ""
    return f"{_to_float(score):.3f}{marker}"


def _print_breakdown_summary(project_name: str, breakdown_payload: Dict[str, Any]) -> None:
    breakdown = breakdown_payload.get("breakdown", {})
    code = breakdown.get("code", {})
    non_code = breakdown.get("non_code", {})
    blend = breakdown.get("blend", {})

    print(f"\n📊 Score Breakdown: {project_name}")
    print(f"   Current score: {_to_float(breakdown_payload.get('score')):.3f}")
    print(f"   Code subtotal ({code.get('type', 'unknown')}): {_to_float(code.get('subtotal')):.3f}")
    print(f"   Non-code subtotal: {_to_float(non_code.get('subtotal')):.3f}")
    print(
        f"   Blend: code={_to_float(blend.get('code_percentage')):.3f}, "
        f"non-code={_to_float(blend.get('non_code_percentage')):.3f}"
    )
    print(f"   Final score: {_to_float(breakdown.get('final_score')):.3f}")
    print(
        f"   Effort mix: code_lines={int(_to_float(blend.get('code_lines')))}, "
        f"doc_words={int(_to_float(blend.get('doc_word_count')))} "
        f"(doc_line_equiv={_to_float(blend.get('doc_line_equiv')):.1f})"
    )

    code_metrics = code.get("metrics", {})
    if code_metrics:
        print("\n   Code metrics:")
        for metric_name, metric_data in code_metrics.items():
            readable_name = _humanize_metric_name(metric_name)
            if not isinstance(metric_data, dict):
                raw_value = _to_float(metric_data)
                raw_display = int(raw_value) if raw_value.is_integer() else round(raw_value, 3)
                print(
                    f"      - {readable_name}: your project has {raw_display}. "
                    f"(Detailed benchmark data is unavailable for this metric.)"
                )
                continue
            raw = _to_float(metric_data.get("raw"))
            cap = _to_float(metric_data.get("cap"))
            normalized = _to_float(metric_data.get("normalized"))
            weight = _to_float(metric_data.get("weight"))
            contribution = _to_float(metric_data.get("contribution"))
            raw_display = int(raw) if raw.is_integer() else round(raw, 3)
            cap_display = int(cap) if cap.is_integer() else round(cap, 3)
            gap = max(cap - raw, 0.0)
            gap_display = int(gap) if float(gap).is_integer() else round(gap, 3)
            print(
                f"      - {readable_name}: your project has {raw_display}. "
                f"A full score for this metric is {cap_display}. "
                f"You are at {normalized * 100:.1f}% of full score "
                f"({gap_display} away from the cap). "
                f"This metric weight is {weight * 100:.1f}% and currently contributes {contribution:.3f}."
            )
    else:
        print("\n   Code metrics: none (no code metrics available).")

    non_code_metrics = non_code.get("metrics", {})
    if non_code_metrics:
        print("\n   Non-code metrics:")
        for metric_name, metric_data in non_code_metrics.items():
            readable_name = _humanize_metric_name(metric_name)
            if not isinstance(metric_data, dict):
                raw_value = _to_float(metric_data)
                raw_display = int(raw_value) if raw_value.is_integer() else round(raw_value, 3)
                print(
                    f"      - {readable_name}: your project has {raw_display}. "
                    f"(Detailed benchmark data is unavailable for this metric.)"
                )
                continue
            raw = _to_float(metric_data.get("raw"))
            cap = _to_float(metric_data.get("cap"))
            normalized = _to_float(metric_data.get("normalized"))
            weight = _to_float(metric_data.get("weight"))
            contribution = _to_float(metric_data.get("contribution"))
            raw_display = int(raw) if raw.is_integer() else round(raw, 3)
            cap_display = int(cap) if cap.is_integer() else round(cap, 3)
            gap = max(cap - raw, 0.0)
            gap_display = int(gap) if float(gap).is_integer() else round(gap, 3)
            print(
                f"      - {readable_name}: your project has {raw_display}. "
                f"A full score for this metric is {cap_display}. "
                f"You are at {normalized * 100:.1f}% of full score "
                f"({gap_display} away from the cap). "
                f"This metric weight is {weight * 100:.1f}% and currently contributes {contribution:.3f}."
            )


def _prompt_metric_exclusions(breakdown_payload: Dict[str, Any]) -> List[str]:
    metric_names = list(
        breakdown_payload.get("breakdown", {})
        .get("code", {})
        .get("metrics", {})
        .keys()
    )
    if metric_names:
        print("\nAvailable code metrics to exclude:")
        print("   " + ", ".join(metric_names))

    raw = input(
        "Enter metrics to exclude (comma-separated, blank for none): "
    ).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _run_project_actions(signature: str, project_name: str) -> None:
    while True:
        try:
            breakdown_payload = compute_project_breakdown(signature)
        except ProjectNotFoundError:
            print("Project not found.")
            return

        _print_breakdown_summary(project_name, breakdown_payload)
        print("\nRanking options:")
        print("   1. Understand score breakdown")
        print("   2. Preview override")
        print("   3. Apply override")
        print("   4. Clear override")
        print("   5. Back")
        action = input("Select option (1-5): ").strip().lower()

        if action in ("5", "back", "b"):
            return

        if action in ("1", "breakdown", "understand"):
            continue

        if action == "4" or action == "clear":
            try:
                cleared = clear_project_score_override(signature)
                print(
                    f"Override cleared. Score restored to {_to_float(cleared.get('score')):.3f}"
                )
            except ProjectNotFoundError:
                print("Project not found.")
            continue

        if action not in ("2", "3", "preview", "apply"):
            print("Invalid option. Please enter 1, 2, 3, 4, or 5.")
            continue

        exclusions = _prompt_metric_exclusions(breakdown_payload)

        if action in ("2", "preview"):
            try:
                preview = preview_project_score_override(signature, exclusions)
                print(
                    f"Preview score: {_to_float(preview.get('preview_score')):.3f} "
                    f"(current: {_to_float(preview.get('current_score')):.3f})"
                )
            except (ProjectNotFoundError, OverrideValidationError) as exc:
                print(f"Cannot preview override: {exc}")
            continue

        try:
            applied = apply_project_score_override(signature, exclusions)
            print(f"Override applied. New score: {_to_float(applied.get('score')):.3f}*")
        except (ProjectNotFoundError, OverrideValidationError) as exc:
            print(f"Cannot apply override: {exc}")


def run_project_score_override_cli(
    project_signatures: List[str],
    require_confirmation: bool = True,
) -> None:
    """
    CLI flow for score breakdown preview/apply/clear by project.
    """
    if not project_signatures:
        print("No projects available for score ranking.")
        return

    if require_confirmation:
        manage = input(
            "\nWould you like to review or override project scores for this session? (yes/no): "
        ).lower().strip()
        if manage not in ("yes", "y"):
            return

    print("\n* indicates an overridden score.")

    while True:
        projects = get_projects_by_signatures(project_signatures)
        if not projects:
            print("No projects available for score override.")
            return

        print("\nSelect a project:")
        for idx, project in enumerate(projects, 1):
            print(f"   {idx}. {project['name']} — Score: {format_project_score_display(project)}")

        selection = input("Enter project number or 'done': ").strip().lower()
        if selection in ("", "done", "d", "exit", "quit", "q"):
            return
        if not selection.isdigit():
            print("Invalid input. Please enter a project number or 'done'.")
            continue

        index = int(selection) - 1
        if index < 0 or index >= len(projects):
            print("Invalid project number.")
            continue

        project = projects[index]
        signature = project.get("project_signature")
        if not signature:
            print("Project signature missing. Try another project.")
            continue

        _run_project_actions(signature, project["name"])
