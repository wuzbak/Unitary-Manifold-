const FAILURE_CODES = new Set([
  'ENTRY_NOT_FOUND', 'INVALID_PYTHON', 'PORT_UNAVAILABLE', 'SPAWN_ERROR',
  'PROCESS_EXIT', 'HEALTH_TIMEOUT', 'START_CANCELLED', 'START_ERROR',
  'UI_LOAD_FAILED', 'NOT_READY', 'UNKNOWN',
]);
const MISSING_MODULES = new Set([
  'numpy', 'scipy', 'sympy', 'httpx', 'src', 'src.infrastructure',
  'src.infrastructure.execution_spine', 'ox_navigator',
  'bot', 'bot.rag_index', 'bot.session_bootstrap', 'bot.research_resources',
]);
const RESOURCES = new Set([
  'run.py', 'ox_navigator/app/server.py', 'ox_navigator/engine/merlin_benchmark.py',
  'src/infrastructure/execution_spine.py', '9-INFRASTRUCTURE/ox_full_context.md',
  'sync_backend/server.py', 'desktop/ui/index.html', 'desktop/ui/app.js', 'desktop/ui/app.css',
  'bot/assistant_api.py', 'bot/rag_index.py',
  'bot/__init__.py', 'bot/session_bootstrap.py', 'bot/research_resources.py',
  'ui/interrogator-kb.json',
]);

function pythonFailure(stderr) {
  const missing = /ModuleNotFoundError: No module named ['"]([^'"\r\n]+)['"]/.exec(stderr);
  if (missing) return {
    python_error: 'MODULE_NOT_FOUND',
    missing_module: MISSING_MODULES.has(missing[1]) ? missing[1] : 'other',
  };
  for (const [name, code] of [
    ['ImportError', 'IMPORT_ERROR'], ['FileNotFoundError', 'FILE_NOT_FOUND'],
    ['PermissionError', 'PERMISSION_DENIED'], ['SyntaxError', 'SYNTAX_ERROR'],
    ['OSError', 'OS_ERROR'],
  ]) {
    if (new RegExp(`(?:^|\\n)${name}:`).test(stderr)) {
      const missing = name === 'FileNotFoundError'
        ? [...RESOURCES].find((resource) => stderr.replaceAll('\\', '/').includes(`/${resource}`))
        : null;
      return { python_error: code, ...(missing ? { missing_resource: missing } : {}) };
    }
  }
  return {};
}

function componentState(state = {}) {
  const safe = {
    status: ['ready', 'failed', 'starting', 'disabled', 'stopping', 'stopped', 'not_started'].includes(state.status) ? state.status : 'unknown',
    failure_code: FAILURE_CODES.has(state.failure_code) ? state.failure_code : 'UNKNOWN',
  };
  if (Number.isInteger(state.exit_code)) safe.exit_code = state.exit_code;
  if (['SIGTERM', 'SIGKILL', 'SIGINT', 'SIGABRT', 'SIGSEGV'].includes(state.exit_signal)) safe.exit_signal = state.exit_signal;
  if (['ENOENT', 'EACCES', 'EPERM', 'EADDRINUSE', 'EINVAL'].includes(state.spawn_code)) safe.spawn_code = state.spawn_code;
  if (['MODULE_NOT_FOUND', 'IMPORT_ERROR', 'FILE_NOT_FOUND', 'PERMISSION_DENIED', 'SYNTAX_ERROR', 'OS_ERROR'].includes(state.python_error)) safe.python_error = state.python_error;
  if (MISSING_MODULES.has(state.missing_module) || state.missing_module === 'other') safe.missing_module = state.missing_module;
  if (RESOURCES.has(state.missing_resource)) safe.missing_resource = state.missing_resource;
  if (Number.isInteger(state.health_http_status) && state.health_http_status >= 100 && state.health_http_status <= 599) safe.health_http_status = state.health_http_status;
  if (typeof state.health_payload_valid === 'boolean') safe.health_payload_valid = state.health_payload_valid;
  return safe;
}

function safeFailureContext(context = {}) {
  const component = ['sync', 'navigator', 'ui', 'bootstrap'].includes(context.component) ? context.component : 'bootstrap';
  const components = {};
  for (const name of ['ui', 'sync', 'navigator']) {
    if (context.components?.[name]) components[name] = componentState(context.components[name]);
  }
  const resources = (Array.isArray(context.resources) ? context.resources : [])
    .filter((entry) => RESOURCES.has(entry?.resource) && typeof entry.exists === 'boolean')
    .map((entry) => ({ resource: entry.resource, exists: entry.exists }));
  return { component, components, resources };
}

module.exports = { pythonFailure, componentState, safeFailureContext };
