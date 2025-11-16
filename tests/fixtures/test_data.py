"""
Test fixtures and sample data for code analysis tests.
Separated from main test logic for better maintainability.
"""

from typing import Dict, List

# Complex sample for testing all new design patterns
design_pattern_files: List[Dict] = [
    {
        "file_path": "src/factories/UserFactory.js",
        "language": "javascript",
        "lines_of_code": 120,
        "imports": ["react", "axios"],
        "functions": [
            {
                "name": "createUserFactory",
                "parameters": ["config"],
                "calls": ["buildUser", "createInstance", "makeUser"],
                "lines_of_code": 25
            },
            {
                "name": "buildUser",
                "parameters": ["data"],
                "calls": ["construct", "newUser"],
                "lines_of_code": 18
            }
        ],
        "components": [
            {
                "name": "UserObserver",
                "props": ["observable"],
                "state_variables": ["subscribers"],
                "hooks_used": ["useState", "useEffect"]
            }
        ]
    },
    {
        "file_path": "src/patterns/Observer.py",
        "language": "python",
        "lines_of_code": 200,
        "imports": ["flask", "sqlalchemy"],
        "functions": [
            {
                "name": "observer_pattern",
                "parameters": ["subject"],
                "calls": ["subscribe", "notify", "emit"],
                "lines_of_code": 30
            },
            {
                "name": "notify_subscribers",
                "parameters": ["event"],
                "calls": ["emit", "broadcast", "update"],
                "lines_of_code": 22
            },
            {
                "name": "strategy_execute",
                "parameters": ["algorithm"],
                "calls": ["process", "handle", "execute"],
                "lines_of_code": 28
            },
            {
                "name": "singleton_getInstance",
                "parameters": [],
                "calls": ["createInstance", "getinstance"],
                "lines_of_code": 15
            }
        ],
        "components": []
    },
    {
        "file_path": "src/architecture/UserController.java",
        "language": "java",
        "lines_of_code": 180,
        "imports": ["spring", "hibernate"],
        "functions": [
            {
                "name": "getUserModel",
                "parameters": ["id"],
                "calls": ["repository.find", "validateModel"],
                "lines_of_code": 20
            },
            {
                "name": "userServiceLayer",
                "parameters": ["request"],
                "calls": ["businessLayer", "dataLayer"],
                "lines_of_code": 35
            }
        ],
        "components": [
            {
                "name": "UserViewController",
                "props": ["model", "presenter"],
                "state_variables": ["viewModel"],
                "hooks_used": []
            }
        ]
    },
    {
        "file_path": "src/microservices/ApiGateway.go",
        "language": "go", 
        "lines_of_code": 150,
        "imports": ["gin", "kubernetes"],
        "functions": [
            {
                "name": "microservice_handler",
                "parameters": ["request"],
                "calls": ["apiGateway", "serviceRegistry"],
                "lines_of_code": 25
            },
            {
                "name": "rest_endpoint",
                "parameters": ["path"],
                "calls": ["get", "post", "put", "delete"],
                "lines_of_code": 40
            },
            {
                "name": "event_handler",
                "parameters": ["event"],
                "calls": ["messageQueue", "pubsub", "kafka"],
                "lines_of_code": 30
            }
        ],
        "components": []
    }
]

# Complex architectural patterns commits
architectural_commits: List[Dict] = [
    {
        "hash": "arch001",
        "author_name": "Software Architect",
        "author_email": "arch@example.com",
        "authored_datetime": "2025-10-15T10:00:00",
        "committed_datetime": "2025-10-15T10:02:00",
        "message_summary": "implement microservices architecture with API gateway",
        "message_full": "implement microservices architecture with API gateway\n\nAdded service discovery and circuit breaker patterns",
        "is_merge": False,
        "files": [
            {"status": "A", "path_after": "services/user-service/main.py"},
            {"status": "A", "path_after": "services/auth-service/auth.py"},
            {"status": "A", "path_after": "gateway/api-gateway.js"},
            {"status": "A", "path_after": "config/kubernetes/deployment.yml"}
        ]
    },
    {
        "hash": "arch002", 
        "author_name": "Backend Developer",
        "authored_datetime": "2025-10-16T14:30:00",
        "message_summary": "refactor: implement repository pattern with layered architecture",
        "message_full": "refactor: implement repository pattern with layered architecture\n\nAdded data access layer and business logic separation",
        "files": [
            {"status": "A", "path_after": "repositories/UserRepository.java"},
            {"status": "A", "path_after": "services/UserService.java"},
            {"status": "A", "path_after": "controllers/UserController.java"},
            {"status": "M", "path_after": "models/User.java"}
        ]
    },
    {
        "hash": "arch003",
        "author_name": "Frontend Architect", 
        "authored_datetime": "2025-10-17T09:15:00",
        "message_summary": "feat: implement MVVM pattern with React and Redux",
        "message_full": "feat: implement MVVM pattern with React and Redux\n\nAdded ViewModels and state management",
        "files": [
            {"status": "A", "path_after": "viewmodels/UserViewModel.js"},
            {"status": "A", "path_after": "views/UserView.jsx"},
            {"status": "A", "path_after": "models/UserModel.js"},
            {"status": "M", "path_after": "store/userStore.js"}
        ]
    },
    {
        "hash": "arch004",
        "author_name": "DevOps Engineer",
        "authored_datetime": "2025-10-18T16:45:00", 
        "message_summary": "deploy: setup event-driven architecture with message queues",
        "message_full": "deploy: setup event-driven architecture with message queues\n\nAdded Kafka for pub/sub messaging and event streaming",
        "files": [
            {"status": "A", "path_after": "events/UserEventHandler.py"},
            {"status": "A", "path_after": "messaging/MessageQueue.js"},
            {"status": "A", "path_after": "config/kafka/producer.yml"},
            {"status": "A", "path_after": "streams/UserEventStream.java"}
        ]
    }
]

# Original samples for compatibility
complex_parsed_files: List[Dict] = [
    {
        "file_path": "frontend/src/App.js",
        "language": "javascript",
        "lines_of_code": 256,
        "imports": ["react", "axios", "./components/Chart", "./utils/helpers", "redux", "react-router"],
        "functions": [
            {
                "name": "fetchUserData",
                "parameters": ["userId", "options"],
                "calls": ["axios.get", "validateUser", "parseResponse"],
                "lines_of_code": 18
            },
            {
                "name": "createUserFactory",
                "parameters": ["config"],
                "calls": ["buildUser", "setDefaults"],
                "lines_of_code": 25
            }
        ],
        "components": [
            {
                "name": "Dashboard",
                "props": ["user", "data", "onUpdate"],
                "state_variables": ["loading", "chartData", "error"],
                "hooks_used": ["useState", "useEffect", "useCallback"]
            }
        ],
        "metrics": {"average_function_length": 21.5, "comment_ratio": 0.12}
    },
    {
        "file_path": "backend/api/users.py",
        "language": "python", 
        "lines_of_code": 180,
        "imports": ["flask", "sqlalchemy", "jwt", "bcrypt"],
        "functions": [
            {
                "name": "create_user_observer",
                "parameters": ["user_data", "notify_callback"],
                "calls": ["validate_data", "save_to_db", "notify_subscribers"],
                "lines_of_code": 30
            }
        ],
        "components": [],
        "metrics": {"average_function_length": 30, "comment_ratio": 0.08}
    }
]

# Multi-framework test data for framework-agnostic testing
multi_framework_files: List[Dict] = [
    {
        "file_path": "src/ReactComponent.jsx",
        "language": "javascript",
        "imports": ["react"],
        "functions": [],
        "components": [
            {
                "name": "ReactDashboard", 
                "props": ["data"],
                "state_variables": ["loading"],
                "hooks_used": ["useState", "useEffect"]
            }
        ]
    },
    {
        "file_path": "src/VueComponent.vue",
        "language": "javascript", 
        "imports": ["vue"],
        "functions": [],
        "components": [
            {
                "name": "VueDashboard",
                "props": ["data"],
                "state_variables": ["loading"], 
                "hooks_used": ["onMounted", "reactive"]
            }
        ]
    },
    {
        "file_path": "src/AngularComponent.ts",
        "language": "typescript",
        "imports": ["angular"],
        "functions": [],
        "components": [
            {
                "name": "AngularDashboard",
                "props": ["data"],
                "state_variables": ["loading"],
                "hooks_used": ["ngOnInit", "ngOnDestroy"]
            }
        ]
    }
]

# Test files for role inference
role_inference_test_files: List[Dict] = [
    {"file_path": "frontend/react/App.tsx", "imports": ["react", "typescript"]},
    {"file_path": "backend/django/models.py", "imports": ["django", "postgresql"]},
    {"file_path": "data/analysis.ipynb", "imports": ["pandas", "numpy", "sklearn"]},
    {"file_path": "devops/kubernetes/deployment.yml", "imports": ["docker"]},
    {"file_path": "mobile/flutter/main.dart", "imports": ["flutter"]},
]