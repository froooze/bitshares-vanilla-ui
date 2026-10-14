#!/usr/bin/env python3
"""Rename blind -> privato wording in it.json (REPLACE, not insert).

Owns: the it blind -> privato/privati value replacements only (11 keys).
Consumes: vanilla/locales/it.json (ordered dict).
Side effects: overwrites it.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-latin5 (it batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Blind-family guard: current must contain blind
(case-insensitive; bare loanword). Agreement: trasferimento masculin
singular (privato); trasferimenti/saldi plural (privati). "a/da blind" ->
"a/da privato". Placeholders, op numbers and vendored tokens preserved.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

BLIND_RE = re.compile(r"blind", re.IGNORECASE)


def abort(msg):
    print(f"ABORT it: {msg}", file=sys.stderr)
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

    reps = [
        ("account", "op_blind_from",
         "Trasferimento da privato"),
        ("account", "op_blind_to",
         "Trasferimento a privato"),
        ("account", "op_blind_transfer",
         "Trasferimento privato"),
        ("account", "sum_blind",
         "Trasferimento privato (%(in)s in, %(out)s out)"),
        ("proposal", "err_blind_disabled",
         "I trasferimenti privati sono disabilitati: richiedono crittografia commitment/range-proof vendored (solo consultazione)."),
        ("vesting", "blind_op39",
         "Trasferimento a privato (op 39)"),
        ("vesting", "blind_op40",
         "Trasferimento privato (op 40)"),
        ("vesting", "blind_op41",
         "Trasferimento da privato (op 41)"),
        ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
         "Trasferimenti privati (op 39/40/41) disabilitati: richiedono crittografia Pedersen-commitment e range-proof vendored che nessuna pagina statica fornisce. La ricerca commitment qui sotto dimostra solo il percorso di lettura."),
        ("vesting", "blinded_balances_read_only",
         "Saldi privati (sola lettura)"),
        ("vesting", "disabled_blind_transfers_need_vendored_commit",
         "Disabilitato: i trasferimenti privati richiedono crittografia commitment/range-proof vendored."),
    ]
    for sec, key, new in reps:
        cur = get(sec, key)
        need_blind(cur, f"{sec}.{key}")
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new:
                abort(f"{sec}.{key} would drop placeholder {ph}")
        for tok in re.findall(r"op\s*\d[\d/]*", cur):
            if tok not in new:
                abort(f"{sec}.{key} would drop op token {tok!r}")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("it: blind -> privato replacements applied.")


if __name__ == "__main__":
    main()
