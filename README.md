[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20539381&assignment_repo_type=AssignmentRepo)

# Project details

 - [Data Flow Diagram and Explanation](docs/plan/DFD.md)
 - [Work Breakdown Structure](docs/plan/Work%20Breakdown%20Structure.md)
 - [System Architecture](docs/plan/System_Architecture_Diagram.md)

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

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8000.

Quick helper script:
- `scripts/setup.sh` builds and runs the app. Options:
  - `USE_COMPOSE=1 ./scripts/setup.sh` to use docker compose
  - `PLATFORM=linux/amd64 ./scripts/setup.sh` to force platform

**Note:**
- **Make sure you have the docker daemon running in the background i.e. open the Docker app installed on your machine**
- **Make sure `requirements.txt` exists (Dockerfile installs from it).**
- **Keep Dockerfile and compose files tracked in git; use `.dockerignore` to exclude files from the build context.**

In the terminal, run the following command to stop the application: `docker compose down`.

### Database Setup and Usage with Docker

The project includes a basic SQL database initialization process that runs automatically when the application starts in Docker. This setup ensures that your database tables and schemas are created without manual intervention.

How It Works:

  The database initialization is handled by init_db() function inside app/data/db.py.

  When you run the application (`docker compose up --build`), the FastAPI server triggers this initialization to create the required tables.

  All SQL scripts and schema definitions should be stored inside the app/data/ directory to maintain consistency.

Local Development
  First time use : 
  From the project root (where compose.yaml lives):
    `docker compose up --build`

  If everything is correct, you should see these logs in the terminal:
   ` Database initialized at: /app/app/data/app.sqlite3`
    `App started`
    `INFO:     Uvicorn running on http://0.0.0.0:8000`
  
  If you modify your database schema or add new tables:

    Stop your running container: 
  `docker compose down`

    Rebuild the container to apply changes: 
  `docker compose up --build`

The new schema will be automatically applied on startup.

Accessing the Database

  By default, the database file (e.g., app.db) is created in the /app directory inside the container.
  You can access it locally using:
  `docker compose exec server bash`
  `sqlite3 app/app.db`

Run SQL commands directly within the container to inspect or test data.

### Running Tests in Docker Environment
To run all the python tests in the docker environment, run `docker compose exec server pytest`.

You might need to run this in a new terminal window after running `docker compose up --build`.

### Deploying your application to the cloud

Build & run (single-image):
- Build: `docker build -t myapp .`
- Run: `docker run -p 8000:8000 --env-file .env myapp`

If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)