#!/usr/bin/env python3
"""i18n zh chunk-A: fill the six desk sections zh.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from zh.json, or one whose English master moved, is REFUSED;
  * ZH + KEPT_ENGLISH together must account for EVERY untranslated key of the
    six sections, so a forgotten string is a refusal, never a silent English.

chunk-B owns the help/pool/explorer tail and REFUSES anything outside it; this
batch REFUSES anything outside account, account_net, settings, market,
market_net and asset. A key that crosses the line is a reviewer's problem,
never a script's silent edit.

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
                      letter. Chinese does not need any of them: the 3174
                      strings zh.json already ships use none, and the quotes it
                      does use are the curly pair " " (U+201C/U+201D), which this
                      gate does not touch. This is the Chinese sibling of the ru
                      batch's apostrophe gate.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: zh.json already ships "x·y=k" in
                      pool_detail.pool_curve, outside this batch's six
                      sections. The sweep runs file-wide, but a hit OUTSIDE the
                      six sections is reported as PRE-EXISTING and does not
                      gate this batch: chunk-B owns those keys, and an
                      insert-only pass that repaired a neighbour would be
                      exactly the silent edit the scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                      LOAN below, or the write is refused. Chinese crypto UIs
                      keep the English word for DEX, HTLC, BitShares, BTS, API,
                      Memo, Swap, Proxy, Smartcoin, Pool, Brainkey, FBA, Same-T,
                      URI, CER/MCR/NFT/PMA/UIA, get_settle_orders and the
                      GitHub / ipaddress.to service names - inventing a fake
                      transliteration instead would be worse than the loanword.
                      The gate is batch-scoped on purpose: the rest of zh.json
                      already carries 243 distinct Latin tokens from earlier
                      batches, and re-litigating those is not this file's job.

The spellings are reused verbatim from the part of zh.json that is already
translated, so this batch reads like the rest of the dictionary instead of like
a second dictionary: 账户, 资产, 余额, 订单 / 限价单 / 挂单, 成交, 价格, 数量,
报价, 手续费, 钱包, 节点, 索引, 权限, 提案, 见证人, 理事会, 工人, 发行者, 喂价,
喂价生产者, 抵押物, 归属, 智能币, 资金池, 质押, 解押, 票据, 借贷, 信用报价,
直接扣款, 交易台, 签名, 广播, 区块, 精度. The op labels (account.op_*) follow
the nominal pattern the translated ones already established - "Account create"
ships as "账户创建", "Limit order create" as "限价单创建", "Fill order" as
"订单撮合" - so a history column reads as a list of nouns. The account.sum_*
history lines keep the shipped finished-voice ("Registered %(name)s" is a
finished act, not a noun), because they describe one row, not a column.

Chinese writes no space between words, so this batch never invents one: a space
appears only where the file already puts one (a trailing space on a label
prefix that a value follows, " · " between graph fields, a gap around a Latin
run). The two glue strings that are pure data are therefore left byte-identical
in KEPT_ENGLISH rather than "translated" with a space the reader does not want.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (first 8 publishers, first 100, op 19, op 23, 7-day,
24h, 90d) the translation keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_zh_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_zh_chunkA.py --apply         # writes zh.json
  python3 tooling/apply_i18n_zh_chunkA.py --verify        # structural re-proof
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

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from ZH below so they keep the
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
# G9: a Latin run inside a Chinese value. A token may continue through - _ . /
# so "Same-T", "get_settle_orders" and "ipaddress.to" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Chinese crypto UI prints in Latin; anything else has to be Chinese.
LOAN = frozenset((
    "CER", "FBA", "GitHub", "HTLC", "Same-T", "BTS", "alice",
    "committee-account", "get_settle_orders", "https", "ipaddress.to", "op",
))


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
    # are printed loudly and never repaired here: chunk-B (or whoever wrote the
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

    print("zh chunk-A: %d planned, %d differ from en, %d intentionally identical"
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
    # =========================================================== account (150)
    # The shared-account line: "active" and "owner" are the two weight types,
    # and zh's permissions help already calls them 活跃权限 and 主人权限, so the
    # line reuses that pair rather than inventing a third spelling.
    "account.draw_network": u"绘制网络图",
    "account.lookup_placeholder": u"账户名",
    "account.multisig_checking": u"正在检查权限…",
    "account.multisig_open_txbuilder": u"打开交易构建器",
    "account.multisig_shared": (
        u"共享账户——活跃权限 %(ath)s/%(an)s · 主人权限 %(oth)s/%(on)s。"
    ),
    "account.multisig_single": (
        u"单密钥——活跃权限 %(ath)s/%(an)s · 主人权限 %(oth)s/%(on)s。"
    ),
    "account.multisig_single_hint": (
        u"共享账户？请到提案页面处理提案。"
    ),
    "account.multisig_unavailable": (
        u"权限不可用——提案仍可在提案页面查看。"
    ),
    "account.multisig_view_proposals": u"查看提案",
    # Operation labels. Nominal, like the translated ones ("账户创建",
    # "限价单创建", "订单撮合") so a history column reads as a list of nouns.
    "account.op_assert_op": u"断言",
    "account.op_asset_burn": u"资产销毁",
    "account.op_asset_issue": u"资产发行",
    "account.op_asset_settle": u"资产结算",
    "account.op_asset_update": u"资产更新",
    "account.op_authority_create": u"权限创建",
    "account.op_authority_delete": u"权限删除",
    "account.op_authority_update": u"权限更新",
    "account.op_balance_claim": u"余额认领",
    # The blind legs are named by direction so the pair reads as one transfer:
    # 盲转入 / 盲转出 / 盲转账.
    "account.op_blind_from": u"盲转入",
    "account.op_blind_to": u"盲转出",
    "account.op_blind_transfer": u"盲转账",
    "account.op_claim_fees": u"领取手续费",
    "account.op_claim_pool": u"手续费池领取",
    "account.op_collateral_bid": u"抵押物竞价",
    "account.op_committee_join": u"加入理事会",
    "account.op_committee_update": u"理事会更新",
    "account.op_custom_op": u"自定义操作",
    "account.op_deal_expired": u"交易过期",
    "account.op_deal_repay": u"交易还款",
    "account.op_deal_update": u"交易更新",
    "account.op_debit_claim": u"直接扣款领取",
    "account.op_debit_create": u"直接扣款创建",
    "account.op_debit_delete": u"直接扣款删除",
    "account.op_debit_update": u"直接扣款更新",
    "account.op_execute_bid": u"执行竞价",
    "account.op_fba_distribute": u"FBA 分配",
    "account.op_fee_pool_fund": u"手续费池注资",
    "account.op_feed_producers_update": u"喂价生产者更新",
    "account.op_feed_publish": u"喂价发布",
    "account.op_global_settle": u"全局结算",
    "account.op_htlc_create": u"HTLC 创建",
    "account.op_htlc_extend": u"HTLC 延长",
    "account.op_htlc_redeem": u"HTLC 赎回",
    "account.op_htlc_redeemed": u"HTLC 已赎回",
    "account.op_htlc_refund": u"HTLC 退款",
    "account.op_issuer_update": u"发行者更新",
    "account.op_offer_accept": u"接受信用",
    "account.op_offer_create": u"信用报价创建",
    "account.op_offer_delete": u"信用报价删除",
    "account.op_offer_update": u"信用报价更新",
    "account.op_order_update": u"订单更新",
    "account.op_override_transfer": u"覆盖式转账",
    "account.op_params_update": u"全局参数更新",
    "account.op_pool_create": u"资金池创建",
    "account.op_pool_delete": u"资金池删除",
    "account.op_pool_deposit": u"资金池存入",
    "account.op_pool_swap": u"资金池兑换",
    "account.op_pool_update": u"资金池更新",
    "account.op_pool_withdraw": u"资金池取出",
    "account.op_proposal_create": u"提案创建",
    "account.op_proposal_delete": u"提案删除",
    "account.op_proposal_update": u"提案更新",
    "account.op_samet_borrow": u"Same-T 借入",
    "account.op_samet_create": u"Same-T 资金池创建",
    "account.op_samet_delete": u"Same-T 资金池删除",
    "account.op_samet_repay": u"Same-T 还款",
    "account.op_samet_update": u"Same-T 资金池更新",
    "account.op_settle_cancel": u"取消结算",
    "account.op_smartcoin_update": u"智能币更新",
    "account.op_ticket_create": u"票据创建",
    "account.op_ticket_update": u"票据更新",
    "account.op_vesting_create": u"归属创建",
    "account.op_vesting_withdraw": u"归属提取",
    "account.op_witness_join": u"加入见证人",
    "account.op_witness_update": u"见证人更新",
    "account.op_worker_create": u"工人创建",
    # Pager + its note. The trailing space on page_total is load-bearing: a
    # computed figure follows it.
    "account.page_total": u"本页合计 ≈ ",
    "account.portfolio_page": u"第 %(page)s 页 / 共 %(pages)s 页",
    "account.prices_cover_this_page": (
        u"价格仅覆盖本页——翻页即可为更多资产估值。"
    ),
    # History one-liners: a finished act, one row, so every line reads 已…
    # rather than as a noun the way the op labels do.
    "account.sum_account_create": u"已注册 %(name)s",
    "account.sum_account_transfer": u"账户已转移给 %(owner)s",
    "account.sum_account_update": u"账户已更新：%(account)s",
    "account.sum_asset_burn": u"已销毁 %(amount)s",
    "account.sum_asset_create": u"已创建资产 %(symbol)s",
    "account.sum_asset_issue": u"已向 %(to)s 发行 %(amount)s",
    "account.sum_asset_settle": u"已请求结算 %(amount)s",
    "account.sum_asset_update": u"已更新资产 %(asset)s",
    "account.sum_authorities": u"已更新 %(account)s 的权限",
    "account.sum_balance_claim": u"已认领 %(amount)s",
    "account.sum_bid": u"已提交竞价：抵押 %(coll)s，债务 %(debt)s",
    "account.sum_blind": u"盲转账（转入 %(in)s，转出 %(out)s）",
    "account.sum_call_update": u"已调整仓位：抵押物 %(coll)s，债务 %(debt)s",
    "account.sum_claim_fees": u"已领取手续费 %(amount)s",
    "account.sum_committee_create": u"已加入理事会：%(account)s",
    "account.sum_committee_update": u"已更新理事会成员 %(account)s",
    "account.sum_custom": u"%(account)s 发起的自定义操作",
    "account.sum_deal_expired": u"交易 %(deal)s 已过期",
    "account.sum_deal_repay": u"已为交易 %(deal)s 还款 %(amount)s",
    "account.sum_deal_update": u"已更新交易 %(deal)s",
    "account.sum_debit_claim": u"已领取扣款 %(amount)s",
    "account.sum_debit_create": u"已授权为 %(to)s 扣款 %(amount)s",
    "account.sum_debit_delete": u"已删除扣款授权 %(perm)s",
    "account.sum_debit_update": u"已更新对 %(to)s 的扣款 %(amount)s",
    "account.sum_execute_bid": u"已执行竞价：抵押 %(coll)s，债务 %(debt)s",
    "account.sum_fee_pool_fund": (
        u"已向 %(asset)s 的手续费池注资 %(amount)s"
    ),
    "account.sum_feed": u"%(publisher)s 已为 %(asset)s 发布喂价",
    "account.sum_feed_producers": (
        u"已为 %(asset)s 设置 %(n)s 个喂价生产者"
    ),
    "account.sum_fill": u"已撮合：支付 %(pays)s，收到 %(receives)s",
    "account.sum_global_settle": u"已对 %(asset)s 全局结算",
    "account.sum_htlc_claimed": u"已领取 HTLC %(id)s",
    "account.sum_htlc_create": (
        u"HTLC %(id)s：%(amount)s，%(from)s → %(to)s"
    ),
    "account.sum_htlc_extend": u"已延长 HTLC %(id)s",
    "account.sum_htlc_redeem": u"已赎回 HTLC %(id)s",
    "account.sum_htlc_refund": u"HTLC %(id)s 已退款",
    "account.sum_issuer_update": u"%(asset)s 的新发行者：%(issuer)s",
    "account.sum_offer_accept": (
        u"已以 %(coll)s 抵押借入 %(amount)s（报价 %(offer)s）"
    ),
    "account.sum_offer_create": u"已在 %(asset)s 中创建信用报价",
    "account.sum_offer_delete": u"已删除报价 %(offer)s",
    "account.sum_offer_update": u"已更新报价 %(offer)s",
    "account.sum_order_cancel": u"已取消订单 %(order)s",
    "account.sum_order_create": u"已挂单卖出 %(sell)s，至少换取 %(buy)s",
    "account.sum_order_update": u"已更新订单 %(order)s",
    "account.sum_pool_create": u"已创建资金池 %(a)s / %(b)s",
    "account.sum_pool_delete": u"已删除资金池 %(pool)s",
    "account.sum_pool_deposit": u"已向资金池 %(pool)s 存入 %(a)s + %(b)s",
    "account.sum_pool_swap": (
        u"已在资金池 %(pool)s 兑换 %(sell)s → 至少 %(buy)s"
    ),
    "account.sum_pool_update": u"已更新资金池 %(pool)s",
    "account.sum_pool_withdraw": u"已从资金池 %(pool)s 提取 %(shares)s",
    "account.sum_proposal_create": u"已提议 %(n)s 项操作",
    "account.sum_proposal_delete": u"已删除提案 %(proposal)s",
    "account.sum_proposal_update": u"已批准提案 %(proposal)s",
    "account.sum_samet_borrow": u"已从资金池 %(fund)s 借入 %(amount)s",
    "account.sum_samet_create": u"已创建 Same-T 资金池，规模 %(amount)s",
    "account.sum_samet_delete": u"已删除 Same-T 资金池 %(fund)s",
    "account.sum_samet_repay": u"已向资金池 %(fund)s 还款 %(amount)s",
    "account.sum_samet_update": u"已更新 Same-T 资金池 %(fund)s",
    "account.sum_settle_cancel": u"已取消 %(amount)s 的结算",
    "account.sum_smartcoin_update": u"已更新智能币 %(asset)s",
    "account.sum_ticket_create": u"已创建票据 %(amount)s",
    "account.sum_ticket_update": u"已更新票据 %(ticket)s",
    "account.sum_transfer": u"转账 %(amount)s：%(from)s → %(to)s",
    "account.sum_transfer_recv": u"收到 %(from)s 转来 %(amount)s",
    "account.sum_transfer_send": u"已向 %(to)s 转出 %(amount)s",
    "account.sum_upgrade": u"已升级 %(account)s",
    "account.sum_vesting_create": u"已为 %(owner)s 归属 %(amount)s",
    "account.sum_vesting_withdraw": u"已提取归属的 %(amount)s",
    "account.sum_whitelist": u"已将 %(account)s 加入名单",
    "account.sum_witness_create": u"已成为见证人：%(account)s",
    "account.sum_witness_update": u"已更新见证人 %(account)s",
    "account.sum_worker_create": u"已创建工人“%(name)s”",

    # ====================================================== account_net (61)
    "account_net.canvas_missing": (
        u"此版本的网络画布不可用；下方表格仍列出每一条连线。"
    ),
    "account_net.class_credit": u"信用",
    "account_net.class_credit_help": u"已接受并已还款的信用报价。",
    "account_net.class_debit": u"直接扣款",
    "account_net.class_debit_help": u"直接扣款授权及据此发生的扣款。",
    "account_net.class_htlc_help": u"哈希时间锁定合约及其更新。",
    # "relation" is a permission line, not a movement of value - the help text
    # says so, so the chip label stays distinguishable from "资金流".
    "account_net.class_override": u"覆盖式转账",
    "account_net.class_override_help": u"由资产发行者支付手续费的转账。",
    "account_net.class_transfer": u"转账",
    "account_net.class_transfer_help": u"账户之间的直接转账。",
    "account_net.class_vesting": u"归属",
    "account_net.class_vesting_help": u"由第三方管理的归属余额。",
    # Graph terms: a hop is one edge traversal, a ring is the neighbourhood the
    # expansion walks. Both are the plain Chinese words, and zh's pool map
    # already says "{s} 距 BTS {n} 跳", so the hop reuses 跳.
    "account_net.depth_1": u"1 跳",
    "account_net.depth_2": u"2 跳",
    "account_net.depth_label": u"深度",
    "account_net.detail_hint": (
        u"点击连线查看详情；点击账户即可打开它。"
    ),
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s 条操作 · "
        u"%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s 条操作 · "
        u"%(kind)s"
    ),
    "account_net.es_bad_account": u"该名称不是本链上的账户。",
    "account_net.es_disabled": (
        u"社区索引已关闭。请在“设置”中开启后再绘制此图。"
    ),
    "account_net.es_unavailable": u"社区索引当前不可达。请稍后重试。",
    "account_net.go": u"绘制网络图",
    "account_net.idle": u"尚未绘制任何内容。",
    "account_net.intro": (
        u"输入一个或多个账户，看看它们向谁转账、向谁放贷、从谁借入。"
        u"数据读取自社区历史索引；不签名任何内容，也不保存任何内容。"
    ),
    "account_net.kind_flow": u"资金流",
    "account_net.kind_relation": u"关联",
    "account_net.more_assets": u" + 另外 %(n)s 个",
    "account_net.need_class": u"请至少开启一种连线类型再绘制。",
    "account_net.need_seeds": u"请至少输入一个账户以绘制网络。",
    "account_net.no_amount": u"无金额",
    "account_net.ring1_label": u"环 1",
    "account_net.ring2_label": u"环 2",
    "account_net.scanning": u"正在读取社区索引…",
    "account_net.seeds_label": u"待绘制的账户",
    "account_net.stale_settings": (
        u"深度或邻居设置已更改——请按“绘制网络图”。"
    ),
    "account_net.status_credit_index": (
        u"从索引解析出 %(n)s 条信用连线（其报价或交易对象已从链上消失）"
    ),
    "account_net.status_credit_missing": (
        u"已跳过 %(n)s 条信用连线（链上未找到报价或交易）"
    ),
    "account_net.status_depth": u"网络深度 %(depth)s",
    "account_net.status_edge_cap": u"显示前 %(n)s 条连线",
    "account_net.status_expanded": u"已展开：%(names)s",
    "account_net.status_expansion_scanned": u"展开后读取 %(n)s 条已索引操作",
    "account_net.status_expansion_truncated": u"展开扫描已截断为最新操作",
    "account_net.status_graph": u"%(nodes)s 个账户 · %(edges)s 条连线",
    "account_net.status_node_cap": u"显示前 %(n)s 个交易对手",
    "account_net.status_scanned": (
        u"从 %(n)s 个账户读取 %(scanned)s 条已索引操作"
    ),
    "account_net.status_self": u"已跳过 %(n)s 笔自转账",
    "account_net.status_shape": u"已跳过 %(n)s 条无法解析的记录",
    "account_net.status_truncated": u"每个账户最新 %(n)s 条操作",
    "account_net.status_unexpanded": u"未展开 %(n)s 个直接交易对手",
    "account_net.status_unknown": u"未找到：%(names)s",
    "account_net.title": u"账户网络图",
    "account_net.twin_amount": u"金额",
    "account_net.twin_class": u"类型",
    "account_net.twin_count": u"操作数",
    "account_net.twin_depth": u"跳数",
    "account_net.twin_empty": (
        u"在已扫描的已索引操作中，这些账户之间没有连线。"
    ),
    "account_net.twin_from": u"发起方",
    "account_net.twin_relation": u"资金流/关联",
    "account_net.twin_span": u"首笔 → 末笔",
    "account_net.twin_summary": u"表格视图（可访问）",
    "account_net.twin_to": u"接收方",

    # ============================================================== asset (33)
    "asset.cer_row": u"核心汇率（CER）",
    "asset.committee_fed_note": (
        u"理事会喂价：所有活跃理事会成员均可发布。"
    ),
    "asset.feed_history_title": u"喂价历史",
    "asset.history_capped": u"显示前 8 位发布者（为速度设定上限）…",
    "asset.history_days": u"范围",
    "asset.history_exchange": u"正在加载交易所与资金池…",
    "asset.history_failed": u"无法加载喂价历史。",
    "asset.history_loading": u"正在加载喂价历史…",
    "asset.history_pub": u"发布者 %(i)s/%(n)s…",
    "asset.invert_btn": u"反转",
    "asset.issue_memo_no_key": u"该账户没有备注密钥。",
    "asset.issue_memo_warning": (
        u"请附上备注——它会以明文存储在链上。"
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"发行者默认为当前查看身份的账户（%(id)s 已锁定，您的账户已解锁）"
        u"——请输入您控制的任意发行者。从账户页面打开时，请在此粘贴该账户名。"
    ),
    "asset.loading_producers": u"正在加载生产者…",
    # "Co-owner" is the same term the shared-account help body uses for the
    # second key holder, so the hint reuses it verbatim.
    "asset.multisig_body": (
        u"如果该资产需要多方批准，直接签名将失败——请改为提议变更，"
        u"并请共同所有者批准（op 23）。"
    ),
    "asset.multisig_coowner_hint": (
        u"共同所有者？请在提案页面提议变更，并请共同所有者批准（op 23）。"
    ),
    "asset.multisig_open_proposals": u"查看提案",
    "asset.multisig_open_txbuilder": u"打开交易构建器",
    "asset.multisig_title": u"共享发行者？请提议变更",
    "asset.new_issuer_field": u"新发行者",
    "asset.no_history": (
        u"此范围内没有历史——发布者发布频率很低；请尝试 90d。"
    ),
    "asset.no_producers": (
        u"尚未发布喂价——发布后生产者会显示在这里。"
    ),
    "asset.orientation_note": u"%(m)s / %(b)s",
    "asset.owner_key_note": u"需要资产所有者的活跃密钥。",
    "asset.plot_feeds": u"绘制喂价图",
    "asset.producer_col": u"生产者",
    "asset.producers_failed": u"无法加载生产者。",
    "asset.producers_live_title": u"喂价生产者",
    "asset.producers_title": u"喂价生产者（op %(op)s）",
    "asset.publish_op19_title": u"发布喂价（op %(op)s）",
    "asset.published_col": u"发布时间",
    # "Viewing as" is the phrase shell.acting_default and every *_viewing_as
    # notice already ships as 当前以…身份查看; this reuses it so principle #9
    # reads one way.
    "asset.viewing_notice": (
        u"当前以 %(name)s（%(id)s）身份查看——解锁后即可签名。"
    ),
    "asset.witness_fed_note": u"见证人喂价：所有活跃见证人均可发布。",

    # ============================================================ market (48)
    "market.adjust_button": u"调整",
    "market.confirm_adjust": u"确认调整",
    "market.discrete_fills": u"笔成交",
    "market.discrete_no_fills": (
        u"暂无成交——请下单或尝试其他交易对。"
    ),
    "market.discrete_swaps": u"笔兑换",
    "market.discrete_tip_account": u"账户",
    "market.discrete_tip_block": u"区块",
    "market.discrete_tip_order": u"订单",
    "market.discrete_tip_price": u"价格",
    "market.discrete_tip_time": u"时间",
    "market.discrete_tip_volume": u"成交量",
    "market.discrete_tip_volume_quote": u"成交量（报价资产）",
    "market.discrete_unavailable": u"离散模式下指标不可用。",
    "market.discrete_volume": u"离散成交量",
    "market.exchange_desk": u"交易台",
    "market.fail_update": u"更新失败。",
    "market.flt_max_price": u"最高价",
    "market.flt_min_price": u"最低价",
    "market.loading_pool_map": u"正在加载图谱…",
    "market.map_aria": u"市场网络图。连线代表过去 24 小时内有成交的市场。",
    "market.map_connects": (
        u"两个资产之间有连线，表示过去 24 小时内两者之间发生过市场成交。"
    ),
    "market.map_connects_fallback": (
        u"两个资产之间有连线，表示存在已注资的资金池。"
        u"24 小时成交情况未获确认（历史不可用）——显示的是已注资的资金池。"
    ),
    "market.map_edge_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24小时成交 %(fills)s 笔"
    ),
    "market.map_hops_empty": u"这些资产在过去 24 小时内没有相关市场成交。",
    "market.map_hops_filtered": (
        u"连线代表过去 24 小时内有成交的市场。显示 %(total)s 个交易对中的 "
        u"%(shown)s 个（最少 24 小时成交 %(min)s 笔）。"
    ),
    "market.map_hops_no_route": u"通过有成交的市场无法到达 BTS。",
    "market.map_hops_note": (
        u"连线代表过去 24 小时内有成交的市场。已显示 %(pairs)s 个交易对。"
    ),
    "market.map_leg_ok": u"{s} 与 BTS 相连",
    "market.map_leg_orphan": u"警告：{s} 没有经由有成交市场的路径！",
    "market.min_fills": u"最少成交数",
    "market.no_filter_match": u"没有符合这些筛选条件的成交。",
    "market.settle_first100": u"显示前 100 条（get_settle_orders 上限 100）",
    "market.settle_no_cancel": (
        u"结算订单无法取消——它们会在结算时执行（在资产强制结算延迟之后）。"
    ),
    "market.tf_discrete": u"离散",
    # The three trailing spaces are load-bearing: an input follows them.
    "market.update_amount": u"待售数量（新的总量） ",
    "market.update_amount_change": u"数量变化",
    "market.update_bad_amount": u"请输入大于零的数量。",
    "market.update_bad_expiry": u"请输入未来的到期时间。",
    "market.update_bad_price": u"请输入大于零的价格。",
    "market.update_broadcasting": u"正在广播更新…",
    "market.update_done": u"订单已更新",
    "market.update_expiry": u"新的到期时间 ",
    "market.update_expiry_change": u"到期时间（旧 → 新）",
    "market.update_no_change": u"没有变更——请修改价格、数量或到期时间。",
    "market.update_price": u"新价格 ",
    "market.update_price_change": u"价格（旧 → 新）",
    "market.update_review": u"复核更新",
    "market.update_title": u"调整订单",

    # ======================================================= market_net (37)
    "market_net.asset_1_field": u"资产 1（任意一端）",
    "market_net.asset_2_field": u"资产 2（任意一端）",
    "market_net.band_title": u"市场网络图",
    "market_net.canvas_label": u"市场网络图。按回车打开该市场。",
    "market_net.clear_btn": u"清除",
    # The short column heads reuse the stats-tab wording verbatim: "24小时 Δ"
    # is market.chg_label / market.stat_chg, and market_net.col_vol repeats
    # market.stat_vol (24小时成交量) rather than inventing a shorter one.
    "market_net.col_change": u"24小时 Δ",
    "market_net.col_last": u"最新",
    "market_net.col_market": u"市场",
    "market_net.col_vol": u"24小时成交量",
    "market_net.collapse": u"收起",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24小时成交 %(fills)s 笔"
    ),
    "market_net.empty": u"此筛选下未找到市场。",
    "market_net.expand": u"展开",
    "market_net.list_btn": u"市场列表",
    "market_net.loading": u"正在加载市场…",
    "market_net.map_empty": u"近期无成交量的市场。",
    "market_net.map_fallback": (
        u"%(pairs)s 个交易对 · %(assets)s 个资产 · 24小时成交未确认"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s 个交易对 · %(assets)s 个资产 · 24小时成交"
    ),
    "market_net.map_ready": u"%(markets)s 个市场 · %(assets)s 个资产",
    "market_net.node_card": u"%(sym)s（%(id)s） · %(n)s 个市场",
    "market_net.offline": (
        u"网络不可用——显示的是缓存的市场。连接后请重试。"
    ),
    "market_net.open_desk": u"打开 %(id)s",
    "market_net.prompt": u"点击节点查看资产，点击连线查看市场。",
    "market_net.ramp": u"24小时成交量：由低到高",
    "market_net.ramp_fills": u"24小时成交：由低到高",
    "market_net.selector_title": u"市场选择器",
    "market_net.spark_label": u"%(id)s 的 7 天趋势",
    "market_net.subtitle": (
        u"按 24 小时成交量排名的头部订单簿市场。选择一行即可打开交易台。"
    ),
    "market_net.title": u"市场",
    "market_net.top_note": (
        u"已探测的 %(probed)s 个中排名前 %(shown)s 名——按 24 小时成交量。"
    ),
    "market_net.twin": u"市场行（%(n)s）",
    "market_net.twin_more": (
        u"显示 %(n)s 个市场中的 %(shown)s 个——请缩小筛选范围以查看更少内容。"
    ),
    "market_net.verdict_full": u"%(markets)s 个市场 · %(assets)s 个资产",
    "market_net.verdict_no_path": (
        u"%(a)s 与 %(b)s 之间没有经由有成交市场的路径"
    ),
    "market_net.verdict_path": (
        u"%(a)s 可经 %(n)s 个有成交的市场到达 %(b)s"
    ),
    "market_net.verdict_star": u"涉及 %(s)s 的市场：%(n)s",
    "market_net.verdict_web": u"从 %(s)s 可达的市场：%(n)s",

    # ========================================================== settings (39)
    "settings.confirm_back": u"返回",
    "settings.confirm_remove_action": u"操作",
    "settings.confirm_remove_hide": u"隐藏该节点（保持隐藏，直至重新添加）",
    "settings.confirm_remove_result": u"结果",
    "settings.confirm_remove_switch": u"当前节点将切换到 %(node)s",
    "settings.confirm_remove_title": u"移除节点？",
    "settings.confirm_remove_unlist": u"从我的列表中移除",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**“发现节点”会在 GitHub 上搜索节点列表，然后探测找到的内容。"
        u"GitHub 和被探测的节点都会看到您的网络地址。结果只是供您审核的候选"
        u"——不会自动添加任何内容。"
    ),
    "settings.geo_note": (
        u"*位置与运营商信息来自 ipaddress.to（https，无需密钥）——它会在被请求时"
        u"看到您的地址；结果在本设备上缓存 24 小时。"
    ),
    "settings.hist_no": u"否",
    "settings.hist_yes": u"是",
    "settings.language_title": u"语言",
    # Signing section. 扩展 (browser extension) and 站点 (site) are this
    # batch's first spellings of those two words in zh.json; 批准 reuses the
    # existing proposal wording, and 撤销 the existing transfer wording.
    "settings.sign_auto": u"自动（可用时使用扩展）",
    "settings.sign_badge": u"扩展签名已启用——详情见“登录”",
    "settings.sign_badge_local": u"本页签名——详情见“登录”",
    "settings.sign_browser": u"始终在本页签名",
    "settings.sign_ext": u"始终使用扩展",
    "settings.sign_ext_absent": (
        u"未在此设备上检测到扩展——签名将在本页完成。"
    ),
    "settings.sign_ext_present": u"已在此设备上检测到扩展。",
    "settings.sign_guide": u"如何安装扩展",
    "settings.sign_mode_browser": u"签名在本页内存中完成。",
    "settings.sign_mode_ext": u"签名在扩展窗口中确认。",
    "settings.sign_mode_ext_page": u"签名保留在扩展内——与网站隔离。",
    "settings.sign_revoke": u"撤销",
    "settings.sign_sites": u"已连接的站点",
    "settings.sign_sites_empty": (
        u"尚无已批准的站点——批准后会显示在这里，并可逐站点撤销。"
    ),
    "settings.sign_sites_story_a": u"示例：位于 ",
    "settings.sign_sites_story_b": (
        u" 的骰子游戏请求以您的账户进行游戏——批准后会将其列在此处，"
        u"且仅绑定该账户。签名仍会每次询问。（该链接不会跳转"
        u"——这是一个虚构示例。）"
    ),
    "settings.sign_title": u"签名",
    "settings.sign_warn": (
        u"在此页面上运行的任何脚本——包括被入侵的托管副本——都可能在解锁期间"
        u"读取您的密钥。请通过扩展进行签名，或运行您自己掌控的副本。"
    ),
    # Node-table column heads. 延迟 / 头部 / 参与度 reuse the node-health
    # wording zh's settings help article already uses.
    "settings.th_chain": u"链",
    "settings.th_handshake": u"握手",
    "settings.th_head": u"头部",
    "settings.th_history": u"历史",
    "settings.th_location": u"位置 *",
    "settings.th_participation": u"参与度",
    "settings.th_ping": u"延迟",
    "settings.th_provider": u"运营商 *",
    "settings.theme_title": u"主题",
}

# Keys whose Chinese value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from ZH. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Chinese crypto UI keeps in Latin: HTLC, NFT,
#     MCR, PMA, UIA, URI, SMA, EMA, BB, PSAR, get_settle_orders;
#   * network ids and sentinels the brief pins: mainnet / testnet / devnet,
#     original-blue / light / dark, "wss://…", "…", "—", "7d";
#   * pure glue a table cell or edge card prints as data: "@ %(price)s ·
#     %(vol)s", "%(desk)s · %(a)s–%(b)s · %(vol)s", "@ %(price)s",
#     "%(first)s → %(last)s", "—" — translating the space inside a glue string
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