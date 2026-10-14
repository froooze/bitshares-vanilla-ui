#!/usr/bin/env python3
"""Rename "testigo" -> "validador de bloques" in vanilla/locales/es.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s / %(ticket)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).

Compound (per brief, from locale's own attested words): sing
"validador de bloques", plur "validadores de bloques" — "bloque"/"bloques"
plus the "validar/validan/validación" stem ("productores de bloques" is the
help article's *definition*, not the term). Title case at sentence/title
start ("Validador(es) de bloques"), lowercase elsewhere. The approved term
is the full compound everywhere — bare "validador" alone is not enough.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a testigo-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\n" formatting.

Usage: python3 tooling/rename_witness_validator_es.py [--apply]
Dry run (asserts only) by default; --apply writes es.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ES = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

WITNESS_RE = re.compile(r"testigo", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_witness_join": (
        "Ingreso como testigo",
        "Ingreso como validador de bloques",
    ),
    "account.op_witness_update": (
        "Actualizaci\xf3n de testigo",
        "Actualizaci\xf3n de validador de bloques",
    ),
    "account.sum_witness_create": (
        "Se convirti\xf3 en testigo: %(account)s",
        "Se convirti\xf3 en validador de bloques: %(account)s",
    ),
    "account.sum_witness_update": (
        "Actualiz\xf3 al testigo %(account)s",
        "Actualiz\xf3 al validador de bloques %(account)s",
    ),
    "asset.witness_fed_note": (
        "Con feed de testigos: todos los testigos activos pueden publicar.",
        "Con feed de validadores de bloques: todos los validadores de bloques activos pueden publicar.",
    ),
    "explorer.stat_wit": (
        "Testigos activos",
        "Validadores de bloques activos",
    ),
    "explorer.th_witness": (
        "Testigo",
        "Validador de bloques",
    ),
    "explorer.witness_row": (
        "Testigo",
        "Validador de bloques",
    ),
    "help.topic_assets-mpa_text": (
        "Smartcoins respaldadas por colateral con feeds de precios de los testigos.",
        "Smartcoins respaldadas por colateral con feeds de precios de los validadores de bloques.",
    ),
    "help.topic_glossary_text": (
        "Nombres usados en esta billetera: objetos (1.x.y), operaciones, testigos, comit\xe9.",
        "Nombres usados en esta billetera: objetos (1.x.y), operaciones, validadores de bloques, comit\xe9.",
    ),
    "help.topic_voting_text": (
        "Vota testigos, comit\xe9 y propuestas de grant, o delega en un apoderado.",
        "Vota validadores de bloques, comit\xe9 y propuestas de grant, o delega en un apoderado.",
    ),
    "help.topic_witnesses_title": (
        "Testigos",
        "Validadores de bloques",
    ),
    "menu.d_asset_feed": (
        "Publica feeds de precios como emisor o testigo.",
        "Publica feeds de precios como emisor o validador de bloques.",
    ),
    "menu.d_voting": (
        "Testigos, comit\xe9, propuestas de grant y proxies.",
        "Validadores de bloques, comit\xe9, propuestas de grant y proxies.",
    ),
    "news.voting_witnesses_committee_workers": (
        "Votaci\xf3n \u2014 testigos, comit\xe9, propuestas de grant",
        "Votaci\xf3n \u2014 validadores de bloques, comit\xe9, propuestas de grant",
    ),
    "seo.desc_voting": (
        "Vota testigos, comit\xe9 y propuestas de grant de BitShares. Cada voto se firma localmente en tu dispositivo.",
        "Vota validadores de bloques, comit\xe9 y propuestas de grant de BitShares. Cada voto se firma localmente en tu dispositivo.",
    ),
    "seo.title_voting": (
        "Vota testigos \u2014 BitShares Wallet",
        "Vota validadores de bloques \u2014 BitShares Wallet",
    ),
    "splash.pulse_witnesses": (
        "Testigos",
        "Validadores de bloques",
    ),
    "vote.ballot_intro": (
        "Tu participaci\xf3n elige testigos y comit\xe9 y financia propuestas de grant \u2014 todos los conteos y pesos siguientes son lecturas en vivo de la cadena.",
        "Tu participaci\xf3n elige validadores de bloques y comit\xe9 y financia propuestas de grant \u2014 todos los conteos y pesos siguientes son lecturas en vivo de la cadena.",
    ),
    "vote.confirm_witness_update_op_21": (
        "Confirmar actualizaci\xf3n de testigo (op %(op)s)",
        "Confirmar actualizaci\xf3n de validador de bloques (op %(op)s)",
    ),
    "vote.empty_list": (
        "El nodo no devolvi\xf3 testigos ni miembros del comit\xe9.",
        "El nodo no devolvi\xf3 validadores de bloques ni miembros del comit\xe9.",
    ),
    "vote.join_as_witness": (
        "Unirse como testigo",
        "Unirse como validador de bloques",
    ),
    "vote.no_witness_object_for_this_account_use_join_a": (
        "Sin objeto testigo para esta cuenta \u2014 usa Unirse como testigo en su lugar.",
        "Sin objeto validador de bloques para esta cuenta \u2014 usa Unirse como validador de bloques en su lugar.",
    ),
    "vote.tab_witnesses": (
        "Testigos (",
        "Validadores de bloques (",
    ),
    "vote.update_witness": (
        "Actualizar testigo",
        "Actualizar validador de bloques",
    ),
    "vote.witness": (
        "Testigo",
        "Validador de bloques",
    ),
    "vote.witness_updated": (
        "Testigo actualizado",
        "Validador de bloques actualizado",
    ),
}

SNIPPETS = {
    "help.topic_assets-mpa_body": [
        (
            "los testigos publican los feeds de precio del mundo real",
            "los validadores de bloques publican los feeds de precio del mundo real",
            1,
        ),
    ],
    "help.topic_assets-private_body": [
        (
            "no los testigos \u2014 elige qui\xe9n puede publicar",
            "no los validadores de bloques \u2014 elige qui\xe9n puede publicar",
            1,
        ),
        (
            "sin esperar feeds de testigos.",
            "sin esperar feeds de validadores de bloques.",
            1,
        ),
        (
            "no al de los testigos:",
            "no al de los validadores de bloques:",
            1,
        ),
    ],
    "help.topic_blockchain_body": [
        (
            "preferidos, llamados testigos, y los m\xe1s votados",
            "preferidos, llamados validadores de bloques, y los m\xe1s votados",
            1,
        ),
        (
            "contra el trabajo de los testigos,",
            "contra el trabajo de los validadores de bloques,",
            1,
        ),
        (
            "Ver los art\xedculos Votaci\xf3n y Testigos.",
            "Ver los art\xedculos Votaci\xf3n y Validadores de bloques.",
            1,
        ),
    ],
    "help.topic_committee_body": [
        (
            "Como los testigos, los miembros",
            "Como los validadores de bloques, los miembros",
            1,
        ),
    ],
    "help.topic_dex-shorting_body": [
        (
            "el respaldo m\xednimo de los testigos.",
            "el respaldo m\xednimo de los validadores de bloques.",
            1,
        ),
    ],
    "help.topic_glossary_body": [
        (
            "propuestas, testigos \u2014 casi todo",
            "propuestas, validadores de bloques \u2014 casi todo",
            1,
        ),
        (
            "Los testigos producen bloques;",
            "Los validadores de bloques producen bloques;",
            1,
        ),
    ],
    "help.topic_settings_body": [
        (
            "participaci\xf3n de testigos y retraso",
            "participaci\xf3n de validadores de bloques y retraso",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Testigos](#/explorer/witnesses)",
            "- [Validadores de bloques](#/explorer/witnesses)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "alimenta votos de testigos, comit\xe9",
            "alimenta votos de validadores de bloques, comit\xe9",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "no puede votar directo por testigos, miembros",
            "no puede votar directo por validadores de bloques, miembros",
            1,
        ),
        (
            "# Testigos\nLos testigos construyen y firman bloques",
            "# Validadores de bloques\nLos validadores de bloques construyen y firman bloques",
            1,
        ),
        (
            "El detalle vive en el art\xedculo Testigos.",
            "El detalle vive en el art\xedculo Validadores de bloques.",
            1,
        ),
    ],
    "help.topic_witnesses_body": [
        (
            "# Qu\xe9 hacen los testigos\nLos testigos son los productores",
            "# Qu\xe9 hacen los validadores de bloques\nLos validadores de bloques son los productores",
            1,
        ),
        (
            "Puede votar por cuantos testigos quiera,",
            "Puede votar por cuantos validadores de bloques quiera,",
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
    raw = open(ES, encoding="utf-8").read()
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
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no testigo-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script's old string has no testigo word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no testigo-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no testigo word (script bug): %r" % (key, old_snip))
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

    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        if WITNESS_RE.search(v):
            print("FAIL: %s still carries a testigo word: %r" % (key, v[:120]))
            return 1

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
        open(ES, "w", encoding="utf-8").write(out)
        print("OK es: %d full + %d snippet keys renamed to validador de bloques" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK es: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
