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
