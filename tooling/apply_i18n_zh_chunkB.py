#!/usr/bin/env python3
"""i18n zh chunk-B: fill the nine display-heavy sections zh.json still leaves in English.

Scope: ONLY the nine sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from zh.json, or one whose English master moved, is REFUSED;
  * ZH + KEPT_ENGLISH together must account for EVERY untranslated key of the
    nine sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset and
REFUSES anything outside them; this batch REFUSES everything outside help,
pool, pool_net, explorer, seo, splash, about, shell and menu. A key that
crosses the line is a reviewer's problem, never a script's silent edit.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/validate_translations.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an untranslated key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  zh punctuation no value this batch writes may carry an ASCII or
                      typographic apostrophe, an ideographic space, or a Cyrillic
                      letter. Chinese does not need any of them: the strings
                      zh.json already ships use none, and the quotes it does use
                      are the curly pair “ ” (U+201C/U+201D), which this gate does
                      not touch. Every possessive in the English masters
                      ("the asset's precision", "a pair's desk") is therefore
                      rephrased in Chinese rather than borrowed with an
                      apostrophe.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. The sweep runs file-wide, but
                      a hit OUTSIDE the nine sections is reported as PRE-EXISTING
                      and does not gate this batch: chunk-A owns those keys, and
                      an insert-only pass that repaired a neighbour would be
                      exactly the silent edit the scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                      LOAN below, or the write is refused. Chinese crypto UIs
                      keep the English word for BitShares, BTS, USD, HTLC, API,
                      LP, CER, LP shares, Same-T, GitHub, WebSocket/WebCrypto/
                      BigInt, React and the GitHub issue tracker - inventing a
                      fake transliteration instead would be worse than the
                      loanword. Three unit/placeholder suffixes ride along
                      because the Chinese sentence cannot drop them: "px" and
                      "K" in a viewport range, "x" in the 1.3.x / 1.19.x object
                      id prefix, and "bin" in the reference wallet's file
                      extension. The gate is batch-scoped on purpose: the rest of
                      zh.json already carries Latin tokens from earlier batches,
                      and re-litigating those is not this file's job.

The spellings are reused verbatim from the part of zh.json that is already
translated, so this batch reads like the rest of the dictionary instead of like
a second dictionary: 资金池, 资产, 份额, 兑换, 质押, 解押, 订单簿, 限价单, 价格,
手续费, 余额, 钱包, 节点, 权限, 提案, 见证人, 理事会, 工人, 归属, 票据, 智能币,
市场锚定资产, 用户发行资产, 喂价, 价格源, 交易台, 浏览器, 脑密钥, 区块, 精度.
Where two surfaces already meet - the burger menu and the #/help/sitemap
article - the same Chinese word is used on both, so the sitemap labels are
copied from the shipped menu.p_* values rather than re-invented.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (360px, 4K, first 100, op 1, #3583, 26 September 2026,
3 October) the translation keeps it byte-verbatim.

Markdown bodies: help, about and splash hold prose. G4 pins the line count and
the link hashes, so every body is written through md(), which joins one source
line per argument - the line count is then visible in the source instead of
being a count of backslash-n characters. In [label](#/hash) only the label is
translated; the hash stays byte-verbatim, which is what keeps the sitemap's
burger-menu coverage test and its route-resolution test passing in every
locale at once.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_zh_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_zh_chunkB.py --apply         # writes zh.json
  python3 tooling/apply_i18n_zh_chunkB.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
ZH_PATH = os.path.join(BASE, "zh.json")

# The nine sections this batch owns. Everything else belongs to chunk-A and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool", "pool_net", "explorer", "seo", "splash", "about", "shell",
    "menu",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from ZH below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live in chunk-A's settings section; the shell brands live here,
# so they are kept in the list so a drift anywhere in the file is caught.
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
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
# G9: a Latin run inside a Chinese value. A token may continue through - _ . /
# so "Same-T", "docs/vanilla-ui-dialog.md", "http" and "index.html" are one
# decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")
# G9 scoping: in-app ADDRESSES are data, exactly like a placeholder. The
# markdown destinations ("[label](#/pools)") and the bare route / deep-link
# references an article makes in prose ("(#/about)", "?dialog=N") are stripped
# before the Latin sweep so a route hash cannot be mistaken for a loanword.
# Nothing is lost: G4 fails hard if any of these bytes differs from the
# English master, so the strip hides a Latin token from a sweep, never a drift
# from the gate that owns these bytes.
LINK_DEST = re.compile(r"\]\([^)]*\)")
ROUTE_REF = re.compile(r"(?:#/|\?[A-Za-z_][A-Za-z0-9_]*=)\S*")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Chinese crypto UI prints in Latin; anything else has to be Chinese.
# Entries that no value actually uses are pruned, so the allowlist cannot rot
# into a blanket permission. Note what is NOT here and does not need to be:
# "360px" and "4K" in the viewport range, because COUNT_UNIT already strips a
# number with a unit suffix - it is data a reader compares, not prose.
LOAN = frozenset((
    # Chain names, symbols and units. BTS/USD is one token to the scanner
    # because the slash continues a Latin run, and it is a market pair.
    "BTS", "BTS/USD", "BitShares", "CER", "USD",
    # BitShares operations and UI surfaces that ship as Latin in every locale.
    "HTLC", "LP", "Same-T", "Spotlight",
    # Platform / tooling names.
    "BigInt", "GitHub", "JavaScript", "React", "WebCrypto", "WebSocket",
    # Sentence-initial acronyms and names the UI itself prints.
    "API", "ES", "ID", "Master",
    # Paths, protocols, hosts and the object-id wildcard: DATA inside a
    # translated sentence (rule 1).
    "bin", "bitshares-ui", "docs/vanilla-ui-dialog.md", "http", "https",
    "index.html", "localhost", "x",
    # The tracker noun the correction route opens.
    "issue",
))


def md(*lines):
    """Join markdown body source lines into one value.

    G4 pins a body's line count to the English master's, and paintBlock()
    splits on blank lines, so every body is written one source line per
    argument. Params: lines, one paragraph or list item each. Returns the
    joined string. Never raises; an empty call yields an empty string.
    """
    return u"\n".join(lines)


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    A middle dot is clean when it is space-separated, as it is everywhere in
    this dictionary - or when both neighbours are alphanumeric, which is
    algebraic notation (zh.json ships "x·y=k"). Anything else is a stray dot
    that will render as a different word to the reader.
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
            "line count changed: %s (en %d, zh %d)"
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


def check_zh_hygiene(batch, problems):
    """G7 + G9: apostrophes, ideographic space, Cyrillic, undeclared Latin.

    Scoped to the values THIS BATCH writes. zh.json's other sections carry
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
        # into "90天" without changing the number the reader compares against
        # the range control beside it.
        prose = COUNT_UNIT.sub("", prose)
        # In-app addresses, for the same reason (see LINK_DEST/ROUTE_REF).
        prose = LINK_DEST.sub("", prose)
        prose = ROUTE_REF.sub("", prose)
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
    zh, en = load(ZH_PATH), load(EN_PATH)
    d, e = flat(zh), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: chunk-A (or whoever wrote the
    # section) owns them, and an insert-only batch that "fixed" a neighbour
    # would be the silent edit the scope refusal exists to prevent. Only `bad`
    # — problems this batch can answer for — gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
            check_batch(e, key, d[key], bad, chars=key in ZH)
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
            if key in ZH:
                bad.append(where)
            else:
                pre.append(where)
    check_zh_hygiene(ZH, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(ZH) if d.get(k) == e.get(k)]
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
        and k not in ZH and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(ZH) - len(same), len(ZH)))
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
    meta = zh.get("_meta", {})
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
    raw = open(ZH_PATH, encoding="utf-8").read()
    zh = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(zh, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: zh.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(zh))
    before_meta = json.dumps(zh["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(ZH.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in zh.json: %s" % key)
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
        deep_set(zh, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(ZH) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (ZH and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(ZH) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in zh.json: %s" % key)
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

    check_zh_hygiene(ZH, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(zh)
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
    meta = zh["_meta"]
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
    added = sorted(k for k in ZH
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

    print("zh chunk-B: %d planned, %d differ from en, %d intentionally identical"
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

    with open(ZH_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(zh, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/zh.json")
    return 0


ZH = {
    # ============================================================ about (19)
    # The build-dialog widget. 完整构建对话框 is the same phrase in the about
    # help article's pointer, so the two surfaces name one section.
    "about.dlg_heading": u"完整构建对话框",
    "about.dlg_heading_c": u"完整构建对话框（%(total)s 条）",
    # An archive entry with no reply is a fact about the transcript, not an
    # error: the next prompt simply followed. Say so plainly.
    "about.dlg_no_reply": u"未记录回复——下一条提示紧随其后。",
    # The .md path is DATA inside the sentence: the file name is byte-verbatim.
    "about.dlg_noscript": (
        u"此归档需要 JavaScript；同样的文本位于源码仓库的 "
        u"docs/vanilla-ui-dialog.md。"
    ),
    "about.dlg_search_clear": u"清除",
    "about.dlg_search_ph": u"筛选对话…",
    "about.dlg_showing": u"显示",
    "about.dlg_showing_c": u"显示 %(shown)s / %(total)s",
    "about.dlg_unavailable": u"构建对话框归档不可用。",
    "about.hero_lede": (
        u"面向 BitShares 区块链的钱包——市场、账户、治理与浏览器——"
        u"以纯网页文件的形式运行。没有框架，没有安装程序，"
        u"也不存在我们的账户。您的密钥永不离开此浏览器。"
    ),
    # One paragraph, no line breaks in the English either, so one string here.
    "about.making_body": (
        u"以下是最初的构建记录：创建本钱包的每一次提示，从 2026 年 9 月 26 日的"
        u"“获取 bitshares-ui”到 10 月 3 日修复第 1 号问题，以及构建者的回复"
        u"——原样保留，未作删改。其中记录了本钱包赖以成立的决策：在问题 #3583 "
        u"及其上千小时的陷阱之后放弃再次 React 升级，使本钱包不依赖任何有发布"
        u"周期的东西；像旧钱包一样在本地签名每一笔交易，而不是外包出去；"
        u"三套主题，并以经典外观为默认；数字以人类可读的方式呈现，"
        u"绝不显示链上原始整数；布局从第一个切片起就以手机为先；"
        u"手续费从实时链上读取，绝不估算。请把它当作历史来读："
        u"本钱包就是这样建起来的。"
    ),
    "about.making_title": u"本钱包的构建过程",
    "about.s2_title": u"在真实订单簿上交易",
    "about.s3_body": (
        u"它所取代的那个钱包，死在一百个停滞的依赖和无人能复现的工具链之下。"
        u"本钱包为避免依赖发布周期而构建：没有框架，没有包管理器，"
        u"没有构建步骤——十年之后仍能在浏览器中运行的最简之物。"
    ),
    "about.s3_title": u"多年无需更新，仍可运行",
    "about.s4_body": (
        u"回来的用户会立刻感到熟悉——与经典钱包相同的页面、面板与用词——"
        u"同时余额、订单簿与连接状态就地实时更新。跨市场、账户与资产的宽容搜索，"
        u"三套主题，以及从 360px 手机到 4K 交易台都能使用的布局。"
    ),
    "about.s4_title": u"相同的页面，实时的更新",
    # "you never see them" is the whole promise: the chain's integers stop at
    # the format layer (AGENTS.md 3.5), and this sentence is where a reader
    # learns that.
    "about.s5_body": (
        u"链上说的是整数，您永远看不到它们。每一笔金额都落在其资产的小数位上，"
        u"每一个百分比都是真实数值，每一笔手续费都在您签名前从实时链上读取。"
    ),

    # ========================================================= explorer (17)
    "explorer.assets_mode_all": u"全部",
    # 智能币 is the shipped zh word for a smartcoin (help, market, pool).
    "explorer.assets_mode_market": u"智能币",
    "explorer.assets_mode_prediction": u"预测类",
    # 用户发行资产 is the shipped article title; the mode chip is its stem.
    "explorer.assets_mode_user": u"用户发行",
    # A count glue string, like the shipped explorer.markets_of: the counts
    # around it are data, and a Chinese "共" between two numbers reads worse.
    "explorer.assets_of": u"/",
    "explorer.assets_showing": u"显示",
    "explorer.feed_cer_premium": (
        u"核心汇率（CER）溢价（按发布者规则估算）"
    ),
    # CER is the acronym asset.cer_row already carries; the full label is
    # asset.cer_row's own wording.
    "explorer.feeds_of": u"/",
    # "first 100" is a chain-side cap, kept verbatim with the parenthetical
    # shape the English uses.
    "explorer.feeds_scanned_suffix": u"已扫描（前 100 个资产）",
    "explorer.feeds_showing": u"显示",
    # Curly quotes, the pair zh.json already uses for quoting a user's string.
    "explorer.no_assets_match": u"没有资产匹配“%(q)s”。",
    "explorer.stat_tpb": u"交易/区块",
    "explorer.stat_tps": u"交易/秒",

    # ============================================================= help (37)
    "help.about_link": u"关于本钱包",
    "help.confidence_good": u"良好",
    "help.confidence_high": u"高",
    "help.confidence_language": u"语言",
    "help.confidence_level": u"置信度",
    "help.confidence_moderate": u"中等——请自行核对",
    "help.elastic": u"社区索引（第三方历史）",
    "help.report_translation_link": u"在 GitHub 上报告翻译问题",
    # aria-label for the sitemap section nav, whose button labels come from
    # the body's own "# " headings, so this one word names all nine.
    "help.sitemap_sections": u"章节",
    # The honesty article. It is the one page whose subject IS its own
    # unread status, so it is translated plainly rather than left as a stub:
    # a Chinese reader who cannot read the Chinese warning cannot be warned.
    # Every " *" stays a literal asterisk - it is the chip this page explains -
    # and the 22 blank-line-separated source lines below match the master
    # line for line (G4).
    "help.topic_translation-limitations_body": md(
        u"标为机器填充的翻译由机器写成。没有人读过它、"
        u"核对它是否与英文含义一致——正因如此，本钱包页眉中"
        u"除英文外的每种语言都带有标记徽标。英文是其余语言翻译所依据的原文，"
        u"因此不带标记。",
        u"",
        u"# 行上的 * 意味着什么",
        u"签名行上的 * 同时表示两件事：措辞由机器填充，"
        u"且原始英文触手可及。点一下 *，英文就会显示在该行下方，"
        u"与本钱包英文母本中存储的完全一致——也就是其余语言翻译所依据的原文，"
        u"而不是它的转述。",
        u"",
        u"标记跟随的是整行，而不是行内的词语。一个 * 标记一整行翻译文本，"
        u"钱包按固定规则挑选这些行：签名、不可逆操作或恢复类页面上的每一行"
        u"——但有长度上限，因为长段落由本文说明——"
        u"再加上任何页面中英文原文带有危险措辞的行。因此，"
        u"只写出 ID 或金额的行仍会带标记（例如转账的收款方字段），"
        u"而提到 ID 的长段落则不会。裸露的链上数值"
        u"——单元格里的金额、列中的 ID、资产符号"
        u"——根本不算翻译行，因此永远不带标记："
        u"它背后没有可比的英文措辞。",
        u"",
        u"# 置信等级的含义",
        u"本钱包提供的每种语言都有一个评级，列于下表。"
        u"高表示措辞紧贴英文、读起来自然。良好表示可用，"
        u"但个别短语可能仍显生硬。中等表示请当作草稿阅读，"
        u"依赖它之前先核对英文。",
        u"",
        u"以下每个评级都是写出这些字符串的机器给自己打的分；"
        u"没有独立第三方审计过。评级描述的是迄今已核查的内容，"
        u"且针对整种语言而非逐行。英文本身是基准："
        u"它由人工撰写，其余语言都由它翻译而来。",
        u"",
        u"# 如何更正一条字符串",
        u"更正从一份报告开始。请说明该行属于哪种语言，"
        u"给出该行披露的键，粘贴它本应表达的英文，"
        u"并建议您希望使用的措辞。",
        u"",
        u"- 每行一份报告，更正才好落地。",
        u"- 请优先报告签名页面：确认对话框上的错句代价最高。",
        u"- 使用本文末尾的链接。它会在本项目的追踪器上打开一个"
        u"已标注翻译标签的 issue，无需重复填写任何内容。",
        u"",
        u"# 更正是走向人工审阅的唯一途径",
        u"除此之外，没有任何东西能把字符串移出机器填充状态："
        u"使用人数、第二台机器的认同、翻译记忆都不行。"
        u"一条字符串在某个人用母语读过并认可后，即为人工审阅；"
        u"一行文本只有对真正被核查的那种语言才算人工审阅。",
        u"",
        u"在此之前，标记保持原位。没人读过的翻译胜过完全没有翻译，"
        u"但它与有人为之背书的翻译不是一回事。",
    ),
    "help.topic_translation-limitations_text": (
        u"机器填充的翻译均有标记；英文原文始终触手可及。"
        u"欢迎帮我们修正某一行的译文。"
    ),
    "help.topic_translation-limitations_title": u"翻译局限",
    "help.translation_confidence_heading": u"各语言的置信程度",
    # The About-page build story. The 5 source lines match the master's 4
    # newlines (G4); the one in-app link (#/about) and the ?dialog=N deep link
    # are DATA and stay byte-verbatim, while the two curly-quoted section
    # names follow about.making_title and about.dlg_heading.
    "help.topic_about-making_body": md(
        u"# 本钱包的构建过程",
        u"以下是最初的构建记录：创建本钱包的每一次提示，"
        u"从 2026 年 9 月 26 日的“获取 bitshares-ui”"
        u"到 10 月 3 日修复第 1 号问题，以及构建者的回复"
        u"——原样保留，未作删改。",
        u"其中记录了本钱包赖以成立的决策：在问题 #3583 "
        u"及其上千小时的陷阱之后放弃再次 React 升级，"
        u"使本钱包不依赖任何有发布周期的东西；"
        u"像旧钱包一样在本地签名每一笔交易，而不是外包出去；"
        u"三套主题，并以经典外观为默认；数字以人类可读的方式呈现，"
        u"绝不显示链上原始整数；布局从第一个切片起就以手机为先；"
        u"手续费从实时链上读取，绝不估算。请把它当作历史来读："
        u"本钱包就是这样建起来的。",
        u"# 完整构建对话框归档",
        u"完整的逐轮记录在“关于”页面（#/about）。"
        u"展开那里的“完整构建对话框”一节，即可浏览全部对话、"
        u"按关键词筛选，或用 ?dialog=N 直接链接到某一轮。",
    ),
    "help.topic_about-making_text": u"本钱包背后的构建故事——",
    "help.topic_about-making_title": u"本钱包的构建过程",
    "help.topic_api-lab_title": u"API 实验室",
    "help.topic_assets-feed_body": md(
        u"# 发布喂价",
        u"在喂价工作台发布市场锚定资产的结算价；"
        u"确认对话框会在您签名前显示确切手续费。",
    ),
    "help.topic_assets-feed_text": u"为您负责喂价的市场锚定资产发布价格喂价。",
    "help.topic_assets-feed_title": u"发布喂价",
    "help.topic_assets-issue_body": md(
        u"# 发行资产",
        u"在发行工作台为您的账户所控制的资产创建新供应量；"
        u"金额按该资产的精度计算，"
        u"确认对话框会在您签名前显示确切手续费。",
    ),
    "help.topic_assets-issue_text": (
        u"在发行工作台铸造您所控制资产的新供应量。"
    ),
    "help.topic_assets-issue_title": u"发行资产",
    "help.topic_backups_body": md(
        u"# 及早备份，备份两份",
        u"在给本地钱包充值之前先做备份——往后一份备份通常就够，"
        u"但请把它放在至少两个只有您能接触到的安全地点。",
        u"本钱包没有备份文件：脑密钥本身就是备份，"
        u"仅凭口令恢复不了任何东西。单词与口令缺一不可，"
        u"否则资金就没了。切勿把口令与单词放在一起。",
        u"# 脑密钥就是备份",
        u"如果您从未手动导入原始密钥，整个钱包都确定性地由一个脑密钥"
        u"——一串单词——推导而来。抄下脑密钥，"
        u"就等于备份了该钱包中的每个账户与每笔资金。",
        u"在钱包管理器中查看它并抄到纸上，与任何数字设备分开存放。"
        u"此处无法导入参考钱包的 .bin 文件"
        u"——钱包会在屏幕上说明这一点，也不存在文件下载。",
        u"# 进阶：分层权限",
        u"如果您用的是加权多账户权限而非普通密钥，"
        u"仅备份密钥可能无法恢复访问——权限结构本身同样重要。",
        u"请重读“权限”一文，记录完整的权限设置，而不只是那串单词。",
    ),
    "help.topic_browser_body": md(
        u"# 检测功能特性，而非品牌名称",
        u"本钱包从不询问您使用哪个浏览器"
        u"——它只探测自己真正需要的四项平台特性："
        u"WebSocket（链上数据）、WebCrypto（密钥库）、"
        u"BigInt（金额运算）以及本地存储（设置）。"
        u"没有提示即为通过：现代浏览器上不出现横幅，就说明功能齐备。",
        u"# 最常见的原因：不安全上下文",
        u"现代浏览器只在安全上下文中提供 WebCrypto：https 页面、"
        u"localhost，以及直接打开的文件。同样是最新的浏览器，"
        u"若通过普通 http 提供（例如局域网地址），"
        u"就会报告缺少 WebCrypto——浏览器没问题，地址有问题。"
        u"请通过 https 或 localhost 提供该文件夹，或直接打开 index.html。",
        u"# 仍可正常使用的部分",
        u"浏览始终可用：余额、市场、浏览器与投票只读取公开链上数据，"
        u"无需任何钱包功能。只有本地签名才需要缺失的那一项。"
        u"关闭提示只是在本机隐藏它，绝不会阻挡任何页面。",
    ),
    "help.topic_browser_text": (
        u"哪些浏览器能运行本钱包，以及兼容性提示的含义。"
    ),
    "help.topic_browser_title": u"浏览器支持",
    "help.topic_community_body": md(
        u"# 社区",
        u"BitShares 周边的人与地——官网、代码、区块浏览器、"
        u"论坛与聊天——都在社区页。",
    ),
    "help.topic_community_text": (
        u"BitShares 周边的聊天、论坛、区块浏览器与代码。"
    ),
    "help.topic_community_title": u"社区",
    "help.topic_es-lab_title": u"ES 实验室",
    "help.topic_htlc_text": u"哈希锁定的互换：要么付款，要么退款。",
    "help.topic_menu_body": md(
        u"# 站点菜单",
        u"菜单页面按分组列出本钱包的每个界面，任何操作台都触手可及。",
    ),
    "help.topic_menu_text": (
        u"本钱包的每个页面，按导航菜单的分组方式排列。"
    ),
    "help.topic_menu_title": u"站点菜单",
    # The sitemap. All 83 source lines are present and in English order (G4),
    # and every "[label](#/hash)" keeps its hash byte-verbatim so the
    # burger-menu coverage and route-resolution tests hold in this locale too.
    # The labels are the SHIPPED menu.p_* / menu.section_* values, not fresh
    # wording: the article and the burger menu name a page identically. The
    # two prose lines and the closing one name 无菜单卡页面 in the same words
    # as the heading they point at.
    "help.topic_sitemap_body": md(
        u"本钱包的每个页面，按汉堡菜单的分组方式排列。"
        u"凡带链接的都可直接打开；“无菜单卡页面”下列出的详情视图"
        u"则从其上级页面进入。",
        u"# 钱包",
        u"- [仪表盘](#/)",
        u"- [我的账户](#/account/me)",
        u"- [账户](#/accounts)",
        u"- [转账](#/transfer)",
        u"- [发票](#/invoice)",
        u"- [归属](#/vesting)",
        u"- [钱包](#/wallet)",
        u"- [修改钱包密码](#/wallet/password)",
        u"- [创建钱包（脑密钥）](#/create-wallet-brainkey)",
        u"- [导入现有账户](#/existing-account)",
        u"- [注册新账户](#/create-account)",
        u"- [登录](#/login)",
        u"- [注册](#/registration)",
        u"- [推荐](#/referrals)",
        u"# 交易",
        u"- [交易所](#/markets)",
        u"- [闪兑](#/instant-trade)",
        u"- [流动性资金池](#/pools)",
        u"- [交叉汇率](#/cross-rates)",
        u"- [借币](#/borrow)",
        u"- [易货](#/barter)",
        u"- [充值 / 提现](#/deposit-withdraw)",
        u"- [Same-T 基金](#/samet)",
        u"- [Spotlight](#/spotlight)",
        u"# 收益与保障",
        u"- [信用借贷](#/credit-offer)",
        u"- [直接扣款](#/direct-debit)",
        u"- [HTLC](#/htlc)",
        u"- [票据](#/tickets)",
        u"- [空投](#/airdrop)",
        u"- [自定义权限](#/authorities)",
        u"- [账户名单](#/lists)",
        u"# 治理",
        u"- [投票](#/voting)",
        u"- [提案](#/proposals)",
        u"- [创建工人](#/create-worker)",
        u"- [预测市场](#/prediction)",
        u"# 发现",
        u"- [浏览](#/explorer)",
        u"- [资产](#/assets)",
        u"- [创建资产](#/assets/create)",
        u"- [发行资产](#/assets/issue)",
        u"- [发布喂价](#/assets/feed)",
        u"- [网络手续费](#/explorer/fees)",
        u"- [操作](#/ops)",
        u"- [热门操作](#/top-ops)",
        u"- [新闻](#/news)",
        u"# 链上浏览器",
        u"- [浏览（区块链）](#/explorer)",
        u"- [资产](#/explorer/assets)",
        u"- [资金池](#/explorer/pools)",
        u"- [账户](#/explorer/accounts)",
        u"- [见证人](#/explorer/witnesses)",
        u"- [理事会](#/explorer/committee)",
        u"- [市场](#/explorer/markets)",
        u"- [手续费](#/explorer/fees)",
        u"- [价格源](#/explorer/feeds)",
        u"# 实验室",
        u"- [API 实验室](#/api-lab)",
        u"- [ES 实验室](#/es-lab)",
        u"- [交易构建器](#/txbuilder)",
        u"- [账户网络图](#/account-network)",
        u"# 个人",
        u"- [聊天室](#/trollbox)",
        u"- [收藏](#/favourites)",
        u"- [价格提醒](#/alerts)",
        u"- [帮助](#/help)",
        u"- [翻译局限](#/help/translation-limitations)",
        u"- [关于](#/about)",
        u"- [社区](#/community)",
        u"- [设置](#/settings)",
        u"# 无菜单卡页面",
        u"注册的各种路径、账户与市场操作台，以及详情视图，"
        u"均可从上述页面或钱包内其他链接进入。",
        u"- [本地注册](#/registration/local)",
        u"- [云端注册](#/registration/cloud)",
        u"- [账户页面示例](#/account/committee-account)",
        u"- [市场交易台示例](#/market/BTS_USD)",
        u"- [资产页面示例](#/asset/BTS)",
        u"- [资金池交易台示例](#/pools/1.19.66)",
        u"- [菜单总览](#/menu)",
        u"某个信用报价、交易、提案、区块、交易记录、HTLC、预测市场、"
        u"转账收款方、发票、网关、设置标签、浏览器标签或帮助文章的详情视图，"
        u"均从其上级页面打开，并在地址中带一个 ID 或名称。",
    ),
    "help.topic_sitemap_text": (
        u"本钱包的所有页面集中一页：每个菜单页面，"
        u"以及没有菜单卡片的流程与详情视图。"
    ),
    "help.topic_sitemap_title": u"站点地图",
    "help.topic_voting_text": (
        u"为见证人、理事会、工人投票——也可交给代理。"
    ),
    "help.topic_wallets_body": md(
        u"# 带本地保险库的网页应用",
        u"本应用在您的浏览器中运行，并通过链节点作为进入网络的网关。"
        u"所有机密都留在您浏览器的本地保险库中。",
        u"# 没有云端登录",
        u"本钱包没有用户名加密码的登录：这里的每个钱包"
        u"都只存在于某一个浏览器中。要在新的浏览器或电脑上使用您的账户，"
        u"请从同一个脑密钥开始——不存在任何能自行打开它的凭据。",
        u"# 本地钱包",
        u"本地钱包是某个特定浏览器内部的一个数据库。"
        u"除非您把脑密钥带过去并导入，"
        u"否则它不会跟随您到另一台电脑或另一个浏览器。",
        u"在用本地钱包存放真实资金之前，请先阅读“备份”一文。",
        u"# 口令纪律",
        u"口令用于加密保险库。短口令或重复使用的口令挡不住猜测；"
        u"写在纸上的唯一口令则不然。",
        u"修改口令会重新加密全部内容——请先核对当前口令，"
        u"再确认钱包仍能解锁，然后才离开。",
    ),

    # ============================================================= menu (11)
    "menu.blurb_labs": u"面向链与节点工作的得力工具。",
    "menu.blurb_personal": u"聊天、提醒与您的设置。",
    # 资金流 is the shipped account_net word for value movement, so the blurb
    # names the graph's subject the way the graph's own legend does.
    "menu.d_account_net": u"追踪资金流",
    "menu.d_xrates": u"每个资产按资金池价格折算为 BTS 等单位。",
    "menu.p_account_net": u"账户网络图",
    "menu.p_xrates": u"交叉汇率",
    "menu.section_explore": u"发现",
    "menu.section_labs": u"实验室",
    "menu.section_personal": u"个人",

    # ============================================== pool + pool_net (48)
    "pool.asset_1_field": u"资产 1（任意一端）",
    "pool.asset_2_field": u"资产 2（任意一端）",
    "pool.clear_btn": u"清除",
    "pool.delete_not_empty": u"非空——删除前 %(legs)s 必须为 0。",
    "pool.direct_hit": u"直接查找资金池——已隐藏分页。",
    "pool.map_core_self": u"BTS 是 BitShares 的核心代币",
    "pool.min_swaps": u"最少兑换",
    "pool.my_swaps_hint": (
        u" 请在上方的兑换面板发起一笔——您在此资金池的兑换将列在这里。"
    ),
    "pool.no_filter_match": u"没有兑换符合这些筛选条件。",
    "pool.share_or_pool_hint": u"符号、1.3.x 或 1.19.x 资金池",
    "pool.stake_autofill_hint": (
        u"输入一个数量——另一侧按资金池比率自动填充。"
    ),
    "pool.stake_preview_bad": u"请核对数量——无法估算份额。",
    "pool.stake_preview_need_both": u"请输入两个数量以估算份额。",
    "pool.stake_preview_unavailable": u"份额估算不可用（离线）。",
    "pool.stake_ratio_empty": u"资金池为空——请手动输入两个数量。",
    "pool.stake_ratio_row": u"比率（现价）",
    "pool.stake_shares_row": u"估算 LP 份额",
    "pool.swap_desk": u"兑换交易台",
    "pool.swap_mkt_preview_dash": u"市场手续费（预览）：—",
    "pool.swap_mkt_row": u"市场手续费",
    # The trailing space is load-bearing: the quoted amount follows it.
    "pool.swap_preview": u"报价（预览）： ",
    "pool.swap_preview_dash": u"报价（预览）：—",
    # The leading space is load-bearing: the table's empty-state sentence
    # follows it, exactly as pool.owned_hint and pool.depth_hint already do.
    "pool.swaps_hint": (
        u" 此资金池发生首次兑换后即显示兑换记录"
        u"——请在上方的兑换面板发起一笔。"
    ),
    "pool.uc_action": u"操作",
    "pool.uc_title": u"解锁以继续",
    "pool_net.canvas_label": u"资金池网络图。按回车打开 BTS。",
    "pool_net.col_a": u"资产 1",
    "pool_net.col_b": u"资产 2",
    "pool_net.col_pool": u"资金池",
    "pool_net.collapse": u"收起",
    "pool_net.direct": u"与 BTS 配对",
    "pool_net.empty": u"没有资金池符合此筛选。",
    "pool_net.expand": u"展开",
    "pool_net.hops": u"%(n)s 跳到 BTS",
    # The legend groups nodes by ISSUER/exchange brand, so 品牌 is the word.
    "pool_net.legend": u"品牌",
    "pool_net.loading": u"正在加载网络…",
    # Same shape as the shipped market_net.node_card: full-width parens around
    # the id, then space-separated middle dots (G8).
    "pool_net.node_card": (
        u"%(sym)s（%(id)s） · %(n)s 个资金池 · %(hops)s"
    ),
    "pool_net.offline": (
        u"网络不可用——显示的是内置骨架数据。连接后请重试。"
    ),
    "pool_net.offline_empty": u"网络不可用——未缓存任何骨架资金池。",
    "pool_net.orphan": u"已与 BTS 断开",
    "pool_net.partial": u"实时更新不完整——显示的是内置资金池数据。",
    "pool_net.phys": u"物理",
    "pool_net.prompt": u"点击节点查看资产，点击连线查看资金池。",
    "pool_net.ramp": u"资金池规模：小 → 大",
    "pool_net.ready": u"%(pools)s 个资金池 · %(assets)s 个资产",
    "pool_net.title": u"资金池网络图",
    "pool_net.twin": u"资金池行（%(n)s）",
    "pool_net.twin_more": (
        u"显示 %(n)s 个资金池中的 %(shown)s 个——请缩小筛选范围。"
    ),
    "pool_net.verdict_full": u"%(pools)s 个资金池 · %(assets)s 个资产",
    "pool_net.verdict_orphan": u"%(a)s 与 %(b)s 之间没有路径",
    "pool_net.verdict_path": u"%(a)s 可在 %(n)s 跳内到达 %(b)s",
    "pool_net.verdict_star": u"涉及 %(s)s 的资金池：%(n)s",

    # =============================================================== seo (26)
    # Meta titles and descriptions: short and factual, no claims the page does
    # not make. "BitShares Wallet" is the product name on every page title, so
    # it is 钱包 rather than a transliteration; BTS/USD stays byte-verbatim.
    "seo.desc_about": (
        u"关于本 BitShares 钱包——本地密钥，无需注册，不做跟踪。"
        u"可自由浏览，本地签名。"
    ),
    "seo.desc_account": (
        u"查看此 BitShares 账户——余额、订单与历史实时读自链上。无需登录。"
    ),
    "seo.desc_account_net": (
        u"绘制某账户向谁转账、向谁放贷、从谁借入的网络图"
        u"——数据读自社区索引。无需登录。"
    ),
    "seo.desc_dashboard": (
        u"BitShares 仪表盘——余额、市场与链上动态一览。"
        u"可自由浏览；密钥留在您的设备上。"
    ),
    "seo.desc_explorer": (
        u"浏览 BitShares 的区块、交易与资产——实时链上数据，无需登录即可查看。"
    ),
    "seo.desc_help": (
        u"BitShares 钱包帮助——账户、交易、投票与恢复的指南。遇到困难请从这里开始。"
    ),
    "seo.desc_login": (
        u"解锁您本地的 BitShares 钱包——口令、脑密钥或导入的密钥。"
        u"密钥永不离开本设备。"
    ),
    "seo.desc_market": (
        u"在 BitShares 订单簿上用 BTS 兑换 USD"
        u"——实时买卖盘与历史，在您的设备本地签名。"
    ),
    "seo.desc_markets": (
        u"按 24 小时成交量浏览 BitShares 订单簿市场，"
        u"打开任意交易对的交易台。无需登录。"
    ),
    "seo.desc_pools": (
        u"浏览 BitShares 流动性资金池——交易对、余额与动态实时读自链上。"
        u"无需登录。"
    ),
    "seo.desc_transfer": (
        u"向任意账户发送 BitShares 资产。逐项复核后在本地签名"
        u"——密钥永不离开您的设备。"
    ),
    "seo.desc_voting": (
        u"为 BitShares 见证人、理事会成员与工人投票。"
        u"每一张选票都在您的设备本地签名。"
    ),
    "seo.desc_xrates": (
        u"每个资金池资产按最近一次兑换价格折算为 BTS 等单位。无需登录。"
    ),
    "seo.title_about": u"关于 — BitShares 钱包",
    "seo.title_account": u"账户 %(name)s — BitShares 钱包",
    "seo.title_account_net": u"账户网络图 — BitShares 钱包",
    "seo.title_dashboard": u"仪表盘 — BitShares 钱包",
    "seo.title_explorer": u"区块链浏览器 — BitShares 钱包",
    "seo.title_help": u"帮助 — BitShares 钱包",
    "seo.title_login": u"登录 — BitShares 钱包",
    "seo.title_market": u"BTS/USD 交易所 — BitShares 钱包",
    "seo.title_markets": u"市场 — BitShares 钱包",
    "seo.title_pools": u"流动性资金池 — BitShares 钱包",
    "seo.title_transfer": u"转账 — BitShares 钱包",
    "seo.title_voting": u"见证人投票 — BitShares 钱包",
    "seo.title_xrates": u"交叉汇率 — BitShares 钱包",

    # ============================================================ shell (13)
    # Footer-left commit relation. The "of" in "N commits ahead of" is the
    # Master link the caller appends, so these read as a prefix.
    "shell.footer_ahead": u"%(n)s 个提交领先于",
    "shell.footer_ahead_one": u"1 个提交领先于",
    "shell.footer_at_build": u"构建于 %(date)s",
    "shell.footer_behind": u"落后 %(n)s 个提交",
    "shell.footer_behind_one": u"落后 1 个提交",
    "shell.footer_dahead": u"领先 %(n)s",
    "shell.footer_dbehind": u"落后 %(n)s",
    "shell.footer_diverged": u"已分叉（偏离）",
    # Master is the upstream branch name: data, kept in Latin.
    "shell.footer_offbranch": u"不在 Master 上",
    "shell.footer_sync": u"与……同步",
    "shell.report": u"报告",

    # =========================================================== splash (22)
    "splash.card_dex_d": u"在开放市场买卖。",
    "splash.card_explore_d": u"查看区块与账户历史。",
    "splash.card_pool_d": u"提供两种资产的流动性，赚取分成。",
    "splash.card_wallet_d": u"密钥只保存在本设备。",
    "splash.cards_title": u"交易、资金池、浏览——从这里开始",
    "splash.cta_exchange": u"前往交易所交易",
    "splash.hero_sub": u"您的密钥，您的资金，都在链上。",
    "splash.hero_sub2": u"浏览市场免费。只有签名时才需解锁。",
    "splash.hero_title": (
        u"浏览器中的 BitShares 钱包——无需安装任何东西。"
    ),
    # The leading glyph is the same em dash the stat cards print for a missing
    # value; only the word changes.
    "splash.pulse_stale": u"— 已过期",
    "splash.pulse_time": u"头区块时间",
    "splash.pulse_title": u"实时链上数字",
    "splash.step1_d": u"无需登录——先浏览链上数据。",
    "splash.step1_t": u"先逛一逛",
    "splash.step2_d": u"脑密钥在本设备上生成。请抄写到纸上。",
    "splash.step2_t": u"创建钱包",
    "splash.step3_d": u"限价单、流动性资金池与选票——全都在链上。",
    "splash.step3_t": u"交易 / 资金池 / 投票",
    "splash.topvol_unavailable": (
        u"成交额最高的市场数据离线——请检查“设置 → 节点”。"
    ),
    "splash.trust_keys_d": (
        u"签名在本设备的本地完成。任何服务器都不会看到密码或密钥。"
    ),
}

# Keys whose Chinese value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from ZH. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Chinese crypto UI keeps in Latin: HTLC, MCR,
#     MSSR, Spotlight (the four zh.json locales that finished these sections
#     before us also left every one of them in Latin);
#   * brands, pinned by rule 1 and by tooling/validate_translations.py:
#     BitShares, BITSHARES, BITSHARES VANILLA UI;
#   * pure data a table cell or a card prints: "%(id)s @ %(ts)s",
#     "MCR / MSSR", "MSSR", "ID", "%(net)s - %(host)s" (both substitutions are
#     themselves pinned network ids / hostnames), and the two edge-card glue
#     strings whose middle-dot separators and balance amounts are data.
KEPT_ENGLISH = {
    # ---- explorer
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.th_mssr": u"MSSR",
    # ---- help
    "help.topic_spotlight_title": u"Spotlight",
    # ---- menu
    "menu.p_htlc": u"HTLC",
    "menu.p_spotlight": u"Spotlight",
    # ---- pool_net
    "pool_net.edge_card": (
        u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s"
    ),
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
}


if __name__ == "__main__":
    sys.exit(main())
