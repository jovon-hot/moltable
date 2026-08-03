#!/usr/bin/env python3
"""Benchmark 3 — Provision Completeness (上下文加载完整性).

Verifies that auto_provision() returns the full user context an agent needs:
  • 10 preference memories  → preferences >= 10
  • 3 personas              → available_personas >= 3
  • 2 projects              → active_projects >= 2
  • 5 fact memories         → core_knowledge >= 5
  (+ 5 decision memories for realism; memory_count >= 20)

Completeness % = mean(actual / required) per checked section, capped at 100%.
Pass target: 100% completeness (all sections PASS).

Run:  python3 provision_completeness.py
Env:  MOLTABLE_API (default http://127.0.0.1:8700)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    DEFAULT_BASE, banner, check, mcp_call, mcp_save_memory, register_user,
    require_server, rest_request, write_result,
)

PREFERENCES = [
    "用户喜欢在早晨喝美式咖啡",
    "用户偏好暗色模式的软件界面",
    "用户喜欢用番茄工作法安排时间",
    "用户习惯在周五下午做周报",
    "用户喜欢听爵士乐作为工作背景音乐",
    "用户偏好中文交流，偶尔使用英文",
    "用户喜欢简洁直接的沟通风格",
    "用户习惯每天睡前阅读半小时",
    "用户喜欢在咖啡馆远程办公",
    "用户偏好键盘快捷键操作，很少用鼠标",
]
DECISIONS = [
    "决定采用 React 重写前端架构",
    "决定把数据存储迁移到 PostgreSQL",
    "决定今年不涨订阅价格",
    "决定将客服响应时间目标定为两小时内",
    "决定优先投入移动端开发",
]
FACTS = [
    "用户的开发环境是 macOS",
    "用户所在团队有十二名工程师",
    "用户的工作语言是中文",
    "公司的产品主要面向中小型企业客户",
    "用户拥有三年的全栈开发经验",
]

REQUIRED = {
    "preferences": 10,
    "personas": 3,
    "projects": 2,
    "core_knowledge": 5,
}


def run():
    banner("Moltable Benchmark 3 — Provision Completeness (上下文加载完整性)")
    base = os.getenv("MOLTABLE_API", DEFAULT_BASE)
    print(f"  • 服务器: {base}")
    require_server(base)

    # 1. Seed data
    print("\n[1/4] 创建测试数据: 10 偏好 + 5 决策 + 5 事实...")
    user = register_user(base, name="Provision Tester")
    api_key = user["key"]

    all_mems = [(c, m) for c, ms in (("preference", PREFERENCES),
                                      ("decision", DECISIONS),
                                      ("fact", FACTS)) for m in ms]
    saved = 0
    for i, (cat, content) in enumerate(all_mems):
        resp, _ = mcp_save_memory(base, api_key, content, cat, req_id=i + 1)
        if resp.get("saved"):
            saved += 1
    print(f"  ✅ 写入记忆 {saved}/{len(all_mems)} 条")
    if saved < len(all_mems):
        sys.exit("  ❌ 记忆写入不完整，中止评测")

    print("\n[2/4] 创建 3 个 Persona...")
    persona_ids = []
    for i in range(3):
        status, data = rest_request(base, api_key, "POST", "/api/personas", {
            "name": f"测试人格{i + 1}",
            "type": "constructed",
            "description": f"基准测试用 Persona {i + 1}",
            "system_prompt": f"你是测试人格{i + 1}，回答保持简洁。",
        })
        if status not in (200, 201) or not data.get("id"):
            sys.exit(f"  ❌ 创建 Persona 失败 ({status}): {data}")
        persona_ids.append(data["id"])
    print(f"  ✅ Persona x3: {[p[:8] for p in persona_ids]}")

    print("\n[3/4] 创建 2 个项目...")
    for i in range(2):
        status, data = rest_request(base, api_key, "POST", "/api/projects", {
            "name": f"基准项目{i + 1}",
            "description": f"Provision 完整性测试项目 {i + 1}",
            "knowledge_bases": ["docs", "wiki"],
            "tools": ["github", "slack"],
        })
        if status not in (200, 201):
            sys.exit(f"  ❌ 创建项目失败 ({status}): {data}")
    print("  ✅ Projects x2")

    # 4. auto_provision + checks
    print("\n[4/4] auto_provision 完整性检查...")
    prov = mcp_call(base, api_key, "auto_provision", {}, req_id=999)
    actual = {
        "preferences": len(prov.get("preferences", [])),
        "personas": len(prov.get("available_personas", [])),
        "projects": len(prov.get("active_projects", [])),
        "core_knowledge": len(prov.get("core_knowledge", [])),
    }
    memory_count = prov.get("memory_count", 0)
    print(f"  • 返回 sections: preferences={actual['preferences']}, "
          f"personas={actual['personas']}, projects={actual['projects']}, "
          f"core_knowledge={actual['core_knowledge']}, memory_count={memory_count}")

    ratios = {}
    passed_all = True
    for section, req in REQUIRED.items():
        got = actual[section]
        ok = got >= req
        passed_all = passed_all and ok
        ratios[section] = min(1.0, got / req)
        check(ok, f"{section}: {got} ≥ {req}", f"完整度 {min(100, int(got / req * 100))}%")
    check(memory_count >= 20, f"memory_count: {memory_count} ≥ 20", "总记忆数")

    completeness = round(sum(ratios.values()) / len(ratios) * 100, 1)
    print(f"\n  上下文完整度: {completeness}%")

    result = {
        "benchmark": "provision_completeness",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server": base,
        "required": REQUIRED,
        "actual": actual,
        "memory_count": memory_count,
        "completeness_percent": completeness,
        "metrics": {"sections": {k: {"required": REQUIRED[k], "actual": actual[k],
                                     "ratio": round(ratios[k], 4)} for k in REQUIRED}},
        "passed": bool(passed_all),
        "provision_snapshot": prov,
    }
    path = write_result("provision_completeness", result)
    print(f"\n  结论: {'✅ PASS' if result['passed'] else '❌ FAIL'} — 完整度 {completeness}%")
    print(f"  完整明细: {path}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(run())
