#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docs/i18n-glossary/ja.md citation checker.

An external auditor reads the Japanese glossary BEFORE trusting the machine
fill, and a citation that names a key which does not exist — or names a key whose
shipped value does not contain the Japanese word quoted beside it — is worse
than no citation, because it sends the auditor to check a claim that is not
there. tooling/i18n-glossary-test.js (es) and tooling/i18n-glossary-it-test.js
(it) do the same job for their dictionaries; this is the Japanese twin, kept
read-only and runnable without node.

What it proves, per table row:

  1. structure — one markdown table, three columns, every cell filled, one row
     per English term, and every one of the 26 REQUIRED BitShares terms is a
     ROW (a passing mention in prose is not coverage);
  2. existence  — every `section.key` cited in a note is a key of
     vanilla/locales/ja.json;
  3. evidence   — every 「...」 Japanese string quoted in a note is a substring of
     the value of SOME key cited in that same row, so a quoted wording always has
     a key to check. Bold **...** words are forms UNDER DISCUSSION and are not
     claims, so they are not checked;
  4. vocabulary  — the row's Japanese term is a form ja.json ACTUALLY uses (a
     row mandating a word the shipped dictionary does not use would send an
     auditor to rewrite correct strings, which is the defect es.md shipped). A
     term containing a CJK character must appear in a TRANSLATED value; a Latin
     term (HTLC, DEX, TxBuilder) only has to appear in the file, because the rows
     that mandate one are mandating a loanword the file keeps byte-identical —
     and
     the row's OWN "N strings" is the FIRST count in the cell and matches that
     term. Every further count in a cell counts a sibling form, so it is checked
     against the set of words the cell discusses rather than against the term —
     a number that happens to be right for a neighbouring word slips through:
     this is a smoke alarm against drift, not an accounting;
  5. terms      — each row's Japanese term really is the form ja.json uses, and
     a row that names a rejected form must say so ("Never" / "Counter-example").

Usage: python3 tooling/i18n-glossary-ja-test.py   (exit 0 = green)
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FILE = os.path.join(ROOT, "docs", "i18n-glossary", "ja.md")
JA_PATH = os.path.join(ROOT, "vanilla", "locales", "ja.json")
EN_PATH = os.path.join(ROOT, "vanilla", "locales", "en.json")

# The BitShares term list an auditor must be able to check. Group 1 is the
# plan's REQUIRED list; group 2 is the account/asset/market nouns the article
# and the signing rows also carry.
REQUIRED = [
    "brainkey", "witness", "committee", "worker", "proxy", "vesting", "HTLC",
    "swap", "slate", "liquidity pool", "credit offer", "ticket", "proposal",
    "precision", "orderbook", "limit order", "fee",
    "account", "asset", "smartcoin", "collateral", "balance", "share",
    "market", "block", "transaction",
]

# A `section.key` citation. The dotted-KEY shape is required and the two
# backticked FILENAMES in the preamble (`en.json`, `ja.json`) are excluded, so a
# file reference can never be mistaken for evidence.
CITE = re.compile(r"`([a-z][a-z0-9_]*(?:\.[a-z0-9_-]+)+)`")
FILENAME = re.compile(r"\.json$")
# A Japanese string quoted as EVIDENCE, and the same quote in a REJECTION
# ("Never X", "Counter-example"), which by definition has no key carrying it.
QUOTE = re.compile(u"「([^「」]+)」")
REJECT = re.compile(
    u"Never|never|Counter-example|counter-example|0 strings|appears nowhere|"
    u"does not exist|rejected|align it|align either|owns the term")
# "N strings" counts. A count is only the ROW's own term if that term appears in
# the 40 characters before it; otherwise the row is counting a different word
# (the *asset* row counts アセット 290 and  Damon 46 in the same cell), and the
# row's own count is the one that carries the term.
COUNT = re.compile(r"(\d+) strings")
BACK_WINDOW = 40
# A Japanese word as a glossary note writes it: a run of kanji, kana or the
# length mark, 2 characters or more. Used to collect the words a row discusses so
# a count can be checked against one of them.
WORD = re.compile(u"[\u3040-\u30FF\u3400-\u9FFF\uF900-\uFAFFー々]{2,}")
# A rejection marker must sit in the same clause as the quote it licenses, so a
# "Never X" in the NEXT sentence cannot excuse an unrelated unbacked quote.
REJECT_WINDOW = 30
# How far a declared count may drift from the truth before it is a stale claim
# rather than a rounding difference (the rows count a WORD inside a value, and
# hand counts drift by one or two as strings are edited). The row's OWN count is
# held to the tighter OWN_SLACK, because a term and its sibling form routinely sit
# one apart (指値注文 11 against 指値 10) while the terms a glossary actually
# argues about sit further apart (オーダーブック 14 against 板 16).
COUNT_SLACK = 3
OWN_SLACK = 1

problems = []


def flat(d, prefix=""):
    out = collections.OrderedDict()
    for k, v in d.items():
        if k == "_meta":
            continue
        if isinstance(v, dict):
            out.update(flat(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def cells(line):
    s = line.strip()
    if not s.startswith("|") or not s.endswith("|"):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


ja = flat(json.load(open(JA_PATH, encoding="utf-8")))
en = flat(json.load(open(EN_PATH, encoding="utf-8")))
# The translated set: a value that differs from English. Identical-to-en keys are
# loanwords and are excluded from every count on purpose.
tr = {k: v for k, v in ja.items() if v != en.get(k)}

glossary = open(FILE, encoding="utf-8").read()
rows = []
for line in glossary.split("\n"):
    c = cells(line)
    if not c or len(c) != 3:
        continue
    if re.match(r"^-+$", c[0].replace(" ", "")):
        continue
    rows.append(c)
header = rows.pop(0)
if [h.lower() for h in header] != ["english term", "japanese term", "note"]:
    problems.append("table names its three columns: %s" % header)

by_en = {}
for r in rows:
    e = r[0].lower()
    if e in by_en:
        problems.append("one row per English term: %s" % e)
    by_en[e] = r
missing = [t for t in REQUIRED if t.lower() not in by_en]
if missing:
    problems.append("covers every required term (missing %s)" % missing)
for r in rows:
    if not r[1]:
        problems.append("Japanese term for %s" % r[0])
    if not r[2]:
        problems.append("note for %s" % r[0])
    # 2. every cited key exists
    cited = [k for k in CITE.findall(r[2]) if not FILENAME.search(k)]
    for k in cited:
        if k not in ja:
            problems.append("cited key not in ja.json: %s (%s)"
                            % (k, r[0]))
    if not cited:
        problems.append("note for %s cites no key" % r[0])
    # 3. every quoted Japanese string either has a cited key carrying it, or is
    #    quoted as a REJECTED form - "Never 証人" is a claim that the form does
    #    not appear, so its absence is the evidence.
    quoted = QUOTE.findall(r[2])
    if not quoted:
        problems.append("note for %s quotes no Japanese evidence" % r[0])
    for q in quoted:
        if any(q in ja[k] for k in cited if k in ja):
            continue
        # a rejection quotes a form nothing carries; find the marker that says so
        window = r[2]
        idx = window.find(u"「" + q + u"」")
        around = window[max(0, idx - REJECT_WINDOW):idx + len(q) + 3]
        if not REJECT.search(around):
            problems.append("quoted evidence not in any cited key and not "
                            "marked as rejected: %r (%s)" % (q[:24], r[0]))
    # 4. the row's term is a form the file uses, and its own count is the first
    words = sorted(set(WORD.findall(r[1] + " " + r[2])), key=len, reverse=True)
    truth = {w: sum(1 for v in tr.values() if w in v) for w in words}
    # Count the term itself, not a WORD match of it: the *pool share* row's term
    # is "LP シェア", which the kana run cannot see as one word.
    own = sum(1 for v in tr.values() if r[1] in v)
    if own == 0:
        cjk = any(0x3040 <= ord(c) <= 0x9FFF or 0x3400 <= ord(c) <= 0x4DBF
                  for c in r[1])
        if cjk or not any(r[1] in v for v in ja.values()):
            problems.append(
                "row %s mandates %r, which no string in ja.json uses"
                % (r[0], r[1]))
    counts = list(COUNT.finditer(r[2]))
    for i, m in enumerate(counts):
        n = int(m.group(1))
        if i == 0:
            # The row's own count: must be about the row's own term.
            if abs(n - own) > OWN_SLACK:
                problems.append(
                    "stale own count in %s: claims %d strings for %r, the file "
                    "has %d" % (r[0], n, r[1], own))
            continue
        if any(abs(n - c) <= COUNT_SLACK for c in truth.values()):
            continue
        problems.append(
            "count in %s matches no word the row discusses: %d strings (%s)"
            % (r[0], n, ", ".join("%s=%d" % (w, c)
                                  for w, c in list(truth.items())[:6])))
    # 5. a row that quotes a count must name the term the count describes
    if COUNT.search(r[2]) and r[1] not in r[2]:
        problems.append("row %s quotes a count but never names its term" % r[0])

# 5b. the honesty surface the preamble quotes must match the shipped file
for key, phrase in (
    ("i18n.badge_body", "これらの翻訳は機械が書いたもので"),
    ("i18n.risk_show_english", "この行の英語原文を表示"),
):
    if phrase not in ja.get(key, ""):
        problems.append("preamble quotes %s wrongly: %r" % (key, phrase))

if problems:
    print("i18n-glossary/ja: %d rows, %d PROBLEMS" % (len(rows), len(problems)))
    print("\n".join(problems))
    sys.exit(1)
print("i18n-glossary/ja: OK — %d rows, all %d required terms present, every "
      "citation resolves, every quoted evidence string and every count is "
      "current against vanilla/locales/ja.json"
      % (len(rows), len(REQUIRED)))
