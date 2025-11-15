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

def extract_technical_keywords_from_github(commits: List[Dict]) -> List[str]:
    """
    Extract technical keywords from GitHub commit messages and file changes.
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
    
    # Extract keywords from commit messages
    tech_terms = set()
    
    # Common technical keywords in commit messages
    tech_patterns = [
    # Development Actions (present and past tense)
    r'\b(implement|implemented|add|added|create|created|build|built|develop|developed|design|designed|refactor|refactored|optimize|optimized|fix|fixed|update|updated|enhance|enhanced|improve|improved|integrate|integrated|deploy|deployed|configure|configured|setup|set up|install|installed|remove|removed|delete|deleted|migrate|migrated|upgrade|upgraded|downgrade|downgraded)\b',
    # Architecture & Components
    r'\b(api|apis|database|databases|frontend|backend|fullstack|full-stack|component|components|service|services|module|modules|class|classes|function|functions|method|methods|library|libraries|framework|frameworks|middleware|plugin|plugins|extension|extensions|microservice|microservices|monolith)\b',
    # Testing & Quality
    r'\b(test|testing|tests|unit|units|integration|e2e|end-to-end|automation|automated|spec|specs|mock|mocks|stub|stubs|coverage|benchmark|benchmarks|performance|profiling|debugging|debug|validation|validate|verification|verify)\b',
    # DevOps & Infrastructure
    r'\b(docker|dockerfile|kubernetes|k8s|ci|cd|pipeline|pipelines|jenkins|github|actions|workflow|workflows|deploy|deployment|deployments|infrastructure|cloud|aws|azure|gcp|terraform|ansible|vagrant|nginx|apache|load|balancer|scaling|monitoring|logging|metrics)\b',
    # Frontend Technologies
    r'\b(react|reactjs|vue|vuejs|angular|angularjs|svelte|next|nextjs|nuxt|nuxtjs|gatsby|html|css|scss|sass|less|tailwind|bootstrap|jquery|typescript|javascript|js|ts|jsx|tsx|webpack|vite|parcel|babel|eslint|prettier)\b',
    # Backend Technologies
    r'\b(node|nodejs|express|expressjs|django|flask|fastapi|spring|springboot|laravel|rails|ruby|python|java|php|golang|go|rust|kotlin|scala|dotnet|csharp|nestjs|koa)\b',
    # Databases & Storage
    r'\b(mysql|postgresql|postgres|sqlite|mongodb|mongo|redis|elasticsearch|elastic|cassandra|dynamodb|firebase|firestore|orm|sql|nosql|migration|migrations|schema|schemas|index|indexes|query|queries|transaction|transactions)\b',
    # Mobile & Desktop
    r'\b(android|ios|swift|kotlin|flutter|dart|react-native|reactnative|xamarin|ionic|cordova|phonegap|electron|tauri|pwa|mobile|native|cross-platform)\b',
    # Data & Analytics
    r'\b(data|analytics|ml|ai|machine|learning|deep|neural|network|pandas|numpy|tensorflow|pytorch|sklearn|jupyter|notebook|visualization|dashboard|etl|pipeline|bigdata|spark|hadoop|kafka|stream|streaming)\b',
    # Security & Authentication
    r'\b(auth|authentication|authorization|oauth|jwt|token|tokens|security|secure|encryption|decrypt|encrypt|ssl|tls|https|cors|csrf|xss|hash|hashing|bcrypt|session|sessions|login|logout|signup|password|permissions|role|roles)\b',
    # Communication & Protocols
    r'\b(rest|restful|graphql|grpc|websocket|websockets|mqtt|http|https|api|soap|json|xml|yaml|protobuf|messaging|queue|queues|pub|sub|pubsub|webhook|webhooks)\b',
    # Version Control & Collaboration
    r'\b(git|github|gitlab|bitbucket|commit|commits|branch|branches|merge|merges|pull|request|requests|pr|fork|clone|push|rebase|cherry-pick|tag|tags|release|releases|version|versioning)\b',
    # Project Management & Methodologies
    r'\b(agile|scrum|kanban|sprint|sprints|story|stories|epic|epics|bug|bugs|issue|issues|feature|features|requirement|requirements|specification|specifications|documentation|docs|readme|changelog|license)\b'
]
    
    for message in all_messages:
        for pattern in tech_patterns:
            matches = re.findall(pattern, message)
            tech_terms.update(matches)
    
    # Extract meaningful file names
    for filename in all_file_names:
        if filename and len(filename) > 2 and not filename.endswith(('.git', '.md')):
            # Remove extensions and split camelCase
            name_without_ext = filename.split('.')[0]
            words = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', name_without_ext)
            tech_terms.update(word.lower() for word in words if len(word) > 2)
    
    return sorted(list(tech_terms))[:15]

def analyze_code_patterns_from_parsed(parsed_files: List[Dict]) -> Dict:
    """
    Analyze code patterns, architecture, and practices from parsed files.
    """
    patterns = {
        "frameworks_detected": [],
        "design_patterns": [],
        "architectural_patterns": [],
        "development_practices": [],
        "technology_stack": []
    }
    
    all_imports = []
    all_functions = []
    all_components = []
    
    for file in parsed_files:
        all_imports.extend(file.get("imports", []))
        all_functions.extend(file.get("functions", []))
        all_components.extend(file.get("components", []))
    
    # Framework Detection
    import_str = ' '.join(all_imports).lower()
    detected_frameworks = []
    
    # Detect all frameworks present
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
            patterns["frameworks_detected"].append(framework_name)
    
    # Generic Component Analysis (works for ANY framework)
    hooks_found = []
    state_variables_found = []
    components_with_props = []
    
    for comp in all_components:
        # Collect hooks (React, Vue Composition API, etc.)
        hooks_used = comp.get("hooks_used", [])
        if hooks_used:
            hooks_found.extend(hooks_used)
        
        # Collect state variables (React state, Vue data, Angular properties, etc.)
        state_vars = comp.get("state_variables", [])
        if state_vars:
            state_variables_found.extend(state_vars)
        
        # Collect props/inputs (React props, Vue props, Angular inputs, etc.)
        props = comp.get("props", [])
        if props:
            components_with_props.append(comp.get("name", ""))
    
    # Add practices based on actual data (not framework-specific)
    if hooks_found:
        unique_hooks = set(hooks_found)
        if detected_frameworks:
            framework_names = "/".join(detected_frameworks)
            patterns["development_practices"].append(f"{framework_names} Hooks/Lifecycle ({len(unique_hooks)} types)")
        else:
            patterns["development_practices"].append(f"Component Hooks/Lifecycle ({len(unique_hooks)} types)")
    
    if state_variables_found:
        if detected_frameworks:
            framework_names = "/".join(detected_frameworks)
            patterns["development_practices"].append(f"{framework_names} State Management")
        else:
            patterns["development_practices"].append("Component State Management")
    
    if components_with_props:
        patterns["development_practices"].append(f"Component Props/Data Flow ({len(components_with_props)} components)")
    
    # Backend Framework Analysis
    backend_frameworks = [fw for fw in detected_frameworks if fw in ['Flask', 'Django', 'Express.js', 'Spring', 'Laravel', 'Ruby on Rails']]
    if backend_frameworks:
        patterns["architectural_patterns"].append("Web API Development")
    
    # Enhanced Design Pattern Detection (more accurate and comprehensive)
    function_names = [func.get("name", "").lower() for func in all_functions]
    component_names = [comp.get("name", "").lower() for comp in all_components]
    function_calls = []
    for func in all_functions:
        function_calls.extend([call.lower() for call in func.get("calls", [])])

    all_identifiers = function_names + component_names + function_calls

    # Factory Pattern - More specific detection
    factory_indicators = [
        "factory", "createfactory", "factorymethod", "abstractfactory",
        "builder", "createbuilder", "builderfactory",
        "create", "makecreate", "newcreate", "buildcreate"
    ]
    if any(any(indicator in name for indicator in factory_indicators) for name in all_identifiers):
     # Additional validation - check for actual creation patterns
        creation_patterns = ["create", "make", "build", "new", "construct"]
        if sum(1 for name in function_names if any(pattern in name for pattern in creation_patterns)) >= 2:
            patterns["design_patterns"].append("Factory Pattern")

# Observer Pattern - More specific detection
    observer_indicators = [
        "observer", "observable", "subject", "subscriber", "publisher",
        "listener", "eventlistener", "watcher", "notify", "notifier",
        "emit", "emitter", "dispatch", "dispatcher", "broadcast",
        "subscribe", "unsubscribe", "addlistener", "removelistener"
    ]
    if any(any(indicator in name for indicator in observer_indicators) for name in all_identifiers):
    # Validate with multiple observer-related methods
        observer_methods = ["subscribe", "notify", "emit", "listen", "observe", "update"]
        if sum(1 for name in function_names if any(method in name for method in observer_methods)) >= 2:
            patterns["design_patterns"].append("Observer Pattern")

# Strategy Pattern - More specific detection
    strategy_indicators = [
        "strategy", "strategyfactory", "strategypattern",
        "algorithm", "algorithmstrategy", "context",
        "handler", "handlerfactory", "processor", "processorfactory"
    ]
    if any(any(indicator in name for indicator in strategy_indicators) for name in all_identifiers):
        # Validate with strategy-like structure
        if any("execute" in name or "process" in name or "handle" in name for name in function_names):
            patterns["design_patterns"].append("Strategy Pattern")

    # Singleton Pattern
    singleton_indicators = [
        "singleton", "instance", "getinstance", "createinstance",
        "shared", "sharedinstance", "default", "defaultinstance"
    ]
    if any(any(indicator in name for indicator in singleton_indicators) for name in all_identifiers):
        if any("getinstance" in name or "instance" in name for name in function_names):
            patterns["design_patterns"].append("Singleton Pattern")

    # Decorator Pattern
    decorator_indicators = [
        "decorator", "wrapper", "wrap", "decorate",
        "middleware", "interceptor", "proxy"
    ]
    if any(any(indicator in name for indicator in decorator_indicators) for name in all_identifiers):
        patterns["design_patterns"].append("Decorator Pattern")

    # Command Pattern
    command_indicators = [
        "command", "commandpattern", "execute", "executor",
        "invoker", "receiver", "undocommand", "redocommand"
    ]
    if any(any(indicator in name for indicator in command_indicators) for name in all_identifiers):
        if any("execute" in name or "invoke" in name for name in function_names):
            patterns["design_patterns"].append("Command Pattern")

    # Repository Pattern
    repository_indicators = [
        "repository", "repo", "datarepository", "userrepository",
        "dataaccess", "dal", "datasource"
    ]
    if any(any(indicator in name for indicator in repository_indicators) for name in all_identifiers):
        patterns["design_patterns"].append("Repository Pattern")

    # MVC/MVP/MVVM Architecture - More comprehensive
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

    if sum(mvc_found.values()) >= 2:  # At least 2 out of 3 MVC components
        if mvc_found["controller"] and mvc_found["view"]:
            patterns["architectural_patterns"].append("MVC Architecture")
        elif any("presenter" in name for name in component_names):
            patterns["architectural_patterns"].append("MVP Architecture")
        elif any("viewmodel" in name for name in component_names):
            patterns["architectural_patterns"].append("MVVM Architecture")

    # Service-Oriented Architecture - More specific
    service_indicators = [
        "service", "serviceimpl", "servicebase", "webservice",
        "apiservice", "dataservice", "userservice", "authservice"
    ]
    service_count = sum(1 for name in function_names + component_names 
    if any(indicator in name for indicator in service_indicators))

    if service_count >= 2:  # Multiple services indicate SOA
        patterns["architectural_patterns"].append("Service-Oriented Architecture")

    # Microservices Architecture
    microservice_indicators = [
        "microservice", "service", "api", "gateway", "apigateway",
        "serviceregistry", "discovery", "circuit", "circuitbreaker"
    ]
    # Check imports for microservice frameworks
    microservice_frameworks = ["spring", "express", "flask", "fastapi", "gin"]
    has_microservice_framework = any(fw in import_str for fw in microservice_frameworks)

    microservice_patterns = sum(1 for name in all_identifiers 
                        if any(indicator in name for indicator in microservice_indicators))

    if microservice_patterns >= 3 and has_microservice_framework:
        patterns["architectural_patterns"].append("Microservices Architecture")

    # RESTful API Architecture
    rest_indicators = [
        "rest", "restapi", "restcontroller", "api", "endpoint",
        "resource", "restresource", "httpclient", "webclient"
    ]
    http_methods = ["get", "post", "put", "delete", "patch"]

    has_rest_patterns = any(any(indicator in name for indicator in rest_indicators) 
    for name in all_identifiers)
    has_http_methods = sum(1 for name in function_names 
        if any(method in name for method in http_methods)) >= 2

    if has_rest_patterns and has_http_methods:
        patterns["architectural_patterns"].append("RESTful API Architecture")

    # Event-Driven Architecture
    event_indicators = [
        "event", "eventhandler", "eventbus", "eventstore",
        "message", "messagehandler", "queue", "messagequeue",
        "pub", "sub", "pubsub", "kafka", "rabbitmq"
    ]
    if any(any(indicator in name for indicator in event_indicators) for name in all_identifiers):
        patterns["architectural_patterns"].append("Event-Driven Architecture")

    # Layered Architecture
    layer_indicators = [
        "layer", "presentation", "presentationlayer",
        "business", "businesslayer", "service", "servicelayer",
        "data", "datalayer", "repository", "repositorylayer"
    ]
    layer_count = sum(1 for name in all_identifiers 
                 if any(indicator in name for indicator in layer_indicators))

    if layer_count >= 3:  # Multiple layers suggest layered architecture
        patterns["architectural_patterns"].append("Layered Architecture")
    # Technology Stack Analysis
        languages = set()
        for file in parsed_files:
            lang = file.get("language", "")
            if lang:
                languages.add(lang.title())
    
        patterns["technology_stack"] = list(languages)
    
    return patterns

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
    
    # Analyze file changes for project evolution
    file_extensions = defaultdict(int)
    for commit in commits:
        for file in commit.get("files", []):
            path = file.get("path_after") or file.get("path_before", "")
            if path:
                ext = path.split('.')[-1].lower()
                file_extensions[ext] += 1
    
    if file_extensions:
        dominant_tech = max(file_extensions, key=file_extensions.get)
        if dominant_tech in ['js', 'jsx', 'ts', 'tsx']:
            patterns["project_evolution"].append("JavaScript/Frontend Development")
        elif dominant_tech in ['py']:
            patterns["project_evolution"].append("Python Development")
        elif dominant_tech in ['java']:
            patterns["project_evolution"].append("Java Development")
        else:
            patterns["project_evolution"].append("Multi-technology Development")
    
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
    
    # File and code changes
    files_added = metrics.get('files_added', 0)
    files_modified = metrics.get('files_modified', 0)
    code_files = metrics.get('code_files_changed', 0)
    
    if code_files > 0:
        summary.append(f"Implemented changes across {code_files} code files, with {files_added} new files created and {files_modified} existing files enhanced")
    
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