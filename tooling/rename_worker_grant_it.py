#!/usr/bin/env python3
"""Rename treasury "worker" -> "proposta di grant" in it.json.

Scope: ONLY values carrying the treasury-proposal sense (36 keys). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from the dict's OWN attested words): sing "proposta di
grant", plur "proposte di grant" — "proposta" (proposal.create_proposal "Crei
proposta") + loanword "grant" (no Italian grant noun is attested anywhere in
it.json; di-order mirrors the ticket wave's "stake di voto"). Pay stays the
attested "paga", budget the attested "budget", refund "rimborso", recipients
"beneficiari".

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_it.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

WORKER_RE = re.compile(r"worker|lavoratore|lavoratori", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Creazione worker",
        "Creazione proposta di grant",
    ),
    "account.sum_worker_create": (
        "Worker \"%(name)s\" creato",
        "Proposta di grant \"%(name)s\" creata",
    ),
    "createworker.confirm_worker_op_34": (
        "Confermi il worker (op %(op)s)",
        "Confermi la proposta di grant (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "Impossibile mostrare l\u2019anteprima del worker.",
        "Impossibile mostrare l\u2019anteprima della proposta di grant.",
    ),
    "createworker.create_worker": (
        "Crei worker",
        "Crei proposta di grant",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Scriva un worker (op %(op)s). L\u2019anteprima \u00e8 live; la verifica cita la commissione live, poi Firmi e invii trasmette direttamente l\u2019op %(op)s \u2014 i worker sono creati con op diretta, non con una proposta.",
        "Scriva una proposta di grant (op %(op)s). L\u2019anteprima \u00e8 live; la verifica cita la commissione live, poi Firmi e invii trasmette direttamente l\u2019op %(op)s \u2014 le proposte di grant sono create con op diretta, non con una proposta.",
    ),
    "createworker.enter_a_worker_name": (
        "Inserisca un nome worker.",
        "Inserisca un nome per la proposta di grant.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "L\u2019owner paga la commissione e riceve la paga worker \u2014 usi un account lifetime-member che controlla.",
        "L\u2019owner paga la commissione e riceve la paga della proposta di grant \u2014 usi un account lifetime-member che controlla.",
    ),
    "createworker.preview_worker": (
        "Anteprima worker",
        "Anteprima proposta di grant",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Pubblicare un worker richiede un account lifetime-member \u2014 gli account basic non possono pagare questa commissione. L\u2019owner qui sotto deve essere gi\u00e0 aggiornato.",
        "Pubblicare una proposta di grant richiede un account lifetime-member \u2014 gli account basic non possono pagare questa commissione. L\u2019owner qui sotto deve essere gi\u00e0 aggiornato.",
    ),
    "createworker.reading_existing_workers": (
        "Lettura worker esistenti\u2026",
        "Lettura proposte di grant esistenti\u2026",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Backend worker mancante: js/account.js o js/format.js non caricati.",
        "Backend proposta di grant mancante: js/account.js o js/format.js non caricati.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Backend worker mancante: js/asset-ops.js non caricato.",
        "Backend proposta di grant mancante: js/asset-ops.js non caricato.",
    ),
    "createworker.worker_name": (
        "Nome worker ",
        "Nome proposta di grant ",
    ),
    "createworker.worker_preview_op_34": (
        "Anteprima del worker (op %(op)s)",
        "Anteprima della proposta di grant (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Worker",
        "Proposte di grant",
    ),
    "help.topic_voting_text": (
        "Voti witness, comitato, worker \u2014 oppure deleghi a un proxy.",
        "Voti witness, comitato, proposte di grant \u2014 oppure deleghi a un proxy.",
    ),
    "menu.d_voting": (
        "Witness, comitato, worker e proxy.",
        "Witness, comitato, proposte di grant e proxy.",
    ),
    "menu.p_worker": (
        "Crei Worker",
        "Crei proposta di grant",
    ),
    "news.voting_witnesses_committee_workers": (
        "Voto \u2014 witness, comitato, worker",
        "Voto \u2014 witness, comitato, proposte di grant",
    ),
    "seo.desc_voting": (
        "Voti i witness, i membri del comitato e i worker di BitShares. Ogni scheda \u00e8 firmata in locale sul Suo dispositivo.",
        "Voti i witness, i membri del comitato e le proposte di grant di BitShares. Ogni scheda \u00e8 firmata in locale sul Suo dispositivo.",
    ),
    "vote.ballot_intro": (
        "Il Suo stake elegge witness e comitato e finanzia i worker \u2014 tutti i conteggi e le quote qui sotto sono letture live della chain.",
        "Il Suo stake elegge witness e comitato e finanzia le proposte di grant \u2014 tutti i conteggi e le quote qui sotto sono letture live della chain.",
    ),
    "vote.empty_hint": (
        " Le voci compaiono quando la chain le riporta \u2014 i worker sono proposti da #/create-worker.",
        " Le voci compaiono quando la chain le riporta \u2014 le proposte di grant sono proposte da #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Finanziamento worker non disponibile (",
        "Finanziamento delle proposte di grant non disponibile (",
    ),
    "vote.hide_legacy_label": (
        " Nascondi proposte legacy (sempre on \u2014 i worker scaduti sono esclusi al fetch)",
        " Nascondi proposte legacy (sempre on \u2014 le proposte di grant scadute sono escluse al fetch)",
    ),
    "vote.hide_legacy_title": (
        "Le liste worker provengono da get_all_workers(false); le righe scadute non arrivano mai.",
        "Le liste di proposte di grant provengono da get_all_workers(false); le righe scadute non arrivano mai. Ogni proposta di grant scaduta \u00e8 esclusa.",
    ),
    "vote.no_workers": (
        "Nessun worker trovato. Sulle testnet spesso non ce ne sono \u2014 \u00e8 valido, non un errore.",
        "Nessuna proposta di grant trovata. Sulle testnet spesso non ce ne sono \u2014 \u00e8 valido, non un errore.",
    ),
    "vote.tab_workers": (
        "Worker (",
        "Proposte di grant (",
    ),
    "vote.worker_budget": (
        "Budget worker: \u2014",
        "Budget delle proposte di grant: \u2014",
    ),
    "vote.worker_budget_loading": (
        "Budget worker: caricamento\u2026",
        "Budget delle proposte di grant: caricamento\u2026",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "i worker consegnano progetti retribuiti",
            "i beneficiari di grant consegnano progetti retribuiti",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Crea un worker](#/create-worker)",
            "- [Crea una proposta di grant](#/create-worker)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "i voti di witness, comitato e worker tramite la normale scheda",
            "i voti di witness, comitato e proposte di grant tramite la normale scheda",
            1,
        ),
    ],
    "help.topic_vesting_body": [
        (
            "paghe worker, ricompense referral",
            "paghe delle proposte di grant, ricompense referral",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "e quali progetti worker vengono pagati.",
            "e quali progetti di proposte di grant vengono pagati.",
            1,
        ),
        (
            "o worker. Pu\u00f2 revocare il proxy",
            "o proposte di grant. Pu\u00f2 revocare il proxy",
            1,
        ),
        (
            "# Worker e budget\nI worker sono proposte retribuite che da proposte diventano attive quando superano il worker di rimborso, pagate da un budget giornaliero fisso in ordine di rango. Il dettaglio completo \u00e8 nell'articolo Worker.",
            "# Proposte di grant e budget\nLe proposte di grant sono proposte retribuite che da proposte diventano attive quando superano la proposta di grant di rimborso, pagate da un budget giornaliero fisso in ordine di rango. Il dettaglio completo \u00e8 nell'articolo Proposte di grant.",
            1,
        ),
    ],
    "help.topic_workers_body": [
        (
            "I worker sono proposte di fare qualcosa di utile",
            "Le proposte di grant sono proposte di fare qualcosa di utile",
            1,
        ),
        (
            "I worker proposti raccolgono voti. Quando una proposta supera il worker di rimborso diventa attiva",
            "Le proposte di grant proposte raccolgono voti. Quando una proposta supera la proposta di grant di rimborso diventa attiva",
            1,
        ),
        (
            "Tutti i worker condividono un unico budget giornaliero fisso",
            "Tutte le proposte di grant condividono un unico budget giornaliero fisso",
            1,
        ),
        (
            "se i worker di rango superiore hanno gi\u00e0 consumato i fondi del giorno",
            "se le proposte di grant di rango superiore hanno gi\u00e0 consumato i fondi del giorno",
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
        print("FAIL: it.json does not round-trip indent=2/ensure_ascii=False + \\n")
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
        print("OK it: %d full + %d snippet keys renamed to proposta/proposte di grant" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK it: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
