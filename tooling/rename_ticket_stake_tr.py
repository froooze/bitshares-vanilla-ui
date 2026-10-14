#!/usr/bin/env python3
"""Rename vote-locked "bilet" -> "oy stake" in vanilla/locales/tr.json.

Compound (per brief): sing "oy stake", plur "oy stakeler" (vote oy + stake
stake, both verbatim: tickets_title "Oy kilitli", tickets_body "oy ağırlığı/
oy listesi", pool.confirm_stake "Stake işlemini onayla", menu.d_tickets
"oy kilitli stake", pool.list_sub "Stake, LP payları..."). Case follows the
old string (Bilet->Oy stake, bilet->oy stake, Biletler->Oy stakeler).
Bare "stake/stakeler" where the sentence already says oy: title + body
line 1 keep "Oy kilitli" and take bare stakeler. Do NOT reuse the ballot
words "oy listesi" for this concept. Share=pay stays untouched.

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
Event-admission "etkinlik biletleri" in help.topic_assets-uia_body
EXCLUDED (different sense, kept).

Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_tr.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "tr.json")

TICKET_RE = re.compile("[Bb]ilet")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Bilet oluşturma",
        "Oy stake oluşturma",
    ),
    "account.op_ticket_update": (
        "Bilet güncelleme",
        "Oy stake güncelleme",
    ),
    "account.sum_ticket_create": (
        "%(amount)s tutarında bilet oluşturuldu",
        "%(amount)s tutarında oy stake oluşturuldu",
    ),
    "account.sum_ticket_update": (
        "Bilet %(ticket)s güncellendi",
        "Oy stake %(ticket)s güncellendi",
    ),
    "help.topic_tickets_title": (
        "Oy kilitli biletler",
        "Oy kilitli stakeler",
    ),
    "menu.p_tickets": (
        "Biletler",
        "Oy stakeler",
    ),
    "proposal.err_downgrade_unproven": (
        "Bilet düşürme kanıtlanmadı — güncel kilidi veya daha uzununu seçin.",
        "Oy stake düşürme kanıtlanmadı — güncel kilidi veya daha uzununu seçin.",
    ),
    "proposal.err_unknown_ticket": (
        "Bilinmeyen bilet.",
        "Bilinmeyen oy stake.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "İç bilet tutarı > 0 olmalı.",
        "İç oy stake tutarı > 0 olmalı.",
    ),
    "proposal.op_57": (
        "bilet oluşturma",
        "oy stake oluşturma",
    ),
    "proposal.op_58": (
        "bilet güncelleme",
        "oy stake güncelleme",
    ),
    "proposal.ticket": (
        "Bilet",
        "Oy stake",
    ),
    "proposals_ticket.title": (
        "Biletler",
        "Oy stakeler",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Bilet oluşturmayı onayla (op 57)",
        "Oy stake oluşturmayı onayla (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Bilet güncellemeyi onayla (op 58)",
        "Oy stake güncellemeyi onayla (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "Bilet oluşturulamadı (hesap, varlık ve tutarı denetleyin).",
        "Oy stake oluşturulamadı (hesap, varlık ve tutarı denetleyin).",
    ),
    "ticket.could_not_load_tickets": (
        "Biletler yüklenemedi.",
        "Oy stakeler yüklenemedi.",
    ),
    "ticket.create_ticket": (
        "Bilet oluştur",
        "Oy stake oluştur",
    ),
    "ticket.loading_my_tickets": (
        "Biletlerim yükleniyor…",
        "Oy stakelerim yükleniyor…",
    ),
    "ticket.loading_tickets": (
        "Biletler yükleniyor…",
        "Oy stakeler yükleniyor…",
    ),
    "ticket.my_tickets": (
        "Biletlerim",
        "Oy stakelerim",
    ),
    "ticket.review_ticket": (
        "Bileti incele",
        "Oy stakeyi incele",
    ),
    "ticket.ticket": (
        "Bilet",
        "Oy stake",
    ),
    "ticket.ticket_amount_must_be_0": (
        "Bilet tutarı > 0 olmalı.",
        "Oy stake tutarı > 0 olmalı.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Bilet oluşturuldu ve zincirde yeniden okundu.",
        "Oy stake oluşturuldu ve zincirde yeniden okundu.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Bilet güncellendi ve zincirde yeniden okundu.",
        "Oy stake güncellendi ve zincirde yeniden okundu.",
    ),
    "ticket.tickets": (
        "Biletler",
        "Oy stakeler",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Biletler silinemez (silme işlemi yok) — yukarıdaki satırlar kalıcıdır.",
        "Oy stakeler silinemez (silme işlemi yok) — yukarıdaki satırlar kalıcıdır.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Biletler oy ağırlığı için fon kilitler. Silme işlemi yoktur, her bilet satırı kalıcıdır.",
        "Oy stakeler oy ağırlığı için fon kilitler. Silme işlemi yoktur, her oy stake satırı kalıcıdır.",
    ),
    "tickets.title": (
        "Biletler",
        "Oy stakeler",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "havuz hareketleri, biletler, sohbet.",
            "havuz hareketleri, oy stakeler, sohbet.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Biletler](#/tickets)",
            "- [Oy stakeler](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Oy kilitli biletler pay artı zamanı oy ağırlığına çevirir",
            "Oy kilitli stakeler pay artı zamanı oy ağırlığına çevirir",
            1,
        ),
        (
            "Likit paydan bilet oluşturun, üstüne ekleyin, kilit bitince geri alın.",
            "Likit paydan oy stake oluşturun, üstüne ekleyin, kilit bitince geri alın.",
            1,
        ),
        (
            "Bilet ağırlığı normal oy listesi üzerinden",
            "Oy stake ağırlığı normal oy listesi üzerinden",
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
    if "etkinlik biletleri" not in excl:
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
        print("OK tr: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK tr: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
