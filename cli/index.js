#!/usr/bin/env node
/**
 * @moltable/connect — One-command Moltable MCP integration.
 *
 *   npx @moltable/connect <platform> --api-key <molt_xxx>
 *
 * Platforms: claude | cursor | hermes
 *
 * What it does:
 *   1. Reads/creates the platform's MCP config file
 *   2. Writes the Moltable MCP server entry (url + X-API-Key header)
 *   3. Backs up the previous config file (if any)
 *   4. Validates the API key against GET /api/auth/me
 *   5. Prints an onboarding guide on success
 *
 * Zero dependencies. Node >= 14. Works offline-ish (--skip-verify).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const http = require('http');
const { spawnSync } = require('child_process');

const VERSION = '0.1.0';

const DEFAULTS = {
  MCP_URL: 'https://api.moltable.ai/mcp',
  API_BASE: 'https://api.moltable.ai',
};

/* ------------------------------------------------------------------ *
 *  Small helpers
 * ------------------------------------------------------------------ */

const isTTY = Boolean(process.stdout.isTTY) && !process.env.NO_COLOR;
const C = {
  reset: isTTY ? '\x1b[0m' : '',
  bold: isTTY ? '\x1b[1m' : '',
  dim: isTTY ? '\x1b[2m' : '',
  red: isTTY ? '\x1b[31m' : '',
  green: isTTY ? '\x1b[32m' : '',
  yellow: isTTY ? '\x1b[33m' : '',
  cyan: isTTY ? '\x1b[36m' : '',
};
const out = (s) => process.stdout.write(s + '\n');
const err = (s) => process.stderr.write(s + '\n');
const info = (s) => out(C.dim + s + C.reset);
const ok = (s) => out(C.green + '✓ ' + C.reset + s);
const fail = (s) => err(C.red + '✗ ' + C.reset + s);
const warn = (s) => out(C.yellow + '⚠ ' + C.reset + s);

function homedir() {
  return os.homedir();
}

/* ------------------------------------------------------------------ *
 *  Platform definitions
 * ------------------------------------------------------------------ */

function claudeConfigPath() {
  if (process.platform === 'darwin') {
    return path.join(homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  }
  if (process.platform === 'win32') {
    const base = process.env.APPDATA || path.join(homedir(), 'AppData', 'Roaming');
    return path.join(base, 'Claude', 'claude_desktop_config.json');
  }
  // linux / others
  return path.join(homedir(), '.config', 'Claude', 'claude_desktop_config.json');
}

const PLATFORMS = {
  claude: {
    label: 'Claude Desktop',
    configPath: claudeConfigPath(),
    kind: 'json',
  },
  cursor: {
    label: 'Cursor',
    configPath: path.join(homedir(), '.cursor', 'mcp.json'),
    kind: 'json',
  },
  hermes: {
    label: 'Hermes',
    configPath: path.join(homedir(), '.hermes', 'config.yaml'),
    kind: 'hermes',
  },
};

/* ------------------------------------------------------------------ *
 *  Arg parsing
 * ------------------------------------------------------------------ */

function usage() {
  out('');
  out(C.bold + 'Moltable Connect ' + VERSION + C.reset + ' — one-command MCP integration');
  out('');
  out('Usage:');
  out(C.cyan + '  npx @moltable/connect <platform> --api-key <molt_xxx>' + C.reset);
  out('');
  out('Platforms:');
  out('  claude    Claude Desktop  -> ~/Library/Application Support/Claude/claude_desktop_config.json');
  out('  cursor    Cursor          -> ~/.cursor/mcp.json');
  out('  hermes    Hermes          -> ~/.hermes/config.yaml (via `hermes config set`)');
  out('');
  out('Options:');
  out('  -k, --api-key <key>   Moltable API key (molt_...) or session token (mol_...)');
  out('      --mcp-url <url>   Override MCP endpoint        (default: ' + DEFAULTS.MCP_URL + ')');
  out('      --api-base <url>  Override API base for key validation');
  out('                        (default: ' + DEFAULTS.API_BASE + ')');
  out('      --config-path <p> Override config file path (testing / unusual setups)');
  out('      --skip-verify     Skip API key validation');
  out('  -h, --help            Show this help');
  out('  -V, --version         Show version');
  out('');
  out('Examples:');
  out('  npx @moltable/connect claude --api-key molt_abc123');
  out('  npx @moltable/connect cursor --api-key molt_abc123');
  out('  npx @moltable/connect hermes --api-key molt_abc123');
  out('');
}

function parseArgs(argv) {
  const a = {
    platform: null,
    apiKey: process.env.MOLTABLE_API_KEY || null,
    mcpUrl: DEFAULTS.MCP_URL,
    apiBase: DEFAULTS.API_BASE,
    configPath: null,
    verify: true,
    help: false,
    version: false,
  };
  const positional = [];
  const take = (i, flag) => {
    if (i + 1 >= argv.length) {
      err(C.red + 'Missing value for ' + flag + C.reset);
      process.exit(1);
    }
    return argv[i + 1];
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case '-h': case '--help': a.help = true; break;
      case '-V': case '--version': a.version = true; break;
      case '-k': case '--api-key': a.apiKey = take(i, arg); i++; break;
      case '--mcp-url': a.mcpUrl = take(i, arg); i++; break;
      case '--api-base': a.apiBase = take(i, arg); i++; break;
      case '--config-path': a.configPath = take(i, arg); i++; break;
      case '--skip-verify': a.verify = false; break;
      default:
        if (arg.startsWith('--api-key=')) a.apiKey = arg.slice('--api-key='.length);
        else if (arg.startsWith('--mcp-url=')) a.mcpUrl = arg.slice('--mcp-url='.length);
        else if (arg.startsWith('--api-base=')) a.apiBase = arg.slice('--api-base='.length);
        else if (arg.startsWith('--config-path=')) a.configPath = arg.slice('--config-path='.length);
        else if (arg.startsWith('-')) {
          err(C.red + 'Unknown option: ' + arg + C.reset);
          usage();
          process.exit(1);
        } else positional.push(arg);
    }
  }
  if (positional.length > 0) a.platform = String(positional[0]).toLowerCase();
  return a;
}

/* ------------------------------------------------------------------ *
 *  API key validation (GET /api/auth/me)
 * ------------------------------------------------------------------ */

function looksLikeKey(key) {
  return (
    typeof key === 'string' &&
    (/^molt_[A-Za-z0-9_-]+$/.test(key) || /^mol_[A-Za-z0-9_-]+$/.test(key))
  );
}

function httpRequest(url, options) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https:') ? https : http;
    const req = lib.request(
      url,
      { method: options.method || 'GET', headers: options.headers || {} },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => resolve({ status: res.statusCode, body }));
      }
    );
    req.on('error', reject);
    req.setTimeout(options.timeout || 15000, () => {
      req.destroy(new Error('Request timed out after ' + (options.timeout || 15000) + 'ms'));
    });
    req.end();
  });
}

async function verifyKey(apiBase, apiKey) {
  const base = String(apiBase).replace(/\/+$/, '');
  const url = base + '/api/auth/me';
  info('Validating API key against ' + url + ' …');
  let res;
  try {
    res = await httpRequest(url, {
      headers: { 'X-API-Key': apiKey, Accept: 'application/json' },
    });
  } catch (e) {
    return { ok: false, error: 'Network error: ' + e.message };
  }
  if (res.status === 200) {
    let user = {};
    try { user = JSON.parse(res.body) || {}; } catch (_) { /* non-JSON body — ignore */ }
    return { ok: true, user };
  }
  let detail = '';
  try {
    const parsed = JSON.parse(res.body);
    detail = parsed.detail || parsed.message || parsed.error || '';
  } catch (_) { /* ignore */ }
  return { ok: false, status: res.status, detail: String(detail || '').trim() };
}

/* ------------------------------------------------------------------ *
 *  Config file operations
 * ------------------------------------------------------------------ */

function backupFile(filePath) {
  if (!fs.existsSync(filePath)) return null;
  const ts = new Date()
    .toISOString()
    .replace(/[:.]/g, '-')
    .replace('T', '_')
    .slice(0, 19);
  const bak = filePath + '.bak-' + ts;
  fs.copyFileSync(filePath, bak);
  return bak;
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return { existed: false, data: {} };
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    throw new Error('Cannot read ' + filePath + ': ' + e.message);
  }
  try {
    const data = JSON.parse(raw);
    return { existed: true, data: data && typeof data === 'object' && !Array.isArray(data) ? data : {} };
  } catch (e) {
    throw new Error(
      filePath + ' is not valid JSON (' + e.message + '). ' +
      'The original file was NOT modified.'
    );
  }
}

function writeJsonMcpConfig(configPath, mcpUrl, apiKey) {
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  const { data } = readJson(configPath);
  if (!data.mcpServers || typeof data.mcpServers !== 'object') data.mcpServers = {};
  data.mcpServers.moltable = {
    type: 'http',
    url: mcpUrl,
    headers: { 'X-API-Key': apiKey },
  };
  fs.writeFileSync(configPath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

/* ------------------------------------------------------------------ *
 *  Hermes — via `hermes config set`
 * ------------------------------------------------------------------ */

function findHermesBinary() {
  const candidates = [];
  (process.env.PATH || '').split(path.delimiter).forEach((dir) => {
    if (dir) candidates.push(path.join(dir, 'hermes'));
  });
  if (process.platform === 'win32') candidates.push(path.join(homedir(), '.hermes', 'hermes.exe'));
  else {
    candidates.push(path.join(homedir(), '.local', 'bin', 'hermes'));
    candidates.push('/usr/local/bin/hermes');
    candidates.push('/opt/homebrew/bin/hermes');
  }
  for (const c of candidates) {
    try {
      fs.accessSync(c, fs.constants.X_OK);
      return c;
    } catch (_) { /* keep looking */ }
  }
  return 'hermes'; // let the shell resolve it; the error will tell us
}

function runHermes(args) {
  const bin = findHermesBinary();
  const res = spawnSync(bin, args, { encoding: 'utf8', timeout: 60000 });
  if (res.error) {
    throw new Error(
      'Failed to run `' + bin + '`: ' + res.error.message +
      '. Is Hermes installed and on PATH? (https://hermes-agent.nousresearch.com)'
    );
  }
  if (res.status !== 0) {
    const detail = (res.stderr || res.stdout || '').trim();
    throw new Error(
      '`' + bin + ' ' + args.join(' ') + '` exited with code ' + res.status +
      (detail ? '\n' + detail : '')
    );
  }
  return (res.stdout || '').trim();
}

function setupHermes(apiKey, mcpUrl, configPath) {
  const steps = [
    ['config', 'set', 'mcp_servers.moltable.url', mcpUrl],
    ['config', 'set', 'mcp_servers.moltable.headers.X-API-Key', apiKey],
  ];
  for (const step of steps) {
    info('$ hermes ' + step.join(' ').replace(apiKey, '••••••'));
    runHermes(step);
  }
  if (configPath && configPath !== PLATFORMS.hermes.configPath && fs.existsSync(configPath)) {
    info('(custom config path ' + configPath + ' — assuming `hermes` is pointed at it)');
  }
}

/* ------------------------------------------------------------------ *
 *  Guides
 * ------------------------------------------------------------------ */

function describeUser(user) {
  if (!user || typeof user !== 'object') return '';
  const name = user.name || user.email || user.plan_name || user.plan || '';
  return name ? ' (' + name + ')' : '';
}

/* ------------------------------------------------------------------ *
 *  Login config + skill install (备份/恢复的产品层)
 * ------------------------------------------------------------------ */

const SKILL_SOURCE_URL =
  'https://raw.githubusercontent.com/jovon-hot/moltable/main/skill/moltable-sync/SKILL.md';

function saveLoginConfig(apiKey) {
  // 一次性登录：把 API key 存到 ~/.moltable/config.json，skill 之后静默读取。
  const dir = path.join(homedir(), '.moltable');
  fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
  const file = path.join(dir, 'config.json');
  const payload = {
    api_key: apiKey,
    saved_at: new Date().toISOString(),
    note: 'Moltable login — 由 moltable-sync skill 自动读取。',
  };
  fs.writeFileSync(file, JSON.stringify(payload, null, 2), { mode: 0o600 });
  return file;
}

async function installSyncSkill() {
  // 下载 moltable-sync skill 到 ~/.hermes/skills/moltable-sync/SKILL.md。
  // 之后用户一句"备份我"/"恢复我"即触发。
  try {
    const skillDir = path.join(homedir(), '.hermes', 'skills', 'moltable-sync');
    const skillFile = path.join(skillDir, 'SKILL.md');
    fs.mkdirSync(skillDir, { recursive: true });
    const res = await httpRequest(SKILL_SOURCE_URL, { method: 'GET' });
    // 严格校验:必须是 200 且 frontmatter 的 name 字段精确匹配 moltable-sync。
    const valid = res.status === 200 && res.body &&
      /^---\s*\nname:\s*moltable-sync\s*\n/.test(res.body);
    if (valid) {
      fs.writeFileSync(skillFile, res.body);
      return true;
    }
    return false;
  } catch (e) {
    // 网络错误等：降级为失败，不向上抛异常（避免误导性 exit(1)）。
    return false;
  }
}

function printGuide(platform, mcpUrl) {
  out('');
  out(C.bold + '🎉 Moltable MCP server configured for ' + PLATFORMS[platform].label + C.reset);
  out('');
  out('  Server name : moltable');
  out('  Endpoint    : ' + mcpUrl);
  out('  Auth        : X-API-Key header');
  out('');

  if (platform === 'claude') {
    out(C.bold + 'Next steps:' + C.reset);
    out('  1. Fully quit Claude Desktop (Cmd+Q) and reopen it.');
    out('  2. Settings (gear) → Developer → MCP Servers → check "moltable" is connected.');
    out('  3. Start a new chat and ask: "用 auto_provision 读取我的身份" or');
    out('     "connect to Moltable and load my identity".');
  } else if (platform === 'cursor') {
    out(C.bold + 'Next steps:' + C.reset);
    out('  1. In Cursor: Settings (Cmd+Shift+P → "Cursor Settings") → MCP.');
    out('  2. The "moltable" server should appear. Toggle it on if needed.');
    out('  3. If it does not appear, restart Cursor and reopen MCP settings.');
    out('  4. Start a chat and ask: "用 auto_provision 读取我的身份".');
  } else if (platform === 'hermes') {
    out(C.bold + 'Next steps:' + C.reset);
    out('  1. Verify: hermes mcp list        (should show moltable enabled)');
    out('  2. Verify: hermes mcp test moltable  (ping OK + 14 tools discovered)');
    out('  3. No restart needed — Hermes auto-reloads MCP servers.');
    out('  4. Start a chat and ask: "用 auto_provision 读取我的身份".');
  }
  out('');
  out(C.dim + 'Tip: switch AI assistants anytime — run this command again with a different platform.' + C.reset);
  out('');
}

/* ------------------------------------------------------------------ *
 *  Main
 * ------------------------------------------------------------------ */

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.version) {
    out(VERSION);
    return;
  }
  if (args.help || !args.platform) {
    usage();
    return;
  }

  const platform = PLATFORMS[args.platform];
  if (!platform) {
    fail('Unknown platform "' + args.platform + '". Supported: claude, cursor, hermes.');
    usage();
    process.exit(1);
  }

  if (!args.apiKey) {
    fail('Missing API key. Pass it with --api-key <molt_xxx> (or set MOLTABLE_API_KEY).');
    usage();
    process.exit(1);
  }
  args.apiKey = String(args.apiKey).trim();
  if (!looksLikeKey(args.apiKey)) {
    fail(
      'API key "' + args.apiKey.slice(0, 8) + '…" does not look like a Moltable key.\n' +
      '  Expected format: molt_<random> (API key) or mol_<random> (session token).'
    );
    process.exit(1);
  }

  const mcpUrl = args.mcpUrl;
  const configPath = args.configPath || platform.configPath;
  info('Target  : ' + PLATFORMS[args.platform].label + ' → ' + configPath);

  // 1. Validate the API key FIRST — never write config for a dead key.
  let user = null;
  if (args.verify) {
    const v = await verifyKey(args.apiBase, args.apiKey);
    if (!v.ok) {
      fail('API key rejected by Moltable' + (v.status ? ' (HTTP ' + v.status + ')' : '') + '.');
      if (v.detail) err('  Server says: ' + v.detail);
      if (v.error) err('  ' + v.error);
      err('  Get a key at https://moltable.ai/dashboard/settings or re-run with --skip-verify to force.');
      process.exit(1);
    }
    user = v.user;
    ok('API key valid' + describeUser(user) + '.');
  } else {
    warn('--skip-verify: skipping API key validation.');
  }

  // 2. Back up the previous config (if any).
  let backup = null;
  if (fs.existsSync(configPath)) {
    backup = backupFile(configPath);
    info('Backed up existing config → ' + backup);
  }

  // 3. Write the Moltable MCP config.
  if (platform.kind === 'hermes') {
    try {
      setupHermes(args.apiKey, mcpUrl, configPath);
    } catch (e) {
      fail('Hermes config update failed.');
      err('  ' + e.message);
      if (backup) err('  Your config backup is at: ' + backup);
      process.exit(1);
    }
  } else {
    try {
      writeJsonMcpConfig(configPath, mcpUrl, args.apiKey);
    } catch (e) {
      fail('Could not write ' + configPath + '.');
      err('  ' + e.message);
      if (backup) err('  Your config backup is at: ' + backup);
      process.exit(1);
    }
  }
  ok('Moltable MCP server written to ' + configPath + '.');

  // 4. Save login config (一次性登录).
  try {
    const cfgFile = saveLoginConfig(args.apiKey);
    ok('Login saved → ' + cfgFile);
  } catch (e) {
    warn('Could not save login config: ' + e.message);
  }

  // 5. Install sync skill (Hermes 独有:备份/恢复一句话触发).
  if (platform.kind === 'hermes') {
    const installed = await installSyncSkill();
    if (installed) {
      ok('同步 skill 已安装 → ~/.hermes/skills/moltable-sync/');
      out(C.dim + '  以后一句话触发:"备份我" / "恢复我" + 同步码。' + C.reset);
    } else {
      warn('同步 skill 下载失败(网络?)— 不影响 MCP 连接,可稍后重试。');
    }
  }

  // 6. Guide.
  printGuide(args.platform, mcpUrl);
}

main().catch((e) => {
  fail('Unexpected error: ' + (e && e.stack ? e.stack : e));
  process.exit(1);
});
