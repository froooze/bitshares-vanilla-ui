#!/usr/bin/env python3
"""Rename vote-locked "ticket" -> "stake di voto" in it.json.

Compound: sing/plur "stake di voto" (masc. invariable — the dict already
uses invariable "stake" in plural contexts: help.topic_txbuilder_body
"trasferimenti, voti, stake"). Halves reused verbatim: "stake"
(pool.confirm_stake "Confermi stake", vote.ballot_intro "Il Suo stake...")
+ "voto" (vote.title "Voto", "a voto bloccato", "peso di voto").
Articles re-agree (il->lo, i->gli, del->dello, un->uno, dei->degli).

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
No event-admission "ticket" sense in it.json (assets-uia uses "biglietti"),
nothing excluded.
Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_it.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

TICKET_RE = re.compile(r"[Tt]icket")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Creazione ticket",
        "Creazione stake di voto",
    ),
    "account.op_ticket_update": (
        "Aggiornamento ticket",
        "Aggiornamento stake di voto",
    ),
    "account.sum_ticket_create": (
        "Ticket %(amount)s creato",
        "Stake di voto %(amount)s creato",
    ),
    "account.sum_ticket_update": (
        "Ticket %(ticket)s aggiornato",
        "Stake di voto %(ticket)s aggiornato",
    ),
    "help.topic_tickets_title": (
        "Ticket a voto bloccato",
        "Stake di voto bloccato",
    ),
    "menu.p_tickets": (
        "Ticket",
        "Stake di voto",
    ),
    "proposal.err_downgrade_unproven": (
        "I downgrade dei ticket non sono comprovati \u2014 scelga il lock corrente o uno pi\u00f9 lungo.",
        "I downgrade degli stake di voto non sono comprovati \u2014 scelga il lock corrente o uno pi\u00f9 lungo.",
    ),
    "proposal.err_unknown_ticket": (
        "Ticket sconosciuto.",
        "Stake di voto sconosciuto.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "L'importo del ticket interno deve essere > 0.",
        "L'importo dello stake di voto interno deve essere > 0.",
    ),
    "proposal.op_57": (
        "creazione ticket",
        "creazione stake di voto",
    ),
    "proposal.op_58": (
        "aggiornamento ticket",
        "aggiornamento stake di voto",
    ),
    "proposal.ticket": (
        "Ticket",
        "Stake di voto",
    ),
    "proposals_ticket.title": (
        "Ticket",
        "Stake di voto",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Confermi creazione ticket (op 57)",
        "Confermi creazione stake di voto (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Confermi aggiornamento ticket (op 58)",
        "Confermi aggiornamento stake di voto (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "Impossibile costruire il ticket (controlli account, asset e importo).",
        "Impossibile costruire lo stake di voto (controlli account, asset e importo).",
    ),
    "ticket.could_not_load_tickets": (
        "Impossibile caricare i ticket.",
        "Impossibile caricare gli stake di voto.",
    ),
    "ticket.create_ticket": (
        "Crei ticket",
        "Crei stake di voto",
    ),
    "ticket.loading_my_tickets": (
        "Caricamento miei ticket\u2026",
        "Caricamento miei stake di voto\u2026",
    ),
    "ticket.loading_tickets": (
        "Caricamento ticket\u2026",
        "Caricamento stake di voto\u2026",
    ),
    "ticket.my_tickets": (
        "Miei ticket",
        "Miei stake di voto",
    ),
    "ticket.review_ticket": (
        "Verifichi ticket",
        "Verifichi stake di voto",
    ),
    "ticket.ticket": (
        "Ticket",
        "Stake di voto",
    ),
    "ticket.ticket_amount_must_be_0": (
        "L\u2019importo ticket deve essere > 0.",
        "L\u2019importo stake di voto deve essere > 0.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Ticket creato e riletto on-chain.",
        "Stake di voto creato e riletto on-chain.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Ticket aggiornato e riletto on-chain.",
        "Stake di voto aggiornato e riletto on-chain.",
    ),
    "ticket.tickets": (
        "Ticket",
        "Stake di voto",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "I ticket non possono essere eliminati (nessuna op di eliminazione esiste) \u2014 le righe qui sopra sono permanenti.",
        "Gli stake di voto non possono essere eliminati (nessuna op di eliminazione esiste) \u2014 le righe qui sopra sono permanenti.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "I ticket bloccano fondi per peso di voto. Non esiste operazione di eliminazione, quindi ogni riga ticket \u00e8 permanente.",
        "Gli stake di voto bloccano fondi per peso di voto. Non esiste operazione di eliminazione, quindi ogni riga stake di voto \u00e8 permanente.",
    ),
    "tickets.title": (
        "Ticket",
        "Stake di voto",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "mosse pool, ticket, chat.",
            "mosse pool, stake di voto, chat.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Ticket](#/tickets)",
            "- [Stake di voto](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "I ticket a voto bloccato convertono",
            "Gli stake di voto bloccato convertono",
            1,
        ),
        (
            "Crei un ticket da stake liquido",
            "Crei uno stake di voto da stake liquido",
            1,
        ),
        (
            "Il peso del ticket alimenta",
            "Il peso dello stake di voto alimenta",
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
        print("OK it: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK it: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
