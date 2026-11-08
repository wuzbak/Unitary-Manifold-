// Firebase serves a bundled snapshot; it does not provide /api/status.
function loadBundledStatus(url, fields) {
  return fetch(url).then(function(response) {
    if (!response.ok) throw new Error('status snapshot unavailable');
    return response.json();
  }).then(function(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('invalid status snapshot');
    Object.keys(fields).forEach(function(key) {
      var value = data[key];
      var valid = (typeof value === 'number' && Number.isFinite(value) && value >= 0) ||
                  (typeof value === 'string' && value.trim() !== '');
      fields[key].forEach(function(id) {
        document.getElementById(id).textContent = valid ? value.toLocaleString() : 'Unavailable';
      });
    });
    document.getElementById('status-source').textContent =
      'Bundled historical snapshot: ' + url + ' · date: ' + (data.date || 'unknown');
  }).catch(function() {
    Object.keys(fields).forEach(function(key) {
      fields[key].forEach(function(id) { document.getElementById(id).textContent = 'Unavailable'; });
    });
    document.getElementById('status-source').textContent = 'Status snapshot unavailable.';
  });
}
