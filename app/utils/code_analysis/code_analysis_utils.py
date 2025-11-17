from typing import Dict, List
import os
from datetime import datetime
from collections import Counter, defaultdict
import re

def extract_technical_keywords_from_parsed(parsed_files: List[Dict]) -> List[str]:
    """
    Extract meaningful technical keywords from parsed files using NLP techniques.
    """
    all_identifiers = []
    all_imports = []
    
    for file in parsed_files:
        # Collect function names, component names, and other identifiers
        functions = file.get("functions", [])
        components = file.get("components", [])
        imports = file.get("imports", [])
        
        # Extract function names and calls
        for func in functions:
            all_identifiers.append(func.get("name", ""))
            all_identifiers.extend(func.get("calls", []))
        
        # Extract component names, props, and hooks
        for comp in components:
            all_identifiers.append(comp.get("name", ""))
            all_identifiers.extend(comp.get("props", []))
            all_identifiers.extend(comp.get("state_variables", []))
            all_identifiers.extend(comp.get("hooks_used", []))
        
        all_imports.extend(imports)
    
    # Clean and filter technical terms
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
    
    # Process identifiers
    for identifier in all_identifiers:
        if identifier and len(identifier) > 2:
            # Split camelCase and snake_case
            words = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', identifier)
            tech_keywords.update(word.lower() for word in words if len(word) > 2)
    
    # Filter out common programming terms
    common_terms = {
        "function", "component", "state", "props", "data", "user", "name", 
        "get", "set", "add", "remove", "update", "delete", "create", "main"
    }
    
    filtered_keywords = [kw for kw in tech_keywords if kw not in common_terms and len(kw) > 2]
    
    # Return top keywords by frequency/importance
    return sorted(list(set(filtered_keywords)))[:15]

def _detect_frameworks(imports: List[str]) -> List[str]:
    """Helper: Detect frameworks from imports."""
    import_str = ' '.join(imports).lower()
    detected_frameworks = []
    
    framework_mapping = {
        'react': 'React',
        'vue': 'Vue.js', 
        'angular': 'Angular',
        'flask': 'Flask',
        'django': 'Django',
        'express': 'Express.js',
        'spring': 'Spring',
        'laravel': 'Laravel',
        'rails': 'Ruby on Rails'
    }
    
    for framework_key, framework_name in framework_mapping.items():
        if framework_key in import_str:
            detected_frameworks.append(framework_name)
    
    return detected_frameworks

def _detect_design_patterns(all_identifiers: List[str], function_names: List[str]) -> List[str]:
    """Helper: Detect design patterns from code identifiers."""
    patterns = []
    
    # Factory Pattern
    factory_indicators = ["factory", "createfactory", "factorymethod", "abstractfactory", "builder", "createbuilder"]
    if any(any(indicator in name for indicator in factory_indicators) for name in all_identifiers):
        creation_patterns = ["create", "make", "build", "new", "construct"]
        if sum(1 for name in function_names if any(pattern in name for pattern in creation_patterns)) >= 2:
            patterns.append("Factory Pattern")
    
    # Observer Pattern
    observer_indicators = ["observer", "observable", "subject", "subscriber", "notify", "emit", "subscribe"]
    if any(any(indicator in name for indicator in observer_indicators) for name in all_identifiers):
        observer_methods = ["subscribe", "notify", "emit", "listen", "observe", "update"]
        if sum(1 for name in function_names if any(method in name for method in observer_methods)) >= 2:
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
    Now refactored into focused helper functions for maintainability.
    """
    patterns = {
        "frameworks_detected": [],
        "design_patterns": [],
        "architectural_patterns": [],
        "development_practices": [],
        "technology_stack": []
    }
    
    # Collect all data
    all_imports = []
    all_functions = []
    all_components = []
    
    for file in parsed_files:
        all_imports.extend(file.get("imports", []))
        all_functions.extend(file.get("functions", []))
        all_components.extend(file.get("components", []))
    
    # Extract identifiers
    function_names = [func.get("name", "").lower() for func in all_functions]
    component_names = [comp.get("name", "").lower() for comp in all_components]
    function_calls = []
    for func in all_functions:
        function_calls.extend([call.lower() for call in func.get("calls", [])])
    
    all_identifiers = function_names + component_names + function_calls
    import_str = ' '.join(all_imports).lower()
    
    # Use helper functions for focused analysis
    patterns["frameworks_detected"] = _detect_frameworks(all_imports)
    patterns["design_patterns"] = _detect_design_patterns(all_identifiers, function_names)
    patterns["architectural_patterns"] = _detect_architectural_patterns(
        all_identifiers, function_names, component_names, import_str)
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
    """
    complexity_metrics = {
        "function_complexity": [],
        "component_complexity": [],
        "maintainability_factors": {}
    }
    
    total_functions = 0
    total_components = 0
    total_lines = 0
    
    for file in parsed_files:
        total_lines += file.get("lines_of_code", 0)
        functions = file.get("functions", [])
        components = file.get("components", [])
        
        # Analyze function complexity
        for func in functions:
            total_functions += 1
            func_lines = func.get("lines_of_code", 0)
            calls = len(func.get("calls", []))
            params = len(func.get("parameters", []))
            
            # Simple complexity score
            complexity_score = func_lines + calls + (params * 2)
            complexity_metrics["function_complexity"].append(complexity_score)
        
        # Analyze component complexity
        for comp in components:
            total_components += 1
            props = len(comp.get("props", []))
            state_vars = len(comp.get("state_variables", []))
            hooks = len(comp.get("hooks_used", []))
            
            # Component complexity score
            comp_complexity = props + (state_vars * 2) + hooks
            complexity_metrics["component_complexity"].append(comp_complexity)
    
    # Calculate maintainability factors
    if complexity_metrics["function_complexity"]:
        avg_func_complexity = sum(complexity_metrics["function_complexity"]) / len(complexity_metrics["function_complexity"])
        high_complexity_funcs = sum(1 for c in complexity_metrics["function_complexity"] if c > 50)
        
        complexity_metrics["maintainability_factors"] = {
            "average_function_complexity": round(avg_func_complexity, 2),
            "high_complexity_functions": high_complexity_funcs,
            "complexity_ratio": round(high_complexity_funcs / max(total_functions, 1), 2),
            "functions_per_file": round(total_functions / max(len(parsed_files), 1), 2),
            "lines_per_function": round(total_lines / max(total_functions, 1), 2) if total_functions > 0 else 0
        }
    
    return complexity_metrics

def generate_resume_summary_from_parsed(metrics: Dict) -> List[str]:
    """
    Generate detailed resume summary using enhanced NLP analysis for local projects.
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
    
    # Component and function metrics
    functions = metrics.get('functions', 0)
    components = metrics.get('components', 0)
    
    if functions > 0:
        summary.append(f"Architected {functions} functions" + (f" and {components} components" if components > 0 else ""))
    
    # Import analysis
    imports = metrics.get('imports', [])
    if len(imports) > 5:
        summary.append(f"Integrated {len(imports)} external libraries and dependencies for enhanced functionality")
    
    return summary


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
    }

    # Collect metrics from each file
    for file in parsed_files:
        metrics["languages"].add(file.get("language"))
        metrics["total_files"] += 1
        metrics["total_lines"] += file.get("lines_of_code", 0)
        metrics["functions"] += len(file.get("functions", []))
        metrics["components"] += len(file.get("components", []))
        metrics["roles"].update(infer_roles_from_file(file))
        metrics["imports"].update(file.get("imports", []))
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
    