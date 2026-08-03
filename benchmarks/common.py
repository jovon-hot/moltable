#!/usr/bin/env python3
"""Moltable benchmark shared helpers — pure Python stdlib (urllib only).

Each benchmark script is standalone-runnable: `python3 <benchmark>.py`.
Configuration via env vars:
  MOLTABLE_API        base URL of the Moltable server (default http://127.0.0.1:8700)
  MOLTABLE_EMBED_MODEL  (informational — set on the SERVER side)
  DEEPSEEK_API_KEY    required by persona_fidelity.py
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = os.getenv("MOLTABLE_API", "http://127.0.0.1:8700")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

PASS = "\u2705"  # ✅
FAIL = "\u274c"  # ❌


def no_proxy_opener():
    """Opener that bypasses HTTP(S)_PROXY (Clash on 127.0.0.1:7890 breaks localhost)."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http_request(method, url, payload=None, headers=None, timeout=30, use_proxy=False):
    """Generic HTTP helper. Returns (status, parsed_json_or_text).

    use_proxy=True → respect env proxies (for external APIs like DeepSeek);
    use_proxy=False → bypass proxies (for localhost Moltable).
    """
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if not use_proxy else urllib.request.build_opener()
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error calling {url}: {e.reason}")


# ── Moltable REST ─────────────────────────────────────────────

def health_check(base=DEFAULT_BASE, timeout=5):
    try:
        status, body = http_request("GET", base.rstrip("/") + "/health", timeout=timeout)
        return status == 200
    except Exception:
        return False


def register_user(base=DEFAULT_BASE, name="Benchmark Agent"):
    """Register a fresh user; returns dict with user_id + API key."""
    ts = int(time.time() * 1000)
    payload = {
        "email": f"bench-{ts}@moltable-bench.local",
        "password": "Benchmark2026!!",
        "name": name,
    }
    status, data = http_request("POST", base.rstrip("/") + "/api/auth/register", payload)
    if status != 200:
        raise RuntimeError(f"Register failed ({status}): {data}")
    if not data.get("key"):
        raise RuntimeError(f"Register response missing API key: {data}")
    return data


def rest_request(base, api_key, method, path, payload=None, timeout=30):
    url = base.rstrip("/") + path
    hdrs = {"X-API-Key": api_key}
    status, data = http_request(method, url, payload, headers=hdrs, timeout=timeout)
    return status, data


# ── Moltable MCP (JSON-RPC 2.0, tools/call wrapper) ───────────

def mcp_call(base, api_key, tool, arguments=None, req_id=1, timeout=60):
    """Call an MCP tool via the tools/call wrapper.

    Returns the parsed tool payload (already unwrapped from
    result.content[0].text). Raises RuntimeError on JSON-RPC error.
    """
    body = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments or {}},
    }
    status, data = http_request(
        "POST", base.rstrip("/") + "/mcp", body,
        headers={"X-API-Key": api_key}, timeout=timeout,
    )
    if isinstance(data, dict) and "error" in data and isinstance(data["error"], dict):
        err = data["error"]
        raise RuntimeError(f"MCP {tool} error ({err.get('code')}): {err.get('message')}")
    if not isinstance(data, dict) or "result" not in data:
        raise RuntimeError(f"MCP {tool} unexpected response: {str(data)[:200]}")
    result = data.get("result", {}) if isinstance(data, dict) else {}
    content = result.get("content") or []
    text = ""
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            text += c.get("text", "")
    try:
        return json.loads(text) if text.strip() else {}
    except Exception:
        return {"raw": text}


def mcp_save_memory(base, api_key, content, category, force=False, tags=None, req_id=1, timeout=60):
    """Save one memory via MCP; auto-retries with force=true on conflict."""
    args = {"content": content, "category": category, "source": "benchmark"}
    if tags:
        args["tags"] = tags
    if force:
        args["force"] = True
    resp = mcp_call(base, api_key, "save_memory", args, req_id=req_id, timeout=timeout)
    if not resp.get("saved") and resp.get("conflict"):
        resp = mcp_call(base, api_key, "save_memory", {**args, "force": True},
                        req_id=req_id, timeout=timeout)
        return resp, True  # (response, conflict_occurred)
    return resp, False


# ── Output helpers ────────────────────────────────────────────

def write_result(benchmark, payload):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"{benchmark}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  📄 结果已写入 {path}")
    return path


def banner(title):
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64)


def require_server(base=DEFAULT_BASE):
    if not health_check(base):
        sys.stderr.write(
            f"\n{FAIL} 无法连接 Moltable 服务 {base}\n"
            "   请先启动服务器，例如:\n"
            "     cd ~/Desktop/moltable\\ v2/server && \\\n"
            "     SUPABASE_URL= SUPABASE_SERVICE_ROLE_KEY= SUPABASE_ANON_KEY= SUPABASE_JWT_SECRET= \\\n"
            "     MOLTABLE_EMBED_MODEL=paraphrase-multilingual-MiniLM-L12-v2 ./venv311/bin/python main.py\n"
        )
        sys.exit(1)


def check(cond, label, detail=""):
    mark = PASS if cond else FAIL
    line = f"  {mark} {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return bool(cond)


# ── Number counting (persona fidelity objective metric) ───────

_NUM_RE = re.compile(r"\d+(?:[.,]\d+)?%?")


def count_numbers(text: str) -> int:
    """Count numeric references: Arabic digit groups (+ % / decimals).

    Each standalone digit group counts once (e.g. "87%、92%、15%" → 3).
    """
    if not text:
        return 0
    return len(_NUM_RE.findall(text))
