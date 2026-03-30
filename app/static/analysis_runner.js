const uploadIdInput = document.getElementById('uploadId');
const defaultModeSelect = document.getElementById('defaultMode');
const similarityActionSelect = document.getElementById('similarityAction');
const cleanupZipSelect = document.getElementById('cleanupZip');
const cleanupExtractedSelect = document.getElementById('cleanupExtracted');

const loadProjectsBtn = document.getElementById('loadProjectsBtn');
const runAnalysisBtn = document.getElementById('runAnalysisBtn');
const copyPayloadBtn = document.getElementById('copyPayloadBtn');

const loadStatus = document.getElementById('loadStatus');
const runStatus = document.getElementById('runStatus');
const projectsBody = document.getElementById('projectsBody');
const responseBox = document.getElementById('responseBox');

let projects = [];

function setStatus(el, message, isError = false) {
  el.textContent = message;
  el.className = `status ${isError ? 'error' : 'ok'}`;
}

function renderProjects() {
  if (!projects.length) {
    projectsBody.innerHTML = '<tr><td colspan="3" style="color:#718096;">No projects loaded yet.</td></tr>';
    return;
  }

  projectsBody.innerHTML = projects.map((project, index) => `
    <tr>
      <td>${project.name}</td>
      <td>
        <select data-project-index="${index}" class="project-mode-select">
          <option value="local" ${project.mode === 'local' ? 'selected' : ''}>local</option>
          <option value="ai" ${project.mode === 'ai' ? 'selected' : ''}>ai</option>
        </select>
      </td>
      <td style="font-size:12px; color:#4a5568;">${project.path}</td>
    </tr>
  `).join('');

  document.querySelectorAll('.project-mode-select').forEach(select => {
    select.addEventListener('change', (event) => {
      const index = Number(event.target.dataset.projectIndex);
      projects[index].mode = event.target.value;
    });
  });
}

function buildPayload() {
  const uploadId = (uploadIdInput.value || '').trim();
  const project_analysis_types = {};
  projects.forEach(project => {
    project_analysis_types[project.name] = project.mode;
  });

  return {
    upload_id: uploadId,
    default_analysis_type: defaultModeSelect.value,
    project_analysis_types,
    similarity_action: similarityActionSelect.value,
    cleanup_zip: cleanupZipSelect.value === 'true',
    cleanup_extracted: cleanupExtractedSelect.value === 'true',
  };
}

async function loadProjects() {
  const uploadId = (uploadIdInput.value || '').trim();
  if (!uploadId) {
    setStatus(loadStatus, 'Please provide upload_id first.', true);
    return;
  }

  setStatus(loadStatus, 'Loading projects...');

  try {
    const response = await fetch(`/api/analysis/uploads/${encodeURIComponent(uploadId)}/projects`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to load projects');
    }

    projects = (data.projects || []).map(project => ({
      name: project.name,
      path: project.path,
      mode: defaultModeSelect.value,
    }));

    renderProjects();
    setStatus(loadStatus, `Loaded ${projects.length} project(s).`);
  } catch (error) {
    projects = [];
    renderProjects();
    setStatus(loadStatus, `Error: ${error.message}`, true);
  }
}

async function runAnalysis() {
  const payload = buildPayload();

  if (!payload.upload_id) {
    setStatus(runStatus, 'Please provide upload_id first.', true);
    return;
  }

  setStatus(runStatus, 'Running analysis...');

  try {
    const response = await fetch('/api/analysis/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    responseBox.textContent = JSON.stringify(data, null, 2);

    if (!response.ok) {
      throw new Error(data.detail || 'Analysis failed');
    }

    setStatus(runStatus, `Done: analyzed=${data.analyzed_projects}, skipped=${data.skipped_projects}, failed=${data.failed_projects}`);
  } catch (error) {
    setStatus(runStatus, `Error: ${error.message}`, true);
  }
}

async function copyPayload() {
  const payload = buildPayload();
  const text = JSON.stringify(payload, null, 2);
  await navigator.clipboard.writeText(text);
  setStatus(runStatus, 'Payload copied to clipboard.');
}

loadProjectsBtn.addEventListener('click', loadProjects);
runAnalysisBtn.addEventListener('click', runAnalysis);
copyPayloadBtn.addEventListener('click', copyPayload);
defaultModeSelect.addEventListener('change', () => {
  projects = projects.map(project => ({ ...project, mode: defaultModeSelect.value }));
  renderProjects();
});
