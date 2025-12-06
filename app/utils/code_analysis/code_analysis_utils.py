import json
from typing import Dict, List, Set
import os
from datetime import datetime
from collections import Counter, defaultdict
import re
from .patterns.tech_patterns import TechnicalPatterns


def _split_camelcase_and_filter(text: str, min_length: int = 2) -> Set[str]:
    """
    Helper: Split camelCase/snake_case text and filter by length.
    Shared logic for both GitHub and parsed file keyword extraction.
    """
    if not text or len(text) <= min_length:
        return set()
    
    # Split camelCase and snake_case
    words = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', text)
    
    # Filter by length and common terms
    filtered_words = {
        word.lower() for word in words 
        if len(word) > min_length and word.lower() not in TechnicalPatterns.COMMON_TERMS
    }
    
    return filtered_words

def _extract_meaningful_filename_keywords(filenames: List[str]) -> Set[str]:
    """
    Helper: Extract meaningful keywords from file names and paths.
    Shared logic for processing file paths.
    """
    tech_terms = set()
    
    for filename in filenames:
        if not filename or len(filename) <= 2:
            continue
            
        # Skip git and markdown files
        if filename.endswith(('.git', '.md')):
            continue
        
        # Remove extension and process
        name_without_ext = filename.split('.')[0]
        tech_terms.update(_split_camelcase_and_filter(name_without_ext))
    
    return tech_terms

def _get_top_keywords(keywords: Set[str], limit: int = 15) -> List[str]:
    """
    Helper: Get top keywords sorted alphabetically.
    Shared logic for returning final keyword lists.
    """
    return sorted(list(keywords))[:limit]

def extract_technical_keywords_from_github(commits: List[Dict]) -> List[str]:
    """
    Extract technical keywords from GitHub commit messages and file changes.
    Optimized with set-based lookup for performance.
    """
    all_messages = []
    all_file_names = []
    
    for commit in commits:
        # Collect commit messages
        message = commit.get("message_summary", "") + " " + commit.get("message_full", "")
        all_messages.append(message.lower())
        
        # Collect file names and paths
        files = commit.get("files", [])
        for file in files:
            path = file.get("path_after") or file.get("path_before", "")
            if path:
                all_file_names.extend(path.split("/"))
    
    # Fast set-based keyword extraction from commit messages
    tech_terms = set()
    
    for message in all_messages:
        # Split message into words and find intersection with tech keywords
        message_words = set(message.lower().split())
        tech_terms.update(message_words & TechnicalPatterns.GITHUB_TECH_KEYWORDS)
    
    # Extract meaningful file name keywords using shared helper
    filename_keywords = _extract_meaningful_filename_keywords(all_file_names)
    tech_terms.update(filename_keywords)
    
    return _get_top_keywords(tech_terms)



def extract_technical_keywords_from_parsed(parsed_files: List[Dict]) -> List[str]:
    """
    Extract meaningful technical keywords from parsed files using shared helpers.
    Updated to handle new JSON structure with entities.
    """
    all_identifiers = []
    all_imports = []
    
    for file in parsed_files:
        # Handle both old and new structure for backward compatibility
        entities = file.get("entities", {})
        
        # Extract from functions (new structure: entities.functions, old: functions)
        functions = entities.get("functions", []) or file.get("functions", [])
        for func in functions:
            all_identifiers.append(func.get("name", ""))
            all_identifiers.extend(func.get("calls", []))
        
        # Extract from components (new structure: entities.components, old: components)  
        components = entities.get("components", []) or file.get("components", [])
        for comp in components:
            all_identifiers.append(comp.get("name", ""))
            all_identifiers.extend(comp.get("props", []))
            all_identifiers.extend(comp.get("state_variables", []))
            all_identifiers.extend(comp.get("hooks_used", []))
        
        # Extract from classes (new structure only)
        classes = entities.get("classes", [])
        for cls in classes:
            class_name = cls.get("name")
            if class_name:  # Skip null class names
                all_identifiers.append(class_name)
            
            # Extract methods from classes
            methods = cls.get("methods", [])
            for method in methods:
                method_name = method.get("name")
                if method_name:  # Skip null method names
                    all_identifiers.append(method_name)
                    all_identifiers.extend(method.get("calls", []))
        
        # Handle imports and internal dependencies
        all_imports.extend(file.get("imports", []))
        all_imports.extend(file.get("dependencies_internal", []))
    
    # Clean and filter technical terms using shared helpers
    tech_keywords = set()
    
    # Process imports for frameworks/libraries
    for imp in all_imports:
        # Extract meaningful parts from imports like "./components/Chart" -> "Chart"
        if "/" in imp:
            tech_keywords.add(imp.split("/")[-1])
        elif "." in imp and not imp.startswith("."):
            tech_keywords.add(imp.split(".")[0])
        else:
            tech_keywords.add(imp)
    
    # Process identifiers using shared camelCase splitting
    for identifier in all_identifiers:
        tech_keywords.update(_split_camelcase_and_filter(identifier))
    
    return _get_top_keywords(tech_keywords)

def _detect_frameworks(imports: List[str]) -> List[str]:
    """Helper: Detect frameworks from imports."""
    import_str = ' '.join(imports).lower()
    detected_frameworks = []
    
    for framework_key, framework_name in TechnicalPatterns.FRAMEWORK_MAPPING.items():
        if framework_key in import_str:
            detected_frameworks.append(framework_name)
    
    return detected_frameworks

# Add new function for commit pattern analysis:

def analyze_github_commit_patterns(commits: List[Dict]) -> Dict:
    """Analyze commit patterns for demo-worthy insights."""
    patterns = {
        "commit_frequency": {},
        "work_style": [],
        "code_evolution": {},
        "impact_metrics": {}
    }
    
    if not commits:
        return patterns
    
    total_commits = len(commits)
    
    # Commit size analysis
    large_commits = sum(1 for commit in commits if commit.get("total_lines", 0) > 100)
    small_commits = sum(1 for commit in commits if commit.get("total_lines", 0) < 100)
    
    if large_commits > total_commits * 0.3:
        patterns["work_style"].append("feature_focused")
    if small_commits > total_commits * 0.5:
        patterns["work_style"].append("incremental_development")
    
    # Time-based patterns
    dates = [commit.get("authored_datetime") for commit in commits if commit.get("authored_datetime")]
    if dates and len(dates) > 1:
        duration = (datetime.fromisoformat(max(dates).replace('Z', '+00:00')) - 
                   datetime.fromisoformat(min(dates).replace('Z', '+00:00'))).days
        
        patterns["commit_frequency"] = {
            "total_commits": total_commits,
            "avg_commits_per_day": round(total_commits / max(duration, 1), 2),
            "development_intensity": "high" if total_commits / max(duration, 1) > 2 else "steady"
        }
    
    # Code evolution analysis
    file_changes = sum(len(commit.get("files", [])) for commit in commits)
    patterns["code_evolution"] = {
        "total_file_changes": file_changes,
        "avg_files_per_commit": round(file_changes / total_commits, 2),
        "change_style": "focused" if file_changes / total_commits < 3 else "broad"
    }
    
    # Impact metrics
    total_lines = sum(commit.get("total_lines", 0) for commit in commits)
    patterns["impact_metrics"] = {
        "total_contribution": total_lines,
        "avg_lines_per_commit": round(total_lines / total_commits, 2) if total_commits > 0 else 0,
        "contribution_scale": "substantial" if total_lines > 1000 else "moderate" if total_lines > 200 else "targeted"
    }
    
    return patterns

def analyze_github_development_patterns(commits: List[Dict]) -> Dict:
    """
    Analyze development patterns from GitHub commit history.
    """
    patterns = {
        "code_practices": [],
        "project_evolution": []
    }
    
    if not commits:
        return patterns
    
    # Analyze commit messages for patterns
    commit_types = defaultdict(int)
    all_messages = []
    all_files = []
    
    for commit in commits:
        message = commit.get("message_summary", "").lower()
        all_messages.append(message)
        
        # Collect all file paths for additional analysis
        files = commit.get("files", [])
        for file in files:
            path = file.get("path_after") or file.get("path_before", "")
            if path:
                all_files.append(path.lower())
        
        # Categorize commit types
        if any(keyword in message for keyword in ['feat:', 'feature', 'add', 'implement']):
            commit_types['feature'] += 1
        if any(keyword in message for keyword in ['fix:', 'bug', 'error']):
            commit_types['bugfix'] += 1
        if any(keyword in message for keyword in ['refactor:', 'restructure', 'cleanup']):
            commit_types['refactor'] += 1
        if any(keyword in message for keyword in ['test:', 'testing', 'spec']):
            commit_types['testing'] += 1
        if any(keyword in message for keyword in ['docs:', 'documentation', 'readme']):
            commit_types['documentation'] += 1
    
    total_commits = len(commits)
    
    # Calculate ratios and check thresholds
    if total_commits > 0:
        testing_ratio = commit_types['testing'] / total_commits
        refactor_ratio = commit_types['refactor'] / total_commits  
        doc_ratio = commit_types['documentation'] / total_commits
        if testing_ratio > 0.1:
            patterns["code_practices"].append("Test-Driven Development")
        if refactor_ratio > 0.15:
            patterns["code_practices"].append("Code Refactoring")
        
        if doc_ratio > 0.05:
            patterns["code_practices"].append("Documentation-Focused")
    
    # Analyze file changes for project evolution - FIXED EXTENSION HANDLING
    file_extensions = defaultdict(int)
    for commit in commits:
        for file in commit.get("files", []):
            path = file.get("path_after") or file.get("path_before", "")
            if path:
                # Handle files without extensions (Dockerfile, Makefile)
                if '.' in path:
                    ext = path.split('.')[-1].lower()
                else:
                    # Use filename as extension for files without extensions
                    ext = os.path.basename(path).lower()
                
                file_extensions[ext] += 1
    
    if file_extensions:
        dominant_tech = max(file_extensions, key=file_extensions.get)
        if dominant_tech in ['js', 'jsx', 'ts', 'tsx']:
            patterns["project_evolution"].append("JavaScript/Frontend Development")
        elif dominant_tech in ['py']:
            patterns["project_evolution"].append("Python Development")
        elif dominant_tech in ['java']:
            patterns["project_evolution"].append("Java Development")
        elif dominant_tech in ['dockerfile', 'makefile']:
            patterns["project_evolution"].append("DevOps/Infrastructure Development")
        else:
            patterns["project_evolution"].append("Multi-technology Development")
    
    return patterns

def generate_github_resume_summary(metrics: Dict) -> List[str]:
    """
    Enhanced GitHub resume generation with commit patterns and file contribution insights.
    """
    summary = []
    
    # Get enhanced patterns
    commit_patterns = metrics.get("commit_patterns", {})
    
    # Basic metrics
    total_commits = metrics.get('total_commits', 0)
    total_lines = metrics.get('total_lines', 0)
    languages = metrics.get('languages', [])
    duration = metrics.get('duration_days', 0)
    
    # Work style insights from commit patterns
    work_style = commit_patterns.get("work_style", [])
    development_intensity = commit_patterns.get("commit_frequency", {}).get("development_intensity", "")
    
    # ENHANCED OPENING: Combine commit patterns with languages/duration
    if "feature_focused" in work_style and total_lines > 500:
        if duration > 0 and languages:
            lang_text = '/'.join(languages[:2])
            summary.append(f"Delivered {total_commits} feature-focused commits in {lang_text} over {duration} days, contributing {total_lines} lines of production code")
        else:
            lang_text = '/'.join(languages[:2]) if languages else "multiple technologies"
            summary.append(f"Delivered {total_commits} feature-focused commits in {lang_text}, contributing {total_lines} lines of production code")
    elif "incremental_development" in work_style:
        if duration > 0:
            summary.append(f"Applied incremental development methodology with {total_commits} targeted commits over {duration} days of consistent code evolution")
        else:
            summary.append(f"Applied incremental development methodology with {total_commits} targeted commits and consistent code evolution")
    elif duration > 0 and languages and total_lines > 0:
        # Fallback to original enhanced opening
        lang_text = ', '.join(languages[:3])
        summary.append(f"Contributed {total_commits} commits adding {total_lines} lines of code in {lang_text} over {duration} days")
    else:
        summary.append(f"Contributed {total_commits} commits demonstrating systematic development approach")
    
    # BETTER FILE CONTRIBUTION MESSAGING (KEPT FROM ORIGINAL)
    files_added = metrics.get('files_added', 0)
    files_modified = metrics.get('files_modified', 0)
    code_files = metrics.get('code_files_changed', 0)
    total_files = metrics.get('total_files_changed', 0)
    
    if code_files > 5 and languages:
        lang_text = '/'.join(languages[:2])  # Use slash for tech stack
        summary.append(f"Developed full-stack solution using {lang_text} with {code_files} source files and comprehensive project structure")
    elif code_files > 0 and total_lines > 500:
        summary.append(f"Built substantial codebase with {code_files} core modules and {total_lines} lines of production code")
    elif total_files > 10:
        summary.append(f"Engineered comprehensive project architecture spanning {total_files} files with modern development practices")
    elif files_added > 5:
        summary.append(f"Established project foundation with {files_added} new modules and {files_modified} enhanced components")
    else:
        # Fallback for smaller contributions
        if languages:
            lang_text = '/'.join(languages)
            summary.append(f"Implemented {lang_text} solution with focused development approach")
        else:
            summary.append(f"Delivered focused technical contributions across {total_commits} commits")
    
    # COMMIT PATTERNS INSIGHTS (NEW)
    # Development intensity and consistency
    if development_intensity == "high":
        summary.append("Maintained high development velocity with consistent daily contributions")
    elif development_intensity == "steady":
        summary.append("Demonstrated consistent development rhythm and sustainable coding practices")
    
    # Technical contribution scope from commit patterns
    code_evolution = commit_patterns.get("code_evolution", {})
    change_style = code_evolution.get("change_style", "")  # Fixed: use change_scope not change_style
    
    if change_style == "focused":
        summary.append("Applied focused development approach with targeted, high-impact code changes")
    elif change_style == "broad":
        summary.append("Executed comprehensive development across multiple project components and modules")
    
    # TECHNICAL EXPERTISE (KEPT)
    #tech_keywords = metrics.get("technical_keywords", [])
    #if tech_keywords:
    #    summary.append(f"Demonstrated expertise in: {', '.join(tech_keywords[:6])}")
    
    # DEVELOPMENT PATTERNS (KEPT)
    dev_patterns = metrics.get("development_patterns", {})
    practices = dev_patterns.get("code_practices", [])
    if practices:
        summary.append(f"Applied best practices: {', '.join(practices)}")
    
    # Project evolution with language context (KEPT)
    evolution = dev_patterns.get("project_evolution", [])
    if evolution:
        summary.append(f"Led development in: {', '.join(evolution)}")
    
    # Technology stack summary (KEPT)
    if len(languages) > 1:
        summary.append(f"Utilized multi-technology stack: {', '.join(languages)}")
    
    # QUALITY EMPHASIS (KEPT)
    test_files = metrics.get('test_files_changed', 0)
    doc_files = metrics.get('doc_files_changed', 0)
    
    quality_aspects = []
    if test_files > 0:
        quality_aspects.append(f"testing ({test_files} test files)")
    if doc_files > 0:
        quality_aspects.append(f"documentation ({doc_files} docs)")
    
    if quality_aspects:
        summary.append(f"Emphasized code quality through {' and '.join(quality_aspects)}")
    
    # IMPACT METRICS FROM COMMIT PATTERNS (NEW)
    impact_metrics = commit_patterns.get("impact_metrics", {})
    contribution_scale = impact_metrics.get("contribution_scale", "")
    avg_lines_per_commit = impact_metrics.get("avg_lines_per_commit", 0)
    
    if contribution_scale == "substantial" and avg_lines_per_commit > 50:
        summary.append(f"Delivered substantial impact with average of {avg_lines_per_commit:.0f} lines per commit, demonstrating thorough implementation approach")
    elif contribution_scale == "targeted" and avg_lines_per_commit < 20:
        summary.append("Applied precise, targeted development approach with focused, well-scoped commits")
    
    return summary
    
# Aggregate metrics from a list of GitHub commits
def aggregate_github_individual_metrics(commits: List[Dict]) -> Dict:
    """
    Aggregates key metrics from a list of individual commit dicts.
    Updated to handle new fields: language and code_lines_added.
    Returns a dictionary of contribution statistics.
    """
    file_status_counter = Counter()
    file_types_counter = Counter()
    language_counter = Counter()  # NEW: Track languages
    authors = set()
    dates = []
    messages = []
    total_files_changed = set()
    total_code_lines_added = 0  # NEW: Track total code lines
    roles = set()
    
    # File type extensions for classification
    code_exts = TechnicalPatterns.CODE_EXTS
    doc_exts = TechnicalPatterns.DOC_EXTS
    test_exts = TechnicalPatterns.TEST_EXTS

    # Collect metrics from each commit
    for commit in commits:
        authors.add(commit.get("author_name"))
        dates.append(commit.get("authored_datetime"))
        messages.append(commit.get("message_summary"))
        files = commit.get("files", [])
        
        for f in files:
            status = f.get("status")
            file_status_counter[status] += 1
            path = f.get("path_after") or f.get("path_before")
            
            if path:
                total_files_changed.add(path)
                ext = os.path.splitext(path)[1].lower()
                fname = os.path.basename(path).lower()
                
                # NEW: Track language from file
                language = f.get("language")
                if language:
                    language_counter[language] += 1
                
                # NEW: Track code lines added
                code_lines = f.get("code_lines_added", 0)
                if code_lines:
                    total_code_lines_added += code_lines
                
                # Strict test-file detection
                if any(fname.endswith(e) or fname.startswith(e) for e in test_exts) or (ext and fname.endswith("_test" + ext)):
                    file_types_counter["test"] += 1
                elif ext in doc_exts:
                    file_types_counter["docs"] += 1
                elif ext in code_exts:
                    file_types_counter["code"] += 1
                else:
                    file_types_counter["other"] += 1
        
        roles.update(infer_roles_from_commit_files(files))
        
    # Calculate duration in days between first and last commit
    def parse_dt(dt): return datetime.fromisoformat(dt)
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
        "languages": list(language_counter.keys()),  # NEW: Languages detected
        "total_lines": total_code_lines_added,  # NEW: Total code lines for consistency
        "sample_messages": (messages[:5] + messages[len(messages)//2:len(messages)//2+5] + messages[-5:] if len(messages) >= 20 else messages), 
        "roles": list(roles),
    }
    return metrics

# --- Role inference for GitHub commits ---
def infer_roles_from_commit_files(files):
    """
    Infers roles played based on file types changed in GitHub commits.
    Updated to use language field when available.
    Returns a set of detected roles.
    """
    roles = set()
    
    # Language-based role mapping
    language_roles = {
        "JavaScript": "frontend",
        "TypeScript": "frontend", 
        "CSS": "frontend",
        "HTML": "frontend",
        "Python": "backend",
        "Java": "backend",
        "Go": "backend",
        "Ruby": "backend",
        "C++": "backend",
        "C": "backend",
        "SQL": "database",
        "Shell": "devops",
        "Dockerfile": "devops"
    }
    
    # Extension-based fallback
    frontend_exts = {".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".vue", ".svelte"}
    backend_exts = {".py", ".java", ".rb", ".go", ".cpp", ".c", ".php", ".cs"}
    database_exts = {".sql", ".db", ".json"}
    devops_exts = {".yml", ".yaml", ".sh", ".dockerfile"}
    datascience_exts = {".ipynb", ".csv", ".pkl", ".r", ".scala"}

    for f in files:
        path = f.get("path_after") or f.get("path_before", "")
        ext = os.path.splitext(path)[1].lower()
        fname = os.path.basename(path).lower()
        
        # NEW: Try language-based detection first
        language = f.get("language")
        if language and language in language_roles:
            roles.add(language_roles[language])
        else:
            # Fallback to extension-based detection
            if ext in frontend_exts:
                roles.add("frontend")
            elif ext in backend_exts:
                roles.add("backend")
            elif ext in database_exts:
                roles.add("database")
            elif ext in devops_exts or "dockerfile" in fname:
                roles.add("devops")
            elif ext in datascience_exts:
                roles.add("data science")

    return roles


def _detect_design_patterns(all_identifiers: List[str], function_names: List[str]) -> List[str]:
    """Helper: Detect design patterns from code identifiers."""
    patterns = []
    
    # Factory Pattern
    factory_indicators = ["factory", "createfactory", "factorymethod", "abstractfactory", "builder", "createbuilder"]
    if any(any(indicator in name for indicator in factory_indicators) for name in all_identifiers):
        creation_patterns = ["create", "make", "build", "new", "construct"]
        if sum(1 for name in function_names if any(pattern in name for pattern in creation_patterns)) >= 2:
            patterns.append("Factory Pattern")
    
    # Observer Pattern - FIXED LOGIC
    observer_indicators = ["observer", "observable", "subject", "subscriber", "notify", "emit", "subscribe", "broadcast", "update"]
    observer_count = 0
    
    # Check for observer-related identifiers
    for identifier in all_identifiers:
        if any(indicator in identifier.lower() for indicator in observer_indicators):
            observer_count += 1
    
    # Check for observer-related method names
    observer_methods = ["subscribe", "notify", "emit", "listen", "observe", "update", "broadcast", "notify_subscribers"]
    observer_method_count = sum(1 for name in function_names if any(method in name.lower() for method in observer_methods))
    
    # If we have multiple observer indicators or at least one clear observer method
    if observer_count >= 2 or observer_method_count >= 1:
        patterns.append("Observer Pattern")
    
    # Strategy Pattern
    strategy_indicators = ["strategy", "algorithm", "handler", "processor"]
    if any(any(indicator in name for indicator in strategy_indicators) for name in all_identifiers):
        if any("execute" in name or "process" in name or "handle" in name for name in function_names):
            patterns.append("Strategy Pattern")
    
    # Singleton Pattern
    singleton_indicators = ["singleton", "instance", "getinstance", "createinstance", "shared"]
    if any(any(indicator in name for indicator in singleton_indicators) for name in all_identifiers):
        if any("getinstance" in name or "instance" in name for name in function_names):
            patterns.append("Singleton Pattern")
    
    # Command Pattern
    command_indicators = ["command", "execute", "executor", "invoker"]
    if any(any(indicator in name for indicator in command_indicators) for name in all_identifiers):
        if any("execute" in name or "invoke" in name for name in function_names):
            patterns.append("Command Pattern")
    
    # Repository Pattern
    repository_indicators = ["repository", "repo", "datarepository", "dataaccess"]
    if any(any(indicator in name for indicator in repository_indicators) for name in all_identifiers):
        patterns.append("Repository Pattern")
    
    return patterns

def _detect_architectural_patterns(all_identifiers: List[str], function_names: List[str], 
                                 component_names: List[str], import_str: str) -> List[str]:
    """Helper: Detect architectural patterns."""
    patterns = []
    
    # MVC/MVP/MVVM Architecture
    mvc_indicators = {
        "controller": ["controller", "ctrl", "controllerbase"],
        "model": ["model", "viewmodel", "datamodel", "entity"],
        "view": ["view", "viewcontroller", "presenter", "template"]
    }
    
    mvc_found = {"controller": False, "model": False, "view": False}
    for category, indicators in mvc_indicators.items():
        if any(any(indicator in name for indicator in indicators) 
               for name in component_names + function_names):
            mvc_found[category] = True
    
    if sum(mvc_found.values()) >= 2:
        if mvc_found["controller"] and mvc_found["view"]:
            patterns.append("MVC Architecture")
        elif any("presenter" in name for name in component_names):
            patterns.append("MVP Architecture")
        elif any("viewmodel" in name for name in component_names):
            patterns.append("MVVM Architecture")
    
    # Service-Oriented Architecture
    service_indicators = ["service", "serviceimpl", "servicebase", "webservice"]
    service_count = sum(1 for name in function_names + component_names 
                       if any(indicator in name for indicator in service_indicators))
    if service_count >= 2:
        patterns.append("Service-Oriented Architecture")
    
    # Microservices Architecture
    microservice_indicators = ["microservice", "service", "api", "gateway", "apigateway"]
    microservice_frameworks = ["spring", "express", "flask", "fastapi", "gin"]
    has_microservice_framework = any(fw in import_str for fw in microservice_frameworks)
    microservice_patterns = sum(1 for name in all_identifiers 
                               if any(indicator in name for indicator in microservice_indicators))
    
    if microservice_patterns >= 3 and has_microservice_framework:
        patterns.append("Microservices Architecture")
    
    # RESTful API Architecture
    rest_indicators = ["rest", "restapi", "restcontroller", "api", "endpoint"]
    http_methods = ["get", "post", "put", "delete", "patch"]
    has_rest_patterns = any(any(indicator in name for indicator in rest_indicators) 
                           for name in all_identifiers)
    has_http_methods = sum(1 for name in function_names 
                          if any(method in name for method in http_methods)) >= 2
    
    if has_rest_patterns and has_http_methods:
        patterns.append("RESTful API Architecture")
    
    # Event-Driven Architecture
    event_indicators = ["event", "eventhandler", "message", "queue", "pubsub", "kafka"]
    if any(any(indicator in name for indicator in event_indicators) for name in all_identifiers):
        patterns.append("Event-Driven Architecture")
    
    # Layered Architecture
    layer_indicators = ["layer", "presentation", "business", "service", "data", "repository"]
    layer_count = sum(1 for name in all_identifiers 
                     if any(indicator in name for indicator in layer_indicators))
    if layer_count >= 3:
        patterns.append("Layered Architecture")
    
    return patterns

def _analyze_development_practices(all_components: List[Dict], detected_frameworks: List[str]) -> List[str]:
    """Helper: Analyze development practices from components."""
    practices = []
    
    hooks_found = []
    state_variables_found = []
    components_with_props = []
    
    for comp in all_components:
        hooks_used = comp.get("hooks_used", [])
        if hooks_used:
            hooks_found.extend(hooks_used)
        
        state_vars = comp.get("state_variables", [])
        if state_vars:
            state_variables_found.extend(state_vars)
        
        props = comp.get("props", [])
        if props:
            components_with_props.append(comp.get("name", ""))
    
    # Add practices based on actual data
    if hooks_found:
        unique_hooks = set(hooks_found)
        if detected_frameworks:
            framework_names = "/".join(detected_frameworks)
            practices.append(f"{framework_names} Hooks/Lifecycle ({len(unique_hooks)} types)")
        else:
            practices.append(f"Component Hooks/Lifecycle ({len(unique_hooks)} types)")
    
    if state_variables_found:
        if detected_frameworks:
            framework_names = "/".join(detected_frameworks)
            practices.append(f"{framework_names} State Management")
        else:
            practices.append("Component State Management")
    
    if components_with_props:
        practices.append(f"Component Props/Data Flow ({len(components_with_props)} components)")
    
    return practices

def analyze_code_patterns_from_parsed(parsed_files: List[Dict]) -> Dict:
    """
    Analyze code patterns, architecture, and practices from parsed files.
    Updated to handle new JSON structure with entities.
    """
    patterns = {
        "frameworks_detected": [],
        "design_patterns": [],
        "architectural_patterns": [],
        "development_practices": [],
        "technology_stack": []
    }
    
    # Collect all data from both old and new structures
    all_imports = []
    all_functions = []
    all_components = []
    all_classes = []
    
    for file in parsed_files:
        all_imports.extend(file.get("imports", []))
        all_imports.extend(file.get("dependencies_internal", []))
        
        entities = file.get("entities", {})
        
        # Handle functions (new: entities.functions, old: functions)
        functions = entities.get("functions", []) or file.get("functions", [])
        all_functions.extend(functions)
        
        # Handle components (new: entities.components, old: components)
        components = entities.get("components", []) or file.get("components", [])
        all_components.extend(components)
        
        # Handle classes (new structure only)
        classes = entities.get("classes", [])
        all_classes.extend([cls for cls in classes if cls.get("name")])  # Filter out null names
    
    # Extract identifiers from all sources
    function_names = []
    function_calls = []
        # From standalone functions
    for func in all_functions:
        name = func.get("name", "")
        if name:
            function_names.append(name.lower())
            function_calls.extend([call.lower() for call in func.get("calls", [])])
    
    # From class methods
    for cls in all_classes:
        methods = cls.get("methods", [])
        for method in methods:
            name = method.get("name", "")
            if name:
                function_names.append(name.lower())
                function_calls.extend([call.lower() for call in method.get("calls", [])])
    
    component_names = [comp.get("name", "").lower() for comp in all_components if comp.get("name")]
    class_names = [cls.get("name", "").lower() for cls in all_classes if cls.get("name")]
    
    all_identifiers = function_names + component_names + class_names + function_calls
    import_str = ' '.join(all_imports).lower()
    
    # Use helper functions for focused analysis
    patterns["frameworks_detected"] = _detect_frameworks(all_imports)
    patterns["design_patterns"] = _detect_design_patterns(all_identifiers, function_names)
    patterns["architectural_patterns"] = _detect_architectural_patterns(
        all_identifiers, function_names, component_names + class_names, import_str)
    patterns["development_practices"] = _analyze_development_practices(
        all_components, patterns["frameworks_detected"])
    
    # Add backend API detection
    backend_frameworks = [fw for fw in patterns["frameworks_detected"] 
                         if fw in ['Flask', 'Django', 'Express.js', 'Spring', 'Laravel', 'Ruby on Rails']]
    if backend_frameworks:
        patterns["architectural_patterns"].append("Web API Development")
        # Technology stack
    languages = set()
    for file in parsed_files:
        lang = file.get("language", "")
        if lang:
            languages.add(lang.title())
    patterns["technology_stack"] = list(languages)
    
    return patterns

# Replace the calculate_advanced_complexity_from_parsed function:

def calculate_advanced_complexity_from_parsed(parsed_files: List[Dict]) -> Dict:
    """
    Calculate advanced complexity metrics from parsed files with consistent naming.
    Provides actionable maintainability insights.
    """
    complexity_metrics = {
        "function_complexity": [],
        "component_complexity": [],
        "class_complexity": [],
        "maintainability_score": {},
        "complexity_breakdown": {}
    }
    
    total_functions = 0
    total_components = 0
    total_classes = 0
    total_lines = 0
    
    for file in parsed_files:
        total_lines += file.get("lines_of_code", 0)
        entities = file.get("entities", {})
        
        # Handle functions
        functions = entities.get("functions", []) or file.get("functions", [])
        for func in functions:
            total_functions += 1
            func_lines = func.get("lines_of_code", 0)
            calls = len(func.get("calls", []))
            params = len(func.get("parameters", []))
            
            # Weighted complexity score (lines have less weight than calls/params)
            complexity_score = func_lines + (calls * 2) + (params * 3)
            complexity_metrics["function_complexity"].append(complexity_score)
        
        # Handle components
        components = entities.get("components", []) or file.get("components", [])
        for comp in components:
            total_components += 1
            props = len(comp.get("props", []))
            state_vars = len(comp.get("state_variables", []))
            hooks = len(comp.get("hooks_used", []))
            
            # Component complexity (state and hooks are more complex than props)
            comp_complexity = props + (state_vars * 3) + (hooks * 2)
            complexity_metrics["component_complexity"].append(comp_complexity)
        
        # Handle classes
        classes = entities.get("classes", [])
        for cls in classes:
            if not cls.get("name"):
                continue
                
            total_classes += 1
            methods = cls.get("methods", [])
            total_class_lines = 0
            total_class_calls = 0
            method_count = 0
            
            for method in methods:
                if method.get("name"):
                    method_count += 1
                    total_class_lines += method.get("lines_of_code", 0)
                    total_class_calls += len(method.get("calls", []))
            
            # Class complexity: methods + normalized lines + calls
            class_complexity = (method_count * 5) + (total_class_lines // 10) + total_class_calls
            complexity_metrics["class_complexity"].append(class_complexity)
    
    # Calculate comprehensive maintainability metrics
    all_code_units = (complexity_metrics["function_complexity"] + 
                      complexity_metrics["class_complexity"] + 
                      complexity_metrics["component_complexity"])
    
    if all_code_units:
        avg_complexity = sum(all_code_units) / len(all_code_units)
        
        # Define thresholds based on unit type
        high_complexity_threshold = 50
        medium_complexity_threshold = 25
        
        high_complexity_count = sum(1 for c in all_code_units if c > high_complexity_threshold)
        medium_complexity_count = sum(1 for c in all_code_units if medium_complexity_threshold < c <= high_complexity_threshold)
        low_complexity_count = len(all_code_units) - high_complexity_count - medium_complexity_count
        
        # Calculate maintainability score (0-100, higher is better)
        complexity_ratio = high_complexity_count / len(all_code_units)
        maintainability_score = max(0, 100 - (complexity_ratio * 80) - (avg_complexity / 2))
        
        complexity_metrics["maintainability_score"] = {
            "overall_score": round(maintainability_score, 1),
            "average_complexity": round(avg_complexity, 2),
            "total_code_units": len(all_code_units),
            "complexity_distribution": {
                "low_complexity": low_complexity_count,
                "medium_complexity": medium_complexity_count, 
                "high_complexity": high_complexity_count
            },
            "quality_indicators": {
                "functions_per_file": round((total_functions + total_classes + total_components) / max(len(parsed_files), 1), 2),
                "avg_lines_per_unit": round(total_lines / max(len(all_code_units), 1), 2),
                "complexity_trend": "good" if complexity_ratio < 0.2 else "moderate" if complexity_ratio < 0.4 else "needs_attention"
            }
        }
        
        # Detailed breakdown by type
        complexity_metrics["complexity_breakdown"] = {
            "functions": {
                "count": total_functions,
                "avg_complexity": round(sum(complexity_metrics["function_complexity"]) / max(len(complexity_metrics["function_complexity"]), 1), 2),
                "high_complexity": sum(1 for c in complexity_metrics["function_complexity"] if c > high_complexity_threshold)
            },
            "classes": {
                "count": total_classes,
                "avg_complexity": round(sum(complexity_metrics["class_complexity"]) / max(len(complexity_metrics["class_complexity"]), 1), 2),
                "high_complexity": sum(1 for c in complexity_metrics["class_complexity"] if c > high_complexity_threshold)
            },
            "components": {
                "count": total_components,
                "avg_complexity": round(sum(complexity_metrics["component_complexity"]) / max(len(complexity_metrics["component_complexity"]), 1), 2),
                "high_complexity": sum(1 for c in complexity_metrics["component_complexity"] if c > high_complexity_threshold)
            }
        }
    
    return complexity_metrics

def generate_resume_summary_from_parsed(metrics: Dict) -> List[str]:
    """
    Generate detailed resume summary using enhanced NLP analysis for local projects.
    Updated to handle new metrics including classes and updated complexity structure.
    """
    summary = []
    
    # Project scope
    total_files = metrics.get('total_files', 0)
    total_lines = metrics.get('total_lines', 0)
    languages = metrics.get('languages', [])
    
    if languages:
        summary.append(f"Developed a comprehensive {total_lines}-line codebase across {total_files} files using {', '.join(languages)}")
    
    # Technical skills and frameworks
    #tech_keywords = metrics.get("technical_keywords", [])
   # if tech_keywords:
   #     summary.append(f"Demonstrated expertise in key technologies: {', '.join(tech_keywords[:8])}")
    
    # Framework and patterns
    patterns = metrics.get("code_patterns", {})
    frameworks = patterns.get("frameworks_detected", [])
    if frameworks:
        summary.append(f"Built solutions using {', '.join(frameworks)} framework{'s' if len(frameworks) > 1 else ''}")
    
    design_patterns = patterns.get("design_patterns", [])
    if design_patterns:
        summary.append(f"Implemented software design patterns: {', '.join(design_patterns)}")
    
    # Architecture and development practices
    arch_patterns = patterns.get("architectural_patterns", [])
    dev_practices = patterns.get("development_practices", [])
    
    if arch_patterns or dev_practices:
        practices_text = ", ".join(arch_patterns + dev_practices)
        summary.append(f"Applied modern development practices: {practices_text}")
    
    # Code quality and complexity (UPDATED TO NEW STRUCTURE)
    complexity = metrics.get("complexity_analysis", {})
    maintainability = complexity.get("maintainability_score", {})  # Changed from maintainability_factors
    
    if maintainability:
        overall_score = maintainability.get("overall_score", 0)
        avg_complexity = maintainability.get("average_complexity", 0)
        complexity_trend = maintainability.get("quality_indicators", {}).get("complexity_trend", "")
        
        if overall_score >= 80:
            summary.append("Maintained excellent code quality with high maintainability score and well-structured functions")
        elif overall_score >= 60:
            summary.append("Achieved good code maintainability with moderate complexity and clean architecture")
        elif overall_score >= 40:
            summary.append("Developed functional codebase with room for maintainability improvements")
        
        # Add specific complexity insights
        if complexity_trend == "good":
            summary.append("Followed best practices with low-complexity, maintainable code structure")
        elif complexity_trend == "moderate":
            summary.append("Balanced complexity management with structured development approach")
    
    # Component, function, and class metrics (updated for new structure)
    functions = metrics.get('functions', 0)
    components = metrics.get('components', 0)
    classes = metrics.get('classes', 0)
    
    if functions > 0 or components > 0 or classes > 0:
        architecture_parts = []
        if functions > 0:
            architecture_parts.append(f"{functions} functions")
        if classes > 0:
            architecture_parts.append(f"{classes} classes")
        if components > 0:
            architecture_parts.append(f"{components} components")
        
        summary.append(f"Architected modular solution with {' and '.join(architecture_parts)}")
    
    # Complexity breakdown insights (NEW)
    complexity_breakdown = complexity.get("complexity_breakdown", {})
    if complexity_breakdown:
        high_complexity_items = []
        
        for unit_type, data in complexity_breakdown.items():
            high_count = data.get("high_complexity", 0)
            total_count = data.get("count", 0)
            
            if total_count > 0 and high_count == 0:
                high_complexity_items.append(f"all {unit_type}")
        
        if high_complexity_items:
            summary.append(f"Maintained low complexity across {' and '.join(high_complexity_items)}")
    
    # Import and dependency analysis (updated for new structure)
    imports = metrics.get('imports', [])
    internal_deps = metrics.get('dependencies_internal', [])
    
    if len(imports) > 5:
        summary.append(f"Integrated {len(imports)} external libraries and dependencies for enhanced functionality")
    
    if len(internal_deps) > 3:
        summary.append(f"Designed modular architecture with {len(internal_deps)} internal dependencies promoting code reusability")
    
    # Quality indicators (NEW)
    quality_indicators = maintainability.get("quality_indicators", {})
    if quality_indicators:
        functions_per_file = quality_indicators.get("functions_per_file", 0)
        if functions_per_file > 0 and functions_per_file <= 5:
            summary.append("Followed clean code principles with well-organized file structure")
        elif functions_per_file > 10:
            summary.append("Developed feature-rich modules with comprehensive functionality")
    
    return summary

# Aggregate metrics from parsed source files
def aggregate_parsed_files_metrics(parsed_files: List[Dict]) -> Dict:
    """
    Aggregates key metrics from a list of parsed file dicts.
    Updated to handle new JSON structure with entities.
    """
    file_types_counter = Counter()
    
    # File type extensions for classification
    code_exts = TechnicalPatterns.CODE_EXTS
    doc_exts = TechnicalPatterns.DOC_EXTS
    test_exts = TechnicalPatterns.TEST_EXTS
    
    metrics = {
        "languages": set(),
        "total_files": 0,
        "total_lines": 0,
        "functions": 0,
        "components": 0,
        "classes": 0,  # New for classes
        "roles": set(),
        "imports": set(),
        "dependencies_internal": set(),  # New for internal dependencies
        "average_function_length": [],
        "comment_ratios": [],
        "code_files_changed": 0, #new for contribution by filetype
        "doc_files_changed": 0,
        "test_files_changed": 0,
        "other_files_changed": 0
    }

    # Collect metrics from each file
    for file in parsed_files:
        path = file.get("file_path")
        ext = os.path.splitext(path)[1].lower()
        fname = os.path.basename(path).lower()
        # Strict test-file detection: filename-only prefixes/suffixes and known test extensions
        if any(fname.endswith(e) or fname.startswith(e) for e in test_exts)or (ext and fname.endswith("_test" + ext)):
            file_types_counter["test"] += 1
        elif ext in doc_exts:
            file_types_counter["docs"] += 1
        elif ext in code_exts:
            file_types_counter["code"] += 1
        else:
            file_types_counter["other"] += 1
        
        metrics["languages"].add(file.get("language"))
        metrics["total_files"] += 1
        metrics["total_lines"] += file.get("lines_of_code", 0)
        
        # Handle imports and internal dependencies
        metrics["imports"].update(file.get("imports", []))
        metrics["dependencies_internal"].update(file.get("dependencies_internal", []))
        
        entities = file.get("entities", {})
        
        # Count functions (new: entities.functions, old: functions)
        functions = entities.get("functions", []) or file.get("functions", [])
        metrics["functions"] += len(functions)
        
        # Count components (new: entities.components, old: components)
        components = entities.get("components", []) or file.get("components", [])
        metrics["components"] += len(components)
        
        # Count classes (new structure only) - exclude null names
        classes = entities.get("classes", [])
        valid_classes = [cls for cls in classes if cls.get("name")]
        metrics["classes"] += len(valid_classes)
        
        # Infer roles from file
        metrics["roles"].update(infer_roles_from_file(file))
        
        # Handle metrics
        if "metrics" in file:
            if "average_function_length" in file["metrics"]:
                metrics["average_function_length"].append(file["metrics"]["average_function_length"])
            if "comment_ratio" in file["metrics"]:
                metrics["comment_ratios"].append(file["metrics"]["comment_ratio"])

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
    metrics["dependencies_internal"] = list(metrics["dependencies_internal"])
    metrics["code_files_changed"] = file_types_counter["code"]  # new for contribution by filetype
    metrics["doc_files_changed"] = file_types_counter["docs"]
    metrics["test_files_changed"] = file_types_counter["test"]
    metrics["other_files_changed"] = file_types_counter["other"]
    return metrics


# --- Role inference for local files ---
def infer_roles_from_file(file):
    """
    Infers roles played in a local project file based on file path and imports.
    Returns a set of detected roles.
    """
    roles = set()
    path = file.get("file_path", "").lower()
    imports = [imp.lower() for imp in file.get("imports", [])]

    # Define keyword sets for each role
    frontend_keywords = {"frontend", "src", "component", "react", "vue", "angular", ".js", ".jsx", ".ts", ".tsx", ".css", ".html"}
    backend_keywords = {"backend", "api", "server", "django", "flask", "express", ".py", ".java", ".rb", ".go", ".cpp", ".c"}
    database_keywords = {"db", "database", "models", "sql", "mongodb", "postgres", "mysql", ".sql", ".db", ".json"}
    devops_keywords = {"docker", "ci", "pipeline", "deploy", "k8s", "kubernetes", ".yml", ".yaml", "dockerfile", ".sh"}
    datascience_keywords = {"notebook", "pandas", "numpy", "sklearn", "matplotlib", ".ipynb", ".csv", ".pkl"}

    # Helper to check keywords in path or imports
    def has_keyword(keywords):
        return any(kw in path or kw in imports for kw in keywords)

    if has_keyword(frontend_keywords):
        roles.add("frontend")
    if has_keyword(backend_keywords):
        roles.add("backend")
    if has_keyword(database_keywords):
        roles.add("database")
    if has_keyword(devops_keywords):
        roles.add("devops")
    if has_keyword(datascience_keywords):
        roles.add("data science")

    return roles

# Main entry point for local project analysis
def analyze_parsed_project(parsed_files: List[Dict], llm_client=None) -> Dict:
    """
    Analyze a project from parsed file dicts and return a structured JSON summary.
    """
    # Get existing rich analysis
    metrics = aggregate_parsed_files_metrics(parsed_files)
    technical_keywords = extract_technical_keywords_from_parsed(parsed_files)
    code_patterns = analyze_code_patterns_from_parsed(parsed_files)
    complexity_analysis = calculate_advanced_complexity_from_parsed(parsed_files)
    
    # Enhanced metrics for analysis
    metrics["technical_keywords"] = technical_keywords
    metrics["code_patterns"] = code_patterns
    metrics["complexity_analysis"] = complexity_analysis
    
    if llm_client:
        # Use LLM for resume bullets - FIXED TO ENSURE ARRAY
        resume_prompt = (
                "Generate exactly 3-5 professional resume bullet points based on this project analysis. "
                "Return ONLY the bullet points, one per line, without any explanatory text. "
                "Each line should start with '•' followed by the bullet point. "
                "Focus on quantifiable achievements and technical expertise.\n\n"
                "PROJECT METRICS:\n"
                f"{json.dumps(metrics, indent=2)}"
            )
        
        llm_response = llm_client.generate(resume_prompt)
        if llm_response:
            # Split by newlines and clean up
            raw_bullets = llm_response.strip().split('\n')
            # Filter out empty lines and clean up bullet formatting
            resume_bullets = []
            for bullet in raw_bullets:
                cleaned = bullet.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                if cleaned and len(cleaned) > 10:  # Skip very short lines
                    resume_bullets.append(cleaned)
        else:
            # Fallback to NLP analysis if LLM fails
            resume_bullets = generate_resume_summary_from_parsed(metrics)
    else:
        # Use existing enhanced NLP analysis
        resume_bullets = generate_resume_summary_from_parsed(metrics)
    
    # Ensure resume_bullets is always a list
    if not isinstance(resume_bullets, list):
        resume_bullets = [str(resume_bullets)] if resume_bullets else []
    
    return {
        "Resume_bullets": resume_bullets,  # Always an array
        "Metrics": {
            "languages": metrics["languages"],
            "total_files": metrics["total_files"],
            "total_lines": metrics["total_lines"],
            "functions": metrics["functions"],
            "components": metrics["components"],
            "classes": metrics["classes"],
            "roles": metrics["roles"],
            "average_function_length": metrics["average_function_length"],
            "average_comment_ratio": metrics["average_comment_ratio"],
            "code_files_changed": metrics["code_files_changed"],
            "doc_files_changed": metrics["doc_files_changed"],
            "test_files_changed": metrics["test_files_changed"],
            "technical_keywords": technical_keywords,
            "code_patterns": code_patterns,
            "complexity_analysis": complexity_analysis
        }
    }

# Main entry point for github project analysis
def analyze_github_project(commits: List[Dict], llm_client=None) -> Dict:
    """
    Analyze a project from GitHub commit dicts and return a structured JSON summary.
    """
    # Get existing rich analysis
    metrics = aggregate_github_individual_metrics(commits)
    technical_keywords = extract_technical_keywords_from_github(commits)
    development_patterns = analyze_github_development_patterns(commits)
    commit_patterns = analyze_github_commit_patterns(commits)
    
    # Enhanced metrics for analysis
    metrics["technical_keywords"] = technical_keywords
    metrics["development_patterns"] = development_patterns
    metrics["commit_patterns"] = commit_patterns  # NEW
    if llm_client:
        # Use LLM for resume bullets - FIXED TO ENSURE ARRAY
        resume_prompt = (
                "Generate exactly 3-5 professional resume bullet points based on this GitHub project analysis. "
                "Return ONLY the bullet points, one per line, without any explanatory text. "
                "Each line should start with '•' followed by the bullet point. "
                "Focus on quantifiable contributions and collaborative development.\n\n"
                "PROJECT METRICS:\n"
                f"{json.dumps(metrics, indent=2)}"
            )
        
        llm_response = llm_client.generate(resume_prompt)
        if llm_response:
            # Split by newlines and clean up
            raw_bullets = llm_response.strip().split('\n')
            # Filter out empty lines and clean up bullet formatting
            resume_bullets = []
            for bullet in raw_bullets:
                cleaned = bullet.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                if cleaned and len(cleaned) > 10:  # Skip very short lines
                    resume_bullets.append(cleaned)
        else:
            # Fallback to NLP analysis if LLM fails
            resume_bullets = generate_github_resume_summary(metrics)
    else:
        # Use existing enhanced NLP analysis
        resume_bullets = generate_github_resume_summary(metrics)
    
    # Ensure resume_bullets is always a list
    if not isinstance(resume_bullets, list):
        resume_bullets = [str(resume_bullets)] if resume_bullets else []
    
    return {
        "Resume_bullets": resume_bullets,  # Always an array
        "Metrics": {
            "authors": metrics["authors"],
            "total_commits": metrics["total_commits"],
            "duration_days": metrics["duration_days"],
            "files_added": metrics["files_added"],
            "files_modified": metrics["files_modified"],
            "files_deleted": metrics["files_deleted"],
            "total_files_changed": metrics["total_files_changed"],
            "code_files_changed": metrics["code_files_changed"],
            "doc_files_changed": metrics["doc_files_changed"],
            "test_files_changed": metrics["test_files_changed"],
            "languages": metrics["languages"],
            "total_lines": metrics["total_lines"],
            "roles": metrics["roles"],
            "technical_keywords": technical_keywords,
            "development_patterns": development_patterns
        }
    }