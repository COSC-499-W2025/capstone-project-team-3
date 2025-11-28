"""
Technical pattern definitions for code analysis.
Optimized for performance with set-based lookups.
"""

from typing import List, Set

class TechnicalPatterns:
    """Collection of optimized technical patterns for keyword extraction."""
    
    # Fast set-based lookup for GitHub commit keywords
    GITHUB_TECH_KEYWORDS: Set[str] = {
        # Development Actions
        'implement', 'implemented', 'add', 'added', 'create', 'created', 
        'build', 'built', 'develop', 'developed', 'design', 'designed', 
        'refactor', 'refactored', 'optimize', 'optimized', 'fix', 'fixed', 
        'update', 'updated', 'enhance', 'enhanced', 'improve', 'improved',
        'integrate', 'integrated', 'deploy', 'deployed', 'configure', 'configured',
        'setup', 'install', 'installed', 'remove', 'removed', 'delete', 'deleted',
        'migrate', 'migrated', 'upgrade', 'upgraded', 'downgrade', 'downgraded',
        
        # Architecture & Components  
        'api', 'apis', 'database', 'databases', 'frontend', 'backend', 
        'fullstack', 'full-stack', 'component', 'components', 'service', 'services',
        'module', 'modules', 'class', 'classes', 'function', 'functions',
        'method', 'methods', 'library', 'libraries', 'framework', 'frameworks',
        'middleware', 'plugin', 'plugins', 'extension', 'extensions', 
        'microservice', 'microservices', 'monolith',
        
        # Testing & Quality
        'test', 'testing', 'tests', 'unit', 'units', 'integration', 'e2e', 
        'end-to-end', 'automation', 'automated', 'spec', 'specs', 'mock', 'mocks',
        'stub', 'stubs', 'coverage', 'benchmark', 'benchmarks', 'performance',
        'profiling', 'debugging', 'debug', 'validation', 'validate', 'verification', 'verify',
        
        # DevOps & Infrastructure
        'docker', 'dockerfile', 'kubernetes', 'k8s', 'ci', 'cd', 'pipeline', 'pipelines',
        'jenkins', 'github', 'actions', 'workflow', 'workflows', 'deploy', 'deployment',
        'deployments', 'infrastructure', 'cloud', 'aws', 'azure', 'gcp', 'terraform',
        'ansible', 'vagrant', 'nginx', 'apache', 'load', 'balancer', 'scaling',
        'monitoring', 'logging', 'metrics',
        
        # Frontend Technologies
        'react', 'reactjs', 'vue', 'vuejs', 'angular', 'angularjs', 'svelte', 
        'next', 'nextjs', 'nuxt', 'nuxtjs', 'gatsby', 'html', 'css', 'scss', 'sass',
        'less', 'tailwind', 'bootstrap', 'jquery', 'typescript', 'javascript',
        'js', 'ts', 'jsx', 'tsx', 'webpack', 'vite', 'parcel', 'babel', 'eslint', 'prettier',
        
        # Backend Technologies
        'node', 'nodejs', 'express', 'expressjs', 'django', 'flask', 'fastapi',
        'spring', 'springboot', 'laravel', 'rails', 'ruby', 'python', 'java',
        'php', 'golang', 'go', 'rust', 'kotlin', 'scala', 'dotnet', 'csharp', 'nestjs', 'koa',
        
        # Databases & Storage
        'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'mongo', 'redis',
        'elasticsearch', 'elastic', 'cassandra', 'dynamodb', 'firebase', 'firestore',
        'orm', 'sql', 'nosql', 'migration', 'migrations', 'schema', 'schemas',
        'index', 'indexes', 'query', 'queries', 'transaction', 'transactions',
        
        # Mobile & Desktop
        'android', 'ios', 'swift', 'kotlin', 'flutter', 'dart', 'react-native',
        'reactnative', 'xamarin', 'ionic', 'cordova', 'phonegap', 'electron',
        'tauri', 'pwa', 'mobile', 'native', 'cross-platform',
        
        # Data & Analytics
        'data', 'analytics', 'ml', 'ai', 'machine', 'learning', 'deep', 'neural',
        'network', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'sklearn', 'jupyter',
        'notebook', 'visualization', 'dashboard', 'etl', 'pipeline', 'bigdata',
        'spark', 'hadoop', 'kafka', 'stream', 'streaming',
        
        # Security & Authentication
        'auth', 'authentication', 'authorization', 'oauth', 'jwt', 'token', 'tokens',
        'security', 'secure', 'encryption', 'decrypt', 'encrypt', 'ssl', 'tls',
        'https', 'cors', 'csrf', 'xss', 'hash', 'hashing', 'bcrypt', 'session',
        'sessions', 'login', 'logout', 'signup', 'password', 'permissions', 'role', 'roles',
        
        # Communication & Protocols
        'rest', 'restful', 'graphql', 'grpc', 'websocket', 'websockets', 'mqtt',
        'http', 'https', 'api', 'soap', 'json', 'xml', 'yaml', 'protobuf',
        'messaging', 'queue', 'queues', 'pub', 'sub', 'pubsub', 'webhook', 'webhooks',
        
        # Version Control & Collaboration
        'git', 'github', 'gitlab', 'bitbucket', 'commit', 'commits', 'branch', 'branches',
        'merge', 'merges', 'pull', 'request', 'requests', 'pr', 'fork', 'clone',
        'push', 'rebase', 'cherry-pick', 'tag', 'tags', 'release', 'releases', 'version', 'versioning',
        
        # Project Management & Methodologies
        'agile', 'scrum', 'kanban', 'sprint', 'sprints', 'story', 'stories',
        'epic', 'epics', 'bug', 'bugs', 'issue', 'issues', 'feature', 'features',
        'requirement', 'requirements', 'specification', 'specifications',
        'documentation', 'docs', 'readme', 'changelog', 'license'
    }
    
    # Rest of your existing patterns stay the same...
    FRAMEWORK_MAPPING = {
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
    
    # Common terms to filter out
    COMMON_TERMS = {
        "function", "component", "state", "props", "data", "user", "name", 
        "get", "set", "add", "remove", "update", "delete", "create", "main"
    }
    
    # File extension mappings for role inference
    ROLE_EXTENSIONS = {
        'frontend': {".js", ".jsx", ".ts", ".tsx", ".css", ".html"},
        'backend': {".py", ".java", ".rb", ".go", ".cpp", ".c"},
        'database': {".sql", ".db", ".json"},
        'devops': {".yml", ".yaml", ".sh"},
        'datascience': {".ipynb", ".csv", ".pkl"}
    }
    
    CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp", ".cc",
                 ".cs", ".go", ".rb", ".rs", ".kt", ".kts", ".swift", ".scala", ".php", ".m", ".mm",
                 ".sh", ".ps1", ".pl", ".lua", ".r", ".jl", ".sql", ".dart", ".groovy", ".hs", ".erl",
                 ".ex", ".exs", ".clj", ".cljs", ".coffee", ".asm", ".s", ".vb", ".vbs", ".v", ".sv", 
                 ".vhdl", ".zig", ".nim", ".gd", ".proto", ".graphql", ".vue", ".scss", ".less", ".css",
                 ".qml", ".cmake", ".gradle", ".make"
                 }
    DOC_EXTS = {".md"}
    TEST_EXTS = {"test_", "_test.py", ".test.py", ".test.js", ".test.ts", ".test.jsx", ".test.tsx",
                 ".spec.py", ".spec.js", ".spec.ts", ".spec.jsx", ".spec.tsx"}