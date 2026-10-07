import './style.css';

const byId = (id) => document.getElementById(id);
const TOKEN_KEY = 'psicat_vite_workbench_token';
let connected = false;

function writeActivity(value) {
  byId('activity').textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
}

async function api(path, options = {}) {
  const token = byId('token').value.trim();
  if (!token) throw new Error('Enter the local workbench token first.');
  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: 'Bearer'.concat(' ', token),
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
  });
  const result = await response.json();
  if (!response.ok || result.ok === false) throw new Error(result.error || `HTTP ${response.status}`);
  return result;
}

function actionButton(label, action, projectName, className = '') {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = className;
  button.textContent = label;
  button.addEventListener('click', async () => {
    try {
      button.disabled = true;
      const result = await api('/api/action', {
        method: 'POST',
        body: JSON.stringify({ action, name: projectName }),
      });
      writeActivity(result);
      await refreshProjects();
    } catch (error) {
      writeActivity(error.message);
    } finally {
      button.disabled = false;
    }
  });
  return button;
}

function renderProjects(projects) {
  const root = byId('projects');
  root.replaceChildren();
  if (!projects.length) {
    const empty = document.createElement('p');
    empty.className = 'empty';
    empty.textContent = 'No projects yet. Scaffold a starter to begin.';
    root.appendChild(empty);
    return;
  }
  projects.forEach((project) => {
    const card = document.createElement('article');
    card.className = 'project-card';
    const heading = document.createElement('div');
    heading.className = 'project-heading';
    const name = document.createElement('h3');
    name.textContent = project.name;
    const template = document.createElement('span');
    template.className = 'pill';
    template.textContent = project.template;
    heading.append(name, template);
    const files = document.createElement('p');
    files.className = 'file-count';
    files.textContent = `${project.files.length} project files${project.ignored_project_vite_config ? ' · project Vite config is ignored' : ''}`;
    const actions = document.createElement('div');
    actions.className = 'actions';
    actions.append(
      actionButton('Inspect', 'inspect', project.name),
      actionButton(project.preview ? 'Stop preview' : 'Start preview', project.preview ? 'preview_stop' : 'preview_start', project.name),
      actionButton('Build', 'build', project.name, 'build-button'),
    );
    if (project.preview) {
      const link = document.createElement('a');
      link.href = project.preview;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Open preview ↗';
      link.className = 'preview-link';
      actions.appendChild(link);
    }
    card.append(heading, files, actions);
    root.appendChild(card);
  });
}

async function refreshProjects() {
  if (!connected) return;
  const [status, projectList] = await Promise.all([api('/api/status'), api('/api/projects')]);
  byId('status').textContent = `${status.running_previews.length} active preview${status.running_previews.length === 1 ? '' : 's'} · ${status.workspace_root}`;
  byId('status-dot').classList.add('ready');
  byId('version').textContent = `Vite ${status.vite_version} · Node ${status.node_version}`;
  byId('footer-version').textContent = status.vite_version;
  renderProjects(projectList.projects);
}

byId('token').value = sessionStorage.getItem(TOKEN_KEY) || '';
byId('connect').addEventListener('click', async () => {
  try {
    await api('/api/status');
    connected = true;
    sessionStorage.setItem(TOKEN_KEY, byId('token').value.trim());
    byId('status').textContent = 'Connected to the local Vite workbench.';
    await refreshProjects();
  } catch (error) {
    connected = false;
    byId('status').textContent = error.message;
    byId('status-dot').classList.remove('ready');
  }
});

byId('create-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const result = await api('/api/action', {
      method: 'POST',
      body: JSON.stringify({
        action: 'create',
        name: byId('project-name').value,
        template: byId('template').value,
      }),
    });
    writeActivity(result);
    byId('project-name').value = '';
    await refreshProjects();
  } catch (error) {
    writeActivity(error.message);
  }
});

byId('refresh').addEventListener('click', () => refreshProjects().catch((error) => writeActivity(error.message)));
byId('clear').addEventListener('click', () => writeActivity('No workbench actions yet.'));
if (byId('token').value) byId('connect').click();
