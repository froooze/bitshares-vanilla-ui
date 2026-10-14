#!/usr/bin/env python3
"""Rename treasury "worker" -> "proposition de grant" in fr.json.

Scope: ONLY values carrying the treasury-proposal sense (36 keys). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from the dict's OWN attested words): sing "proposition
de grant", plur "propositions de grant" — "proposition"
(proposal.create_proposal "Créer une proposition") + loanword "grant" (no
French grant noun is attested anywhere in fr.json; thing-first order mirrors
the ticket wave's "stake de vote"). Pay stays the attested "paie", budget the
attested "budget", refund "remboursement", recipients "bénéficiaires".

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_fr.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

WORKER_RE = re.compile(r"worker|travailleur", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Cr\u00e9ation de worker",
        "Cr\u00e9ation de proposition de grant",
    ),
    "account.sum_worker_create": (
        "Worker \u201c%(name)s\u201d cr\u00e9\u00e9",
        "Proposition de grant \u201c%(name)s\u201d cr\u00e9\u00e9e",
    ),
    "createworker.confirm_worker_op_34": (
        "Confirmer le worker (op %(op)s)",
        "Confirmer la proposition de grant (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "Impossible de pr\u00e9visualiser le worker.",
        "Impossible de pr\u00e9visualiser la proposition de grant.",
    ),
    "createworker.create_worker": (
        "Cr\u00e9er un worker",
        "Cr\u00e9er une proposition de grant",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "R\u00e9digez un worker (op %(op)s). L'aper\u00e7u est en direct ; la v\u00e9rification cite les frais en direct, puis Signer et envoyer diffuse directement l'op %(op)s \u2014 les workers sont cr\u00e9\u00e9s par op directe, pas par proposition.",
        "R\u00e9digez une proposition de grant (op %(op)s). L'aper\u00e7u est en direct ; la v\u00e9rification cite les frais en direct, puis Signer et envoyer diffuse directement l'op %(op)s \u2014 les propositions de grant sont cr\u00e9\u00e9es par op directe, pas par proposition.",
    ),
    "createworker.enter_a_worker_name": (
        "Saisissez un nom de worker.",
        "Saisissez un nom de proposition de grant.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "Le propri\u00e9taire paie les frais et re\u00e7oit la paie du worker \u2014 utilisez un compte membre \u00e0 vie que vous contr\u00f4lez.",
        "Le propri\u00e9taire paie les frais et re\u00e7oit la paie de la proposition de grant \u2014 utilisez un compte membre \u00e0 vie que vous contr\u00f4lez.",
    ),
    "createworker.preview_worker": (
        "Pr\u00e9visualiser le worker",
        "Pr\u00e9visualiser la proposition de grant",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Publier un worker n\u00e9cessite un compte membre \u00e0 vie \u2014 les comptes de base ne peuvent pas payer ces frais. Le propri\u00e9taire ci-dessous doit d\u00e9j\u00e0 \u00eatre surclass\u00e9.",
        "Publier une proposition de grant n\u00e9cessite un compte membre \u00e0 vie \u2014 les comptes de base ne peuvent pas payer ces frais. Le propri\u00e9taire ci-dessous doit d\u00e9j\u00e0 \u00eatre surclass\u00e9.",
    ),
    "createworker.reading_existing_workers": (
        "Lecture des workers existants\u2026",
        "Lecture des propositions de grant existantes\u2026",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Backend des workers manquant : js/account.js ou js/format.js n'ont pas pu \u00eatre charg\u00e9s.",
        "Backend des propositions de grant manquant : js/account.js ou js/format.js n'ont pas pu \u00eatre charg\u00e9s.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Backend des workers manquant : js/asset-ops.js n'a pas pu \u00eatre charg\u00e9.",
        "Backend des propositions de grant manquant : js/asset-ops.js n'a pas pu \u00eatre charg\u00e9.",
    ),
    "createworker.worker_name": (
        "Nom du worker ",
        "Nom de la proposition de grant ",
    ),
    "createworker.worker_preview_op_34": (
        "Aper\u00e7u du worker (op %(op)s)",
        "Aper\u00e7u de la proposition de grant (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Workers",
        "Propositions de grant",
    ),
    "help.topic_voting_text": (
        "Votez pour les t\u00e9moins, le comit\u00e9, les workers \u2014 ou d\u00e9l\u00e9guez \u00e0 un proxy.",
        "Votez pour les t\u00e9moins, le comit\u00e9, les propositions de grant \u2014 ou d\u00e9l\u00e9guez \u00e0 un proxy.",
    ),
    "menu.d_voting": (
        "T\u00e9moins, comit\u00e9, workers et proxies.",
        "T\u00e9moins, comit\u00e9, propositions de grant et proxies.",
    ),
    "menu.p_worker": (
        "Cr\u00e9er un worker",
        "Cr\u00e9er une proposition de grant",
    ),
    "news.voting_witnesses_committee_workers": (
        "Vote \u2014 t\u00e9moins, comit\u00e9, workers",
        "Vote \u2014 t\u00e9moins, comit\u00e9, propositions de grant",
    ),
    "seo.desc_voting": (
        "Votez pour les t\u00e9moins, membres du comit\u00e9 et workers BitShares. Chaque bulletin est sign\u00e9 localement sur votre appareil.",
        "Votez pour les t\u00e9moins, membres du comit\u00e9 et propositions de grant BitShares. Chaque bulletin est sign\u00e9 localement sur votre appareil.",
    ),
    "vote.ballot_intro": (
        "Votre stake \u00e9lit les t\u00e9moins et le comit\u00e9 et finance les workers \u2014 tous les d\u00e9comptes et parts ci-dessous sont des lectures en direct de la cha\u00eene.",
        "Votre stake \u00e9lit les t\u00e9moins et le comit\u00e9 et finance les propositions de grant \u2014 tous les d\u00e9comptes et parts ci-dessous sont des lectures en direct de la cha\u00eene.",
    ),
    "vote.empty_hint": (
        " Les entr\u00e9es apparaissent quand la cha\u00eene les porte \u2014 les workers sont propos\u00e9s depuis #/create-worker.",
        " Les entr\u00e9es apparaissent quand la cha\u00eene les porte \u2014 les propositions de grant sont propos\u00e9es depuis #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Financement du worker indisponible (",
        "Financement des propositions de grant indisponible (",
    ),
    "vote.hide_legacy_label": (
        " Masquer les propositions historiques (toujours actif \u2014 les workers expir\u00e9s sont exclus d\u00e8s la r\u00e9cup\u00e9ration)",
        " Masquer les propositions historiques (toujours actif \u2014 les propositions de grant expir\u00e9es sont exclues d\u00e8s la r\u00e9cup\u00e9ration)",
    ),
    "vote.hide_legacy_title": (
        "Les listes de workers viennent de get_all_workers(false) ; les lignes expir\u00e9es n'arrivent jamais.",
        "Les listes de propositions de grant viennent de get_all_workers(false) ; les lignes expir\u00e9es n'arrivent jamais.",
    ),
    "vote.no_workers": (
        "Aucun worker trouv\u00e9. Les testnets n'en ont souvent aucun \u2014 c'est valide, pas une erreur.",
        "Aucune proposition de grant trouv\u00e9e. Les testnets n'en ont souvent aucune \u2014 c'est valide, pas une erreur.",
    ),
    "vote.tab_workers": (
        "Workers (",
        "Propositions de grant (",
    ),
    "vote.worker_budget": (
        "Budget des workers : \u2014",
        "Budget des propositions de grant : \u2014",
    ),
    "vote.worker_budget_loading": (
        "Budget des workers : chargement\u2026",
        "Budget des propositions de grant : chargement\u2026",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "les workers livrent des projets pay\u00e9s",
            "les b\u00e9n\u00e9ficiaires de grant livrent des projets pay\u00e9s",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Cr\u00e9er un worker](#/create-worker)",
            "- [Cr\u00e9er une proposition de grant](#/create-worker)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "les votes t\u00e9moins, comit\u00e9 et workers via le bulletin ordinaire",
            "les votes t\u00e9moins, comit\u00e9 et propositions de grant via le bulletin ordinaire",
            1,
        ),
    ],
    "help.topic_vesting_body": [
        (
            "paies workers, r\u00e9compenses de parrainage",
            "paies des propositions de grant, r\u00e9compenses de parrainage",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "et quels projets workers sont pay\u00e9s.",
            "et quels projets de propositions de grant sont pay\u00e9s.",
            1,
        ),
        (
            "ou les workers. Vous pouvez lib\u00e9rer le proxy",
            "ou les propositions de grant. Vous pouvez lib\u00e9rer le proxy",
            1,
        ),
        (
            "# Workers et budget\nLes workers sont des propositions pay\u00e9es qui passent de propos\u00e9es \u00e0 actives une fois qu\u2019elles d\u00e9passent le worker de remboursement en votes, pay\u00e9es depuis un budget quotidien fixe premier arriv\u00e9 premier servi par rang. Le d\u00e9tail complet vit dans l\u2019article Workers.",
            "# Propositions de grant et budget\nLes propositions de grant sont des propositions pay\u00e9es qui passent de propos\u00e9es \u00e0 actives une fois qu\u2019elles d\u00e9passent la proposition de grant de remboursement en votes, pay\u00e9es depuis un budget quotidien fixe premier arriv\u00e9 premier servi par rang. Le d\u00e9tail complet vit dans l\u2019article Propositions de grant.",
            1,
        ),
    ],
    "help.topic_workers_body": [
        (
            "Les workers sont des propositions pour faire quelque chose d\u2019utile",
            "Les propositions de grant sont des propositions pour faire quelque chose d\u2019utile",
            1,
        ),
        (
            "Les workers propos\u00e9s collectent des votes. Une fois qu\u2019une proposition d\u00e9passe le worker de remboursement en votes elle devient active",
            "Les propositions de grant propos\u00e9es collectent des votes. Une fois qu\u2019une proposition d\u00e9passe la proposition de grant de remboursement en votes elle devient active",
            1,
        ),
        (
            "Tous les workers partagent un seul budget quotidien fixe",
            "Toutes les propositions de grant partagent un seul budget quotidien fixe",
            1,
        ),
        (
            "si des workers mieux class\u00e9s ont d\u00e9j\u00e0 consomm\u00e9 les fonds du jour",
            "si des propositions de grant mieux class\u00e9es ont d\u00e9j\u00e0 consomm\u00e9 les fonds du jour",
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
        print("FAIL: fr.json does not round-trip indent=2/ensure_ascii=False + \\n")
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
        print("OK fr: %d full + %d snippet keys renamed to proposition(s) de grant" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK fr: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
