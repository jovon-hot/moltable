#!/usr/bin/env python3
"""moltable backup — Agent 灵魂资产打包上传/下载（P1: Hermes adapter）。

用法：
  moltable backup sources                列出备份源
  moltable backup push [--name X]       扫描灵魂资产 → 增量上传快照
  moltable backup pull [--version N]     下载快照 → 还原到工作区
  moltable backup init                   生成 ~/.moltable/backup.json 配置

环境变量：
  MOLTABLE_API   后端地址（默认 https://api.moltable.ai）
  MOLTABLE_KEY   API Key（也可写入 ~/.moltable/backup.json 的 api_key 字段）

纯 stdlib，无第三方依赖，可 curl 下载即用。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

from hermes_adapter import (
    build_manifest,
    collect_files,
    default_config,
    load_config,
)

DEFAULT_API = os.getenv("MOLTABLE_API", "https://api.moltable.ai")


def _api_key(config: dict) -> str:
    key = os.getenv("MOLTABLE_KEY") or config.get("api_key") or ""
    if not key:
        print("❌ 缺少 API Key。设置 MOLTABLE_KEY 环境变量，或在 ~/.moltable/backup.json 写 api_key 字段。")
        sys.exit(1)
    return key


def _request(path: str, config: dict, payload: dict | None = None, method: str = "POST") -> dict:
    """调用后端 API，返回 JSON。"""
    api = config.get("api") or DEFAULT_API
    url = f"{api}/api/backup/{path}"
    key = _api_key(config)
    data = json.dumps(payload or {}).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"❌ HTTP {e.code}: {body[:300]}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        sys.exit(1)


def cmd_sources(config: dict) -> None:
    result = _request("sources", config, method="GET")
    sources = result.get("sources", [])
    if not sources:
        print("（暂无备份源。先执行 push 会自动创建，或用 init 初始化。）")
        return
    print(f"{'名称':<24} {'类型':<14} {'最新版本':<8}")
    for s in sources:
        print(f"{s.get('name',''):<24} {s.get('agent_type',''):<14} v{s.get('latest_version',0)}")


def cmd_push(config: dict, name: str | None, source_id: str | None) -> None:
    # 1. 收集文件
    files = collect_files(config)
    if not files:
        print("⚠  没有可备份的文件。检查 ~/.moltable/backup.json 的 workspace 配置。")
        sys.exit(1)
    manifest = build_manifest(files)

    # 2. 确定 source_id（有则用，无则查/建）
    if not source_id:
        source_id = _resolve_source(config, name)
        if not source_id:
            src = _request("sources", config, {
                "agent_type": config.get("agent_type", "hermes"),
                "name": name or config.get("name", "default"),
            })
            source_id = src["id"]

    # 3. 拿服务端最新 manifest，diff 出变化文件
    server = _request("manifest", config, {"source_id": source_id})
    server_manifest = server.get("manifest", {})
    server_version = server.get("version", 0)

    changed_blobs = {}
    for path, h in manifest.items():
        if server_manifest.get(path) != h:
            changed_blobs[h] = files[path]

    # 4. push（blobs 转 base64）
    blobs_b64 = {h: base64.b64encode(d).decode() for h, d in changed_blobs.items()}
    result = _request("push", config, {
        "source_id": source_id,
        "manifest": manifest,
        "blobs": blobs_b64,
    })

    total = len(manifest)
    changed = len(changed_blobs)
    print(f"✅ 快照 v{result['version']} 已上传")
    print(f"   文件总数 {total}，变化 {changed}，新增 blob {result['stored_blobs']}，复用 {result['skipped_blobs']}")
    if server_version > 0 and changed == 0:
        print(f"   （与 v{server_version} 无差异，已生成新版本点）")


def cmd_pull(config: dict, source_id: str | None, version: int | None, name: str | None) -> None:
    if not source_id:
        source_id = _resolve_source(config, name)
        if not source_id:
            print("❌ 找不到备份源。先 push 一次，或用 --source-id 指定。")
            sys.exit(1)

    result = _request("pull", config, {"source_id": source_id, "version": version})
    if result.get("version", 0) == 0:
        print("（空备份源，无可还原内容。）")
        return

    manifest = result.get("manifest", {})
    blobs = result.get("blobs", {})
    workspace = os.path.expanduser(config.get("workspace") or "~/.hermes")

    restored = 0
    for path, h in manifest.items():
        b64 = blobs.get(h)
        if b64 is None:
            print(f"⚠  缺少 blob {h}（{path}），跳过")
            continue
        data = base64.b64decode(b64)
        target = _resolve_target(workspace, config, path)
        if target is None:
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)
        restored += 1

    print(f"✅ 已还原 v{result['version']}，共 {restored} 个文件 → {workspace}")


def _resolve_source(config: dict, name: str | None) -> str | None:
    result = _request("sources", config, method="GET")
    sources = result.get("sources", [])
    want = name or config.get("name", "default")
    for s in sources:
        if s.get("name") == want or s.get("id") == want:
            return s["id"]
    # 只有一个 source 时默认返回它
    if len(sources) == 1:
        return sources[0]["id"]
    return None


def _resolve_target(workspace: str, config: dict, path: str) -> str | None:
    """把 manifest 逻辑路径还原成真实路径。self/ → workspace，refs/逻辑名 → 用户声明路径。"""
    if path.startswith("self/"):
        return os.path.join(workspace, path[len("self/"):])
    if path.startswith("refs/"):
        rest = path[len("refs/"):]
        logical, _, rel = rest.partition("/")
        for ref in config.get("references", []):
            if ref.get("logical_name") == logical:
                return os.path.join(os.path.expanduser(ref.get("path", "")), rel)
        print(f"⚠  引用 {logical} 未在配置中声明，跳过还原")
        return None
    return None


def cmd_init(config_path: str) -> None:
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    cfg = default_config()
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"✅ 已生成 {config_path}")
    else:
        print(f"⚠  {config_path} 已存在，未覆盖")
    print(f"   工作目录（自动发现）: {cfg.get('workspace')}")
    print("   如需改路径，编辑此文件里的 workspace 字段")
    print("   也可设 HERMES_HOME 环境变量指向自定义目录")
    print("   api_key 可写在此文件，或设 MOLTABLE_KEY 环境变量")


def cmd_detect(config_path: str) -> None:
    """检测并报告 agent 的工作目录路径（不写配置）。"""
    from hermes_adapter import detect_workspace
    ws = detect_workspace()
    print(f"检测到的 Agent 工作目录: {ws}")
    exists = os.path.isdir(ws)
    print(f"目录存在: {'是' if exists else '否（请检查路径或设 HERMES_HOME）'}")
    if exists:
        # 列出灵魂资产是否齐全
        soul = ["SOUL.md", "AGENTS.md", "USER.md", "memories", "skills"]
        found = [s for s in soul if os.path.exists(os.path.join(ws, s))]
        missing = [s for s in soul if s not in found]
        print(f"灵魂资产: 找到 {found if found else '无'}")
        if missing:
            print(f"缺失: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="moltable backup", description="Agent 灵魂资产备份同步")
    parser.add_argument("--config", default=os.path.expanduser("~/.moltable/backup.json"), help="配置文件路径")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("sources", help="列出备份源")
    sub.add_parser("init", help="生成配置文件")
    sub.add_parser("detect", help="检测 agent 工作目录路径")

    p_push = sub.add_parser("push", help="上传快照")
    p_push.add_argument("--name", help="备份源名称")
    p_push.add_argument("--source-id", help="指定备份源 ID")

    p_pull = sub.add_parser("pull", help="下载还原")
    p_pull.add_argument("--version", type=int, help="指定版本（默认最新）")
    p_pull.add_argument("--name", help="备份源名称")
    p_pull.add_argument("--source-id", help="指定备份源 ID")

    args = parser.parse_args()

    config_path = os.path.expanduser(args.config)
    if args.cmd == "init":
        cmd_init(config_path)
        return
    if args.cmd == "detect":
        cmd_detect(config_path)
        return

    config = load_config(config_path)
    if args.cmd == "sources":
        cmd_sources(config)
    elif args.cmd == "push":
        cmd_push(config, args.name, args.source_id)
    elif args.cmd == "pull":
        cmd_pull(config, args.source_id, args.version, args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
