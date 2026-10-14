#!/usr/bin/env python3
"""Rename blind -> private wording in hi.json (REPLACE, not insert).

Owns: the hi ब्लाइंड/ब्लाइंडेड -> प्राइवेट value replacements only
  (11 keys).
Consumes: vanilla/locales/hi.json (ordered dict).
Side effects: overwrites hi.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-blind-cjk-ru-hi (hi batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise: the old fragment must occur exactly once, the current
must carry a blind-family word, the derived new value must equal the
hardcoded expectation, and placeholders / op numbers / vendored tokens
are preserved verbatim. Formal आप register and postpositions (से/को)
untouched; compounds mirrored exactly. प्राइवेट matches the already
audited "private key" vocabulary (प्राइवेट कुंजी). Adverbial आँख बंद
कर / आँख मूँदकर ("eyes closed" = blindly) is NOT touched.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

NEW = "प्राइवेट"
BLIND_RE = re.compile(r"ब्लाइंड")
OP_RE = re.compile(r"op(?:s)?\s*\d[\d/]*", re.IGNORECASE)

# (section, key, old fragment, expected new value).
TARGETS = [
    ("account", "op_blind_from",
     "ब्लाइंड", "प्राइवेट से ट्रांसफर"),
    ("account", "op_blind_to",
     "ब्लाइंड", "प्राइवेट को ट्रांसफर"),
    ("account", "op_blind_transfer",
     "ब्लाइंड", "प्राइवेट ट्रांसफर"),
    ("account", "sum_blind",
     "ब्लाइंड", "प्राइवेट ट्रांसफर (%(in)s अंदर, %(out)s बाहर)"),
    ("proposal", "err_blind_disabled",
     "ब्लाइंड", "प्राइवेट ट्रांसफर अक्षम हैं: उन्हें एम्बेडेड कमिटमेंट/रेंज-प्रूफ क्रिप्टो चाहिए (केवल पढ़ने योग्य खोज)।"),
    ("vesting", "blind_op39",
     "ब्लाइंड", "प्राइवेट को ट्रांसफर (op 39)"),
    ("vesting", "blind_op40",
     "ब्लाइंड", "प्राइवेट ट्रांसफर (op 40)"),
    ("vesting", "blind_op41",
     "ब्लाइंड", "प्राइवेट से ट्रांसफर (op 41)"),
    ("vesting", "blind_transfers_ops_39_40_41_are_disabled_the",
     "ब्लाइंड", "प्राइवेट ट्रांसफर (op 39/40/41) अक्षम हैं: उन्हें वेंडर किए गए Pedersen-प्रतिबद्धता और रेंज-प्रूफ क्रिप्टो चाहिए जो कोई स्थिर पेज नहीं देता। नीचे प्रतिबद्धता जानकारी केवल पठन मार्ग सिद्ध करती है।"),
    ("vesting", "blinded_balances_read_only",
     "ब्लाइंडेड", "प्राइवेट बैलेंस (केवल-पठन)"),
    ("vesting", "disabled_blind_transfers_need_vendored_commit",
     "ब्लाइंड", "अक्षम: प्राइवेट ट्रांसफर को वेंडर की गई प्रतिबद्धता/रेंज-प्रूफ क्रिप्टो चाहिए।"),
]

# Adverbial keys allowed to keep आँख after the run.
ADVERBIAL_KEYS = {
    ("createworker", "send_failed_check_state_before_retrying_do_no"),
    ("help", "topic_witnesses_body"),
    ("vote", "sent_note"),
    ("common", "failed_check_state"),
}


def abort(msg):
    print(f"ABORT hi: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # Whole-file footprint: ब्लाइंड must live in exactly the 11 targets
    # (ब्लाइंडेड contains ब्लाइंड as a substring; adverbials use आँख).
    found = {(sec, k) for sec in d for k, v in d[sec].items()
             if isinstance(v, str) and "ब्लाइंड" in v}
    want = {(s, k) for s, k, _, _ in TARGETS}
    if found != want:
        abort(f"unexpected ब्लाइंड footprint: extra={found - want} "
              f"missing={want - found}")

    for sec, key, old, expected in TARGETS:
        cur = get(sec, key)
        if not isinstance(cur, str) or not BLIND_RE.search(cur):
            abort(f"{sec}.{key} current value lacks blind-family word: {cur!r}")
        if cur.count(old) != 1:
            abort(f"{sec}.{key} old fragment {old!r} occurs "
                  f"{cur.count(old)}x, expected 1x: {cur!r}")
        new = cur.replace(old, NEW)
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

    # Adverbial guard: आँख forms must survive untouched.
    for sec, key in ADVERBIAL_KEYS:
        v = get(sec, key)
        if "आँख" not in v:
            abort(f"{sec}.{key} lost adverbial आँख: {v!r}")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("hi: blind -> private replacements applied.")


if __name__ == "__main__":
    main()
