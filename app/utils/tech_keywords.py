"""
Curated set of meaningful tech-domain keywords used as a baseline vocabulary
for ATS scoring. Supplements Gemini-extracted JD keywords.
"""

TECH_KEYWORDS: set = {
    # Languages
    "python", "java", "javascript", "typescript", "golang", "go", "rust",
    "scala", "kotlin", "swift", "ruby", "php", "perl", "haskell", "elixir",
    "clojure", "groovy", "matlab", "r", "dart", "lua", "bash", "shell",
    "powershell", "c", "c++", "c#", "objective-c", "assembly",

    # Web fundamentals
    "html", "css", "scss", "sass", "less", "jsx", "tsx", "xml", "json", "yaml",

    # JavaScript / Node ecosystem
    "node", "nodejs", "npm", "yarn", "pnpm", "deno", "bun",
    "webpack", "vite", "esbuild", "parcel", "rollup", "turbopack",
    "babel", "eslint", "prettier",

    # Web frameworks & libraries
    "react", "angular", "vue", "svelte", "nextjs", "nuxtjs", "gatsby",
    "express", "fastapi", "django", "flask", "rails", "spring", "springboot",
    "laravel", "symfony", "nestjs", "fastify", "hapi", "koa", "asp.net",
    "blazor", "htmx", "tailwind", "bootstrap", "material-ui", "chakra",

    # Backend / APIs
    "rest", "restful", "graphql", "grpc", "websocket", "openapi", "swagger",
    "oauth", "jwt", "saml", "oidc", "api", "microservices", "serverless",
    "event-driven", "message-queue",

    # Cloud & infrastructure
    "aws", "gcp", "azure", "cloudflare", "vercel", "netlify", "heroku",
    "digitalocean", "lambda", "ec2", "s3", "rds", "dynamodb", "cloudwatch",
    "iam", "vpc", "eks", "ecs", "fargate", "bigquery", "pubsub",
    "cloud-run", "app-engine", "azure-functions", "blob-storage",

    # DevOps / CI-CD
    "docker", "kubernetes", "helm", "terraform", "ansible", "puppet",
    "chef", "jenkins", "github-actions", "gitlab-ci", "circleci", "argocd",
    "spinnaker", "packer", "vagrant", "prometheus", "grafana", "datadog",
    "newrelic", "splunk", "elk", "logstash", "kibana", "istio", "envoy",
    "nginx", "apache", "haproxy", "traefik", "devops", "sre", "devsecops",
    "ci/cd", "cicd", "infrastructure", "observability",

    # Databases
    "sql", "postgresql", "mysql", "sqlite", "mariadb", "mssql", "oracle",
    "mongodb", "cassandra", "redis", "memcached", "elasticsearch",
    "opensearch", "neo4j", "influxdb", "cockroachdb", "planetscale",
    "supabase", "firebase", "couchdb", "hbase", "dynamodb",

    # Data / streaming
    "kafka", "rabbitmq", "sqs", "pubsub", "kinesis", "flink", "spark",
    "hadoop", "hive", "airflow", "dbt", "prefect", "dagster", "luigi",
    "dask", "pandas", "numpy", "polars", "arrow",

    # ML / AI
    "machine-learning", "deep-learning", "nlp", "llm", "generative-ai",
    "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost", "lightgbm",
    "huggingface", "langchain", "openai", "gemini", "bert", "gpt",
    "transformer", "diffusion", "rag", "embedding", "vector-database",
    "faiss", "pinecone", "weaviate", "mlflow", "kubeflow", "sagemaker",
    "computer-vision", "object-detection", "reinforcement-learning",

    # Mobile
    "ios", "android", "react-native", "flutter", "expo", "xcode",
    "android-studio", "swiftui", "jetpack-compose",

    # Testing
    "unit-testing", "integration-testing", "e2e", "pytest", "jest",
    "mocha", "chai", "cypress", "playwright", "selenium", "testng",
    "junit", "mockito", "storybook", "tdd", "bdd",

    # Security
    "cybersecurity", "penetration-testing", "owasp", "soc2", "gdpr",
    "encryption", "cryptography", "ssl", "tls", "zero-trust",
    "identity", "access-management", "devsecops",

    # Architecture / patterns
    "system-design", "distributed-systems", "high-availability",
    "fault-tolerance", "scalability", "load-balancing", "caching",
    "sharding", "replication", "eventual-consistency", "cap-theorem",
    "design-patterns", "solid", "clean-architecture", "hexagonal",
    "domain-driven", "event-sourcing", "cqrs", "saga",

    # Methodologies
    "agile", "scrum", "kanban", "lean", "xp", "safe", "sprint",
    "retrospective", "standup",

    # Version control & collaboration
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "linear", "notion",

    # Years / seniority indicators (token-level)
    "senior", "lead", "principal", "staff", "architect", "manager",
}
