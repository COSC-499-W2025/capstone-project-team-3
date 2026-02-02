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
    
    renderTopProjects(projects) {
        const topProjects = document.getElementById('topProjects');
        
        if (!projects || projects.length === 0) {
            topProjects.innerHTML = '<div style="color: var(--text-muted)">No projects selected</div>';
            return;
        }
        
        // Sort by rank and take top 6
        const sortedProjects = projects.sort((a, b) => (b.rank || 0) - (a.rank || 0)).slice(0, 6);
        
        topProjects.innerHTML = sortedProjects.map((project, index) => {
            const rank = ['🥇', '🥈', '🥉', '4th', '5th', '6th'][index] || `${index + 1}th`;
            const metrics = project.metrics || {};
            const skills = project.skills || [];
            const complexity = metrics.complexity_analysis || {};
            const commitPatterns = metrics.commit_patterns || {};
            const contributionActivity = metrics.contribution_activity || {};
            
            // Format complex data for display
            const maintainabilityScore = complexity.maintainability_score ? 
                `${complexity.maintainability_score.overall_score || 0}/100` : 'N/A';
            
            const commitFreq = commitPatterns.commit_frequency || {};
            const developmentIntensity = commitFreq.development_intensity || 'N/A';
            
            const docTypes = contributionActivity.doc_type_counts || {};
            const docTypesDisplay = Object.entries(docTypes).map(([type, count]) => 
                `${type}: ${count}`).join(', ') || 'N/A';
            
            return `
                <div class="project-card">
                    <div class="project-rank">${rank} Place</div>
                    <div class="project-title">${project.title}</div>
                    <div class="project-score-display editable-field" data-field="rank" data-project="${project.id}">
                        ${(project.rank || 0).toFixed(2)}
                    </div>
                    <div class="project-dates editable-field" data-field="dates" data-project="${project.id}">
                        ${project.dates}
                    </div>
                    
                    ${project.summary ? `
                        <div class="project-summary">
                            <h4>📝 Summary</h4>
                            <p class="editable-field" data-field="summary" data-project="${project.id}">
                                ${project.summary.substring(0, 300)}${project.summary.length > 300 ? '...' : ''}
                            </p>
                        </div>
                    ` : ''}
                    
                    <div class="project-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Lines of Code:</span>
                            <span class="metric-value">${(metrics.total_lines || 0).toLocaleString()}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Commits:</span>
                            <span class="metric-value">${metrics.total_commits || 'N/A'}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Type:</span>
                            <span class="metric-value">${project.type || 'Unknown'}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Test Files:</span>
                            <span class="metric-value">${metrics.test_files_changed || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Functions:</span>
                            <span class="metric-value">${metrics.functions || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Classes:</span>
                            <span class="metric-value">${metrics.classes || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Maintainability:</span>
                            <span class="metric-value">${maintainabilityScore}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Dev Intensity:</span>
                            <span class="metric-value">${developmentIntensity}</span>
                        </div>
                        ${metrics.completeness_score ? `
                            <div class="metric-item">
                                <span class="metric-label">Completeness:</span>
                                <span class="metric-value">${metrics.completeness_score}%</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Word Count:</span>
                                <span class="metric-value">${(metrics.word_count || 0).toLocaleString()}</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${docTypesDisplay !== 'N/A' ? `
                        <div class="contribution-details">
                            <h4>📊 Document Types</h4>
                            <p>${docTypesDisplay}</p>
                        </div>
                    ` : ''}
                    
                    <div class="project-skills-display">
                        ${skills.slice(0, 8).map(skill => 
                            `<span class="project-skill-tag">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click handlers for editable fields
        document.querySelectorAll('.editable-field').forEach(element => {
            element.style.cursor = 'pointer';
            element.style.position = 'relative';
            element.title = 'Click to edit';
            
            element.addEventListener('click', (e) => {
                const field = e.target.dataset.field;
                const projectId = e.target.dataset.project;
                console.log(`Edit ${field} for project ${projectId}`);
                // Add visual indicator that field is editable
                e.target.style.backgroundColor = 'rgba(45, 55, 72, 0.1)';
                e.target.style.border = '1px dashed var(--accent)';
                
                // TODO: Implement editing logic here
                alert(`Editing ${field} for project ${projectId.substring(0, 8)}... - Logic to be implemented by teammate`);
            });
        });
    }
    
    renderDetailedAnalysis(projects) {
        const analysisContainer = document.getElementById('detailedAnalysis');
        
        if (!projects || projects.length === 0) {
            analysisContainer.innerHTML = '<div style="color: var(--text-muted)">No projects selected</div>';
            return;
        }
        
        // Aggregate analysis data across all projects
        let totalTestFiles = 0;
        let totalFunctions = 0;
        let totalClasses = 0;
        let totalComponents = 0;
        let githubProjects = 0;
        let localProjects = 0;
        let totalCompleteness = 0;
        let totalWords = 0;
        let developmentPatterns = new Set();
        let allTechKeywords = new Set();
        let docTypes = {};
        
        projects.forEach(project => {
            const metrics = project.metrics || {};
            
            totalTestFiles += metrics.test_files_changed || 0;
            totalFunctions += metrics.functions || 0;
            totalClasses += metrics.classes || 0;
            totalComponents += metrics.components || 0;
            
            if (project.type === 'GitHub') githubProjects++;
            else localProjects++;
            
            if (metrics.completeness_score) totalCompleteness += metrics.completeness_score;
            if (metrics.word_count) totalWords += metrics.word_count;
            
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
        });
        
        const avgCompleteness = projects.length > 0 ? (totalCompleteness / projects.length).toFixed(1) : 0;
        
        analysisContainer.innerHTML = `
            <div class="analysis-card">
                <h4>🧪 Testing & Quality</h4>
                <div class="analysis-item">
                    <span class="analysis-label">Total Test Files:</span>
                    <span class="analysis-value">${totalTestFiles}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Functions Created:</span>
                    <span class="analysis-value">${totalFunctions}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Classes Created:</span>
                    <span class="analysis-value">${totalClasses}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Components Built:</span>
                    <span class="analysis-value">${totalComponents}</span>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>📊 Project Distribution</h4>
                <div class="analysis-item">
                    <span class="analysis-label">GitHub Projects:</span>
                    <span class="analysis-value">${githubProjects}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Local Projects:</span>
                    <span class="analysis-value">${localProjects}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Avg Completeness:</span>
                    <span class="analysis-value">${avgCompleteness}%</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Total Words:</span>
                    <span class="analysis-value">${totalWords.toLocaleString()}</span>
                </div>
            </div>
            
            <div class="analysis-card">
                <h4>🚀 Development Patterns</h4>
                <div class="analysis-item">
                    <span class="analysis-label">Evolution Patterns:</span>
                </div>
                ${Array.from(developmentPatterns).map(pattern => 
                    `<div class="keyword-tags"><span class="keyword-tag">${pattern}</span></div>`
                ).join('')}
            </div>
            
            <div class="analysis-card">
                <h4>📝 Document Types</h4>
                ${Object.entries(docTypes).map(([type, count]) => `
                    <div class="analysis-item">
                        <span class="analysis-label">${type}:</span>
                        <span class="analysis-value">${count}</span>
                    </div>
                `).join('')}
            </div>
            
        `;
    }
    
    showError(message) {
        console.error(message);
        // You could add a toast notification system here
        alert(`Error: ${message}`);
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
