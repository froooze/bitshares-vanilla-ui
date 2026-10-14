#!/usr/bin/env python3
"""Rename vote-locked "티켓" -> "투표 스테이크" in vanilla/locales/ko.json.

Compound (per brief): "투표 스테이크" (vote 투표 + stake 스테이크, both
verbatim: vote.title "투표", tickets_body "투표 잠금/투표 가중치/투표 목록",
pool.confirm_stake "스테이크를 확인합니다", tickets_body "스테이크").
Bare "스테이크" where the sentence already says vote (title + body line 1).

Particles re-agree after the vowel-final 스테이크 (으니까 batchim-ㅅ 티켓
took 을/이/은; vowel-final 스테이크 takes 를/가/는) — same class of fix as
the blind pass 로→으로 note, in reverse.

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
Event-admission "이벤트 티켓" in help.topic_assets-uia_body EXCLUDED.

Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_ko.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ko.json")

TICKET_RE = re.compile("티켓")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "티켓 생성",
        "투표 스테이크 생성",
    ),
    "account.op_ticket_update": (
        "티켓 업데이트",
        "투표 스테이크 업데이트",
    ),
    "account.sum_ticket_create": (
        "티켓 %(amount)s 생성됨",
        "투표 스테이크 %(amount)s 생성됨",
    ),
    "account.sum_ticket_update": (
        "티켓 %(ticket)s 업데이트됨",
        "투표 스테이크 %(ticket)s 업데이트됨",
    ),
    "help.topic_tickets_title": (
        "투표 잠금 티켓",
        "투표 잠금 스테이크",
    ),
    "menu.p_tickets": (
        "티켓",
        "투표 스테이크",
    ),
    "proposal.err_downgrade_unproven": (
        "티켓 하향은 검증되지 않았습니다 — 현재 잠금 또는 더 긴 잠금을 선택하십시오.",
        "투표 스테이크 하향은 검증되지 않았습니다 — 현재 잠금 또는 더 긴 잠금을 선택하십시오.",
    ),
    "proposal.err_unknown_ticket": (
        "알 수 없는 티켓입니다.",
        "알 수 없는 투표 스테이크입니다.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "내부 티켓 금액은 0보다 커야 합니다.",
        "내부 투표 스테이크 금액은 0보다 커야 합니다.",
    ),
    "proposal.op_57": (
        "티켓 생성",
        "투표 스테이크 생성",
    ),
    "proposal.op_58": (
        "티켓 업데이트",
        "투표 스테이크 업데이트",
    ),
    "proposal.ticket": (
        "티켓",
        "투표 스테이크",
    ),
    "proposals_ticket.title": (
        "티켓",
        "투표 스테이크",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "티켓 생성 확인 (op 57)",
        "투표 스테이크 생성 확인 (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "티켓 업데이트 확인 (op 58)",
        "투표 스테이크 업데이트 확인 (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "티켓을 만들 수 없습니다 (계정, 자산, 금액을 확인하십시오).",
        "투표 스테이크를 만들 수 없습니다 (계정, 자산, 금액을 확인하십시오).",
    ),
    "ticket.could_not_load_tickets": (
        "티켓을 불러올 수 없습니다.",
        "투표 스테이크를 불러올 수 없습니다.",
    ),
    "ticket.create_ticket": (
        "티켓 생성",
        "투표 스테이크 생성",
    ),
    "ticket.loading_my_tickets": (
        "내 티켓 불러오는 중…",
        "내 투표 스테이크 불러오는 중…",
    ),
    "ticket.loading_tickets": (
        "티켓 불러오는 중…",
        "투표 스테이크 불러오는 중…",
    ),
    "ticket.my_tickets": (
        "내 티켓",
        "내 투표 스테이크",
    ),
    "ticket.review_ticket": (
        "티켓 검토",
        "투표 스테이크 검토",
    ),
    "ticket.ticket": (
        "티켓",
        "투표 스테이크",
    ),
    "ticket.ticket_amount_must_be_0": (
        "티켓 금액은 0보다 커야 합니다.",
        "투표 스테이크 금액은 0보다 커야 합니다.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "티켓이 생성되어 온체인에서 다시 읽었습니다.",
        "투표 스테이크가 생성되어 온체인에서 다시 읽었습니다.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "티켓이 업데이트되어 온체인에서 다시 읽었습니다.",
        "투표 스테이크가 업데이트되어 온체인에서 다시 읽었습니다.",
    ),
    "ticket.tickets": (
        "티켓",
        "투표 스테이크",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "티켓은 삭제할 수 없습니다 (삭제 오퍼레이션이 없습니다) — 위 행은 영구적입니다.",
        "투표 스테이크는 삭제할 수 없습니다 (삭제 오퍼레이션이 없습니다) — 위 행은 영구적입니다.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "티켓은 투표 가중치를 위해 자금을 잠급니다. 삭제 오퍼레이션이 없으므로 모든 티켓 행은 영구적입니다.",
        "투표 스테이크는 투표 가중치를 위해 자금을 잠급니다. 삭제 오퍼레이션이 없으므로 모든 투표 스테이크 행은 영구적입니다.",
    ),
    "tickets.title": (
        "티켓",
        "투표 스테이크",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "전송, 주문, 투표, 풀 이동, 티켓, 채팅.",
            "전송, 주문, 투표, 풀 이동, 투표 스테이크, 채팅.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [티켓](#/tickets)",
            "- [투표 스테이크](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "투표 잠금 티켓은 스테이크와 시간을 투표 가중치로 바꿉니다.",
            "투표 잠금 스테이크는 스테이크와 시간을 투표 가중치로 바꿉니다.",
            1,
        ),
        (
            "유동 스테이크에서 티켓을 만들고 보충한 뒤 잠금이 끝나면 회수하십시오.",
            "유동 스테이크에서 투표 스테이크를 만들고 보충한 뒤 잠금이 끝나면 회수하십시오.",
            1,
        ),
        (
            "티켓 가중치는 일반 투표 목록을 통해",
            "투표 스테이크 가중치는 일반 투표 목록을 통해",
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
    if "이벤트 티켓" not in excl:
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
        print("OK ko: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ko: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
