#!/usr/bin/env python3
"""Rename "témoin" -> "validateur de blocs" in vanilla/locales/fr.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).

Compound (per brief, from locale's own attested words): sing
"validateur de blocs", plur "validateurs de blocs" — "bloc"/"blocs" plus
the "validés/validation" stem ("producteurs de blocs" is the help
article's *definition*, not the term). Title case at sentence/title start
("Validateur(s) de blocs"), lowercase elsewhere. The approved term is the
full compound everywhere — bare "validateur" alone is not enough.
Typography (U+00A0, U+2019) follows the existing string byte-for-byte.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a témoin-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\n" formatting.

Usage: python3 tooling/rename_witness_validator_fr.py [--apply]
Dry run (asserts only) by default; --apply writes fr.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

WITNESS_RE = re.compile(r"t\xe9moin", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_witness_join": (
        "Adh\xe9sion comme t\xe9moin",
        "Adh\xe9sion comme validateur de blocs",
    ),
    "account.op_witness_update": (
        "Mise \xe0 jour de t\xe9moin",
        "Mise \xe0 jour de validateur de blocs",
    ),
    "account.sum_witness_create": (
        "Devenu t\xe9moin : %(account)s",
        "Devenu validateur de blocs : %(account)s",
    ),
    "account.sum_witness_update": (
        "T\xe9moin %(account)s mis \xe0 jour",
        "Validateur de blocs %(account)s mis \xe0 jour",
    ),
    "asset.witness_fed_note": (
        "Aliment\xe9 par les t\xe9moins : tous les t\xe9moins actifs peuvent publier.",
        "Aliment\xe9 par les validateurs de blocs : tous les validateurs de blocs actifs peuvent publier.",
    ),
    "explorer.stat_wit": (
        "T\xe9moins actifs",
        "Validateurs de blocs actifs",
    ),
    "explorer.th_witness": (
        "T\xe9moin",
        "Validateur de blocs",
    ),
    "explorer.witness_row": (
        "T\xe9moin",
        "Validateur de blocs",
    ),
    "help.topic_assets-mpa_text": (
        "Smartcoins adoss\xe9s \xe0 du collat\xe9ral avec flux de prix des t\xe9moins.",
        "Smartcoins adoss\xe9s \xe0 du collat\xe9ral avec flux de prix des validateurs de blocs.",
    ),
    "help.topic_glossary_text": (
        "Noms utilis\xe9s dans ce portefeuille\xa0: objets (1.x.y), op\xe9rations, t\xe9moins, comit\xe9.",
        "Noms utilis\xe9s dans ce portefeuille\xa0: objets (1.x.y), op\xe9rations, validateurs de blocs, comit\xe9.",
    ),
    "help.topic_voting_text": (
        "Votez pour les t\xe9moins, le comit\xe9, les propositions de grant \u2014 ou d\xe9l\xe9guez \xe0 un proxy.",
        "Votez pour les validateurs de blocs, le comit\xe9, les propositions de grant \u2014 ou d\xe9l\xe9guez \xe0 un proxy.",
    ),
    "help.topic_witnesses_title": (
        "T\xe9moins",
        "Validateurs de blocs",
    ),
    "menu.d_asset_feed": (
        "Publier des flux de prix comme \xe9metteur ou t\xe9moin.",
        "Publier des flux de prix comme \xe9metteur ou validateur de blocs.",
    ),
    "menu.d_voting": (
        "T\xe9moins, comit\xe9, propositions de grant et proxies.",
        "Validateurs de blocs, comit\xe9, propositions de grant et proxies.",
    ),
    "news.voting_witnesses_committee_workers": (
        "Vote \u2014 t\xe9moins, comit\xe9, propositions de grant",
        "Vote \u2014 validateurs de blocs, comit\xe9, propositions de grant",
    ),
    "seo.desc_voting": (
        "Votez pour les t\xe9moins, membres du comit\xe9 et propositions de grant BitShares. Chaque bulletin est sign\xe9 localement sur votre appareil.",
        "Votez pour les validateurs de blocs, membres du comit\xe9 et propositions de grant BitShares. Chaque bulletin est sign\xe9 localement sur votre appareil.",
    ),
    "seo.title_voting": (
        "Voter pour des t\xe9moins \u2014 Portefeuille BitShares",
        "Voter pour des validateurs de blocs \u2014 Portefeuille BitShares",
    ),
    "splash.pulse_witnesses": (
        "T\xe9moins",
        "Validateurs de blocs",
    ),
    "vote.ballot_intro": (
        "Votre stake \xe9lit les t\xe9moins et le comit\xe9 et finance les propositions de grant \u2014 tous les d\xe9comptes et parts ci-dessous sont des lectures en direct de la cha\xeene.",
        "Votre stake \xe9lit les validateurs de blocs et le comit\xe9 et finance les propositions de grant \u2014 tous les d\xe9comptes et parts ci-dessous sont des lectures en direct de la cha\xeene.",
    ),
    "vote.confirm_witness_update_op_21": (
        "Confirmer la mise \xe0 jour du t\xe9moin (op %(op)s)",
        "Confirmer la mise \xe0 jour du validateur de blocs (op %(op)s)",
    ),
    "vote.empty_list": (
        "Le n\u0153ud n'a renvoy\xe9 ni t\xe9moins ni membres du comit\xe9.",
        "Le n\u0153ud n'a renvoy\xe9 ni validateurs de blocs ni membres du comit\xe9.",
    ),
    "vote.join_as_witness": (
        "Devenir t\xe9moin",
        "Devenir validateur de blocs",
    ),
    "vote.no_witness_object_for_this_account_use_join_a": (
        "Aucun objet t\xe9moin pour ce compte \u2014 utilisez Devenir t\xe9moin \xe0 la place.",
        "Aucun objet validateur de blocs pour ce compte \u2014 utilisez Devenir validateur de blocs \xe0 la place.",
    ),
    "vote.tab_witnesses": (
        "T\xe9moins (",
        "Validateurs de blocs (",
    ),
    "vote.update_witness": (
        "Mettre \xe0 jour le t\xe9moin",
        "Mettre \xe0 jour le validateur de blocs",
    ),
    "vote.witness": (
        "T\xe9moin",
        "Validateur de blocs",
    ),
    "vote.witness_updated": (
        "T\xe9moin mis \xe0 jour",
        "Validateur de blocs mis \xe0 jour",
    ),
}

SNIPPETS = {
    "help.topic_assets-mpa_body": [
        (
            "les t\xe9moins publient les flux de prix du monde r\xe9el",
            "les validateurs de blocs publient les flux de prix du monde r\xe9el",
            1,
        ),
    ],
    "help.topic_assets-private_body": [
        (
            "pas les t\xe9moins \u2014 choisit qui peut publier",
            "pas les validateurs de blocs \u2014 choisit qui peut publier",
            1,
        ),
        (
            "sans attendre les flux des t\xe9moins.",
            "sans attendre les flux des validateurs de blocs.",
            1,
        ),
        (
            "pas celui des t\xe9moins\xa0:",
            "pas celui des validateurs de blocs\xa0:",
            1,
        ),
    ],
    "help.topic_blockchain_body": [
        (
            "appel\xe9s t\xe9moins, et les plus vot\xe9s",
            "appel\xe9s validateurs de blocs, et les plus vot\xe9s",
            1,
        ),
        (
            "face au travail des t\xe9moins,",
            "face au travail des validateurs de blocs,",
            1,
        ),
        (
            "Voir les articles Vote et T\xe9moins.",
            "Voir les articles Vote et Validateurs de blocs.",
            1,
        ),
    ],
    "help.topic_committee_body": [
        (
            "Comme les t\xe9moins, les membres",
            "Comme les validateurs de blocs, les membres",
            1,
        ),
    ],
    "help.topic_dex-shorting_body": [
        (
            "l\u2019adossement minimum des t\xe9moins.",
            "l\u2019adossement minimum des validateurs de blocs.",
            1,
        ),
    ],
    "help.topic_glossary_body": [
        (
            "propositions, t\xe9moins \u2014 presque tout",
            "propositions, validateurs de blocs \u2014 presque tout",
            1,
        ),
        (
            "Les t\xe9moins produisent les blocs\xa0;",
            "Les validateurs de blocs produisent les blocs\xa0;",
            1,
        ),
    ],
    "help.topic_settings_body": [
        (
            "participation des t\xe9moins et retard",
            "participation des validateurs de blocs et retard",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [T\xe9moins](#/explorer/witnesses)",
            "- [Validateurs de blocs](#/explorer/witnesses)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "alimente les votes t\xe9moins, comit\xe9",
            "alimente les votes validateurs de blocs, comit\xe9",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "pas voter directement pour les t\xe9moins, les membres",
            "pas voter directement pour les validateurs de blocs, les membres",
            1,
        ),
        (
            "# T\xe9moins\nLes t\xe9moins construisent et signent les blocs",
            "# Validateurs de blocs\nLes validateurs de blocs construisent et signent les blocs",
            1,
        ),
        (
            "vit dans l\u2019article T\xe9moins.",
            "vit dans l\u2019article Validateurs de blocs.",
            1,
        ),
    ],
    "help.topic_witnesses_body": [
        (
            "# Ce que font les t\xe9moins\nLes t\xe9moins sont les producteurs",
            "# Ce que font les validateurs de blocs\nLes validateurs de blocs sont les producteurs",
            1,
        ),
        (
            "pour autant de t\xe9moins que vous voulez,",
            "pour autant de validateurs de blocs que vous voulez,",
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
    raw = open(FR, encoding="utf-8").read()
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
            problems.append("ABORT %s: current value has no t\xe9moin-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script's old string has no t\xe9moin word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no t\xe9moin-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no t\xe9moin word (script bug): %r" % (key, old_snip))
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
            print("FAIL: %s still carries a t\xe9moin word: %r" % (key, v[:120]))
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
        open(FR, "w", encoding="utf-8").write(out)
        print("OK fr: %d full + %d snippet keys renamed to validateur de blocs" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK fr: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
