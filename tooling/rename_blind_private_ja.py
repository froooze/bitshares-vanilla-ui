#!/usr/bin/env python3
"""Rename blind -> private wording in ja.json (REPLACE, not insert).

Owns: the ja ブラインド -> プライベート value replacements only (11 keys).
Consumes: vanilla/locales/ja.json (ordered dict).
Side effects: overwrites ja.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-cjk-ru-hi (ja batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise: the old fragment must occur exactly once, the current
must carry a blind-family word, the derived new value must equal the
hardcoded expectation, and placeholders / op numbers / vendored tokens
are preserved verbatim. Polite です/ます register untouched; compounds
mirrored exactly (ブラインド送金 -> プライベート送金 etc.).
Adverbial 盲目投票 (help.topic_witnesses_body, voting without research)
is NOT touched.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "ja.json")

OLD = "ブラインド"
NEW = "プライベート"
BLIND_RE = re.compile(re.escape(OLD))
OP_RE = re.compile(r"op(?:s)?\s*\d[\d/]*", re.IGNORECASE)

TARGETS = [
    ("account", "op_blind_from",
     "プライベートからの送金"),
    ("account", "op_blind_to",
     "プライベートへの送金"),
    ("account", "op_blind_transfer",
     "プライベート送金"),
    ("account", "sum_blind",
     "プライベート送金（入金 %(in)s、出金 %(out)s）"),
    ("proposal", "err_blind_disabled",
     "プライベート送金は無効です: ベンダー提供のコミットメント／レンジプルーフ暗号が必要です（読み取り専用照会のみ）。"),
    ("vesting", "blind_op39",
     "プライベートへの送金（op 39）"),
    ("vesting", "blind_op40",
     "プライベート送金（op 40）"),
    ("vesting", "blind_op41",
     "プライベートからの送金（op 41）"),
    ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
     "プライベート送金（ops 39/40/41）は無効です: 静的ページが同梱しないPedersenコミットメントとレンジプルーフ暗号が必要です。下のコミットメント照会は読み取りパスの実証のみです。"),
    ("vesting", "blinded_balances_read_only",
     "プライベート残高（読み取り専用）"),
    ("vesting", "disabled_blind_transfers_need_vendored_commit",
     "無効: プライベート送金には同梱済みのコミットメント/レンジプルーフ暗号が必要です。"),
]

# Keys allowed to keep blind-family characters after the run (adverbial
# 盲目 = "blindly / without checking", not the transfer feature).
ADVERBIAL_OK = {
    ("help", "topic_witnesses_body"),
}


def abort(msg):
    print(f"ABORT ja: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Whole-file footprint: ブラインド must live in exactly the 11 targets.
    found = {(sec, k) for sec in d for k, v in d[sec].items()
             if isinstance(v, str) and OLD in v}
    if found != {(s, k) for s, k, _ in TARGETS}:
        abort(f"unexpected ブラインド footprint: "
              f"extra={found - {(s, k) for s, k, _ in TARGETS}} "
              f"missing={( {(s, k) for s, k, _ in TARGETS} ) - found}")

    for sec, key, expected in TARGETS:
        cur = get(sec, key)
        if not isinstance(cur, str) or not BLIND_RE.search(cur):
            abort(f"{sec}.{key} current value lacks blind-family word: {cur!r}")
        if cur.count(OLD) != 1:
            abort(f"{sec}.{key} old fragment occurs {cur.count(OLD)}x, "
                  f"expected 1x: {cur!r}")
        new = cur.replace(OLD, NEW)
        if new != expected:
            abort(f"{sec}.{key} derived value differs from expectation:\n"
                  f"  derived:  {new!r}\n  expected: {expected!r}")
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new:
                abort(f"{sec}.{key} would drop placeholder {ph}")
        for tok in OP_RE.findall(cur):
            if tok not in new:
                abort(f"{sec}.{key} would drop op token {tok!r}")
        if "vendored" in cur and "vendored" not in new:
            abort(f"{sec}.{key} would drop vendored token")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    # Adverbial guard: 盲目投票 must survive untouched.
    adv = get("help", "topic_witnesses_body")
    if "盲目投票" not in adv:
        abort("help.topic_witnesses_body lost adverbial 盲目投票")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("ja: blind -> private replacements applied.")


if __name__ == "__main__":
    main()
