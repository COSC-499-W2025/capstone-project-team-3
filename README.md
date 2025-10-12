[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20539381&assignment_repo_type=AssignmentRepo)

#Project details

- Project Proposal
 - [Data Flow Diagram and Explanation](docs/DFD%20Level1.md)
 - [System Architecture Diagram and Explanation](docs/plan/System_Architecture_Diagram.md)
# Project-Starter
Please use the provided folder structure for your project. You are free to organize any additional internal folder structure as required by the project. 

```
.
├── docs                    # Documentation files
│   ├── contract            # Team contract
│   ├── proposal            # Project proposal 
│   ├── design              # UI mocks
│   ├── minutes             # Minutes from team meetings
│   ├── logs                # Team and individual Logs
│   └── ...          
├── src                     # Source files (alternatively `app`)
├── tests                   # Automated tests 
├── utils                   # Utility files
└── README.md
```

Please use a branching workflow, and once an item is ready, do remember to issue a PR, review, and merge it into the master branch.
Be sure to keep your docs and README.md up-to-date.

### Building and running with Docker

Prereqs: Docker Desktop (or Docker Engine + docker-compose).

Build & run (single-image):
- Build: `docker build -t capstone-app .`
- Run: `docker run -p 8000:8000 --env-file .env capstone-app`

If you're on Apple Silicon (M1/M2) and the target is amd64:
- `docker build --platform=linux/amd64 -t capstone-app .`

Using docker compose:
- `docker compose up --build`
- App will be available at http://localhost:8000

Quick helper script:
- `scripts/setup.sh` builds and runs the app. Options:
  - `USE_COMPOSE=1 ./scripts/setup.sh` to use docker compose
  - `PLATFORM=linux/amd64 ./scripts/setup.sh` to force platform

Notes:
- Make sure `requirements.txt` exists (Dockerfile installs from it).
- Keep Dockerfile and compose files tracked in git; use `.dockerignore` to exclude files from the build context.
