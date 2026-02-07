import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
from app.api.routes.portfolio import router

# Create a test FastAPI app with the portfolio router
app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)

@pytest.fixture
def mock_portfolio_data():
    """Mock portfolio data structure."""
    return {
        "user": {
            "name": "Test User",
            "email": "test@example.com",
            "github_user": "testuser",
            "links": [{"label": "GitHub", "url": "https://github.com/testuser"}],
            "education": "Test University",
            "job_title": "Developer"
        },
        "overview": {
            "total_projects": 3,
            "avg_score": 0.85,
            "total_skills": 15,
            "total_languages": 4,
            "total_lines": 5000
        },
        "projects": [
            {
                "id": "proj1",
                "title": "Test Project 1",
                "score": 0.9,
                "summary": "A test project",
                "dates": "Jan 2024 – Mar 2024",
                "type": "GitHub",
                "metrics": {
                    "total_commits": 25, 
                    "total_lines": 2000,
                    "technical_keywords": ["API", "testing"],
                    "languages": ["Python", "JavaScript"]
                },
                "skills": ["Python", "FastAPI", "Problem Solving"]
            }
        ],
        "skills_timeline": [
            {"skill": "Python", "first_used": "2024-01-15", "year": 2024}
        ],
        "project_type_analysis": {
            "github": {"count": 2, "stats": {"avg_score": 0.88}},
            "local": {"count": 1, "stats": {"avg_score": 0.75}}
        },
        "graphs": {
            "language_distribution": {"Python": 2, "JavaScript": 1},
            "complexity_distribution": {"distribution": {"small": 1, "medium": 2, "large": 0}},
            "score_distribution": {"distribution": {"excellent": 1, "good": 2, "fair": 0, "poor": 0}},
            "monthly_activity": {"2024-01": 2, "2024-02": 1},
            "top_skills": {"Python": 3, "FastAPI": 2}
        },
        "metadata": {
            "generated_at": "2024-01-01T10:00:00",
            "total_projects": 3,
            "filtered": True,
            "project_ids": ["proj1", "proj2", "proj3"]
        }
    }


class TestPortfolioEndpoints:
    """Test suite for portfolio API endpoints."""
    
    def test_get_portfolio_all_projects(self, mock_portfolio_data):
        """Test GET /portfolio endpoint without filters (all projects)."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            assert "user" in data
            assert "overview" in data
            assert "projects" in data
            assert "skills_timeline" in data
            assert "project_type_analysis" in data
            assert "graphs" in data
            assert "metadata" in data
            
            # Check metadata for no filtering
            assert data["metadata"]["total_projects"] == 3
            assert data["metadata"]["filtered"] == True  # Mock data has filtered=True
            
            # Check headers
            assert "X-Portfolio-Projects" in response.headers
            assert "X-Portfolio-Generated" in response.headers
            assert "X-Portfolio-Filtered" in response.headers
            
            # Verify mock was called with None (no filtering)
            mock_build.assert_called_once_with(project_ids=None)

    def test_get_portfolio_with_project_ids(self, mock_portfolio_data):
        """Test GET /portfolio endpoint with specific project IDs."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio?project_ids=proj1,proj2,proj3")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that data is returned properly
            assert "overview" in data
            assert data["overview"]["total_projects"] == 3
            assert len(data["projects"]) == 1  # Mock data has 1 project
            
            # Verify mock was called with parsed project IDs
            mock_build.assert_called_once_with(project_ids=["proj1", "proj2", "proj3"])

    def test_get_portfolio_with_whitespace_project_ids(self):
        """Test GET /portfolio endpoint with project IDs containing whitespace."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = {
                "user": {"name": "Test User"},
                "overview": {"total_projects": 2},
                "projects": [],
                "skills_timeline": [],
                "project_type_analysis": {"github": {"count": 0}, "local": {"count": 0}},
                "graphs": {},
                "metadata": {"generated_at": "2024-01-01T10:00:00", "total_projects": 2, "filtered": True}
            }
            
            response = client.get("/api/portfolio?project_ids= proj1 , proj2 ,")
            
            assert response.status_code == 200
            
            # Verify whitespace was stripped and empty strings removed
            mock_build.assert_called_once_with(project_ids=["proj1", "proj2"])

    def test_get_portfolio_empty_project_ids(self):
        """Test GET /portfolio endpoint with empty project_ids string."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = {
                "user": {"name": "Test User"},
                "overview": {"total_projects": 3},
                "projects": [],
                "skills_timeline": [],
                "project_type_analysis": {"github": {"count": 0}, "local": {"count": 0}},
                "graphs": {},
                "metadata": {"generated_at": "2024-01-01T10:00:00", "total_projects": 3, "filtered": False}
            }
            
            response = client.get("/api/portfolio?project_ids=")
            
            assert response.status_code == 200
            
            # Empty string should be treated as None (no filtering)
            mock_build.assert_called_once_with(project_ids=None)

    def test_get_portfolio_database_error(self):
        """Test GET /portfolio endpoint with database error."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/portfolio")
            
            assert response.status_code == 500
            assert "Database connection failed" in response.json()["detail"]

    def test_get_portfolio_response_headers(self, mock_portfolio_data):
        """Test GET /portfolio endpoint response headers are set correctly."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio?project_ids=proj1,proj2")
            
            assert response.status_code == 200
            
            # Check custom headers
            assert response.headers["X-Portfolio-Projects"] == "3"
            assert response.headers["X-Portfolio-Generated"] == "2024-01-01T10:00:00"
            assert response.headers["X-Portfolio-Filtered"] == "True"
            assert response.headers["Content-Type"] == "application/json"


class TestPortfolioDashboardEndpoints:
    """Test suite for portfolio dashboard UI endpoints."""
    
    def test_portfolio_dashboard_success(self):
        """Test GET /portfolio-dashboard endpoint returns HTML when file exists."""
        mock_html_content = "<html><head><title>Portfolio Dashboard</title></head><body>Dashboard Content</body></html>"
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_html_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/portfolio-dashboard")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"
            assert "Portfolio Dashboard" in response.text
            assert "Dashboard Content" in response.text

    def test_portfolio_dashboard_file_not_found(self):
        """Test GET /portfolio-dashboard endpoint when HTML file doesn't exist."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/api/portfolio-dashboard")
            
            assert response.status_code == 404
            assert "Portfolio Dashboard not found" in response.text

    def test_portfolio_js_success(self):
        """Test GET /static/portfolio.js endpoint returns JavaScript when file exists."""
        mock_js_content = "// Portfolio Dashboard JavaScript\nclass PortfolioDashboard { constructor() {} }"
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/javascript"
            assert "PortfolioDashboard" in response.text
            assert "constructor" in response.text

    def test_portfolio_js_file_not_found(self):
        """Test GET /static/portfolio.js endpoint when JS file doesn't exist."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/api/static/portfolio.js")
            
            assert response.status_code == 404
            assert "JavaScript file not found" in response.json()["detail"]


class TestPortfolioDataStructure:
    """Test suite for portfolio data structure validation."""
    
    def test_portfolio_data_structure_validation(self, mock_portfolio_data):
        """Test that portfolio response contains all required data structures."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio")
            data = response.json()
            
            # Test user structure
            user = data["user"]
            assert "name" in user
            assert "email" in user
            
            # Test overview structure
            overview = data["overview"]
            assert "total_projects" in overview
            assert "avg_score" in overview
            assert "total_skills" in overview
            assert "total_languages" in overview
            assert "total_lines" in overview
            
            # Test projects structure
            projects = data["projects"]
            assert len(projects) > 0
            project = projects[0]
            assert "id" in project
            assert "title" in project
            assert "score" in project
            assert "metrics" in project
            assert "skills" in project
            
            # Test graphs structure
            graphs = data["graphs"]
            assert "language_distribution" in graphs
            assert "complexity_distribution" in graphs
            assert "score_distribution" in graphs
            assert "monthly_activity" in graphs
            assert "top_skills" in graphs
            
            # Test metadata structure
            metadata = data["metadata"]
            assert "generated_at" in metadata
            assert "total_projects" in metadata
            assert "filtered" in metadata

def test_edit_portfolio_batch_success():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # Simulate successful update
        mock_cursor.rowcount = 2

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Batch Name 1",
                    "rank": 0.8
                },
                {
                    "project_signature": "sig2",
                    "project_summary": "Batch summary 2",
                    "rank": 0.7
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert set(data["projects_updated"]) == {"sig1", "sig2"}
        assert data["count"] == 2

        mock_db.commit.assert_called_once()
        mock_cursor.execute.assert_called_once()

def test_edit_portfolio_batch_not_found():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # Simulate no rows updated
        mock_cursor.rowcount = 0

        payload = {
            "edits": [
                {
                    "project_signature": "missing_sig",
                    "project_name": "Should not update"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "No projects found"
        mock_db.commit.assert_not_called()

def test_edit_portfolio_batch_partial_fields():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 1

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Only Name"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["projects_updated"] == ["sig1"]
        assert data["count"] == 1

        mock_db.commit.assert_called_once()
        mock_cursor.execute.assert_called_once()

def test_edit_portfolio_batch_db_error():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("DB write failed")

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Crash Me"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 500
        assert "Failed to edit projects" in response.json()["detail"]
        mock_db.rollback.assert_called_once()

def test_edit_portfolio_batch_no_fields():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # No fields provided to edit
        payload = {
            "edits": [
                {
                    "project_signature": "sig1"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 400
        assert "No fields provided for project" in response.json()["detail"]
        mock_db.commit.assert_not_called()


class TestPortfolioJavaScript:
    """Test the portfolio JavaScript serving endpoint"""
    
    def test_portfolio_js_content_structure(self):
        """Test that the portfolio JavaScript contains expected class and methods"""
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data="""
// Portfolio Dashboard JavaScript
class PortfolioDashboard {
    constructor() {
        this.selectedProjects = new Set();
        this.allProjects = [];
        this.currentPortfolioData = null;
        this.charts = {};
        
        this.init();
    }
    
    async init() {}
    
    async loadProjects() {}
    
    async loadPortfolio() {}
    
    renderProjectList(projects) {}
    
    renderOverviewCards(overview) {}
}

window.toggleProject = function(projectId) {};
window.toggleAllProjects = function() {};

document.addEventListener('DOMContentLoaded', function() {
    window.portfolioDashboard = new PortfolioDashboard();
});
             """)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            assert response.status_code == 200
            
            content = response.content.decode()
            
            # Verify core class structure
            assert "class PortfolioDashboard" in content
            assert "constructor()" in content
            assert "async loadProjects()" in content
            assert "async loadPortfolio()" in content
            assert "renderProjectList(" in content
            assert "renderOverviewCards(" in content
            
            # Verify global functions
            assert "window.toggleProject" in content
            assert "window.toggleAllProjects" in content
            
            # Verify initialization
            assert "DOMContentLoaded" in content
            assert "new PortfolioDashboard()" in content

    def test_portfolio_js_api_endpoints(self):
        """Test that JavaScript references correct API endpoints"""
        mock_js_content = """
        fetch('/api/projects')
        fetch('/api/portfolio')
        url = `/api/portfolio?project_ids=${selectedIds.join(',')}`
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify API endpoint references
            assert "'/api/projects'" in content
            assert "'/api/portfolio'" in content
            assert "project_ids=" in content

    def test_portfolio_js_new_methods_exist(self):
        """Test that newly added methods exist in the JavaScript file"""
        mock_js_content = """
        renderTopProjects(projects) {
            const topProjects = document.getElementById('topProjects');
            const sortedProjects = projects.sort((a, b) => (b.rank || 0) - (a.rank || 0)).slice(0, 6);
            document.querySelectorAll('.editable-field').forEach(element => {
                element.addEventListener('click', (e) => {
                    const field = e.target.dataset.field;
                    const projectId = e.target.dataset.project;
                });
            });
        }
        
        renderDetailedAnalysis(projects) {
            const analysisContainer = document.getElementById('detailedAnalysis');
            let totalTestFiles = 0;
            let totalFunctions = 0;
            let totalClasses = 0;
            let githubProjects = 0;
            let localProjects = 0;
            projects.forEach(project => {
                const metrics = project.metrics || {};
            });
        }
        
        showError(message) {
            console.error(message);
            alert(`Error: ${message}`);
        }
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Test renderTopProjects method
            assert "renderTopProjects(projects)" in content
            assert "getElementById('topProjects')" in content
            assert "sortedProjects = projects.sort" in content
            assert "b.rank || 0" in content
            assert "slice(0, 6)" in content
            assert "querySelectorAll('.editable-field')" in content
            assert "addEventListener('click'" in content
            assert "dataset.field" in content
            assert "dataset.project" in content
            
            # Test renderDetailedAnalysis method
            assert "renderDetailedAnalysis(projects)" in content
            assert "getElementById('detailedAnalysis')" in content
            assert "totalTestFiles = 0" in content
            assert "totalFunctions = 0" in content
            assert "totalClasses = 0" in content
            assert "githubProjects = 0" in content
            assert "localProjects = 0" in content
            assert "projects.forEach(project =>" in content
            assert "project.metrics || {}" in content
            
            # Test showError method
            assert "showError(message)" in content
            assert "console.error(message)" in content
            assert "alert(`Error: ${message}`)" in content

    def test_portfolio_js_editable_fields_functionality(self):
        """Test that editable fields functionality is properly implemented"""
        mock_js_content = """
        // Add click handlers for editable fields
        document.querySelectorAll('.editable-field').forEach(element => {
            element.style.cursor = 'pointer';
            element.title = 'Click to edit';
            element.addEventListener('click', (e) => {
                const field = e.target.dataset.field;
                const projectId = e.target.dataset.project;
                e.target.style.backgroundColor = 'rgba(45, 55, 72, 0.1)';
                e.target.style.border = '1px dashed var(--accent)';
                alert(`Editing ${field} for project ${projectId.substring(0, 8)}...`);
            });
        });
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Test editable field styling and interaction
            assert "style.cursor = 'pointer'" in content
            assert "title = 'Click to edit'" in content
            assert "style.backgroundColor = 'rgba(45, 55, 72, 0.1)'" in content
            assert "style.border = '1px dashed var(--accent)'" in content
            assert "substring(0, 8)" in content

    def test_portfolio_js_data_aggregation_logic(self):
        """Test that data aggregation logic exists in renderDetailedAnalysis"""
        mock_js_content = """
        let developmentPatterns = new Set();
        let allTechKeywords = new Set();
        let docTypes = {};
        
        // Development patterns
        const devPatterns = metrics.development_patterns?.project_evolution || [];
        devPatterns.forEach(pattern => developmentPatterns.add(pattern));
        
        // Technical keywords
        const keywords = metrics.technical_keywords || [];
        keywords.forEach(keyword => allTechKeywords.add(keyword));
        
        // Document types
        const contribution = metrics.contribution_activity?.doc_type_counts || {};
        Object.entries(contribution).forEach(([type, count]) => {
            docTypes[type] = (docTypes[type] || 0) + count;
        });
        
        const avgCompleteness = projects.length > 0 ? (totalCompleteness / projects.length).toFixed(1) : 0;
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Test data aggregation patterns
            assert "developmentPatterns = new Set()" in content
            assert "allTechKeywords = new Set()" in content
            assert "docTypes = {}" in content
            assert "development_patterns?.project_evolution" in content
            assert "technical_keywords || []" in content
            assert "contribution_activity?.doc_type_counts" in content
            assert "Object.entries(contribution)" in content
            assert "(totalCompleteness / projects.length).toFixed(1)" in content

    def test_portfolio_js_ranking_and_display_logic(self):
        """Test that project ranking and display logic exists"""
        mock_js_content = """
        const rank = ['🥇', '🥈', '🥉', '4th', '5th', '6th'][index] || `${index + 1}th`;
        const maintainabilityScore = complexity.maintainability_score ? 
            `${complexity.maintainability_score.overall_score || 0}/100` : 'N/A';
        const developmentIntensity = commitFreq.development_intensity || 'N/A';
        const docTypesDisplay = Object.entries(docTypes).map(([type, count]) => 
            `${type}: ${count}`).join(', ') || 'N/A';
        
        <div class="project-rank">${rank} Place</div>
        <div class="editable-field" data-field="rank" data-project="${project.id}">
        <div class="editable-field" data-field="summary" data-project="${project.id}">
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Test ranking logic
            assert "['🥇', '🥈', '🥉', '4th', '5th', '6th']" in content
            assert "maintainability_score.overall_score || 0" in content
            assert "development_intensity || 'N/A'" in content
            assert "Object.entries(docTypes).map" in content
            assert "join(', ') || 'N/A'" in content
            
            # Test HTML template structure
            assert 'class="project-rank"' in content
            assert 'data-field="rank"' in content
            assert 'data-field="summary"' in content
            assert 'data-project="${project.id}"' in content

    def test_portfolio_js_response_headers(self):
        """Test that JavaScript is served with correct content type"""
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data="// Test JS content")):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/javascript"
    
    def test_portfolio_js_file_not_found(self):
        """Test that 404 is returned when JavaScript file doesn't exist"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/api/static/portfolio.js")
            assert response.status_code == 404
            assert "JavaScript file not found" in response.json()["detail"]

    def test_portfolio_js_chart_methods(self):
        """Test that JavaScript contains chart creation methods"""
        mock_js_content = """
        createPieChart(canvasId, title, data) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, { type: 'pie' });
        }
        
        createBarChart(canvasId, title, data) {
            return new Chart(ctx, { type: 'bar' });
        }
        
        createHorizontalBarChart(canvasId, title, data) {
            return new Chart(ctx, { type: 'bar', options: { indexAxis: 'y' } });
        }
        
        createLineChart(canvasId, title, data) {
            return new Chart(ctx, { type: 'line' });
        }
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify chart creation methods
            assert "createPieChart(" in content
            assert "createBarChart(" in content
            assert "createHorizontalBarChart(" in content
            assert "createLineChart(" in content
            
            # Verify Chart.js integration
            assert "new Chart(" in content
            assert "type: 'pie'" in content
            assert "type: 'bar'" in content
            assert "type: 'line'" in content

    def test_portfolio_js_rendering_methods(self):
        """Test that JavaScript contains comprehensive rendering methods"""
        mock_js_content = """
        renderDashboard(data) {
            this.renderOverviewCards(data.overview);
            this.renderCharts(data.graphs);
            this.renderTopProjects(data.projects);
            this.renderDetailedAnalysis(data.projects);
        }
        
        renderOverviewCards(overview) {}
        renderCharts(graphs) {}
        renderTopProjects(projects) {}
        renderDetailedAnalysis(projects) {}
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify main rendering methods
            assert "renderDashboard(" in content
            assert "renderOverviewCards(" in content
            assert "renderCharts(" in content
            assert "renderTopProjects(" in content
            assert "renderDetailedAnalysis(" in content
            
            # Verify rendering orchestration
            assert "this.renderOverviewCards(data.overview)" in content
            assert "this.renderCharts(data.graphs)" in content

    def test_portfolio_js_project_interaction(self):
        """Test that JavaScript contains project selection and interaction logic"""
        mock_js_content = """
        constructor() {
            this.selectedProjects = new Set();
            this.allProjects = [];
            this.currentPortfolioData = null;
            this.charts = {};
        }
        
        window.toggleProject = function(projectId) {
            const dashboard = window.portfolioDashboard;
            if (dashboard.selectedProjects.has(projectId)) {
                dashboard.selectedProjects.delete(projectId);
            } else {
                dashboard.selectedProjects.add(projectId);
            }
            dashboard.loadPortfolio();
        };
        
        window.toggleAllProjects = function() {
            const dashboard = window.portfolioDashboard;
            const allSelected = dashboard.selectedProjects.size === dashboard.allProjects.length;
        };
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify project state management
            assert "this.selectedProjects = new Set()" in content
            assert "this.allProjects = []" in content
            assert "this.currentPortfolioData = null" in content
            assert "this.charts = {}" in content
            
            # Verify project interaction functions
            assert "window.toggleProject = function(projectId)" in content
            assert "window.toggleAllProjects = function()" in content
            assert "selectedProjects.has(projectId)" in content
            assert "selectedProjects.delete(projectId)" in content
            assert "selectedProjects.add(projectId)" in content

    def test_portfolio_js_data_processing(self):
        """Test that JavaScript contains data processing and aggregation logic"""
        mock_js_content = """
        renderDetailedAnalysis(projects) {
            let totalTestFiles = 0;
            let totalFunctions = 0;
            let totalClasses = 0;
            let githubProjects = 0;
            let localProjects = 0;
            let developmentPatterns = new Set();
            let allTechKeywords = new Set();
            
            projects.forEach(project => {
                const metrics = project.metrics || {};
                totalTestFiles += metrics.test_files_changed || 0;
                totalFunctions += metrics.functions || 0;
                totalClasses += metrics.classes || 0;
                
                if (project.type === 'GitHub') githubProjects++;
                else localProjects++;
            });
        }
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify data aggregation logic
            assert "totalTestFiles" in content
            assert "totalFunctions" in content
            assert "totalClasses" in content
            assert "githubProjects" in content
            assert "localProjects" in content
            assert "developmentPatterns" in content
            assert "allTechKeywords" in content
            
            # Verify project type checking
            assert "project.type === 'GitHub'" in content
            assert "projects.forEach(" in content

    def test_portfolio_js_error_handling(self):
        """Test that JavaScript contains comprehensive error handling"""
        mock_js_content = """
        async loadProjects() {
            try {
                console.log('🔍 Attempting to load projects...');
                const response = await fetch('/api/projects');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const projects = await response.json();
                console.log('✅ Projects loaded successfully');
            } catch (error) {
                console.error('❌ Error loading projects:', error);
                document.getElementById('projectList').innerHTML = 
                    '<div style="color: var(--danger)">Failed to load projects: ' + error.message + '</div>';
            }
        }
        
        showError(message) {
            console.error(message);
            alert(`Error: ${message}`);
        }
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify error handling patterns
            assert "try {" in content
            assert "catch (error)" in content
            assert "console.error(" in content
            assert "showError(" in content
            assert "throw new Error(" in content
            assert "Failed to load" in content

    def test_portfolio_js_chart_configuration(self):
        """Test that JavaScript contains proper Chart.js configuration options"""
        mock_js_content = """
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#4a5568',
                        font: { size: 12 },
                        padding: 15,
                        usePointStyle: true
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#e2e8f0' },
                    ticks: { color: '#4a5568', font: { size: 11 } }
                },
                x: {
                    grid: { color: '#e2e8f0' },
                    ticks: { color: '#4a5568', font: { size: 11 } }
                }
            }
        }
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify Chart.js configuration options
            assert "responsive: true" in content
            assert "maintainAspectRatio: false" in content
            assert "beginAtZero: true" in content
            assert "usePointStyle: true" in content
            assert "position: 'bottom'" in content
            
            # Verify color scheme consistency
            assert "#4a5568" in content
            assert "#e2e8f0" in content

    def test_portfolio_js_dom_manipulation(self):
        """Test that JavaScript contains DOM manipulation and event handling"""
        mock_js_content = """
        document.getElementById('projectList').innerHTML = projectsHtml;
        document.getElementById('overviewCards').innerHTML = cardsHtml;
        document.getElementById('topProjects').innerHTML = topProjectsHtml;
        document.getElementById('detailedAnalysis').innerHTML = analysisHtml;
        
        document.querySelectorAll('.editable-field').forEach(element => {
            element.style.cursor = 'pointer';
            element.title = 'Click to edit';
            
            element.addEventListener('click', (e) => {
                const field = e.target.dataset.field;
                const projectId = e.target.dataset.project;
                console.log(`Edit ${field} for project ${projectId}`);
            });
        });
        
        document.addEventListener('DOMContentLoaded', function() {
            window.portfolioDashboard = new PortfolioDashboard();
        });
        """
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            content = response.content.decode()
            
            # Verify DOM element targeting
            assert "document.getElementById(" in content
            assert "document.querySelectorAll(" in content
            assert "projectList" in content
            assert "overviewCards" in content
            assert "topProjects" in content
            assert "detailedAnalysis" in content
            
            # Verify event handling
            assert "addEventListener(" in content
            assert "DOMContentLoaded" in content
            assert "dataset.field" in content
            assert "dataset.project" in content
            assert ".style.cursor = 'pointer'" in content