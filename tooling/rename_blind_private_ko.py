#!/usr/bin/env python3
"""Rename blind -> private wording in ko.json (REPLACE, not insert).

Owns: the ko 블라인드 -> 프라이빗 value replacements only (11 keys).
Consumes: vanilla/locales/ko.json (ordered dict).
Side effects: overwrites ko.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-cjk-ru-hi (ko batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise: the old fragment must occur exactly once, the current
must carry a blind-family word, the derived new value must equal the
hardcoded expectation, and placeholders / op numbers / vendored tokens
are preserved verbatim. Polite split register untouched; compounds
mirrored exactly (블라인드 이체 -> 프라이빗 이체, existing 전송 kept
where the current string uses it). Glued dots untouched.
Adverbials 무작정 / 맹목 투표 ("without checking") are NOT touched.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "ko.json")

OLD = "블라인드"
BLIND_RE = re.compile(re.escape(OLD))
OP_RE = re.compile(r"op(?:s)?\s*\d[\d/]*", re.IGNORECASE)

# (section, key, old fragment, new fragment, expected new value).
# Particle note: 프라이빗 ends in batchim ㅅ, so the 로 particle of
# 블라인드로 becomes 으로 (프라이빗으로); 에서 is unchanged.
TARGETS = [
    ("account", "op_blind_from",
     "블라인드에서", "프라이빗에서",
     "프라이빗에서 이체"),
    ("account", "op_blind_to",
     "블라인드로", "프라이빗으로",
     "프라이빗으로 이체"),
    ("account", "op_blind_transfer",
     "블라인드", "프라이빗",
     "프라이빗 이체"),
    ("account", "sum_blind",
     "블라인드", "프라이빗",
     "프라이빗 이체(입금 %(in)s, 출금 %(out)s)"),
    ("proposal", "err_blind_disabled",
     "블라인드", "프라이빗",
     "프라이빗 전송은 비활성입니다. vendored 커밋먼트/레인지프루프 암호가 필요합니다(읽기 전용 조회만)."),
    ("vesting", "blind_op39",
     "블라인드로", "프라이빗으로",
     "프라이빗으로 이체(op 39)"),
    ("vesting", "blind_op40",
     "블라인드", "프라이빗",
     "프라이빗 이체(op 40)"),
    ("vesting", "blind_op41",
     "블라인드에서", "프라이빗에서",
     "프라이빗에서 이체(op 41)"),
    ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
     "블라인드", "프라이빗",
     "프라이빗 이체(op 39/40/41)는 비활성화되어 있습니다. 정적 페이지에서 제공하지 않는 벤더링된 Pedersen-commitment 및 range-proof 암호가 필요합니다. 아래 commitment 조회는 읽기 경로만 검증합니다."),
    ("vesting", "blinded_balances_read_only",
     "블라인드", "프라이빗",
     "프라이빗 잔액(읽기 전용)"),
    ("vesting", "disabled_blind_transfers_need_vendored_commit",
     "블라인드", "프라이빗",
     "비활성화됨: 프라이빗 이체에는 벤더링된 commitment/range-proof 암호가 필요합니다."),
]

# Adverbial keys allowed to keep 무작정 / 맹목 after the run.
ADVERBIAL_KEYS = {
    ("createworker", "send_failed_check_state_before_retrying_do_no"),
    ("help", "topic_witnesses_body"),
    ("vote", "sent_note"),
    ("common", "failed_check_state"),
}


def abort(msg):
    print(f"ABORT ko: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Whole-file footprint: 블라인드 must live in exactly the 11 targets.
    found = {(sec, k) for sec in d for k, v in d[sec].items()
             if isinstance(v, str) and OLD in v}
    want = {(s, k) for s, k, _, _, _ in TARGETS}
    if found != want:
        abort(f"unexpected 블라인드 footprint: extra={found - want} "
              f"missing={want - found}")

    for sec, key, old, new_frag, expected in TARGETS:
        cur = get(sec, key)
        if not isinstance(cur, str) or not BLIND_RE.search(cur):
            abort(f"{sec}.{key} current value lacks blind-family word: {cur!r}")
        if cur.count(old) != 1:
            abort(f"{sec}.{key} old fragment {old!r} occurs "
                  f"{cur.count(old)}x, expected 1x: {cur!r}")
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
        if "vendored" in cur and "vendored" not in new:
            abort(f"{sec}.{key} would drop vendored token")
        if BLIND_RE.search(new):
            abort(f"{sec}.{key} new value still has blind-family word: {new!r}")
        d[sec][key] = new

    # Adverbial guard: 무작정 / 맹목 must survive untouched.
    for sec, key in ADVERBIAL_KEYS:
        v = get(sec, key)
        if ("무작정" not in v and "맹목" not in v):
            abort(f"{sec}.{key} lost adverbial 무작정/맹목: {v!r}")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("ko: blind -> private replacements applied.")


if __name__ == "__main__":
    main()
