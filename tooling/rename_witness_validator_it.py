#!/usr/bin/env python3
"""Rename "witness" -> "validatore di blocchi" in vanilla/locales/it.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).

Compound (per brief, from locale's own attested words): sing
"validatore di blocchi", plur "validatori di blocchi" — "blocco"/"blocchi"
plus the "valido/convalida" stem ("produttori di blocchi" is the help
article's *definition*, not the term). Title case at sentence/title start
("Validatore/Validatori di blocchi"), lowercase elsewhere. The old loanword
was number-invariant ("I witness", "tutti i witness attivi"); the new
compound marks number explicitly. The approved term is the full compound
everywhere — bare "validatore" alone is not enough.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a witness-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\n" formatting.

Usage: python3 tooling/rename_witness_validator_it.py [--apply]
Dry run (asserts only) by default; --apply writes it.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IT = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

WITNESS_RE = re.compile(r"witness", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_witness_join": (
        "Adesione come witness",
        "Adesione come validatore di blocchi",
    ),
    "account.op_witness_update": (
        "Aggiornamento witness",
        "Aggiornamento validatore di blocchi",
    ),
    "account.sum_witness_create": (
        "Diventato witness: %(account)s",
        "Diventato validatore di blocchi: %(account)s",
    ),
    "account.sum_witness_update": (
        "Witness %(account)s aggiornato",
        "Validatore di blocchi %(account)s aggiornato",
    ),
    "asset.witness_fed_note": (
        "Alimentato dai witness: tutti i witness attivi possono pubblicare.",
        "Alimentato dai validatori di blocchi: tutti i validatori di blocchi attivi possono pubblicare.",
    ),
    "explorer.stat_wit": (
        "Witness attivi",
        "Validatori di blocchi attivi",
    ),
    "explorer.th_witness": (
        "Witness",
        "Validatore di blocchi",
    ),
    "explorer.witness_row": (
        "Witness",
        "Validatore di blocchi",
    ),
    "help.topic_assets-mpa_text": (
        "Smartcoin garantiti da collaterale con feed di prezzo dai witness.",
        "Smartcoin garantiti da collaterale con feed di prezzo dai validatori di blocchi.",
    ),
    "help.topic_glossary_text": (
        "Nomi usati in questo wallet: oggetti (1.x.y), operazioni, witness, comitato.",
        "Nomi usati in questo wallet: oggetti (1.x.y), operazioni, validatori di blocchi, comitato.",
    ),
    "help.topic_voting_text": (
        "Voti witness, comitato, proposte di grant \u2014 oppure deleghi a un proxy.",
        "Voti validatori di blocchi, comitato, proposte di grant \u2014 oppure deleghi a un proxy.",
    ),
    "help.topic_witnesses_title": (
        "Witness",
        "Validatori di blocchi",
    ),
    "menu.d_asset_feed": (
        "Pubblichi feed di prezzo come emittente o witness.",
        "Pubblichi feed di prezzo come emittente o validatore di blocchi.",
    ),
    "menu.d_voting": (
        "Witness, comitato, proposte di grant e proxy.",
        "Validatori di blocchi, comitato, proposte di grant e proxy.",
    ),
    "news.voting_witnesses_committee_workers": (
        "Voto \u2014 witness, comitato, proposte di grant",
        "Voto \u2014 validatori di blocchi, comitato, proposte di grant",
    ),
    "seo.desc_voting": (
        "Voti i witness, i membri del comitato e le proposte di grant di BitShares. Ogni scheda \xe8 firmata in locale sul Suo dispositivo.",
        "Voti i validatori di blocchi, i membri del comitato e le proposte di grant di BitShares. Ogni scheda \xe8 firmata in locale sul Suo dispositivo.",
    ),
    "seo.title_voting": (
        "Voto ai witness \u2014 BitShares Wallet",
        "Voto ai validatori di blocchi \u2014 BitShares Wallet",
    ),
    "splash.pulse_witnesses": (
        "Witness",
        "Validatori di blocchi",
    ),
    "vote.ballot_intro": (
        "Il Suo stake elegge witness e comitato e finanzia le proposte di grant \u2014 tutti i conteggi e le quote qui sotto sono letture live della chain.",
        "Il Suo stake elegge validatori di blocchi e comitato e finanzia le proposte di grant \u2014 tutti i conteggi e le quote qui sotto sono letture live della chain.",
    ),
    "vote.confirm_witness_update_op_21": (
        "Confermi l'aggiornamento del witness (op %(op)s)",
        "Confermi l'aggiornamento del validatore di blocchi (op %(op)s)",
    ),
    "vote.empty_list": (
        "Il nodo non ha restituito witness n\xe9 membri del comitato.",
        "Il nodo non ha restituito validatori di blocchi n\xe9 membri del comitato.",
    ),
    "vote.join_as_witness": (
        "Aderisca come witness",
        "Aderisca come validatore di blocchi",
    ),
    "vote.no_witness_object_for_this_account_use_join_a": (
        "Nessun oggetto witness per questo account \u2014 usi invece Aderisca come witness.",
        "Nessun oggetto validatore di blocchi per questo account \u2014 usi invece Aderisca come validatore di blocchi.",
    ),
    "vote.tab_witnesses": (
        "Witness (",
        "Validatori di blocchi (",
    ),
    "vote.update_witness": (
        "Aggiorni witness",
        "Aggiorni validatore di blocchi",
    ),
    "vote.witness": (
        "Witness",
        "Validatore di blocchi",
    ),
    "vote.witness_updated": (
        "Witness aggiornato",
        "Validatore di blocchi aggiornato",
    ),
}

SNIPPETS = {
    "help.topic_assets-mpa_body": [
        (
            "i witness pubblicano i feed di prezzo reali",
            "i validatori di blocchi pubblicano i feed di prezzo reali",
            1,
        ),
    ],
    "help.topic_assets-private_body": [
        (
            "non i witness \u2014 sceglie chi pu\xf2 pubblicarne",
            "non i validatori di blocchi \u2014 sceglie chi pu\xf2 pubblicarne",
            1,
        ),
        (
            "senza attendere i feed dei witness.",
            "senza attendere i feed dei validatori di blocchi.",
            1,
        ),
        (
            "non quello dei witness:",
            "non quello dei validatori di blocchi:",
            1,
        ),
    ],
    "help.topic_blockchain_body": [
        (
            "detti witness, e i pi\xf9 votati",
            "detti validatori di blocchi, e i pi\xf9 votati",
            1,
        ),
        (
            "contro il lavoro dei witness,",
            "contro il lavoro dei validatori di blocchi,",
            1,
        ),
        (
            "Veda gli articoli Voto e Witness.",
            "Veda gli articoli Voto e Validatori di blocchi.",
            1,
        ),
    ],
    "help.topic_committee_body": [
        (
            "Come i witness, i membri",
            "Come i validatori di blocchi, i membri",
            1,
        ),
    ],
    "help.topic_dex-shorting_body": [
        (
            "la garanzia minima dei witness.",
            "la garanzia minima dei validatori di blocchi.",
            1,
        ),
    ],
    "help.topic_glossary_body": [
        (
            "proposte, witness \u2014 quasi tutto",
            "proposte, validatori di blocchi \u2014 quasi tutto",
            1,
        ),
        (
            "I witness producono blocchi;",
            "I validatori di blocchi producono blocchi;",
            1,
        ),
    ],
    "help.topic_settings_body": [
        (
            "partecipazione dei witness e ritardo",
            "partecipazione dei validatori di blocchi e ritardo",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Witness](#/explorer/witnesses)",
            "- [Validatori di blocchi](#/explorer/witnesses)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "alimenta i voti di witness, comitato",
            "alimenta i voti di validatori di blocchi, comitato",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "non pu\xf2 votare direttamente per witness, membri",
            "non pu\xf2 votare direttamente per validatori di blocchi, membri",
            1,
        ),
        (
            "# Witness\nI witness costruiscono e firmano i blocchi",
            "# Validatori di blocchi\nI validatori di blocchi costruiscono e firmano i blocchi",
            1,
        ),
        (
            "nell'articolo Witness.",
            "nell'articolo Validatori di blocchi.",
            1,
        ),
    ],
    "help.topic_witnesses_body": [
        (
            "# Cosa fanno i witness\nI witness sono i produttori",
            "# Cosa fanno i validatori di blocchi\nI validatori di blocchi sono i produttori",
            1,
        ),
        (
            "per quanti witness vuole e ciascuno riceve",
            "per quanti validatori di blocchi vuole e ciascuno riceve",
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
    raw = open(IT, encoding="utf-8").read()
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
            problems.append("ABORT %s: current value has no witness-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script's old string has no witness word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no witness-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no witness word (script bug): %r" % (key, old_snip))
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

    # Post-check: no prose witness remains in the 38 targets. The sitemap
    # href "#/explorer/witnesses" is the one allowed survivor (router path).
    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        tmp = HREF_RE.sub("", v)
        if WITNESS_RE.search(tmp):
            print("FAIL: %s still carries a witness word: %r" % (key, v[:120]))
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
        open(IT, "w", encoding="utf-8").write(out)
        print("OK it: %d full + %d snippet keys renamed to validatore di blocchi" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK it: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
