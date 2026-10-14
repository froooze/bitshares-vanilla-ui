#!/usr/bin/env python3
"""Rename treasury "trabajador/worker" -> "propuesta de grant" in es.json.

Scope: ONLY values carrying the treasury-proposal sense (36 keys). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from the dict's OWN attested words): sing "propuesta de
grant", plur "propuestas de grant" — "propuesta" (proposal.create_proposal
"Crear propuesta") + loanword "grant" (no Spanish grant noun is attested
anywhere in es.json; thing-first order mirrors the ticket wave's
"participación de voto"). Pay stays the attested "paga", budget the attested
"Presupuesto", refund "reembolso", recipients "beneficiarios" (attested in
help.topic_referrals_body "sin beneficiarios ocultos").

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_es.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

WORKER_RE = re.compile(r"worker|trabajador(?:es)?", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Creaci\u00f3n de trabajador",
        "Creaci\u00f3n de propuesta de grant",
    ),
    "account.sum_worker_create": (
        "Cre\u00f3 el trabajador \"%(name)s\"",
        "Cre\u00f3 la propuesta de grant \"%(name)s\"",
    ),
    "createworker.confirm_worker_op_34": (
        "Confirmar trabajador (op %(op)s)",
        "Confirmar propuesta de grant (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "No se pudo ver el worker.",
        "No se pudo ver la propuesta de grant.",
    ),
    "createworker.create_worker": (
        "Crear trabajador",
        "Crear propuesta de grant",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Redacta un trabajador (op %(op)s). La vista previa est\u00e1 en vivo; la revisi\u00f3n cita la comisi\u00f3n en vivo, y luego Firmar y enviar transmite la op %(op)s directamente \u2014 los trabajadores se crean con una op directa, no con una propuesta.",
        "Redacta una propuesta de grant (op %(op)s). La vista previa est\u00e1 en vivo; la revisi\u00f3n cita la comisi\u00f3n en vivo, y luego Firmar y enviar transmite la op %(op)s directamente \u2014 las propuestas de grant se crean con una op directa, no con una propuesta.",
    ),
    "createworker.enter_a_worker_name": (
        "Introduce un nombre de worker.",
        "Introduce un nombre de propuesta de grant.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "El propietario paga la comisi\u00f3n y recibe la paga del worker \u2014 usa una cuenta lifetime-member que controles.",
        "El propietario paga la comisi\u00f3n y recibe la paga de la propuesta de grant \u2014 usa una cuenta lifetime-member que controles.",
    ),
    "createworker.preview_worker": (
        "Ver worker",
        "Ver propuesta de grant",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Publicar un worker exige una cuenta lifetime-member \u2014 las cuentas b\u00e1sicas no pueden pagar esta comisi\u00f3n. El propietario de abajo ya debe estar actualizado.",
        "Publicar una propuesta de grant exige una cuenta lifetime-member \u2014 las cuentas b\u00e1sicas no pueden pagar esta comisi\u00f3n. El propietario de abajo ya debe estar actualizado.",
    ),
    "createworker.reading_existing_workers": (
        "Leyendo workers existentes\u2026",
        "Leyendo propuestas de grant existentes\u2026",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Falta el m\u00f3dulo de worker: no se pudo cargar js/account.js o js/format.js.",
        "Falta el m\u00f3dulo de propuesta de grant: no se pudo cargar js/account.js o js/format.js.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Falta el m\u00f3dulo de worker: no se pudo cargar js/asset-ops.js.",
        "Falta el m\u00f3dulo de propuesta de grant: no se pudo cargar js/asset-ops.js.",
    ),
    "createworker.worker_name": (
        "Nombre del worker ",
        "Nombre de la propuesta de grant ",
    ),
    "createworker.worker_preview_op_34": (
        "Vista previa del trabajador (op %(op)s)",
        "Vista previa de la propuesta de grant (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Trabajadores",
        "Propuestas de grant",
    ),
    "help.topic_voting_text": (
        "Vota testigos, comit\u00e9 y trabajadores, o delega en un apoderado.",
        "Vota testigos, comit\u00e9 y propuestas de grant, o delega en un apoderado.",
    ),
    "menu.d_voting": (
        "Testigos, comit\u00e9, trabajadores y proxies.",
        "Testigos, comit\u00e9, propuestas de grant y proxies.",
    ),
    "menu.p_worker": (
        "Crear trabajador",
        "Crear propuesta de grant",
    ),
    "news.voting_witnesses_committee_workers": (
        "Votaci\u00f3n \u2014 testigos, comit\u00e9, workers",
        "Votaci\u00f3n \u2014 testigos, comit\u00e9, propuestas de grant",
    ),
    "seo.desc_voting": (
        "Vota testigos, comit\u00e9 y trabajadores de BitShares. Cada voto se firma localmente en tu dispositivo.",
        "Vota testigos, comit\u00e9 y propuestas de grant de BitShares. Cada voto se firma localmente en tu dispositivo.",
    ),
    "vote.ballot_intro": (
        "Tu participaci\u00f3n elige testigos y comit\u00e9 y financia trabajadores \u2014 todos los conteos y pesos siguientes son lecturas en vivo de la cadena.",
        "Tu participaci\u00f3n elige testigos y comit\u00e9 y financia propuestas de grant \u2014 todos los conteos y pesos siguientes son lecturas en vivo de la cadena.",
    ),
    "vote.empty_hint": (
        " Las entradas aparecen cuando la cadena las trae \u2014 los trabajadores se proponen desde #/create-worker.",
        " Las entradas aparecen cuando la cadena las trae \u2014 las propuestas de grant se proponen desde #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Fondos para trabajadores no disponibles (",
        "Fondos para propuestas de grant no disponibles (",
    ),
    "vote.hide_legacy_label": (
        " Ocultar propuestas antiguas (siempre activo \u2014 los trabajadores vencidos se excluyen al cargar)",
        " Ocultar propuestas antiguas (siempre activo \u2014 las propuestas de grant vencidas se excluyen al cargar)",
    ),
    "vote.hide_legacy_title": (
        "Las listas de trabajadores vienen de get_all_workers(false); las filas vencidas nunca llegan.",
        "Las listas de propuestas de grant vienen de get_all_workers(false); las filas vencidas nunca llegan.",
    ),
    "vote.no_workers": (
        "Sin trabajadores encontrados. Las testnets suelen no tener \u2014 es v\u00e1lido, no es un error.",
        "Sin propuestas de grant encontradas. Las testnets suelen no tener \u2014 es v\u00e1lido, no es un error.",
    ),
    "vote.tab_workers": (
        "Trabajadores (",
        "Propuestas de grant (",
    ),
    "vote.worker_budget": (
        "Presupuesto para trabajadores: \u2014",
        "Presupuesto para propuestas de grant: \u2014",
    ),
    "vote.worker_budget_loading": (
        "Presupuesto para trabajadores: cargando\u2026",
        "Presupuesto para propuestas de grant: cargando\u2026",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "los trabajadores entregan proyectos pagados",
            "los beneficiarios de grant entregan proyectos pagados",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Crear trabajador](#/create-worker)",
            "- [Crear propuesta de grant](#/create-worker)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "alimenta votos de testigos, comit\u00e9 y trabajadores v\u00eda la lista normal",
            "alimenta votos de testigos, comit\u00e9 y propuestas de grant v\u00eda la lista normal",
            1,
        ),
    ],
    "help.topic_vesting_body": [
        (
            "pagos de trabajadores, recompensas por referidos",
            "pagos de propuestas de grant, recompensas por referidos",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "y qu\u00e9 proyectos de trabajadores se pagan.",
            "y qu\u00e9 proyectos de propuestas de grant se pagan.",
            1,
        ),
        (
            "ni trabajadores. Puede soltar el proxy",
            "ni propuestas de grant. Puede soltar el proxy",
            1,
        ),
        (
            "# Trabajadores y el presupuesto\nLos trabajadores son propuestas pagadas que suben de propuestas a activas cuando superan en votos al trabajador de reembolso, pagadas desde un presupuesto diario fijo por orden de llegada seg\u00fan rango. El detalle vive en el art\u00edculo Trabajadores.",
            "# Propuestas de grant y el presupuesto\nLas propuestas de grant son propuestas pagadas que suben de propuestas a activas cuando superan en votos a la propuesta de grant de reembolso, pagadas desde un presupuesto diario fijo por orden de llegada seg\u00fan rango. El detalle vive en el art\u00edculo Propuestas de grant.",
            1,
        ),
    ],
    "help.topic_workers_body": [
        (
            "Los trabajadores son propuestas para hacer algo \u00fatil",
            "Las propuestas de grant son propuestas para hacer algo \u00fatil",
            1,
        ),
        (
            "Los trabajadores propuestos juntan votos. Cuando una propuesta supera en votos al trabajador de reembolso se vuelve activa y empieza a cobrar;",
            "Las propuestas de grant en estado propuesto juntan votos. Cuando una propuesta supera en votos a la propuesta de grant de reembolso se vuelve activa y empieza a cobrar;",
            1,
        ),
        (
            "Todos los trabajadores comparten un presupuesto diario fijo",
            "Todas las propuestas de grant comparten un presupuesto diario fijo",
            1,
        ),
        (
            "si trabajadores de mayor rango ya consumieron los fondos del d\u00eda",
            "si propuestas de grant de mayor rango ya consumieron los fondos del d\u00eda",
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
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print("FAIL: es.json does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
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
            problems.append("ABORT %s: script's old string has no worker word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip):
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
        cur = dig(d, key)
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
        print("OK es: %d full + %d snippet keys renamed to propuesta(s) de grant" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK es: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
