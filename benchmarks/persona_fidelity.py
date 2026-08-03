#!/usr/bin/env python3
"""Benchmark 2 — Persona Fidelity (Persona 忠诚度).

Creates the "数据极客" persona (system_prompt: 你热爱数据，每次回答必须引用至少3个数字),
answers 10 standard questions with the persona's system_prompt driving the LLM,
then scores every answer with an LLM-as-judge (DeepSeek) + objective regex check.

Metrics:
  • 数字引用率 (number citation rate)  — % answers containing ≥3 numeric references
  • Persona 一致性 (persona consistency) — mean judge score (1–5) and % judged consistent
  • Judge 一致性 — agreement rate between LLM judge and objective regex count

Pass targets: 数字引用率 >= 0.80, persona 一致性(均分) >= 4.0

Run:  python3 persona_fidelity.py [--api-key sk-...]
Env:  DEEPSEEK_API_KEY (required), MOLTABLE_API (default http://127.0.0.1:8700)
"""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    DEFAULT_BASE, banner, check, count_numbers, http_request, mcp_call,
    register_user, require_server, rest_request, write_result,
)

DEEPSEEK_URLS = [
    "https://api.deepseek.com/chat/completions",
    "https://api.deepseek.com/v1/chat/completions",
]
MODEL = "deepseek-chat"

PERSONA = {
    "name": "数据极客",
    "type": "constructed",
    "description": "热爱数据、一切用数字说话的技术极客",
    "system_prompt": "你热爱数据，每次回答必须引用至少3个数字",
    "traits": {"style": "数据驱动", "detail": "高"},
}

QUESTIONS = [
    "请推荐一款适合编程的笔记本电脑",
    "如何提高每天的工作效率？",
    "周末应该怎么安排才充实？",
    "请推荐几本值得读的书",
    "如何规划一次预算有限的旅行？",
    "晚餐吃什么比较健康？",
    "怎样培养早起的好习惯？",
    "请介绍一下人工智能的发展现状",
    "如何选择一款适合自己的手机？",
    "新的一年你有什么目标建议？",
]

JUDGE_SYSTEM = (
    "你是严格的 LLM 评审员。评估一段 AI 回答是否符合其 Persona 设定。\n"
    "必须只输出一个 JSON 对象（不要输出任何其他文字），格式如下：\n"
    '{"number_refs": <回答中引用的数字个数，整数>, '
    '"has_3_numbers": <是否引用了至少3个数字，true/false>, '
    '"persona_consistent": <是否体现"热爱数据、数据驱动"的人设，true/false>, '
    '"score": <1到5的整数，5=完全符合人设且数据引用充分，1=完全不符合>, '
    '"reason": "<一句话理由>"}'
)

TARGET_CITE_RATE = 0.80
TARGET_SCORE = 4.0


def deepseek_chat(api_key, messages, json_mode=False, temperature=0.3, max_tokens=800):
    """Call DeepSeek chat completions via urllib (stdlib only).

    Tries each base URL with both proxy strategies (env proxy first, then direct)
    to survive flaky networks. Returns the assistant message text.
    """
    body = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    last_err = None
    for url in DEEPSEEK_URLS:
        for use_proxy in (True, False):
            for attempt in range(2):
                try:
                    status, data = http_request(
                        "POST", url, body,
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=90, use_proxy=use_proxy,
                    )
                    if status != 200:
                        raise RuntimeError(f"HTTP {status}: {str(data)[:300]}")
                    return data["choices"][0]["message"]["content"]
                except Exception as e:  # noqa: BLE001
                    last_err = e
                    time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"DeepSeek API 调用失败: {last_err}")


def parse_judge_json(text):
    """Robustly extract the judge's JSON object from model output."""
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"number_refs": 0, "has_3_numbers": False, "persona_consistent": False,
            "score": 0, "reason": f"judge output unparseable: {text[:120]}"}


def run():
    banner("Moltable Benchmark 2 — Persona Fidelity (Persona 忠诚度)")
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="DeepSeek API key (或设置 DEEPSEEK_API_KEY)")
    args, _ = parser.parse_known_args()

    api_key_ds = args.api_key or os.getenv("DEEPSEEK_API_KEY")
    if not api_key_ds:
        sys.stderr.write(
            f"\n{chr(0x274C)} 缺少 DEEPSEEK_API_KEY — Persona Fidelity 需要 LLM-as-judge。\n"
            "   请设置环境变量 DEEPSEEK_API_KEY 或传参 --api-key sk-xxx\n"
        )
        sys.exit(2)

    base = os.getenv("MOLTABLE_API", DEFAULT_BASE)
    print(f"  • 服务器: {base}")
    require_server(base)

    # 1. Create persona via Moltable REST API
    print("\n[1/4] 创建 Persona「数据极客」...")
    user = register_user(base, name="数据极客测试")
    status, data = rest_request(base, user["key"], "POST", "/api/personas", PERSONA)
    if status not in (200, 201) or not data.get("id"):
        sys.exit(f"  ❌ 创建 Persona 失败 ({status}): {data}")
    persona_id = data["id"]
    print(f"  ✅ Persona 创建成功 id={persona_id}")

    # 2. Verify the persona is retrievable (as an agent would load it)
    status, loaded = rest_request(base, user["key"], "GET", f"/api/personas/{persona_id}")
    system_prompt = (loaded or {}).get("system_prompt", "") if isinstance(loaded, dict) else ""
    if system_prompt != PERSONA["system_prompt"]:
        print(f"  ⚠️  读回的 system_prompt 与写入不一致: {system_prompt!r}")
    else:
        print("  ✅ MCP/REST 读回 system_prompt 一致")

    # 3. Answer 10 questions with the persona's system_prompt driving the LLM
    print(f"\n[2/4] 用 Persona system_prompt 回答 {len(QUESTIONS)} 个标准问题...")
    answers = []
    for i, q in enumerate(QUESTIONS):
        content = deepseek_chat(
            api_key_ds,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q},
            ],
            temperature=0.5, max_tokens=600,
        )
        answers.append({"question": q, "answer": content})
        print(f"  ✅ Q{i+1}: {q[:22]}… → {content[:58].replace(chr(10), ' ')}…")

    # 4. LLM-as-judge scoring
    print("\n[3/4] LLM-as-judge 逐条评分 (DeepSeek)...")
    judged = []
    for i, a in enumerate(answers):
        judge_out = deepseek_chat(
            api_key_ds,
            [
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": (
                    f"Persona system_prompt: {system_prompt}\n"
                    f"问题: {a['question']}\n"
                    f"回答: {a['answer']}"
                )},
            ],
            json_mode=True, temperature=0.0, max_tokens=400,
        )
        j = parse_judge_json(judge_out)
        obj_refs = count_numbers(a["answer"])
        j["objective_number_refs"] = obj_refs
        j["judge_agrees_with_regex"] = bool(j.get("has_3_numbers")) == (obj_refs >= 3)
        judged.append({**a, "judge": j})
        print(f"  ✅ A{i+1}: 数字={obj_refs}(正则)/{j.get('number_refs')}(judge)  "
              f"一致性={j.get('persona_consistent')} 得分={j.get('score')}")

    # ── Metrics ──
    n = len(judged)
    cite_rate = sum(1 for a in judged if a["judge"]["objective_number_refs"] >= 3) / n
    judge_cite_rate = sum(1 for a in judged if a["judge"].get("has_3_numbers")) / n
    consistency_rate = sum(1 for a in judged if a["judge"].get("persona_consistent")) / n
    mean_score = sum(a["judge"].get("score", 0) for a in judged) / n
    judge_agreement = sum(1 for a in judged if a["judge"].get("judge_agrees_with_regex")) / n

    print("\n[4/4] 评测结果")
    p_cite = cite_rate >= TARGET_CITE_RATE
    p_score = mean_score >= TARGET_SCORE
    check(p_cite, f"数字引用率 = {cite_rate:.0%}", f"目标 ≥ {TARGET_CITE_RATE:.0%}")
    check(judge_cite_rate >= TARGET_CITE_RATE, f"数字引用率(judge) = {judge_cite_rate:.0%}")
    check(p_score, f"Persona 一致性均分 = {mean_score:.2f}/5.0", f"目标 ≥ {TARGET_SCORE}")
    check(consistency_rate >= 0.80, f"一致性判定通过率 = {consistency_rate:.0%}", "目标 ≥ 80%")
    check(judge_agreement >= 0.85, f"LLM-judge 与客观正则一致性 = {judge_agreement:.0%}", "目标 ≥ 85%")

    result = {
        "benchmark": "persona_fidelity",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server": base,
        "llm": f"{MODEL} (LLM-as-judge)",
        "persona": PERSONA,
        "n_questions": n,
        "targets": {"数字引用率": TARGET_CITE_RATE, "persona_一致性均分": TARGET_SCORE},
        "metrics": {
            "数字引用率_客观": round(cite_rate, 4),
            "数字引用率_judge": round(judge_cite_rate, 4),
            "persona_一致性均分": round(mean_score, 4),
            "persona_一致性通过率": round(consistency_rate, 4),
            "llm_judge_一致性": round(judge_agreement, 4),
            "answers": judged,
        },
        "passed": bool(p_cite and p_score),
    }
    path = write_result("persona_fidelity", result)
    print(f"\n  结论: {'✅ PASS' if result['passed'] else '❌ FAIL'} — "
          f"数字引用率={cite_rate:.0%} (≥{TARGET_CITE_RATE:.0%}), "
          f"一致性均分={mean_score:.2f} (≥{TARGET_SCORE})")
    print(f"  完整明细: {path}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(run())
