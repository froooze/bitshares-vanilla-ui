#!/usr/bin/env python3
"""Rename vote-locked "ticket" -> "stake de vote" in fr.json.

Compound: sing "stake de vote", plur "stakes de vote" (masc., articles
unchanged). Halves reused verbatim: "stake" (pool.confirm_stake
"Confirmer le stake", vote.ballot_intro "Votre stake \u00e9lit...") + "vote"
(vote.title "Votes", help.topic_tickets_title "Tickets \u00e0 vote
verrouill\u00e9", "poids de vote").

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
No event-admission "ticket" sense in fr.json (assets-uia uses "billets
d'\u00e9v\u00e9nements"), nothing excluded. The stake-sense "mise" lines are
NOT touched (glossary flags them for a later pass).
Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_fr.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

TICKET_RE = re.compile(r"[Tt]icket")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Cr\u00e9ation de ticket",
        "Cr\u00e9ation de stake de vote",
    ),
    "account.op_ticket_update": (
        "Mise \u00e0 jour de ticket",
        "Mise \u00e0 jour de stake de vote",
    ),
    "account.sum_ticket_create": (
        "Ticket %(amount)s cr\u00e9\u00e9",
        "Stake de vote %(amount)s cr\u00e9\u00e9",
    ),
    "account.sum_ticket_update": (
        "Ticket %(ticket)s mis \u00e0 jour",
        "Stake de vote %(ticket)s mis \u00e0 jour",
    ),
    "help.topic_tickets_title": (
        "Tickets \u00e0 vote verrouill\u00e9",
        "Stakes de vote verrouill\u00e9",
    ),
    "menu.p_tickets": (
        "Tickets",
        "Stakes de vote",
    ),
    "proposal.err_downgrade_unproven": (
        "Les r\u00e9trogradations de ticket ne sont pas prouv\u00e9es \u2014 choisissez le verrouillage actuel ou un plus long.",
        "Les r\u00e9trogradations de stake de vote ne sont pas prouv\u00e9es \u2014 choisissez le verrouillage actuel ou un plus long.",
    ),
    "proposal.err_unknown_ticket": (
        "Ticket inconnu.",
        "Stake de vote inconnu.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "Le montant du ticket interne doit \u00eatre > 0.",
        "Le montant du stake de vote interne doit \u00eatre > 0.",
    ),
    "proposal.op_57": (
        "cr\u00e9ation de ticket",
        "cr\u00e9ation de stake de vote",
    ),
    "proposal.op_58": (
        "mise \u00e0 jour de ticket",
        "mise \u00e0 jour de stake de vote",
    ),
    "proposal.ticket": (
        "Ticket",
        "Stake de vote",
    ),
    "proposals_ticket.title": (
        "Tickets",
        "Stakes de vote",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Confirmer la cr\u00e9ation du ticket (op 57)",
        "Confirmer la cr\u00e9ation du stake de vote (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Confirmer la mise \u00e0 jour du ticket (op 58)",
        "Confirmer la mise \u00e0 jour du stake de vote (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "Impossible de construire le ticket (v\u00e9rifiez le compte, l'actif et le montant).",
        "Impossible de construire le stake de vote (v\u00e9rifiez le compte, l'actif et le montant).",
    ),
    "ticket.could_not_load_tickets": (
        "Impossible de charger les tickets.",
        "Impossible de charger les stakes de vote.",
    ),
    "ticket.create_ticket": (
        "Cr\u00e9er un ticket",
        "Cr\u00e9er un stake de vote",
    ),
    "ticket.loading_my_tickets": (
        "Chargement de mes tickets\u2026",
        "Chargement de mes stakes de vote\u2026",
    ),
    "ticket.loading_tickets": (
        "Chargement des tickets\u2026",
        "Chargement des stakes de vote\u2026",
    ),
    "ticket.my_tickets": (
        "Mes tickets",
        "Mes stakes de vote",
    ),
    "ticket.review_ticket": (
        "V\u00e9rifier le ticket",
        "V\u00e9rifier le stake de vote",
    ),
    "ticket.ticket": (
        "Ticket",
        "Stake de vote",
    ),
    "ticket.ticket_amount_must_be_0": (
        "Le montant du ticket doit \u00eatre > 0.",
        "Le montant du stake de vote doit \u00eatre > 0.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Ticket cr\u00e9\u00e9 et relu sur la cha\u00eene.",
        "Stake de vote cr\u00e9\u00e9 et relu sur la cha\u00eene.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Ticket mis \u00e0 jour et relu sur la cha\u00eene.",
        "Stake de vote mis \u00e0 jour et relu sur la cha\u00eene.",
    ),
    "ticket.tickets": (
        "Tickets",
        "Stakes de vote",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Les tickets ne peuvent pas \u00eatre supprim\u00e9s (aucune op de suppression n'existe) \u2014 les lignes ci-dessus sont permanentes.",
        "Les stakes de vote ne peuvent pas \u00eatre supprim\u00e9s (aucune op de suppression n'existe) \u2014 les lignes ci-dessus sont permanentes.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Les tickets verrouillent des fonds pour le poids de vote. Il n'existe aucune op\u00e9ration de suppression, donc chaque ligne de ticket est permanente.",
        "Les stakes de vote verrouillent des fonds pour le poids de vote. Il n'existe aucune op\u00e9ration de suppression, donc chaque ligne de stake de vote est permanente.",
    ),
    "tickets.title": (
        "Tickets",
        "Stakes de vote",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "mouvements de pool, tickets, chat.",
            "mouvements de pool, stakes de vote, chat.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Tickets](#/tickets)",
            "- [Stakes de vote](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Les tickets \u00e0 vote verrouill\u00e9 convertissent",
            "Les stakes de vote verrouill\u00e9 convertissent",
            1,
        ),
        (
            "Cr\u00e9ez un ticket depuis la mise liquide",
            "Cr\u00e9ez un stake de vote depuis la mise liquide",
            1,
        ),
        (
            "Le poids des tickets alimente",
            "Le poids des stakes de vote alimente",
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
        print("OK fr: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK fr: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
