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


def format_project_score_display(project: Dict[str, Any]) -> str:
    """
    Format project score with override marker.
    """
    score = project.get("display_score", project.get("score", 0.0))
    marker = "*" if project.get("score_overridden") else ""
    return f"{_to_float(score):.3f}{marker}"


def _print_breakdown_summary(project_name: str, breakdown_payload: Dict[str, Any]) -> None:
    breakdown = breakdown_payload.get("breakdown", {})
    code = breakdown.get("code", {})
    non_code = breakdown.get("non_code", {})
    blend = breakdown.get("blend", {})

    print(f"\n📊 Score Breakdown: {project_name}")
    print(f"   Current score: {_to_float(breakdown_payload.get('display_score')):.3f}")
    print(f"   Code subtotal ({code.get('type', 'unknown')}): {_to_float(code.get('subtotal')):.3f}")
    print(f"   Non-code subtotal: {_to_float(non_code.get('subtotal')):.3f}")
    print(
        f"   Blend: code={_to_float(blend.get('code_percentage')):.3f}, "
        f"non-code={_to_float(blend.get('non_code_percentage')):.3f}"
    )
    print(f"   Final score: {_to_float(breakdown.get('final_score')):.3f}")


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


def run_project_score_override_cli(project_signatures: List[str]) -> None:
    """
    CLI flow for score breakdown preview/apply/clear by project.
    """
    if not project_signatures:
        return

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
        if selection in ("done", "d", "exit", "quit", "q"):
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

        try:
            breakdown_payload = compute_project_breakdown(signature)
        except ProjectNotFoundError:
            print("Project not found.")
            continue

        _print_breakdown_summary(project["name"], breakdown_payload)

        action = input("Action (preview/apply/clear/back): ").strip().lower()
        if action in ("back", "b"):
            continue
        if action == "clear":
            try:
                cleared = clear_project_score_override(signature)
                print(
                    f"Override cleared. Score restored to {_to_float(cleared.get('display_score')):.3f}"
                )
            except ProjectNotFoundError:
                print("Project not found.")
            continue
        if action not in ("preview", "apply"):
            print("Invalid action.")
            continue

        exclusions = _prompt_metric_exclusions(breakdown_payload)

        if action == "preview":
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
            print(f"Override applied. New score: {_to_float(applied.get('display_score')):.3f}*")
        except (ProjectNotFoundError, OverrideValidationError) as exc:
            print(f"Cannot apply override: {exc}")
