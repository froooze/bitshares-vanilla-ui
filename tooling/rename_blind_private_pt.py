#!/usr/bin/env python3
"""Rename blind -> privado wording in pt.json (REPLACE, not insert).

Owns: the pt cego/cega/blind/blinded -> privada/privado value replacements
  only (11 keys).
Consumes: vanilla/locales/pt.json (ordered dict).
Side effects: overwrites pt.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-latin5 (pt batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Blind-family guard: current must contain ceg or blind
(case-insensitive). Agreement: transferência feminine (privada/privadas);
"de/para cego" and "a/para blind" become "de/para saldo privado" (masculine
saldo) so the string never reads as "a blind person". Placeholders, op
numbers and vendorizada/incluída tokens preserved verbatim.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

BLIND_RE = re.compile(r"ceg|blind", re.IGNORECASE)


def abort(msg):
    print(f"ABORT pt: {msg}", file=sys.stderr)
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
         "Transferência de saldo privado"),
        ("account", "op_blind_to",
         "Transferência para saldo privado"),
        ("account", "op_blind_transfer",
         "Transferência privada"),
        ("account", "sum_blind",
         "Transferência privada (%(in)s entrando, %(out)s saindo)"),
        ("proposal", "err_blind_disabled",
         "Transferências privadas estão desativadas: precisam de cripto de commitment/range-proof vendorizada (só consulta somente leitura)."),
        ("vesting", "blind_op39",
         "Transferência para saldo privado (op 39)"),
        ("vesting", "blind_op40",
         "Transferência privada (op 40)"),
        ("vesting", "blind_op41",
         "Transferência de saldo privado (op 41)"),
        ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
         "Transferências privadas (ops 39/40/41) estão desativadas: exigem cripto Pedersen-commitment e range-proof incluída que nenhuma página estática embarca. A consulta de commitment abaixo prova apenas o caminho de leitura."),
        ("vesting", "blinded_balances_read_only",
         "Saldos privados (somente leitura)"),
        ("vesting", "disabled_blind_transfers_need_vendored_commit",
         "Desativado: transferências privadas exigem cripto commitment/range-proof incluída."),
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
    print("pt: cego/blind -> privada/saldo privado replacements applied.")


if __name__ == "__main__":
    main()
