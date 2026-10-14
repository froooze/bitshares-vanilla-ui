#!/usr/bin/env python3
"""Rename vote-locked "ticket" -> "stake de voto" in pt.json.

Compound: sing "stake de voto", plur "stakes de voto" (masc., articles
unchanged). Halves reused verbatim: "stake" (pool.confirm_stake
"Confirmar stake", vote.ballot_intro "Seu stake elege...") + "voto"
(help.topic_voting_body "seu voto", tickets_body "com voto travado",
"peso de voto").

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
No event-admission "ticket" sense in pt.json (assets-uia uses "ingressos"),
nothing excluded.
Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_pt.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

TICKET_RE = re.compile(r"[Tt]icket")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Cria\u00e7\u00e3o de ticket",
        "Cria\u00e7\u00e3o de stake de voto",
    ),
    "account.op_ticket_update": (
        "Atualiza\u00e7\u00e3o de ticket",
        "Atualiza\u00e7\u00e3o de stake de voto",
    ),
    "account.sum_ticket_create": (
        "Ticket %(amount)s criado",
        "Stake de voto %(amount)s criado",
    ),
    "account.sum_ticket_update": (
        "Ticket %(ticket)s atualizado",
        "Stake de voto %(ticket)s atualizado",
    ),
    "help.topic_tickets_title": (
        "Tickets com voto travado",
        "Stakes de voto travado",
    ),
    "menu.p_tickets": (
        "Tickets",
        "Stakes de voto",
    ),
    "proposal.err_downgrade_unproven": (
        "Downgrades de ticket n\u00e3o s\u00e3o comprovados \u2014 escolha a trava atual ou uma mais longa.",
        "Downgrades de stake de voto n\u00e3o s\u00e3o comprovados \u2014 escolha a trava atual ou uma mais longa.",
    ),
    "proposal.err_unknown_ticket": (
        "Ticket desconhecido.",
        "Stake de voto desconhecido.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "Valor do ticket interno deve ser > 0.",
        "Valor do stake de voto interno deve ser > 0.",
    ),
    "proposal.op_57": (
        "cria\u00e7\u00e3o de ticket",
        "cria\u00e7\u00e3o de stake de voto",
    ),
    "proposal.op_58": (
        "atualiza\u00e7\u00e3o de ticket",
        "atualiza\u00e7\u00e3o de stake de voto",
    ),
    "proposal.ticket": (
        "Ticket",
        "Stake de voto",
    ),
    "proposals_ticket.title": (
        "Tickets",
        "Stakes de voto",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Confirmar cria\u00e7\u00e3o de ticket (op 57)",
        "Confirmar cria\u00e7\u00e3o de stake de voto (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Confirmar atualiza\u00e7\u00e3o de ticket (op 58)",
        "Confirmar atualiza\u00e7\u00e3o de stake de voto (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "N\u00e3o foi poss\u00edvel montar o ticket (confira conta, ativo e valor).",
        "N\u00e3o foi poss\u00edvel montar o stake de voto (confira conta, ativo e valor).",
    ),
    "ticket.could_not_load_tickets": (
        "N\u00e3o foi poss\u00edvel carregar os tickets.",
        "N\u00e3o foi poss\u00edvel carregar os stakes de voto.",
    ),
    "ticket.create_ticket": (
        "Criar ticket",
        "Criar stake de voto",
    ),
    "ticket.loading_my_tickets": (
        "Carregando meus tickets\u2026",
        "Carregando meus stakes de voto\u2026",
    ),
    "ticket.loading_tickets": (
        "Carregando tickets\u2026",
        "Carregando stakes de voto\u2026",
    ),
    "ticket.my_tickets": (
        "Meus tickets",
        "Meus stakes de voto",
    ),
    "ticket.review_ticket": (
        "Revisar ticket",
        "Revisar stake de voto",
    ),
    "ticket.ticket": (
        "Ticket",
        "Stake de voto",
    ),
    "ticket.ticket_amount_must_be_0": (
        "O valor do ticket deve ser > 0.",
        "O valor do stake de voto deve ser > 0.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Ticket criado e relido on-chain.",
        "Stake de voto criado e relido on-chain.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Ticket atualizado e relido on-chain.",
        "Stake de voto atualizado e relido on-chain.",
    ),
    "ticket.tickets": (
        "Tickets",
        "Stakes de voto",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Tickets n\u00e3o podem ser exclu\u00eddos (n\u00e3o existe op de exclus\u00e3o) \u2014 as linhas acima s\u00e3o permanentes.",
        "Stakes de voto n\u00e3o podem ser exclu\u00eddos (n\u00e3o existe op de exclus\u00e3o) \u2014 as linhas acima s\u00e3o permanentes.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Tickets bloqueiam fundos para peso de voto. N\u00e3o h\u00e1 opera\u00e7\u00e3o de exclus\u00e3o, ent\u00e3o cada linha de ticket \u00e9 permanente.",
        "Stakes de voto bloqueiam fundos para peso de voto. N\u00e3o h\u00e1 opera\u00e7\u00e3o de exclus\u00e3o, ent\u00e3o cada linha de stake de voto \u00e9 permanente.",
    ),
    "tickets.title": (
        "Tickets",
        "Stakes de voto",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "movimentos de pool, tickets, chat.",
            "movimentos de pool, stakes de voto, chat.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Tickets](#/tickets)",
            "- [Stakes de voto](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Tickets com voto travado convertem",
            "Stakes de voto travado convertem",
            1,
        ),
        (
            "Crie um ticket de stake l\u00edquido",
            "Crie um stake de voto de stake l\u00edquido",
            1,
        ),
        (
            "Peso de ticket alimenta",
            "Peso de stake de voto alimenta",
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
        print("OK pt: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK pt: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
