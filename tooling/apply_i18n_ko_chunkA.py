#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ko chunk-A: fill the six desk sections ko.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ko.json, or one whose English master moved, is REFUSED;
  * KO + KEPT_ENGLISH together must account for EVERY untranslated key of the
    six sections, so a forgotten string is a refusal, never a silent English.

This is the Korean sibling of tooling/apply_i18n_ja_chunkA.py and keeps its
gates one for one, with two of them INVERTED for Korean (G7 and G8 below) —
inverting them silently would be the worst kind of copy-paste bug.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/check_i18n.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an unclaimed key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  ko hygiene     no value this batch writes may carry an ASCII or
                      typographic apostrophe, an ideographic space (U+3000), a
                      Cyrillic/Devanagari/other CJK letter, or an invisible
                      code point. ko.json already ships 3,167 translated
                      strings with ZERO apostrophes (it quotes with “”, the
                      convention its own `uri.*` errors already use), and a
                      Cyrillic or Han letter in a Korean string is not a typo,
                      it is a different language. Hangul is what this file is
                      FOR, so it is of course allowed.
  G8  dot hygiene    INVERTED from the ja batch: Korean attaches the middle
                      dot, it does not float it. A dot with a space on either
                      side is a refusal; a dot glued to its neighbours is
                      correct, as is the algebraic x·y=k notation. ko.json's own
                      translated prose already writes it that way
                      ("계정을 등록·추천한 주체", "동기화·브로드캐스트되지"),
                      while the spaced “ · ” forms that survive in ko.json all
                      live in KEPT_ENGLISH glue strings or in other batches'
                      keys. The sweep runs file-wide; a hit OUTSIDE the six
                      sections is reported as PRE-EXISTING and does not gate
                      this batch, because repairing a neighbour here would be
                      exactly the silent edit the scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                      LOAN below, or the write is refused. A Korean crypto UI
                      prints HTLC, DEX, BitShares, BTS, Memo, Smartcoin, Brainkey
                      and the indicator tickers in Latin exactly as a Japanese
                      one prints DEX and HTLC — a fake hangul spelling
                      ("에이치티엘씨") would be worse than the loanword. The
                      gate is batch-scoped on purpose: the rest of ko.json
                      already carries hundreds of distinct Latin tokens from
                      earlier batches, and re-litigating those is not this
                      file's job.

Register: the 3,167 strings ko.json already ships are POLITE and split the way
Korean splits them — “~습니다” for statements ("잔액을 불러오지 못했습니다.",
"여기에 표시됩니다.") and “~하십시오” for instructions addressed to the reader
("계정 이름을 입력하십시오.", "시장을 선택하십시오."). This batch is polite too.
Labels and column heads stay bare nouns ("잔액", "주문", "자산"), which is how
a table head reads in any register.

Spacing: this is the one place Korean is NOT like Japanese. Korean writes real
spaces between its words, so every space the English master has is real
grammar here and this batch invents none and removes none. What it does NOT do
is translate the space inside a GLUE string — the trailing space on
account.page_total and the leading one on account_net.more_assets are layout,
not prose, and the two pure-symbol cards in KEPT_ENGLISH stay English because
their separator IS their content.

Particles: the 3,167 shipped strings already fixed the placeholder-particle
problem with the parenthesised dual forms — "%(name)s은(는)", "%(amount)s을(를)",
"%(name)s(으)로" — and the universal ones where no form is needed ("의", "에게",
"에게서"). This batch reuses exactly that convention rather than inventing one.

Quotation: “ ”, matching the ko strings that already quote (uri.error_*,
proposal). The `account.sum_worker_create` worker name therefore becomes
“%(name)s”, not "…".

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md 3.5) — and no prose number is invented. Where the
English quotes one (first 8 publishers, first 100, op 19, op 23, 24h, 90d,
7-day, 175) the translation keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ko_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ko_chunkA.py --apply         # writes ko.json
  python3 tooling/apply_i18n_ko_chunkA.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
KO_PATH = os.path.join(BASE, "ko.json")

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from KO below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live in this batch's own settings section; the shell brands live
# outside it and are kept in the list so a drift anywhere in the file is caught.
PINNED = (
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
    "settings.network_mainnet",
    "settings.network_testnet",
    "settings.network_devnet",
    "settings.custom_placeholder",
    "settings.pending",
    "settings.dash",
    "settings.theme_original_blue",
    "settings.theme_light",
    "settings.theme_dark",
)

PLACEHOLDER = re.compile(r"%\([A-Za-z0-9_]+\)s")
BRACE = re.compile(r"\{[A-Za-z0-9_]+\}")
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")
INVISIBLE = re.compile(u"[­‍⁠﻿]")
DOT_CHARS = u"·•‧･"
APO_TYPO = u"’"
APO_ASCII = u"'"
IDEO_SPACE = u"　"
# G7: a letter from a script this file must never emit. Written as explicit
# \uXXXX escapes on purpose: typing these block ends by hand is exactly how a
# range silently swallows Hangul (U+AC00..U+D7A3) and the gate then fires on
# every Korean word in the file. The four Korean blocks below are deliberately
# ABSENT — Hangul syllables, Hangul jamo, Hangul compatibility jamo and the
# jamo-extended block are the point of this batch, not contamination.
FOREIGN = re.compile(
    u"[\u0400-\u04ff"      # Cyrillic
    u"\u0500-\u052f"        # Cyrillic supplement
    u"\u0900-\u097f"        # Devanagari
    u"\u0e00-\u0e7f"        # Thai
    u"\u0e80-\u0eff"        # Lao
    u"\u1000-\u109f"        # Myanmar
    u"\u1200-\u137f"        # Ethiopic
    u"\u1400-\u167f"        # Canadian aboriginal
    u"\u1780-\u17ff"        # Khmer
    u"\u1800-\u18af"        # Mongolian
    u"\u1a00-\u1aff"        # Tibetan / Lepcha
    u"\u1e00-\u1eff"        # Latin-Indic / Thai extra
    u"\u3040-\u30ff"        # Hiragana + Katakana
    u"\u3100-\u312f"        # Bopomofo (Chinese phonetic)
    u"\u31f0-\u31ff"        # Katakana phonetic extensions
    u"\u3400-\u4dbf"        # CJK unified ideographs extension A
    u"\u4e00-\u9fff"        # CJK unified ideographs
    u"\uf900-\ufaff"        # CJK compatibility ideographs
    u"\uff66-\uff9f"        # halfwidth kana
    u"\uff00-\uffef"        # fullwidth forms
    u"\u31c0-\u31ef"        # CJK strokes
    u"\u3200-\u32ff"        # enclosed CJK letters and months
    u"]"
)
# Hangul lives at U+1100..U+11FF (jamo), U+3130..U+318F (compatibility jamo),
# U+A960..U+A97F, U+D7B0..U+D7FF and U+AC00..U+D7A3 (syllables). None of them
# is listed above, and that omission IS the exemption — a single mis-typed
# range end would swallow U+AC00..U+D7A3 and the gate would fire on every
# Korean word in the file, so the ranges stay as escapes a reader can audit.

# G9: a Latin run inside a Korean value. A token may continue through - _ . /
# so "Same-T", "get_settle_orders" and "ipaddress.to" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Korean crypto UI prints in Latin, an API/route name the reader has to
# recognise, or a keyboard key; anything else has to be Korean.
LOAN = frozenset((
    # Brands / chain / asset symbols the brief pins.
    "BTS", "BitShares", "DEX",
    # Operation and protocol acronyms a Korean BitShares UI keeps in Latin.
    "CER", "FBA", "HTLC", "MCR", "MSSR", "NFT", "PMA", "UIA",
    # Feature names Korean crypto UIs loan rather than translate.
    "Brainkey", "Memo", "Proxy", "Smartcoin", "Swap",
    # Indicator tickers — a chart legend of hangul would be unreadable.
    "BB", "EMA", "PSAR", "SMA",
    # Identifiers, keys and method names a reader types or recognises.
    "Enter", "GitHub", "ID", "URL",
    # API method quoted verbatim in market.settle_first100's limit note.
    "get_settle_orders",
    # Host + scheme quoted verbatim in settings.geo_note.
    "https", "ipaddress.to",
    # The op-number marker "(op 23)" / "(op %(op)s)" the brief keeps.
    "op",
    # Same-T fund family name (ops 47/48/49/50 and their history lines).
    "Same-T",
))


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    Korean attaches a middle dot to its neighbours (G8), so the ja rule ("a
    dot must be space-separated") is inverted here. The one clean exception is
    algebraic notation — both neighbours alphanumeric, as in "x·y=k".
    """
    hit = INVISIBLE.search(value)
    if hit:
        return hit.group(0)
    for i, ch in enumerate(value):
        if ch in DOT_CHARS:
            before = value[i - 1] if i else u" "
            after = value[i + 1] if i + 1 < len(value) else u" "
            if before.isalnum() and after.isalnum():
                continue
            if before == u" " or after == u" ":
                return ch
    return None


# --------------------------------------------------------------------------
# helpers + gates
# --------------------------------------------------------------------------
def flat(d, prefix=""):
    """Flatten a locale dict to dotted leaf keys, skipping _meta."""
    out = collections.OrderedDict()
    for k, v in d.items():
        if k == "_meta":
            continue
        if isinstance(v, dict):
            out.update(flat(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def deep_set(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def load(path):
    """Read a locale file keeping key order."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def check_batch(en_flat, key, value, problems, chars=True):
    """G1-G4, G7, G8 + punctuation hygiene for one key/value pair.

    `chars=False` runs every structural rule but leaves the character sweep to
    the caller; verify() uses it for the keys this batch does not own, where a
    stray character is a neighbour's finding to report, not this batch's.
    """
    master = en_flat[key]
    if sorted(PLACEHOLDER.findall(master)) != sorted(
        PLACEHOLDER.findall(value)
    ):
        problems.append("placeholder multiset changed: %s" % key)
    if sorted(BRACE.findall(master)) != sorted(BRACE.findall(value)):
        problems.append("brace placeholder changed: %s" % key)
    if IDENT.match(master) and master != value:
        problems.append("identifier not byte-verbatim: %s" % key)
    if key in PINNED and master != value:
        problems.append("pinned key not byte-verbatim: %s" % key)
    if master.count("\n") != value.count("\n"):
        problems.append(
            "line count changed: %s (en %d, ko %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    if not chars:
        return
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_ko_hygiene(batch, problems):
    """G7 + G9: apostrophes, foreign scripts, undeclared Latin.

    Scoped to the values THIS BATCH writes. ko.json's other sections carry
    their own Latin tokens from earlier batches; re-auditing those here would
    make this file the owner of someone else's vocabulary.
    """
    for key, value in sorted(batch.items()):
        # Interpolations are substituted data, not prose: %(name)s and {s} must
        # never count as an undeclared loanword (G1 proves they survived).
        prose = PLACEHOLDER.sub("", value)
        prose = BRACE.sub("", prose)
        # A count keeping its English unit suffix ("90d", "24h") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # into "90일" without changing the number the reader compares against
        # the range control beside it.
        prose = COUNT_UNIT.sub("", prose)
        if APO_ASCII in value:
            problems.append("G7: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7: typographic apostrophe in %s" % key)
        if IDEO_SPACE in value:
            problems.append("G7: ideographic space in %s" % key)
        hit = FOREIGN.search(value)
        if hit:
            problems.append("G7: foreign script %r in %s" % (hit.group(0), key))
        for token in sorted(set(LATIN_TOKEN.findall(prose))):
            if token not in LOAN:
                problems.append("G9: undeclared Latin token %r in %s"
                                % (token, key))


def verify():
    """Structural re-proof of the shipped file against the en master."""
    ko, en = load(KO_PATH), load(EN_PATH)
    d, e = flat(ko), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: chunk-B (or whoever wrote the
    # section) owns them, and an insert-only batch that "fixed" a neighbour
    # would be the silent edit the scope refusal exists to prevent. Only `bad`
    # - problems this batch can answer for - gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
            check_batch(e, key, d[key], bad, chars=key in KO)
        if PLACEHOLDER.findall(e[key]):
            ph_filled += 1
            if sorted(PLACEHOLDER.findall(e[key])) == sorted(
                PLACEHOLDER.findall(d[key])
            ):
                ph_ok += 1
        if "\n" in e[key] or "\n" in d[key]:
            multi += 1
            if e[key].count("\n") == d[key].count("\n"):
                multi_ok += 1
        if LINK_HASH.findall(e[key]) or LINK_HASH.findall(d[key]):
            links += 1
            if LINK_HASH.findall(e[key]) == LINK_HASH.findall(d[key]):
                links_ok += 1
        hit = suspicious(d[key])
        if hit:
            where = ("suspicious code point U+%04X in %s"
                     % (ord(hit), key))
            if key in KO:
                bad.append(where)
            else:
                pre.append(where)
    check_ko_hygiene(KO, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(KO) if d.get(k) == e.get(k)]
    for k in sorted(KEPT_ENGLISH):
        if d.get(k) != e.get(k) or d.get(k) != KEPT_ENGLISH[k]:
            bad.append("kept-english key drifted: %s" % k)
    by_section = {}
    for k in same + sorted(KEPT_ENGLISH):
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1
    scope_left = [
        k for k in sorted(e)
        if k.split(".")[0] in SECTIONS and d.get(k) == e[k]
        and k not in KO and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(KO) - len(same), len(KO)))
    print("  keys kept byte-identical to en on purpose: %d"
          % (len(KEPT_ENGLISH) + len(same)))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch              : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash    : %d (hashes ok: %d)"
          % (links, links_ok))
    for sec in sorted(by_section):
        print("    %-12s %d identical to en" % (sec, by_section[sec]))
    print("  keys in my sections still at en, not in this batch: %d"
          % len(scope_left))
    for k in scope_left:
        print("      %s = %r" % (k, d.get(k)))
    meta = ko.get("_meta", {})
    print("  _meta version=%r untranslated=%r translated=%d entries"
          % (meta.get("version"), meta.get("untranslated"),
             len(meta.get("translated", []))))
    if pre:
        print("PRE-EXISTING, outside this batch (not touched, not fixed):")
        print("\n".join("  " + p for p in sorted(set(pre))))
    if bad:
        print("FAILURES:")
        print("\n".join(bad))
        return 1
    print("  all gates green")
    return 0


def main():
    argv = sys.argv[1:]
    if "--verify" in argv:
        return verify()
    apply = "--apply" in argv

    # G6: the on-disk formatting must survive a plain round trip, or this
    # script would reformat a file it is only supposed to fill.
    raw = open(KO_PATH, encoding="utf-8").read()
    ko = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(ko, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: ko.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(ko))
    before_meta = json.dumps(ko["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(KO.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in ko.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            continue  # already applied by an earlier run
        if cur != en_flat[key]:
            problems.append(
                "would overwrite a real translation: %s (%r)" % (key, cur)
            )
            continue
        check_batch(en_flat, key, value, problems)
        planned.append(key)
        deep_set(ko, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(KO) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (KO and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(KO) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in ko.json: %s" % key)
            return 1
        if value != en_flat[key]:
            print("REFUSING: kept-english value is not the English string: "
                  "%s (%r vs en %r)" % (key, value, en_flat[key]))
            return 1
    uncovered = sorted(
        k for k in en_flat
        if k.split(".")[0] in SECTIONS
        and k not in owned and before.get(k) == en_flat[k]
    )
    if uncovered:
        print("REFUSING: %d key(s) of my sections are in neither table: %s"
              % (len(uncovered), ", ".join(uncovered[:8])))
        return 1

    check_ko_hygiene(KO, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(ko)
    for key in after:
        if key in planned:
            continue
        if after[key] != before.get(key):
            print("REFUSING: untouched key changed: %s" % key)
            return 1
    if set(after) != set(before):
        print("REFUSING: key set changed")
        return 1
    for key in PINNED:
        if key in after and after[key] != en_flat.get(key):
            print("REFUSING: pinned key drifted: %s" % key)
            return 1

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in planned if after[k] == en_flat[k]]
    by_section = {}
    for k in changed:
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1

    # G5b: _meta.translated is the v1 CLAIM "these keys are translated", and
    # tooling/check_i18n.py reads it in both directions - a claimed key that
    # still reads English is a false claim, and an unclaimed key that is no
    # longer English is an undeclared translation. So the claim moves in
    # lockstep with the bytes, for exactly the keys this batch translated. The
    # values kept byte-identical on purpose (loanwords, brands, ids, glue) stay
    # UNCLAIMED, which is the honest state for them - and check_i18n.py
    # separately forbids claiming its IDENTIFIERS list. Nothing else in _meta
    # moves - filling strings is not verification, so the controller's v2
    # provenance/verified/high_risk fields stay untouched.
    meta = ko["_meta"]
    meta_fields = set(meta)
    if meta.get("version") != 1 or meta.get("untranslated") is not False:
        print("REFUSING: _meta is not a v1 dict (version=%r untranslated=%r)"
              % (meta.get("version"), meta.get("untranslated")))
        return 1
    claimed = meta.get("translated")
    if (not isinstance(claimed, list)
            or any(not isinstance(k, str) for k in claimed)):
        print("REFUSING: _meta.translated is not a list of strings")
        return 1
    unknown = sorted(set(claimed) - set(en_flat))
    if unknown:
        print("REFUSING: _meta.translated names keys absent from en: %s"
              % ", ".join(unknown[:5]))
        return 1
    lie = sorted(k for k in claimed
                 if k in before and before[k] == en_flat[k])
    if lie:
        print("REFUSING: _meta.translated claims keys that still read "
              "English: %s" % ", ".join(lie[:5]))
        return 1
    added = sorted(k for k in KO
                   if after[k] != en_flat[k] and k not in claimed)
    meta["translated"] = sorted(set(claimed) | set(added))
    if claimed != sorted(claimed):
        print("REFUSING: _meta.translated was not sorted")
        return 1
    if set(meta) != meta_fields:
        print("REFUSING: _meta field set changed")
        return 1
    still_here = sorted(set(meta_fields) - {"translated"})
    if json.dumps(
        {k: meta[k] for k in still_here}, sort_keys=True, ensure_ascii=False
    ) != json.dumps(
        {k: json.loads(before_meta)[k] for k in still_here},
        sort_keys=True, ensure_ascii=False,
    ):
        print("REFUSING: _meta changed outside translated")
        return 1

    print("ko chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue / "
              "sentinels - deliberately NOT claimed):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run - no files written (pass --apply)")
        return 0

    with open(KO_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ko, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/ko.json")
    return 0


KO = {
    # =========================================================== account (150)
    # The shared-account line: "active" and "owner" are the two key roles, and
    # ko's permissions help already calls them 활성 and 오너 ("두 개의 자물쇠:
    # 활성과 오너"), so the line reuses that pair rather than inventing a
    # third spelling. The middle dot is attached - Korean, not Japanese (G8).
    "account.draw_network": u"네트워크 그리기",
    "account.lookup_placeholder": u"계정 이름",
    "account.multisig_checking": u"권한 확인 중…",
    "account.multisig_open_txbuilder": u"트랜잭션 빌더 열기",
    "account.multisig_shared": (
        u"공유 계정 — 활성 %(ath)s/%(an)s·오너 %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        u"단일 키 — 활성 %(ath)s/%(an)s·오너 %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"공유 계정입니까? 제안은 제안 페이지에 있습니다."
    ),
    "account.multisig_unavailable": (
        u"권한을 확인할 수 없습니다 — 제안은 제안 페이지에서 계속 볼 수 있습니다."
    ),
    "account.multisig_view_proposals": u"제안 보기",
    # Operation labels. Nominal, like the translated ones ("계정 생성",
    # "지정가 주문 생성", "주문 체결") so a history column reads as a list of
    # nouns. "오퍼레이션" is ko.json's established word for a chain operation.
    "account.op_assert_op": u"어서트",
    "account.op_asset_burn": u"자산 소각",
    "account.op_asset_issue": u"자산 발행",
    "account.op_asset_settle": u"자산 정산",
    "account.op_asset_update": u"자산 업데이트",
    "account.op_authority_create": u"권한 생성",
    "account.op_authority_delete": u"권한 삭제",
    "account.op_authority_update": u"권한 업데이트",
    "account.op_balance_claim": u"잔액 청구",
    # The blind legs reuse the word vesting.blind_op40 already ships for op 40
    # (블라인드 이체), so the history column and the help text say one thing.
    "account.op_blind_from": u"블라인드에서 이체",
    "account.op_blind_to": u"블라인드로 이체",
    "account.op_blind_transfer": u"블라인드 이체",
    "account.op_claim_fees": u"수수료 청구",
    "account.op_claim_pool": u"풀 청구",
    "account.op_collateral_bid": u"담보 입찰",
    "account.op_committee_join": u"위원회 참여",
    "account.op_committee_update": u"위원회 업데이트",
    "account.op_custom_op": u"사용자 지정 오퍼레이션",
    # 계약 is credit.deal's shipped word for a credit deal, so the three deal
    # labels and their history lines agree with the credit desk.
    "account.op_deal_expired": u"계약 만료",
    "account.op_deal_repay": u"계약 상환",
    "account.op_deal_update": u"계약 업데이트",
    # 자동이체 is menu.p_debit and help.topic_direct-debit_title's shipped word
    # for Direct Debit (debit.title spells it 직접 출금, but the menu and the
    # help article are the two the reader meets first).
    "account.op_debit_claim": u"자동이체 청구",
    "account.op_debit_create": u"자동이체 생성",
    "account.op_debit_delete": u"자동이체 삭제",
    "account.op_debit_update": u"자동이체 업데이트",
    "account.op_execute_bid": u"입찰 실행",
    "account.op_fba_distribute": u"FBA 분배",
    "account.op_fee_pool_fund": u"수수료 풀 펀드",
    "account.op_feed_producers_update": u"피드 생산자 업데이트",
    "account.op_feed_publish": u"피드 게시",
    "account.op_global_settle": u"전체 정산",
    "account.op_htlc_create": u"HTLC 생성",
    "account.op_htlc_extend": u"HTLC 연장",
    "account.op_htlc_redeem": u"HTLC 상환",
    "account.op_htlc_redeemed": u"HTLC 상환됨",
    "account.op_htlc_refund": u"HTLC 환불",
    "account.op_issuer_update": u"발행자 업데이트",
    # 신용 제안 is credit.credit_offer's shipped word (Credit Offer), so the
    # accept/create/update labels and the offer history lines say one thing.
    "account.op_offer_accept": u"신용 수락",
    "account.op_offer_create": u"신용 제안 생성",
    "account.op_offer_delete": u"신용 제안 삭제",
    "account.op_offer_update": u"신용 제안 업데이트",
    "account.op_order_update": u"주문 업데이트",
    "account.op_override_transfer": u"오버라이드 이체",
    "account.op_params_update": u"글로벌 매개변수 업데이트",
    "account.op_pool_create": u"풀 생성",
    "account.op_pool_delete": u"풀 삭제",
    "account.op_pool_deposit": u"풀 입금",
    "account.op_pool_swap": u"풀 스왑",
    "account.op_pool_update": u"풀 업데이트",
    "account.op_pool_withdraw": u"풀 출금",
    "account.op_proposal_create": u"제안 생성",
    "account.op_proposal_delete": u"제안 삭제",
    "account.op_proposal_update": u"제안 업데이트",
    "account.op_samet_borrow": u"Same-T 대출",
    "account.op_samet_create": u"Same-T 펀드 생성",
    "account.op_samet_delete": u"Same-T 펀드 삭제",
    "account.op_samet_repay": u"Same-T 상환",
    "account.op_samet_update": u"Same-T 펀드 업데이트",
    "account.op_settle_cancel": u"정산 취소",
    "account.op_smartcoin_update": u"스마트코인 업데이트",
    "account.op_ticket_create": u"티켓 생성",
    "account.op_ticket_update": u"티켓 업데이트",
    "account.op_vesting_create": u"베스팅 생성",
    "account.op_vesting_withdraw": u"베스팅 출금",
    "account.op_witness_join": u"증인 참여",
    "account.op_witness_update": u"증인 업데이트",
    "account.op_worker_create": u"워커 생성",
    # Pager + its note. The trailing space on page_total is load-bearing: a
    # computed figure follows it, and 합계 is account.total's shipped word.
    "account.page_total": u"페이지 합계 ≈ ",
    "account.portfolio_page": u"페이지 %(page)s / %(pages)s",
    "account.prices_cover_this_page": (
        u"가격은 이 페이지의 자산에 적용됩니다 — 페이지를 넘기면 더 많은 자산의 "
        u"가격을 볼 수 있습니다."
    ),
    # History one-liners: a finished act, one row. Particles after a
    # placeholder use the parenthesised dual form ko.json already ships
    # ("%(name)s은(는)", "%(amount)s을(를)"); 에게/에게서/의 need no form.
    "account.sum_account_create": u"%(name)s 등록됨",
    "account.sum_account_transfer": u"계정을 %(owner)s에게 이전했습니다",
    "account.sum_account_update": u"계정 업데이트: %(account)s",
    "account.sum_asset_burn": u"%(amount)s 소각됨",
    "account.sum_asset_create": u"자산 %(symbol)s 생성됨",
    "account.sum_asset_issue": u"%(to)s에게 %(amount)s 발행",
    "account.sum_asset_settle": u"%(amount)s의 정산을 요청했습니다",
    "account.sum_asset_update": u"자산 %(asset)s 업데이트됨",
    "account.sum_authorities": u"%(account)s의 권한을 업데이트했습니다",
    "account.sum_balance_claim": u"%(amount)s 청구함",
    "account.sum_bid": u"%(coll)s 담보로 %(debt)s 입찰",
    "account.sum_blind": u"블라인드 이체(입금 %(in)s, 출금 %(out)s)",
    "account.sum_call_update": u"포지션 조정: 담보 %(coll)s, 부채 %(debt)s",
    "account.sum_claim_fees": u"수수료 %(amount)s 청구함",
    "account.sum_committee_create": u"위원회 위원이 되었습니다: %(account)s",
    "account.sum_committee_update": u"위원회 위원을 업데이트했습니다: %(account)s",
    "account.sum_custom": u"%(account)s의 사용자 지정 오퍼레이션",
    "account.sum_deal_expired": u"계약 만료됨: %(deal)s",
    "account.sum_deal_repay": u"계약 %(deal)s에 %(amount)s을(를) 상환했습니다",
    "account.sum_deal_update": u"계약 %(deal)s 업데이트됨",
    "account.sum_debit_claim": u"%(amount)s 자동이체 청구함",
    "account.sum_debit_create": (
        u"%(to)s에게 %(amount)s 자동이체를 승인했습니다"
    ),
    "account.sum_debit_delete": u"자동이체 권한 %(perm)s 삭제됨",
    "account.sum_debit_update": (
        u"%(to)s의 %(amount)s 자동이체를 업데이트했습니다"
    ),
    "account.sum_execute_bid": u"%(coll)s 담보로 %(debt)s 입찰 실행함",
    "account.sum_fee_pool_fund": (
        u"%(asset)s 수수료 풀에 %(amount)s을(를) 펀드했습니다"
    ),
    "account.sum_feed": u"%(publisher)s이(가) %(asset)s 피드를 게시했습니다",
    "account.sum_feed_producers": u"%(asset)s의 피드 생산자 %(n)s명을 설정했습니다",
    "account.sum_fill": u"체결: %(pays)s 지불, %(receives)s 수령",
    "account.sum_global_settle": u"%(asset)s 전체 정산됨",
    "account.sum_htlc_claimed": u"HTLC %(id)s 청구함",
    "account.sum_htlc_create": u"HTLC %(id)s: %(from)s → %(to)s %(amount)s",
    "account.sum_htlc_extend": u"HTLC %(id)s 연장함",
    "account.sum_htlc_redeem": u"HTLC %(id)s 상환함",
    "account.sum_htlc_refund": u"HTLC %(id)s 환불됨",
    "account.sum_issuer_update": u"%(asset)s의 새 발행자: %(issuer)s",
    "account.sum_offer_accept": (
        u"%(coll)s 담보로 %(amount)s을(를) 빌렸습니다(제안 %(offer)s)"
    ),
    "account.sum_offer_create": u"%(asset)s로 신용 제안을 생성했습니다",
    "account.sum_offer_delete": u"제안 %(offer)s 삭제됨",
    "account.sum_offer_update": u"제안 %(offer)s 업데이트됨",
    "account.sum_order_cancel": u"주문 %(order)s 취소됨",
    "account.sum_order_create": (
        u"%(sell)s을(를) 최소 %(buy)s와 교환하는 주문을 등록했습니다"
    ),
    "account.sum_order_update": u"주문 %(order)s 업데이트됨",
    "account.sum_pool_create": u"풀 %(a)s / %(b)s 생성됨",
    "account.sum_pool_delete": u"풀 %(pool)s 삭제됨",
    "account.sum_pool_deposit": (
        u"풀 %(pool)s에 %(a)s + %(b)s을(를) 스테이크했습니다"
    ),
    "account.sum_pool_swap": (
        u"풀 %(pool)s에서 %(sell)s → 최소 %(buy)s 스왑"
    ),
    "account.sum_pool_update": u"풀 %(pool)s 업데이트됨",
    "account.sum_pool_withdraw": (
        u"풀 %(pool)s에서 %(shares)s을(를) 언스테이크했습니다"
    ),
    "account.sum_proposal_create": u"오퍼레이션 %(n)s건을 제안했습니다",
    "account.sum_proposal_delete": u"제안 %(proposal)s 삭제됨",
    "account.sum_proposal_update": u"제안 %(proposal)s 승인함",
    "account.sum_samet_borrow": u"펀드 %(fund)s에서 %(amount)s을(를) 빌렸습니다",
    "account.sum_samet_create": u"Same-T 펀드를 생성했습니다(%(amount)s)",
    "account.sum_samet_delete": u"Same-T 펀드 %(fund)s 삭제됨",
    "account.sum_samet_repay": u"펀드 %(fund)s에 %(amount)s을(를) 상환했습니다",
    "account.sum_samet_update": u"Same-T 펀드 %(fund)s 업데이트됨",
    "account.sum_settle_cancel": u"%(amount)s의 정산을 취소했습니다",
    "account.sum_smartcoin_update": u"스마트코인 %(asset)s 업데이트됨",
    "account.sum_ticket_create": u"티켓 %(amount)s 생성됨",
    "account.sum_ticket_update": u"티켓 %(ticket)s 업데이트됨",
    "account.sum_transfer": u"%(from)s → %(to)s %(amount)s 이체",
    "account.sum_transfer_recv": u"%(from)s에게서 %(amount)s 수령",
    "account.sum_transfer_send": u"%(to)s에게 %(amount)s 전송함",
    "account.sum_upgrade": u"%(account)s 업그레이드함",
    "account.sum_vesting_create": u"%(owner)s에게 %(amount)s을(를) 베스팅했습니다",
    "account.sum_vesting_withdraw": u"베스팅된 %(amount)s을(를) 인출했습니다",
    "account.sum_whitelist": u"%(account)s을(를) 화이트리스트에 등록했습니다",
    "account.sum_witness_create": u"증인이 되었습니다: %(account)s",
    "account.sum_witness_update": u"증인 %(account)s 업데이트됨",
    # ko.json quotes with “” (its uri.* errors already do), never with an
    # apostrophe, and this file has zero apostrophes across 3,167 strings.
    "account.sum_worker_create": u"워커 “%(name)s” 생성",

    # ====================================================== account_net (64)
    "account_net.canvas_missing": (
        u"이 빌드에서는 네트워크 캔버스를 사용할 수 없습니다. "
        u"아래 표에 모든 연결이 표시됩니다."
    ),
    "account_net.class_credit": u"신용",
    "account_net.class_credit_help": u"수락·상환된 신용 제안.",
    "account_net.class_debit": u"자동이체",
    "account_net.class_debit_help": u"자동이체 권한과 출금.",
    "account_net.class_htlc_help": u"해시 타임락 계약과 그 업데이트.",
    "account_net.class_override": u"오버라이드 이체",
    "account_net.class_override_help": u"자산 발행자가 수수료를 부담하는 이체.",
    "account_net.class_transfer": u"이체",
    "account_net.class_transfer_help": u"계정 간 직접 이체.",
    "account_net.class_vesting": u"베스팅",
    "account_net.class_vesting_help": u"제3자가 관리하는 베스팅 잔액.",
    # Graph terms: a hop is one edge traversal, so 홉 is the single word the
    # depth label, the depth value and the table column all share.
    "account_net.depth_1": u"1홉",
    "account_net.depth_2": u"2홉",
    "account_net.depth_label": u"깊이",
    "account_net.detail_hint": (
        u"선을 탭하면 상세가 표시됩니다. 계정을 탭하면 계정 페이지가 열립니다."
    ),
    # The detail line is a dense stat string, so its dots are attached (G8)
    # and the op count carries the 건 counter the way ko.json writes counts.
    "account_net.detail_line": (
        u"%(from)s → %(to)s·%(class)s·%(amount)s·오퍼레이션 %(count)s건·%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s·%(class)s·%(amount)s·오퍼레이션 %(count)s건·%(kind)s"
    ),
    "account_net.es_bad_account": u"해당 이름은 이 체인의 계정이 아닙니다.",
    "account_net.es_disabled": (
        u"커뮤니티 인덱스가 꺼져 있습니다. 이 지도를 그리려면 설정에서 켜십시오."
    ),
    "account_net.es_unavailable": (
        u"지금은 커뮤니티 인덱스에 연결할 수 없습니다. 잠시 후 다시 시도하십시오."
    ),
    "account_net.go": u"네트워크 그리기",
    "account_net.idle": u"아직 아무것도 그리지 않았습니다.",
    "account_net.intro": (
        u"계정을 하나 이상 입력하면 누구에게 보내고, 누구에게 빌려주고, "
        u"누구에게서 빌리는지 알 수 있습니다. 커뮤니티 히스토리 인덱스에서 읽으며, "
        u"서명도 저장도 하지 않습니다."
    ),
    "account_net.kind_flow": u"자금 흐름",
    "account_net.kind_relation": u"관계",
    # The leading space is load-bearing: this fragment follows an amount.
    "account_net.more_assets": u" 외 %(n)s개",
    "account_net.need_class": u"선을 그리려면 연결 유형을 하나 이상 켜십시오.",
    "account_net.need_seeds": u"지도를 그리려면 계정을 하나 이상 입력하십시오.",
    "account_net.no_amount": u"금액 없음",
    # A "ring" is the BFS neighbour layer, so 이웃 names it plainly rather
    # than transliterating a word no Korean reader would know.
    "account_net.ring1_label": u"이웃 1",
    "account_net.ring2_label": u"이웃 2",
    "account_net.scanning": u"커뮤니티 인덱스를 읽는 중입니다…",
    "account_net.seeds_label": u"그릴 계정",
    "account_net.stale_settings": (
        u"깊이 또는 이웃 설정이 변경되었습니다 — “네트워크 그리기”를 누르십시오."
    ),
    "account_net.status_credit_index": (
        u"인덱스에서 %(n)s개의 신용 연결을 확인했습니다"
        u"(제안 또는 계약 객체가 체인에서 사라졌습니다)"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s개의 신용 연결을 건너뛰었습니다"
        u"(체인에서 제안 또는 계약을 찾지 못했습니다)"
    ),
    "account_net.status_depth": u"%(depth)s 지도",
    "account_net.status_edge_cap": u"상위 %(n)s개 연결 표시",
    "account_net.status_expanded": u"확장됨: %(names)s",
    "account_net.status_expansion_scanned": u"확장에서 인덱싱된 오퍼레이션 %(n)s건",
    "account_net.status_expansion_truncated": (
        u"확장 조회는 최신 오퍼레이션으로 제한됩니다"
    ),
    "account_net.status_graph": u"계정 %(nodes)s개·연결 %(edges)s개",
    "account_net.status_node_cap": u"상위 %(n)s개 거래 상대 표시",
    "account_net.status_scanned": (
        u"계정 %(n)s개에서 인덱싱된 오퍼레이션 %(scanned)s건"
    ),
    "account_net.status_self": u"자기 계정 이체 %(n)s건 건너뜀",
    "account_net.status_shape": u"읽을 수 없는 항목 %(n)s건 건너뜀",
    "account_net.status_truncated": u"계정당 최신 오퍼레이션 %(n)s건",
    "account_net.status_unexpanded": u"직접 거래 상대 %(n)s개는 확장되지 않음",
    "account_net.status_unknown": u"찾을 수 없음: %(names)s",
    "account_net.title": u"계정 네트워크",
    "account_net.twin_amount": u"금액",
    "account_net.twin_class": u"유형",
    "account_net.twin_count": u"오퍼레이션",
    "account_net.twin_depth": u"홉",
    "account_net.twin_empty": (
        u"조회한 인덱싱 오퍼레이션에는 이 계정들 사이의 연결이 없습니다."
    ),
    "account_net.twin_from": u"출발",
    "account_net.twin_relation": u"자금 흐름/관계",
    "account_net.twin_span": u"처음 → 마지막",
    "account_net.twin_summary": u"표 보기(접근 가능)",
    "account_net.twin_to": u"도착",

    # ============================================================== asset (38)
    "asset.cer_row": u"핵심 환율(CER)",
    "asset.committee_fed_note": (
        u"위원회 피드: 활성 상태인 모든 위원회 위원이 게시할 수 있습니다."
    ),
    "asset.feed_history_title": u"피드 내역",
    "asset.history_capped": u"상위 8명의 게시자를 표시합니다(속도를 위해 제한)…",
    "asset.history_days": u"기간",
    "asset.history_exchange": u"거래소와 풀을 불러오는 중입니다…",
    "asset.history_failed": u"피드 내역을 불러오지 못했습니다.",
    "asset.history_loading": u"피드 내역을 불러오는 중입니다…",
    "asset.history_pub": u"게시자 %(i)s/%(n)s…",
    "asset.invert_btn": u"반전",
    "asset.issue_memo_no_key": u"이 계정에 등록된 메모 키가 없습니다.",
    "asset.issue_memo_warning": (
        u"메모를 첨조하십시오 — 체인에 평문으로 저장됩니다."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"발행자는 조회 중인 계정(잠겨 있는 %(id)s, 잠금이 해제된 본인 계정)이 "
        u"기본값입니다 — 직접 관리하는 발행자를 입력하십시오. 계정 페이지에서 "
        u"열었다면 해당 계정 이름을 여기에 붙여넣으십시오."
    ),
    "asset.loading_producers": u"생산자를 불러오는 중입니다…",
    "asset.multisig_body": (
        u"이 자산에 둘 이상의 승인이 필요하면 직접 서명은 실패합니다 — 대신 "
        u"변경 사항을 제안하고 공동 소유자의 승인을 요청하십시오(op 23)."
    ),
    "asset.multisig_coowner_hint": (
        u"공동 소유자입니까? 제안 페이지에서 변경 사항을 제안하고 공동 소유자의 "
        u"승인을 요청하십시오(op 23)."
    ),
    "asset.multisig_open_proposals": u"제안 보기",
    "asset.multisig_open_txbuilder": u"트랜잭션 빌더 열기",
    "asset.multisig_title": u"발행자를 공유하고 있습니까? 제안하십시오",
    "asset.new_issuer_field": u"새 발행자",
    "asset.no_history": (
        u"이 기간에는 내역이 없습니다 — 게시자는 드물게 게시합니다. 90d를 "
        u"사용해 보십시오."
    ),
    "asset.no_producers": (
        u"아직 게시된 피드가 없습니다 — 생산자가 게시하면 여기에 표시됩니다."
    ),
    # Korean counts the other way round: "per BTS" is BTS당, not BTS 마당 per.
    "asset.orientation_note": u"%(b)s당 %(m)s",
    "asset.owner_key_note": u"자산 소유자의 활성 키가 필요합니다.",
    # 플롯 is market.plots_group's shipped word, so the button and its section
    # agree.
    "asset.plot_feeds": u"피드 플롯",
    "asset.producer_col": u"생산자",
    "asset.producers_failed": u"생산자를 불러오지 못했습니다.",
    "asset.producers_live_title": u"피드 생산자",
    "asset.producers_title": u"피드 생산자(op %(op)s)",
    "asset.publish_op19_title": u"피드 게시(op %(op)s)",
    "asset.published_col": u"게시 시각",
    # “조회 중” is the phrase barter.viewing_as and every *_viewing_as notice
    # already ships as …(으)로 보는 중; this reuses it so principle #9 reads
    # one way.
    "asset.viewing_notice": (
        u"%(name)s(%(id)s)(으)로 보는 중입니다 — 서명하려면 잠금을 해제하십시오."
    ),
    "asset.witness_fed_note": (
        u"증인 피드: 활성 상태인 모든 증인이 게시할 수 있습니다."
    ),

    # ============================================================ market (54)
    "market.adjust_button": u"조정",
    "market.confirm_adjust": u"조정 확인",
    # discrete_fills / discrete_swaps are unit suffixes the JS appends after a
    # number and a space, so they stay single words and take no article.
    "market.discrete_fills": u"체결",
    "market.discrete_no_fills": (
        u"체결이 아직 없습니다 — 주문을 내거나 다른 쌍을 시도하십시오."
    ),
    "market.discrete_swaps": u"스왑",
    "market.discrete_tip_account": u"계정",
    "market.discrete_tip_block": u"블록",
    "market.discrete_tip_order": u"주문",
    "market.discrete_tip_price": u"가격",
    "market.discrete_tip_time": u"시간",
    "market.discrete_tip_volume": u"거래량",
    "market.discrete_tip_volume_quote": u"거래량(상대)",
    "market.discrete_unavailable": u"이산 모드에서는 지표를 사용할 수 없습니다.",
    "market.discrete_volume": u"이산 거래량",
    "market.exchange_desk": u"거래 데스크",
    "market.fail_update": u"업데이트에 실패했습니다.",
    "market.flt_max_price": u"최대 가격",
    "market.flt_min_price": u"최소 가격",
    "market.loading_pool_map": u"지도를 불러오는 중입니다…",
    "market.map_aria": (
        u"시장 네트워크. 선은 최근 24시간 동안 체결된 시장입니다."
    ),
    "market.map_connects": (
        u"최근 24시간 동안 시장 거래가 있었던 경우 두 자산을 선으로 연결합니다."
    ),
    "market.map_connects_fallback": (
        u"자금이 예치된 풀이 있으면 두 자산을 선으로 연결합니다. 24시간 거래 "
        u"활동은 확인되지 않았습니다(내역 사용 불가) — 자금이 예치된 풀을 "
        u"표시합니다."
    ),
    "market.map_edge_fills": u"%(desk)s·%(a)s–%(b)s·%(fills)s건/24시간",
    "market.map_hops_empty": (
        u"이 구간 주변에서 최근 24시간 동안 체결된 시장이 없습니다."
    ),
    "market.map_hops_filtered": (
        u"선은 최근 24시간 동안 체결된 시장입니다. 전체 %(total)s개 쌍 중 "
        u"%(shown)s개를 표시합니다(24시간당 최소 %(min)s건 체결)."
    ),
    "market.map_hops_no_route": (
        u"체결된 시장을 거쳐 BTS로 가는 경로가 없습니다."
    ),
    "market.map_hops_note": (
        u"선은 최근 24시간 동안 체결된 시장입니다. %(pairs)s개 쌍을 표시합니다."
    ),
    "market.map_leg_ok": u"{s}는 BTS와 연결됩니다",
    "market.map_leg_orphan": u"경고: {s}에는 체결된 시장을 거치는 경로가 없습니다!",
    "market.min_fills": u"최소 체결 수",
    "market.no_filter_match": u"이 필터와 일치하는 체결이 없습니다.",
    "market.settle_first100": (
        u"상위 100건을 표시합니다(get_settle_orders 제한 100건)"
    ),
    "market.settle_no_cancel": (
        u"정산 주문은 취소할 수 없습니다 — 자산의 강제 정산 지연 기간 이후 정산 "
        u"시점에만 실행됩니다."
    ),
    "market.tf_discrete": u"이산",
    # The three trailing spaces are load-bearing: an input follows them.
    "market.update_amount": u"판매 수량(새 총량) ",
    "market.update_amount_change": u"수량 변경",
    "market.update_bad_amount": u"0보다 큰 수량을 입력하십시오.",
    "market.update_bad_expiry": u"미래의 만료 시각을 입력하십시오.",
    "market.update_bad_price": u"0보다 큰 가격을 입력하십시오.",
    "market.update_broadcasting": u"업데이트를 브로드캐스트하는 중입니다…",
    "market.update_done": u"주문이 업데이트되었습니다",
    "market.update_expiry": u"새 만료 시각 ",
    "market.update_expiry_change": u"만료 시각(기존 → 신규)",
    "market.update_no_change": (
        u"변경 사항이 없습니다 — 가격, 수량 또는 만료 시각을 편집하십시오."
    ),
    "market.update_price": u"새 가격 ",
    "market.update_price_change": u"가격(기존 → 신규)",
    "market.update_review": u"업데이트 검토",
    "market.update_title": u"주문 조정",

    # ======================================================= market_net (40)
    "market_net.asset_1_field": u"자산 1(어느 구간이든 가능)",
    "market_net.asset_2_field": u"자산 2(어느 구간이든 가능)",
    "market_net.band_title": u"시장 네트워크",
    "market_net.canvas_label": (
        u"시장 네트워크 지도. Enter 키를 누르면 시장이 열립니다."
    ),
    "market_net.clear_btn": u"지우기",
    # The short column heads reuse the stats-tab wording verbatim: 24시간 Δ is
    # market.chg_label and 거래량 is market.osc_group_label's noun, not a
    # shorter coinage.
    "market_net.col_change": u"24시간 Δ",
    "market_net.col_last": u"최근 체결가",
    "market_net.col_market": u"시장",
    "market_net.col_vol": u"24시간 거래량",
    "market_net.collapse": u"접기",
    "market_net.edge_card_fills": u"%(desk)s·%(a)s–%(b)s·%(fills)s건/24시간",
    "market_net.empty": u"이 필터와 일치하는 시장이 없습니다.",
    "market_net.expand": u"펼치기",
    "market_net.list_btn": u"시장 목록",
    "market_net.loading": u"시장을 불러오는 중입니다…",
    "market_net.map_empty": u"최근 거래량이 있는 시장이 없습니다.",
    "market_net.map_fallback": (
        u"쌍 %(pairs)s개·자산 %(assets)s개·24시간 체결 미확인"
    ),
    "market_net.map_hops_ready": (
        u"쌍 %(pairs)s개·자산 %(assets)s개·24시간 체결"
    ),
    "market_net.map_ready": u"시장 %(markets)s개·자산 %(assets)s개",
    "market_net.node_card": u"%(sym)s (%(id)s)·시장 %(n)s개",
    "market_net.offline": (
        u"네트워크를 사용할 수 없습니다 — 캐시된 시장을 표시합니다. 연결 후 다시 "
        u"시도하십시오."
    ),
    "market_net.open_desk": u"%(id)s 열기",
    "market_net.prompt": (
        u"노드를 탭하면 자산, 선을 탭하면 시장이 표시됩니다."
    ),
    "market_net.ramp": u"24시간 거래량: 낮음 → 높음",
    "market_net.ramp_fills": u"24시간 체결: 낮음 → 높음",
    "market_net.selector_title": u"시장 선택기",
    "market_net.spark_label": u"%(id)s의 7일 추이",
    "market_net.subtitle": (
        u"24시간 거래량 기준 주요 호가창 시장입니다. 행을 고르면 데스크가 열립니다."
    ),
    "market_net.title": u"시장",
    "market_net.top_note": (
        u"탐색한 %(probed)s개 중 상위 %(shown)s개 — 24시간 거래량 기준."
    ),
    "market_net.twin": u"시장 행(%(n)s)",
    "market_net.twin_more": (
        u"시장 %(n)s개 중 %(shown)s개를 표시합니다. 필터를 좁히면 더 적게 "
        u"표시됩니다."
    ),
    "market_net.verdict_full": u"시장 %(markets)s개·자산 %(assets)s개",
    "market_net.verdict_no_path": (
        u"%(a)s와 %(b)s 사이에 체결된 시장을 거치는 경로가 없습니다"
    ),
    "market_net.verdict_path": (
        u"%(a)s는 체결된 시장 %(n)s개를 거쳐 %(b)s에 도달합니다"
    ),
    "market_net.verdict_star": u"%(s)s와 연결된 시장: %(n)s개",
    "market_net.verdict_web": u"%(s)s에서 도달 가능한 시장: %(n)s개",

    # ========================================================== settings (43)
    # The node-table column heads. 위치 / 참여율 / 헤드 / 지연 reuse the
    # node-health wording ko.json's settings help already uses, and 핑 is
    # settings.probe_all's own word for the same probe.
    "settings.th_chain": u"체인",
    "settings.th_handshake": u"핸드셰이크",
    "settings.th_head": u"헤드",
    "settings.th_history": u"히스토리",
    "settings.th_location": u"위치 *",
    "settings.th_participation": u"참여율",
    "settings.th_ping": u"핑",
    "settings.th_provider": u"제공자 *",
    "settings.theme_title": u"테마",
    # The theme switcher shows three HUMAN names for three theme ids: the ids
    # (original-blue / light / dark) stay English in KEPT_ENGLISH because
    # stored prefs are keyed by them, but these three labels are prose.
    "settings.theme_classic": u"클래식",
    "settings.theme_dex_dark": u"DEX 다크",
    "settings.theme_vanilla_light": u"바닐라 라이트",
    "settings.language_title": u"언어",
    "settings.age_s": u"%(n)s초",
    # hist_yes / hist_no are keyed per BOOLEAN (settings-nodes.js histInfo), so
    # a bare 예 / 아니오 is safe; Korean has no letter case to shout in.
    "settings.hist_no": u"아니오",
    "settings.hist_yes": u"예",
    "settings.confirm_back": u"뒤로",
    "settings.confirm_remove_action": u"동작",
    "settings.confirm_remove_hide": (
        u"이 노드 숨기기(다시 추가할 때까지 숨겨진 상태로 유지)"
    ),
    "settings.confirm_remove_result": u"결과",
    "settings.confirm_remove_switch": u"사용 중인 노드가 %(node)s(으)로 전환됩니다",
    "settings.confirm_remove_title": u"노드를 제거할까요?",
    "settings.confirm_remove_unlist": u"내 목록에서 제거",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**“노드 찾기”는 GitHub에서 노드 목록을 검색한 뒤 발견한 노드를 "
        u"탐색합니다. GitHub과 탐색한 노드는 귀하의 네트워크 주소를 인식합니다. "
        u"결과는 검토용 후보이며 자동으로 추가되지 않습니다."
    ),
    "settings.geo_note": (
        u"*위치와 제공자 정보는 ipaddress.to(https, 키 불필요)에서 가져옵니다 — "
        u"요청할 때 귀하의 주소를 인식하며, 응답은 이 기기에 24시간 캐시됩니다."
    ),
    # Signing section. 확장 기능 is this batch's first spelling of that word
    # in ko.json; 승인은 the proposal wording already in use.
    "settings.sign_auto": u"자동(확장 기능이 있을 때)",
    "settings.sign_badge": u"확장 기능 서명이 활성화됨 — 자세한 내용은 “로그인” 참조",
    "settings.sign_badge_local": u"페이지 내 서명 — 자세한 내용은 “로그인” 참조",
    "settings.sign_browser": u"항상 이 페이지에서 서명",
    "settings.sign_ext": u"항상 확장 기능 사용",
    "settings.sign_ext_absent": (
        u"이 기기에서 확장 기능을 찾지 못했습니다 — 서명은 이 페이지 안에서 "
        u"이루어집니다."
    ),
    "settings.sign_ext_present": u"이 기기에서 확장 기능을 찾았습니다.",
    "settings.sign_guide": u"확장 기능 설치 방법",
    "settings.sign_mode_browser": u"서명은 이 페이지의 메모리 안에서 이루어집니다.",
    "settings.sign_mode_ext": u"서명은 확장 기능 창에서 승인합니다.",
    "settings.sign_mode_ext_page": (
        u"서명은 확장 기능 안에서만 이루어집니다 — 웹사이트와 분리됩니다."
    ),
    "settings.sign_revoke": u"취소",
    "settings.sign_sites": u"연결된 사이트",
    "settings.sign_sites_empty": (
        u"아직 승인한 사이트가 없습니다 — 승인하면 여기에 표시되며 사이트별로 "
        u"취소할 수 있습니다."
    ),
    # The trailing space on story_a is load-bearing: a URL follows it.
    "settings.sign_sites_story_a": u"예: 다음 사이트의 주사위 게임이 ",
    "settings.sign_sites_story_b": (
        u" 에 귀하의 계정으로 플레이할 권한을 요청합니다 — 승인하면 그 계정에만 "
        u"연결되어 여기에 표시됩니다. 서명은 매번 다시 확인을 요청합니다."
        u"(해당 링크는 어디로도 이동하지 않습니다 — 가상의 예시입니다.)"
    ),
    "settings.sign_title": u"서명",
    "settings.sign_warn": (
        u"이 페이지에서 실행되는 모든 스크립트는 잠금 해제 중 귀하의 키를 읽을 "
        u"수 있습니다 — 침해된 호스팅 사본까지 포함합니다. 확장 기능을 통해 서명하거나 "
        u"직접 관리하는 사본을 실행하십시오."
    ),
}

# Keys whose Korean value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from KO. Each one is asserted
# to still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Korean crypto UI keeps in Latin: HTLC, NFT, NFT
#     URI, MCR, PMA, UIA, and the indicator tickers BB / EMA / PSAR / SMA;
#   * network ids, theme ids and sentinels the brief pins: mainnet / testnet /
#     devnet, original-blue / light / dark, "wss://…", "…", "—", "7d";
#   * pure glue a table cell or edge card prints as data: "@ %(price)s",
#     "@ %(price)s · %(vol)s", "%(desk)s · %(a)s–%(b)s · %(vol)s",
#     "%(first)s → %(last)s" — the separator IS the content there, and
#     translating the space inside a glue string would change what the reader
#     sees, so it stays English;
#   * the seed placeholder, which is real account names plus a 1.2.x id and so
#     is DATA under rule 1.
KEPT_ENGLISH = {
    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    # ---- asset
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.nft_uri_field": u"NFT URI",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    # ---- market
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_empty": u"—",
    # ---- market_net
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    # ---- settings
    "settings.custom_placeholder": u"wss://…",
    "settings.dash": u"—",
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.pending": u"…",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",
}


if __name__ == "__main__":
    sys.exit(main())