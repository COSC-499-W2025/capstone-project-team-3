from pathlib import Path
from typing import Dict, Union, List
import os
from datetime import datetime
from collections import Counter

# Aggregate metrics from parsed source files
def aggregate_parsed_files_metrics(parsed_files: List[Dict]) -> Dict:
    """
    Aggregates key metrics from a list of parsed file dicts.
    Returns a dictionary of project-level statistics.
    """
    metrics = {
        "languages": set(),
        "total_files": 0,
        "total_lines": 0,
        "functions": 0,
        "components": 0,
        "roles": set(),
        "imports": set(),
        "average_function_length": [],
        "comment_ratios": [],
        "summary_snippets": [],
    }

    # Collect metrics from each file
    for file in parsed_files:
        metrics["languages"].add(file.get("language"))
        metrics["total_files"] += 1
        metrics["total_lines"] += file.get("lines_of_code", 0)
        metrics["functions"] += len(file.get("functions", []))
        metrics["components"] += len(file.get("components", []))
        metrics["roles"].update(file.get("roles_detected", []))
        metrics["imports"].update(file.get("imports", []))
        if "metrics" in file:
            if "average_function_length" in file["metrics"]:
                metrics["average_function_length"].append(file["metrics"]["average_function_length"])
            if "comment_ratio" in file["metrics"]:
                metrics["comment_ratios"].append(file["metrics"]["comment_ratio"])
        if "summary_snippet" in file:
            metrics["summary_snippets"].append(file["summary_snippet"])

    # Calculate averages and convert sets to lists
    metrics["average_function_length"] = (
        sum(metrics["average_function_length"]) / len(metrics["average_function_length"])
        if metrics["average_function_length"] else 0
    )
    metrics["average_comment_ratio"] = (
        sum(metrics["comment_ratios"]) / len(metrics["comment_ratios"])
        if metrics["comment_ratios"] else 0
    )
    metrics["languages"] = list(metrics["languages"])
    metrics["roles"] = list(metrics["roles"])
    metrics["imports"] = list(metrics["imports"])
    return metrics

# Generate resume summary from parsed file metrics (optionally using LLM)
def generate_resume_summary_from_parsed(metrics: Dict, llm_client=None) -> Union[str, List[str]]:
    """
    Generate resume-like bullet points from aggregated metrics of parsed files.
    Uses LLM if provided, otherwise returns a basic summary.
    """
    if llm_client:
        # Use LLM to generate a more natural summary
        prompt = (
            "Given these aggregated project metrics:\n"
            f"{metrics}\n"
            "Generate resume-like bullet points summarizing the user's contributions, "
            "including key activities, skills, technologies, and impact."
        )
        response = llm_client.generate(prompt)
        return response
    else:
        # Basic rule-based summary
        summary = [
            f"Worked on a project with {metrics.get('total_files', 0)} files and {metrics.get('total_lines', 0)} lines of code.",
            f"Languages used: {', '.join(metrics.get('languages', []))}.",
            f"Roles detected: {', '.join(metrics.get('roles', []))}.",
            f"Implemented {metrics.get('functions', 0)} functions and {metrics.get('components', 0)} components.",
            f"Average function length: {metrics.get('average_function_length', 0):.2f} lines.",
            f"Average comment ratio: {metrics.get('average_comment_ratio', 0):.2f}.",
            f"Key imports: {', '.join(metrics.get('imports', []))}.",
        ]
        # Optionally add summary snippets
        if metrics.get("summary_snippets"):
            summary.append("Sample file summaries:")
            summary.extend(metrics["summary_snippets"][:3])  # Show up to 3
        return summary

# Aggregate metrics from a list of GitHub commits
def aggregate_github_individual_metrics(commits: List[Dict]) -> Dict:
    """
    Aggregates key metrics from a list of individual commit dicts.
    Returns a dictionary of contribution statistics.
    """
    file_status_counter = Counter()
    file_types_counter = Counter()
    authors = set()
    dates = []
    messages = []
    total_files_changed = set()

    # File type extensions for classification
    code_exts = {".py", ".js", ".java", ".cpp", ".c", ".ts", ".rb", ".go"}
    doc_exts = {".md", ".rst", ".txt", ".docx", ".pdf"}
    test_exts = {"test_", "_test.py", ".spec.js", ".spec.ts"}

    # Collect metrics from each commit
    for commit in commits:
        authors.add(commit.get("author_name"))
        dates.append(commit.get("authored_datetime"))
        messages.append(commit.get("message_summary"))
        for f in commit.get("files", []):
            status = f.get("status")
            file_status_counter[status] += 1
            path = f.get("path_after") or f.get("path_before")
            if path:
                total_files_changed.add(path)
                ext = os.path.splitext(path)[1].lower()
                fname = os.path.basename(path).lower()
                if ext in code_exts:
                    file_types_counter["code"] += 1
                elif ext in doc_exts:
                    file_types_counter["docs"] += 1
                elif any(fname.endswith(e) or fname.startswith(e) for e in test_exts):
                    file_types_counter["test"] += 1
                else:
                    file_types_counter["other"] += 1

    # Calculate duration in days between first and last commit
    def parse_dt(dt): return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    if dates:
        dates_sorted = sorted(dates)
        duration_days = (parse_dt(dates_sorted[-1]) - parse_dt(dates_sorted[0])).days
    else:
        duration_days = 0

    metrics = {
        "authors": list(authors),
        "total_commits": len(commits),
        "duration_days": duration_days,
        "files_added": file_status_counter["A"],
        "files_modified": file_status_counter["M"],
        "files_deleted": file_status_counter["D"],
        "total_files_changed": len(total_files_changed),
        "code_files_changed": file_types_counter["code"],
        "doc_files_changed": file_types_counter["docs"],
        "test_files_changed": file_types_counter["test"],
        "other_files_changed": file_types_counter["other"],
        "sample_messages": messages[:3],  # up to 3
    }
    return metrics

# Generate resume summary from GitHub commit metrics (optionally using LLM)
def generate_github_resume_summary(metrics: Dict, llm_client=None) -> Union[str, List[str]]:
    """
    Generate resume-like bullet points from aggregated GitHub commit metrics.
    Uses LLM if provided, otherwise returns a basic summary.
    """
    if llm_client:
        # Use LLM to generate a more natural summary
        prompt = (
            "Given these GitHub contribution metrics:\n"
            f"{metrics}\n"
            "Generate resume-like bullet points summarizing the user's contributions, "
            "including key activities, skills, technologies, and impact."
        )
        response = llm_client.generate(prompt)
        return response
    else:
        # Basic rule-based summary
        summary = [
            f"Contributed {metrics.get('total_commits', 0)} commits over {metrics.get('duration_days', 0)} days.",
            f"Changed {metrics.get('total_files_changed', 0)} files: {metrics.get('files_added', 0)} added, "
            f"{metrics.get('files_modified', 0)} modified, {metrics.get('files_deleted', 0)} deleted.",
            f"Code files changed: {metrics.get('code_files_changed', 0)}, "
            f"Test files: {metrics.get('test_files_changed', 0)}, "
            f"Docs: {metrics.get('doc_files_changed', 0)}.",
            f"Authors: {', '.join(metrics.get('authors', []))}.",
        ]
        if metrics.get("sample_messages"):
            summary.append("Sample commit messages:")
            summary.extend(metrics["sample_messages"])
        return summary

# Main entry point for project analysis
def analyze_parsed_project(parsed_files: List[Dict], llm_client=None):
    """
    Analyze a project from parsed file dicts and return a resume summary.
    Uses LLM if provided, otherwise returns a basic summary.
    """
    metrics = aggregate_parsed_files_metrics(parsed_files)
    return generate_resume_summary_from_parsed(metrics, llm_client)