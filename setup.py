#!/usr/bin/env python3
"""
Moltable 一键接入脚本
注册 → 获取 API Key → 生成 MCP 配置 → 输出粘贴即可用的命令

用法:
  curl -sL https://moltable.ai/setup.py | python3 -
  或
  python3 setup.py --email=me@example.com --name=MyName
"""

import json, os, sys, secrets, urllib.request, urllib.error, argparse, textwrap

API_BASE = os.environ.get("MOLTABLE_API", "https://moltable-production-15ad.up.railway.app")

def api(method, path, body=None):
    req = urllib.request.Request(f"{API_BASE}{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
        raise SystemExit(f"  ❌ {data.get('detail', str(e))}")

# ── Banner ──────────────────────────────────────────────
print()
print("  ╭──────────────────────────────────────────╮")
print("  │   🧬  Moltable — AI Identity Layer        │")
print("  │   你的 AI 不用每次都重新认识你了         │")
print("  ╰──────────────────────────────────────────╯")
print()

# ── Step 1: 获取用户信息 ─────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--email", help="你的邮箱")
parser.add_argument("--name", help="你的名字（可选）")
parser.add_argument("--existing", help="已有账号？直接用 API Key", dest="api_key")
args = parser.parse_args()

if args.api_key:
    api_key = args.api_key
    print("  使用已有 API Key")
else:
    email = args.email
    if not email:
        email = input("  邮箱: ").strip()
    if not email:
        raise SystemExit("  邮箱不能为空")
    
    name = args.name or input("  名字 (可选, 回车跳过): ").strip()
    password = secrets.token_urlsafe(6)
    
    # 先尝试注册
    print(f"\n  ⏳ 注册中...")
    status, data = api("POST", "/api/auth/register", {
        "email": email, "password": password, "name": name or email.split("@")[0]
    })
    
    if status != 200:
        # 可能已注册，尝试登录
        print(f"  账号可能已存在，尝试登录...")
        pw = input(f"  请输入 {email} 的密码: ").strip()
        status, data = api("POST", "/api/auth/login", {"email": email, "password": pw})
        if status != 200:
            raise SystemExit(f"  登录失败: {data.get('detail','未知错误')}")
        api_key = data.get("session_token")
        if not api_key:
            raise SystemExit("  登录成功但未返回 session token，请使用 API Key 方式：--existing=molt_xxx")
    else:
        api_key = data.get("key")
        print(f"\n  ✅ 注册成功！")
        print(f"  ├─ User ID:  {data['user_id'][:12]}...")
        print(f"  ├─ API Key:  {api_key}")
        print(f"  └─ ⚠️  上面这行是你的 API Key，只显示一次，请保存好！")
        print(f"      密码: {password} (自动生成，可在 Dashboard 修改)")

# ── Step 2: 测试连通性 ──────────────────────────────────
print(f"\n  ⏳ 测试连接...")

req = urllib.request.Request(f"{API_BASE}/mcp",
    data=json.dumps({"jsonrpc":"2.0","id":1,"method":"ping"}).encode(),
    headers={"Content-Type":"application/json","X-API-Key":api_key},
    method="POST")
with urllib.request.urlopen(req, timeout=15) as r:
    ping = json.loads(r.read())
    print(f"  ✅ 连接成功 (ping: {ping['result']['status']})")

# 获取工具列表
req = urllib.request.Request(f"{API_BASE}/mcp",
    data=json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}).encode(),
    headers={"Content-Type":"application/json","X-API-Key":api_key},
    method="POST")
with urllib.request.urlopen(req, timeout=15) as r:
    tools = json.loads(r.read())
    tool_names = [t["name"] for t in tools["result"]["tools"]]
    print(f"  ├─ {len(tool_names)} 个工具可用")
    print(f"  └─ {', '.join(tool_names[:6])}...")

# ── Step 3: 生成 MCP 配置 ──────────────────────────────────
MCP_CONFIG = {
    "mcpServers": {
        "moltable": {
            "type": "http",
            "url": f"{API_BASE}/mcp",
            "headers": {
                "X-API-Key": api_key
            },
            "description": "Moltable — AI Identity & Memory Layer"
        }
    }
}

config_json = json.dumps(MCP_CONFIG, indent=2, ensure_ascii=False)

print()
print("  ═══════════════════════════════════════════")
print("  📋  MCP 配置已生成，粘贴到对应位置即可：")
print("  ═══════════════════════════════════════════")
print()

# Hermes
hermes_path = os.path.expanduser("~/.hermes/mcp.json")
print(f"  ┌─ Hermes Agent ──────────────────────────")
print(f"  │  文件: {hermes_path}")
print(f"  │  已生成: {'✅ 自动写入' if False else '✏️  请手动复制'}")
print(f"  └─────────────────────────────────────────")
print()

# Claude Code
print(f"  ┌─ Claude Code ───────────────────────────")
claude_path = os.path.expanduser("~/.claude/mcp.json")
print(f"  │  文件: {claude_path}")
print(f"  │  格式: MCP JSON (同下)")
print(f"  └─────────────────────────────────────────")
print()

# Cursor
print(f"  ┌─ Cursor / Cline / Copilot ──────────────")
print(f"  │  格式: MCP JSON (同下)")
print(f"  └─────────────────────────────────────────")
print()

print(f"  ┌─ 通用 MCP JSON 配置 ────────────────────")
print(f"  │")
for line in config_json.split("\n"):
    print(f"  │  {line}")
print(f"  │")
print(f"  └─────────────────────────────────────────")
print()

# ── Step 4: 自动写入 Hermes（如果目录存在） ────────
if os.path.isdir(os.path.expanduser("~/.hermes")):
    try:
        # 读取已有配置
        existing = {}
        if os.path.exists(hermes_path):
            with open(hermes_path) as f:
                existing = json.load(f)
        
        # 合并 moltable 配置
        if "mcpServers" not in existing:
            existing["mcpServers"] = {}
        existing["mcpServers"]["moltable"] = MCP_CONFIG["mcpServers"]["moltable"]
        
        with open(hermes_path, "w") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print(f"  ✅ 已自动写入 Hermes 配置 → {hermes_path}")
        print(f"     现在在 Hermes 中说: search_memory 查询\"我的偏好\"")
        print()
    except Exception as e:
        print(f"  ⚠️  无法自动写入: {e}")
        print(f"     请手动将上面的 JSON 复制到 {hermes_path}")
        print()

print("  🎉 完成！你的 AI 从现在开始会记住你是谁。")
print()
