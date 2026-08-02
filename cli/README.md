# @moltable/connect

One-command Moltable MCP integration for **Claude Desktop**, **Cursor**, and **Hermes**.
No manual JSON editing. Zero dependencies. Node >= 14.

```bash
npx @moltable/connect claude --api-key molt_xxx
npx @moltable/connect cursor --api-key molt_xxx
npx @moltable/connect hermes --api-key molt_xxx
```

## What it does

1. Reads/creates the platform's MCP config file
2. Writes the Moltable MCP server entry (`url` + `X-API-Key` header)
3. Backs up the previous config file (e.g. `claude_desktop_config.json.bak-2026-08-03_10-00-00`)
4. Validates your API key against `GET /api/auth/me` — refuses to write a dead key
5. Prints the onboarding guide for your platform

## Platform config paths

| Platform | Config file |
|----------|-------------|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Linux) | `~/.config/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Hermes | `~/.hermes/config.yaml` — written via `hermes config set mcp_servers.moltable.*` |

## Options

```
-k, --api-key <key>   Moltable API key (molt_...) or session token (mol_...)
    --mcp-url <url>   Override MCP endpoint          (default: https://api.moltable.ai/mcp)
    --api-base <url>  Override API base for validation (default: https://api.moltable.ai)
    --config-path <p> Override config file path (testing / unusual setups)
    --skip-verify     Skip API key validation
-h, --help            Show help
-V, --version         Show version
```

`MOLTABLE_API_KEY` env var is used as a fallback when `--api-key` is omitted.

## Self-hosted / custom endpoint

```bash
npx @moltable/connect claude --api-key molt_xxx \
  --mcp-url http://localhost:8642/mcp \
  --api-base http://localhost:8642
```

## What gets written

Claude Desktop / Cursor (`mcpServers` merged into the existing file):

```json
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "https://api.moltable.ai/mcp",
      "headers": { "X-API-Key": "molt_xxx" }
    }
  }
}
```

Hermes (equivalent of):

```bash
hermes config set mcp_servers.moltable.url "https://api.moltable.ai/mcp"
hermes config set mcp_servers.moltable.headers.X-API-Key "molt_xxx"
```

## Safety

- The API key is validated **before** anything is written — a rejected key never touches your config.
- Existing configs are backed up with a timestamp suffix before being modified.
- If your config file is invalid JSON, the tool refuses to touch it (no silent overwrite).

## Development

```bash
cd cli
node index.js --help
node index.js cursor --api-key molt_test_123 --skip-verify --config-path /tmp/test-mcp.json
npm pack          # produce tarball for publishing
npm publish       # publish to npm registry (run from repo root: npm publish cli/)
```
