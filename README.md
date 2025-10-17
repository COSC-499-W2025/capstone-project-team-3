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

### Running Tests in Docker Environment
To run all the python tests in the docker environment, run `docker compose exec server pytest`.

You might need to run this in a new terminal window after running `docker compose up --build`.

### How to Check Your Test Coverage

Test coverage shows how much of your code is actually tested by your unit tests. It helps you find parts of the code that **aren't tested yet**, so you can improve your tests and catch potential bugs.

To generate a test coverage report, run this command:

```
docker compose exec server pytest --cov=app --cov-report=html:/app/htmlcov
```

This will run your tests and create a detailed **HTML report** inside the `/app/htmlcov` folder.

To view the coverage report:

1. Open the `htmlcov/index.html` file in a web browser.
2. You’ll see a visual overview showing which lines of code are tested (highlighted in green) and which are not (highlighted in red).

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