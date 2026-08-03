#!/usr/bin/env python3
"""Benchmark 1 — Cross-Agent Recall (跨 Agent 记忆召回).

Tests Moltable's core differentiator: memories written by Agent A must be
semantically retrievable by Agent B (same identity, fresh session).

Flow:
  1. Agent A registers and writes 21 memories (7 categories × 3, natural Chinese).
  2. Agent B loads context via auto_provision (same API key = same identity).
  3. For each memory, a paraphrased semantic query is issued via search_memory.
  4. Metrics: recall@1 / recall@3 / recall@5, MRR (overall + per category).

Pass targets: recall@1 >= 0.70, MRR >= 0.80.

Run:  python3 cross_agent_recall.py
Env:  MOLTABLE_API (default http://127.0.0.1:8700)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    DEFAULT_BASE, banner, check, mcp_call, mcp_save_memory, register_user,
    require_server, write_result,
)

# ── 21 memories: (category, content, semantic query) ──────────
# Queries are natural paraphrases — shared keywords, different wording.
MEMORIES = [
    # preference
    ("preference", "用户喜欢在早晨喝一杯美式咖啡来提神", "早上喝什么咖啡提神？"),
    ("preference", "用户偏好使用暗色模式的软件界面", "软件界面喜欢深色还是浅色？"),
    ("preference", "用户不喜欢吃香菜和榴莲", "有哪些食物是用户讨厌的？"),
    # decision
    ("decision", "团队决定把项目上线时间推迟到十一月", "项目什么时候正式上线？"),
    ("decision", "用户决定不买燃油车，改买电动车", "买车的时候选油车还是电车？"),
    ("decision", "公司确定新办公室选址在望京科技园区", "新办公室选在哪里？"),
    # fact
    ("fact", "用户的生日是十一月十五日", "用户什么时候过生日？"),
    ("fact", "用户住在上海浦东新区，工作在陆家嘴", "用户住在哪个城市哪个区？"),
    ("fact", "用户的母语是中文，英语水平是中级", "用户会说哪几种语言？"),
    # project
    ("project", "跨境电商独立站项目正在进行，目标市场是美国", "目前在做哪个市场的电商项目？"),
    ("project", "智能家居控制App项目已经进入内测阶段", "智能家居App开发到什么阶段了？"),
    ("project", "公司官网改版项目预计下个月启动", "官网改版什么时候开始？"),
    # insight
    ("insight", "用户发现早睡早起后工作效率提升了很多", "怎样做才能提高工作效率？"),
    ("insight", "数据分析显示周末下午是用户最专注的时间段", "用户什么时候状态最专注？"),
    ("insight", "复盘发现短视频投放的转化率比图文内容更高", "哪种内容形式的投放转化更好？"),
    # task
    ("task", "下周三之前需要完成季度销售报告", "季度销售报告什么时候交？"),
    ("task", "明天上午十点约了牙医复诊", "明天上午有什么安排？"),
    ("task", "本周六要参加朋友的婚礼，需要准备礼金", "周六有什么活动要参加？"),
    # relationship
    ("relationship", "用户最好的朋友是大学室友李明", "用户最好的朋友是谁？"),
    ("relationship", "用户和导师王教授保持每月一次的面谈", "用户多久和导师见一次面？"),
    ("relationship", "用户的妹妹在杭州读研究生", "用户的妹妹在哪里上学？"),
]

TOP_K = 5
TARGET_RECALL_1 = 0.70
TARGET_MRR = 0.80


def run():
    banner("Moltable Benchmark 1 — Cross-Agent Recall (跨 Agent 记忆召回)")
    base = os.getenv("MOLTABLE_API", DEFAULT_BASE)
    print(f"  • 服务器: {base}")
    require_server(base)

    # 1. Agent A writes memories
    print("\n[1/4] Agent A 注册并写入 21 条记忆 (7 类别 × 3)...")
    agent_a = register_user(base, name="Agent A")
    api_key = agent_a["key"]
    print(f"  ✅ Agent A 注册成功 user_id={agent_a['user_id'][:8]}...")

    saved_ids, conflicts, failures = [], 0, 0
    for i, (cat, content, _q) in enumerate(MEMORIES):
        resp, was_conflict = mcp_save_memory(base, api_key, content, cat, req_id=i + 1)
        if resp.get("saved"):
            saved_ids.append(resp["id"])
        else:
            failures += 1
            print(f"  ⚠️  保存失败 ({cat}): {resp}")
        conflicts += 1 if was_conflict else 0
    if conflicts:
        print(f"  ⚠️  {conflicts} 条记忆触发冲突检测并已 force 保存")
    if failures:
        sys.exit(f"  ❌ {failures} 条记忆保存失败，中止评测")
    print(f"  ✅ Agent A 写入 {len(saved_ids)} 条记忆")

    # 2. Agent B loads via auto_provision
    print("\n[2/4] Agent B 通过 auto_provision 加载身份上下文...")
    prov = mcp_call(base, api_key, "auto_provision", {}, req_id=100)
    mem_count = prov.get("memory_count", 0)
    print(f"  ✅ auto_provision 返回 memory_count={mem_count}, "
          f"preferences={len(prov.get('preferences', []))}, "
          f"personas={len(prov.get('available_personas', []))}")
    if mem_count < len(saved_ids):
        print(f"  ⚠️  auto_provision 记忆计数 {mem_count} < 实际 {len(saved_ids)}")

    # 3. Semantic queries for every memory
    print(f"\n[3/4] 对 {len(MEMORIES)} 条记忆逐一生成语义查询并检索 (top_k={TOP_K})...")
    ranks = []          # rank of target per query (1-based, None if missing)
    per_query = []
    for i, (cat, content, query) in enumerate(MEMORIES):
        target_id = saved_ids[i]
        resp = mcp_call(base, api_key, "search_memory",
                        {"query": query, "top_k": TOP_K}, req_id=200 + i)
        results = resp.get("results", [])
        found_rank = None
        for rank, r in enumerate(results, start=1):
            if r.get("id") == target_id:
                found_rank = rank
                break
        ranks.append(found_rank)
        per_query.append({
            "category": cat,
            "memory": content,
            "query": query,
            "target_id": target_id,
            "rank": found_rank,
            "top1": results[0]["content"][:40] if results else "",
        })

    # 4. Metrics
    n = len(ranks)
    hit = lambda k: sum(1 for r in ranks if r is not None and r <= k) / n
    recall_1, recall_3, recall_5 = hit(1), hit(3), hit(5)
    mrr = sum(1.0 / r for r in ranks if r is not None) / n

    per_cat = {}
    for cat in ["preference", "decision", "fact", "project", "insight", "task", "relationship"]:
        rs = [r for (c, _m, _q), r in zip(MEMORIES, ranks) if c == cat]
        if rs:
            per_cat[cat] = {
                "n": len(rs),
                "recall@1": round(sum(1 for r in rs if r == 1) / len(rs), 4),
                "recall@5": round(sum(1 for r in rs if r is not None and r <= 5) / len(rs), 4),
                "mrr": round(sum(1.0 / r for r in rs if r is not None) / len(rs), 4),
            }

    print("\n[4/4] 评测结果")
    passed_r1 = recall_1 >= TARGET_RECALL_1
    passed_mrr = mrr >= TARGET_MRR
    check(passed_r1, f"recall@1 = {recall_1:.3f}", f"目标 ≥ {TARGET_RECALL_1}")
    check(recall_3 >= 0.85, f"recall@3 = {recall_3:.3f}", "目标 ≥ 0.85")
    check(recall_5 >= 0.95, f"recall@5 = {recall_5:.3f}", "目标 ≥ 0.95")
    check(passed_mrr, f"MRR = {mrr:.3f}", f"目标 ≥ {TARGET_MRR}")
    print("\n  分类别成绩:")
    for cat, m in per_cat.items():
        print(f"    {cat:<12} recall@1={m['recall@1']:.3f}  recall@5={m['recall@5']:.3f}  MRR={m['mrr']:.3f}")

    result = {
        "benchmark": "cross_agent_recall",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server": base,
        "embedding_model": "server-side (paraphrase-multilingual-MiniLM-L12-v2 recommended)",
        "n_memories": n,
        "n_categories": len(per_cat),
        "top_k": TOP_K,
        "targets": {"recall@1": TARGET_RECALL_1, "mrr": TARGET_MRR},
        "metrics": {
            "recall@1": round(recall_1, 4),
            "recall@3": round(recall_3, 4),
            "recall@5": round(recall_5, 4),
            "mrr": round(mrr, 4),
            "per_category": per_cat,
            "conflicts_forced": conflicts,
            "memory_count_seen_by_agent_b": mem_count,
        },
        "passed": bool(passed_r1 and passed_mrr),
        "queries": per_query,
    }
    path = write_result("cross_agent_recall", result)
    print(f"\n  结论: {'✅ PASS' if result['passed'] else '❌ FAIL'} — "
          f"recall@1={recall_1:.3f} (≥{TARGET_RECALL_1}), MRR={mrr:.3f} (≥{TARGET_MRR})")
    print(f"  完整明细: {path}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(run())
