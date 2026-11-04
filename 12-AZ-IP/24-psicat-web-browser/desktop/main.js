const diagnostics = require('./lib/startup-diagnostics').createStartupDiagnostics();

diagnostics.mark('entry');
try {
  require('./runtime');
} catch (error) {
  diagnostics.failure(error).finally(() => {
    // No asynchronous sidecar startup has run if loading the runtime throws.
    const { app } = require('electron');
    app.exit(1);
  });
}
