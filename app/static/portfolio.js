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
    
    // Helper function to get the display score based on override flag
    getDisplayScore(project) {
        if (project.score_overridden && project.score_overridden_value !== null && project.score_overridden_value !== undefined) {
            return project.score_overridden_value;
        }
        return project.score || 0;
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
                    <div class="project-score">Score: ${this.getDisplayScore(project).toFixed(2)}</div>
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
        console.log('📊 Rendering dashboard with data:', data);
        console.log('📊 Projects count:', data.projects?.length);
        console.log('📊 Graphs data:', data.graphs);
        
        this.renderOverviewCards(data.overview);
        console.log('✅ Overview cards rendered');
        
        this.renderCharts(data.graphs);
        console.log('✅ Charts rendered');
        
        this.renderTopProjects(data.projects);
        console.log('✅ Top projects rendered');
        
        this.renderDetailedAnalysis(data.projects);
        console.log('✅ Detailed analysis rendered');
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

    // Add these defensive checks to your chart methods:

createPieChart(canvasId, title, data) {
    // Guard: Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping pie chart creation');
        return null;
    }
    
    // Guard: Check if canvas element exists
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) {
        console.warn(`Canvas element with ID '${canvasId}' not found, skipping pie chart creation`);
        return null;
    }
    
    // Guard: Check if canvas context is available
    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.warn(`Cannot get 2D context for canvas '${canvasId}', skipping pie chart creation`);
        return null;
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    try {
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
    } catch (error) {
        console.error(`Error creating pie chart for '${canvasId}':`, error);
        return null;
    }
}

createBarChart(canvasId, title, data) {
    // Guard: Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping bar chart creation');
        return null;
    }
    
    // Guard: Check if canvas element exists
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) {
        console.warn(`Canvas element with ID '${canvasId}' not found, skipping bar chart creation`);
        return null;
    }
    
    // Guard: Check if canvas context is available
    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.warn(`Cannot get 2D context for canvas '${canvasId}', skipping bar chart creation`);
        return null;
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    try {
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
    } catch (error) {
        console.error(`Error creating bar chart for '${canvasId}':`, error);
        return null;
    }
}

createHorizontalBarChart(canvasId, title, data) {
    // Guard: Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping horizontal bar chart creation');
        return null;
    }
    
    // Guard: Check if canvas element exists
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) {
        console.warn(`Canvas element with ID '${canvasId}' not found, skipping horizontal bar chart creation`);
        return null;
    }
    
    // Guard: Check if canvas context is available
    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.warn(`Cannot get 2D context for canvas '${canvasId}', skipping horizontal bar chart creation`);
        return null;
    }
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    try {
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
    } catch (error) {
        console.error(`Error creating horizontal bar chart for '${canvasId}':`, error);
        return null;
    }
}

createLineChart(canvasId, title, data) {
    // Guard: Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping line chart creation');
        return null;
    }
    
    // Guard: Check if canvas element exists
    const canvasElement = document.getElementById(canvasId);
    if (!canvasElement) {
        console.warn(`Canvas element with ID '${canvasId}' not found, skipping line chart creation`);
        return null;
    }
    
    // Guard: Check if canvas context is available
    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
        console.warn(`Cannot get 2D context for canvas '${canvasId}', skipping line chart creation`);
        return null;
    }
    
    const sortedData = Object.entries(data).sort();
    const labels = sortedData.map(([month]) => month);
    const values = sortedData.map(([, value]) => value);
    
    try {
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
                        ticks: { 
                            color: '#4a5568', 
                            font: { size: 11 },
                            stepSize: 0.5
                        },
                        title: {
                            display: title === 'Monthly Activity',
                            text: 'Activity Level',
                            color: '#4a5568',
                            font: { size: 12, weight: 'bold' }
                        }
                    },
                    x: {
                        grid: { color: '#e2e8f0' },
                        ticks: { color: '#4a5568', font: { size: 11 } }
                    }
                }
            }
        });
    } catch (error) {
        console.error(`Error creating line chart for '${canvasId}':`, error);
        return null;
    }
}

// Also update renderCharts to handle null chart returns gracefully:
renderCharts(graphs) {
    console.log('📈 renderCharts called with:', graphs);
    
    // Destroy existing charts
    Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    this.charts = {};
    
    // Guard: Check if Chart.js is available at all
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js not loaded! Charts will not render.');
        return;
    }
    console.log('✅ Chart.js is available');
    
    // Language Distribution (Pie Chart)
    const languageChart = this.createPieChart(
        'languageChart',
        'Language Distribution',
        graphs.language_distribution || {}
    );
    if (languageChart) {
        this.charts.language = languageChart;
    }
    
    // Project Complexity (Bar Chart)
    const complexityChart = this.createBarChart(
        'complexityChart', 
        'Project Complexity',
        {
            'Small (<1000)': graphs.complexity_distribution?.distribution?.small || 0,
            'Medium (1000-3000)': graphs.complexity_distribution?.distribution?.medium || 0,
            'Large (>3000)': graphs.complexity_distribution?.distribution?.large || 0
        }
    );
    if (complexityChart) {
        this.charts.complexity = complexityChart;
    }
    
    // Score Distribution (Bar Chart)
    const scoreChart = this.createBarChart(
        'scoreChart',
        'Score Distribution',
        {
            'Excellent (90-100%)': graphs.score_distribution?.distribution?.excellent || 0,
            'Good (80-89%)': graphs.score_distribution?.distribution?.good || 0,
            'Fair (70-79%)': graphs.score_distribution?.distribution?.fair || 0,
            'Poor (<70%)': graphs.score_distribution?.distribution?.poor || 0
        }
    );
    if (scoreChart) {
        this.charts.score = scoreChart;
    }
    
    // Monthly Activity (Line Chart)
    const activityChart = this.createLineChart(
        'activityChart',
        'Monthly Activity',
        graphs.monthly_activity || {}
    );
    if (activityChart) {
        this.charts.activity = activityChart;
    }
    
    // Top Skills (Horizontal Bar Chart)
    const skillsChart = this.createHorizontalBarChart(
        'skillsChart',
        'Top Skills',
        graphs.top_skills || {}
    );
    if (skillsChart) {
        this.charts.skills = skillsChart;
    }
    
    // Project Type Comparison
    if (this.currentPortfolioData?.project_type_analysis) {
        const typeData = this.currentPortfolioData.project_type_analysis;
        const projectTypeChart = this.createBarChart(
            'projectTypeChart',
            'Project Types',
            {
                'GitHub Projects': typeData.github?.count || 0,
                'Local Projects': typeData.local?.count || 0
            }
        );
        if (projectTypeChart) {
            this.charts.projectType = projectTypeChart;
        }
    }
}

// Also add a missing showError method:
showError(message) {
    console.error('Dashboard Error:', message);
    
    // Try to display error in UI if error container exists
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="error-message" style="
                background-color: #fed7d7;
                color: #c53030;
                padding: 1rem;
                border-radius: 0.375rem;
                border: 1px solid #fc8181;
                margin: 1rem 0;
            ">
                <strong>Error:</strong> ${message}
            </div>
        `;
        errorContainer.style.display = 'block';
    } else {
        // Fallback to alert if no error container
        alert(`Dashboard Error: ${message}`);
    }
}

  renderTopProjects(projects) {
        const topProjects = document.getElementById('topProjects');
        
        if (!projects || projects.length === 0) {
            topProjects.innerHTML = '<div style="color: var(--text-muted)">No projects selected</div>';
            return;
        }
        
        // Generate unique cache buster for this render
        const cacheBuster = Date.now() + Math.random().toString(36).substring(7);
        
        // Sort by score and take top 6
        const sortedProjects = projects.sort((a, b) => this.getDisplayScore(b) - this.getDisplayScore(a)).slice(0, 6);
        
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
                <div class="project-card" style="position: relative;">
                    <!-- Thumbnail Button - Top Right -->
                    <div class="thumbnail-button-section" style="position: absolute; top: 16px; right: 16px; z-index: 10;">
                        <button class="upload-thumbnail-btn" 
                                onclick="window.portfolioDashboard.uploadThumbnail('${project.id}')"
                                style="background: var(--accent); color: white; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 11px; font-weight: 500; box-shadow: var(--shadow);">
                            ${project.thumbnail_url ? 'Change Thumbnail' : 'Add Thumbnail'}
                        </button>
                    </div>
                    
                    <div class="project-rank">${rank} Place</div>
                    <div class="project-title" style="padding-right: 140px;">${project.title}</div>
                    
                    <div class="project-score-display editable-field" data-field="rank" data-project="${project.id}">
                        ${this.getDisplayScore(project).toFixed(2)}${project.score_overridden ? ' <span style="color: var(--warning); font-size: 0.8em;">(Override)</span>' : ''}
                    </div>
                    <div class="project-dates editable-field" data-field="dates" data-project="${project.id}">
                        ${project.dates}
                    </div>
                    
                    <!-- Thumbnail Image Display - Center -->
                    ${project.thumbnail_url ? `
                        <div class="thumbnail-display" style="margin: 16px 0; text-align: center;">
                            <img src="${project.thumbnail_url}?cb=${cacheBuster}" 
                                 alt="${project.title} thumbnail" 
                                 class="project-thumbnail"
                                 style="max-width: 100%; height: auto; max-height: 200px; border-radius: 8px; border: 2px solid var(--border); box-shadow: var(--shadow);" 
                                 crossorigin="anonymous" />
                        </div>
                    ` : ''}
                    
                    ${project.summary ? `
                        <div class="project-summary">
                            <h4>📝 Project Summary</h4>
                            <div class="summary-content">
                                <div class="summary-text ${this.shouldTruncateSummary(project.summary) ? 'truncated' : ''}">
                                    <span class="editable-field" data-field="summary" data-project="${project.id}">
                                        ${project.summary}
                                    </span>
                                </div>
                                ${this.shouldTruncateSummary(project.summary) ? `
                                    <button class="show-more-btn" onclick="toggleSummary(this)">Show More</button>
                                ` : ''}
                            </div>
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
    
    async uploadThumbnail(projectId) {
        // Create a hidden file input element
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/jpeg,image/png,image/gif,image/svg+xml,image/webp';
        input.style.display = 'none';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select a valid image file.');
                return;
            }
            
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('Image file is too large. Please select an image smaller than 5MB.');
                return;
            }
            
            try {
                // Create FormData to send the file
                const formData = new FormData();
                formData.append('project_id', projectId);
                formData.append('image', file);
                
                // Show loading state
                console.log('📤 Uploading thumbnail for project:', projectId);
                
                // Upload thumbnail with cache-busting headers
                const response = await fetch('/api/portfolio/project/thumbnail', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache'
                    }
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Upload failed: ${response.status} - ${errorText}`);
                }
                
                const result = await response.json();
                console.log('✅ Thumbnail uploaded successfully:', result);
                
                // Force clear any cached images for this project
                const imageElements = document.querySelectorAll(`img[alt*="${projectId}"]`);
                imageElements.forEach(img => {
                    const src = img.src.split('?')[0];
                    img.src = src + '?cb=' + Date.now() + Math.random();
                });
                
                // Wait a moment for the file to be fully written
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Reload portfolio to show new thumbnail with fresh cache
                await this.loadPortfolio();
                
                console.log('✅ Portfolio reloaded with new thumbnail');
                alert('Thumbnail uploaded successfully!');
            } catch (error) {
                console.error('❌ Error uploading thumbnail:', error);
                alert('Failed to upload thumbnail: ' + error.message);
            }
        };
        
        // Trigger file selection dialog
        input.click();
    }
    
    showError(message) {
        console.error(message);
        // You could add a toast notification system here
        alert(`Error: ${message}`);
    }

    shouldTruncateSummary(summary) {
        // Truncate if summary is longer than 25 words or 150 characters  
        // This ensures consistent card heights with uniform truncation
        const wordCount = summary.split(/\s+/).length;
        const charCount = summary.length;
        return wordCount > 25 || charCount > 150;
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

// Global function to toggle summary visibility
window.toggleSummary = function(button) {
    const summaryContent = button.closest('.summary-content');
    const summaryText = summaryContent.querySelector('.summary-text');
    const isExpanded = !summaryText.classList.contains('truncated');
    
    if (isExpanded) {
        // Collapse
        summaryText.classList.add('truncated');
        button.textContent = 'Show More';
    } else {
        // Expand
        summaryText.classList.remove('truncated');
        button.textContent = 'Show Less';
    }
};

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.portfolioDashboard = new PortfolioDashboard();
});
