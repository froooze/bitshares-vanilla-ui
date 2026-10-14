#!/usr/bin/env python3
"""Rename treasury "Worker" -> "Grant-Vorschlag" in vanilla/locales/de.json.

Scope: ONLY values carrying the treasury-proposal sense (36 keys). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/account.js etc. in backend-missing strings stay).
  * createworker.* pay/work-date chrome with no worker word (daily_pay,
    work_begins/ends, pay_destination ...) — untouched.
  * help.topic_workers_text (no worker word) and menu.d_worker (no worker
    word) — untouched.

Compound (per brief, from the dict's OWN attested words): sing
"Grant-Vorschlag", plur "Grant-Vorschläge" — loanword "Grant" (no German grant
noun is attested anywhere in de.json) + "Vorschlag" (proposal.create_proposal
"Vorschlag erstellen", 86 strings). Money stays the attested "Vergütung" /
"Lohn" (owner grant pay -> "Grant-Vorschlag-Vergütung", vesting grant pay ->
"Grant-Vorschlag-Lohn"); budget stays "Budget" + "Finanzierung".

Safety gates (assert before write):
  G1 every target's CURRENT value contains a worker-family word, else abort.
  G2 every target's current value EQUALS the expected old string (FULL) or
     holds each snippet exactly `count` times (SNIPPETS), else abort.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged;
     get_all_workers + js/ paths + #/create-worker still present after.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 file round-trips json.dumps(indent=2, ensure_ascii=False)+"\\n" before
     and after (no reformatting).

Usage: python3 tooling/rename_worker_grant_de.py [--apply]
Dry run (asserts only) by default; --apply writes de.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

WORKER_RE = re.compile(r"worker|arbeiter", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "account.op_worker_create": (
        "Worker-Erstellung",
        "Grant-Vorschlag-Erstellung",
    ),
    "account.sum_worker_create": (
        "Hat den Worker \u201e%(name)s\u201c erstellt",
        "Hat den Grant-Vorschlag \u201e%(name)s\u201c erstellt",
    ),
    "createworker.confirm_worker_op_34": (
        "Worker best\u00e4tigen (op %(op)s)",
        "Grant-Vorschlag best\u00e4tigen (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "Der Worker konnte nicht in der Vorschau angezeigt werden.",
        "Der Grant-Vorschlag konnte nicht in der Vorschau angezeigt werden.",
    ),
    "createworker.create_worker": (
        "Worker erstellen",
        "Grant-Vorschlag erstellen",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Entwerfen Sie einen Worker (Op %(op)s). Die Vorschau ist live; die Pr\u00fcfung nennt die Live-Geb\u00fchr, dann sendet Signieren & Senden Op %(op)s direkt \u2014 Worker entstehen durch eine direkte Op, nicht durch einen Vorschlag.",
        "Entwerfen Sie einen Grant-Vorschlag (Op %(op)s). Die Vorschau ist live; die Pr\u00fcfung nennt die Live-Geb\u00fchr, dann sendet Signieren & Senden Op %(op)s direkt \u2014 Grant-Vorschl\u00e4ge entstehen durch eine direkte Op, nicht durch einen Vorschlag.",
    ),
    "createworker.enter_a_worker_name": (
        "Geben Sie einen Worker-Namen ein.",
        "Geben Sie einen Grant-Vorschlag-Namen ein.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "Der Eigent\u00fcmer zahlt die Geb\u00fchr und erh\u00e4lt die Worker-Verg\u00fctung \u2014 verwenden Sie ein Lifetime-Konto, das Sie kontrollieren.",
        "Der Eigent\u00fcmer zahlt die Geb\u00fchr und erh\u00e4lt die Grant-Vorschlag-Verg\u00fctung \u2014 verwenden Sie ein Lifetime-Konto, das Sie kontrollieren.",
    ),
    "createworker.preview_worker": (
        "Worker-Vorschau",
        "Grant-Vorschlag-Vorschau",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Das Ver\u00f6ffentlichen eines Workers erfordert ein Lifetime-Mitgliedskonto \u2014 Basis-Konten k\u00f6nnen diese Geb\u00fchr nicht zahlen. Der untenstehende Eigent\u00fcmer muss bereits hochgestuft sein.",
        "Das Ver\u00f6ffentlichen eines Grant-Vorschlags erfordert ein Lifetime-Mitgliedskonto \u2014 Basis-Konten k\u00f6nnen diese Geb\u00fchr nicht zahlen. Der untenstehende Eigent\u00fcmer muss bereits hochgestuft sein.",
    ),
    "createworker.reading_existing_workers": (
        "Bestehende Worker werden gelesen\u2026",
        "Bestehende Grant-Vorschl\u00e4ge werden gelesen\u2026",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Worker-Backend fehlt: js/account.js oder js/format.js konnte nicht geladen werden.",
        "Grant-Vorschlag-Backend fehlt: js/account.js oder js/format.js konnte nicht geladen werden.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Worker-Backend fehlt: js/asset-ops.js konnte nicht geladen werden.",
        "Grant-Vorschlag-Backend fehlt: js/asset-ops.js konnte nicht geladen werden.",
    ),
    "createworker.worker_name": (
        "Worker-Name ",
        "Grant-Vorschlag-Name ",
    ),
    "createworker.worker_preview_op_34": (
        "Worker-Vorschau (op %(op)s)",
        "Grant-Vorschlag-Vorschau (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Worker",
        "Grant-Vorschl\u00e4ge",
    ),
    "help.topic_voting_text": (
        "Stimmen Sie f\u00fcr Zeugen, Komitee, Worker \u2014 oder geben Sie die Stimme an einen Proxy.",
        "Stimmen Sie f\u00fcr Zeugen, Komitee, Grant-Vorschl\u00e4ge \u2014 oder geben Sie die Stimme an einen Proxy.",
    ),
    "menu.d_voting": (
        "Zeugen, Komitee, Worker und Proxys.",
        "Zeugen, Komitee, Grant-Vorschl\u00e4ge und Proxys.",
    ),
    "menu.p_worker": (
        "Worker erstellen",
        "Grant-Vorschlag erstellen",
    ),
    "news.voting_witnesses_committee_workers": (
        "Abstimmung \u2014 Zeugen, Komitee, Worker",
        "Abstimmung \u2014 Zeugen, Komitee, Grant-Vorschl\u00e4ge",
    ),
    "seo.desc_voting": (
        "Stimmen Sie f\u00fcr BitShares-Zeugen, Komitee-Mitglieder und Worker. Jede Stimme wird lokal auf Ihrem Ger\u00e4t signiert.",
        "Stimmen Sie f\u00fcr BitShares-Zeugen, Komitee-Mitglieder und Grant-Vorschl\u00e4ge. Jede Stimme wird lokal auf Ihrem Ger\u00e4t signiert.",
    ),
    "vote.ballot_intro": (
        "Ihr Stake w\u00e4hlt Zeugen und Komitee und finanziert Worker \u2014 alle Z\u00e4hlungen und Anteile unten sind Live-Lesungen der Chain.",
        "Ihr Stake w\u00e4hlt Zeugen und Komitee und finanziert Grant-Vorschl\u00e4ge \u2014 alle Z\u00e4hlungen und Anteile unten sind Live-Lesungen der Chain.",
    ),
    "vote.empty_hint": (
        " Eintr\u00e4ge erscheinen, wenn die Chain sie tr\u00e4gt \u2014 Worker werden \u00fcber #/create-worker vorgeschlagen.",
        " Eintr\u00e4ge erscheinen, wenn die Chain sie tr\u00e4gt \u2014 neue Grant-Vorschlag-Eintr\u00e4ge kommen aus #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Worker-Finanzierung nicht verf\u00fcgbar (",
        "Grant-Vorschlag-Finanzierung nicht verf\u00fcgbar (",
    ),
    "vote.hide_legacy_label": (
        " Legacy-Vorschl\u00e4ge ausblenden (immer an \u2014 abgelaufene Worker werden beim Abruf ausgeschlossen)",
        " Legacy-Vorschl\u00e4ge ausblenden (immer an \u2014 abgelaufene Grant-Vorschl\u00e4ge werden beim Abruf ausgeschlossen)",
    ),
    "vote.hide_legacy_title": (
        "Worker-Listen kommen von get_all_workers(false); abgelaufene Zeilen kommen nie an.",
        "Grant-Vorschlag-Listen kommen von get_all_workers(false); abgelaufene Zeilen kommen nie an.",
    ),
    "vote.no_workers": (
        "Keine Worker gefunden. Testnets haben oft keine \u2014 dies ist g\u00fcltig, kein Fehler.",
        "Keine Grant-Vorschl\u00e4ge gefunden. Testnets haben oft keine \u2014 dies ist g\u00fcltig, kein Fehler.",
    ),
    "vote.tab_workers": (
        "Worker (",
        "Grant-Vorschl\u00e4ge (",
    ),
    "vote.worker_budget": (
        "Worker-Budget: \u2014",
        "Grant-Vorschlag-Budget: \u2014",
    ),
    "vote.worker_budget_loading": (
        "Worker-Budget: wird geladen\u2026",
        "Grant-Vorschlag-Budget: wird geladen\u2026",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "Worker liefern bezahlte Projekte",
            "Grant-Empf\u00e4nger liefern bezahlte Projekte",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Worker erstellen](#/create-worker)",
            "- [Grant-Vorschlag erstellen](#/create-worker)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Zeugen-, Komitee- und Worker-Stimmen \u00fcber die normale Slate",
            "Zeugen-, Komitee- und Grant-Vorschlag-Stimmen \u00fcber die normale Slate",
            1,
        ),
    ],
    "help.topic_vesting_body": [
        (
            "Worker-Lohn, Empfehlungspr\u00e4mien",
            "Grant-Vorschlag-Lohn, Empfehlungspr\u00e4mien",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "welche Worker-Projekte bezahlt werden.",
            "welche Grant-Vorschlag-Projekte bezahlt werden.",
            1,
        ),
        (
            "f\u00fcr Zeugen, Komitee-Mitglieder oder Worker stimmen.",
            "f\u00fcr Zeugen, Komitee-Mitglieder oder Grant-Vorschl\u00e4ge stimmen.",
            1,
        ),
        (
            "# Worker und Budget\nWorker sind bezahlte Vorschl\u00e4ge, die von vorgeschlagen zu aktiv klettern, sobald sie den Refund-Worker \u00fcberstimmen, bezahlt aus festem Tagesbudget nach Rang (Windhundprinzip). Details stehen im Worker-Artikel.",
            "# Grant-Vorschl\u00e4ge und Budget\nGrant-Vorschl\u00e4ge sind bezahlte Vorschl\u00e4ge, die von vorgeschlagen zu aktiv klettern, sobald sie den Refund-Grant-Vorschlag \u00fcberstimmen, bezahlt aus festem Tagesbudget nach Rang (Windhundprinzip). Details stehen im Grant-Vorschlag-Artikel.",
            1,
        ),
    ],
    "help.topic_workers_body": [
        (
            "Worker sind Vorschl\u00e4ge, N\u00fctzliches zu tun",
            "Grant-Vorschl\u00e4ge sind Vorschl\u00e4ge, N\u00fctzliches zu tun",
            1,
        ),
        (
            "Vorgeschlagene Worker sammeln Stimmen. Sobald ein Vorschlag den Refund-Worker \u00fcberstimmt, wird er aktiv und bezahlt;",
            "Vorgeschlagene Grant-Vorschl\u00e4ge sammeln Stimmen. Sobald ein Vorschlag den Refund-Grant-Vorschlag \u00fcberstimmt, wird er aktiv und bezahlt;",
            1,
        ),
        (
            "Alle Worker teilen ein festes Tagesbudget",
            "Alle Grant-Vorschl\u00e4ge teilen ein festes Tagesbudget",
            1,
        ),
        (
            "wenn h\u00f6herrangige Worker die Tagesgelder bereits verbrauchten",
            "wenn h\u00f6herrangige Grant-Vorschl\u00e4ge die Tagesgelder bereits verbrauchten",
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
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print("FAIL: de.json does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    # G1/G2: full-value keys.
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

    # G1: snippet keys.
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

    # Apply.
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

    # G3: identifiers survive.
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

    # G4: structure.
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
        open(DE, "w", encoding="utf-8").write(out)
        print("OK de: %d full + %d snippet keys renamed to Grant-Vorschlag" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK de: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
