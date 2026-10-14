#!/usr/bin/env python3
"""Rename blind -> private wording in ru.json (REPLACE, not insert).

Owns: the ru Слепой/Ослеплённые -> Приватный/Приватные value replacements
  only (11 keys).
Consumes: vanilla/locales/ru.json (ordered dict).
Side effects: overwrites ru.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-cjk-ru-hi (ru batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise: the old fragment must occur exactly once, the current
must carry a blind-family word, the derived new value must equal the
hardcoded expectation, and placeholders / op numbers / vendored tokens
are preserved verbatim. Formal вы register untouched. Case is chosen
per position: nominative for labels (Приватный перевод, Приватные
переводы/балансы), oblique inside the elliptical из/в phrases
(из приватной, в приватную) -- the adjective keeps the gender/case the
old form already had, agreeing with the same (elided) noun.
Adverbial вслепую / слепого голосования ("blindly / without checking")
is NOT touched.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

NEW = "приватн"
BLIND_RE = re.compile(r"слеп|ослепл", re.IGNORECASE)
OP_RE = re.compile(r"op(?:s)?\s*\d[\d/]*", re.IGNORECASE)

# (section, key, old fragment, expected new value).
TARGETS = [
    ("account", "op_blind_from",
     "из слепой", "Перевод из приватной"),
    ("account", "op_blind_to",
     "в слепую", "Перевод в приватную"),
    ("account", "op_blind_transfer",
     "Слепой перевод", "Приватный перевод"),
    ("account", "sum_blind",
     "Слепой перевод", "Приватный перевод (вход %(in)s, выход %(out)s)"),
    ("proposal", "err_blind_disabled",
     "Слепые переводы",
     "Приватные переводы отключены: нужна встроенная криптография commitment/range-proof (только просмотр)."),
    ("vesting", "blind_op39",
     "в слепую", "Перевод в приватную (op 39)"),
    ("vesting", "blind_op40",
     "Слепой перевод", "Приватный перевод (op 40)"),
    ("vesting", "blind_op41",
     "из слепой", "Перевод из приватной (op 41)"),
    ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
     "Слепые переводы",
     "Приватные переводы (ops 39/40/41) отключены: им нужна вендоренная криптография Pedersen-commitment и range-proof, которой нет в статической странице. Поиск коммитмента ниже доказывает только путь чтения."),
    ("vesting", "blinded_balances_read_only",
     "Ослеплённые балансы", "Приватные балансы (только чтение)"),
    ("vesting", "disabled_blind_transfers_need_vendored_commit",
     "слепые переводы",
     "Отключено: приватные переводы нуждаются в вендоренной криптографии коммитментов/range-proof."),
]

# Adverbial keys allowed to keep слеп after the run.
ADVERBIAL_KEYS = {
    ("createworker", "send_failed_check_state_before_retrying_do_no"),
    ("help", "topic_witnesses_body"),
    ("vote", "sent_note"),
    ("common", "failed_check_state"),
}


def abort(msg):
    print(f"ABORT ru: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Whole-file footprint: слеп/ослепл must live in exactly the 11
    # targets plus the 4 adverbial keys.
    found = {(sec, k) for sec in d for k, v in d[sec].items()
             if isinstance(v, str) and BLIND_RE.search(v)}
    want = {(s, k) for s, k, _, _ in TARGETS} | ADVERBIAL_KEYS
    if found != want:
        abort(f"unexpected слеп footprint: extra={found - want} "
              f"missing={want - found}")

    for sec, key, old, expected in TARGETS:
        cur = get(sec, key)
        if not isinstance(cur, str) or not BLIND_RE.search(cur):
            abort(f"{sec}.{key} current value lacks blind-family word: {cur!r}")
        if cur.count(old) != 1:
            abort(f"{sec}.{key} old fragment {old!r} occurs "
                  f"{cur.count(old)}x, expected 1x: {cur!r}")
        # Derive by swapping only the old fragment for its new-form twin.
        new_frag = None
        pairs = [("из слепой", "из приватной"), ("в слепую", "в приватную"),
                 ("Слепой перевод", "Приватный перевод"),
                 ("Слепые переводы", "Приватные переводы"),
                 ("Ослеплённые балансы", "Приватные балансы"),
                 ("слепые переводы", "приватные переводы")]
        for o, n in pairs:
            if o == old:
                new_frag = n
        if new_frag is None:
            abort(f"{sec}.{key} old fragment has no declension pair: {old!r}")
        new = cur.replace(old, new_frag)
        if new != expected:
            abort(f"{sec}.{key} derived value differs from expectation:\n"
                  f"  derived:  {new!r}\n  expected: {expected!r}")
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new:
                abort(f"{sec}.{key} would drop placeholder {ph}")
        for tok in OP_RE.findall(cur):
            if tok not in new:
                abort(f"{sec}.{key} would drop op token {tok!r}")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    # Adverbial guard: вслепую / слепого голосования survive untouched.
    for sec, key in ADVERBIAL_KEYS:
        v = get(sec, key)
        if not BLIND_RE.search(v):
            abort(f"{sec}.{key} lost adverbial слеп form: {v!r}")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("ru: blind -> private replacements applied.")


if __name__ == "__main__":
    main()
