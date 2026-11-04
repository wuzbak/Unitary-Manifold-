const { spawn } = require('node:child_process');
const net = require('node:net');
const path = require('node:path');
const fs = require('node:fs');
const { setTimeout: delay } = require('node:timers/promises');
const { pythonFailure } = require('./component-diagnostics');

function pythonCommand(env = process.env, platform = process.platform) {
  const executable = env.PSICAT_BROWSER_PYTHON;
  if (executable) {
    const paths = platform === 'win32' ? path.win32 : path;
    if (!paths.isAbsolute(executable)) throw new Error('PSICAT_BROWSER_PYTHON must be an absolute executable path (without quotes or arguments).');
    return { executable, args: [] };
  }
  return platform === 'win32'
    ? { executable: 'py', args: ['-3'] }
    : { executable: 'python3', args: [] };
}

function navigatorEnvironment(env = process.env, repoRoot) {
  const result = { ...env };
  // A browser-owned Navigator must not inherit another suite service's authority.
  delete result.PSICAT_LOCAL_EXECUTION_TOKEN;
  delete result.MERLIN_PROFILE_SHARED_KEY;
  delete result.MERLIN_SESSION_SECRET;
  if (repoRoot) {
    if (!path.isAbsolute(repoRoot)) throw new Error('Navigator repository source root must be absolute.');
    result.PYTHONPATH = repoRoot;
  }
  return result;
}

function checkPortAvailable(port, signal) {
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(signal.reason);
    const server = net.createServer();
    server.once('error', () => reject(new Error(`Loopback port ${port} is unavailable; no existing service was adopted.`)));
    server.listen({ host: '127.0.0.1', port, exclusive: true }, () => {
      server.close(() => signal.aborted ? reject(signal.reason) : resolve());
    });
  });
}

class Sidecar {
  constructor({ name, script, args = [], port, healthPath, validateHealth, env = process.env,
    onChange = () => {}, timeoutMs = 10_000, probeTimeoutMs = 750, pollMs = 250,
    stopTimeoutMs = 1500, spawnImpl = spawn, fetchImpl = fetch, checkPort = checkPortAvailable }) {
    Object.assign(this, { name, script, args, port, healthPath, validateHealth, env, onChange,
      timeoutMs, probeTimeoutMs, pollMs, stopTimeoutMs, spawnImpl, fetchImpl, checkPort });
    this.state = { status: 'not_started', pid: null, baseUrl: `http://127.0.0.1:${port}`, error: '' };
    this.child = null;
    this.starting = null;
    this.stopping = null;
  }

  update(patch) {
    this.state = { ...this.state, ...patch };
    this.onChange(this.state);
  }

  start({ enabled = true } = {}) {
    if (this.stopping) return this.stopping.then(() => this.start({ enabled }));
    if (this.starting) return this.starting;
    if (this.child) return Promise.resolve(this.state);
    if (!enabled) {
      this.update({ status: 'disabled', error: '' });
      return Promise.resolve(this.state);
    }
    this.controller = new AbortController();
    this.starting = this.startOwned(this.controller.signal).finally(() => { this.starting = null; });
    return this.starting;
  }

  async startOwned(signal) {
    this.update({ status: 'starting', pid: null, error: '', failure_code: 'UNKNOWN',
      exit_code: null, exit_signal: null, spawn_code: null, python_error: null, missing_module: null, missing_resource: null,
      health_http_status: null, health_payload_valid: null });
    let stage = 'entry';
    try {
      if (!fs.existsSync(this.script)) throw new Error(`${this.name} entry point not found: ${this.script}`);
      stage = 'python';
      const command = pythonCommand(this.env);
      stage = 'port';
      await this.checkPort(this.port, signal);
      signal.throwIfAborted();
      stage = 'spawn';
      const child = this.spawnImpl(command.executable, [
        ...command.args, '-u', this.script, '--host', '127.0.0.1', '--port', String(this.port), ...this.args,
      ], {
        cwd: path.dirname(this.script), env: this.env, stdio: ['ignore', 'ignore', 'pipe'],
        shell: false, detached: false, windowsHide: true,
      });
      this.child = child;
      let diagnosticTail = '';
      child.stderr?.on('data', (chunk) => {
        // Drain stderr, retain only a bounded parser window, never publish raw Python output.
        diagnosticTail = `${diagnosticTail}${chunk.toString('utf8')}`.slice(-8192);
        this.update(pythonFailure(diagnosticTail));
      });
      this.closed = new Promise((resolve) => child.once('close', resolve));
      child.on('error', (error) => {
        this.update({ status: 'failed', failure_code: 'SPAWN_ERROR', spawn_code: error.code,
          error: `${this.name} could not start (${error.code || 'spawn error'}). Check the Python executable and dependencies.` });
        this.controller.abort();
      });
      child.once('exit', (code, exitSignal) => {
        if (!['stopping', 'failed'].includes(this.state.status)) {
          this.update({ status: 'failed', pid: null, failure_code: 'PROCESS_EXIT', exit_code: code,
            exit_signal: exitSignal, error: `${this.name} exited (${exitSignal || code}); check its Python dependencies and port.` });
          this.controller.abort();
        } else this.update({ pid: null });
      });
      child.once('close', () => {
        if (this.child === child) this.child = null;
      });
      this.update({ pid: child.pid || null });
      stage = 'health';
      const deadline = AbortSignal.timeout(this.timeoutMs);
      const startupSignal = AbortSignal.any([signal, deadline]);
      while (!startupSignal.aborted) {
        try {
          const response = await this.fetchImpl(`${this.state.baseUrl}${this.healthPath}`, {
            signal: AbortSignal.any([startupSignal, AbortSignal.timeout(this.probeTimeoutMs)]),
            redirect: 'error',
          });
          const payload = response.ok ? await response.json() : null;
          const valid = Boolean(payload && this.validateHealth(payload));
          this.update({ health_http_status: response.status, health_payload_valid: valid });
          if (valid && !startupSignal.aborted && this.child === child
            && child.exitCode === null && child.signalCode === null) {
            this.update({ status: 'ready', error: '' });
            return this.state;
          }
        } catch (_error) {
          // A bounded retry includes the response body, not just the headers.
        }
        await delay(this.pollMs, undefined, { signal: startupSignal });
      }
      throw new Error(`${this.name} readiness timed out.`);
    } catch (error) {
      if (!['failed', 'stopping'].includes(this.state.status)) {
        this.update({ status: 'failed',
          failure_code: signal.aborted ? 'START_CANCELLED' : ({
            entry: 'ENTRY_NOT_FOUND', python: 'INVALID_PYTHON', port: 'PORT_UNAVAILABLE',
            spawn: 'SPAWN_ERROR', health: 'HEALTH_TIMEOUT',
          }[stage] || 'START_ERROR'),
          error: signal.aborted ? `${this.name} startup cancelled.` : `${this.name} startup failed: ${error.name === 'AbortError' || error.name === 'TimeoutError' ? 'health-check deadline exceeded' : error.message}` });
      }
      await this.terminateChild();
      return this.state;
    }
  }

  async terminateChild() {
    const child = this.child;
    if (!child) return;
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGTERM');
    let timer;
    try {
      const closed = await Promise.race([
        this.closed.then(() => true),
        new Promise((resolve) => { timer = setTimeout(() => resolve(false), this.stopTimeoutMs); }),
      ]);
      if (!closed) {
        child.kill('SIGKILL');
        let finalTimer;
        try {
          const killed = await Promise.race([
            this.closed.then(() => true),
            new Promise((resolve) => { finalTimer = setTimeout(() => resolve(false), this.stopTimeoutMs); }),
          ]);
          if (!killed) throw new Error(`${this.name} child process ${child.pid} did not stop.`);
        } finally {
          clearTimeout(finalTimer);
        }
      }
    } finally {
      clearTimeout(timer);
    }
  }

  stop() {
    if (this.stopping) return this.stopping;
    this.update({ status: 'stopping' });
    this.controller?.abort();
    this.stopping = (async () => {
      await this.starting;
      await this.terminateChild();
      this.update({ status: 'stopped', pid: null });
    })().catch((error) => {
      this.update({ status: 'failed', error: error.message });
      throw error;
    }).finally(() => { this.stopping = null; });
    return this.stopping;
  }
}

module.exports = { Sidecar, pythonCommand, navigatorEnvironment };
