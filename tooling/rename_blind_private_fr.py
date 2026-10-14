#!/usr/bin/env python3
"""Rename blind -> privé wording in fr.json (REPLACE, not insert).

Owns: the fr aveugle(s) -> privé(s) value replacements only (10 keys;
  proposal.err_blind_disabled already says "transferts confidentiels" and
  is LEFT untouched).
Consumes: vanilla/locales/fr.json (ordered dict).
Side effects: overwrites fr.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-latin5 (fr batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Blind-family guard: current must contain aveugle
(case-insensitive). Agreement: transfert masculin (privé), transferts /
soldes plural (privés). NBSP (U+00A0) before high punctuation preserved.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

BLIND_RE = re.compile(r"aveugle", re.IGNORECASE)


def abort(msg):
    print(f"ABORT fr: {msg}", file=sys.stderr)
    sys.exit(1)


def need_blind(cur, label):
    if not isinstance(cur, str) or not BLIND_RE.search(cur):
        abort(f"{label} current value lacks blind-family word: {cur!r}")


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Already private-sense: assert and leave.
    cur_proposal = get("proposal", "err_blind_disabled")
    if "confidentiel" not in cur_proposal:
        abort(f"proposal.err_blind_disabled lost expected confidentiels wording: {cur_proposal!r}")
    if BLIND_RE.search(cur_proposal):
        abort(f"proposal.err_blind_disabled unexpectedly has aveugle: {cur_proposal!r}")

    reps = [
        ("account", "op_blind_from",
         "Transfert depuis privé"),
        ("account", "op_blind_to",
         "Transfert vers privé"),
        ("account", "op_blind_transfer",
         "Transfert privé"),
        ("account", "sum_blind",
         "Transfert privé (%(in)s entrants, %(out)s sortants)"),
        ("vesting", "blind_op39",
         "Transfert vers privé (op 39)"),
        ("vesting", "blind_op40",
         "Transfert privé (op 40)"),
        ("vesting", "blind_op41",
         "Transfert depuis privé (op 41)"),
        ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
         "Les transferts privés (ops 39/40/41) sont désactivés : ils exigent une crypto d’engagement Pedersen et de preuve d’intervalle fournie qu’aucune page statique ne fournit. La recherche d’engagement ci-dessous prouve uniquement la voie de lecture."),
        ("vesting", "blinded_balances_read_only",
         "Soldes privés (lecture seule)"),
        ("vesting", "disabled_blind_transfers_need_vendored_commit",
         "Désactivé : les transferts privés exigent une crypto d’engagement / preuve d’intervalle fournie."),
    ]
    for sec, key, new in reps:
        cur = get(sec, key)
        need_blind(cur, f"{sec}.{key}")
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new:
                abort(f"{sec}.{key} would drop placeholder {ph}")
        for tok in re.findall(r"op(?:s)?\s*\d[\d/]*", cur):
            if tok not in new:
                abort(f"{sec}.{key} would drop op token {tok!r}")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("fr: aveugle -> privé replacements applied (proposal.err_blind_disabled left).")


if __name__ == "__main__":
    main()
