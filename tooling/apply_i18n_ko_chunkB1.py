#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ko chunk-B1: fill the help / pool / pool_net sections, plus the
HONESTY SURFACE ko.json still leaves in English.

Scope: the three sections named by the brief (`help`, `pool`, `pool_net`) and
the `i18n` section, which IS the honesty surface: those seven keys are the
machine-translation warning itself (the header chip, the asterisk's own labels)
and the article they point at lives in `help`. They are carried here because a
Korean-only reader must be able to read the warning in Korean — a
machine-translation notice they cannot read is not a warning. Everything else
belongs to another chunk and is REFUSED here as out of scope.

The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ko.json, or one whose English master moved, is REFUSED;
  * KO + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

This is the Korean sibling of tooling/apply_i18n_ko_chunkA.py and keeps its
gates one for one, with three of them INVERTED or RELAXED for Korean (G7, G8,
G9 below) — inverting them silently would be the worst kind of copy-paste bug.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                     network/theme/dash/placeholder tokens stay byte-verbatim
                     (the same list tooling/check_i18n.py checks), plus the
                     honesty chip `i18n` itself;
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
                     FOR, so it is of course allowed. This matters here more
                     than in chunk A: the English masters of the help articles
                     are full of possessives (`the asset's precision`,
                     `your browser's local vault`, `the builders' replies`),
                     and the only correct Korean rendering is a rewrite of the
                     clause — never an apostrophe.
  G8  dot hygiene    INVERTED from the ja batch: Korean attaches the middle
                     dot, it does not float it. A dot with a space on either
                     side is a refusal; a dot glued to its neighbours is
                     correct, as is the algebraic x·y=k notation. ko.json's own
                     translated prose already writes it that way
                     ("계정을 등록·추천한 주체", "동기화·브로드캐스트되지"),
                     and the spaced “ · ” forms that survive in ko.json all
                     live in KEPT_ENGLISH glue strings or in other batches'
                     keys. The sweep runs file-wide; a hit OUTSIDE the owned
                     sections is reported as PRE-EXISTING and does not gate
                     this batch, because repairing a neighbour here would be
                     exactly the silent edit the scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                     LOAN below, or the write is refused. A Korean crypto UI
                     prints HTLC, DEX, BitShares, BTS, LP, Memo, Smartcoin and
                     the platform names a browser-compat article has to name
                     (WebSocket, WebCrypto, BigInt) in Latin exactly as a
                     Japanese one prints DEX and HTLC — a fake hangul spelling
                     ("웹소켓") would be worse than the loanword. One RELAXATION
                     is deliberate and batch-specific: the href half of a
                     markdown link is stripped before the sweep, because in the
                     sitemap it is a route (`#/account/committee-account`,
                     `#/market/BTS_USD`), which rule 1 calls DATA and which G4
                     has already proven byte-verbatim against en. Without the
                     relaxation the sitemap would need twenty
                     route-shaped entries in LOAN and the list would stop
                     being a judgement and start being a copy of the hashes.
                     The link LABEL is still swept: that is prose, and it is
                     what this batch translates.

Register: the 3,167 strings ko.json already ships are POLITE and split the way
Korean splits them — “~습니다” for statements ("잔액을 불러오지 못했습니다.",
"여기에 표시됩니다.") and “~십시오” for instructions addressed to the reader
("계정 이름을 입력하십시오.", "시장을 선택하십시오."). This batch is polite too.
Labels, column heads and link labels stay bare nouns ("잔액", "풀", "지갑"),
which is how a table head and a menu entry read in any register.

Spacing: this is the one place Korean is NOT like Japanese. Korean writes real
spaces between its words, so every space the English master has is real
grammar here and this batch invents none and removes none. What it does NOT do
is translate the space inside a GLUE string — the trailing spaces on
pool.swap_preview and the leading ones on pool.my_swaps_hint / pool.swaps_hint
are layout, and the two middle-dot edge cards in KEPT_ENGLISH stay English
because their separator IS their content.

Particles: the shipped strings already fixed the placeholder-particle problem
with the parenthesised dual forms — "%(name)s은(는)", "%(amount)s을(를)",
"%(name)s(으)로", "%(a)s이(가)" — and the universal ones where no form is needed
("의", "에게", "에게서"). This batch reuses exactly that convention rather than
inventing one.

Quotation: “ ”, matching the ko strings that already quote (uri.error_*,
proposal, settings.sign_sites_story_a). The English masters of
help.topic_about-making_body carry `the builders' replies` and the two
double-quoted section names; the apostrophe becomes a rewrite and the quotes
become “”.

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md 3.5) — and no prose number is invented. Dates and
counts the English quotes (26 September 2026, 3 October, 3, 6, 29) are carried
across as the same values in Korean order, and the chain ids the help text
quotes (1.2.x, 1.3.x, 1.19.x, 0-77) stay byte-verbatim.

Empty state: `—` is the shipped Korean empty-state marker, so the two
"Quote (preview): —" / "Market fee (preview): —" rows keep it while their label
is translated, exactly the way chunk A kept `market.stat_empty` = "—" while
translating the prose around it.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ko_chunkB1.py                # dry run (asserts)
  python3 tooling/apply_i18n_ko_chunkB1.py --apply        # writes ko.json
  python3 tooling/apply_i18n_ko_chunkB1.py --verify       # structural re-proof
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
SECTIONS = frozenset(("help", "pool", "pool_net"))

# The honesty surface. Its own `i18n` section in ko.json, seven keys, and every
# one of them is part of the machine-translation warning the `help` article
# explains — so it is owned here rather than left to whichever chunk reaches
# `i18n` last (see the scope note above).
HONESTY_SECTION = "i18n"
OWNED_SECTIONS = SECTIONS | {HONESTY_SECTION}

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from KO below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live in another chunk's settings section; the shell brands and
# the honesty chip live outside every section this batch owns, and are kept in
# the list so a drift anywhere in the file is caught.
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
    "i18n.badge_chip",
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
# Without these the sitemap would need twenty route-shaped LOAN entries and the
# loan list would stop being a judgement and start being a copy of the hashes.
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
# so "Same-T", "index.html", "WebCrypto" and "?dialog=N" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Korean crypto UI prints in Latin, a platform/API/route name the reader
# has to recognise, a file name, or a keyboard key; anything else has to be
# Korean.
LOAN = frozenset((
    # Brands / chain / asset symbols the brief pins.
    "BTS", "BitShares",
    # Operation and protocol acronyms a Korean BitShares UI keeps in Latin.
    "HTLC",
    # Feature names Korean crypto UIs loan rather than translate. LP comes from
    # the pool desk's own shipped strings (pool.shares_field = "LP 지분").
    "Brainkey", "LP", "Memo", "Proxy", "Smartcoin", "Swap",
    # Lab names: ko.json already ships menu.p_apilab = "API 랩" and
    # menu.p_eslab = "ES 랩", so the sitemap and the help titles reuse them.
    "API", "ES",
    # Same-T fund family name (the sitemap links the Same-T Funds page).
    "Same-T",
    # Route/deep-link names the reader types: the reference repo this wallet was
    # built from, and the framework the build story says it walked away from.
    "bitshares-ui", "index.html", "React",
    # Platform features the browser-support article names (it is ABOUT them),
    # plus the LAN the same article names as the insecure-context example.
    "BigInt", "LAN", "WebCrypto", "WebSocket",
    # The object id, lower-case: help.topic_glossary_body already ships
    # "1.2.0 같은 id를 가진 객체", so the honesty article reuses that spelling
    # rather than coinning a second one for the same word.
    "id",
    # Identifiers, keys and hosts a reader types or recognises.
    "Enter", "GitHub",
    # Schemes the same article tells the reader to serve the folder with, plus
    # the dev host that makes an insecure context go away.
    "http", "https", "localhost",
    # The reference wallet's key file, named in the backups article.
    "bin",
    # The object id, as the sitemap's last line calls it (ko.json writes ID in
    # pool.id_col, so the article uses the same capitalisation).
    "ID",
    # Identifiers, keys and hosts a reader types or recognises.
    "Enter", "GitHub",
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

    print("ko chunk-B1: %d planned, %d differ from en, %d intentionally "
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
    # ============================================================== help (40)
    # The honesty table cells. They are painted as table CELLS and as the
    # second line of a phone card, never composed into a sentence, so they are
    # bare labels — and the article prose below uses the same three adjectives
    # in the same order, so a reader who lands on the table and a reader who
    # lands on the prose are reading the same word for the same rating.
    "help.confidence_good": u"양호",
    "help.confidence_high": u"높음",
    "help.confidence_language": u"언어",
    "help.confidence_level": u"신뢰도",
    "help.confidence_moderate": u"보통 — 확인하십시오",
    "help.translation_confidence_heading": u"언어별 신뢰도",
    "help.report_translation_link": u"GitHub에서 번역 문제 신고",
    "help.about_link": u"이 지갑 소개",
    # aria-label for the sitemap's section filter; 메뉴.filter is the visible
    # "페이지 필터", and menu.intro already ships 섹션 for the grouping word.
    "help.sitemap_sections": u"섹션",
    # Section head + note for the community-index block. The community index is
    # help.topic_history-index_title's shipped word, so the article and this
    # header say one thing.
    "help.elastic": u"커뮤니티 인덱스(제3자 히스토리)",

    # ---- short help chrome ---------------------------------------------
    "help.topic_api-lab_title": u"API 랩",
    "help.topic_es-lab_title": u"ES 랩",
    "help.topic_community_title": u"커뮤니티",
    "help.topic_community_text": (
        u"BitShares를 둘러싼 채팅, 포럼, 익스플로러 및 코드를 확인합니다."
    ),
    "help.topic_community_body": (
        u"# 커뮤니티\n"
        u"BitShares를 둘러싼 사람과 장소 — 홈페이지, 코드, 익스플로러, 포럼 및 "
        u"채팅 — 는 커뮤니티 페이지에 있습니다."
    ),
    "help.topic_menu_title": u"사이트 메뉴",
    "help.topic_menu_text": (
        u"이 지갑의 모든 페이지를 탐색 메뉴와 같은 방식으로 묶었습니다."
    ),
    "help.topic_menu_body": (
        u"# 사이트 메뉴\n"
        u"메뉴 페이지는 이 지갑의 모든 화면을 섹션별로 나열하므로, 어느 데스크든 "
        u"한 번의 탭으로 갈 수 있습니다."
    ),
    "help.topic_sitemap_title": u"사이트맵",
    "help.topic_sitemap_text": (
        u"이 지갑의 모든 페이지를 한 장에 모았습니다: 메뉴 페이지와 메뉴 카드가 "
        u"없는 흐름 및 상세 보기입니다."
    ),
    # The 83-line sitemap. Every link LABEL is translated with the exact word
    # menu.p_* already ships for that page (so the burger menu and this article
    # read identically), and every hash stays byte-verbatim (G4). Korean fills
    # the space the English's " · " never had — the list IS the separator.
    "help.topic_sitemap_body": (
        u"이 지갑의 모든 페이지를 버거 메뉴와 같은 방식으로 묶었습니다. 링크가 "
        u"있는 항목은 바로 열리고, 메뉴 카드 없이 나열된 상세 보기는 상위 "
        u"페이지에서 열립니다.\n"
        u"# 지갑\n"
        u"- [대시보드](#/)\n"
        u"- [나의 계정](#/account/me)\n"
        u"- [계정](#/accounts)\n"
        u"- [이체](#/transfer)\n"
        u"- [청구서](#/invoice)\n"
        u"- [베스팅](#/vesting)\n"
        u"- [지갑](#/wallet)\n"
        u"- [지갑 비밀번호 변경](#/wallet/password)\n"
        u"- [지갑 생성(브레인키)](#/create-wallet-brainkey)\n"
        u"- [기존 계정 가져오기](#/existing-account)\n"
        u"- [새 계정 등록](#/create-account)\n"
        u"- [로그인](#/login)\n"
        u"- [등록](#/registration)\n"
        u"- [추천](#/referrals)\n"
        u"# 거래\n"
        u"- [거래소](#/markets)\n"
        u"- [간편 거래](#/instant-trade)\n"
        u"- [유동성 풀](#/pools)\n"
        u"- [교차 환율](#/cross-rates)\n"
        u"- [대출](#/borrow)\n"
        u"- [물물교환](#/barter)\n"
        u"- [입금 / 출금](#/deposit-withdraw)\n"
        u"- [Same-T 펀드](#/samet)\n"
        u"- [스포트라이트](#/spotlight)\n"
        u"# 수익 및 보호\n"
        u"- [신용 제안](#/credit-offer)\n"
        u"- [자동이체](#/direct-debit)\n"
        u"- [HTLC](#/htlc)\n"
        u"- [티켓](#/tickets)\n"
        u"- [에어드롭](#/airdrop)\n"
        u"- [사용자 정의 권한](#/authorities)\n"
        u"- [계정 목록](#/lists)\n"
        u"# 거버넌스\n"
        u"- [투표](#/voting)\n"
        u"- [제안](#/proposals)\n"
        u"- [워커 생성](#/create-worker)\n"
        u"- [예측 시장](#/prediction)\n"
        u"# 발견\n"
        u"- [익스플로러](#/explorer)\n"
        u"- [자산](#/assets)\n"
        u"- [자산 생성](#/assets/create)\n"
        u"- [자산 발행](#/assets/issue)\n"
        u"- [피드 게시](#/assets/feed)\n"
        u"- [네트워크 수수료](#/explorer/fees)\n"
        u"- [오퍼레이션](#/ops)\n"
        u"- [상위 오퍼레이션](#/top-ops)\n"
        u"- [뉴스](#/news)\n"
        u"# 익스플로러\n"
        u"- [익스플로러(블록체인)](#/explorer)\n"
        u"- [자산](#/explorer/assets)\n"
        u"- [풀](#/explorer/pools)\n"
        u"- [계정](#/explorer/accounts)\n"
        u"- [증인](#/explorer/witnesses)\n"
        u"- [위원회](#/explorer/committee)\n"
        u"- [시장](#/explorer/markets)\n"
        u"- [수수료](#/explorer/fees)\n"
        u"- [피드](#/explorer/feeds)\n"
        u"# 랩\n"
        u"- [API 랩](#/api-lab)\n"
        u"- [ES 랩](#/es-lab)\n"
        u"- [트랜잭션 빌더](#/txbuilder)\n"
        u"- [계정 네트워크](#/account-network)\n"
        u"# 개인\n"
        u"- [트롤박스](#/trollbox)\n"
        u"- [즐겨찾기](#/favourites)\n"
        u"- [가격 알림](#/alerts)\n"
        u"- [도움말](#/help)\n"
        u"- [번역의 한계](#/help/translation-limitations)\n"
        u"- [소개](#/about)\n"
        u"- [커뮤니티](#/community)\n"
        u"- [설정](#/settings)\n"
        u"# 메뉴 카드가 없는 페이지\n"
        u"등록 방식의 변형, 계정 및 시장 데스크, 상세 보기는 위의 페이지나 지갑 "
        u"안의 다른 링크에서 열립니다.\n"
        u"- [로컬 등록](#/registration/local)\n"
        u"- [클라우드 등록](#/registration/cloud)\n"
        u"- [예시 계정 페이지](#/account/committee-account)\n"
        u"- [예시 시장 데스크](#/market/BTS_USD)\n"
        u"- [예시 자산 페이지](#/asset/BTS)\n"
        u"- [예시 풀 데스크](#/pools/1.19.66)\n"
        u"- [메뉴 개요](#/menu)\n"
        u"특정 신용 제안, 계약, 제안안, 블록, 트랜잭션, HTLC, 예측 시장, 이체 "
        u"수신자, 청구서, 게이트웨이, 설정 탭, 익스플로러 탭 또는 도움말 문서의 "
        u"상세 보기는 상위 페이지에서 열리며, 주소에 ID 또는 이름을 받습니다."
    ),

    # ---- the honesty article itself ------------------------------------
    # The machine-translation warning, in Korean. Blank-line paragraph breaks
    # are structural: paintBody() splits the body on /\n\s*\n/ and paintBlock()
    # re-reads the `# ` and `- ` prefixes, so the 22 newlines are load-bearing
    # and G4 measures them against the English master.
    "help.topic_translation-limitations_title": u"번역의 한계",
    "help.topic_translation-limitations_text": (
        u"기계로 채운 번역은 표시되며 영어 원문은 언제나 한 번의 탭으로 볼 수 "
        u"있습니다. 문구를 고쳐 주십시오."
    ),
    "help.topic_translation-limitations_body": (
        u"기계로 채워진 것으로 표시된 번역은 기계가 쓴 것입니다. 그것이 영어와 "
        u"같은 내용을 말하는지 읽어 본 사람은 아무도 없습니다 — 그래서 영어 "
        u"이외의 모든 언어는 이 지갑의 헤더에 표시 칩이 붙습니다. 영어는 다른 "
        u"언어가 번역된 기준이므로 표시가 없습니다.\n"
        u"\n"
        u"# 줄에 붙은 *가 뜻하는 것\n"
        u"서명 줄에 붙은 *는 두 가지를 동시에 뜻합니다. 그 문구를 기계가 "
        u"채웠다는 뜻이고, 원래 영어가 한 번의 탭으로 보인다는 뜻입니다. *를 "
        u"누르면 영어가 이 지갑의 영어 원문이 저장한 그대로 그 줄 아래에 "
        u"나타납니다 — 다른 모든 언어가 번역된 바로 그 본문이지, 그것을 의역한 "
        u"것이 아닙니다.\n"
        u"\n"
        u"표시는 줄에 붙습니다. 줄 안의 단어에 붙는 것이 아닙니다. *는 번역된 "
        u"한 줄 전체를 표시하며, 그 줄들을 지갑이 고정된 규칙으로 고릅니다. "
        u"서명·비가역 작업·복구 화면의 모든 줄 — 긴 문단은 이 문서에서 설명하므로 "
        u"길이 상한이 있습니다 — 여기에 영어가 위험 문구를 담은 줄을 어디서든 "
        u"더한 것입니다. 그래서 id나 금액만 적은 줄에도 표시가 붙습니다(이체의 "
        u"수신자 필드 같은 경우), 반대로 id를 언급한 긴 문단에는 붙지 않습니다. "
        u"체인의 값 그 자체 — 셀의 금액, 열의 id, 자산 심볼 — 는 번역된 줄이 "
        u"아니므로 표시가 전혀 붙지 않습니다. 비교할 영어 문구가 없기 "
        u"때문입니다.\n"
        u"\n"
        u"# 신뢰도 등급이 뜻하는 것\n"
        u"이 지갑이 제공하는 모든 언어에는 아래 표에 적힌 등급이 하나씩 "
        u"있습니다. 높음은 그 문구가 영어에 가깝게 밀착되어 자연스럽게 "
        u"읽힌다는 뜻입니다. 양호는 쓸 수 있지만 어떤 표현은 여전히 어색할 수 있다는 "
        u"뜻입니다. 보통은 초안으로 읽고 믿기 전에 영어를 확인하라는 "
        u"뜻입니다.\n"
        u"\n"
        u"아래의 모든 등급은 그 문구를 쓴 기계가 자기 일을 평가한 것입니다. "
        u"독립적인 사람은 누구도 이를 검토하지 않았습니다. 등급은 지금까지 "
        u"무엇이 확인되었는지를 줄별로가 아니라 언어 전체 기준으로 적은 "
        u"것입니다. 영어 자체가 기준입니다. 손으로 쓴 글이며 다른 모든 언어는 그 "
        u"글이 번역된 것입니다.\n"
        u"\n"
        u"# 문구를 고치는 방법\n"
        u"수정은 신고에서 시작됩니다. 그 줄이 어느 언어였는지 밝히고, 그 줄이 "
        u"공개하는 키를 제시하고, 말하려던 영어 본문을 붙여 넣고, 대신 쓸 "
        u"문구를 제안하십시오.\n"
        u"\n"
        u"- 한 줄당 신고 하나만 쓰면 수정이 쉽게 적용됩니다.\n"
        u"- 서명 화면을 먼저 신고하십시오. 확인 대화상자의 잘못된 문장은 비용이 "
        u"큰 종류입니다.\n"
        u"- 이 문서 끝의 링크를 사용하십시오. 이 프로젝트의 추적기에 번역용으로 "
        u"이미 표시된 이슈가 열리므로 다시 입력할 것이 없습니다.\n"
        u"\n"
        u"# 사람의 검토로 가는 길은 수정뿐입니다\n"
        u"기계로 채워진 상태에서 그것을 다른 것으로 바꾸는 수단은 없습니다. "
        u"언어를 얼마나 자주 쓰는지, 두 번째 기계가 첫 기계와 동의하는지, 번역 "
        u"메모리도 마찬가지입니다. 어떤 문구가 사람의 검토를 거친 상태가 되려면 "
        u"사람이 자기 언어로 직접 읽고 받아들여야 하며, 한 줄은 실제로 확인한 "
        u"그 언어에 대해서만 사람의 검토를 거친 것이 됩니다.\n"
        u"\n"
        u"그때까지 표시는 원래 자리에 남습니다. 아무도 읽지 않은 번역은 번역이 "
        u"없는 것보다 낫지만, 사람이 책임진 번역과는 같은 것이 아닙니다."
    ),

    # ---- the remaining articles ----------------------------------------
    "help.topic_browser_title": u"브라우저 지원",
    "help.topic_browser_text": (
        u"어떤 브라우저에서 지갑이 동작하며 호환성 알림은 무엇을 뜻합니까."
    ),
    "help.topic_browser_body": (
        u"# 브랜드 이름이 아니라 감지된 기능\n"
        u"이 지갑은 어떤 브라우저를 쓰는지 묻지 않습니다 — 실제로 필요한 네 "
        u"가지 플랫폼 기능만 조사합니다. WebSocket(체인 데이터), "
        u"WebCrypto(키 저장소), BigInt(금액 계산), 로컬 저장소(설정)입니다. "
        u"침묵은 통과입니다. 최신 브라우저에서 배너가 없다는 것은 기능이 모두 "
        u"있다는 뜻입니다.\n"
        u"# 가장 흔한 원인: 보안 컨텍스트가 아님\n"
        u"최신 브라우저는 보안 컨텍스트에서만 WebCrypto를 노출합니다. https "
        u"페이지, localhost, 파일을 직접 연 경우입니다. 같은 최신 브라우저를 "
        u"평문 http로 제공하면(예: LAN 주소) WebCrypto가 없다고 보고합니다 — "
        u"브라우저는 멀쩡하고 주소가 그렇지 않은 것입니다. 폴더를 https나 "
        u"localhost로 제공하거나 index.html을 직접 여십시오.\n"
        u"# 무엇이 계속 동작합니까\n"
        u"조회 기능은 언제나 동작합니다. 잔액, 시장, 익스플로러, 투표는 지갑 "
        u"기능 없이 공개 체인 데이터를 읽습니다. 로컬 서명만 없는 기능이 "
        u"필요합니다. 알림을 닫으면 이 기기에서만 숨겨지고, 어떤 페이지도 "
        u"막지 않습니다."
    ),
    "help.topic_backups_body": (
        u"# 일찍 백업하고, 두 번 백업하십시오\n"
        u"자금을 넣기 전에 로컬 지갑을 백업하십시오 — 앞으로는 백업 하나면 보통 "
        u"충분하지만, 본인만 접근할 수 있는 안전한 장소 두 곳 이상에 "
        u"보관하십시오.\n"
        u"이 지갑에는 백업 파일이 없습니다. 브레인키 자체가 백업이며, "
        u"비밀번호만으로는 아무것도 복구되지 않습니다. 단어와 비밀번호를 모두 "
        u"잃으면 자금은 사라집니다. 비밀번호를 단어 옆에 두는 일은 결코 하지 "
        u"마십시오.\n"
        u"# 브레인키가 백업입니다\n"
        u"원시 키를 직접 가져온 적이 없다면 지갑 전체가 브레인키 하나에서 "
        u"결정적으로 파생됩니다 — 단어들의 나열입니다. 브레인키를 적어 두면 그 "
        u"지갑의 모든 계정과 자금을 백업한 셈입니다.\n"
        u"지갑 관리자에서 확인해 종이에 옮기고, 디지털 자료와 따로 "
        u"보관하십시오. 참조 지갑의 .bin 파일은 여기서 가져올 수 없습니다 — "
        u"지갑이 화면에 그렇게 말하며, 내려받는 파일도 없습니다.\n"
        u"# 고급: 계층적 권한\n"
        u"단순한 키 대신 가중치가 있는 다중 계정 권한을 사용한다면 키 백업만으로 "
        u"접근을 복구하지 못할 수 있습니다 — 권한 구조 자체가 중요합니다.\n"
        u"권한 문서를 다시 읽고 단어만이 아니라 권한 설정 전체를 기록하십시오."
    ),
    "help.topic_wallets_body": (
        u"# 로컬 금고를 갖춘 웹 앱\n"
        u"이 애플리케이션은 브라우저에서 실행되고, 네트워크로 나가는 관문으로 "
        u"체인 노드와 통신합니다. 비밀에 해당하는 모든 것은 브라우저의 로컬 "
        u"금고에 남습니다.\n"
        u"# 클라우드 로그인 없음\n"
        u"이 지갑에는 아이디와 비밀번호 로그인이 없습니다. 이 지갑의 모든 지갑은 "
        u"특정 브라우저 안에만 있습니다. 새 브라우저나 컴퓨터에서 계정을 쓰려면 "
        u"같은 브레인키에서 시작해야 합니다 — 그것을 스스로 여는 증명 정보는 "
        u"없습니다.\n"
        u"# 로컬 지갑\n"
        u"로컬 지갑은 특정 브라우저 안의 데이터베이스입니다. 브레인키를 옮겨 "
        u"가져오지 않으면 다른 컴퓨터나 브라우저로 따라가지 않습니다.\n"
        u"실제 자금을 로컬 지갑에 맡기기 전에 백업 문서를 보십시오.\n"
        u"# 비밀번호 원칙\n"
        u"비밀번호는 금고를 암호화합니다. 짧거나 재사용한 비밀번호는 추측에 "
        u"무너집니다. 종이에 적은 고유한 비밀번호는 그렇지 않습니다.\n"
        u"비밀번호를 바꾸면 전체를 다시 암호화합니다 — 먼저 현재 비밀번호를 "
        u"확인하고, 떠나기 전에 지갑이 여전히 열리는지 확인하십시오."
    ),
    "help.topic_assets-feed_title": u"가격 피드 게시",
    "help.topic_assets-feed_text": (
        u"본인이 피드하는 시장연동자산의 가격을 게시하십시오."
    ),
    "help.topic_assets-feed_body": (
        u"# 가격 피드 게시\n"
        u"시장연동자산의 정산 가격을 피드 데스크에서 게시하십시오. 확인 "
        u"대화상자에 서명 전 정확한 수수료가 표시됩니다."
    ),
    "help.topic_assets-issue_title": u"자산 발행",
    "help.topic_assets-issue_text": (
        u"발행 데스크에서 관리하는 자산의 공급량을 발행하십시오."
    ),
    # The English possessive "the asset's precision" becomes a clause rewrite:
    # G7 forbids the apostrophe outright, and "자산의 정밀도" says the same
    # thing without one.
    "help.topic_assets-issue_body": (
        u"# 자산 발행\n"
        u"계정이 관리하는 자산의 공급량을 발행 데스크에서 생성하십시오. 금액은 "
        u"해당 자산의 정밀도를 따르며 확인 대화상자에 서명 전 정확한 수수료가 "
        u"표시됩니다."
    ),
    "help.topic_htlc_text": u"지급하거나 환불하는 해시 타임락 스왑입니다.",
    "help.topic_voting_text": (
        u"증인, 위원회 위원, 워커에 투표하십시오 — 또는 프록시에 위임하십시오."
    ),
    "help.topic_about-making_title": u"이 지갑의 제작 과정",
    "help.topic_about-making_text": u"이 지갑의 제작 과정 —",
    # Same shape as the English: three `# ` headings and the archive pointer.
    # The builders' replies apostrophe becomes a clause (G7), and the two
    # quoted section names become the ko.json “” convention.
    "help.topic_about-making_body": (
        u"# 이 지갑의 제작 과정\n"
        u"다음은 이 지갑을 만든 최초의 제작 과정입니다. 2026년 9월 26일의 "
        u"“bitshares-ui 인수” 요청부터 10월 3일의 이슈 1 수정까지, 이 지갑을 "
        u"만든 모든 요청과 제작자의 답변을 편집 없이 그대로 옮겼습니다.\n"
        u"이 글은 이 지갑이 서 있는 결정을 기록합니다. 이슈 #3583의 천 시간 "
        u"함정 뒤에 또 다른 React 승격 작업을 포기한 것, 그래서 이 지갑은 "
        u"릴리스 주기가 있는 어떤 것에도 의존하지 않는 것. 서명을 외부에 맡기지 "
        u"않고 옛 지갑처럼 모든 트랜잭션을 로컬에서 하는 것. 클래식 모양을 "
        u"기본으로 한 세 가지 테마. 원시 체인 정수를 절대 보여주지 않고 사람이 "
        u"읽는 단위로 표시하는 숫자. 첫 슬라이스부터 휴대전화 우선 레이아웃을 "
        u"쓰는 것. 그리고 추정이 아니라 살아 있는 체인에서 읽는 수수료. 역사로 "
        u"읽으십시오. 이것이 지갑이 만들어진 방식입니다.\n"
        u"# 전체 대화 기록\n"
        u"대화 전체가 주고받은 그대로 기록된 사본은 소개 페이지(#/about)에 "
        u"있습니다. 그곳의 “전체 제작 대화” 항목을 펼치면 모든 대화를 "
        u"둘러보거나, 키워드로 걸러 내거나, ?dialog=N을 넣어 특정 대화로 바로 갈 "
        u"수 있습니다."
    ),

    # =============================================== i18n — honesty surface (6)
    # The machine-translation warning a Korean-only reader must be able to
    # READ. Left in English it would be the one string on the page that cannot
    # warn its own reader. wording follows the same split as every other
    # Korean string: the chip label and the link labels are bare noun phrases
    # (they are links), the body is a ~습니다 statement.
    "i18n.badge_label": u"번역 상태: 기계 번역이며 사람이 확인하지 않았습니다",
    "i18n.badge_body": (
        u"이 번역은 기계가 쓴 것이며 사람이 확인하지 않았습니다. 서명 화면에서 "
        u"*가 붙은 줄은 원래 영어도 함께 보여줍니다."
    ),
    "i18n.badge_details": u"무슨 뜻입니까",
    "i18n.badge_improve": u"이 번역 개선에 도움주기",
    "i18n.risk_show_english": u"이 줄의 영어 원문 보기",
    "i18n.risk_about_translations": u"이 번역에 대하여",

    # ================================================================ pool (25)
    "pool.asset_1_field": u"자산 1(어느 구간이든 가능)",
    "pool.asset_2_field": u"자산 2(어느 구간이든 가능)",
    "pool.clear_btn": u"지우기",
    # %(legs)s is a comma-joined list of the pool's non-empty legs
    # (pool-ui.js joins the ids), so it takes 잔액 as its head noun rather than
    # a particle the reader would have to resolve per item.
    "pool.delete_not_empty": (
        u"비어 있지 않습니다 — 삭제하려면 %(legs)s 잔액이 0이어야 합니다."
    ),
    "pool.direct_hit": u"풀 직접 조회 — 페이지 매기기 숨겨졌습니다.",
    "pool.map_core_self": u"BTS는 BitShares의 핵심 토큰입니다",
    "pool.min_swaps": u"최소 스왑 수",
    "pool.my_swaps_hint": (
        u" 위의 스왑 패널에서 실행하십시오 — 이 풀에서의 스왑 내역이 여기에 "
        u"표시됩니다."
    ),
    "pool.no_filter_match": u"이 필터와 일치하는 스왑이 없습니다.",
    # The ids stay byte-verbatim (rule 1); only the two words around them are
    # prose, and 심볼 is pool.share_ph's own word for a UIA symbol.
    "pool.share_or_pool_hint": u"심볼, 1.3.x 또는 풀 1.19.x",
    "pool.stake_autofill_hint": (
        u"한쪽 수량만 입력하십시오 — 다른 쪽은 풀 비율로 자동으로 채워집니다."
    ),
    "pool.stake_preview_bad": u"수량을 확인하십시오 — 지분 예상이 없습니다.",
    "pool.stake_preview_need_both": (
        u"지분을 예상하려면 양쪽 수량을 입력하십시오."
    ),
    "pool.stake_preview_unavailable": u"지분 예상값을 사용할 수 없습니다(오프라인).",
    "pool.stake_ratio_empty": u"풀이 비어 있습니다 — 양쪽 수량을 직접 입력하십시오.",
    "pool.stake_ratio_row": u"비율(스팟)",
    "pool.stake_shares_row": u"예상 LP 지분",
    "pool.swap_desk": u"스왑 데스크",
    # 시장 수수료 is the opposite pole of pool.withdrawal_row = 출금 수수료, so
    # the two fee rows of the same form read as a pair. The trailing — is the
    # shipped Korean empty-state marker and stays.
    "pool.swap_mkt_preview_dash": u"시장 수수료(미리보기): —",
    "pool.swap_mkt_row": u"시장 수수료",
    "pool.swap_preview": u"견적(미리보기): ",
    "pool.swap_preview_dash": u"견적(미리보기): —",
    "pool.swaps_hint": (
        u" 스왑은 이 풀에서 첫 교환이 일어나면 표시됩니다 — 위의 스왑 패널에서 "
        u"실행하십시오."
    ),
    "pool.uc_action": u"동작",
    "pool.uc_title": u"계속하려면 잠금을 해제하십시오",

    # =========================================================== pool_net (29)
    "pool_net.canvas_label": (
        u"풀 네트워크 지도입니다. Enter 키를 눌러 BTS를 여십시오."
    ),
    "pool_net.col_a": u"자산 1",
    "pool_net.col_b": u"자산 2",
    "pool_net.col_pool": u"풀",
    "pool_net.collapse": u"접기",
    "pool_net.direct": u"BTS와 쌍",
    "pool_net.empty": u"이 필터와 맞닿는 풀이 없습니다.",
    "pool_net.expand": u"펼치기",
    "pool_net.hops": u"BTS까지 %(n)s홉",
    # The legend introduces the asset chips, and 브랜드 is the word ko.json
    # already uses for a gateway-backed asset brand (topic_gateways_body).
    "pool_net.legend": u"브랜드",
    "pool_net.loading": u"네트워크를 불러오는 중입니다…",
    "pool_net.node_card": u"%(sym)s (%(id)s)·풀 %(n)s개·%(hops)s",
    "pool_net.offline": (
        u"네트워크를 사용할 수 없습니다 — 내장 골격을 표시합니다. 연결 후 다시 "
        u"시도하십시오."
    ),
    "pool_net.offline_empty": (
        u"네트워크를 사용할 수 없습니다 — 골격 풀을 캐시한 것이 없습니다."
    ),
    "pool_net.orphan": u"BTS에서 고립",
    "pool_net.partial": (
        u"실시간 업데이트가 완결되지 않았습니다 — 내장된 풀을 표시합니다."
    ),
    "pool_net.phys": u"물리 효과",
    "pool_net.prompt": (
        u"노드를 탭하면 자산, 선을 탭하면 풀이 표시됩니다."
    ),
    "pool_net.ramp": u"풀 규모: 작음 → 큼",
    "pool_net.ready": u"풀 %(pools)s개·자산 %(assets)s개",
    "pool_net.title": u"풀 네트워크",
    "pool_net.twin": u"풀 행(%(n)s)",
    "pool_net.twin_more": (
        u"풀 %(n)s개 중 %(shown)s개를 표시합니다. 필터를 좁히면 더 적게 "
        u"표시됩니다."
    ),
    "pool_net.verdict_full": u"풀 %(pools)s개·자산 %(assets)s개",
    "pool_net.verdict_orphan": u"%(a)s와 %(b)s 사이에 경로가 없습니다",
    # pool.map_pair_reach is the shipped Korean for the same sentence, so the
    # verdict line and the map card reuse its particle form verbatim.
    "pool_net.verdict_path": u"%(a)s이(가) %(b)s에 %(n)s홉으로 도달합니다",
    "pool_net.verdict_star": u"%(s)s와 연결된 풀: %(n)s개",
}

# Keys whose Korean value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from KO. Each one is asserted
# to still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * the honesty chip, which renders the literal string "i18n" and is identical
#     in every shipped locale (see tooling/apply_i18n_es_honesty.py);
#   * pure glue a map edge card prints as data: "%(pool)s · %(a)s–%(b)s ·
#     %(ba)s %(sa)s + %(bb)s %(sb)s" and its no-balance sibling — the separator
#     IS the content there, and translating the space inside a glue string would
#     change what the reader sees, so they stay English. (Their market-network
#     twins are already listed in chunk A's KEPT_ENGLISH for the same reason.)
KEPT_ENGLISH = {
    # ---- i18n (honesty surface)
    "i18n.badge_chip": u"i18n",
    # ---- pool_net
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
}


if __name__ == "__main__":
    sys.exit(main())