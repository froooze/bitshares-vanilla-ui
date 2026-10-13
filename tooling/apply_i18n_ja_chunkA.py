#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ja chunk-A: fill the six desk sections ja.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ja.json, or one whose English master moved, is REFUSED;
  * JA + KEPT_ENGLISH together must account for EVERY untranslated key of the
    six sections, so a forgotten string is a refusal, never a silent English.

This is the Japanese sibling of tooling/apply_i18n_zh_chunkA.py and keeps its
gates one for one. chunk-B owns the help/pool/explorer tail and REFUSES
anything outside its own sections; this batch REFUSES anything outside account,
account_net, settings, market, market_net and asset. A key that crosses the
line is a reviewer's problem, never a script's silent edit.

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
                      an unclaimed key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  ja punctuation no value this batch writes may carry an ASCII or
                      typographic apostrophe, an ideographic space (U+3000), or a
                      Cyrillic letter. Japanese quotes a button with 「」 and
                      does not apostrophise, and ja.json already ships 3,164
                      translated strings that use none of the three; an
                      ideographic space in particular would smuggle an English
                      word gap back into a language that writes none. This is
                      the ja sibling of the zh batch's apostrophe gate.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: ja.json already ships "x*y=k"-style and
                      "· 有効期限 " neighbours outside this batch. The sweep
                      runs file-wide, but a hit OUTSIDE the six sections is
                      reported as PRE-EXISTING and does not gate this batch:
                      chunk-B owns those keys, and an insert-only pass that
                      repaired a neighbour would be exactly the silent edit the
                      scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                      LOAN below, or the write is refused. A Japanese crypto UI
                      prints DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy,
                      Smartcoin, Pool and Brainkey in Latin exactly as a
                      Chinese one does - inventing a fake katakana transliteration
                      instead would be worse than the loanword. The gate is
                      batch-scoped on purpose: the rest of ja.json already
                      carries hundreds of distinct Latin tokens from earlier
                      batches, and re-litigating those is not this file's job.

Register: the 3,164 strings ja.json already ships are POLITE (です/ます) -
"残高を読み込めませんでした。", "入力してください。", "見つかりませんでした —" - so
this batch is polite too, in prose. Labels and column heads stay bare nouns
("残高", "提案", "発行者"), which is how a table head reads in any register.

Japanese writes no space between words, so this batch never invents one. The
one space Japanese does use is the 和欧間 gap around a Latin or numeric run,
which the existing translations apply consistently ("NFT メタデータ",
"4文字シンボル", "MCR %（人間可読、例: 175）"); this batch follows it. The two glue
strings that are pure data are therefore left byte-identical in KEPT_ENGLISH
rather than "translated" with a space the reader does not want.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (first 8 publishers, first 100, op 19, op 23, 24h,
90d, 7-day) the translation keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ja_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ja_chunkA.py --apply         # writes ja.json
  python3 tooling/apply_i18n_ja_chunkA.py --verify        # structural re-proof
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

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from JA below so they keep the
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
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
# G9: a Latin run inside a Japanese value. A token may continue through - _ . /
# so "Same-T", "get_settle_orders" and "ipaddress.to" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Japanese crypto UI prints in Latin (or an API name and the one key
# name that has to be typed); anything else has to be Japanese.
LOAN = frozenset((
    "BB", "BTS", "CER", "Enter", "FBA", "GitHub", "HTLC", "MCR", "NFT",
    "PMA", "PSAR", "Same-T", "SMA", "UIA", "URI", "committee-account", "alice",
    "get_settle_orders", "https", "ipaddress.to", "op",
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
        # A count keeping its English unit suffix ("90d", "24h") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # into "90日" without changing the number the reader compares against
        # the range control beside it.
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

    print("ja chunk-A: %d planned, %d differ from en, %d intentionally identical"
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

    with open(JA_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ja, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/ja.json")
    return 0


JA = {
    # =========================================================== account (150)
    # The shared-account line: "active" and "owner" are the two weight types,
    # and ja's permissions help already calls them アクティブ and オーナー
    # ("2つの鍵: アクティブとオーナー"), so the line reuses that pair rather
    # than inventing a third spelling.
    "account.draw_network": u"ネットワーク図を描画",
    "account.lookup_placeholder": u"アカウント名",
    "account.multisig_checking": u"権限を確認中…",
    "account.multisig_open_txbuilder": u"トランザクションビルダーを開く",
    "account.multisig_shared": (
        u"共有アカウント — アクティブ %(ath)s/%(an)s · オーナー %(oth)s/%(on)s。"
    ),
    "account.multisig_single": (
        u"単一キー — アクティブ %(ath)s/%(an)s · オーナー %(oth)s/%(on)s。"
    ),
    "account.multisig_single_hint": (
        u"共有アカウントですか？提案は提案ページにあります。"
    ),
    "account.multisig_unavailable": (
        u"権限を取得できません — 提案は提案ページで引き続き確認できます。"
    ),
    "account.multisig_view_proposals": u"提案を見る",
    # Operation labels. Nominal, like the translated ones ("アカウント作成",
    # "指値注文作成", "注文約定") so a history column reads as a list of nouns.
    "account.op_assert_op": u"アサート",
    "account.op_asset_burn": u"アセットバーン",
    "account.op_asset_issue": u"アセット発行",
    "account.op_asset_settle": u"アセット決済",
    "account.op_asset_update": u"アセット更新",
    "account.op_authority_create": u"権限作成",
    "account.op_authority_delete": u"権限削除",
    "account.op_authority_update": u"権限更新",
    "account.op_balance_claim": u"残高請求",
    # The blind legs reuse the three words the vesting help already ships for
    # ops 39/40/41 (ブラインドへの送金 / ブラインド送金 / ブラインドからの
    # 送金), so the history column and the help text say one thing.
    "account.op_blind_from": u"ブラインドからの送金",
    "account.op_blind_to": u"ブラインドへの送金",
    "account.op_blind_transfer": u"ブラインド送金",
    "account.op_claim_fees": u"手数料請求",
    "account.op_claim_pool": u"手数料プール請求",
    "account.op_collateral_bid": u"担保入札",
    "account.op_committee_join": u"委員会参加",
    "account.op_committee_update": u"委員会更新",
    "account.op_custom_op": u"カスタム操作",
    "account.op_deal_expired": u"ディール期限切れ",
    "account.op_deal_repay": u"ディール返済",
    "account.op_deal_update": u"ディール更新",
    # ダイレクトデビット is the feature name menu.p_debit and debit.title
    # already ship; 自動引落 is the help article's prose word for the same
    # thing. Labels follow the menu so a button and its history row agree.
    "account.op_debit_claim": u"ダイレクトデビット請求",
    "account.op_debit_create": u"ダイレクトデビット作成",
    "account.op_debit_delete": u"ダイレクトデビット削除",
    "account.op_debit_update": u"ダイレクトデビット更新",
    "account.op_execute_bid": u"入札実行",
    "account.op_fba_distribute": u"FBA 分配",
    "account.op_fee_pool_fund": u"手数料プール資金供給",
    "account.op_feed_producers_update": u"フィード発行者更新",
    "account.op_feed_publish": u"フィード発行",
    "account.op_global_settle": u"グローバル決済",
    "account.op_htlc_create": u"HTLC 作成",
    "account.op_htlc_extend": u"HTLC 延長",
    "account.op_htlc_redeem": u"HTLC 償還",
    "account.op_htlc_redeemed": u"HTLC 償還済み",
    "account.op_htlc_refund": u"HTLC 返金",
    "account.op_issuer_update": u"発行者更新",
    "account.op_offer_accept": u"クレジット承諾",
    "account.op_offer_create": u"クレジットオファー作成",
    "account.op_offer_delete": u"クレジットオファー削除",
    "account.op_offer_update": u"クレジットオファー更新",
    "account.op_order_update": u"注文更新",
    "account.op_override_transfer": u"オーバーライド送金",
    "account.op_params_update": u"グローバルパラメータ更新",
    "account.op_pool_create": u"プール作成",
    "account.op_pool_delete": u"プール削除",
    "account.op_pool_deposit": u"プール入金",
    "account.op_pool_swap": u"プールスワップ",
    "account.op_pool_update": u"プール更新",
    "account.op_pool_withdraw": u"プール引き出し",
    "account.op_proposal_create": u"提案作成",
    "account.op_proposal_delete": u"提案削除",
    "account.op_proposal_update": u"提案更新",
    "account.op_samet_borrow": u"Same-T 借入",
    "account.op_samet_create": u"Same-T 資金作成",
    "account.op_samet_delete": u"Same-T 資金削除",
    "account.op_samet_repay": u"Same-T 返済",
    "account.op_samet_update": u"Same-T 資金更新",
    "account.op_settle_cancel": u"決済取消",
    "account.op_smartcoin_update": u"スマートコイン更新",
    "account.op_ticket_create": u"チケット作成",
    "account.op_ticket_update": u"チケット更新",
    "account.op_vesting_create": u"ベスティング作成",
    "account.op_vesting_withdraw": u"ベスティング引出",
    "account.op_witness_join": u"ウィットネス参加",
    "account.op_witness_update": u"ウィットネス更新",
    "account.op_worker_create": u"ワーカー作成",
    # Pager + its note. The trailing space on page_total is load-bearing: a
    # computed figure follows it.
    "account.page_total": u"ページ合計 ≈ ",
    "account.portfolio_page": u"%(page)s / %(pages)s ページ",
    "account.prices_cover_this_page": (
        u"価格はこのページの資産に対応しています — ページを切り替えるとさらに多くの"
        u"資産を価格評価できます。"
    ),
    # History one-liners: a finished act, one row, so every line ends in
    # しました the way the shipped ja history captions do.
    "account.sum_account_create": u"%(name)s を登録しました",
    "account.sum_account_transfer": u"アカウントを %(owner)s に移転しました",
    "account.sum_account_update": u"アカウントを更新しました: %(account)s",
    "account.sum_asset_burn": u"%(amount)s をバーンしました",
    "account.sum_asset_create": u"アセット %(symbol)s を作成しました",
    "account.sum_asset_issue": u"%(amount)s を %(to)s に発行しました",
    "account.sum_asset_settle": u"%(amount)s の決済を要求しました",
    "account.sum_asset_update": u"アセット %(asset)s を更新しました",
    "account.sum_authorities": u"%(account)s の権限を更新しました",
    "account.sum_balance_claim": u"%(amount)s を請求しました",
    "account.sum_bid": u"%(coll)s を担保に %(debt)s を借入するため入札しました",
    "account.sum_blind": u"ブラインド送金（入金 %(in)s、出金 %(out)s）",
    "account.sum_call_update": (
        u"ポジションを調整しました: 担保 %(coll)s、債務 %(debt)s"
    ),
    "account.sum_claim_fees": u"手数料 %(amount)s を請求しました",
    "account.sum_committee_create": (
        u"委員会メンバーになりました: %(account)s"
    ),
    "account.sum_committee_update": u"委員会メンバー %(account)s を更新しました",
    "account.sum_custom": u"%(account)s によるカスタム操作",
    "account.sum_deal_expired": u"ディール %(deal)s が期限切れになりました",
    "account.sum_deal_repay": u"ディール %(deal)s に %(amount)s を返済しました",
    "account.sum_deal_update": u"ディール %(deal)s を更新しました",
    "account.sum_debit_claim": u"%(amount)s のダイレクトデビットを請求しました",
    "account.sum_debit_create": (
        u"%(to)s に対して %(amount)s のダイレクトデビットを許可しました"
    ),
    "account.sum_debit_delete": u"ダイレクトデビットの許可 %(perm)s を削除しました",
    "account.sum_debit_update": (
        u"%(to)s に対する %(amount)s のダイレクトデビットを更新しました"
    ),
    "account.sum_execute_bid": (
        u"%(coll)s を担保に %(debt)s を借入するため入札を実行しました"
    ),
    "account.sum_fee_pool_fund": (
        u"%(asset)s の手数料プールに %(amount)s を資金供給しました"
    ),
    "account.sum_feed": u"%(publisher)s が %(asset)s のフィードを発行しました",
    "account.sum_feed_producers": (
        u"%(asset)s のフィード発行者を %(n)s 人に設定しました"
    ),
    "account.sum_fill": u"約定しました: 支払い %(pays)s、受け取り %(receives)s",
    "account.sum_global_settle": u"%(asset)s をグローバル決済しました",
    "account.sum_htlc_claimed": u"HTLC %(id)s を請求しました",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(from)s から %(to)s へ %(amount)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s を延長しました",
    "account.sum_htlc_redeem": u"HTLC %(id)s を償還しました",
    "account.sum_htlc_refund": u"HTLC %(id)s を返金しました",
    "account.sum_issuer_update": u"%(asset)s の新しい発行者: %(issuer)s",
    "account.sum_offer_accept": (
        u"%(coll)s を担保に %(amount)s を借入しました（オファー %(offer)s）"
    ),
    "account.sum_offer_create": u"%(asset)s でクレジットオファーを作成しました",
    "account.sum_offer_delete": u"オファー %(offer)s を削除しました",
    "account.sum_offer_update": u"オファー %(offer)s を更新しました",
    "account.sum_order_cancel": u"注文 %(order)s をキャンセルしました",
    "account.sum_order_create": (
        u"%(sell)s を売り、少なくとも %(buy)s と交換する注文を出しました"
    ),
    "account.sum_order_update": u"注文 %(order)s を更新しました",
    "account.sum_pool_create": u"プール %(a)s / %(b)s を作成しました",
    "account.sum_pool_delete": u"プール %(pool)s を削除しました",
    "account.sum_pool_deposit": u"プール %(pool)s に %(a)s + %(b)s をステークしました",
    "account.sum_pool_swap": (
        u"プール %(pool)s で %(sell)s → 少なくとも %(buy)s にスワップしました"
    ),
    "account.sum_pool_update": u"プール %(pool)s を更新しました",
    "account.sum_pool_withdraw": (
        u"プール %(pool)s から %(shares)s をステーク解除しました"
    ),
    "account.sum_proposal_create": u"%(n)s 件の操作を提案しました",
    "account.sum_proposal_delete": u"提案 %(proposal)s を削除しました",
    "account.sum_proposal_update": u"提案 %(proposal)s を承認しました",
    "account.sum_samet_borrow": u"資金 %(fund)s から %(amount)s を借入しました",
    "account.sum_samet_create": u"%(amount)s で Same-T 資金を作成しました",
    "account.sum_samet_delete": u"Same-T 資金 %(fund)s を削除しました",
    "account.sum_samet_repay": u"資金 %(fund)s に %(amount)s を返済しました",
    "account.sum_samet_update": u"Same-T 資金 %(fund)s を更新しました",
    "account.sum_settle_cancel": u"%(amount)s の決済をキャンセルしました",
    "account.sum_smartcoin_update": u"スマートコイン %(asset)s を更新しました",
    "account.sum_ticket_create": u"チケット %(amount)s を作成しました",
    "account.sum_ticket_update": u"チケット %(ticket)s を更新しました",
    "account.sum_transfer": u"%(from)s から %(to)s へ %(amount)s を送金しました",
    "account.sum_transfer_recv": u"%(from)s から %(amount)s を受け取りました",
    "account.sum_transfer_send": u"%(to)s に %(amount)s を送金しました",
    "account.sum_upgrade": u"%(account)s をアップグレードしました",
    "account.sum_vesting_create": u"%(owner)s の代わりに %(amount)s をベスティングしました",
    "account.sum_vesting_withdraw": u"ベスティング %(amount)s を引き出しました",
    "account.sum_whitelist": u"%(account)s をホワイトリストに登録しました",
    "account.sum_witness_create": u"ウィットネスになりました: %(account)s",
    "account.sum_witness_update": u"ウィットネス %(account)s を更新しました",
    "account.sum_worker_create": u"ワーカー「%(name)s」を作成しました",

    # ====================================================== account_net (64)
    "account_net.canvas_missing": (
        u"このビルドではネットワークキャンバスを利用できません。"
        u"下のテーブルにはすべての線が一覧表示されます。"
    ),
    "account_net.class_credit": u"クレジット",
    "account_net.class_credit_help": u"承諾済み・返済済みのクレジットオファー。",
    "account_net.class_debit": u"ダイレクトデビット",
    "account_net.class_debit_help": u"ダイレクトデビットの許可と引落し。",
    "account_net.class_htlc_help": (
        u"ハッシュタイムロックコントラクトとその更新。"
    ),
    "account_net.class_override": u"オーバーライド送金",
    "account_net.class_override_help": u"手数料をアセット発行者が支払う送金。",
    "account_net.class_transfer": u"送金",
    "account_net.class_transfer_help": u"アカウント間の直接送金。",
    "account_net.class_vesting": u"ベスティング",
    "account_net.class_vesting_help": u"第三者が管理するベスティング残高。",
    # Graph terms: a hop is one edge traversal, and ja's pool map already says
    # "{s} は BTS まで {n} ホップです", so the hop reuses ホップ.
    "account_net.depth_1": u"1 ホップ",
    "account_net.depth_2": u"2 ホップ",
    "account_net.depth_label": u"深さ",
    "account_net.detail_hint": (
        u"線をタップすると詳細が表示されます。アカウントをタップすると開きます。"
    ),
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s 件の操作 · "
        u"%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s 件の操作 · "
        u"%(kind)s"
    ),
    "account_net.es_bad_account": u"その名前はこのチェーンのアカウントではありません。",
    "account_net.es_disabled": (
        u"コミュニティインデックスが無効です。設定で有効にしてからこのマップを"
        u"描いてください。"
    ),
    "account_net.es_unavailable": (
        u"現在コミュニティインデックスに到達できません。"
        u"しばらくしてからもう一度お試しください。"
    ),
    "account_net.go": u"ネットワーク図を描画",
    "account_net.idle": u"まだ何も描いていません。",
    "account_net.intro": (
        u"1つ以上のアカウントを入力すると、誰に送金し、誰に貸し、誰から"
        u"借りているかが分かります。コミュニティ履歴インデックスから"
        u"読み込みます。署名は行われず、保存もされません。"
    ),
    "account_net.kind_flow": u"資金フロー",
    "account_net.kind_relation": u"関係",
    # The leading space is load-bearing: this fragment follows an asset name.
    "account_net.more_assets": u" 他 %(n)s 件",
    "account_net.need_class": u"描画するには線の種類を少なくとも1つ有効にしてください。",
    "account_net.need_seeds": u"マップを描くにはアカウントを少なくとも1つ入力してください。",
    "account_net.no_amount": u"金額なし",
    "account_net.ring1_label": u"リング1",
    "account_net.ring2_label": u"リング2",
    "account_net.scanning": u"コミュニティインデックスを読み込み中…",
    "account_net.seeds_label": u"マップを描くアカウント",
    "account_net.stale_settings": (
        u"深さまたは隣接の設定が変更されました。"
        u"「ネットワーク図を描画」を押してください。"
    ),
    "account_net.status_credit_index": (
        u"%(n)s 本のクレジット線はインデックスから解決しました"
        u"（オファーまたはディールのオブジェクトがチェーン上にありません）"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s 本のクレジット線はスキップしました"
        u"（チェーン上にオファーまたはディールが見つかりません）"
    ),
    "account_net.status_depth": u"%(depth)s のマップ",
    "account_net.status_edge_cap": u"上位 %(n)s 本の線を表示しています",
    "account_net.status_expanded": u"展開しました: %(names)s",
    "account_net.status_expansion_scanned": (
        u"展開から %(n)s 件のインデックス操作を読み込みました"
    ),
    "account_net.status_expansion_truncated": (
        u"展開の読み取りは最新の操作に限定しています"
    ),
    "account_net.status_graph": u"%(nodes)s アカウント · %(edges)s 本の線",
    "account_net.status_node_cap": u"上位 %(n)s 件の取引相手を表示しています",
    "account_net.status_scanned": (
        u"%(n)s 件のアカウントから %(scanned)s 件のインデックス操作を読み込みました"
    ),
    "account_net.status_self": u"自己送金の %(n)s 件をスキップしました",
    "account_net.status_shape": u"読み取れない %(n)s 件をスキップしました",
    "account_net.status_truncated": u"アカウントごとに最新 %(n)s 件の操作",
    "account_net.status_unexpanded": u"%(n)s 件の直接の取引相手は未展開です",
    "account_net.status_unknown": u"見つかりません: %(names)s",
    "account_net.title": u"アカウントネットワーク",
    "account_net.twin_amount": u"数量",
    "account_net.twin_class": u"種別",
    "account_net.twin_count": u"操作数",
    "account_net.twin_depth": u"ホップ数",
    "account_net.twin_empty": (
        u"読み込んだインデックス操作には、これらのアカウント間の線がありません。"
    ),
    "account_net.twin_from": u"送信元",
    "account_net.twin_relation": u"資金フロー / 関係",
    "account_net.twin_span": u"最初 → 最後",
    "account_net.twin_summary": u"テーブル表示（アクセシブル）",
    "account_net.twin_to": u"宛先",

    # ============================================================== asset (38)
    "asset.cer_row": u"コア為替レート（CER）",
    "asset.committee_fed_note": (
        u"委員会フィード：有効なすべての委員会メンバーが公開できます。"
    ),
    "asset.feed_history_title": u"フィード履歴",
    "asset.history_capped": u"最初の8人の公開者を表示しています（速度のため上限あり）…",
    "asset.history_days": u"期間",
    "asset.history_exchange": u"取引所とプールを読み込み中…",
    "asset.history_failed": u"フィード履歴を読み込めませんでした。",
    "asset.history_loading": u"フィード履歴を読み込み中…",
    "asset.history_pub": u"公開者 %(i)s/%(n)s…",
    "asset.invert_btn": u"反転",
    "asset.issue_memo_no_key": u"このアカウントにメモキーは登録されていません。",
    "asset.issue_memo_warning": (
        u"メモを添付してください。チェーン上に平文で保存されます。"
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"発行者は閲覧中のアカウント（%(id)s はロック済み、ご自身のアカウントは"
        u"アンロック済み）が初期値です。管理する発行者を入力してください。"
        u"アカウントページから開いた場合は、そのアカウント名をここに貼り付けてください。"
    ),
    "asset.loading_producers": u"発行者を読み込み中…",
    # "共同所有者" is the co-owner word the shipped help body already uses for
    # the second key holder, so the multisig hints reuse it verbatim.
    "asset.multisig_body": (
        u"このアセットに複数の承認が必要な場合、直接の署名では失敗します。"
        u"変更を提案し、共同所有者に承認を依頼してください（op 23）。"
    ),
    "asset.multisig_coowner_hint": (
        u"共同所有者ですか？提案ページで変更を提案し、共同所有者に承認を"
        u"依頼してください（op 23）。"
    ),
    "asset.multisig_open_proposals": u"提案を見る",
    "asset.multisig_open_txbuilder": u"トランザクションビルダーを開く",
    "asset.multisig_title": u"発行者を共有していますか？提案してください",
    "asset.new_issuer_field": u"新しい発行者",
    "asset.no_history": (
        u"この期間に履歴はありません。公開者の公開頻度は低いです。90d をお試しください。"
    ),
    "asset.no_producers": (
        u"まだフィードは公開されていません。公開者が公開するとここに表示されます。"
    ),
    "asset.orientation_note": u"%(b)s あたり %(m)s",
    "asset.owner_key_note": u"アセットオーナーのアクティブキーが必要です。",
    "asset.plot_feeds": u"フィードをプロット",
    "asset.producer_col": u"発行者",
    "asset.producers_failed": u"発行者を読み込めませんでした。",
    "asset.producers_live_title": u"フィード発行者",
    "asset.producers_title": u"フィード発行者（op %(op)s）",
    "asset.publish_op19_title": u"フィード発行（op %(op)s）",
    "asset.published_col": u"発行日時",
    # "閲覧中" is the phrase barter.viewing_as and every *_viewing_as notice
    # already ships as …として閲覧中; this reuses it so principle #9 reads one
    # way.
    "asset.viewing_notice": (
        u"%(name)s（%(id)s）として閲覧中 — 署名するにはアンロックしてください。"
    ),
    "asset.witness_fed_note": (
        u"ウィットネスフィード：有効なすべてのウィットネスが公開できます。"
    ),

    # ============================================================ market (54)
    "market.adjust_button": u"調整",
    "market.confirm_adjust": u"調整を確認",
    "market.discrete_fills": u"件約定",
    "market.discrete_no_fills": (
        u"まだ約定がありません。注文するか、別のペアをお試しください。"
    ),
    "market.discrete_swaps": u"件スワップ",
    "market.discrete_tip_account": u"アカウント",
    "market.discrete_tip_block": u"ブロック",
    "market.discrete_tip_order": u"注文",
    "market.discrete_tip_price": u"価格",
    "market.discrete_tip_time": u"時刻",
    "market.discrete_tip_volume": u"出来高",
    "market.discrete_tip_volume_quote": u"出来高（クォート）",
    "market.discrete_unavailable": u"離散ではインジケーターを利用できません。",
    "market.discrete_volume": u"離散出来高",
    "market.exchange_desk": u"取引所デスク",
    "market.fail_update": u"更新に失敗しました。",
    "market.flt_max_price": u"最高価格",
    "market.flt_min_price": u"最低価格",
    "market.loading_pool_map": u"マップを読み込み中…",
    "market.map_aria": (
        u"マーケットネットワーク。線は過去24時間に約定があったマーケットです。"
    ),
    "market.map_connects": (
        u"過去24時間にマーケットで取引があった場合、2つのアセットを線で結びます。"
    ),
    "market.map_connects_fallback": (
        u"資金が預けられているプールが存在する場合、2つのアセットを線で結びます。"
        u"24時間の取引状況は確認できません（履歴を利用できません）。"
        u"資金が預けられたプールを表示しています。"
    ),
    "market.map_edge_fills": u"%(desk)s · %(a)s–%(b)s · %(fills)s 件/24時間",
    "market.map_hops_empty": (
        u"これらの脚の周辺では過去24時間に約定のあったマーケットがありません。"
    ),
    "market.map_hops_filtered": (
        u"線は過去24時間に約定があったマーケットです。"
        u"%(total)s ペア中 %(shown)s ペアを表示しています"
        u"（24時間あたり最少 %(min)s 件約定）。"
    ),
    "market.map_hops_no_route": (
        u"約定のあったマーケットを経由して BTS へ到達する経路がありません。"
    ),
    "market.map_hops_note": (
        u"線は過去24時間に約定があったマーケットです。%(pairs)s ペアを表示しています。"
    ),
    # The pool map already ships these two lines verbatim in ja, so the desk
    # map says exactly what the pool map says.
    "market.map_leg_ok": u"{s} は BTS に接続しています",
    "market.map_leg_orphan": u"警告: {s} に約定済みマーケットの経路がありません！",
    "market.min_fills": u"最少約定数",
    "market.no_filter_match": u"これらの条件に一致する約定がありません。",
    "market.settle_first100": (
        u"最初の100件を表示しています（get_settle_orders の上限は100件）"
    ),
    "market.settle_no_cancel": (
        u"決済注文はキャンセルできません。決済時に実行されます"
        u"（アセットの強制決済の遅延期間の後）。"
    ),
    "market.tf_discrete": u"離散",
    # The three trailing spaces are load-bearing: an input follows them.
    "market.update_amount": u"売却する数量（新しい合計） ",
    "market.update_amount_change": u"数量の変更",
    "market.update_bad_amount": u"0より大きい数量を入力してください。",
    "market.update_bad_expiry": u"未来の有効期限を入力してください。",
    "market.update_bad_price": u"0より大きい価格を入力してください。",
    "market.update_broadcasting": u"更新をブロードキャスト中…",
    "market.update_done": u"注文を更新しました",
    "market.update_expiry": u"新しい有効期限 ",
    "market.update_expiry_change": u"有効期限（旧 → 新）",
    "market.update_no_change": (
        u"変更がありません。価格、数量、または有効期限を編集してください。"
    ),
    "market.update_price": u"新しい価格 ",
    "market.update_price_change": u"価格（旧 → 新）",
    "market.update_review": u"更新を確認",
    "market.update_title": u"注文を調整",

    # ======================================================= market_net (40)
    "market_net.asset_1_field": u"アセット1（どちらの脚でも可）",
    "market_net.asset_2_field": u"アセット2（どちらの脚でも可）",
    "market_net.band_title": u"マーケットネットワーク",
    "market_net.canvas_label": (
        u"マーケットネットワークマップ。Enter キーでマーケットを開きます。"
    ),
    "market_net.clear_btn": u"クリア",
    # The short column heads reuse the stats-tab wording verbatim: 24時間 Δ
    # is market.chg_label, and market_net.col_vol repeats market.osc_group_label's
    # 出来高 rather than inventing a shorter one.
    "market_net.col_change": u"24時間 Δ",
    "market_net.col_last": u"最新",
    "market_net.col_market": u"マーケット",
    "market_net.col_vol": u"24時間出来高",
    "market_net.collapse": u"折りたたむ",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s 件/24時間"
    ),
    "market_net.empty": u"この条件に一致するマーケットがありません。",
    "market_net.expand": u"展開",
    "market_net.list_btn": u"マーケット一覧",
    "market_net.loading": u"マーケットを読み込み中…",
    "market_net.map_empty": u"直近に出来高のあるマーケットはありません。",
    "market_net.map_fallback": (
        u"%(pairs)s ペア · %(assets)s アセット · 24時間の約定は未確認"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s ペア · %(assets)s アセット · 24時間の約定"
    ),
    "market_net.map_ready": u"%(markets)s マーケット · %(assets)s アセット",
    "market_net.node_card": u"%(sym)s（%(id)s） · %(n)s マーケット",
    "market_net.offline": (
        u"ネットワークを利用できません。キャッシュしたマーケットを表示しています。"
        u"接続後に再試行してください。"
    ),
    "market_net.open_desk": u"%(id)s を開く",
    "market_net.prompt": (
        u"ノードをタップするとアセット、線はタップするとマーケットが表示されます。"
    ),
    "market_net.ramp": u"24時間出来高: 低 → 高",
    "market_net.ramp_fills": u"24時間の約定: 低 → 高",
    "market_net.selector_title": u"マーケットセレクター",
    "market_net.spark_label": u"%(id)s の7日間の推移",
    "market_net.subtitle": (
        u"24時間出来高で選んだ主要オーダーブックのマーケット。"
        u"行を選ぶとデスクを開きます。"
    ),
    "market_net.title": u"マーケット",
    "market_net.top_note": (
        u"調査した %(probed)s 件のうち上位 %(shown)s 件。24時間出来高順です。"
    ),
    "market_net.twin": u"マーケットの行（%(n)s）",
    "market_net.twin_more": (
        u"%(n)s 件のマーケット中 %(shown)s 件を表示しています。"
        u"条件を絞ると表示数を減らせます。"
    ),
    "market_net.verdict_full": u"%(markets)s マーケット · %(assets)s アセット",
    "market_net.verdict_no_path": (
        u"%(a)s と %(b)s の間に約定済みマーケットの経路はありません"
    ),
    "market_net.verdict_path": (
        u"%(a)s は %(n)s 件の約定済みマーケットを経て %(b)s に到達します"
    ),
    "market_net.verdict_star": u"%(s)s を含むマーケット: %(n)s",
    "market_net.verdict_web": u"%(s)s から到達できるマーケット: %(n)s",

    # ========================================================== settings (48)
    "settings.confirm_back": u"戻る",
    "settings.confirm_remove_action": u"操作",
    "settings.confirm_remove_hide": (
        u"このノードを非表示にする（再追加するまで非表示のまま）"
    ),
    "settings.confirm_remove_result": u"結果",
    "settings.confirm_remove_switch": u"使用中のノードは %(node)s に切り替わります",
    "settings.confirm_remove_title": u"ノードを削除しますか？",
    "settings.confirm_remove_unlist": u"自分の一覧から削除",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**「ノードを探す」は GitHub でノード一覧を検索し、見つかったものを"
        u"調査します。GitHub と調査先のノードはあなたのネットワークアドレスを"
        u"認識します。結果は確認用の候補であり、自動的に追加されることは"
        u"ありません。"
    ),
    "settings.geo_note": (
        u"*位置とプロバイダーの情報は ipaddress.to（https、キー不要）から取得します。"
        u"要求されたときにあなたのアドレスを認識します。"
        u"回答はこのデバイスに24時間キャッシュされます。"
    ),
    "settings.hist_no": u"無",
    "settings.hist_yes": u"有",
    "settings.language_title": u"言語",
    # Signing section. 拡張機能 is this batch's first spelling of that word in
    # ja.json; 承認 reuses the existing proposal wording.
    "settings.sign_auto": u"自動（拡張機能が使えるとき）",
    "settings.sign_badge": u"拡張機能での署名が有効です。詳細は「ログイン」にあります",
    "settings.sign_badge_local": u"このページでの署名です。詳細は「ログイン」にあります",
    "settings.sign_browser": u"常にこのページで署名する",
    "settings.sign_ext": u"常に拡張機能を使う",
    "settings.sign_ext_absent": (
        u"このデバイスで拡張機能を検出できませんでした。署名はこのページ内で"
        u"行われます。"
    ),
    "settings.sign_ext_present": u"このデバイスで拡張機能を検出しました。",
    "settings.sign_guide": u"拡張機能のインストール方法",
    "settings.sign_mode_browser": u"署名はこのページのメモリ内で行われます。",
    "settings.sign_mode_ext": u"署名は拡張機能のウィンドウで承認します。",
    "settings.sign_mode_ext_page": (
        u"署名は拡張機能内で行うため、ウェブサイトから分離されています。"
    ),
    "settings.sign_revoke": u"取り消す",
    "settings.sign_sites": u"接続中のサイト",
    "settings.sign_sites_empty": (
        u"承認されたサイトはまだありません。承認するとここに表示され、"
        u"サイトごとに取り消せます。"
    ),
    # The trailing space on story_a is load-bearing: a URL follows it.
    "settings.sign_sites_story_a": u"例: あるサイコロゲームが ",
    "settings.sign_sites_story_b": (
        u" であなたのアカウントとしてプレイする権限を求めています。"
        u"承認するとそのアカウントにのみ紐づいてここに表示されます。"
        u"署名は毎回確認を求めます。"
        u"（そのリンクはどこにも遷移しません。架空の例です。）"
    ),
    "settings.sign_title": u"署名",
    "settings.sign_warn": (
        u"このページで実行されるスクリプトは、侵害されたホスティング版を含め、"
        u"アンロック中の鍵を読み取る可能性があります。"
        u"署名は拡張機能経由にするか、自分で管理するコピーを実行してください。"
    ),
    # Node-table column heads. 先頭 / 履歴 / 遅延 / 参加率 reuse the node-health
    # wording ja's settings help article already uses (先頭ブロック, 遅延＋ヘッド
    # 経過, ウィットネス参加).
    "settings.th_chain": u"チェーン",
    "settings.th_handshake": u"ハンドシェイク",
    "settings.th_head": u"先頭",
    "settings.th_history": u"履歴",
    "settings.th_location": u"位置 *",
    "settings.th_participation": u"参加率",
    "settings.th_ping": u"遅延",
    "settings.th_provider": u"プロバイダー *",
    "settings.theme_title": u"テーマ",
}

# Keys whose Japanese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from JA. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Japanese crypto UI keeps in Latin: HTLC, NFT,
#     MCR, PMA, UIA, URI, SMA, EMA, BB, PSAR;
#   * network ids and sentinels the brief pins: mainnet / testnet / devnet,
#     original-blue / light / dark, "wss://…", "…", "—", "7d";
#   * pure glue a table cell or edge card prints as data: "@ %(price)s ·
#     %(vol)s", "%(desk)s · %(a)s–%(b)s · %(vol)s", "@ %(price)s",
#     "%(first)s → %(last)s" — translating the space inside a glue string
#     would change what the reader sees, so it stays English;
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