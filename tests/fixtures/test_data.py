"""
Test fixtures and sample data for code analysis tests.
Updated to use new JSON structure with entities.
"""

from typing import Dict, List

# New structure design pattern files with entities
design_pattern_files: List[Dict] = [
    {
        "file_path": "src/factories/UserFactory.js",
        "language": "javascript",
        "lines_of_code": 120,
        "imports": ["react", "axios"],
        "dependencies_internal": ["./models/User", "./utils/helpers"],
        "entities": {
            "classes": [],
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
        "metrics": {"average_function_length": 21.5, "comment_ratio": 0.15}
    },
    {
        "file_path": "src/MainApp.java",
        "language": "java",
        "lines_of_code": 180,
        "imports": ["java.util", "java.io", "org.springframework"],
        "dependencies_internal": ["com.mycompany.app.services.DataService"],
        "entities": {
            "classes": [
                {
                    "name": "MainApp",
                    "methods": [
                        {
                            "name": "main",
                            "parameters": ["args"],
                            "lines_of_code": 15,
                            "calls": ["StringUtils", "System"]
                        },
                        {
                            "name": "singleton_getInstance",
                            "parameters": [],
                            "lines_of_code": 8,
                            "calls": ["createInstance", "getinstance"]
                        }
                    ]
                },
                {
                    "name": "ObserverPattern",
                    "methods": [
                        {
                            "name": "notify_subscribers",
                            "parameters": ["event"],
                            "lines_of_code": 22,
                            "calls": ["emit", "broadcast", "update"]
                        },
                        {
                            "name": "strategy_execute",
                            "parameters": ["algorithm"],
                            "lines_of_code": 28,
                            "calls": ["process", "handle", "execute"]
                        }
                    ]
                }
            ],
            "functions": [],
            "components": []
        },
        "metrics": {"average_function_length": 18.25, "comment_ratio": 0.05}
    },
    {
        "file_path": "src/user-card.component.ts", 
        "language": "typescript",
        "lines_of_code": 95,
        "imports": ["@angular/core", "@angular/common"],
        "dependencies_internal": ["./services/UserService"],
        "entities": {
            "classes": [
                {
                    "name": "UserCardComponent",
                    "methods": [
                        {
                            "name": "ngOnInit",
                            "parameters": [],
                            "lines_of_code": 3,
                            "calls": []
                        },
                        {
                            "name": "like",
                            "parameters": [],
                            "lines_of_code": 3,
                            "calls": ["emit"]
                        }
                    ]
                }
            ],
            "functions": [],
            "components": [
                {
                    "name": "UserCardComponent",
                    "props": ["userName", "initialLikes"],
                    "state_variables": ["likes"],
                    "hooks_used": ["ngOnInit"]
                }
            ]
        },
        "metrics": {"average_function_length": 3.0, "comment_ratio": 0.0}
    }
]

# Edge case test files - mixed old/new structures
edge_case_files: List[Dict] = [
    # Old structure (backward compatibility test)
    {
        "file_path": "legacy/old-structure.js",
        "language": "javascript",
        "lines_of_code": 50,
        "imports": ["react"],
        "functions": [  # Old structure - no entities wrapper
            {
                "name": "oldFunction",
                "parameters": ["param"],
                "calls": ["useState"],
                "lines_of_code": 10
            }
        ],
        "components": [  # Old structure - no entities wrapper
            {
                "name": "OldComponent",
                "props": ["data"],
                "state_variables": ["state"],
                "hooks_used": ["useEffect"]
            }
        ],
        "metrics": {"average_function_length": 10, "comment_ratio": 0.1}
    },
    # New structure with empty values (no nulls)
    {
        "file_path": "edge/empty-values.py",
        "language": "python", 
        "lines_of_code": 25,
        "imports": ["flask"],
        "dependencies_internal": [],
        "entities": {
            "classes": [
                {
                    "name": "ValidClass",
                    "methods": [
                        {
                            "name": "validMethod",
                            "parameters": ["self"],
                            "lines_of_code": 5,
                            "calls": ["print"]
                        }
                    ]
                }
            ],
            "functions": [],
            "components": []
        },
        "metrics": {"average_function_length": 5, "comment_ratio": 0}
    },
    # Empty entities structure
    {
        "file_path": "edge/empty-entities.go",
        "language": "go",
        "lines_of_code": 10,
        "imports": [],
        "dependencies_internal": [],
        "entities": {
            "classes": [],
            "functions": [],
            "components": []
        },
        "metrics": {"average_function_length": 0, "comment_ratio": 0}
    },
    # Missing entities field entirely
    {
        "file_path": "edge/missing-entities.cpp",
        "language": "cpp",
        "lines_of_code": 75,
        "imports": ["iostream", "vector"],
        "dependencies_internal": ["./headers/utils.h"],
        # No entities field at all
        "metrics": {"average_function_length": 12, "comment_ratio": 0.08}
    }
]

# Complex architectural patterns commits (keep existing)
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

# Multi-framework test data updated with new structure
multi_framework_files: List[Dict] = [
    {
        "file_path": "src/ReactComponent.jsx",
        "language": "javascript",
        "lines_of_code": 85,
        "imports": ["react", "@reduxjs/toolkit"],
        "dependencies_internal": ["./hooks/useAuth"],
        "entities": {
            "classes": [],
            "functions": [],
            "components": [
                {
                    "name": "ReactDashboard", 
                    "props": ["data", "theme"],
                    "state_variables": ["loading", "error"],
                    "hooks_used": ["useState", "useEffect", "useCallback"]
                }
            ]
        },
        "metrics": {"average_function_length": 0, "comment_ratio": 0.12}
    },
    {
        "file_path": "src/VueComponent.vue",
        "language": "javascript", 
        "lines_of_code": 70,
        "imports": ["vue", "vuex"],
        "dependencies_internal": ["./composables/useData"],
        "entities": {
            "classes": [],
            "functions": [],
            "components": [
                {
                    "name": "VueDashboard",
                    "props": ["data", "config"],
                    "state_variables": ["loading", "items"], 
                    "hooks_used": ["onMounted", "reactive", "computed"]
                }
            ]
        },
        "metrics": {"average_function_length": 0, "comment_ratio": 0.08}
    },
    {
        "file_path": "src/AngularComponent.ts",
        "language": "typescript",
        "lines_of_code": 90,
        "imports": ["@angular/core", "@angular/common"],
        "dependencies_internal": ["./services/DataService"],
        "entities": {
            "classes": [
                {
                    "name": "AngularDashboardComponent",
                    "methods": [
                        {
                            "name": "ngOnInit",
                            "parameters": [],
                            "lines_of_code": 5,
                            "calls": ["loadData"]
                        },
                        {
                            "name": "ngOnDestroy",
                            "parameters": [],
                            "lines_of_code": 3,
                            "calls": ["unsubscribe"]
                        }
                    ]
                }
            ],
            "functions": [],
            "components": [
                {
                    "name": "AngularDashboard",
                    "props": ["data", "options"],
                    "state_variables": ["loading", "results"],
                    "hooks_used": ["ngOnInit", "ngOnDestroy"]
                }
            ]
        },
        "metrics": {"average_function_length": 4, "comment_ratio": 0.15}
    }
]

# Performance test data - large dataset
performance_test_files: List[Dict] = []
for i in range(50):  # 50 files for performance testing
    performance_test_files.append({
        "file_path": f"performance/file_{i:03d}.py",
        "language": "python",
        "lines_of_code": 100 + (i * 5),
        "imports": ["flask", "sqlalchemy", f"custom_module_{i}"],
        "dependencies_internal": [f"./models/Model{i}", f"./services/Service{i}"],
        "entities": {
            "classes": [
                {
                    "name": f"Class{i}",
                    "methods": [
                        {
                            "name": f"method_{j}",
                            "parameters": ["self", "param"],
                            "lines_of_code": 10,
                            "calls": [f"helper_{j}", "validate"]
                        } for j in range(3)  # 3 methods per class
                    ]
                }
            ],
            "functions": [
                {
                    "name": f"function_{i}",
                    "parameters": ["data"],
                    "calls": ["process", "validate"],
                    "lines_of_code": 15
                }
            ],
            "components": []
        },
        "metrics": {"average_function_length": 12.5, "comment_ratio": 0.1}
    })

# Test files for role inference (simplified)
role_inference_test_files: List[Dict] = [
    {"file_path": "frontend/react/App.tsx", "imports": ["react", "typescript"]},
    {"file_path": "backend/django/models.py", "imports": ["django", "postgresql"]},
    {"file_path": "data/analysis.ipynb", "imports": ["pandas", "numpy", "sklearn"]},
    {"file_path": "devops/kubernetes/deployment.yml", "imports": ["docker"]},
    {"file_path": "mobile/flutter/main.dart", "imports": ["flutter"]},
]

# Complex parsed files updated to new structure
complex_parsed_files: List[Dict] = [
    {
        "file_path": "frontend/src/App.js",
        "language": "javascript",
        "lines_of_code": 256,
        "imports": ["react", "axios", "./components/Chart", "./utils/helpers", "redux", "react-router"],
        "dependencies_internal": ["./components/Chart", "./utils/helpers"],
        "entities": {
            "classes": [],
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
            ]
        },
        "metrics": {"average_function_length": 21.5, "comment_ratio": 0.12}
    },
    {
        "file_path": "backend/api/users.py",
        "language": "python", 
        "lines_of_code": 180,
        "imports": ["flask", "sqlalchemy", "jwt", "bcrypt"],
        "dependencies_internal": ["./models/User", "./utils/auth"],
        "entities": {
            "classes": [
                {
                    "name": "UserService",
                    "methods": [
                        {
                            "name": "create_user_observer",
                            "parameters": ["user_data", "notify_callback"],
                            "calls": ["validate_data", "save_to_db", "notify_subscribers"],
                            "lines_of_code": 30
                        }
                    ]
                }
            ],
            "functions": [],
            "components": []
        },
        "metrics": {"average_function_length": 30, "comment_ratio": 0.08}
    }
]