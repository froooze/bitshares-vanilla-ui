#!/usr/bin/env python3
"""Rename "Zeuge" -> "Block-Validator" in vanilla/locales/de.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * "erzeugen/erzeugt" verb and "Werkzeug" (tool) — share the letters
    "zeug" but are a different sense (create/tool), correct as they stand.
  * "Veranstaltungstickets" (event tickets) — ticket sense, not witness.
  * placeholders — %(account)s / %(op)s / %(ticket)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).

Compound (per brief, from locale's own attested words): sing
"Block-Validator", plur "Block-Validatoren" — "Block"/"Blöcke" plus the
"validieren/validiert/Validierung" stem ("Blockproduzenten" is the help
article's *definition*, not the term). Hyphen compounds use the singular
stem ("Block-Validator-Update", "Block-Validator-Feed",
"Block-Validator-Artikel", "Block-Validator-Objekt",
"Block-Validator-Beitritt"); the closed "Zeugenbeteiligung" becomes
"Block-Validator-Beteiligung".

Safety gates (assert before write):
  G1 every target's CURRENT value contains a Zeuge-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\n" formatting.

Usage: python3 tooling/rename_witness_validator_de.py [--apply]
Dry run (asserts only) by default; --apply writes de.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

WITNESS_RE = re.compile(r"Zeuge")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_witness_join": (
        "Zeugen-Beitritt",
        "Block-Validator-Beitritt",
    ),
    "account.op_witness_update": (
        "Zeugen-Update",
        "Block-Validator-Update",
    ),
    "account.sum_witness_create": (
        "Zeuge geworden: %(account)s",
        "Block-Validator geworden: %(account)s",
    ),
    "account.sum_witness_update": (
        "Hat den Zeugen %(account)s aktualisiert",
        "Hat den Block-Validator %(account)s aktualisiert",
    ),
    "asset.witness_fed_note": (
        "Zeugen-Feed: alle aktiven Zeugen d\xfcrfen ver\xf6ffentlichen.",
        "Block-Validator-Feed: alle aktiven Block-Validatoren d\xfcrfen ver\xf6ffentlichen.",
    ),
    "explorer.stat_wit": (
        "Aktive Zeugen",
        "Aktive Block-Validatoren",
    ),
    "explorer.th_witness": (
        "Zeuge",
        "Block-Validator",
    ),
    "explorer.witness_row": (
        "Zeuge",
        "Block-Validator",
    ),
    "help.topic_assets-mpa_text": (
        "SmartCoins mit Sicherheiten und Preis-Feeds von Zeugen.",
        "SmartCoins mit Sicherheiten und Preis-Feeds von Block-Validatoren.",
    ),
    "help.topic_glossary_text": (
        "Namen in dieser Wallet: Objekte (1.x.y), Operationen, Zeugen, Komitee.",
        "Namen in dieser Wallet: Objekte (1.x.y), Operationen, Block-Validatoren, Komitee.",
    ),
    "help.topic_voting_text": (
        "Stimmen Sie f\xfcr Zeugen, Komitee, Grant-Vorschl\xe4ge \u2014 oder geben Sie die Stimme an einen Proxy.",
        "Stimmen Sie f\xfcr Block-Validatoren, Komitee, Grant-Vorschl\xe4ge \u2014 oder geben Sie die Stimme an einen Proxy.",
    ),
    "help.topic_witnesses_title": (
        "Zeugen",
        "Block-Validatoren",
    ),
    "menu.d_asset_feed": (
        "Preis-Feeds als Emittent oder Zeuge ver\xf6ffentlichen.",
        "Preis-Feeds als Emittent oder Block-Validator ver\xf6ffentlichen.",
    ),
    "menu.d_voting": (
        "Zeugen, Komitee, Grant-Vorschl\xe4ge und Proxys.",
        "Block-Validatoren, Komitee, Grant-Vorschl\xe4ge und Proxys.",
    ),
    "news.voting_witnesses_committee_workers": (
        "Abstimmung \u2014 Zeugen, Komitee, Grant-Vorschl\xe4ge",
        "Abstimmung \u2014 Block-Validatoren, Komitee, Grant-Vorschl\xe4ge",
    ),
    "seo.desc_voting": (
        "Stimmen Sie f\xfcr BitShares-Zeugen, Komitee-Mitglieder und Grant-Vorschl\xe4ge. Jede Stimme wird lokal auf Ihrem Ger\xe4t signiert.",
        "Stimmen Sie f\xfcr BitShares-Block-Validatoren, Komitee-Mitglieder und Grant-Vorschl\xe4ge. Jede Stimme wird lokal auf Ihrem Ger\xe4t signiert.",
    ),
    "seo.title_voting": (
        "Zeugen w\xe4hlen \u2014 BitShares Wallet",
        "Block-Validatoren w\xe4hlen \u2014 BitShares Wallet",
    ),
    "splash.pulse_witnesses": (
        "Zeugen",
        "Block-Validatoren",
    ),
    "vote.ballot_intro": (
        "Ihr Stake w\xe4hlt Zeugen und Komitee und finanziert Grant-Vorschl\xe4ge \u2014 alle Z\xe4hlungen und Anteile unten sind Live-Lesungen der Chain.",
        "Ihr Stake w\xe4hlt Block-Validatoren und Komitee und finanziert Grant-Vorschl\xe4ge \u2014 alle Z\xe4hlungen und Anteile unten sind Live-Lesungen der Chain.",
    ),
    "vote.confirm_witness_update_op_21": (
        "Zeugen-Update best\xe4tigen (Op %(op)s)",
        "Block-Validator-Update best\xe4tigen (Op %(op)s)",
    ),
    "vote.empty_list": (
        "Der Knoten hat keine Zeugen oder Komitee-Mitglieder zur\xfcckgegeben.",
        "Der Knoten hat keine Block-Validatoren oder Komitee-Mitglieder zur\xfcckgegeben.",
    ),
    "vote.join_as_witness": (
        "Als Zeuge beitreten",
        "Als Block-Validator beitreten",
    ),
    "vote.no_witness_object_for_this_account_use_join_a": (
        "Kein Zeugen-Objekt f\xfcr dieses Konto \u2014 nutzen Sie Als Zeuge beitreten stattdessen.",
        "Kein Block-Validator-Objekt f\xfcr dieses Konto \u2014 nutzen Sie Als Block-Validator beitreten stattdessen.",
    ),
    "vote.tab_witnesses": (
        "Zeugen (",
        "Block-Validatoren (",
    ),
    "vote.update_witness": (
        "Zeuge aktualisieren",
        "Block-Validator aktualisieren",
    ),
    "vote.witness": (
        "Zeuge",
        "Block-Validator",
    ),
    "vote.witness_updated": (
        "Zeuge aktualisiert",
        "Block-Validator aktualisiert",
    ),
}

SNIPPETS = {
    "help.topic_assets-mpa_body": [
        (
            "Zeugen ver\xf6ffentlichen die Realwelt-Preis-Feeds",
            "Block-Validatoren ver\xf6ffentlichen die Realwelt-Preis-Feeds",
            1,
        ),
    ],
    "help.topic_assets-private_body": [
        (
            "nicht die Zeugen \u2014 wer seine Preis-Feeds",
            "nicht die Block-Validatoren \u2014 wer seine Preis-Feeds",
            1,
        ),
        (
            "ohne auf Zeugen-Feeds zu warten",
            "ohne auf Block-Validator-Feeds zu warten",
            1,
        ),
        (
            "nicht den der Zeugen:",
            "nicht den der Block-Validatoren:",
            1,
        ),
    ],
    "help.topic_blockchain_body": [
        (
            "bevorzugte Produzenten, Zeugen genannt, und die meistgew\xe4hlten",
            "bevorzugte Produzenten, Block-Validatoren genannt, und die meistgew\xe4hlten",
            1,
        ),
        (
            "an der Arbeit der Zeugen messen",
            "an der Arbeit der Block-Validatoren messen",
            1,
        ),
        (
            "Siehe die Artikel Abstimmen und Zeugen.",
            "Siehe die Artikel Abstimmen und Block-Validatoren.",
            1,
        ),
    ],
    "help.topic_committee_body": [
        (
            "Wie Zeugen gewinnen Komitee-Mitglieder",
            "Wie Block-Validatoren gewinnen Komitee-Mitglieder",
            1,
        ),
    ],
    "help.topic_dex-shorting_body": [
        (
            "die Mindestbesicherung der Zeugen.",
            "die Mindestbesicherung der Block-Validatoren.",
            1,
        ),
    ],
    "help.topic_glossary_body": [
        (
            "Vorschl\xe4ge, Zeugen \u2014 fast alles",
            "Vorschl\xe4ge, Block-Validatoren \u2014 fast alles",
            1,
        ),
        (
            "Zeugen produzieren Bl\xf6cke;",
            "Block-Validatoren produzieren Bl\xf6cke;",
            1,
        ),
    ],
    "help.topic_settings_body": [
        (
            "Zeugenbeteiligung",
            "Block-Validator-Beteiligung",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Zeugen](#/explorer/witnesses)",
            "- [Block-Validatoren](#/explorer/witnesses)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "speist Zeugen-, Komitee- und Grant-Vorschlag-Stimmen",
            "speist Block-Validatoren-, Komitee- und Grant-Vorschlag-Stimmen",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "nicht direkt f\xfcr Zeugen, Komitee-Mitglieder",
            "nicht direkt f\xfcr Block-Validatoren, Komitee-Mitglieder",
            1,
        ),
        (
            "# Zeugen\nZeugen bauen und signieren Bl\xf6cke",
            "# Block-Validatoren\nBlock-Validatoren bauen und signieren Bl\xf6cke",
            1,
        ),
        (
            "Details stehen im Zeugen-Artikel.",
            "Details stehen im Block-Validator-Artikel.",
            1,
        ),
    ],
    "help.topic_witnesses_body": [
        (
            "# Was Zeugen tun\nZeugen sind die Blockproduzenten",
            "# Was Block-Validatoren tun\nBlock-Validatoren sind die Blockproduzenten",
            1,
        ),
        (
            "f\xfcr so viele Zeugen stimmen wie Sie m\xf6gen",
            "f\xfcr so viele Block-Validatoren stimmen wie Sie m\xf6gen",
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

    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no Zeuge-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script's old string has no Zeuge word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no Zeuge-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no Zeuge word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    # Exclusion guards: other senses must be intact.
    for guard_key, guard_word in [
        ("help.topic_assets-issue_body", "Erzeugen"),
        ("apilab.gate_title", "Werkzeug"),
        ("menu.blurb_labs", "Werkzeuge"),
        ("help.topic_assets-uia_body", "Veranstaltungstickets"),
    ]:
        try:
            if guard_word not in dig(d, guard_key):
                problems.append("ABORT %s: exclusion sense changed unexpectedly (%r missing)" % (guard_key, guard_word))
        except KeyError:
            problems.append("missing guard key %s" % guard_key)

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

    # Post-check: no Zeuge-family word remains in the 38 targets
    # (sitemap href has none in German; key names are not values).
    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        if WITNESS_RE.search(v):
            print("FAIL: %s still carries a Zeuge word: %r" % (key, v[:120]))
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
        open(DE, "w", encoding="utf-8").write(out)
        print("OK de: %d full + %d snippet keys renamed to Block-Validator(en)" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK de: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
