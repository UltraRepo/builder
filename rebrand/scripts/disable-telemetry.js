#!/usr/bin/env node
// disable-telemetry.js
// Patches Kilo Code extension to disable telemetry by default and prevent enabling it at runtime.
// Usage: node disable-telemetry.js <kilocode-root>

const fs = require('fs');
const path = require('path');

if (process.argv.length < 3) {
  console.error('Usage: node disable-telemetry.js <kilocode-root>');
  process.exit(1);
}

const root = process.argv[2];
const extFile = path.join(root, 'src', 'extension.ts');
const webviewHandler = path.join(root, 'src', 'core', 'webview', 'webviewMessageHandler.ts');

function patchFile(file, search, replace, description) {
  let content = fs.readFileSync(file, 'utf8');
  if (!content.includes(search)) {
    console.warn(`[WARN] Pattern not found in ${file}: ${description}`);
    return;
  }
  content = content.replace(search, replace);
  fs.writeFileSync(file, content, 'utf8');
  console.log(`[OK] Patched ${file}: ${description}`);
}

// 1. Force telemetrySetting to 'disabled' on first install
patchFile(
  extFile,
  'await context.globalState.update("telemetrySetting", "enabled")',
  'await context.globalState.update("telemetrySetting", "disabled")',
  'Set telemetrySetting to disabled by default'
);

// 2. Prevent enabling telemetry at runtime in webview handler
patchFile(
  webviewHandler,
  'const isOptedIn = telemetrySetting === "enabled"',
  'const isOptedIn = false // forcibly disable telemetry',
  'Force isOptedIn to false (telemetry always disabled)'
);

console.log('Telemetry has been disabled. Rebuild the extension for changes to take effect.');
