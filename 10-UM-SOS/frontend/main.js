const apiBase = '/api/v1';

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status}: ${url}`);
  return r.json();
}

async function loadPredictions() {
  let data;
  try {
    data = await getJSON(`${apiBase}/predictions/all`);
  } catch {
    const reg = await getJSON('../registry/predictions.json');
    data = { predictions: (reg.entries || []).map(e => ({
      id: `P${e.pillar}`,
      quantity: e.prediction_summary,
      predicted_value: '-',
      units: '-',
      experiment: e.experiment,
      current_status: e.status,
      epistemic_label: 'DERIVED',
    })) };
  }
  const rows = data.predictions || [];
  const tbody = document.querySelector('#pred-table tbody');
  tbody.innerHTML = '';
  for (const p of rows) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${p.id}</td><td>${p.quantity || ''}</td><td>${p.predicted_value ?? ''} ${p.units || ''}</td><td>${p.experiment || ''}</td><td>${p.current_status || p.status || ''}</td><td>${p.epistemic_label || ''}</td>`;
    tbody.appendChild(tr);
  }

  const search = document.getElementById('search');
  search.addEventListener('input', () => {
    const q = search.value.toLowerCase();
    for (const tr of tbody.querySelectorAll('tr')) {
      tr.style.display = tr.innerText.toLowerCase().includes(q) ? '' : 'none';
    }
  });

  // Export visible rows as CSV
  document.getElementById('export-btn').addEventListener('click', () => {
    const headers = ['ID', 'Quantity', 'Predicted', 'Experiment', 'Status', 'Label'];
    const visibleRows = [...tbody.querySelectorAll('tr')].filter(tr => tr.style.display !== 'none');
    const csvRows = [headers.join(','), ...visibleRows.map(tr =>
      [...tr.querySelectorAll('td')].map(td => `"${td.innerText.replace(/"/g, '""')}"`).join(',')
    )];
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'um-sos-predictions.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  });
}

async function loadAdmissions() {
  let data;
  try {
    data = await getJSON(`${apiBase}/gaps`);
  } catch {
    const reg = await getJSON('../registry/predictions.json');
    data = { admissions: reg.admissions || [] };
  }
  const ul = document.getElementById('admissions');
  ul.innerHTML = '';
  for (const a of data.admissions || []) {
    const li = document.createElement('li');
    li.textContent = `${a.name} — ${a.status}`;
    ul.appendChild(li);
  }
}

function setupGovernance() {
  const out = document.getElementById('gov-out');

  document.getElementById('gov-run').addEventListener('click', async () => {
    const text = document.getElementById('gov-input').value;
    try {
      const r = await fetch(`${apiBase}/governance/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      out.textContent = JSON.stringify(await r.json(), null, 2);
    } catch {
      out.textContent = JSON.stringify({ lane: 'SENSITIVE', note: 'API unavailable in static mode' }, null, 2);
    }
  });

  document.getElementById('gov-clear').addEventListener('click', () => {
    document.getElementById('gov-input').value = '';
    out.textContent = '';
  });
}

loadPredictions();
loadAdmissions();
setupGovernance();
