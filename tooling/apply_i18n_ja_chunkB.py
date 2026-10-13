#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ja chunk-B: fill the nine tail sections ja.json still leaves in English.

Scope: ONLY the nine sections listed below (help, pool, pool_net, explorer,
seo, splash, about, shell, menu). The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ja.json, or one whose English master moved, is REFUSED;
  * JA + KEPT_ENGLISH together must account for EVERY untranslated key of the
    nine sections, so a forgotten string is a refusal, never a silent English.

This is the Japanese sibling of tooling/apply_i18n_ja_chunkA.py and keeps its
gates one for one; it is also the ja sibling of the zh/de/es chunk-B batches,
which split the file the same way. chunk-A owns account, account_net, settings,
market, market_net and asset and REFUSES anything outside them, so the two
never overlap in either direction.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/validate_translations.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master.
                      This batch translates 10 markdown bodies (help, about):
                      every heading stays a heading on the same line and every
                      [label](#/hash) keeps its hash byte-for-byte while only
                      the label is translated;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an unclaimed key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  ja punctuation no value this batch writes may carry an ASCII or
                      typographic apostrophe, an ideographic space (U+3000), or a
                      Cyrillic letter. Japanese quotes a button with 「」 and
                      does not apostrophise, and ja.json already ships 3,532
                      translated strings that use none of the three; an
                      ideographic space in particular would smuggle an English
                      word gap back into a language that writes none. The English
                      masters DO apostrophise ("the builders' replies"), so those
                      possessives are rephrased rather than carried over. This is
                      the ja sibling of the zh batch's apostrophe gate.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: ja.json already ships "x*y=k"-style and
                      "· 有効期限 " neighbours outside this batch. The sweep
                      runs file-wide, but a hit OUTSIDE the nine sections is
                      reported as PRE-EXISTING and does not gate this batch:
                      chunk-A owns those keys, and an insert-only pass that
                      repaired a neighbour would be exactly the silent edit the
                      scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                      LOAN below, or the write is refused. A Japanese crypto UI
                      prints DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy,
                      Smartcoin, Pool and Brainkey in Latin exactly as a Chinese
                      one does - inventing a fake katakana transliteration
                      instead would be worse than the loanword. Markdown link
                      targets are stripped before the sweep: a `#/account/me`
                      hash is a ROUTE (rule 1 data), and G4 already proves it
                      byte-verbatim. The gate is batch-scoped on purpose: the
                      rest of ja.json already carries hundreds of distinct Latin
                      tokens from earlier batches.

Register: the 3,532 strings ja.json already ships are POLITE (です/ます) -
"残高を読み込めませんでした。", "入力してください。", "見つかりませんでした —" - so
this batch is polite too, in prose. Labels and column heads stay bare nouns
("残高", "提案", "発行者"), which is how a table head reads in any register.
The help bodies are the one place the register is fully continuous: they are
sentences a newcomer reads end to end, so they are plain です/ます throughout
rather than the clipped list style some shipped help bodies use.

Japanese writes no space between words, so this batch never invents one. The
one space Japanese does use is the 和欧間 gap around a Latin or numeric run,
which the existing translations apply consistently ("NFT メタデータ",
"4文字シンボル", "MCR %（人間可読、例: 175）"); this batch follows it. The strings
that are pure data (a row title "ID", a feed stamp "%(id)s @ %(ts)s", the
edge-card glue "%(pool)s · %(a)s–%(b)s") are therefore left byte-identical in
KEPT_ENGLISH rather than "translated" with a space the reader does not want.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (first 100 assets, 360px, 4K, 26 September 2026,
issue #3583, ?dialog=N) the translation keeps it byte-verbatim.

SEO: the seo.* values are <title> and meta descriptions, so they stay factual
and short - what the page shows, that reads need no login - with no marketing
tone, matching the plainness of every other string in this batch.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ja_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ja_chunkB.py --apply         # writes ja.json
  python3 tooling/apply_i18n_ja_chunkB.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
JA_PATH = os.path.join(BASE, "ja.json")

# The nine sections this batch owns. Everything else belongs to chunk-A and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool", "pool_net", "explorer", "seo", "splash", "about", "shell",
    "menu",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from JA below so they keep the
# English bytes, and the verify pass re-asserts every one after the write. Most
# of them live in chunk-A's settings section; the shell brands live here and are
# listed so a drift anywhere in the file is caught.
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
# G9: a markdown link target is a route, not prose. Stripped before the Latin
# sweep so `#/market/BTS_USD` and `#/registration/local` do not read as
# undeclared loanwords; G4 proves every one of them byte-verbatim anyway.
LINK_TARGET = re.compile(r"\]\([^)]*\)")
# A route quoted inside prose ("the About page (#/about)") is the same rule-1
# data as a link target, so it is stripped from the Latin sweep too.
ROUTE = re.compile(r"#/[A-Za-z0-9_\-./?=&%]*")
INVISIBLE = re.compile(u"[­‍⁠﻿]")
DOT_CHARS = u"·•‧･"
APO_TYPO = u"’"
APO_ASCII = u"'"
IDEO_SPACE = u"　"
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
# G9: a Latin run inside a Japanese value. A token may continue through - _ . /
# so "Same-T", "index.html" and "bitshares-ui" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Japanese crypto UI prints in Latin, a platform API name the reader
# looks up verbatim, or a literal that must survive translation (a build-date
# fragment, the ?dialog=N deep link). Anything else has to be Japanese.
#
# "About" is the About page's own name, so the reader has to recognise it;
# "Enter" is the key name the canvas hint teaches; "LP" is the share unit
# ja.json already prints as "LP シェア"; "BTS/USD" is the pair name as one
# token, which is how the market page and the SEO title both spell it.
LOAN = frozenset((
    "API", "BTS", "BTS/USD", "About", "BigInt", "BitShares", "CER", "ES",
    "Enter", "GitHub", "HTLC", "ID", "JavaScript", "JSON", "LAN", "Local",
    "LP", "Master", "MSSR", "N", "React", "Same-T", "USD", "Web", "WebCrypto",
    "WebSocket", "acquire", "bin", "bitshares-ui", "dialog",
    "docs/vanilla-ui-dialog.md", "http", "https", "index.html", "issue",
    "localhost", "op",
))


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    A middle dot is clean when it is space-separated, as it is everywhere in
    this dictionary - or when both neighbours are alphanumeric, which is
    algebraic notation. Anything else is a stray dot that will render as a
    different word to the reader.
    """
    hit = INVISIBLE.search(value)
    if hit:
        return hit.group(0)
    for i, ch in enumerate(value):
        if ch in DOT_CHARS:
            before = value[i - 1] if i else u" "
            after = value[i + 1] if i + 1 < len(value) else u" "
            if before == u" " and after == u" ":
                continue
            if before.isalnum() and after.isalnum():
                continue
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
            "line count changed: %s (en %d, ja %d)"
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


def check_ja_hygiene(batch, problems):
    """G7 + G9: apostrophes, ideographic space, Cyrillic, undeclared Latin.

    Scoped to the values THIS BATCH writes. ja.json's other sections carry
    their own Latin tokens from earlier batches; re-auditing those here would
    make this file the owner of someone else's vocabulary.
    """
    for key, value in sorted(batch.items()):
        # Interpolations are substituted data, not prose: %(name)s and {s} must
        # never count as an undeclared loanword (G1 proves they survived).
        prose = PLACEHOLDER.sub("", value)
        prose = BRACE.sub("", prose)
        # A markdown link target is a route (rule 1 data), already proven
        # byte-verbatim by G4 - never prose, so never a loanword decision. A
        # route quoted in the middle of a sentence is the same case.
        prose = LINK_TARGET.sub("]", prose)
        prose = ROUTE.sub("", prose)
        # A count keeping its English unit suffix ("90d", "24h", "360px") is
        # data the brief requires byte-verbatim, not prose: it cannot be
        # half-translated without changing the number the reader compares
        # against the layout beside it.
        prose = COUNT_UNIT.sub("", prose)
        if APO_ASCII in value:
            problems.append("G7: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7: typographic apostrophe in %s" % key)
        if IDEO_SPACE in value:
            problems.append("G7: ideographic space in %s" % key)
        hit = CYRILLIC.search(value)
        if hit:
            problems.append("G7: Cyrillic %r in %s" % (hit.group(0), key))
        for token in sorted(set(LATIN_TOKEN.findall(prose))):
            if token not in LOAN:
                problems.append("G9: undeclared Latin token %r in %s"
                                % (token, key))


def verify():
    """Structural re-proof of the shipped file against the en master."""
    ja, en = load(JA_PATH), load(EN_PATH)
    d, e = flat(ja), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: chunk-A owns them, and an
    # insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` - problems this batch can
    # answer for - gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
            check_batch(e, key, d[key], bad, chars=key in JA)
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
            if key in JA:
                bad.append(where)
            else:
                pre.append(where)
    check_ja_hygiene(JA, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(JA) if d.get(k) == e.get(k)]
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
        and k not in JA and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(JA) - len(same), len(JA)))
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
    meta = ja.get("_meta", {})
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
    raw = open(JA_PATH, encoding="utf-8").read()
    ja = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(ja, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: ja.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(ja))
    before_meta = json.dumps(ja["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(JA.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in ja.json: %s" % key)
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
        deep_set(ja, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(JA) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (JA and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(JA) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in ja.json: %s" % key)
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

    check_ja_hygiene(JA, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(ja)
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
    # UNCLAIMED, which is the honest state for them. Nothing else in _meta
    # moves - filling strings is not verification, so the controller's v2
    # provenance/verified/high_risk fields stay untouched.
    meta = ja["_meta"]
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
    added = sorted(k for k in JA
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

    print("ja chunk-B: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-10s %d" % (sec, by_section.get(sec, 0)))
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

    with open(JA_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ja, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/ja.json")
    return 0


# The sitemap body is 83 lines of markdown whose every link target must survive
# byte-for-byte, so it is written as an explicit line list: a mistyped line is
# then a wrong list entry, which G4 catches, instead of a lost newline.
SITEMAP = u"\n".join([
    u"このウォレットのすべてのページを、バーガーメニューと同じ区分で並べています。リンクのある項目は直接開きます。メニューカードのないページの下に並ぶ詳細表示は親ページから開きます。",
    u"# ウォレット",
    u"- [ダッシュボード](#/)",
    u"- [マイアカウント](#/account/me)",
    u"- [アカウント](#/accounts)",
    u"- [送金](#/transfer)",
    u"- [請求書](#/invoice)",
    u"- [ベスティング](#/vesting)",
    u"- [ウォレット](#/wallet)",
    u"- [ウォレットパスワードの変更](#/wallet/password)",
    u"- [ウォレット作成（ブレインキー）](#/create-wallet-brainkey)",
    u"- [既存のアカウントをインポート](#/existing-account)",
    u"- [新規アカウントの登録](#/create-account)",
    u"- [ログイン](#/login)",
    u"- [登録](#/registration)",
    u"- [紹介](#/referrals)",
    u"# 取引",
    u"- [取引所](#/markets)",
    u"- [インスタント取引](#/instant-trade)",
    u"- [流動性プール](#/pools)",
    u"- [クロスレート](#/cross-rates)",
    u"- [借入](#/borrow)",
    u"- [バーター](#/barter)",
    u"- [入金 / 出金](#/deposit-withdraw)",
    u"- [Same-T ファンド](#/samet)",
    u"- [スポットライト](#/spotlight)",
    u"# 運用と保護",
    u"- [クレジットオファー](#/credit-offer)",
    u"- [ダイレクトデビット](#/direct-debit)",
    u"- [HTLC](#/htlc)",
    u"- [チケット](#/tickets)",
    u"- [エアドロップ](#/airdrop)",
    u"- [カスタム権限](#/authorities)",
    u"- [アカウントリスト](#/lists)",
    u"# ガバナンス",
    u"- [投票](#/voting)",
    u"- [提案](#/proposals)",
    u"- [ワーカー作成](#/create-worker)",
    u"- [予測市場](#/prediction)",
    u"# 探索",
    u"- [エクスプローラー](#/explorer)",
    u"- [アセット](#/assets)",
    u"- [アセット作成](#/assets/create)",
    u"- [アセット発行](#/assets/issue)",
    u"- [フィード発行](#/assets/feed)",
    u"- [ネットワーク手数料](#/explorer/fees)",
    u"- [操作](#/ops)",
    u"- [主要オペレーション](#/top-ops)",
    u"- [ニュース](#/news)",
    u"# エクスプローラー",
    u"- [エクスプローラー（オンチェーン）](#/explorer)",
    u"- [アセット](#/explorer/assets)",
    u"- [プール](#/explorer/pools)",
    u"- [アカウント](#/explorer/accounts)",
    u"- [ウィットネス](#/explorer/witnesses)",
    u"- [委員会](#/explorer/committee)",
    u"- [マーケット](#/explorer/markets)",
    u"- [手数料](#/explorer/fees)",
    u"- [フィード](#/explorer/feeds)",
    u"# ラボ",
    u"- [API ラボ](#/api-lab)",
    u"- [ES ラボ](#/es-lab)",
    u"- [トランザクションビルダー](#/txbuilder)",
    u"- [アカウントネットワーク](#/account-network)",
    u"# 個人",
    u"- [トロルボックス](#/trollbox)",
    u"- [お気に入り](#/favourites)",
    u"- [価格アラート](#/alerts)",
    u"- [ヘルプ](#/help)",
    u"- [翻訳の制限](#/help/translation-limitations)",
    u"- [このウォレットについて](#/about)",
    u"- [コミュニティ](#/community)",
    u"- [設定](#/settings)",
    u"# メニューカードのないページ",
    u"登録の派生ページ、アカウントとマーケットのデスク、詳細表示は、上記のページから、またはウォレット内の他のリンクから開きます。",
    u"- [ローカル登録](#/registration/local)",
    u"- [クラウド登録](#/registration/cloud)",
    u"- [アカウントページの例](#/account/committee-account)",
    u"- [マーケットデスクの例](#/market/BTS_USD)",
    u"- [アセットページの例](#/asset/BTS)",
    u"- [プールデスクの例](#/pools/1.19.66)",
    u"- [メニュー一覧](#/menu)",
    u"特定のクレジットオファー、ディール、提案、ブロック、トランザクション、HTLC、予測市場、送金先、請求書、ゲートウェイ、設定タブ、エクスプローラーのタブ、ヘルプ記事の詳細表示は親ページから開き、アドレスに ID または名前を受け取ります。",
])

# The translation-limitations body is 23 lines (four headings, four bullets, and
# blank lines between paragraphs) - also written as a line list so G4 can prove
# the structure survived.
TRANSLATION_LIMITS = u"\n".join([
    u"機械で埋められたと表示された翻訳は、機械が書いたものです。英語と同じ意味かどうかを読む人はいません — そのため、このウォレットのヘッダーでは英語以外のすべての言語にマーカーのチップが付きます。英語は他の言語が翻訳元としたテキストなので、マーカーは付きません。",
    u"",
    u"# 行の * が意味すること",
    u"署名画面の行にある * は2つの意味を同時に持ちます: その文言が機械で埋められたことと、元の英語が1タップで表示できることです。* をタップすると、このウォレットの英語マスターが保存している英語がその行の下に現れます — 他のすべての言語が翻訳元とした同じテキストであり、その言い換えではありません。",
    u"",
    u"マーカーは行に付きます。その中の単語に付くのではありません。* は翻訳された行を1つ示し、ウォレットは固定のルールで行を選びます: 署名画面、不可逆な操作の画面、復旧画面のすべての行 — 長い段落は代わりにこの記事で扱うため、長さの上限があります — さらに、英語が危険な表現を含む行は、どの画面でも対象です。ID や金額だけを並べた行にも付きます（例えば送金の宛先フィールド）。ID に言及する長い段落には付きません。チェーン上の値そのもの — セルの金額、列の ID、アセットシンボル — はそもそも翻訳された行ではないので、マーカーは付きません: 比較する英語の文言が背後にないからです。",
    u"",
    u"# 信頼度の意味",
    u"このウォレットが出荷するすべての言語は、下の表に1つの評価を持ちます。高いは英語に忠実で自然に読めることを意味します。良好は使える水準ですが、表現がやや不自然な場合があります。普通は下書きとして読み、頼る前に英語を確認してください。",
    u"",
    u"以下の評価は、文字列を書いた機械が自分の作品を採点したものです。独立した人物による監査は受けていません。評価は行ごとではなく言語全体をまとめて、それまでに確認されたことを示します。英語が基準です: 英語は手で書かれ、他のすべての言語はそこから翻訳されています。",
    u"",
    u"# 文字列を修正する方法",
    u"修正は報告から始まります。行がどの言語だったか、その行を開示するキーは何か、想定されていた英語は何かを伝え、代わりに使う表現を提案してください。",
    u"",
    u"- 1行につき1件の報告にすると、修正を容易に適用できます。",
    u"- まず署名画面の報告をしてください: 確認ダイアログの文が誤っている場合ほど、損失が大きくなります。",
    u"- この記事の末尾にあるリンクを使ってください。このプロジェクトのトラッカーに、翻訳用のラベルが付いた issue が開きます。入力し直す必要はありません。",
    u"",
    u"# 人が確認した状態に至る唯一の道筋",
    u"機械で埋められた状態から何かを移動させるものはありません: その言語がどれくらい使われているかでもなく、2台目の機械が1台目に同意することでもなく、翻訳メモリでもありません。誰かが自分の言語で読んで受け入れたときに、その文字列は人が確認した状態になります。その行は実際に確認された言語についてのみ、人が確認した状態になります。",
    u"",
    u"それまでマーカーはそのままです。誰も読んでいない翻訳は、翻訳がないよりましですが、人がその責任を負った翻訳と同じものではありません。",
])

JA = {
    # ================================================================ about (18)
    # The build-dialog archive is a list of prompt/reply pairs; 開発対話 names
    # the same thing the help article's heading calls it, so the two agree.
    "about.dlg_heading": u"開発対話の全記録",
    "about.dlg_heading_c": u"開発対話の全記録（%(total)s）",
    "about.dlg_no_reply": (
        u"返信は記録されていません — 次のプロンプトがすぐ続きました。"
    ),
    "about.dlg_noscript": (
        u"この記録には JavaScript が必要です。同じテキストはソースリポジトリの "
        u"docs/vanilla-ui-dialog.md にあります。"
    ),
    "about.dlg_search_clear": u"クリア",
    "about.dlg_search_ph": u"開発対話を絞り込み…",
    "about.dlg_showing": u"表示中",
    "about.dlg_showing_c": u"表示中 %(shown)s / %(total)s",
    "about.dlg_unavailable": u"開発対話の記録を利用できません。",
    "about.hero_lede": (
        u"BitShares チェーンのためのウォレット — マーケット、アカウント、ガバナンス、"
        u"探索 — を、プレーンな Web ファイルとして動かしています。フレームワークも"
        u"インストーラーも、私たちへのアカウント登録もありません。鍵がこのブラウザから"
        u"出ることはありません。"
    ),
    # Two quoted literals survive: the build prompt "acquire bitshares-ui" and
    # the ?dialog=N deep link. The English master apostrophises ("the builders'
    # replies"); G7 bans the apostrophe, so the possessive is rephrased as
    # 構築者たち — the same facts, no borrowed punctuation.
    "about.making_body": (
        u"以下は当初の開発記録です — このウォレットを作ったすべてのプロンプトを、"
        u"2026年9月26日の「acquire bitshares-ui」から10月3日の issue 1 の修正まで、"
        u"構築者たちの返信とともに編集せずに残しています。このウォレットが立つ基盤と"
        u"なる判断が記録されています: issue #3583 とその1000時間の罠のあとに React "
        u"の別のアップグレードを断念し、リリースサイクルを持つ何にも依存しないように"
        u"したこと。すべてのトランザクションを古いウォレットと同じくローカルで署名し、"
        u"外部に委ねなかったこと。クラシックな外観を既定とする3つのテーマ。数は常に"
        u"人間表示にし、生の整数は表示しないこと。最初のスライスからスマートフォン"
        u"優先のレイアウトにしたこと。手数料は推定せず、ライブチェーンから読むこと。"
        u"歴史として読んでください — このウォレットはそうやって作られました。"
    ),
    "about.making_title": u"このウォレットの開発の記録",
    "about.s2_title": u"本物のオーダーブックで取引",
    "about.s3_body": (
        u"このウォレットが置き換える側のウォレットは、古いパッケージと誰も再現できない"
        u"ツールチェーンのもとで停止しました。リリースサイクルへの依存を避けるために"
        u"作られています: フレームワークなし、パッケージマネージャーなし、ビルド手順なし "
        u"— 10年後もブラウザで動く最小構成です。"
    ),
    "about.s3_title": u"更新なしで長く動き続けます",
    "about.s4_body": (
        u"戻ってきたユーザーはすぐに馴染めます — クラシックなウォレットと同じページ、同じ"
        u"パネル、同じ語彙 — 此同时、残高、オーダーブック、接続状態はそのままライブ"
        u"更新されます。マーケット、アカウント、アセットを横断して検索でき、3つのテーマと、"
        u"360px のスマートフォンから4Kの取引デスクまで使えるレイアウトです。"
    ),
    "about.s4_title": u"同じページ、ライブ更新",
    "about.s5_body": (
        u"チェーンは整数で話します。あなたが見ることはありません。すべての金額はアセットの"
        u"精度どおりに置かれ、すべてのパーセントは正しい値で示され、すべての手数料は署名の"
        u"前にライブチェーンから読み取ります。"
    ),

    # ============================================================= explorer (17)
    "explorer.assets_mode_all": u"すべて",
    "explorer.assets_mode_market": u"スマートコイン",
    "explorer.assets_mode_prediction": u"予測市場",
    "explorer.assets_mode_user": u"ユーザ発行",
    # The count line is "Showing: <mode> — 10 of 50", so the connective is a
    # slash, exactly as the already-translated markets tab (explorer.markets_of)
    # does; a Japanese word between two digits would read as an extra value.
    "explorer.assets_of": u"/",
    "explorer.assets_showing": u"表示中",
    "explorer.core_suffix": u" (コア)",
    "explorer.feed_cer_premium": u"コア為替レート（CER）プレミアム（公開者ルールによる推定値）",
    "explorer.feeds_of": u"/",
    "explorer.feeds_scanned_suffix": u"件をスキャンしました（最初の100アセット）",
    "explorer.feeds_showing": u"表示中",
    "explorer.info_h": u"情報",
    "explorer.no_assets_match": u"「%(q)s」に一致するアセットはありません。",
    "explorer.raw_json": u"生 JSON",
    "explorer.raw_mark": u" (生値)",
    "explorer.stat_tpb": u"取引/ブロック",
    "explorer.stat_tps": u"取引/秒",
    "explorer.virtual_mark": u" (仮想)",

    # ============================================================ pool_net (23)
    "pool_net.canvas_label": (
        u"プールネットワークマップ。Enter キーで BTS を開きます。"
    ),
    "pool_net.col_a": u"アセット1",
    "pool_net.col_b": u"アセット2",
    "pool_net.col_pool": u"プール",
    "pool_net.collapse": u"折りたたむ",
    "pool_net.direct": u"BTS とペア",
    "pool_net.empty": u"この条件に一致するプールはありません。",
    "pool_net.expand": u"展開",
    "pool_net.hops": u"BTS まで %(n)s ホップ",
    # The legend heads colour-coded asset groups (what the code calls a
    # "brand"), not commercial brands, so グループ names what is on screen.
    "pool_net.legend": u"グループ",
    "pool_net.loading": u"ネットワークを読み込み中…",
    "pool_net.offline": (
        u"ネットワークを利用できません — 同梱のスケルトンを表示しています。"
        u"接続後に再試行してください。"
    ),
    "pool_net.offline_empty": (
        u"ネットワークを利用できません — スケルトンのプールがキャッシュされていません。"
    ),
    "pool_net.orphan": u"BTS から孤立",
    "pool_net.partial": (
        u"ライブ更新が不完全です — 同梱のプールを表示しています。"
    ),
    "pool_net.phys": u"物理演算",
    "pool_net.prompt": (
        u"ノードをタップするとアセット、線はタップするとプールが表示されます。"
    ),
    "pool_net.ramp": u"プール規模: 小 → 大",
    "pool_net.ready": u"%(pools)s プール · %(assets)s アセット",
    "pool_net.title": u"プールネットワーク",
    "pool_net.twin": u"プールの行（%(n)s）",
    "pool_net.twin_more": (
        u"%(n)s 件のプール中 %(shown)s 件を表示しています。"
        u"条件を絞ると表示数を減らせます。"
    ),
    "pool_net.verdict_full": u"%(pools)s プール · %(assets)s アセット",
    "pool_net.verdict_orphan": u"%(a)s と %(b)s の間に経路はありません",
    "pool_net.verdict_path": u"%(a)s は %(n)s ホップで %(b)s に到達します",
    "pool_net.verdict_star": u"%(s)s に触れるプール: %(n)s",

    # ================================================================= pool (24)
    # Both legs are interchangeable, so the field labels reuse market_net's
    # wording verbatim - the same sentence cannot mean two things.
    "pool.asset_1_field": u"アセット1（どちらの脚でも可）",
    "pool.asset_2_field": u"アセット2（どちらの脚でも可）",
    "pool.clear_btn": u"クリア",
    "pool.delete_not_empty": (
        u"空ではありません — 削除するには %(legs)s が 0 である必要があります。"
    ),
    "pool.direct_hit": u"プールを直接検索しました — ページャーは非表示です。",
    "pool.map_core_self": u"BTS は BitShares のコアトークンです",
    "pool.min_swaps": u"最小スワップ数",
    "pool.my_swaps_hint": (
        u" 上のスワップパネルから1つ実行してください — このプールの自分のスワップが"
        u"ここに表示されます。"
    ),
    "pool.no_filter_match": u"これらの条件に一致するスワップはありません。",
    "pool.stake_autofill_hint": (
        u"数量を1つ入力してください — もう一方はプールの比率で自動入力されます。"
    ),
    "pool.stake_preview_bad": u"数量を確認してください — シェアの推定値がありません。",
    "pool.stake_preview_need_both": (
        u"シェアを推定するには両方の数量を入力してください。"
    ),
    "pool.stake_preview_unavailable": u"シェアの推定値を取得できません（オフライン）。",
    "pool.stake_ratio_empty": u"プールが空です — 両方の数量を手入力してください。",
    "pool.stake_ratio_row": u"比率（スポット）",
    "pool.stake_shares_row": u"推定 LP シェア",
    "pool.swap_desk": u"スワップデスク",
    "pool.swap_mkt_preview_dash": u"マーケット手数料（プレビュー）: —",
    "pool.swap_mkt_row": u"マーケット手数料",
    # The trailing space on swap_preview is load-bearing: a number follows it.
    "pool.swap_preview": u"見積（プレビュー）: ",
    "pool.swap_preview_dash": u"見積（プレビュー）: —",
    "pool.swaps_hint": (
        u" このプールで最初の交換を行うと、スワップがここに表示されます — "
        u"上のスワップパネルから実行してください。"
    ),
    "pool.uc_action": u"操作",
    "pool.uc_title": u"続けるにはアンロックしてください",

    # ================================================================= help (61)
    "help.about_link": u"このウォレットについて",
    "help.confidence_good": u"良好",
    "help.confidence_high": u"高い",
    "help.confidence_language": u"言語",
    "help.confidence_level": u"信頼度",
    "help.confidence_moderate": u"普通 — 確認してください",
    "help.elastic": u"コミュニティインデックス（第三者提供の履歴）",
    "help.report_translation_link": u"翻訳の問題を GitHub で報告",
    "help.sitemap_sections": u"セクション",
    "help.translation_confidence_heading": u"各言語の信頼度",
    "help.topic_about-making_body": (
        u"# このウォレットの開発の記録\n"
        u"以下は当初の開発記録です — このウォレットを作ったすべてのプロンプトを、"
        u"2026年9月26日の「acquire bitshares-ui」から10月3日の issue 1 の修正まで、"
        u"構築者たちの返信とともに編集せずに残しています。\n"
        u"このウォレットが立つ基盤となる判断が記録されています: issue #3583 とその"
        u"1000時間の罠のあとに React の別のアップグレードを断念し、リリースサイクルを"
        u"持つ何にも依存しないようにしたこと。すべてのトランザクションを古いウォレットと"
        u"同じくローカルで署名し、外部に委ねなかったこと。クラシックな外観を既定とする"
        u"3つのテーマ。数は常に人間表示にし、生の整数は表示しないこと。最初のスライスから"
        u"スマートフォン優先のレイアウトにしたこと。手数料は推定せず、ライブチェーンから"
        u"読むこと。歴史として読んでください — このウォレットはそうやって作られました。\n"
        u"# 開発対話の全記録\n"
        u"やり取りを1件ずつ完全に記録したものは About ページ（#/about）にあります。"
        u"あそこの「開発対話の全記録」を開くと、すべてのやり取りを閲覧でき、キーワードで"
        u"絞り込め、?dialog=N で特定のやり取りへ直接ジャンプできます。"
    ),
    "help.topic_about-making_text": u"このウォレットを作った記録 —",
    "help.topic_about-making_title": u"このウォレットの開発の記録",
    "help.topic_assets-feed_body": (
        u"# 価格フィードの公開\n"
        u"マーケット連動アセットの決済価格はフィードデスクから公開します。"
        u"確認ダイアログには、署名の前に正確な手数料が表示されます。"
    ),
    "help.topic_assets-feed_text": (
        u"マーケット連動アセットの価格フィードを公開します。"
    ),
    "help.topic_assets-feed_title": u"価格フィードの公開",
    "help.topic_assets-issue_body": (
        u"# アセットの発行\n"
        u"管理しているアセットの新規供給は発行デスクから作成します。"
        u"金額はアセットの精度で扱われ、確認ダイアログには署名の前に正確な手数料が"
        u"表示されます。"
    ),
    "help.topic_assets-issue_text": (
        u"管理しているアセットの新規供給を発行デスクから作成します。"
    ),
    "help.topic_assets-issue_title": u"アセットの発行",
    "help.topic_backups_body": (
        u"# 早めにバックアップ、2か所へ\n"
        u"ローカルウォレットに資金を入れる前にバックアップを取ってください — "
        u"その後の運用は1つのバックアップで通常は十分ですが、自分だけがアクセスできる"
        u"安全な場所に少なくとも2つ保存してください。\n"
        u"このウォレットにバックアップファイルはありません: ブレインキーこそがバックアップで、"
        u"パスフレーズだけでは何も復元できません。単語とパスフレーズの両方がなければ"
        u"資金は失われます。パスフレーズを単語のそばに決して保管しないでください。\n"
        u"# ブレインキーがバックアップです\n"
        u"生の鍵を手で取り込んだことがない場合、ウォレット全体は1つのブレインキー"
        u"（単語の列）から決定的に導出されます。ブレインキーを書き留めれば、そのウォレットの"
        u"すべてのアカウントと資金がバックアップされます。\n"
        u"ウォレット管理画面で表示して紙に写し、デジタルなものとは別に保管します。"
        u"参照ウォレットの .bin ファイルはここでは取り込めません — ウォレットはそれを"
        u"画面に表示し、ダウンロードするファイルも存在しません。\n"
        u"# 上級: 階層的な権限\n"
        u"通常の鍵の代わりに重み付けされた複数アカウントの権限を使っている場合、"
        u"鍵のバックアップだけではアクセスを復元できないことがあります — "
        u"権限の構造そのものが重要です。\n"
        u"権限の記事を読み直し、単語だけでなく権限の設定全体を記録してください。"
    ),
    "help.topic_browser_body": (
        u"# ブランド名ではなく機能を検出します\n"
        u"このウォレットは使用したブラウザを尋ねません — 実際に必要な4つの"
        u"プラットフォーム機能を検出します: WebSocket（チェーンデータ）、"
        u"WebCrypto（キーストア）、BigInt（金額の計算）、ローカルストレージ（設定）。"
        u"表示されないことは合格です: 新しいブラウザにバナーが出ないのは、"
        u"すべてが揃っているということです。\n"
        u"# 最も多い原因: セキュアコンテキストではない\n"
        u"新しいブラウザはセキュアコンテキストでのみ WebCrypto を提供します: "
        u"https のページ、localhost、そして開いたファイルです。同じ新しいブラウザでも、"
        u"http で配信すると（たとえば LAN アドレス）、WebCrypto なしと判定されます — "
        u"ブラウザの問題ではなく、アドレスの問題です。フォルダを https または localhost で"
        u"配信するか、index.html を直接開いてください。\n"
        u"# それでも動く部分\n"
        u"閲覧は常にできます: 残高、マーケット、エクスプローラー、投票は、ウォレット機能を"
        u"使わずに公開のチェーンデータを読みます。必要なのはローカルの署名だけです。"
        u"通知を閉じるとこのマシンでは非表示になりますが、ページがブロックされることは"
        u"ありません。"
    ),
    "help.topic_browser_text": (
        u"動作するブラウザと、互換性に関する通知の意味。"
    ),
    "help.topic_browser_title": u"ブラウザ対応",
    "help.topic_community_body": (
        u"# コミュニティ\n"
        u"BitShares 周辺の人と場所 — ホームページ、コード、エクスプローラー、"
        u"フォーラム、チャット — はコミュニティページにあります。"
    ),
    "help.topic_community_text": u"BitShares 周辺のチャット、フォーラム、エクスプローラー、コード。",
    "help.topic_community_title": u"コミュニティ",
    "help.topic_htlc_text": u"支払うか返金するかのどちらかになる、ハッシュでロックされたスワップ。",
    "help.topic_menu_body": (
        u"# サイトメニュー\n"
        u"メニューこのページには、このウォレットのすべての画面がセクション別に並ぶので、"
        u"どのデスクも1タップで到達できます。"
    ),
    "help.topic_menu_text": (
        u"ナビゲーションメニューと同じ区分で並べた、このウォレットのすべてのページ。"
    ),
    "help.topic_menu_title": u"サイトメニュー",
    "help.topic_sitemap_body": SITEMAP,
    "help.topic_sitemap_text": (
        u"このウォレットのすべてのページを1ページに。メニュー項目に加えて、"
        u"メニューカードのないフローと詳細表示も載っています。"
    ),
    "help.topic_sitemap_title": u"サイトマップ",
    "help.topic_translation-limitations_body": TRANSLATION_LIMITS,
    "help.topic_translation-limitations_text": (
        u"機械で埋められた翻訳にはマーカーの印が付きます。英語の原文は1タップで表示できます。"
        u"修正のご報告をお願いします。"
    ),
    "help.topic_translation-limitations_title": u"翻訳の制限",
    "help.topic_voting_text": (
        u"ウィットネス、委員会、ワーカーに投票します — プロキシに委任することもできます。"
    ),
    "help.topic_wallets_body": (
        u"# ローカル金庫を持つ Web アプリ\n"
        u"このアプリケーションはブラウザで動作し、ネットワークへの窓口として"
        u"チェーンノードと通信します。秘密のものはすべて、ブラウザのローカル金庫に"
        u"留まります。\n"
        u"# クラウドログインはありません\n"
        u"このウォレットにユーザー名とパスワードのログインはありません: ここにある"
        u"ウォレットはすべて1つのブラウザにローカルです。新しいブラウザやコンピューターで"
        u"使うには、同じブレインキーから始めてください — 単体でどこからでも開く認証情報は"
        u"ありません。\n"
        u"# ローカルウォレット\n"
        u"ローカルウォレットは、特定した1つのブラウザの中のデータベースです。"
        u"ブレインキーを持ち越して取り込まない限り、別のコンピューターやブラウザには"
        u"ついてきません。\n"
        u"実際の資金でローカルウォレットに依存する前に、バックアップの記事を読んでください。\n"
        u"# パスワードの決まり方\n"
        u"パスワードは金庫を暗号化します。短く、他で使い回したパスワードは推測されてしまいます。"
        u"紙に書いた一意のパスフレーズは推測されません。\n"
        u"パスワードを変更するとすべてが再暗号化されます — 最初に現在のものを確認し、"
        u"立ち去る前にウォレットがアンロックできることを確かめてください。"
    ),

    # ============================================================ splash (19)
    "splash.card_dex_d": u"公開マーケットで売買します。",
    "splash.card_explore_d": u"ブロックとアカウント履歴を読みます。",
    "splash.card_pool_d": u"2つのアセットをプールして手数料の一部を獲得します。",
    "splash.card_wallet_d": u"鍵はこのデバイスにのみ保持します。",
    "splash.cards_title": u"取引、プール、探索 — ここから始めます",
    "splash.cta_exchange": u"取引所で取引する",
    "splash.hero_sub": u"あなたの鍵。あなたの資金は、チェーンの上で。",
    "splash.hero_sub2": u"マーケットは無料で閲覧できます。アンロックは署名時だけです。",
    "splash.hero_title": u"ブラウザの中の BitShares ウォレット。インストールは不要です。",
    "splash.pulse_stale": u"— 古い",
    "splash.pulse_time": u"ヘッド時刻",
    "splash.pulse_title": u"チェーンのライブ数値",
    "splash.step1_d": u"ログインは不要です — まずチェーンを閲覧しましょう。",
    "splash.step1_t": u"見て回る",
    "splash.step2_d": (
        u"ブレインキーはこのデバイスで生成されます。紙に書き写してください。"
    ),
    "splash.step2_t": u"ウォレットを作成",
    "splash.step3_d": (
        u"指値注文、流動性プール、投票 — すべてチェーン上で完結します。"
    ),
    "splash.step3_t": u"取引 / プール / 投票",
    "splash.topvol_unavailable": (
        u"トップマーケットの出来高を取得できません — 設定 → ノードを確認してください。"
    ),
    "splash.trust_keys_d": (
        u"署名はこのデバイス上でローカルに行われます。サーバーがパスワードや鍵を"
        u"見ることはありません。"
    ),

    # ================================================================= seo (26)
    # Meta descriptions: what the page shows and that reading needs no login.
    # Factual and short on purpose - a search-result snippet is not a
    # landing page, and marketing tone there would be unearned.
    "seo.desc_about": (
        u"この BitShares ウォレットについて — 鍵はローカル、登録不要、追跡なし。"
        u"自由に閲覧し、ローカルで署名します。"
    ),
    "seo.desc_account": (
        u"この BitShares アカウントを表示します — 残高、注文、履歴はチェーンから"
        u"ライブで読み取ります。ログインは不要です。"
    ),
    "seo.desc_account_net": (
        u"アカウントが誰に送金し、誰に貸し、誰から借りているかを表示します — "
        u"コミュニティインデックスから読み取ります。ログインは不要です。"
    ),
    "seo.desc_dashboard": (
        u"BitShares ダッシュボード — 残高、マーケット、チェーンの活動をひと目で。"
        u"自由に閲覧でき、鍵はデバイス上に留まります。"
    ),
    "seo.desc_explorer": (
        u"BitShares のブロック、トランザクション、アセットを探索 — "
        u"ライブのチェーンデータを、ログインなしで閲覧できます。"
    ),
    "seo.desc_help": (
        u"BitShares ウォレットのヘルプ — アカウント、取引、投票、復旧のガイド。"
        u"詰まったときはここから。"
    ),
    "seo.desc_login": (
        u"ローカルの BitShares ウォレットをアンロック — パスワード、ブレインキー、"
        u"取り込んだ鍵。鍵がデバイスから出ることはありません。"
    ),
    "seo.desc_market": (
        u"BitShares のオーダーブックで BTS を USD と取引 — ライブの買い値と売り値、"
        u"履歴。署名はデバイス上でローカルに行います。"
    ),
    "seo.desc_markets": (
        u"BitShares のオーダーブック市場を24時間出来高で並べ、任意のペアの取引デスクを"
        u"開けます。ログインは不要です。"
    ),
    "seo.desc_pools": (
        u"BitShares の流動性プールを閲覧 — ペア、残高、活動をチェーンからライブで"
        u"読み取ります。ログインは不要です。"
    ),
    "seo.desc_transfer": (
        u"BitShares のアセットを任意のアカウントへ送ります。各項目を確認してから"
        u"ローカルで署名 — 鍵がデバイスから出ることはありません。"
    ),
    "seo.desc_voting": (
        u"BitShares のウィットネス、委員会メンバー、ワーカーに投票します。"
        u"すべての投票はデバイス上でローカルに署名されます。"
    ),
    "seo.desc_xrates": (
        u"すべてのプールアセットを BTS 建て、最後のスワップ価格でも併記します。"
        u"ログインは不要です。"
    ),
    "seo.title_about": u"このウォレットについて — BitShares ウォレット",
    "seo.title_account": u"アカウント %(name)s — BitShares ウォレット",
    "seo.title_account_net": u"アカウントネットワーク — BitShares ウォレット",
    "seo.title_dashboard": u"ダッシュボード — BitShares ウォレット",
    "seo.title_explorer": u"オンチェーンエクスプローラー — BitShares ウォレット",
    "seo.title_help": u"ヘルプ — BitShares ウォレット",
    "seo.title_login": u"ログイン — BitShares ウォレット",
    "seo.title_market": u"BTS/USD 取引所 — BitShares ウォレット",
    "seo.title_markets": u"マーケット — BitShares ウォレット",
    "seo.title_pools": u"流動性プール — BitShares ウォレット",
    "seo.title_transfer": u"送金 — BitShares ウォレット",
    "seo.title_voting": u"ウィットネス投票 — BitShares ウォレット",
    "seo.title_xrates": u"クロスレート — BitShares ウォレット",

    # ================================================================ shell (9)
    # The build line renders "<rel> <a>Master</a>", so each relation phrase has
    # to read as a predicate BEFORE the branch name rather than a label after it.
    "shell.footer_ahead": u"%(n)s 件のコミットが先行",
    "shell.footer_ahead_one": u"1 件のコミットが先行",
    "shell.footer_at_build": u"ビルド %(date)s 時点",
    "shell.footer_behind": u"%(n)s 件のコミットが遅行",
    "shell.footer_behind_one": u"1 件のコミットが遅行",
    "shell.footer_dahead": u"%(n)s 先行",
    "shell.footer_dbehind": u"%(n)s 遅行",
    "shell.footer_diverged": u"乖離",
    "shell.footer_offbranch": u"Master 以外",
    "shell.footer_sync": u"同期済み",

    # ================================================================= menu (8)
    "menu.blurb_labs": u"チェーンとノードを扱うための実用ツール。",
    "menu.blurb_personal": u"チャット、アラート、あなたの設定。",
    "menu.d_account_net": u"送金の追跡",
    "menu.d_xrates": u"すべてのアセットを BTS 建てのプール価格とあわせて表示します。",
    "menu.p_account_net": u"アカウントネットワーク",
    "menu.p_xrates": u"クロスレート",
    # "Discover" (menu) and "Explore" (blockchain tabs) are two different
    # sections in English too, so they get two different Japanese names; the
    # sitemap below reuses both verbatim.
    "menu.section_explore": u"探索",
    "menu.section_labs": u"ラボ",
    "menu.section_personal": u"個人",
}

# Keys whose Japanese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from JA. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Japanese crypto UI keeps in Latin: HTLC, MSSR,
#     MCR, ID, JSON-style table labels;
#   * brands the brief pins: shell.brand, the two footer brand lines;
#   * op / Tx glue: "Op 19" and "Tx <hash>" are a label and a hash, so
#     translating the prefix would put a Japanese word in front of a hex hash;
#   * row titles that name a chain value rather than prose: explorer.id_row;
#   * feed stamps and feed-pair titles that print two raw values side by side:
#     "%(id)s @ %(ts)s", "mcr %(mcr)s; mssr %(mssr)s", "MCR / MSSR";
#   * edge cards and node cards whose every slot is a number, a symbol or an id;
#   * the pool lookup hint "symbol, 1.3.x, or pool 1.19.x", which is real
#     account/object ids and so is DATA under rule 1;
#   * the network host line, whose %(net)s is the pinned mainnet/testnet id.
KEPT_ENGLISH = {
    # ---- explorer
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.th_mssr": u"MSSR",
    "explorer.tx_prefix": u"Tx ",
    # ---- menu
    "menu.p_htlc": u"HTLC",
    # ---- pool
    "pool.share_or_pool_hint": u"symbol, 1.3.x, or pool 1.19.x",
    # ---- pool_net
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pools · %(hops)s",
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
}


if __name__ == "__main__":
    sys.exit(main())