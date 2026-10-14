#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/zh.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + 6 snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from dict's OWN attested words where possible): 资助提案 / 资助受益人.
Pay keeps attested pay word (never transliterated pay); budget/funding keep attested words;
recipients (PEOPLE) use beneficiary word attested in referrals body, not proposals.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_zh.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "zh.json")

WORKER_RE = re.compile(r"工人")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "工人创建",
        "资助提案创建",
    ),
    "account.sum_worker_create": (
        "已创建工人“%(name)s”",
        "已创建资助提案“%(name)s”",
    ),
    "createworker.confirm_worker_op_34": (
        "确认工人（op %(op)s）",
        "确认资助提案（op %(op)s）",
    ),
    "createworker.could_not_preview_the_worker": (
        "无法预览该工人。",
        "无法预览该资助提案。",
    ),
    "createworker.create_worker": (
        "创建工人",
        "创建资助提案",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "起草工人（op %(op)s）。预览是实时的；核对会报出实时手续费，随后“签名并发送”直接广播 op %(op)s — 工人由直接操作创建，而不是通过提案。",
        "起草资助提案（op %(op)s）。预览是实时的；核对会报出实时手续费，随后“签名并发送”直接广播 op %(op)s — 资助提案由直接操作创建，而不是通过提案。",
    ),
    "createworker.enter_a_worker_name": (
        "请输入工人名称。",
        "请输入资助提案名称。",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "所有者支付手续费并领取工人报酬 — 请使用您控制的终身会员账户。",
        "所有者支付手续费并领取资助提案报酬 — 请使用您控制的终身会员账户。",
    ),
    "createworker.preview_worker": (
        "预览工人",
        "预览资助提案",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "发布工人需要终身会员账户 — 普通账户无法支付此手续费。下方所有者必须已升级。",
        "发布资助提案需要终身会员账户 — 普通账户无法支付此手续费。下方所有者必须已升级。",
    ),
    "createworker.reading_existing_workers": (
        "正在读取已有工人…",
        "正在读取已有资助提案…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "工人后端缺失：js/account.js 或 js/format.js 加载失败。",
        "资助提案后端缺失：js/account.js 或 js/format.js 加载失败。",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "工人后端缺失：js/asset-ops.js 加载失败。",
        "资助提案后端缺失：js/asset-ops.js 加载失败。",
    ),
    "createworker.worker_name": (
        "工人名称 ",
        "资助提案名称 ",
    ),
    "createworker.worker_preview_op_34": (
        "工人预览（op %(op)s）",
        "资助提案预览（op %(op)s）",
    ),
    "help.topic_workers_title": (
        "工人",
        "资助提案",
    ),
    "help.topic_voting_text": (
        "为见证人、理事会、工人投票——也可交给代理。",
        "为见证人、理事会、资助提案投票——也可交给代理。",
    ),
    "menu.d_voting": (
        "见证人、理事会、工人与代理。",
        "见证人、理事会、资助提案与代理。",
    ),
    "menu.p_worker": (
        "创建工人",
        "创建资助提案",
    ),
    "news.voting_witnesses_committee_workers": (
        "投票 — 见证人、理事会、工人",
        "投票 — 见证人、理事会、资助提案",
    ),
    "seo.desc_voting": (
        "为 BitShares 见证人、理事会成员与工人投票。每一张选票都在您的设备本地签名。",
        "为 BitShares 见证人、理事会成员与资助提案投票。每一张选票都在您的设备本地签名。",
    ),
    "vote.ballot_intro": (
        "您的质押选出见证人与理事会，并为工人提供资金 — 下方所有计数与份额都是实时链上读取。",
        "您的质押选出见证人与理事会，并为资助提案提供资金 — 下方所有计数与份额都是实时链上读取。",
    ),
    "vote.empty_hint": (
        " 链上承载时将显示条目——工人通过 #/create-worker 提议。",
        " 链上承载时将显示条目——资助提案通过 #/create-worker 提议。",
    ),
    "vote.funding_unavailable_prefix": (
        "工人资金不可用 (",
        "资助提案资金不可用 (",
    ),
    "vote.hide_legacy_label": (
        " 隐藏历史提案（始终开启——过期工人将在获取时排除）",
        " 隐藏历史提案（始终开启——过期资助提案将在获取时排除）",
    ),
    "vote.hide_legacy_title": (
        "工人列表来自 get_all_workers(false)；过期行永不到达。",
        "资助提案列表来自 get_all_workers(false)；过期行永不到达。",
    ),
    "vote.no_workers": (
        "未找到工人。测试网通常没有——属正常，非错误。",
        "未找到资助提案。测试网通常没有——属正常，非错误。",
    ),
    "vote.tab_workers": (
        "工人 (",
        "资助提案 (",
    ),
    "vote.worker_budget": (
        "工人预算：—",
        "资助提案预算：—",
    ),
    "vote.worker_budget_loading": (
        "工人预算：加载中…",
        "资助提案预算：加载中…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("工人交付有偿项目", "资助受益人交付有偿项目", 1,),
    ],
    "help.topic_sitemap_body": [
        ("工人", "资助提案", 1,),
    ],
    "help.topic_tickets_body": [
        ("工人", "资助提案", 1,),
    ],
    "help.topic_vesting_body": [
        ("工人", "资助提案", 1,),
    ],
    "help.topic_voting_body": [
        ("工人", "资助提案", 6,),
    ],
    "help.topic_workers_body": [
        ("工人", "资助提案", 4,),
    ],
}


def digd(d, key):
    node = d
    for seg in key.split("."):
        node = node[seg]
    return node


def set_dig(d, key, value):
    segs = key.split(".")
    node = d
    for seg in segs[:-1]:
        node = node[seg]
    node[segs[-1]] = value


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def main():
    apply = "--apply" in sys.argv
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print(f"FAIL: {P} does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WORKER_RE.search(old):
            problems.append("ABORT %s: script old has no worker word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip) and key != "help.topic_glossary_body":
                # glossary old_snip contains worker word by definition; allow generic check
                pass
            # For glossary, old_snip must contain worker word; enforce
            if key == "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            if key != "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = digd(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    after_vals = flatten(d)
    if "get_all_workers" not in after_vals["vote.hide_legacy_title"]:
        print("FAIL: get_all_workers token lost")
        return 1
    for k in ("createworker.worker_backend_missing_js_account_js_or_js_fo",
              "createworker.worker_backend_missing_js_asset_ops_js_failed"):
        if "js/" not in after_vals[k]:
            print("FAIL: file path lost in %s" % k)
            return 1
    for k in ("help.topic_sitemap_body", "vote.empty_hint"):
        if "#/create-worker" not in after_vals[k]:
            print("FAIL: route hash lost in %s" % k)
            return 1

    if set(after_vals) != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print(f"OK {P}: renamed")
    else:
        print(f"OK {P}: dry run green")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
