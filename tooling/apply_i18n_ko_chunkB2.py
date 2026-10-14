#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ko chunk-B2: fill the explorer / seo / splash / about / shell / menu
sections — the surfaces a first-time visitor lands on.

Scope: exactly the six sections named by the brief (`explorer`, `seo`,
`splash`, `about`, `shell`, `menu`). `explorer`, `splash` and `about` were
carried by chunk A only partially, so what is left here is the residue every
one of those three pages still shows in English; `menu` and `shell` are the
two chrome sections no earlier chunk owned. Nothing outside the six is
touched: every key listed below is checked against en, and any other key is
REFUSED here as out of scope.

The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ko.json, or one whose English master moved, is REFUSED;
  * KO + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

This is the Korean sibling of tooling/apply_i18n_ko_chunkB1.py and keeps its
gates one for one, including the three that were INVERTED or RELAXED for
Korean there (G7, G8, G9) — inverting them silently would be the worst kind
of copy-paste bug.

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
                     G4b data carve-out proven, not trusted: every parenthesised
                     route, ?key=value deep link and 1.2.x object id in a value
                     this batch writes must survive byte-for-byte;
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
                     Cyrillic/Han/kana/other foreign letter, or an invisible
                     code point. ko.json already ships 3,637 translated strings
                     with ZERO apostrophes (it quotes with “”, the convention
                     its own explorer.unknown_tab_prefix already uses), and a
                     Cyrillic or Han letter in a Korean string is not a typo, it
                     is a different language. Hangul is what this file is FOR,
                     so it is of course allowed. This batch is the one that
                     meets the English masters full of possessives —
                     `the builders' replies` (about.making_body),
                     `Your keys`, `the asset's decimals` — and the only correct
                     Korean rendering of each is a rewrite of the clause, never
                     an apostrophe;
  G8  dot hygiene    INVERTED from the ja batch: Korean attaches the middle
                     dot, it does not float it. A dot with a space on either
                     side is a refusal; a dot glued to its neighbours is
                     correct, as is the algebraic x·y=k notation. The sweep runs
                     file-wide; a hit OUTSIDE the owned sections is reported as
                     PRE-EXISTING and does not gate this batch, because
                     repairing a neighbour here would be exactly the silent edit
                     the scope refusal forbids;
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                     LOAN below, or the write is refused. A Korean crypto UI
                     prints BTS, USD, HTLC, BitShares, React, JavaScript, the
                     repo and branch names it compares itself against, and a
                     screen width, in Latin exactly as a Japanese one prints
                     DEX and HTLC — a fake hangul spelling ("웹소켓", "미터")
                     would be worse than the loanword. Four shapes are DATA
                     under rule 1 and are stripped from the PROSE before the
                     sweep (LINK_TARGET a markdown href, ROUTE_INLINE a
                     parenthesised route, DEEP_LINK a ?key=value deep link,
                     CHAIN_ID an object id) — in this batch only
                     about.making_body comes near them, with `#3583` and the
                     dates the English quotes; G4/G4b is what makes the
                     carve-out checked rather than trusted.

Register: the 3,637 strings ko.json already ships are POLITE and split the way
Korean splits them — “~습니다” for statements ("자산을 불러오지 못했습니다.",
"잔액, 호가창, 연결 상태는 제자리에서 갱신됩니다.") and “~십시오” for
instructions addressed to the reader ("계정 이름을 입력하십시오.",
"시장을 선택하십시오."). This batch is polite too, and the SEO descriptions —
the one place in the app that is addressed to a stranger before they know the
product — keep the same split the page copy uses.

Labels, column heads, menu entries and section titles stay bare nouns
("표시 중", "익스플로러", "발견", "지갑"), which is how a table head and a menu
entry read in any register.

One-term-one-spelling across the dict (this is the load-bearing rule of the
batch, and every decision below was checked against the 3,637 shipped strings):
  * 메뉴 그룹 headings — `menu.section_*` uses the EXACT words chunk B1 wrote
    into the sitemap article: Discover = 발견, Labs = 랩, Personal = 개인. The
    burger menu and `#/help/sitemap` are two renderings of one grouping, and
    before this batch one of them was Korean and the other English;
  * 페이지 이름 — Cross Rates = 교차 환율, Account Network = 계정 네트워크,
    HTLC = HTLC (the loanword chunk B1 keeps in the sitemap too);
  * 탐색기 — 탐색기 is already the shipped word for explorer (explorer.title),
    so the SEO title follows it and the money screens use the page's own
    names (호가창, 유동성 풀);
  * showing-line — "Showing" is 표시 중 everywhere, which is what
    explorer.markets_showing already ships;
  * SmartCoin is 스마트코인 and User-Issued is 사용자 발행, both of them
    strings ko.json already ships;
  * the About prose reuses chunk B1's rendering of the build story WORD FOR
    WORD, because help.topic_about-making_body is the same paragraph with a
    pointer underneath and a divergent retelling would be visible on two pages.

Spacing: Korean writes real spaces between its words, so every space the
English master has is real grammar here and this batch invents none and
removes none. What it does NOT do is translate the space inside a GLUE
string — the trailing space on explorer.tx_prefix and shell.footer_* and the
` · ` in shell.footer_brand_vanilla's caller are layout, and the KEPT_ENGLISH
glue keys stay English because the separator IS their content.

Word order the code pins (worth stating, because it is the one place a naive
translation inverts): the shell footer appends the hyperlinked branch name
AFTER the relation fragment ("<rel> Master"), so a Korean fragment must not
carry a post-nominal that expects the noun to follow — the fragments end in a
colon ("다음과 동기화됨:", "%(n)s개 커밋 앞섬:") and read as a label. The
explorer count line concatenates `<shown> <of> <total>`, whose natural Korean
"총 N개 중 M개" is the other way round, so the connector is the same slash
explorer.markets_of already ships ("5 / 120") rather than a 中 that would
reverse into a wrong count.

Particles: the shipped strings already fixed the placeholder-particle problem
with the parenthesised dual forms — "%(name)s은(는)", "%(amount)s을(를)" — and
the universal ones where no form is needed ("의", "에게"). This batch reuses
exactly that convention rather than inventing one.

Quotation: “ ”, matching the ko strings that already quote (explorer.unknown_
tab_prefix, settings.sign_sites_story_a). about.no_assets_match quotes the
search term with them rather than the ASCII \" the English master uses.

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md 3.5) — and no prose number is invented. The dates
the About prose quotes (26 September 2026, 3 October), the issue number
(#3583), the feed scan cap (first 100 assets) and the two viewports (360px,
4K) are carried across as the same values, and about.dlg_bad_link's sibling
chain ids stay byte-verbatim.

Empty state: `—` is the shipped Korean empty-state marker, so splash.pulse_
stale ("— stale" → "— 오래됨") keeps its dash, exactly the way chunk A kept
market.stat_empty = "—" while translating the prose around it.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ko_chunkB2.py                # dry run (asserts)
  python3 tooling/apply_i18n_ko_chunkB2.py --apply        # writes ko.json
  python3 tooling/apply_i18n_ko_chunkB2.py --verify       # structural re-proof
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

# The sections this batch owns. Everything else belongs to another chunk and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "explorer", "seo", "splash", "about", "shell", "menu",
))
OWNED_SECTIONS = SECTIONS

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from KO below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live in another chunk's settings section; the shell brands live
# in a section this batch owns, and are kept in the list so a drift anywhere
# in the file is caught.
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
# G9 data carve-outs. Four shapes are DATA under rule 1 — translating or
# "declaring" one in LOAN would be the bug, not the fix — so they are removed
# from the PROSE before the loanword sweep:
#   LINK_TARGET  a markdown href           `[지갑](#/wallet)`
#   ROUTE_INLINE a parenthesised route     `소개 페이지(#/about)`
#   DEEP_LINK    a ?key=value deep link   `?dialog=N`
#   CHAIN_ID     an object id              `1.3.x`, `1.19.66`
# The link LABEL is never stripped: that is prose, and it is what this batch
# translates. G4b below is what makes the carve-out checked rather than trusted
# — LINK_HASH already covers the first shape, and ROUTE_INLINE / DEEP_LINK /
# CHAIN_ID are compared against the English master key by key.
LINK_TARGET = re.compile(r"\]\([^)]*\)")
ROUTE_INLINE = re.compile(r"\(#/[^)]*\)")
DEEP_LINK = re.compile(r"\?[A-Za-z][A-Za-z0-9]*=[A-Za-z0-9=_&#%\-]*")
CHAIN_ID = re.compile(r"\d+\.\d+\.[\dx]+")
INVISIBLE = re.compile(u"[­‍⁠﻿]")
DOT_CHARS = u"·•‧･"
APO_TYPO = u"’"
APO_ASCII = u"'"
IDEO_SPACE = u"　"
# G7: a letter from a script this file must never emit. Written as explicit
# \uXXXX escapes on purpose: typing these blocks by hand is exactly how a range
# silently swallows Hangul (U+AC00..U+D7A3) and the gate then fires on every
# Korean word in the file. The four Korean blocks below are deliberately
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
# U+A960..U+A97F, U+D7B0..U+D7FF and U+AC00..U+D7A3 (syllables). None of them is
# listed above, and that omission IS the exemption — a single mis-typed range
# end would swallow U+AC00..U+D7A3 and the gate would fire on every Korean word
# in the file, so the ranges stay as escapes a reader can audit.

# G9: a Latin run inside a Korean value. A token may continue through - _ . /
# so "Same-T", "docs/vanilla-ui-dialog.md" and "BTS/USD" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Korean BitShares UI prints in Latin, a platform/repo/branch name the
# reader has to recognise, a file name, or a screen unit; anything else has to
# be Korean.
LOAN = frozenset((
    # Brands / chain / asset symbols the brief pins. BTS/USD is the one market
    # the SEO market title names, and it is a single token to the sweep.
    "BTS", "BTS/USD", "BitShares", "USD",
    # The one chain acronym this batch's prose spells out: explorer
    # feed_cer_premium's row label (core exchange rate).
    "CER",
    # Platform name about.dlg_noscript tells the reader the archive needs.
    "JavaScript",
    # The reference repo and the framework the About build story says this
    # wallet walked away from — the two names a reader compares the page
    # against, and the two chunk B1 keeps in the same paragraph on /help.
    "bitshares-ui", "React",
    # The markdown file that holds the noscript copy of the build dialog, and
    # the viewports the About section claims to work from. A screen width is
    # written px in every Korean UI; there is no hangul spelling of a
    # resolution.
    "docs/vanilla-ui-dialog.md", "px", "4K",
    # The branch name the shell footer links after every relation fragment.
    "Master",
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
    """G1-G4, G4b, G7, G8 + punctuation hygiene for one key/value pair.

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
    # G4b: the G9 carve-outs, proven rather than trusted. Every parenthesised
    # route, every ?key=value deep link and every object id must survive byte-
    # verbatim, because they are data the reader types or compares — a Korean
    # rewrite of `(#/about)` or `1.3.x` would be a broken link and a wrong
    # lookup, while the markdown href above is only half of that story.
    for shape, rx in (("route", ROUTE_INLINE), ("deep link", DEEP_LINK),
                      ("object id", CHAIN_ID)):
        if rx.findall(master) != rx.findall(value):
            problems.append("%s changed: %s" % (shape, key))
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
        # Rule-1 data, all four shapes proven byte-verbatim by G4/G4b.
        for rx in (LINK_TARGET, ROUTE_INLINE, DEEP_LINK, CHAIN_ID):
            prose = rx.sub("", prose)
        # A count keeping its English unit suffix ("24h", "0-77") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # into "24시간" without changing the number the reader compares against
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
    # are printed loudly and never repaired here: another chunk owns them, and
    # an insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` — problems this batch can
    # answer for — gates the exit code.
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
        if k.split(".")[0] in OWNED_SECTIONS and d.get(k) == e[k]
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
        if key.split(".")[0] not in OWNED_SECTIONS:
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
        if key.split(".")[0] not in OWNED_SECTIONS:
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
        if k.split(".")[0] in OWNED_SECTIONS
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
    # separately forbids claiming its IDENTIFIERS list (shell.brand is one of
    # them, which is exactly why it is KEPT_ENGLISH rather than KO). Nothing
    # else in _meta moves - filling strings is not verification, so the
    # controller's v2 provenance/verified/high_risk fields stay untouched.
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

    print("ko chunk-B2: %d planned, %d differ from en, %d intentionally "
          "identical" % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(OWNED_SECTIONS):
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
    # ============================================================ explorer (11)
    # The asset-mode radios and the honest "Showing" line under the assets
    # table share assetModeLabel(), so these four are one decision: the mode
    # NAMES, which ko.json already ships as 스마트코인 and 사용자 발행 자산.
    "explorer.assets_mode_all": u"전체",
    "explorer.assets_mode_market": u"스마트코인",
    "explorer.assets_mode_prediction": u"예측",
    "explorer.assets_mode_user": u"사용자 발행",
    # The count line concatenates "<shown> <of> <total>", whose natural Korean
    # ("총 120개 중 5개") runs the other way. A 중 here would print "5 중 120",
    # which a reader parses backwards. So the connector is the slash
    # explorer.markets_of already ships in this very file: "5 / 120" reads as
    # the fraction it looks like, in both directions.
    "explorer.assets_of": u"/",
    # A row label in the feed detail: core exchange rate is the CER this label
    # names, so the acronym rides along in the parentheses the master gives it,
    # and "publisher-rule estimate" states WHO estimated the premium — a value
    # this wallet does not compute itself.
    "explorer.feed_cer_premium": u"핵심 환율(CER) 프리미엄(발행자 규칙 추정치)",
    # 표시 중 is the word explorer.markets_showing already ships for the same
    # English "Showing" in the same page family.
    "explorer.assets_showing": u"표시 중",
    # The feed scan disclosure reads "표시 중: 3 / 200개를 스캔했습니다(처음
    # 100개 자산)". 개를 is the bare counter the number before it needs, and
    # the cap stays the same 100 the code scanned, never a rounded Korean word.
    "explorer.feeds_scanned_suffix": u"개를 스캔했습니다(처음 100개 자산)",
    "explorer.feeds_of": u"/",
    "explorer.feeds_showing": u"표시 중",
    # A row LABEL, so no trailing period. The search term is quoted with the
    # “ ” ko.json already uses (explorer.unknown_tab_prefix), never the ASCII
    # \" the English master has: G7 forbids that apostrophe class outright.
    "explorer.no_assets_match": u"“%(q)s”와 일치하는 자산이 없습니다.",

    # ===================================================================== seo (26)
    # Meta descriptions: factual, short, and the one surface addressed to a
    # stranger before they know the product. “BitShares 지갑” is the product
    # name; the em dash and the second sentence come straight from the master.
    # Every title keeps the "— BitShares Wallet" tail the router.js table
    # splices between the page name and the brand.
    "seo.desc_about": (
        u"이 BitShares 지갑 소개 — 로컬 키, 가입 없음, 추적 없음. 자유롭게 "
        u"둘러보고 로컬에서 서명하십시오."
    ),
    "seo.desc_account": (
        u"이 BitShares 계정 보기 — 잔액, 주문, 이력을 체인에서 실시간으로 "
        u"읽습니다. 로그인은 필요 없습니다."
    ),
    "seo.desc_account_net": (
        u"계정이 누구에게 이체하고, 누구에게 빌려주고, 누구에게 빌리는지 "
        u"지도에서 확인하십시오 — 커뮤니티 인덱스에서 읽습니다. 로그인은 필요 "
        u"없습니다."
    ),
    "seo.desc_dashboard": (
        u"BitShares 대시보드 — 잔액, 시장, 체인 활동을 한눈에. 자유롭게 "
        u"둘러보십시오. 키는 기기에 남습니다."
    ),
    "seo.desc_explorer": (
        u"BitShares 블록, 트랜잭션, 자산 살펴보기 — 실시간 체인 데이터, "
        u"로그인 없이 볼 수 있습니다."
    ),
    "seo.desc_help": (
        u"BitShares 지갑 도움말 — 계정, 거래, 투표, 복구 안내. 막힐 때는 "
        u"여기서 시작하십시오."
    ),
    "seo.desc_login": (
        u"로컬 BitShares 지갑 잠금 해제 — 비밀번호, 브레인키 또는 가져온 "
        u"키. 키는 이 기기를 절대 떠나지 않습니다."
    ),
    "seo.desc_market": (
        u"BitShares 호가창에서 BTS를 USD와 거래 — 실시간 매수·매도 호가와 "
        u"이력, 기기에서 로컬 서명."
    ),
    # 24h becomes 24시간: the unit is prose here (no range control beside it to
    # compare against), and ko.json writes 시간 for every other duration.
    "seo.desc_markets": (
        u"BitShares 호가창 시장을 24시간 거래량으로 살펴보고 어느 쌍이든 "
        u"거래 데스크를 여십시오. 로그인은 필요 없습니다."
    ),
    "seo.desc_pools": (
        u"BitShares 유동성 풀 살펴보기 — 쌍, 잔액, 활동을 체인에서 실시간으로 "
        u"읽습니다. 로그인은 필요 없습니다."
    ),
    "seo.desc_transfer": (
        u"BitShares 자산을 어떤 계정으로든 보내십시오. 모든 필드를 확인한 뒤 "
        u"로컬에서 서명하십시오 — 키는 이 기기를 떠나지 않습니다."
    ),
    "seo.desc_voting": (
        u"BitShares 증인, 위원, 워커에 투표하십시오. 모든 투표는 기기에서 "
        u"로컬 서명됩니다."
    ),
    "seo.desc_xrates": (
        u"모든 풀 자산을 BTS 등으로 마지막 스왑 가격에 환산합니다. 로그인은 "
        u"필요 없습니다."
    ),
    "seo.title_about": u"소개 — BitShares 지갑",
    "seo.title_account": u"계정 %(name)s — BitShares 지갑",
    "seo.title_account_net": u"계정 네트워크 — BitShares 지갑",
    "seo.title_dashboard": u"대시보드 — BitShares 지갑",
    # 탐색기 is explorer.title's shipped Korean; the page itself is called
    # 익스플로러 in the menu, so the SEO title carries both words.
    "seo.title_explorer": u"블록체인 익스플로러 — BitShares 지갑",
    "seo.title_help": u"도움말 — BitShares 지갑",
    "seo.title_login": u"로그인 — BitShares 지갑",
    "seo.title_market": u"BTS/USD 거래소 — BitShares 지갑",
    "seo.title_markets": u"시장 — BitShares 지갑",
    "seo.title_pools": u"유동성 풀 — BitShares 지갑",
    "seo.title_transfer": u"자금 보내기 — BitShares 지갑",
    "seo.title_voting": u"증인 투표 — BitShares 지갑",
    # 교차 환율 is the exact word the sitemap article (chunk B1) writes for
    # this page, so the tab title and the menu card name one thing.
    "seo.title_xrates": u"교차 환율 — BitShares 지갑",

    # ================================================================ splash (20)
    "splash.card_dex_d": u"공개 시장에서 매수하고 매도합니다.",
    "splash.card_explore_d": u"블록과 계정 이력을 확인합니다.",
    "splash.card_pool_d": u"두 자산을 풀에 모으면 수익을 나눠받습니다.",
    "splash.card_wallet_d": u"키는 이 기기에만 보관합니다.",
    # The card strip's heading: an instruction, so ~십시오 like every other
    # heading in the step block (splash.steps_title ships 세 단계로 시작하기).
    "splash.cards_title": u"거래, 풀, 탐색 — 여기서 시작하십시오",
    # A button, so the 하다 form the other CTAs ship (about.cta_trade =
    # 거래소 열기, splash.final_cta = 지갑 만들기).
    "splash.cta_exchange": u"거래소에서 거래하기",
    # Reuses about.hero_title's shipped opening (브라우저 속 BitShares) with
    # the 지갑 this page is about, so the two heroes read as one sentence.
    "splash.hero_title": u"브라우저 속 BitShares 지갑 — 설치할 것이 없습니다.",
    "splash.hero_sub": u"당신의 키. 당신의 자금, 온체인에.",
    "splash.hero_sub2": u"시장은 무료로 둘러보십시오. 서명할 때만 잠금을 해제하십시오.",
    # 오래됨 is explorer.state_stale's shipped word for "stale"; the — in front
    # of it is the shipped Korean empty-state marker and stays.
    "splash.pulse_stale": u"— 오래됨",
    # 헤드 블록 is splash.pulse_head's shipped word; 시각 is the time noun the
    # pulse band shows the block time in.
    "splash.pulse_time": u"헤드 블록 시각",
    "splash.pulse_title": u"실시간 체인 숫자",
    "splash.step1_d": u"로그인은 필요 없습니다 — 먼저 체인을 둘러보십시오.",
    "splash.step1_t": u"둘러보기",
    "splash.step2_d": u"브레인키가 이 기기에서 생성됩니다. 종이에 적어 두십시오.",
    "splash.step2_t": u"지갑 만들기",
    "splash.step3_d": u"호가 주문, 유동성 풀, 투표 — 모두 온체인에서.",
    "splash.step3_t": u"거래 / 풀 / 투표",
    # The arrow keeps the master's own path shape (설정 → 노드), and 설정 is
    # the shipped Korean for the settings page.
    "splash.topvol_unavailable": (
        u"상위 시장 거래량을 가져올 수 없습니다 — 설정 → 노드를 확인하십시오."
    ),
    "splash.trust_keys_d": (
        u"서명은 기기에서 로컬로 이루어집니다. 어떤 서버도 비밀번호나 키를 "
        u"보지 못합니다."
    ),

    # ================================================================== about (18)
    # The build-dialog <details>: one exchange per prompt/reply pair, filtered
    # and counted. Answers are 기록 and filters are 지우기 — the two words
    # ko.json already ships for those widgets (about.dlg_no_match, pool.clear_btn).
    "about.dlg_heading": u"전체 제작 대화",
    "about.dlg_heading_c": u"전체 제작 대화 (%(total)s)",
    "about.dlg_no_reply": u"답변 기록이 없습니다 — 다음 요청이 바로 이어졌습니다.",
    "about.dlg_noscript": (
        u"이 기록에는 JavaScript가 필요합니다. 같은 글은 소스 저장소의 "
        u"docs/vanilla-ui-dialog.md에 있습니다."
    ),
    "about.dlg_search_clear": u"지우기",
    "about.dlg_search_ph": u"교환 필터링…",
    "about.dlg_showing": u"표시 중",
    "about.dlg_showing_c": u"표시 중 %(shown)s / %(total)s",
    "about.dlg_unavailable": u"제작 대화 기록을 사용할 수 없습니다.",
    "about.hero_lede": (
        u"BitShares 체인을 위한 지갑 — 시장, 계정, 거버넌스, 탐색 — 이 일반 "
        u"웹 파일로 실행됩니다. 프레임워크도, 설치 프로그램도, 우리 쪽 계정도 "
        u"없습니다. 당신의 키는 이 브라우저를 떠나지 않습니다."
    ),
    # The build story, one paragraph. WORD FOR WORD chunk B1's rendering of the
    # same two sentences in help.topic_about-making_body (joined, because this
    # page's master has no paragraph break): the builders' apostrophe becomes
    # a clause (G7), the quoted prompt keeps ko.json's “” quoting, and the
    # repo, the framework and the issue number stay byte-verbatim.
    "about.making_body": (
        u"다음은 이 지갑을 만든 최초의 제작 과정입니다. 2026년 9월 26일의 "
        u"“bitshares-ui 인수” 요청부터 10월 3일의 이슈 1 수정까지, 이 지갑을 "
        u"만든 모든 요청과 제작자의 답변을 편집 없이 그대로 옮겼습니다. 이 글은 "
        u"이 지갑이 서 있는 결정을 기록합니다. 이슈 #3583의 천 시간 함정 뒤에 "
        u"또 다른 React 승격 작업을 포기한 것, 그래서 이 지갑은 릴리스 주기가 "
        u"있는 어떤 것에도 의존하지 않는 것. 서명을 외부에 맡기지 않고 옛 지갑처럼 "
        u"모든 트랜잭션을 로컬에서 하는 것. 클래식 모양을 기본으로 한 세 가지 "
        u"테마. 원시 체인 정수를 절대 보여주지 않고 사람이 읽는 단위로 표시하는 "
        u"숫자. 첫 슬라이스부터 휴대전화 우선 레이아웃을 쓰는 것. 그리고 추정이 "
        u"아니라 살아 있는 체인에서 읽는 수수료. 역사로 읽으십시오. 이것이 지갑이 "
        u"만들어진 방식입니다."
    ),
    # 이 지갑의 제작 과정 is help.topic_about-making_title's shipped heading.
    "about.making_title": u"이 지갑의 제작 과정",
    # s2_title pairs with s2_body, which ships 거래할 수 있는 실제 호가창.
    "about.s2_title": u"실제 호가창에서 거래",
    "about.s3_body": (
        u"이 지갑이 대체하는 그 지갑은 백 개의 낡은 패키지와 아무도 재현할 수 "
        u"없는 툴체인 무게에 죽었습니다. 릴리스 주기 의존을 피하려고 만들었습니다: "
        u"프레임워크도, 패키지 관리자도, 빌드 단계도 없이 — 십 년 뒤에도 "
        u"브라우저에서 실행될 수 있는 가장 작은 것."
    ),
    "about.s3_title": u"업데이트 없이 수년 동안 동작",
    "about.s4_body": (
        u"돌아오는 사용자는 곧바로 익숙한 자리를 찾습니다 — 클래식 지갑과 같은 "
        u"페이지, 패널, 말 — 그 한편 잔액, 호가창, 연결 상태는 제자리에서 "
        u"실시간으로 갱신됩니다. 시장, 계정, 자산을 관대하게 찾아주는 검색, 세 "
        u"가지 테마, 그리고 360px 휴대전화에서 4K 트레이딩 데스크까지 동작하는 "
        u"레이아웃."
    ),
    "about.s4_title": u"같은 페이지, 실시간 갱신",
    # "the asset's decimals" becomes a clause — the possessive never survives
    # into Korean here (G7), and 관대하게 is the shipped adverb of the search
    # promise this section makes.
    "about.s5_body": (
        u"체인은 정수로 말하고 당신은 그것을 결코 보지 않습니다. 모든 금액은 그 "
        u"자산의 소수 자리에, 모든 퍼센트는 그대로의 값에, 모든 수수료는 서명 "
        u"전에 살아 있는 체인에서 읽습니다."
    ),

    # ================================================================= shell (10)
    # The footer-left build line renders "<brand> · <rel> Master", with the
    # hyperlinked branch name appended AFTER the relation fragment. A Korean
    # fragment therefore must not end in a post-nominal that expects the noun
    # to follow it ("Master와" would arrive before the noun), so each fragment
    # closes with a colon and reads as the label it is.
    "shell.footer_ahead": u"%(n)s개 커밋 앞섬:",
    "shell.footer_ahead_one": u"1개 커밋 앞섬:",
    "shell.footer_at_build": u"빌드 시점 %(date)s",
    "shell.footer_behind": u"%(n)s개 커밋 뒤처짐:",
    "shell.footer_behind_one": u"1개 커밋 뒤처짐:",
    "shell.footer_dahead": u"%(n)s개 앞섬",
    "shell.footer_dbehind": u"%(n)s개 뒤처짐",
    # "diverged from (<ahead>, <behind>)" — the counts live in parentheses the
    # caller adds, so this half stays a bare predicate.
    "shell.footer_diverged": u"분기됨 —",
    "shell.footer_offbranch": u"Master 브랜치 위가 아닙니다",
    "shell.footer_sync": u"다음과 동기화됨:",

    # ================================================================== menu (9)
    # Section group headings. These three are the burger-menu twins of the
    # sitemap article's own groupings (chunk B1): 발견 / 랩 / 개인. Before
    # this batch the article was Korean and the menu was English, so the same
    # seven groupings had two names. Same words, both places.
    "menu.section_explore": u"발견",
    "menu.section_labs": u"랩",
    "menu.section_personal": u"개인",
    "menu.blurb_labs": u"체인과 노드 작업을 위한 강력한 도구.",
    "menu.blurb_personal": u"채팅, 알림, 그리고 내 설정.",
    # A bare tag, not a sentence: the master is a two-word noun phrase and
    # the other menu cards that are noun phrases stay noun phrases in Korean.
    "menu.d_account_net": u"이체 추적",
    "menu.d_xrates": u"BTS와 그 밖의 모든 자산에 대한 풀 가격을 보여줍니다.",
    # 계정 네트워크 and 교차 환율 are the sitemap's words for these two pages.
    "menu.p_account_net": u"계정 네트워크",
    "menu.p_xrates": u"교차 환율",
}

# Keys whose Korean value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from KO. Each one is asserted
# to still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * brands and the branch name the footer links (shell.*): a brand has no
#     hangul spelling, and check_i18n.py lists shell.brand in IDENTIFIERS —
#     claiming it in _meta.translated would be the false claim that gate exists
#     to catch;
#   * the network · host glue the footer-right prints as DATA ("%(net)s -
#     %(host)s"), where the separator IS the content;
#   * explorer acronyms (MCR / MSSR, MSSR) and the two keys that print a raw
#     chain FIELD NAME (mcr %(mcr)s; mssr %(mssr)s) or a publisher/time pair
#     (%(id)s @ %(ts)s) — a Korean rewrite of a field name is a wrong lookup,
#     not a translation;
#   * explorer.id_row / th_mssr: the shipped Korean writes ID (pool.id_col) and
#     keeps MSSR next to it;
#   * explorer.tx_prefix: "Tx " is a compact link prefix with a layout space —
#     the fuller 트랜잭션 is already shipped as explorer.tx_title_prefix, and a
#     longer word here would break the dense block line it sits in;
#   * menu.p_htlc: HTLC is the loanword chunk B1 keeps in the same sitemap.
KEPT_ENGLISH = {
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    # ---- explorer
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.th_mssr": u"MSSR",
    "explorer.tx_prefix": u"Tx ",
    # ---- menu
    "menu.p_htlc": u"HTLC",
}


if __name__ == "__main__":
    sys.exit(main())