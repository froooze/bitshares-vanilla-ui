#!/usr/bin/env python3
"""Rename vote-locked "Ticket" -> "Voting-Stake" in vanilla/locales/de.json.

Scope: ONLY values carrying the vote-locked sense. Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * help.topic_assets-uia_body — "Veranstaltungstickets" is the
    event-admission sense, not the vote-locked one.
  * placeholders — %(ticket)s / %(amount)s stay byte-identical (code-bound).
  * route targets — "#/tickets" stays (the router path /tickets is code).

Compound (per brief): sing "Voting-Stake", plur "Voting-Stakes",
mirroring existing German forms ("Stake" in vote.ballot_intro "Ihr Stake",
"Voting-" in help.topic_txbuilder_body "Voting- oder Pool-Stake-Seiten",
masc. "Vote-gesperrter Stake" in menu.d_tickets).

Safety gates (assert before write):
  G1 every target's CURRENT value contains a ticket-family word, else abort.
  G2 every target's current value EQUALS the expected old string, else abort.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_ticket_stake_de.py [--apply]
Dry run (asserts only) by default; --apply writes de.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

TICKET_RE = re.compile(r"[Tt]icket")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "account.op_ticket_create": (
        "Ticket-Erstellung",
        "Voting-Stake-Erstellung",
    ),
    "account.op_ticket_update": (
        "Ticket-Update",
        "Voting-Stake-Update",
    ),
    "account.sum_ticket_create": (
        "Hat das Ticket %(amount)s erstellt",
        "Hat den Voting-Stake %(amount)s erstellt",
    ),
    "account.sum_ticket_update": (
        "Hat das Ticket %(ticket)s aktualisiert",
        "Hat den Voting-Stake %(ticket)s aktualisiert",
    ),
    "help.topic_tickets_title": (
        "Stimmsperr-Tickets",
        "Stimmsperr-Voting-Stakes",
    ),
    "menu.p_tickets": (
        "Tickets",
        "Voting-Stakes",
    ),
    "proposal.err_downgrade_unproven": (
        "Ticket-Downgrades sind unbewiesen \u2014 w\u00e4hlen Sie den aktuellen Lock oder einen l\u00e4ngeren.",
        "Voting-Stake-Downgrades sind unbewiesen \u2014 w\u00e4hlen Sie den aktuellen Lock oder einen l\u00e4ngeren.",
    ),
    "proposal.err_unknown_ticket": (
        "Unbekanntes Ticket.",
        "Unbekannter Voting-Stake.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "Innerer Ticket-Betrag muss > 0 sein.",
        "Innerer Voting-Stake-Betrag muss > 0 sein.",
    ),
    "proposal.op_57": (
        "Ticket-Erstellung",
        "Voting-Stake-Erstellung",
    ),
    "proposal.op_58": (
        "Ticket-Aktualisierung",
        "Voting-Stake-Aktualisierung",
    ),
    "proposal.ticket": (
        "Ticket",
        "Voting-Stake",
    ),
    "proposals_ticket.title": (
        "Tickets",
        "Voting-Stakes",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Ticket-Erstellung best\u00e4tigen (Op 57)",
        "Voting-Stake-Erstellung best\u00e4tigen (Op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Ticket-Update best\u00e4tigen (Op 58)",
        "Voting-Stake-Update best\u00e4tigen (Op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "Ticket konnte nicht erstellt werden (Konto, Asset und Betrag pr\u00fcfen).",
        "Voting-Stake konnte nicht erstellt werden (Konto, Asset und Betrag pr\u00fcfen).",
    ),
    "ticket.could_not_load_tickets": (
        "Tickets konnten nicht geladen werden.",
        "Voting-Stakes konnten nicht geladen werden.",
    ),
    "ticket.create_ticket": (
        "Ticket erstellen",
        "Voting-Stake erstellen",
    ),
    "ticket.loading_my_tickets": (
        "Meine Tickets werden geladen\u2026",
        "Meine Voting-Stakes werden geladen\u2026",
    ),
    "ticket.loading_tickets": (
        "Tickets werden geladen\u2026",
        "Voting-Stakes werden geladen\u2026",
    ),
    "ticket.my_tickets": (
        "Meine Tickets",
        "Meine Voting-Stakes",
    ),
    "ticket.review_ticket": (
        "Ticket pr\u00fcfen",
        "Voting-Stake pr\u00fcfen",
    ),
    "ticket.ticket": (
        "Ticket",
        "Voting-Stake",
    ),
    "ticket.ticket_amount_must_be_0": (
        "Ticket-Betrag muss > 0 sein.",
        "Voting-Stake-Betrag muss > 0 sein.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Ticket erstellt und on-chain neu gelesen.",
        "Voting-Stake erstellt und on-chain neu gelesen.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Ticket aktualisiert und on-chain neu gelesen.",
        "Voting-Stake aktualisiert und on-chain neu gelesen.",
    ),
    "ticket.tickets": (
        "Tickets",
        "Voting-Stakes",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Tickets k\u00f6nnen nicht gel\u00f6scht werden (kein L\u00f6sch-Op existiert) \u2014 obige Zeilen sind dauerhaft.",
        "Voting-Stakes k\u00f6nnen nicht gel\u00f6scht werden (kein L\u00f6sch-Op existiert) \u2014 obige Zeilen sind dauerhaft.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Tickets sperren Gelder f\u00fcr Stimmgewicht. Es gibt keine L\u00f6schoperation, daher ist jede Ticketzeile dauerhaft.",
        "Voting-Stakes sperren Gelder f\u00fcr Stimmgewicht. Es gibt keine L\u00f6schoperation, daher ist jede Voting-Stake-Zeile dauerhaft.",
    ),
    "tickets.title": (
        "Tickets",
        "Voting-Stakes",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "Transfers, Orders, Stimmen, Pool-Bewegungen, Tickets, Chat.",
            "Transfers, Orders, Stimmen, Pool-Bewegungen, Voting-Stakes, Chat.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Tickets](#/tickets)",
            "- [Voting-Stakes](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Stimmsperr-Tickets wandeln",
            "Stimmsperr-Voting-Stakes wandeln",
            1,
        ),
        (
            "Erstellen Sie ein Ticket aus liquidem Stake, stocken Sie auf und fordern Sie es nach Lock-Ende zur\u00fcck.",
            "Erstellen Sie einen Voting-Stake aus liquidem Stake, stocken Sie auf und fordern Sie ihn nach Lock-Ende zur\u00fcck.",
            1,
        ),
        (
            "Ticket-Gewicht speist",
            "Voting-Stake-Gewicht speist",
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
    raw = open(DE, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    # G1/G2: full-value keys.
    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: current value has no ticket-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not TICKET_RE.search(old):
            problems.append("ABORT %s: script's old string has no ticket word (script bug)" % key)
            continue

    # G1: snippet keys.
    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: current value has no ticket-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not TICKET_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no ticket word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    # Exclusion guard: event-admission sense must still be intact afterwards.
    excl = dig(d, "help.topic_assets-uia_body")
    if "Veranstaltungstickets" not in excl:
        problems.append("ABORT help.topic_assets-uia_body: event sense changed unexpectedly")

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    # Apply.
    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        # Route targets in the sitemap must be byte-identical.
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    # G4: structure.
    after_keys = set(flatten(d))
    if after_keys != before_keys:
        print("FAIL: key set drift")
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
        open(DE, "w", encoding="utf-8").write(out)
        print("OK de: %d full + %d snippet keys renamed to Voting-Stake(s)" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK de: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
