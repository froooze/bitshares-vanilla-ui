#!/usr/bin/env python3
"""i18n zh chunk-C: the signing/UX sections zh.json still leaves in English.

Scope: the 37 sections listed below. chunk-A owns account, account_net,
settings, market, market_net and asset; chunk-B owns help, pool, pool_net,
explorer, seo, splash, about, shell and menu. Each of those three scripts
REFUSES anything outside itself, and so does this one. This script is
strictly insert-only:

  * a key already holding a NON-Chinese value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from zh.json, or one whose English master moved, is REFUSED;
  * ZH + KEPT_ENGLISH together must account for EVERY untranslated key of the
    37 sections, so a forgotten string is a refusal, never a silent English.

This is the SAFETY-CRITICAL batch. Most of these strings render DUAL-LINE
inside a signing confirmation dialog: the reader sees the Chinese line with an
English reference one tap away, an asterisk, and a link to the warning. The
hazard specific to Chinese is BREVITY. Chinese is far more compact than
English, so a short rendering can silently DROP a qualifier the English
carried - an amount, a direction, an irreversibility, a permission - and the
reader comparing the two lines has no way to tell the qualifier was ever
there. So wherever compressing could hide one, the fuller Chinese wins:

  * borrow.bids_no_cancel keeps 提交 into 无法取消 (irreversible) plus BOTH
    outcomes, so a reader cannot mistake it for a cancellable action;
  * trade.uc_total is 卖出总量, not 总计: the direction of the sale is the
    qualifier that decides what the number spends;
  * transfer.enclosed_op_note keeps 仅在批准之后 (a permission gate), not a
    bare 内含转账;
  * proposal.delete_proposal_op_24 / vote.retried_prefix keep the plainest
    possible verb and say WHOSE stake signed (以自己身份), because a reader
    must be able to see whose key the action was taken with.

Verb forms match the already-translated neighbours of the SAME flow
(misc.confirm_authority_delete_op_56 "确认删除权限", credit.confirm_offer_delete
"确认删除报价", proposal.review "核对"), so a dialog title never contradicts
the button that opened it.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/validate_translations.py checks);
  G4  structure      same line count and same markdown link hashes (#/...)
                      for every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving
                      in lockstep with the bytes: a claimed key must differ
                      from en, an unclaimed key must still equal en. Filling
                      strings is not verification, so the controller's v2
                      provenance / verified / high_risk fields are never
                      touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  punctuation    no value this batch writes may carry an ASCII or
                      typographic apostrophe, an ideographic space, or a
                      Cyrillic letter. Chinese needs none of them: the strings
                      zh.json already ships use none, and the quotes it does
                      use are the curly pair “ ” (U+201C/U+201D), which this
                      gate does not touch. Every possessive in the English
                      masters ("both sides' transfers", "another account's
                      vote slate") is rephrased in Chinese rather than
                      borrowed with an apostrophe.
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. The sweep runs file-wide,
                      but a hit OUTSIDE the 37 sections is reported as
                      PRE-EXISTING and does not gate this batch: chunk-A /
                      chunk-B own those keys, and an insert-only pass that
                      repaired a neighbour would be exactly the silent edit
                      the scope refusal forbids.
  G9  loanwords      every Latin token a value THIS BATCH writes is declared
                      in LOAN below, or the write is refused. Chinese crypto
                      UIs keep the English word for BitShares, BTS, HTLC,
                      op 23, call_order_update, get_required_fees, WebCrypto,
                      https/localhost and the indicator acronyms SMA/EMA/RSI/
                      MACD - inventing a fake transliteration instead would be
                      worse than the loanword. The gate is batch-scoped on
                      purpose: the rest of zh.json already carries Latin tokens
                      from earlier batches, and re-litigating those is not this
                      file's job.

The honesty surface (i18n.badge_*, i18n.risk_*) IS translated here: it is the
warning a Chinese reader gets about their own Chinese, so leaving it English
would mean the one string that admits the text is machine-written is the one
string no Chinese speaker can read. i18n.risk_show_english is an aria-label
spoken aloud at EVERY signing line, so it is the shortest string in the batch
("显示本行英文原文", 8 characters against English's 39).

Vocabulary is reused verbatim from the part of zh.json that is already
translated, so this batch reads like the rest of the dictionary: 资产, 市场,
资金池, 订单, 限价单, 订单簿, 价格, 手续费, 余额, 钱包, 密码, 节点, 权限,
提案, 见证人, 理事会, 工人, 代理, 选票名单, 归属, 票据, 智能币, 脑密钥,
市场锚定资产, 用户发行资产, 喂价, 交易台, 浏览器, 区块, 精度, 抵押物, 仓位,
易货, 兑换, 质押, 结算, 汇率.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (op 23, 1.10.N, 24 hours, 3 hops, 6 hops, 24 字节)
the translation keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_zh_chunkC.py                 # dry run (asserts)
  python3 tooling/apply_i18n_zh_chunkC.py --apply         # writes zh.json
  python3 tooling/apply_i18n_zh_chunkC.py --verify        # structural re-proof
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

# The 37 sections this batch owns. Everything else belongs to chunk-A or
# chunk-B and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "approval", "assets_feed", "auth", "barter", "borrow", "common", "compat",
    "createaccount", "createworker", "credit", "dashboard", "debit", "eslab",
    "explorer_assets", "gateway", "htlc", "i18n", "instant", "market_ind",
    "misc", "nav", "news", "pool_detail", "pools", "prediction", "proposal",
    "ticket", "tour", "trade", "transfer", "trollbox", "txbuilder",
    "unlockconfirm", "vesting", "viewing", "vote", "xrate",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from ZH below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# None of them live in this batch's sections (the settings keys live in
# chunk-A's), so the list is a file-wide watchdog rather than a scope guard -
# a drift in someone else's section is still reported, never repaired.
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
# so "Same-T", "call_order_update" and "voting_account" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")
# G9 scoping: in-app ADDRESSES are data, exactly like a placeholder. The
# markdown destinations ("[label](#/pools)") and the bare route / deep-link
# references a string makes in prose ("(#/about)", "?dialog=N") are stripped
# before the Latin sweep so a route hash cannot be mistaken for a loanword.
# Nothing is lost: G4 fails hard if any of these bytes differs from the English
# master, so the strip hides a Latin token from a sweep, never a drift from the
# gate that owns these bytes.
LINK_DEST = re.compile(r"\]\([^)]*\)")
ROUTE_REF = re.compile(r"(?:#/|\?[A-Za-z_][A-Za-z0-9_]*=)\S*")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# token a Chinese crypto UI prints in Latin; anything else has to be Chinese.
# Entries that no value actually uses are pruned, so the allowlist cannot rot
# into a blanket permission.
LOAN = frozenset((
    # Chain name, asset symbol and protocol acronym, all shipped in Latin.
    "BTS", "BitShares", "HTLC",
    # The operation numbers the confirm dialogs are titled by, and the two
    # chain field names those dialogs quote. op is the abbreviation the whole
    # dictionary keeps; N is the id wildcard in 1.10.N / 1.3.N / 1.2.N.
    "call_order_update", "N", "op", "voting_account",
    # id: the dictionary's own word for an object identifier, already shipped
    # in nine zh strings (misc.account_or_authority_id 账户或权限 id).
    "id",
    # The two sides of a pool route or a barter: A and B name the legs, which
    # is data in the string ("fee-payer = A 方", "A 计 B / B 计 A").
    "A", "B",
    # Technical indicator acronyms the wallet prints as overlays, exactly as
    # every crypto chart does.
    "MACD", "RSI", "EMA", "SMA",
    # Platform names a compatibility warning has to name to be actionable.
    "WebCrypto", "localhost",
    # Protocols and hosts: the advice is "serve over one of these", so they
    # are DATA inside a Chinese sentence, not prose to translate.
    "http", "https",
    # The chart unit. K 线 is the shipped zh word (market_ind.candle_count),
    # but the letter rides along because the master says "candles".
    "K",
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
        # A count keeping its English unit suffix ("24h", "1024") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # without changing the number the reader compares against the figure
        # beside it.
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
    # are printed loudly and never repaired here: chunk-A / chunk-B own them,
    # and an insert-only batch that "fixed" a neighbour would be the silent
    # edit the scope refusal exists to prevent. Only `bad` - problems this
    # batch can answer for - gates the exit code.
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
        if k.split('.')[0] in SECTIONS and d.get(k) == e[k]
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
    # values kept byte-identical on purpose (loanwords, brands, ids, glue)
    # stay UNCLAIMED, which is the honest state for them. Nothing else in
    # _meta moves - filling strings is not verification, so the controller's
    # v2 provenance/verified/high_risk fields stay untouched.
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

    print("zh chunk-C: %d planned, %d differ from en, %d intentionally identical"
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
    # ========================================================= approval (20)
    # The dApp approval sheet. Its verbs are deliberately plain: 批准 / 拒绝
    # are the only two outcomes, and the reader must not have to guess which
    # one a button performs before they tap it.
    "approval.account": u"账户：",
    "approval.approve": u"批准",
    "approval.approved": u"已批准并广播。",
    "approval.chain": u"链：",
    "approval.close": u"关闭",
    "approval.denied": u"已拒绝。",
    "approval.deny": u"拒绝",
    # The trailing space is load-bearing: the remaining time follows it.
    "approval.expires_in": u"有效期还剩 ",
    "approval.load_failed": u"无法加载该审批。",
    "approval.loading": u"正在加载审批…",
    # The locked variant must name the password, not just say "locked": the
    # approval is gated on it.
    "approval.locked_note": u"会话已锁定 — 请输入钱包密码以批准。",
    "approval.no_fields": u"没有可显示的字段。",
    "approval.no_reply": u"签名方没有回复。",
    "approval.no_runtime": u"扩展运行时缺失。",
    "approval.password": u"密码",
    "approval.remember": u"记住此站点所用的账户",
    "approval.site_prefix": u"站点：",
    "approval.title": u"批准签名",
    "approval.unknown_intent": u"未找到审批请求。",
    "approval.wallet_title": u"本钱包请求签名",

    # ============================================================= auth (7)
    # The multisig explainer. "only signing needs the password" is the whole
    # promise of principle #9, so it keeps its own clause at the end.
    "auth.multisig_body": (
        u"本钱包只持有一把密钥。共享账户需要提案 + 共同所有者批准，"
        u"并以提案 id（1.10.N）协调。浏览是公开的；只有签名才需要密码。"
    ),
    "auth.multisig_open_proposals": u"查看提案",
    "auth.multisig_open_txbuilder": u"打开交易构建器",
    # "on the proposal page, or co-sign via the transaction builder" is two
    # routes, and the reader needs both to know where to go.
    "auth.multisig_step_approve": (
        u"共同所有者在提案页面上批准（op 23），或通过交易构建器联签。"
    ),
    "auth.multisig_step_propose": (
        u"提议该操作（转账有“发送/提议”；资产、易货与借贷都链向提案）。"
    ),
    "auth.multisig_step_share": u"把 1.10.N 提案 id 分享给共同所有者。",
    "auth.multisig_title": u"共享 / 多签账户",

    # ========================================================== barter (7)
    "barter.confirm_barter_proposal_op_22": u"确认易货提案（op %(op)s）",
    "barter.propose_barter_op_22": u"提议易货（op %(op)s）",
    "barter.step_build": u"构建",
    "barter.step_preview": u"预览",
    "barter.step_propose": u"提议",
    # "both sides' transfers" is rephrased, not transliterated: the English
    # possessive has no Chinese form and an apostrophe is banned by G7. The
    # fee-payer stays spelled out - it is the number a reader must not lose.
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"双方原子兑换预览。请先预览，然后“提议”会把双方的转账装进同一个提案"
        u"（op %(op)s，手续费支付方 = A 方）。"
    ),
    "barter.uc_title": u"解锁以签名",

    # ========================================================== borrow (9)
    "borrow.adjust": u"调整",
    "borrow.adjust_position_op_3": u"调整仓位（op %(op)s）",
    # Irreversibility is the whole sentence: a reader must see BOTH that the
    # bid cannot be taken back and what happens instead (it fills or expires).
    "borrow.bids_no_cancel": u"竞价一旦提交就无法取消 — 要么成交，要么过期。",
    "borrow.close_position": u"关闭仓位",
    # "Topping up ... or repaying debt adjusts op N on your call order" is the
    # explanation of why the same op serves both directions; keep both verbs.
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"保证金仓位以抵押物为担保借入智能币。追加抵押物或偿还债务，"
        u"都会在您的抵押单上调整 op %(op)s（call_order_update）。"
    ),
    "borrow.open_a_new_position_op_3": u"新建仓位（op %(op)s）",
    "borrow.repay_full": u"全额还款",
    "borrow.settlement_bids_op_45": u"结算竞价（op %(op)s）",
    "borrow.uc_title": u"解锁以签名",

    # ========================================================= common (2)
    "common.page_n": u"第 %(n)s 页",
    "common.unknown_asset": u"未知资产。",

    # ========================================================= compat (1)
    # The advice is only actionable if it names the protocols verbatim: the
    # reader has to type https or localhost, not a translation of them.
    "compat.insecure_hint": (
        u"此地址不是安全上下文，浏览器因此不提供 WebCrypto。"
        u"浏览器本身是新的 — 请通过 https 或 localhost 提供，或直接打开该文件。"
    ),

    # ==================================================== createaccount (3)
    # The wizard's step names. 脑密钥 is the shipped zh word in every other
    # slot on this very page, so the step name uses it too: a wizard that
    # spelled the same concept two ways on one screen would be the reader's
    # first proof the translation is machine-made.
    "createaccount.step_brainkey": u"脑密钥",
    "createaccount.step_name": u"名称",
    "createaccount.step_register": u"注册",

    # ===================================================== createworker (3)
    "createworker.confirm_worker_op_34": u"确认工人（op %(op)s）",
    # The last clause is a permission fact, not a nicety: workers are created
    # by a direct op, so there is no proposal and no approval round. Dropping
    # it would make a reader wait for co-signers who are never asked.
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"起草工人（op %(op)s）。预览是实时的；核对会报出实时手续费，"
        u"随后“签名并发送”直接广播 op %(op)s — "
        u"工人由直接操作创建，而不是通过提案。"
    ),
    "createworker.worker_preview_op_34": u"工人预览（op %(op)s）",

    # ========================================================= credit (3)
    "credit.my_deals_borrower": u"我的借贷（借入方）",
    "credit.no_borrower_deals": (
        u"暂无借入方借贷 — 您针对某个报价借入后，借贷就会出现在这里。"
    ),
    "credit.uc_title": u"解锁以签名",

    # ====================================================== dashboard (2)
    "dashboard.tagline": u"免费浏览市场 — 创建钱包即可交易。",
    "dashboard.welcome": u"用您自己掌握的密钥交易 BTS",

    # =========================================================== debit (2)
    "debit.uc_order": u"订单",
    "debit.uc_title": u"解锁以签名",

    # =========================================================== eslab (1)
    # Paraphrases eslab.hint_holders and eslab.hint_agg, which ship the same
    # "raw integer" warning in the same words.
    "eslab.hint_donors": u"窗口期内的计数；合计为原始整数 — 请除以资产精度。",

    # ========================================================= gateway (2)
    # The trailing space is load-bearing: the two halves are concatenated.
    "gateway.intro_a": u"请把外部币种发送到所显示的地址。本页不发送任何东西。 ",
    "gateway.intro_b": u"提现将在转账页完成，并附实时手续费预览。",

    # ============================================================ htlc (3)
    # The two outcomes (redeem or be refunded) and the timing rule are what
    # make this safe to read; neither is compressed away.
    "htlc.list_sub": (
        u"把资金锁到某个哈希 — 接收方须在到期前用密钥赎回，"
        u"否则您将获得退款。任何人可读；仅在签名时才询问密码。"
    ),
    # htlc.title stays "HTLC": the acronym is the on-chain object name, the
    # same decision chunk-B took for menu.p_htlc.
    "htlc.uc_title": u"解锁以签名",

    # ============================================================= i18n (7)
    # The honesty surface. A reader who cannot read the warning in their own
    # language is not warned: this is the one string that admits the text is
    # machine-written, so it must not stay English. The phrasing is the one
    # help.topic_translation-limitations_body already uses (机器写成 /
    # 未经人工核对), so the badge and the article say the same thing.
    "i18n.badge_body": (
        u"这些译文由机器写成，未经人工核对。签名页面上标有 * 的行还会显示英文原文。"
    ),
    # i18n.badge_chip stays "i18n": it is the chip's own name, not prose.
    "i18n.badge_details": u"这是什么意思",
    "i18n.badge_improve": u"帮助改进这份译文",
    "i18n.badge_label": u"翻译状态：机器翻译，未经人工核对",
    "i18n.risk_about_translations": u"关于这些译文",
    # Spoken aloud by a screen reader at EVERY signing line, so this is the
    # shortest string in the batch: 8 characters against English's 39.
    "i18n.risk_show_english": u"显示本行英文原文",

    # ========================================================== instant (3)
    "instant.preview_balances_note": (
        u"正以 %(name)s（%(id)s）身份预览 — 未检查余额。"
        u"请在签名前解锁，以核对您自己的余额。"
    ),
    "instant.uc_title": u"解锁以签名",
    "instant.unlock_sign": u"解锁并签名",

    # ===================================================== market_ind (3)
    "market_ind.count_capped": u"窗口已截断",
    "market_ind.count_note": u"%(count)s × %(bucket)s 根 K 线",
    # "actual of requested" becomes "requested 中的 actual" so the reader
    # keeps the denominator: a bare "X" would hide how much is missing.
    "market_ind.count_partial": (
        u"%(requested)s 中的 %(actual)s × %(bucket)s 根 K 线"
    ),

    # ============================================================= nav (4)
    # The shell strip. 信用 / 保证金 / 市场 / 资金池 are the stems the pages
    # themselves are titled with (credit.title 信用报价, borrow.borrow_margin
    # 借贷（保证金）, pools.title 流动性资金池), so the strip and the page
    # heading name one thing.
    "nav.credit": u"信用",
    "nav.margin": u"保证金",
    "nav.markets": u"市场",
    "nav.pools": u"资金池",

    # ============================================================ news (1)
    "news.explorer_blocks_and_transactions": u"浏览这条链",

    # ===================================================== pool_detail (8)
    "pool_detail.candle_capped": u"窗口已截断",
    "pool_detail.candle_count": (
        u"%(swaps)s 笔兑换 · %(count)s × %(bucket)s 根 K 线"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s 笔兑换 · %(requested)s 中的 %(actual)s × %(bucket)s 根 K 线"
    ),
    "pool_detail.invert": u"反转",
    # A and B name the two pool legs, so they stay Latin inside the Chinese -
    # the same two letters the pool table's columns already use.
    "pool_detail.invert_label": u"反转图表方向（A 计 B / B 计 A）",
    # Both conditions are load-bearing: the line means "funded AND traded in
    # 24h", and a reader who sees only one of them over-reads the map.
    "pool_detail.map_connects": (
        u"当存在有资金的资金池，且过去 24 小时内发生过成交时，"
        u"才会用一条连线连接两个资产。"
    ),
    "pool_detail.map_connects_fallback": (
        u"当存在有资金的资金池时，即用一条连线连接两个资产。"
        u"24 小时成交活跃度未经确认（历史不可用）— 因此只显示有资金的资金池。"
    ),
    "pool_detail.map_min_swaps": u"（最少 %(min)s 笔兑换）",

    # ============================================================ pools (1)
    # 资金池选择器 mirrors market_net.selector_title (市场选择器).
    "pools.selector_title": u"资金池选择器",

    # ====================================================== prediction (1)
    "prediction.uc_title": u"解锁以签名",

    # ======================================================== proposal (7)
    "proposal.confirm_proposal_create_op_22": u"确认创建提案（op %(op)s）",
    # Deletion is irreversible; the verb stays the plainest possible one, the
    # same one proposal.remove (移除) and misc.confirm_authority_delete_op_56
    # already use, so the dialog title cannot soften it.
    "proposal.confirm_proposal_delete_op_24": u"确认删除提案（op %(op)s）",
    "proposal.delete_proposal_op_24": u"删除提案（op %(op)s）",
    "proposal.multisig_story": (
        u"共享账户？由一位共同所有者提议，分享 1.10.N 的 id，"
        u"其余人在下方批准。涉及多个操作或多个设备的工作请在交易构建器中继续。"
    ),
    "proposal.open_txbuilder": u"打开交易构建器",
    "proposal.viewing_as": (
        u"正以 %(name)s（%(id)s）身份查看 — 解锁后以您本人身份操作。"
    ),

    # ============================================================= tour (7)
    "tour.away_note": u"在交易所交易台上 — 打开它即可看到此处的高亮。",
    "tour.s1_body": (
        u"每个页面都无需登录即可读取公开链上数据。先打开一个市场 — "
        u"您的密码仅在签名时才询问。"
    ),
    "tour.s1_title": u"免费浏览一切，本地签名",
    "tour.s3_body": (
        u"价格 K 线、成交量与深度，再加上指标菜单：SMA 与 EMA 等叠加指标，"
        u"RSI、MACD 与随机指标等振荡指标。打开交易所即可实时查看。"
    ),
    "tour.s3_title": u"查看实时价格图表",
    "tour.s4_body": (
        u"买入与卖出面板接受任意数字，供您练习。在您核对并用已解锁的钱包签名之前，"
        u"不会有任何东西离开您的设备。打开交易所即可试用。"
    ),
    "tour.s4_title": u"练习买入与卖出",

    # ============================================================ trade (7)
    # 单个 pairs with the shipped 阶梯 (trade.tab_scaled): the two tabs are
    # single vs scaled orders, not buy vs sell (those are the other two tabs).
    "trade.tab_single": u"单个",
    "trade.uc_amount": u"金额",
    "trade.uc_orders": u"订单",
    "trade.uc_price": u"价格",
    "trade.uc_range": u"价格区间",
    "trade.uc_title": u"解锁以继续",
    # The direction is the qualifier: 卖出总量 says what the number spends,
    # where a bare 总计 would not.
    "trade.uc_total": u"卖出总量",

    # ========================================================= transfer (6)
    "transfer.confirm_proposal_title": u"确认提案（op %(op)s）",
    # "executes only after approvals" is a permission gate, not a footnote:
    # without it a reader could sign once and assume the transfer moved.
    "transfer.enclosed_op_note": (
        u"内含操作：转账（op %(op)s）— 仅在批准之后才会执行。"
    ),
    "transfer.propose_notice_locked": (
        u"锁定期间提议人默认为 %(name)s（%(id)s）— 解锁后以您本人身份操作。"
    ),
    "transfer.share_needs_to_amount": u"可分享链接需要收款人和金额。",
    "transfer.uc_title": u"解锁以继续",
    "transfer.unlock_sign": u"解锁并复核",

    # ========================================================= trollbox (8)
    "trollbox.bytes_unit": u"字节",
    "trollbox.channel_row": u"频道",
    "trollbox.fee": u"手续费",
    "trollbox.language_row": u"语言",
    "trollbox.message_row": u"消息",
    "trollbox.post_review_title": u"复核消息",
    "trollbox.size_row": u"大小",
    "trollbox.unlock_post": u"解锁并发布",

    # ======================================================= txbuilder (1)
    "txbuilder.link_proposals": u"提案",

    # ==================================================== unlockconfirm (5)
    "unlockconfirm.cancel": u"返回",
    "unlockconfirm.empty_password": u"请输入钱包密码。",
    "unlockconfirm.password": u"密码",
    "unlockconfirm.unlock_failed": u"解锁失败。",
    "unlockconfirm.unlock_post": u"解锁并发布",

    # ========================================================= viewing (1)
    # The four other locales render the master's hyphenated "account-name" as
    # a translated shape; a Chinese reader gets the plain word the rest of the
    # dictionary uses (common.account_name 账户名), because the hyphen in the
    # English is decoration, not a format the field enforces.
    "viewing.dialog_placeholder": u"账户名",

    # ============================================================ vote (9)
    "vote.ballot_intro": (
        u"您的质押选出见证人与理事会，并为工人提供资金 — "
        u"下方所有计数与份额都是实时链上读取。"
    ),
    "vote.confirm_witness_update_op_21": u"确认见证人更新（op %(op)s）",
    "vote.direct_note": u"已直接发布投票（voting_account %(id)s）。",
    "vote.in_sync": u"选票名单与链上一致 — 没有需要发布的内容。",
    # "another account's vote slate" is rephrased rather than transliterated;
    # G7 bans the apostrophe the English possessive needs.
    "vote.proxies_follow_another_account_s_slate_re": (
        u"代理会跟随另一账户的选票名单 — 设置代理前，请先了解投票是如何运作的。"
    ),
    "vote.proxy_follows": u" — 您的质押跟随该账户；下方的选票名单为只读。",
    # "as self" says WHOSE stake signed. Both retry strings must name it: a
    # reader who only sees 代理模式 rejected cannot tell whether the vote
    # went out with their key or with the proxy's.
    "vote.retried_prefix": (
        u"节点拒绝了 %(mode)s 代理模式，因此投票已以自己身份发布"
        u"（voting_account %(id)s）。"
    ),
    "vote.retry_self": u"节点拒绝了 %(mode)s 代理模式 — 正以自己身份重试一次…",

    # =========================================================== xrate (18)
    "xrate.add_btn": u"添加一列",
    "xrate.asset_col": u"资产",
    "xrate.base_pinned": u"BTS 是基础列，无法移除。",
    "xrate.empty": u"本链上距 BTS 3 跳以内没有资金池资产。",
    # The second clause is a safety promise: nothing is signed, nothing is
    # stored. It is the reason the page is safe to browse while locked.
    "xrate.intro": (
        u"每个资金池资产都按其最近一次兑换定价，并经资金池图交叉换算。"
        u"不签名，也不存储任何内容。"
    ),
    "xrate.load_failed": u"无法加载交叉汇率：",
    "xrate.loading": u"正在读取资金池…",
    "xrate.no_route_col": u"6 跳资金池路径内没有通往 %(sym)s 的路线。",
    "xrate.refresh_btn": u"刷新价格",
    # The trailing space is load-bearing: the asset symbol follows it.
    "xrate.remove_btn": u"移除 ",
    "xrate.retry_btn": u"重试",
    "xrate.show_all": u"显示全部资产",
    "xrate.status": (
        u"%(pools)s 个资金池 · 3 跳以内 %(assets)s 个资产 · "
        u"%(total)s 个资金池中，有 %(done)s 个记录了最近一次兑换"
    ),
    "xrate.title": u"交叉汇率",
    "xrate.token_label": u"添加报价代币",
    "xrate.unknown_token": u"没有名为 %(sym)s 的资金池资产。",
    # "a leg on this route" - a leg is one pool hop, the same word the barter
    # page uses for its two sides (barter.no_legs 无分支).
    "xrate.unpriced": u"此路径上的某一条分支尚无记录的兑换。",
}

KEPT_ENGLISH = {
    # ---- empty-state dashes (the wallet's own «—» for "no value")
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",

    # ---- machine sentinels / example payloads a user overwrites
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "xrate.token_placeholder": u"USD, CNY, BTC…",

    # ---- acronyms naming an on-chain concept or a UI term
    "htlc.title": u"HTLC",
    "i18n.badge_chip": u"i18n",
    "misc.id": u"ID",
    "proposal.id": u"ID",
    "ticket.id": u"ID",
    "vesting.id": u"ID",
    "vote.url": u"URL",
}


if __name__ == "__main__":
    sys.exit(main())