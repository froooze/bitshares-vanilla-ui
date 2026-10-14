#!/usr/bin/env python3
"""Rename vote-locked "票据/票证" -> "投票质押" in vanilla/locales/zh.json.

Compound (per brief): "投票质押" (vote 投票 + stake 质押, both verbatim:
vote.title "投票", tickets_body "投票锁定/投票权重", vote.ballot_intro
"您的质押", pool.confirm_stake "确认质押"). No spaces, no plural.
Bare "质押" where the sentence already says vote (title + body line 1).

Both 票据 (ticket pages, 24 strings) and 票证 (proposal/help, 9 strings) are
the vote-locked sense and both go. Event-admission "活动门票" in
help.topic_assets-uia_body is EXCLUDED (different sense, kept) — note 门票
contains 票, so the guard checks the full 门票 string, not 票据/票证.

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_zh.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "zh.json")

TICKET_RE = re.compile("票据|票证")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "票据创建",
        "投票质押创建",
    ),
    "account.op_ticket_update": (
        "票据更新",
        "投票质押更新",
    ),
    "account.sum_ticket_create": (
        "已创建票据 %(amount)s",
        "已创建投票质押 %(amount)s",
    ),
    "account.sum_ticket_update": (
        "已更新票据 %(ticket)s",
        "已更新投票质押 %(ticket)s",
    ),
    "help.topic_tickets_title": (
        "投票锁定票证",
        "投票锁定质押",
    ),
    "menu.p_tickets": (
        "票据",
        "投票质押",
    ),
    "proposal.err_downgrade_unproven": (
        "票证降级未经验证——请选择当前锁定或更长的锁定。",
        "投票质押降级未经验证——请选择当前锁定或更长的锁定。",
    ),
    "proposal.err_unknown_ticket": (
        "未知票证。",
        "未知投票质押。",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "内部票证金额必须大于 0。",
        "内部投票质押金额必须大于 0。",
    ),
    "proposal.op_57": (
        "创建票证",
        "创建投票质押",
    ),
    "proposal.op_58": (
        "更新票证",
        "更新投票质押",
    ),
    "proposal.ticket": (
        "票证",
        "投票质押",
    ),
    "proposals_ticket.title": (
        "票据",
        "投票质押",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "确认创建票据（操作 57）",
        "确认创建投票质押（操作 57）",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "确认更新票据（操作 58）",
        "确认更新投票质押（操作 58）",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "无法构建票据（请检查账户、资产和金额）。",
        "无法构建投票质押（请检查账户、资产和金额）。",
    ),
    "ticket.could_not_load_tickets": (
        "无法加载票据。",
        "无法加载投票质押。",
    ),
    "ticket.create_ticket": (
        "创建票据",
        "创建投票质押",
    ),
    "ticket.loading_my_tickets": (
        "正在加载我的票据…",
        "正在加载我的投票质押…",
    ),
    "ticket.loading_tickets": (
        "正在加载票据…",
        "正在加载投票质押…",
    ),
    "ticket.my_tickets": (
        "我的票据",
        "我的投票质押",
    ),
    "ticket.review_ticket": (
        "核对票据",
        "核对投票质押",
    ),
    "ticket.ticket": (
        "票据",
        "投票质押",
    ),
    "ticket.ticket_amount_must_be_0": (
        "票据金额必须大于 0。",
        "投票质押金额必须大于 0。",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "票据已创建并已在链上重读。",
        "投票质押已创建并已在链上重读。",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "票据已更新并已在链上重读。",
        "投票质押已更新并已在链上重读。",
    ),
    "ticket.tickets": (
        "票据",
        "投票质押",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "票据无法删除（不存在删除操作） — 上方行均为永久记录。",
        "投票质押无法删除（不存在删除操作） — 上方行均为永久记录。",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "票据将资金锁定为投票权重。不存在删除操作，因此每条票据记录都是永久的。",
        "投票质押将资金锁定为投票权重。不存在删除操作，因此每条投票质押记录都是永久的。",
    ),
    "tickets.title": (
        "票据",
        "投票质押",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "资金池动作、票证、聊天。",
            "资金池动作、投票质押、聊天。",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [票据](#/tickets)",
            "- [投票质押](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "投票锁定票证把质押加时间换成投票权重",
            "投票锁定质押把质押加时间换成投票权重",
            1,
        ),
        (
            "从活期质押建票证，可追加，到期领回。",
            "从活期质押建投票质押，可追加，到期领回。",
            1,
        ),
        (
            "票证权重经正常选票名单计入",
            "投票质押权重经正常选票名单计入",
            1,
        ),
    ],
}


def dig(d, key):
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
    raw = open(LOC, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []
    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder change" % key)
            continue
        if not TICKET_RE.search(old):
            problems.append("ABORT %s: script old has no ticket word" % key)
            continue
    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not TICKET_RE.search(old_snip):
                problems.append("ABORT %s: snippet w/o ticket: %r" % (key, old_snip))
                continue
            if cur.count(old_snip) != count:
                problems.append("ABORT %s: snippet x%d != %d: %r" % (key, cur.count(old_snip), count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change" % key)
    excl = dig(d, "help.topic_assets-uia_body")
    if "活动门票" not in excl:
        problems.append("ABORT help.topic_assets-uia_body: event sense changed unexpectedly")
    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    if set(flatten(d)) != before_keys:
        print("FAIL: key drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    after_vals = flatten(d)
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(LOC, "w", encoding="utf-8").write(out)
        print("OK zh: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK zh: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
