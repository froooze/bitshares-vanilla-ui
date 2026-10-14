#!/usr/bin/env python3
"""Rename blind -> privat wording in de.json (REPLACE, not insert).

Owns: the de blind-family -> privat value replacements only (11 keys,
  proposal.err_blind_disabled included; fr-style confidentiels exemption
  does not apply to de).
Consumes: vanilla/locales/de.json (ordered dict).
Side effects: overwrites de.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-latin5 (de batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Blind-family guard: current must contain blind/verblend
(case-insensitive). Placeholders (%(in)s etc.), op numbers and vendored
tokens are preserved verbatim.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

BLIND_RE = re.compile(r"verblend|blind", re.IGNORECASE)


def abort(msg):
    print(f"ABORT de: {msg}", file=sys.stderr)
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
         "Privater Transfer (von)"),
        ("account", "op_blind_to",
         "Privater Transfer (an)"),
        ("account", "op_blind_transfer",
         "Privater Transfer"),
        ("account", "sum_blind",
         "Privater Transfer (%(in)s ein, %(out)s aus)"),
        ("proposal", "err_blind_disabled",
         "Private Transfers sind deaktiviert: Sie benötigen mitgelieferte Commitment/Range-Proof-Krypto (nur schreibgeschützte Suche)."),
        ("vesting", "blind_op39",
         "Transfer zu privat (Op 39)"),
        ("vesting", "blind_op40",
         "Privat-Transfer (Op 40)"),
        ("vesting", "blind_op41",
         "Transfer von privat (Op 41)"),
        ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
         "Privat-Transfers (Ops 39/40/41) sind deaktiviert: Sie benötigen vendored Pedersen-Commitment- und Range-Proof-Krypto, die keine statische Seite mitliefert. Die Commitment-Suche unten belegt nur den Lesepfad."),
        ("vesting", "blinded_balances_read_only",
         "Private Salden (schreibgeschützt)"),
        ("vesting", "disabled_blind_transfers_need_vendored_commit",
         "Deaktiviert: Privat-Transfers benötigen vendored Commitment-/Range-Proof-Krypto."),
    ]
    for sec, key, new in reps:
        cur = get(sec, key)
        need_blind(cur, f"{sec}.{key}")
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new:
                abort(f"{sec}.{key} would drop placeholder {ph}")
        for tok in re.findall(r"Op(?:s)?\s*\d[\d/]*", cur):
            if tok not in new:
                abort(f"{sec}.{key} would drop op token {tok!r}")
        if "vendored" in cur and "vendored" not in new:
            abort(f"{sec}.{key} would drop vendored token")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("de: blind -> privat replacements applied.")


if __name__ == "__main__":
    main()
