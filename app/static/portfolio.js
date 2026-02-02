// Portfolio Dashboard JavaScript
class PortfolioDashboard {
    constructor() {
        this.selectedProjects = new Set();
        this.allProjects = [];
        this.currentPortfolioData = null;
        this.charts = {};
        
        this.init();
    }
    
    async init() {
        try {
            // Load projects for sidebar
            await this.loadProjects();
            
            // Load initial portfolio data (all projects selected)
            await this.loadPortfolio();
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async loadProjects() {
        try {
            console.log('🔍 Attempting to load projects from /api/projects...');
            console.log('🌐 Current location:', window.location.href);
            
            const response = await fetch('/api/projects');
            console.log('📡 Response status:', response.status);
            console.log('📡 Response URL:', response.url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const projects = await response.json();
            console.log('✅ Projects loaded successfully:', projects.length, 'projects');
            
            this.allProjects = projects;
            // Select all projects by default
            this.selectedProjects = new Set(projects.map(p => p.id));
            
            this.renderProjectList(projects);
        } catch (error) {
            console.error('❌ Error loading projects:', error);
            document.getElementById('projectList').innerHTML = 
                '<div style="color: var(--danger)">Failed to load projects: ' + error.message + '</div>';
        }
    }
    
    renderProjectList(projects) {
        const projectList = document.getElementById('projectList');
        
        if (projects.length === 0) {
            projectList.innerHTML = '<div style="color: var(--text-muted)">No projects found</div>';
            return;
        }
        
        projectList.innerHTML = projects.map(project => {
            const isSelected = this.selectedProjects.has(project.id);
            const skillsHtml = (project.skills || []).slice(0, 3).map(skill => 
                `<span class="skill-tag">${skill}</span>`
            ).join('');
            
            return `
                <div class="project-item ${isSelected ? 'selected' : ''}" 
                     onclick="toggleProject('${project.id}')">
                    <input type="checkbox" class="project-checkbox" 
                           ${isSelected ? 'checked' : ''} 
                           onclick="event.stopPropagation()">
                    <div class="project-name">${project.name}</div>
                    <div class="project-score">Score: ${(project.score || 0).toFixed(2)}</div>
                    <div class="project-skills">${skillsHtml}</div>
                </div>
            `;
        }).join('');
    }
    
    async loadPortfolio() {
        try {
            const selectedIds = Array.from(this.selectedProjects);
            const url = selectedIds.length > 0 && selectedIds.length < this.allProjects.length 
                ? `/api/portfolio?project_ids=${selectedIds.join(',')}`
                : '/api/portfolio';
            
            console.log('🔍 Attempting to load portfolio from:', url);
            const response = await fetch(url);
            console.log('📡 Portfolio response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const portfolioData = await response.json();
            console.log('✅ Portfolio loaded successfully:', portfolioData.metadata);
            
            this.currentPortfolioData = portfolioData;
            this.renderDashboard(portfolioData);
        } catch (error) {
            console.error('❌ Error loading portfolio:', error);
            this.showError('Failed to load portfolio data: ' + error.message);
        }
    }
    
    renderDashboard(data) {
        this.renderOverviewCards(data.overview);
        this.renderCharts(data.graphs);
        this.renderTopProjects(data.projects);
        this.renderDetailedAnalysis(data.projects);
    }
    
    renderOverviewCards(overview) {
        const overviewCards = document.getElementById('overviewCards');
        
        overviewCards.innerHTML = `
            <div class="overview-card">
                <div class="overview-card-value">${overview.total_projects}</div>
                <div class="overview-card-label">Total Projects</div>
            </div>
            <div class="overview-card">
                <div class="overview-card-value">${overview.avg_score.toFixed(2)}</div>
                <div class="overview-card-label">Average Score</div>
            </div>
            <div class="overview-card">
                <div class="overview-card-value">${overview.total_skills}</div>
                <div class="overview-card-label">Total Skills</div>
            </div>
            <div class="overview-card">
                <div class="overview-card-value">${overview.total_languages}</div>
                <div class="overview-card-label">Languages Used</div>
            </div>
            <div class="overview-card">
                <div class="overview-card-value">${(overview.total_lines || 0).toLocaleString()}</div>
                <div class="overview-card-label">Lines of Code</div>
            </div>
        `;
    }
      renderCharts(graphs) {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        
        // Language Distribution (Pie Chart)
        this.charts.language = this.createPieChart(
            'languageChart',
            'Language Distribution',
            graphs.language_distribution
        );
        
        // Project Complexity (Bar Chart)
        this.charts.complexity = this.createBarChart(
            'complexityChart', 
            'Project Complexity',
            {
                'Small (<1000)': graphs.complexity_distribution.distribution.small,
                'Medium (1000-3000)': graphs.complexity_distribution.distribution.medium,
                'Large (>3000)': graphs.complexity_distribution.distribution.large
            }
        );
        
        // Score Distribution (Bar Chart)
        this.charts.score = this.createBarChart(
            'scoreChart',
            'Score Distribution',
            {
                'Excellent (90-100%)': graphs.score_distribution.distribution.excellent,
                'Good (80-89%)': graphs.score_distribution.distribution.good,
                'Fair (70-79%)': graphs.score_distribution.distribution.fair,
                'Poor (<70%)': graphs.score_distribution.distribution.poor
            }
        );
        
        // Monthly Activity (Line Chart)
        this.charts.activity = this.createLineChart(
            'activityChart',
            'Monthly Activity',
            graphs.monthly_activity
        );
        
        // Top Skills (Horizontal Bar Chart)
        this.charts.skills = this.createHorizontalBarChart(
            'skillsChart',
            'Top Skills',
            graphs.top_skills
        );
        
        // Project Type Comparison
        if (this.currentPortfolioData?.project_type_analysis) {
            const typeData = this.currentPortfolioData.project_type_analysis;
            this.charts.projectType = this.createBarChart(
                'projectTypeChart',
                'Project Types',
                {
                    'GitHub Projects': typeData.github.count,
                    'Local Projects': typeData.local.count
                }
            );
        }
    }
    
    createPieChart(canvasId, title, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#2d3748', '#4a5568', '#718096', '#a0aec0',
                        '#48bb78', '#ed8936', '#667eea', '#764ba2',
                        '#f687b3', '#9f7aea', '#38b2ac', '#68d391'
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
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
                }
            }
        });
    }
    
    createBarChart(canvasId, title, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: '#2d3748',
                    borderColor: '#4a5568',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
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
        });
    }
    
    createHorizontalBarChart(canvasId, title, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: '#4a5568',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: '#e2e8f0' },
                        ticks: { color: '#4a5568', font: { size: 11 } }
                    },
                    y: {
                        grid: { color: '#e2e8f0' },
                        ticks: { color: '#4a5568', font: { size: 11 } }
                    }
                }
            }
        });
    }
    
    createLineChart(canvasId, title, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const sortedData = Object.entries(data).sort();
        const labels = sortedData.map(([month]) => month);
        const values = sortedData.map(([, value]) => value);
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Activity',
                    data: values,
                    borderColor: '#2d3748',
                    backgroundColor: 'rgba(45, 55, 72, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#2d3748',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
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
        });
    }
    

}

// Global functions for HTML event handlers
window.toggleProject = function(projectId) {
    const dashboard = window.portfolioDashboard;
    const projectItem = event.currentTarget;
    const checkbox = projectItem.querySelector('.project-checkbox');
    
    if (dashboard.selectedProjects.has(projectId)) {
        dashboard.selectedProjects.delete(projectId);
        projectItem.classList.remove('selected');
        checkbox.checked = false;
    } else {
        dashboard.selectedProjects.add(projectId);
        projectItem.classList.add('selected');
        checkbox.checked = true;
    }
    
    // Reload portfolio with new selection
    dashboard.loadPortfolio();
};

window.toggleAllProjects = function() {
    const dashboard = window.portfolioDashboard;
    const allSelected = dashboard.selectedProjects.size === dashboard.allProjects.length;
    
    if (allSelected) {
        // Deselect all
        dashboard.selectedProjects.clear();
        document.querySelector('.select-all-btn').textContent = 'Select All';
    } else {
        // Select all
        dashboard.selectedProjects = new Set(dashboard.allProjects.map(p => p.id));
        document.querySelector('.select-all-btn').textContent = 'Deselect All';
    }
    
    dashboard.renderProjectList(dashboard.allProjects);
    dashboard.loadPortfolio();
};

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.portfolioDashboard = new PortfolioDashboard();
});
