#!/usr/bin/env python3
"""Rename vote-locked "ticket" -> "participacion de voto" in es.json.

Compound: sing "participaci\u00f3n de voto", plur "participaciones de voto"
(fem.). Halves reused verbatim from the shipped dict: "participaci\u00f3n"
(pool.confirm_stake "Confirmar participaci\u00f3n", vote.ballot_intro
"Tu participaci\u00f3n elige testigos...") + "voto"
(help.topic_tickets_body "peso de voto", "con voto bloqueado").
Articles/adjectives re-agree feminine (el->la, los->las, -o->-a).

Keys unchanged. Placeholders (%(ticket)s, %(amount)s) byte-identical.
Route "#/tickets" unchanged. No event-admission "ticket" sense exists in
es.json (assets-uia uses "boletos de eventos"), so nothing is excluded.

Gates G1-G5: same as rename_ticket_stake_de.py (assert currents first).
Usage: python3 tooling/rename_ticket_stake_es.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

TICKET_RE = re.compile(r"[Tt]icket")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Creaci\u00f3n de ticket",
        "Creaci\u00f3n de participaci\u00f3n de voto",
    ),
    "account.op_ticket_update": (
        "Actualizaci\u00f3n de ticket",
        "Actualizaci\u00f3n de participaci\u00f3n de voto",
    ),
    "account.sum_ticket_create": (
        "Cre\u00f3 el ticket %(amount)s",
        "Cre\u00f3 la participaci\u00f3n de voto %(amount)s",
    ),
    "account.sum_ticket_update": (
        "Actualiz\u00f3 el ticket %(ticket)s",
        "Actualiz\u00f3 la participaci\u00f3n de voto %(ticket)s",
    ),
    "help.topic_tickets_title": (
        "Tickets con voto bloqueado",
        "Participaciones de voto bloqueado",
    ),
    "menu.p_tickets": (
        "Tickets",
        "Participaciones de voto",
    ),
    "proposal.err_downgrade_unproven": (
        "Las reducciones de ticket no est\u00e1n probadas \u2014 elija el bloqueo actual o uno m\u00e1s largo.",
        "Las reducciones de participaci\u00f3n de voto no est\u00e1n probadas \u2014 elija el bloqueo actual o uno m\u00e1s largo.",
    ),
    "proposal.err_unknown_ticket": (
        "Ticket desconocido.",
        "Participaci\u00f3n de voto desconocida.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "El monto del ticket interno debe ser > 0.",
        "El monto de la participaci\u00f3n de voto interna debe ser > 0.",
    ),
    "proposal.op_57": (
        "creaci\u00f3n de ticket",
        "creaci\u00f3n de participaci\u00f3n de voto",
    ),
    "proposal.op_58": (
        "actualizaci\u00f3n de ticket",
        "actualizaci\u00f3n de participaci\u00f3n de voto",
    ),
    "proposal.ticket": (
        "Ticket",
        "Participaci\u00f3n de voto",
    ),
    "proposals_ticket.title": (
        "Tickets",
        "Participaciones de voto",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Confirmar creaci\u00f3n de ticket (op 57)",
        "Confirmar creaci\u00f3n de participaci\u00f3n de voto (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Confirmar actualizaci\u00f3n de ticket (op 58)",
        "Confirmar actualizaci\u00f3n de participaci\u00f3n de voto (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "No se pudo construir el ticket (revisa cuenta, activo y cantidad).",
        "No se pudo construir la participaci\u00f3n de voto (revisa cuenta, activo y cantidad).",
    ),
    "ticket.could_not_load_tickets": (
        "No se pudieron cargar los tickets.",
        "No se pudieron cargar las participaciones de voto.",
    ),
    "ticket.create_ticket": (
        "Crear ticket",
        "Crear participaci\u00f3n de voto",
    ),
    "ticket.loading_my_tickets": (
        "Cargando mis tickets\u2026",
        "Cargando mis participaciones de voto\u2026",
    ),
    "ticket.loading_tickets": (
        "Cargando tickets\u2026",
        "Cargando participaciones de voto\u2026",
    ),
    "ticket.my_tickets": (
        "Mis tickets",
        "Mis participaciones de voto",
    ),
    "ticket.review_ticket": (
        "Revisar ticket",
        "Revisar participaci\u00f3n de voto",
    ),
    "ticket.ticket": (
        "Ticket",
        "Participaci\u00f3n de voto",
    ),
    "ticket.ticket_amount_must_be_0": (
        "La cantidad del ticket debe ser > 0.",
        "La cantidad de la participaci\u00f3n de voto debe ser > 0.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Ticket creado y rele\u00eddo en la cadena.",
        "Participaci\u00f3n de voto creada y rele\u00edda en la cadena.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Ticket actualizado y rele\u00eddo en la cadena.",
        "Participaci\u00f3n de voto actualizada y rele\u00edda en la cadena.",
    ),
    "ticket.tickets": (
        "Tickets",
        "Participaciones de voto",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Los tickets no se pueden eliminar (no existe op de borrado) \u2014 las filas de arriba son permanentes.",
        "Las participaciones de voto no se pueden eliminar (no existe op de borrado) \u2014 las filas de arriba son permanentes.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Los tickets bloquean fondos para peso de voto. No hay operaci\u00f3n de borrado, as\u00ed que cada fila de ticket es permanente.",
        "Las participaciones de voto bloquean fondos para peso de voto. No hay operaci\u00f3n de borrado, as\u00ed que cada fila de participaci\u00f3n de voto es permanente.",
    ),
    "tickets.title": (
        "Tickets",
        "Participaciones de voto",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "movimientos de pools, tickets, chat.",
            "movimientos de pools, participaciones de voto, chat.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Tickets](#/tickets)",
            "- [Participaciones de voto](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Los tickets con voto bloqueado convierten",
            "Las participaciones de voto bloqueado convierten",
            1,
        ),
        (
            "Cree un ticket desde participaci\u00f3n l\u00edquida, aum\u00e9ntelo y recl\u00e1melo cuando termine el bloqueo.",
            "Cree una participaci\u00f3n de voto desde participaci\u00f3n l\u00edquida, aum\u00e9ntela y recl\u00e1mela cuando termine el bloqueo.",
            1,
        ),
        (
            "El peso del ticket alimenta",
            "El peso de la participaci\u00f3n de voto alimenta",
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
        print("OK es: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK es: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
