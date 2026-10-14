#!/usr/bin/env python3
"""Rename vote-locked "チケット" -> "投票ステーク" in vanilla/locales/ja.json.

Compound (per brief): full "投票ステーク" (vote 投票 + stake ステーク, both
verbatim from the shipped dict: vote.title "投票", vote.publish "投票を発行",
pool.confirm_stake "ステークを確認", vote.ballot_intro "あなたのステーク",
menu.d_tickets "投票ロックされたステーク"). Japanese has no plural.
Bare "ステーク" where the sentence already says vote (title + body line 1),
per brief — noted in the report.

Keys unchanged. Placeholders (%(ticket)s, %(amount)s) byte-identical.
Route "#/tickets" unchanged. Event-admission "イベントチケット" in
help.topic_assets-uia_body is EXCLUDED (different sense, kept).

Gates G1-G5: same as rename_ticket_stake_de.py (assert currents first).
Usage: python3 tooling/rename_ticket_stake_ja.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ja.json")

TICKET_RE = re.compile("チケット")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "チケット作成",
        "投票ステーク作成",
    ),
    "account.op_ticket_update": (
        "チケット更新",
        "投票ステーク更新",
    ),
    "account.sum_ticket_create": (
        "チケット %(amount)s を作成しました",
        "投票ステーク %(amount)s を作成しました",
    ),
    "account.sum_ticket_update": (
        "チケット %(ticket)s を更新しました",
        "投票ステーク %(ticket)s を更新しました",
    ),
    "help.topic_tickets_title": (
        "投票ロックチケット",
        "投票ロックステーク",
    ),
    "menu.p_tickets": (
        "チケット",
        "投票ステーク",
    ),
    "proposal.err_downgrade_unproven": (
        "チケットのダウングレードは未検証です — 現在のロックまたはより長いものを選んでください。",
        "投票ステークのダウングレードは未検証です — 現在のロックまたはより長いものを選んでください。",
    ),
    "proposal.err_unknown_ticket": (
        "不明なチケット。",
        "不明な投票ステーク。",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "内部チケット数量は0より大きくしてください。",
        "内部投票ステーク数量は0より大きくしてください。",
    ),
    "proposal.op_57": (
        "チケット作成",
        "投票ステーク作成",
    ),
    "proposal.op_58": (
        "チケット更新",
        "投票ステーク更新",
    ),
    "proposal.ticket": (
        "チケット",
        "投票ステーク",
    ),
    "proposals_ticket.title": (
        "チケット",
        "投票ステーク",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "チケット作成の確認（op 57）",
        "投票ステーク作成の確認（op 57）",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "チケット更新の確認（op 58）",
        "投票ステーク更新の確認（op 58）",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "チケットを構築できませんでした（アカウント、アセット、額を確認してください）。",
        "投票ステークを構築できませんでした（アカウント、アセット、額を確認してください）。",
    ),
    "ticket.could_not_load_tickets": (
        "チケットを読み込めませんでした。",
        "投票ステークを読み込めませんでした。",
    ),
    "ticket.create_ticket": (
        "チケットを作成",
        "投票ステークを作成",
    ),
    "ticket.loading_my_tickets": (
        "マイチケットを読み込み中…",
        "マイ投票ステークを読み込み中…",
    ),
    "ticket.loading_tickets": (
        "チケットを読み込み中…",
        "投票ステークを読み込み中…",
    ),
    "ticket.my_tickets": (
        "マイチケット",
        "マイ投票ステーク",
    ),
    "ticket.review_ticket": (
        "チケットを確認",
        "投票ステークを確認",
    ),
    "ticket.ticket": (
        "チケット",
        "投票ステーク",
    ),
    "ticket.ticket_amount_must_be_0": (
        "チケット額は0より大きくしてください。",
        "投票ステーク額は0より大きくしてください。",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "チケットを作成し、チェーン上で再読み取りしました。",
        "投票ステークを作成し、チェーン上で再読み取りしました。",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "チケットを更新し、チェーン上で再読み取りしました。",
        "投票ステークを更新し、チェーン上で再読み取りしました。",
    ),
    "ticket.tickets": (
        "チケット",
        "投票ステーク",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "チケットは削除できません（削除opが存在しません） — 上の行は永久的です。",
        "投票ステークは削除できません（削除opが存在しません） — 上の行は永久的です。",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "チケットは投票ウェイトのために資金をロックします。削除操作がないため、すべてのチケット行は永久的です。",
        "投票ステークは投票ウェイトのために資金をロックします。削除操作がないため、すべての投票ステーク行は永久的です。",
    ),
    "tickets.title": (
        "チケット",
        "投票ステーク",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "送金、注文、投票、プール移動、チケット、チャット。",
            "送金、注文、投票、プール移動、投票ステーク、チャット。",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [チケット](#/tickets)",
            "- [投票ステーク](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "投票ロックチケットはステーク＋時間を投票ウェイトに変換します。",
            "投票ロックステークはステーク＋時間を投票ウェイトに変換します。",
            1,
        ),
        (
            "流動ステークからチケットを作成し、追加し、ロック終了時に回収します。",
            "流動ステークから投票ステークを作成し、追加し、ロック終了時に回収します。",
            1,
        ),
        (
            "チケット重みは通常投票リスト経由で",
            "投票ステーク重みは通常投票リスト経由で",
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
    if "イベントチケット" not in excl:
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
        print("OK ja: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ja: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
