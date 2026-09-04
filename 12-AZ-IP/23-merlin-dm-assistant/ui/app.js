async function loadSummary() {
  const output = document.getElementById('output');
  output.textContent = 'Loading…';
  try {
    const response = await fetch('/api/health');
    const payload = await response.json();
    output.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    output.textContent = `Unable to reach local API: ${error}`;
  }
}

document.getElementById('load-demo')?.addEventListener('click', loadSummary);
