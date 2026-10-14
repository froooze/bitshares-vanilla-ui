#!/usr/bin/env python3
"""Rename blind -> private wording in zh.json (REPLACE, not insert).

Owns: the zh 盲 -> 私密 value replacements for transfers only (4 account
  keys). The 7 vesting/proposal keys already say 隐身 (hidden), which
  means hidden/private and is correct -- they are ASSERTED but left
  untouched. 隐身余额 and other 隐身 strings are never replaced.
Consumes: vanilla/locales/zh.json (ordered dict).
Side effects: overwrites zh.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-cjk-ru-hi (zh batch).

Each key asserts its CURRENT value before anything else and aborts
loudly otherwise. Adverbial 盲目 / 盲投 ("blindly / without checking")
and explorer.stat_stealth (a different feature) are NOT touched.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "zh.json")

OLD = "盲"
NEW = "私密"
HIDDEN = "隐身"
OP_RE = re.compile(r"op(?:s)?\s*\d[\d/]*", re.IGNORECASE)

# (section, key, expected new value); new is derived as cur.replace(OLD, NEW).
TARGETS = [
    ("account", "op_blind_from",
     "私密转入"),
    ("account", "op_blind_to",
     "私密转出"),
    ("account", "op_blind_transfer",
     "私密转账"),
    ("account", "sum_blind",
     "私密转账（转入 %(in)s，转出 %(out)s）"),
]

# Already-private 隐身 keys: assert presence of 隐身 and absence of 盲,
# change nothing.
LEAVE_KEYS = [
    ("proposal", "err_blind_disabled"),
    ("vesting", "blind_op39"),
    ("vesting", "blind_op40"),
    ("vesting", "blind_op41"),
    ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the"),
    ("vesting", "blinded_balances_read_only"),
    ("vesting", "disabled_blind_transfers_need_vendored_commit"),
]

# Keys allowed to keep 盲 after the run (adverbials, not the feature).
ADVERBIAL_KEYS = {
    ("createworker", "send_failed_check_state_before_retrying_do_no"),
    ("help", "topic_witnesses_body"),
    ("vote", "sent_note"),
    ("common", "failed_check_state"),
}


def abort(msg):
    print(f"ABORT zh: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Whole-file footprint: 盲 must live in exactly the 4 targets plus
    # the 4 adverbial keys.
    found = {(sec, k) for sec in d for k, v in d[sec].items()
             if isinstance(v, str) and OLD in v}
    want = {(s, k) for s, k, _ in TARGETS} | ADVERBIAL_KEYS
    if found != want:
        abort(f"unexpected 盲 footprint: extra={found - want} "
              f"missing={want - found}")

    for sec, key, expected in TARGETS:
        cur = get(sec, key)
        if not isinstance(cur, str) or OLD not in cur:
            abort(f"{sec}.{key} current value lacks 盲: {cur!r}")
        if HIDDEN in cur:
            abort(f"{sec}.{key} unexpectedly mixes 隐身: {cur!r}")
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
        if OLD in new:
            abort(f"{sec}.{key} new value still has 盲: {new!r}")
        d[sec][key] = new

    for sec, key in LEAVE_KEYS:
        cur = get(sec, key)
        if HIDDEN not in cur:
            abort(f"{sec}.{key} lost expected 隐身 wording: {cur!r}")
        if OLD in cur:
            abort(f"{sec}.{key} unexpectedly contains 盲: {cur!r}")

    # Adverbial + stealth guards.
    for sec, key in ADVERBIAL_KEYS:
        v = get(sec, key)
        if OLD not in v:
            abort(f"{sec}.{key} lost adverbial 盲: {v!r}")
    if HIDDEN not in get("explorer", "stat_stealth"):
        abort("explorer.stat_stealth lost 隐身")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("zh: blind -> private replacements applied (4 replaced, 7 already 隐身).")


if __name__ == "__main__":
    main()
