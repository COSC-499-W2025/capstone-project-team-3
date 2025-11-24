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

def analyze_github_development_patterns(commits: List[Dict]) -> Dict:
    """
    Analyze development patterns from GitHub commit history.
    """
    patterns = {
        "development_workflow": [],
        "collaboration_patterns": [],
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
    Generate detailed resume summary using enhanced analysis for GitHub projects.
    """
    summary = []
    
    # Contribution overview
    total_commits = metrics.get('total_commits', 0)
    duration = metrics.get('duration_days', 0)
    
    if duration > 0:
        summary.append(f"Contributed {total_commits} commits over {duration} days, demonstrating consistent development activity")
    else:
        summary.append(f"Delivered {total_commits} focused commits in a concentrated development effort")
    
    # File and code changes - FIXED FALLBACK
    files_added = metrics.get('files_added', 0)
    files_modified = metrics.get('files_modified', 0)
    code_files = metrics.get('code_files_changed', 0)
    total_files = metrics.get('total_files_changed', 0)
    
    if code_files > 0:
        summary.append(f"Implemented changes across {code_files} code files, with {files_added} new files created and {files_modified} existing files modified")
    elif total_files > 0:
        # FALLBACK: If no code files detected, mention total files changed
        summary.append(f"Modified {total_files} project files, including {files_added} new additions and {files_modified} enhancements")
    elif files_added > 0 or files_modified > 0:
        # FALLBACK: If only file operations detected
        summary.append(f"Contributed {files_added} new files and enhanced {files_modified} existing project assets")
    else:
        # FINAL FALLBACK: If no files detected at all
        summary.append(f"Made {total_commits} focused contributions to project development and maintenance")
    
    # Development patterns
    tech_keywords = metrics.get("technical_keywords", [])
    if tech_keywords:
        summary.append(f"Focused on key technical areas: {', '.join(tech_keywords[:6])}")
    
    dev_patterns = metrics.get("development_patterns", {})
    practices = dev_patterns.get("code_practices", [])
    if practices:
        summary.append(f"Followed industry best practices: {', '.join(practices)}")
    
    # Project evolution
    evolution = dev_patterns.get("project_evolution", [])
    if evolution:
        summary.append(f"Led development in: {', '.join(evolution)}")
    
    # Testing and documentation
    test_files = metrics.get('test_files_changed', 0)
    doc_files = metrics.get('doc_files_changed', 0)
    
    quality_aspects = []
    if test_files > 0:
        quality_aspects.append(f"testing ({test_files} test files)")
    if doc_files > 0:
        quality_aspects.append(f"documentation ({doc_files} docs)")
    
    if quality_aspects:
        summary.append(f"Emphasized code quality through {' and '.join(quality_aspects)}")
    
    # Sample impactful commit messages
    sample_messages = metrics.get('sample_messages', [])
    if sample_messages:
        impactful_commits = [msg for msg in sample_messages[:3] if any(keyword in msg.lower() 
                            for keyword in ['implement', 'add', 'create', 'build', 'develop'])]
        if impactful_commits:
            summary.append(f"Key contributions include: {'; '.join(impactful_commits)}")
    
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
    roles = set()
    
    # File type extensions for classification
    code_exts = {".py", ".js", ".java", ".cpp", ".c", ".ts", ".rb", ".go"}
    doc_exts = {".md"}
    test_exts = {"test_", "_test.py", ".spec.js", ".spec.ts"}

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
                if any(fname.endswith(e) or fname.startswith(e) for e in test_exts) or "test" in path.lower():
                    file_types_counter["test"] += 1
                elif ext in doc_exts:
                    file_types_counter["docs"] += 1
                elif ext in code_exts:
                    file_types_counter["code"] += 1
                else:
                    file_types_counter["other"] += 1
        roles.update(infer_roles_from_commit_files(files))
        
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
        "sample_messages": (messages[:5] + messages[len(messages)//2:len(messages)//2+5] + messages[-5:] if len(messages) >= 20 else messages), 
        "roles": list(roles),
    }
    return metrics

# --- Role inference for GitHub commits ---
def infer_roles_from_commit_files(files):
    """
    Infers roles played based on file types changed in GitHub commits.
    Returns a set of detected roles.
    """
    roles = set()
    # Define extension sets for each role
    frontend_exts = {".js", ".jsx", ".ts", ".tsx", ".css", ".html"}
    backend_exts = {".py", ".java", ".rb", ".go", ".cpp", ".c"}
    database_exts = {".sql", ".db", ".json"}
    devops_exts = {".yml", ".yaml", ".sh"}
    datascience_exts = {".ipynb", ".csv", ".pkl"}

    for f in files:
        path = f.get("path_after") or f.get("path_before", "")
        ext = os.path.splitext(path)[1].lower()
        fname = os.path.basename(path).lower()

        if ext in frontend_exts:
            roles.add("frontend")
        if ext in backend_exts:
            roles.add("backend")
        if ext in database_exts:
            roles.add("database")
        if ext in devops_exts or "dockerfile" in fname:
            roles.add("devops")
        if ext in datascience_exts:
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

def calculate_advanced_complexity_from_parsed(parsed_files: List[Dict]) -> Dict:
    """
    Calculate advanced complexity metrics from parsed files.
    Updated to handle new JSON structure with entities.
    """
    complexity_metrics = {
        "function_complexity": [],
        "component_complexity": [],
        "class_complexity": [],  # New for classes
        "maintainability_factors": {}
    }
    
    total_functions = 0
    total_components = 0
    total_classes = 0
    total_lines = 0
    
    for file in parsed_files:
        total_lines += file.get("lines_of_code", 0)
        entities = file.get("entities", {})
        
        # Handle functions (new: entities.functions, old: functions)
        functions = entities.get("functions", []) or file.get("functions", [])
        for func in functions:
            total_functions += 1
            func_lines = func.get("lines_of_code", 0)
            calls = len(func.get("calls", []))
            params = len(func.get("parameters", []))
            
            # Simple complexity score
            complexity_score = func_lines + calls + (params * 2)
            complexity_metrics["function_complexity"].append(complexity_score)
        
        # Handle components (new: entities.components, old: components)
        components = entities.get("components", []) or file.get("components", [])
        for comp in components:
            total_components += 1
            props = len(comp.get("props", []))
            state_vars = len(comp.get("state_variables", []))
            hooks = len(comp.get("hooks_used", []))
            
                        # Component complexity score
            comp_complexity = props + (state_vars * 2) + hooks
            complexity_metrics["component_complexity"].append(comp_complexity)
        
        # Handle classes (new structure only)
        classes = entities.get("classes", [])
        for cls in classes:
            if not cls.get("name"):  # Skip null class names
                continue
                
            total_classes += 1
            methods = cls.get("methods", [])
            total_class_lines = 0
            total_class_calls = 0
            
            for method in methods:
                if method.get("name"):  # Skip null method names
                    total_class_lines += method.get("lines_of_code", 0)
                    total_class_calls += len(method.get("calls", []))
            
            # Class complexity based on methods, lines, and calls
            class_complexity = len(methods) + (total_class_lines // 10) + total_class_calls
            complexity_metrics["class_complexity"].append(class_complexity)
    
    # Calculate maintainability factors
    all_complexities = complexity_metrics["function_complexity"] + complexity_metrics["class_complexity"]
    
    if all_complexities:
        avg_complexity = sum(all_complexities) / len(all_complexities)
        high_complexity_items = sum(1 for c in all_complexities if c > 50)
        
        complexity_metrics["maintainability_factors"] = {
            "average_function_complexity": round(avg_complexity, 2),
            "high_complexity_functions": high_complexity_items,
            "complexity_ratio": round(high_complexity_items / max(len(all_complexities), 1), 2),
            "functions_per_file": round((total_functions + total_classes) / max(len(parsed_files), 1), 2),
            "lines_per_function": round(total_lines / max(total_functions + total_classes, 1), 2) if (total_functions + total_classes) > 0 else 0
        }
    
    return complexity_metrics

def generate_resume_summary_from_parsed(metrics: Dict) -> List[str]:
    """
    Generate detailed resume summary using enhanced NLP analysis for local projects.
    Updated to handle new metrics including classes and internal dependencies.
    """
    summary = []
    
    # Project scope
    total_files = metrics.get('total_files', 0)
    total_lines = metrics.get('total_lines', 0)
    languages = metrics.get('languages', [])
    
    if languages:
        summary.append(f"Developed a comprehensive {total_lines}-line codebase across {total_files} files using {', '.join(languages)}")
    
    # Technical skills and frameworks
    tech_keywords = metrics.get("technical_keywords", [])
    if tech_keywords:
        summary.append(f"Demonstrated expertise in key technologies: {', '.join(tech_keywords[:8])}")
    
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
    
    # Code quality and complexity
    complexity = metrics.get("complexity_analysis", {})
    maintainability = complexity.get("maintainability_factors", {})
    
    if maintainability:
        avg_complexity = maintainability.get("average_function_complexity", 0)
        if avg_complexity < 30:
            summary.append("Maintained high code quality with well-structured, low-complexity functions")
        elif avg_complexity < 50:
            summary.append("Achieved good code maintainability with moderate complexity functions")
    
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
        
        summary.append(f"Architected {' and '.join(architecture_parts)}")
    
    # Import and dependency analysis (updated for new structure)
    imports = metrics.get('imports', [])
    internal_deps = metrics.get('dependencies_internal', [])
    
    if len(imports) > 5:
        summary.append(f"Integrated {len(imports)} external libraries and dependencies for enhanced functionality")
    
    if len(internal_deps) > 3:
        summary.append(f"Designed modular architecture with {len(internal_deps)} internal dependencies promoting code reusability")
    
    return summary

# Aggregate metrics from parsed source files
def aggregate_parsed_files_metrics(parsed_files: List[Dict]) -> Dict:
    """
    Aggregates key metrics from a list of parsed file dicts.
    Updated to handle new JSON structure with entities.
    """
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
    }

    # Collect metrics from each file
    for file in parsed_files:
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
def analyze_parsed_project(parsed_files: List[Dict], llm_client=None):
    """
    Analyze a project from parsed file dicts and return a resume summary.
    Uses LLM if provided, otherwise returns enhanced NLP analysis.
    """
    metrics = aggregate_parsed_files_metrics(parsed_files)
    
    if llm_client:
        # Use LLM to generate summary
        prompt = (
            "Given these aggregated project metrics:\n"
            f"{metrics}\n"
            "Generate resume-like bullet points summarizing the user's contributions, "
            "including key activities, skills, technologies, and impact."
            "Do NOT include any explanations, headings, or options—just the list."
        )
        return llm_client.generate(prompt)
    else:
        # Use enhanced NLP analysis
        metrics["technical_keywords"] = extract_technical_keywords_from_parsed(parsed_files)
        metrics["code_patterns"] = analyze_code_patterns_from_parsed(parsed_files)
        metrics["complexity_analysis"] = calculate_advanced_complexity_from_parsed(parsed_files)
        return generate_resume_summary_from_parsed(metrics)

# Main entry point for Github project analysis
def analyze_github_project(commits: List[Dict], llm_client=None):
    """
    Analyze a project from GitHub commit dicts and return a resume summary.
    Uses LLM if provided, otherwise returns enhanced NLP analysis.
    """
    metrics = aggregate_github_individual_metrics(commits)
    
    if llm_client:
        # Use LLM to generate summary
        prompt = (
            "Given these GitHub contribution metrics:\n"
            f"{metrics}\n"
            "Generate resume-like bullet points summarizing the user's contributions, "
            "including key activities, skills, technologies, and impact."
            "Do NOT include any explanations, headings, or options—just the list."
        )
        return llm_client.generate(prompt)
    else:
        # Use enhanced NLP analysis
        metrics["technical_keywords"] = extract_technical_keywords_from_github(commits)
        metrics["development_patterns"] = analyze_github_development_patterns(commits)
        return generate_github_resume_summary(metrics)
