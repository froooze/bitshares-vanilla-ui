#!/usr/bin/env python3
"""Rename blind -> privado wording in es.json (REPLACE, not insert).

Owns: the es ciega/ciegas/ciegos -> privada/privadas/privados value
  replacements only (11 keys).
Consumes: vanilla/locales/es.json (ordered dict).
Side effects: overwrites es.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-latin5 (es batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Blind-family guard: current must contain cieg
(case-insensitive). Gender/number agreement: transferencia is feminine
(-privada singular, -privadas plural); saldos masculine plural (-privados).
Placeholders, op numbers and vendored/incluida tokens preserved verbatim.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

BLIND_RE = re.compile(r"cieg", re.IGNORECASE)


def abort(msg):
    print(f"ABORT es: {msg}", file=sys.stderr)
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
         "Transferencia desde privada"),
        ("account", "op_blind_to",
         "Transferencia a privada"),
        ("account", "op_blind_transfer",
         "Transferencia privada"),
        ("account", "sum_blind",
         "Transferencia privada (%(in)s dentro, %(out)s fuera)"),
        ("proposal", "err_blind_disabled",
         "Las transferencias privadas están desactivadas: necesitan criptografía de compromiso/prueba de rango incorporada (solo consulta de lectura)."),
        ("vesting", "blind_op39",
         "Transferencia a privada (op 39)"),
        ("vesting", "blind_op40",
         "Transferencia privada (op 40)"),
        ("vesting", "blind_op41",
         "Transferencia desde privada (op 41)"),
        ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
         "Las transferencias privadas (ops 39/40/41) están desactivadas: necesitan cripto Pedersen-commitment y range-proof incluida que ninguna página estática trae. La búsqueda de compromiso abajo solo demuestra la ruta de lectura."),
        ("vesting", "blinded_balances_read_only",
         "Saldos privados (solo lectura)"),
        ("vesting", "disabled_blind_transfers_need_vendored_commit",
         "Desactivado: las transferencias privadas necesitan cripto commitment/range-proof incluida."),
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
    print("es: ciega -> privada replacements applied.")


if __name__ == "__main__":
    main()
