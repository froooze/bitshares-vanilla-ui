#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ja chunk-C: fill the LAST Japanese batch - the 162 signing/UX strings
ja.json still leaves in English, and declare the 55 keys that stay English on
purpose. This is the closing chunk: after it, every key of ja.json is either
translated or listed in KEPT_ENGLISH below, and that is PROVED, not assumed.

Scope: the explicit key list in JA plus the explicit list in KEPT_ENGLISH. The
script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ja.json, or one whose English master moved, is REFUSED;
  * JA + KEPT_ENGLISH together must account for EVERY key of ja.json that still
    equals English, so a forgotten string is a refusal, never a silent English.

It is the Japanese sibling of tooling/apply_i18n_ja_chunkA/B.py and keeps their
gates one for one (chunkA owns the six desk sections and chunkB the nine tail
sections; each refuses keys outside its own set, and this batch owns what they
both left, so it is scoped by key rather than by section). It is also the ja
sibling of tooling/apply_i18n_es_chunkC.py, the batch that did the same job for
Spanish, and inherits its SAFETY POSTURE: every string here is read BEFORE a
user authorizes a transaction, so where a terse Japanese rendering could lose
an amount, a direction, an irreversibility or a permission, the fuller polite
form wins over the more idiomatic short one.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                     network/theme/dash/placeholder tokens stay byte-verbatim
                     (the same list tooling/check_i18n.py and
                     tooling/validate_translations.py read);
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
  G7  ja punctuation no value this batch writes may carry an ASCII or
                     typographic apostrophe, an ideographic space (U+3000), or a
                     Cyrillic letter. Japanese quotes a button with 「」 and
                     does not apostrophise. The English masters DO apostrophise
                     ("both sides' transfers", "another account's vote slate"),
                     so those possessives are rephrased rather than carried
                     over - 双方, 他のアカウントの.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                     locale - except inside an algebraic notation where both
                     neighbours are alphanumeric. That one exception is
                     load-bearing: ja.json already ships "x*y=k"-style and
                     "· 有効期限 " neighbours outside this batch. The sweep
                     runs file-wide; a hit outside this batch is reported as
                     PRE-EXISTING and does not gate, because repairing a
                     neighbour here would be the silent edit the insert-only
                     scope refusal exists to forbid.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                     LOAN below, or the write is refused. A Japanese crypto UI
                     prints DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy,
                     Smartcoin, Pool and Brainkey in Latin exactly as a Chinese
                     one does - inventing a fake katakana transliteration
                     instead would be worse than the loanword. Markdown link
                     targets, quoted routes (#/account/me), %(name)s
                     interpolations and count-with-unit literals (90d, 24h,
                     360px) are stripped before the sweep: those are rule-1
                     DATA, and G1/G4 already prove they survived. The gate is
                     batch-scoped on purpose: the rest of ja.json already
                     carries hundreds of distinct Latin tokens from earlier
                     batches.

Register: the 3,700+ strings ja.json already ships are POLITE (です/ます) -
"残高を読み込めませんでした。", "入力してください。", "見つかりませんでした —" - so
this batch is polite too, in prose. Labels and column heads stay bare nouns
("数量", "価格", "提案"), which is how a table head and a button read in any
register.

Japanese writes no space between words, so this batch never invents one. The
one space Japanese does use is the 和欧間 gap around a Latin or numeric run,
which the existing translations apply consistently ("NFT メタデータ",
"1.2.42 形式", "3 ホップ以内"); this batch follows it. Asides take a spaced
em dash ( — ), loaders end in …, and a button quoted inside prose is 「」.
The strings that are pure data (a row title "ID", a feed stamp "%(id)s @ %(ts)s",
the edge-card glue "%(pool)s · %(a)s–%(b)s", an example payload the reader
overwrites) are therefore left byte-identical in KEPT_ENGLISH rather than
"translated" with a space the reader does not want.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes one (op 22, op 23, op 34, op 45, 1.10.N, 3 hops, 6 pool hops,
24 hours, 1024 chars) the translation keeps it byte-verbatim or spells the
same figure in kanji numerals.

SAFETY POSTURE FOR THE DUAL-LINE STRINGS. The signing screens render a
Japanese line beside its English master. Japanese drops qualifiers readily, so
for the rows below the fuller polite form is deliberate and is recorded in the
comment next to the entry: transfer.propose_notice_locked names the signer in
full and repeats the shipped 「ご自身として操作するにはアンロックしてください」;
transfer.enclosed_op_note keeps 承認がすべてそろってから (executes ONLY after
approvals); createworker.draft_... keeps 提案ではなく直接の操作 (workers are
broadcast directly, NOT proposed); borrow.bids_no_cancel keeps both outcomes
(執行されるか、期限切れ); vote.retried_prefix / vote.retry_self say 自分自身の
アカウント so the reader can see WHOSE stake signed; instant.preview_balances_note
keeps 残高は確認していません (the balances on screen were NOT checked); and
trade.uc_total says 売却する合計数量 rather than 合計, so an amount can never be
read as a summary line.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ja_chunkC.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ja_chunkC.py --apply         # writes ja.json
  python3 tooling/apply_i18n_ja_chunkC.py --verify        # structural re-proof
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

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from JA below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
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
# so "call_order_update", "voting_account", "same-t" and "index.html" are one
# decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Japanese crypto UI prints in Latin, a platform API name the reader
# looks up verbatim, or a literal that must survive translation.
#
# "Stochastic" is a chart indicator name the wallet lists by its menu label
# (tour.s3_body names SMA, EMA, RSI, MACD and Stochastic together, so the tour
# and the indicator menu read the same). "URI" and "NFT" name the two halves of
# the asset.nft_uri_field label. "call_order_update" and "voting_account" are
# chain field names a reader greps for while debugging. "op" is the
# operation-number shorthand the English masters keep in every "… (op 22)"
# title. "A" and "B" are the two legs of a swap, which the barter desk already
# labels ピアA / ピアB and the pool chart already prints as A-per-B / B-per-A.
# "ID" is the uppercase form the shipped dictionary uses everywhere an object
# id is named (プール ID, 1.17.x IDで, プロキシアカウント名または ID を…); the
# lowercase "proposal id" of the English master is normalised to it here.
# "N" is the placeholder tail of an object id, 1.10.N, and is data (rule 1):
# the digit-and-dot prefix is not Latin, so the sweep sees the N alone.
LOAN = frozenset((
    "A", "B", "BTS", "EMA", "HTLC", "ID", "JSON", "MACD", "N", "NFT", "RSI",
    "SMA", "URL", "URI", "WebCrypto", "call_order_update", "https",
    "localhost", "op", "voting_account", "Stochastic",
))


# Values this script itself wrote in an earlier revision and has since replaced
# or moved into KEPT_ENGLISH. Listing them keeps both the rewrite and the revert
# loops' preconditions exact - they may touch THIS script's own earlier words
# and nothing else - so a later pass can settle a disagreement without silently
# dropping a real translation from any other batch.
#   tour.s3_body  深度 -> デプス: the shipped depth word is デプス (market.depth_title
#                  デプス, market_book.depth_plot デプス階段, pool.depth_title デプス（CPMM 曲線）,
#                  10 strings). 深度 is the correct Japanese word for "depth" and
#                  was the natural first choice, but it is a MINORITY form here and
#                  the tour is where a reader is being taught the vocabulary.
#   xrate.base_pinned  基準列 -> ベース列: the shipped base/quote pair is ベースアセット /
#                  クォートアセット (credit.ph_base_asset, credit.ph_quote_asset), so the column
#                  names follow that pair and not a third word.
#   asset.nft_uri_field  moved to KEPT_ENGLISH: chunkA had already decided it, and a
#                  key it declares English must stay English for its --verify.
SUPERSEDED = {
    "tour.s3_body": (
        u"価格のローソク足、出来高、深度に加え、指標メニューがあります。"
        u"SMA や EMA のような重ね指標、RSI、MACD、Stochastic のような"
        u"オシレーターです。取引所を開けばライブで確認できます。"
    ),
    "xrate.base_pinned": u"BTS は基準列のため削除できません。",
    "asset.nft_uri_field": u"NFT の URI",
}


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
    # are printed loudly and never repaired here: chunkA / chunkB own them, and
    # an insert-only batch that "fixed" a neighbour would be the silent edit the
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
    claimed = set(ja.get("_meta", {}).get("translated", []))
    for k in sorted(KEPT_ENGLISH):
        if k in claimed:
            bad.append("kept-english key is claimed as translated: %s" % k)
    by_section = {}
    for k in same + sorted(KEPT_ENGLISH):
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1
    scope_left = [
        k for k in sorted(e)
        if d.get(k) == e[k] and k not in JA and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(JA) - len(same), len(JA)))
    print("  keys kept byte-identical to en on purpose: %d"
          % (len(KEPT_ENGLISH) + len(same)))
    print("  keys of ja.json still equal to en      : %d"
          % len(scope_left))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch              : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash    : %d (hashes ok: %d)"
          % (links, links_ok))
    for sec in sorted(by_section):
        print("    %-12s %d identical to en" % (sec, by_section[sec]))
    if scope_left:
        print("  keys still at en, in neither table:")
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
    reverted = []
    # Converge, don't pile up. chunkA / chunkB already declared some of these
    # keys English on purpose, and one of them (asset.nft_uri_field) was briefly
    # translated by an earlier run of THIS script before the disagreement was
    # settled. Put the English bytes back so their --verify stays green. The
    # precondition is exact: only a value THIS batch's own JA dict, or plain
    # English, may be reverted - a real translation from any other batch is
    # never silently lost.
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key in JA:
            problems.append("key is in both tables: %s" % key)
            continue
        if key not in before:
            problems.append("kept-english key not in ja.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            continue  # already held
        if cur != en_flat[key] and cur != SUPERSEDED.get(key):
            problems.append(
                "would revert a real translation: %s (%r)" % (key, cur)
            )
            continue
        deep_set(ja, key, value)
        reverted.append(key)
    if reverted:
        before = collections.OrderedDict(flat(ja))

    for key, value in sorted(JA.items()):
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in ja.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            continue  # already applied by an earlier run
        if cur != en_flat[key] and cur != SUPERSEDED.get(key):
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
    for key, value in sorted(KEPT_ENGLISH.items()):
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
    owned = set(JA) | set(KEPT_ENGLISH)
    uncovered = sorted(k for k in en_flat
                       if k not in owned and before.get(k) == en_flat[k])
    if uncovered:
        print("REFUSING: %d key(s) are in neither table and still read "
              "English: %s" % (len(uncovered), ", ".join(uncovered[:8])))
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
                 if k in before and before[k] == en_flat[k]
                 and k not in reverted)
    if lie:
        print("REFUSING: _meta.translated claims keys that still read "
              "English: %s" % ", ".join(lie[:5]))
        return 1
    # A key this run reverted to English must lose its claim in the same breath:
    # a claimed key that reads English is exactly the false claim G5b exists to
    # prevent, and the revert is what makes the value English.
    if reverted:
        meta["translated"] = [k for k in claimed if k not in reverted]
        claimed = meta["translated"]
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

    print("ja chunk-C: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(set(list(by_section) + [k.split(".")[0]
                                              for k in KEPT_ENGLISH])):
        print("  %-16s %d translated, %d kept English"
              % (sec, by_section.get(sec, 0),
                 sum(1 for k in KEPT_ENGLISH
                     if k.split(".")[0] == sec)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    print("  keys of ja.json still equal to en after this batch: %d"
          % len(uncovered))
    if reverted:
        print("  reverted to English (decision settled in KEPT_ENGLISH, so "
              "chunkA / chunkB --verify stays green): %s" % ", ".join(reverted))
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


JA = {
    # ================================================================= i18n (6)
    # THE HONESTY SURFACE. These strings ARE the warning a reader sees, so they
    # are written to be unmissable rather than idiomatic: who wrote them, who
    # has NOT checked them, and what the asterisk does. A Japanese reader who
    # cannot read the English badge cannot be told their Japanese is unreviewed,
    # so these must read naturally in Japanese - and each says the same three
    # facts the English master says, no more and no less.
    "i18n.badge_body": (
        u"これらの翻訳は機械が書いたもので、人が確認したものではありません。"
        u"署名画面に * が付いた行は、元の英語も併せて表示されます。"
    ),
    "i18n.badge_details": u"これはどういう意味か",
    "i18n.badge_improve": u"この翻訳の改善に協力する",
    "i18n.badge_label": u"翻訳の状態: 機械翻訳で、人が確認していません",
    "i18n.risk_about_translations": u"この翻訳について",
    # i18n.risk_show_english is an aria-label spoken at EVERY signing line, one
    # tap each, so it is deliberately the shortest string here - 14 characters,
    # naming the line and the action and nothing else.
    "i18n.risk_show_english": u"この行の英語原文を表示",

    # ============================================================= approval (20)
    # The dApp approval popup: a site asks, the reader decides. Its two
    # buttons are the whole screen, so 承認 / 却下 are the plainest possible
    # verbs and the outcome lines say what ALREADY HAPPENED (ブロードキャスト
    # しました / 却下しました) - never what will happen.
    "approval.account": u"アカウント: ",
    "approval.approve": u"承認",
    "approval.approved": u"承認し、ブロードキャストしました。",
    "approval.chain": u"チェーン: ",
    "approval.close": u"閉じる",
    "approval.denied": u"却下しました。",
    "approval.deny": u"却下",
    "approval.expires_in": u"有効期限まで ",
    "approval.load_failed": u"承認リクエストを読み込めませんでした。",
    "approval.loading": u"承認リクエストを読み込み中…",
    # The one line that can make a reader approve as themselves: it names the
    # lock, the consequence and what typing the password buys. Nothing dropped.
    "approval.locked_note": (
        u"セッションはロック中です — 承認するにはウォレットのパスワードを"
        u"入力してください。"
    ),
    "approval.no_fields": u"表示できる項目がありません。",
    "approval.no_reply": u"署名者から返信がありません。",
    "approval.no_runtime": u"拡張機能の実行環境がありません。",
    "approval.password": u"パスワード",
    "approval.remember": u"このサイトでこのアカウントを記憶する",
    "approval.site_prefix": u"サイト: ",
    "approval.title": u"署名を承認",
    "approval.unknown_intent": u"承認リクエストが見つかりません。",
    "approval.wallet_title": u"このウォレットが署名を求めています",

    # ================================================================= auth (7)
    # The multisig explainer. co-owner is 共同所有者 (the wording
    # asset.multisig_body and asset.multisig_coowner_hint already ship); the
    # 1.10.N object-id shape stays byte-verbatim; 浏览は公開 keeps the read
    # half's no-login promise in the same sentence as the write half's.
    "auth.multisig_body": (
        u"このウォレットは1つの鍵を保持しています。共有アカウントには提案と"
        u"共同所有者の承認が必要で、提案 ID（1.10.N）で調整します。閲覧は公開です "
        u"— パスワードが求められるのは署名のときだけです。"
    ),
    "auth.multisig_open_proposals": u"提案を表示",
    "auth.multisig_open_txbuilder": u"トランザクションビルダーを開く",
    # The button names are QUOTED, not paraphrased: the reader has to be able to
    # find 「送信 / 提案」 on the transfer page from this sentence.
    "auth.multisig_step_approve": (
        u"共同所有者は提案ページで承認（op 23）するか、トランザクションビルダーで"
        u"共同署名します。"
    ),
    "auth.multisig_step_propose": (
        u"その操作を提案します（送金画面には「送信 / 提案」のボタンがあります。"
        u"アセット、バーター、借入も提案に連動します）。"
    ),
    "auth.multisig_step_share": (
        u"1.10.N の提案 ID を共同所有者に共有します。"
    ),
    "auth.multisig_title": u"共有 / マルチシグアカウント",

    # ================================================================ barter (7)
    "barter.confirm_barter_proposal_op_22": u"バーターの提案を確認（op %(op)s）",
    "barter.propose_barter_op_22": u"バーターを提案（op %(op)s）",
    "barter.step_build": u"構築",
    "barter.step_preview": u"プレビュー",
    "barter.step_propose": u"提案",
    # HIGH RISK. The English apostrophe in "both sides' transfers" is rephrased
    # (G7) as 双方, and the two clauses stay in the same order as the English:
    # preview FIRST, then the button encloses BOTH transfers in ONE proposal,
    # and the fee payer is named. "両脚" is the barter desk's own word for a
    # leg (barter.no_legs レッグなし lives one page away), so the reader is not
    # asked to learn a second word in the sentence that decides what gets sent.
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"双方向のアトミックスワップのプレビューです。まずプレビューを確認し、"
        u"「提案」を押すと双方の送金を1つの提案にまとめます（op %(op)s、"
        u"手数料の支払者 = ピアA）。"
    ),
    "barter.uc_title": u"署名するにはアンロックしてください",

    # ================================================================ borrow (9)
    # 担保 is the collateral word the borrow desk already ships
    # (borrow.hdr_collateral 担保), and 決済入札 is the settlement-bid button
    # (borrow.confirm_settlement_bid 決済入札を確認). "Call order" is left as
    # コールオーダー, not a coinage, because the desk's own help text uses it.
    "borrow.adjust": u"調整",
    "borrow.adjust_position_op_3": u"ポジションを調整（op %(op)s）",
    # HIGH RISK. Irreversibility plus BOTH outcomes. 執行されるか、期限切れになるか
    # is kept in full: a Japanese 取り消せません alone would leave a reader
    # guessing whether the bid silently lapses or quietly fills.
    "borrow.bids_no_cancel": (
        u"入札は出したら取り消せません — 執行されるか、期限切れになるかの"
        u"いずれかになります。"
    ),
    "borrow.close_position": u"ポジションを閉じる",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"マージンポジションは担保を抵当にビットアセットを借り入れる仕組みです。"
        u"担保を追加するか債務を返済すると、あなたのコールオーダーで "
        u"op %(op)s（call_order_update）が調整されます。"
    ),
    "borrow.open_a_new_position_op_3": u"新しいポジションを開く（op %(op)s）",
    "borrow.repay_full": u"全額返済",
    "borrow.settlement_bids_op_45": u"決済入札（op %(op)s）",
    "borrow.uc_title": u"署名するにはアンロックしてください",

    # =========================================================== createaccount (3)
    # The wizard's three step names. Breinkey follows the 40+ shipped strings
    # that already say ブレインキー (wallet.brainkey, help.topic_backups_body) -
    # a wizard that spelled it two ways on one screen would be the reader's
    # first proof that the translation is machine-made.
    "createaccount.step_brainkey": u"ブレインキー",
    "createaccount.step_name": u"名前",
    "createaccount.step_register": u"登録",

    # ============================================================ createworker (4)
    "createworker.confirm_worker_op_34": u"ワーカーを確認（op %(op)s）",
    # HIGH RISK, and the sharpest string in this batch. It exists to stop a user
    # assuming a worker is proposed rather than broadcast, so BOTH halves stay:
    # the op number appears twice, 「署名して送信」 is the shipped button
    # (common.sign_send), and 提案ではなく直接の操作で作成されます is not softened.
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"ワーカーを作成します（op %(op)s）。プレビューはライブ値で、確認画面には"
        u"実際の手数料が表示されます。その後「署名して送信」で op %(op)s を直接"
        u"ブロードキャストします — ワーカーは提案ではなく直接の操作で"
        u"作成されます。"
    ),
    "createworker.worker_preview_op_34": u"ワーカーのプレビュー（op %(op)s）",

    # ================================================================ credit (3)
    # ディール is the credit-deal noun the account op table already ships
    # (account.op_deal_repay ディール返済, account.sum_deal_update). The
    # borrowed-side label is 借り手, not 借入先, so it reads as the ROLE.
    "credit.my_deals_borrower": u"自分のディール（借り手）",
    "credit.no_borrower_deals": (
        u"借り手としてのディールはまだありません — オファーに対して借り入れると、"
        u"ディールが表示されます。"
    ),
    "credit.uc_title": u"署名するにはアンロックしてください",

    # ================================================================ debit (2)
    # The direct-debit ladder's per-step order. It is NOT a resting limit order
    # (trade.back_orders 注文に戻る), so the plain 注文 is right here and the
    # _scale_ desk keeps its own word.
    "debit.uc_order": u"注文",
    "debit.uc_title": u"署名するにはアンロックしてください",

    # ============================================================= dashboard (2)
    "dashboard.tagline": (
        u"マーケットは無料で閲覧できます — 取引するにはウォレットを作成してください。"
    ),
    "dashboard.welcome": u"自分で持つ鍵で BTS を取引",

    # ================================================================ gateway (3)
    # The trailing space on intro_a is load-bearing: intro_b follows it.
    "gateway.intro_a": (
        u"外部のコインは表示されたアドレスへ送ってください。このページ自体は何も"
        u"送りません。 "
    ),
    "gateway.intro_b": (
        u"出金は送金画面で、ライブの手数料プレビューとともに完了します。"
    ),
    "gateway.raw_prefix": u"生: ",

    # ================================================================= htlc (3)
    # The hash-lock gloss. 返金 is stated as the alternative to redemption so a
    # reader knows the lock has two exits, and the no-login half of the promise
    # stays in the same sentence.
    "htlc.list_sub": (
        u"資金をハッシュにロックします — 期限前に受信者がシークレットで償還できなければ、"
        u"送信者に返金されます。誰でも読めます。パスワードが尋ねられるのは署名の"
        u"ときだけです。"
    ),
    "htlc.uc_title": u"署名するにはアンロックしてください",

    # =============================================================== instant (4)
    "instant.fill_or_kill": u"全量約定または取消",
    # HIGH RISK. This note is the only thing telling the reader that the
    # balances on screen were NOT checked, so 残高は確認していません stays blunt
    # (not おおよその残高) and the unlock instruction follows it.
    "instant.preview_balances_note": (
        u"%(name)s（%(id)s）としてプレビューしています — 残高は確認していません。"
        u"署名の前にアンロックして、ご自身の残高を確かめてください。"
    ),
    "instant.uc_title": u"署名するにはアンロックしてください",
    "instant.unlock_sign": u"アンロックして署名",

    # ================================================================== nav (4)
    # The four burger-menu tiles. Reuse the desk's own word for each page:
    # マーケット (market.picker_title), プール (txbuilder.link_pools),
    # クレジット (account.credit_offers_page), マージン (account.margin_positions).
    "nav.credit": u"クレジット",
    "nav.margin": u"マージン",
    "nav.markets": u"マーケット",
    "nav.pools": u"プール",

    # =============================================================== news (1)
    "news.explorer_blocks_and_transactions": u"チェーンを探索",

    # ======================================================= market_ind (3)
    # ローソク足 is the shipped word for a candle (market_ind.candle_count
    # ローソク足, market_ind.count_range ...本のローソク足), and the count
    # pattern "X 件のうち Y" keeps the requested number FIRST so a truncated
    # window cannot read as a complete one.
    "market_ind.count_capped": u"表示範囲を縮小しています",
    "market_ind.count_note": u"%(count)s × %(bucket)s ローソク足",
    "market_ind.count_partial": u"%(requested)s 件のうち %(actual)s × %(bucket)s ローソク足",

    # ============================================================== proposal (9)
    "proposal.confirm_proposal_create_op_22": u"提案の作成を確認（op %(op)s）",
    # DELETE is irreversible, so both the button and its confirmation use the
    # plainest verb the dictionary owns (proposal.remove 削除).
    "proposal.confirm_proposal_delete_op_24": u"提案の削除を確認（op %(op)s）",
    "proposal.delete_proposal_op_24": u"提案を削除（op %(op)s）",
    # HIGH RISK. Three facts, three sentences, no clause dropped: ONE co-owner
    # proposes, the id is SHARED, THE REST approve below - and multi-operation
    # or multi-device work moves to the builder rather than happening here.
    "proposal.multisig_story": (
        u"共有アカウントですか？共同所有者の一人が提案し、1.10.N の ID を"
        u"共有すると、残りの人が下で承認します。複数の操作にまたがる作業や"
        u"複数デバイスでの作業は、トランザクションビルダーで続きます。"
    ),
    "proposal.open_txbuilder": u"トランザクションビルダーを開く",
    "proposal.raw_json": u"生 JSON",
    "proposal.raw_prefix": u"生: ",
    # HIGH RISK. Same shape as the shipped viewing.notice_locked so the read
    # mode and the signing mode read identically wherever they appear.
    "proposal.viewing_as": (
        u"%(name)s（%(id)s）として閲覧中 — ご自身として操作するには"
        u"アンロックしてください。"
    ),

    # =============================================================== tour (7)
    # The onboarding tour. It quotes the page names the reader is about to tap
    # (取引所デスク, 取引所), so the button and the sentence use one word.
    "tour.away_note": u"取引所デスクのページです — 開くと、この場所が強調表示されました。",
    "tour.s1_body": (
        u"すべてのページは、ログインなしでチェーンの公開データを読みます。"
        u"まずマーケットを開いてみてください — パスワードが尋ねられるのは"
        u"署名のときだけです。"
    ),
    "tour.s1_title": u"すべてを無料で閲覧し、ローカルで署名",
    "tour.s3_body": (
        u"価格のローソク足、出来高、デプスに加え、指標メニューがあります。"
        u"SMA や EMA のような重ね指標、RSI、MACD、Stochastic のような"
        u"オシレーターです。取引所を開けばライブで確認できます。"
    ),
    "tour.s3_title": u"ライブの価格チャートを見る",
    # The practice step: the safety sentence ("Nothing leaves your machine
    # until...") is the point of the step and is kept whole.
    "tour.s4_body": (
        u"購入と売却のパネルは練習のために任意の数値を受け取ります。アンロックした"
        u"ウォレットで確認して署名するまで、あなたの端末から外に出るものはありません。"
        u"取引所を開いて試してみてください。"
    ),
    "tour.s4_title": u"購入と売却を試す",

    # ========================================================== transfer (6)
    "transfer.confirm_proposal_title": u"提案を確認（op %(op)s）",
    # HIGH RISK. The trailing clause IS the point - nothing executes until the
    # approvals are in - so 承認がすべてそろってから実行されます is kept emphatic
    # and literal rather than shortened to 承認後に実行.
    "transfer.enclosed_op_note": (
        u"内包する操作: 送金（op %(op)s） — 承認がすべてそろってから実行されます。"
    ),
    # HIGH RISK. The notice that names WHO will sign while the wallet is locked.
    # It must not read as "somebody else proposed it" nor as a cosmetic banner,
    # so the name and the id stay, and the fix is the same sentence the rest of
    # the app already uses.
    "transfer.propose_notice_locked": (
        u"ロック中のため、提案者は %(name)s（%(id)s）になります — アンロックすると"
        u"ご自身として操作します。"
    ),
    "transfer.share_needs_to_amount": u"共有リンクには受取先と数量が必要です。",
    "transfer.uc_title": u"続けるにはアンロックしてください",
    "transfer.unlock_sign": u"アンロックして確認",

    # =============================================================== trade (8)
    # The unlock-confirm rows. Amount is 数量 (account.amount_field 数量) not
    # 金額, because the value is an asset amount, and Total says 合計数量 so a
    # bare 合計 can never be read as a summary line. The gate titles match the
    # already-translated pool.uc_title word for word.
    "trade.row_fok": u"全量約定または取消",
    "trade.tab_single": u"単一",
    "trade.uc_amount": u"数量",
    "trade.uc_orders": u"注文",
    "trade.uc_price": u"価格",
    "trade.uc_range": u"価格範囲",
    "trade.uc_title": u"続けるにはアンロックしてください",
    "trade.uc_total": u"売却する合計数量",

    # ============================================================ trollbox (8)
    # The chat desk's form labels. チャンネル is already the section's word
    # (trollbox.channels_title チャンネル) and 手数料 the section's word
    # (trollbox.fee_prefix ネットワーク手数料：), so the bare row heads reuse
    # them rather than coining a second pair.
    "trollbox.bytes_unit": u"バイト",
    "trollbox.channel_row": u"チャンネル",
    "trollbox.fee": u"手数料",
    "trollbox.language_row": u"言語",
    "trollbox.message_row": u"メッセージ",
    "trollbox.post_review_title": u"メッセージを確認",
    "trollbox.size_row": u"サイズ",
    "trollbox.unlock_post": u"アンロックして投稿",

    # ====================================================== unlockconfirm (5)
    # The modal that gates every posting/signing action. Matches the shipped
    # common.unlock_failed アンロックに失敗しました。 and the 22 shipped 戻る
    # buttons word for word.
    "unlockconfirm.cancel": u"戻る",
    "unlockconfirm.empty_password": u"ウォレットのパスワードを入力してください。",
    "unlockconfirm.password": u"パスワード",
    "unlockconfirm.unlock_failed": u"アンロックに失敗しました。",
    "unlockconfirm.unlock_post": u"アンロックして投稿",

    # =============================================================== vote (9)
    # ステーク is the stake word the ticket desk already ships
    # (help.topic_tickets_body ステークをロック / vote.* 投票力), and every
    # count in this block is described as a live chain READ so a reader never
    # treats the number as final.
    "vote.ballot_intro": (
        u"あなたのステークがウィットネスと委員会を選び、ワーカーを支えます — "
        u"以下の数値と比率はすべてチェーンからのライブ読み取りです。"
    ),
    "vote.confirm_witness_update_op_21": u"ウィットネス更新を確認（op %(op)s）",
    "vote.direct_note": (
        u"直接の投票を発行しました（voting_account %(id)s）。"
    ),
    "vote.in_sync": u"投票スレートはチェーンと一致しています — 発行すべき変更はありません。",
    # G7: the English possessive ("another account's vote slate") is rephrased
    # as 他のアカウントの rather than borrowed with an apostrophe. The warning -
    # read how voting works BEFORE setting one - is kept, because a reader who
    # sets a proxy without reading it locks their own slate by accident.
    "vote.proxies_follow_another_account_s_slate_re": (
        u"プロキシは他のアカウントの投票スレートに従います — 設定する前に、"
        u"投票の仕組みについての記事を読んでください。"
    ),
    "vote.proxy_follows": (
        u" — あなたのステークはこのアカウントに従います。下部の投票スレートは"
        u"読み取り専用です。"
    ),
    # HIGH RISK. The reader has to be able to see WHOSE stake signed, so
    # "as self" becomes 自分自身のアカウント as a full noun phrase, not a
    # pronoun, and the rejected mode stays named.
    "vote.retried_prefix": (
        u"ノードが %(mode)s のプロキシモードを拒否したため、投票は自分自身の"
        u"アカウントとして発行されました（voting_account %(id)s）。"
    ),
    "vote.retry_self": (
        u"ノードが %(mode)s のプロキシモードを拒否しました — 自分自身のアカウントで"
        u"1回だけ再試行します…"
    ),

    # =============================================================== xrate (18)
    # The cross-rates desk. クロスレート is the page name menu.p_xrates and
    # seo.title_xrates already ship; ホップ is the graph-step word the account
    # and pool network maps already ship (pool_net.hops BTS まで %(n)s ホップ).
    "xrate.add_btn": u"列を追加",
    "xrate.asset_col": u"アセット",
    "xrate.base_pinned": u"BTS はベース列のため削除できません。",
    "xrate.empty": u"このチェーンには BTS から 3 ホップ以内のプールアセットがありません。",
    "xrate.intro": (
        u"すべてのプールアセットを直近のスワップ価格で表示し、プールグラフを"
        u"通じてクロスレートを計算します。署名は行われず、保存もされません。"
    ),
    "xrate.load_failed": u"クロスレートを読み込めませんでした: ",
    "xrate.loading": u"プールを読み込み中…",
    "xrate.no_route_col": u"6 ホップのプール経路内に %(sym)s への経路はありません。",
    "xrate.refresh_btn": u"価格を再取得",
    "xrate.remove_btn": u"削除 ",
    "xrate.retry_btn": u"再試行",
    "xrate.show_all": u"すべてのアセットを表示",
    "xrate.status": (
        u"%(pools)s プール · 3 ホップ以内 %(assets)s アセット · "
        u"%(total)s プール中 %(done)s 件が直近のスワップを保持"
    ),
    "xrate.title": u"クロスレート",
    "xrate.token_label": u"クォートトークンを追加",
    "xrate.unknown_token": u"%(sym)s という名前のプールアセットはありません。",
    "xrate.unpriced": (
        u"この経路のいずれかの脚に、まだ記録されたスワップがありません。"
    ),
}

# The remaining labels from the smaller sections, kept in their own block so
# the JA dict above stays organised by the SAFETY argument rather than by
# alphabet: everything from here down is a single word, a button, or a short
# sentence with no amount, direction or permission in it.
JA.update({
    # ============================================================== asset (0)
    # All five asset-page keys in this batch are byte-identical to English on
    # purpose (MCR, NFT, NFT URI, PMA, UIA) and live in KEPT_ENGLISH below: the
    # NFT URI field is the same Latin acronym as the NFT row head beside it, so
    # the two read as one term, and chunkA already made that call.
    # ============================================================= common (2)
    # The pager indicator, shaped like the already-shipped
    # account.portfolio_page 「%(page)s / %(pages)s ページ」.
    "common.page_n": u"%(n)s ページ",
    "common.unknown_asset": u"不明なアセットです。",

    # ============================================================= compat (1)
    # The insecure-context notice. https and localhost stay Latin because the
    # reader is going to TYPE one of them, and WebCrypto is the platform API
    # the message is about.
    "compat.insecure_hint": (
        u"このアドレスはセキュアコンテキストではないため、ブラウザが WebCrypto を"
        u"提供しません。ブラウザ自体は最新です — https か localhost で配信するか、"
        u"ファイルを直接開いてください。"
    ),

    # =============================================================== eslab (1)
    # The raw-integer warning on the ES (elastic search) lab. 精度 is the
    # precision word the whole dictionary already uses, and 生の整数 says the
    # values are UNPROCESSED rather than merely unformatted.
    "eslab.hint_donors": (
        u"期間内のカウント値です。合計は生の整数です — アセットの精度で割ってください。"
    ),

    # ============================================================ pool_detail (8)
    # The pool desk's chart + map captions. ローソク足 is the shipped candle
    # word, スワップ the shipped swap word, and 脚 the shipped leg word; the
    # FALLBACK caption keeps its 24時間 hedge, because the difference between
    # "there was a trade" and "we could not check" is the whole sentence.
    "pool_detail.candle_capped": u"表示範囲を縮小しています",
    "pool_detail.candle_count": u"%(swaps)s スワップ · %(count)s × %(bucket)s ローソク足",
    "pool_detail.candle_count_partial": (
        u"%(swaps)s スワップ · %(requested)s 件のうち %(actual)s × %(bucket)s ローソク足"
    ),
    "pool_detail.invert": u"反転",
    "pool_detail.invert_label": u"チャートの向きを反転（A あたり B / B あたり A）",
    "pool_detail.map_connects": (
        u"資金を入れられたプールがあり、かつ過去 24 時間に約定があったとき、"
        u"2 つのアセットを線で結びます。"
    ),
    "pool_detail.map_connects_fallback": (
        u"資金を入れられたプールがあるとき、2 つのアセットを線で結びます。"
        u"24 時間の約定状況は確認できません（履歴を取得できないため） — "
        u"資金を入れられたプールだけを表示しています。"
    ),
    "pool_detail.map_min_swaps": u"（最小 %(min)s スワップ）",

    # =========================================================== pools (1)
    "pools.selector_title": u"プールセレクター",

    # ======================================================== prediction (1)
    "prediction.uc_title": u"署名するにはアンロックしてください",

    # ============================================================ txbuilder (1)
    # Sits next to txbuilder.link_pools プール / link_transfer 送金 /
    # link_voting 投票, so it takes the bare noun the other three already use.
    "txbuilder.link_proposals": u"提案",
})

# Keys whose Japanese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of the file is explicit and
# auditable instead of implied by their absence from JA. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift. Every value below is either
#   * a loanword, acronym or brand: HTLC, URL, ID, NFT, MCR, PMA, UIA, i18n,
#     SMA, EMA, PSAR, BB, MSSR, Op, Tx, Brainkey-as-brand (shell.brand);
#   * a network / theme id the stored-prefs contract depends on: mainnet,
#     testnet, devnet, original-blue, light, dark;
#   * a chain object-id or a lookup hint made of real ids: 1.3.x, 1.19.x, 1.2.42;
#   * an example payload the reader overwrites: alice,10 / bob,2.5, USD, CNY,
#     BTC…, account-name, committee-account, alice;
#   * a punctuation sentinel: —, …, wss://…;
#   * pure data glue: a feed stamp, an edge card, a node card, a range arrow, a
#     "7d" window chip, a count unit.
# chunkA and chunkB already declared the explorer / pool / pool_net / shell /
# menu items in their own KEPT_ENGLISH; they are repeated here so this closing
# batch's coverage gate can prove the WHOLE file is accounted for. Two scripts
# agreeing is the point - neither re-writes the other's bytes.
KEPT_ENGLISH = {
    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    # ---- asset
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    # The field label is the same Latin acronym as the row head above it, so the
    # pair reads as one term. chunkA already decided this; repeating the
    # decision here is what keeps its --verify green (see the revert loop in
    # main() for how a key moved out of JA is put back to the English bytes).
    "asset.nft_uri_field": u"NFT URI",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    # ---- chain glue
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.th_mssr": u"MSSR",
    "explorer.tx_prefix": u"Tx ",
    # ---- empty-state sentinels
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    "market.stat_empty": u"—",
    "settings.dash": u"—",
    "settings.pending": u"…",
    # ---- branding
    "createworker.url": u"URL",
    "vote.url": u"URL",
    "htlc.title": u"HTLC",
    "i18n.badge_chip": u"i18n",
    "menu.p_htlc": u"HTLC",
    "misc.id": u"ID",
    "proposal.id": u"ID",
    "ticket.id": u"ID",
    "vesting.id": u"ID",
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    # ---- stored-prefs ids: theme and network names the settings page writes
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.network_devnet": u"devnet",
    "settings.theme_original_blue": u"original-blue",
    "settings.theme_light": u"light",
    "settings.theme_dark": u"dark",
    "settings.custom_placeholder": u"wss://…",
    # ---- indicator acronyms (the menu names them in Latin everywhere)
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    # ---- example payloads the reader overwrites
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "viewing.dialog_placeholder": u"account-name",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
    # ---- real object ids in a lookup hint
    "pool.share_or_pool_hint": u"symbol, 1.3.x, or pool 1.19.x",
    # ---- pure data glue: every slot is a number, a symbol, an id or a window
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pools · %(hops)s",
}


if __name__ == "__main__":
    sys.exit(main())
