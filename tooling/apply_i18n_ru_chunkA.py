#!/usr/bin/env python3
"""i18n ru chunk-A: fill the six desk sections ru.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ru.json, or one whose English master moved, is REFUSED;
  * RU + KEPT_ENGLISH together must account for EVERY untranslated key of the
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
  G7  script + quotes  no word in ru.json mixes Cyrillic and Latin letters
                      (the homoglyph a transliterated loanword invites - "ордер"
                      is impossible in the shipped file and stays that way), and
                      no value this batch writes may carry an ASCII or
                      typographic apostrophe: Russian quotes with «...», and the
                      14 apostrophes already in the file all sit in untranslated
                      English. This is the Russian sibling of the pt batch's
                      "zero apostrophes" gate.

G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: ru.json already ships "x·y=k" in
                      pool_detail.pool_curve, outside this batch's six
                      sections, and the file-wide sweep in verify() would
                      otherwise fail on someone else's honest formula.

Vocabulary is reused verbatim from the part of ru.json that is already
translated, so this batch reads like the rest of the dictionary instead of like
a second dictionary: аккаунт (m.), актив (m.), баланс, ордер, исполнение, цена,
количество, предложение, комиссия, комитет, заверитель, работник, эмитент,
поставщик (published assets), публикатор (feed publisher), залог, вестинг,
смарткоин, битассет, тикет, пул, своп, стейк, полномочие, кошелёк, нода, цепь,
деск, стакан, фид, апгрейд, пожизненный член, ончейн, тестнет, майннет, браузер,
фаусет, брейнкей. Nothing is invented where a Russian crypto UI keeps the English
word - DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy, Smartcoin, Pool,
Brainkey, Feed, NFT, PMA, UIA, MCR, CER, SMA, EMA, BB, PSAR, the get_* call
names - and the run prints every value that stays identical to en so a reviewer
checks the list instead of guessing.

The op labels (account.op_*) follow the nominal pattern the translated ones
already established - "Account create" ships as "Создание аккаунта", "Fill
order" as "Исполнение ордера" - so a history column reads as a list of nouns.
The account.sum_* history lines keep the shipped past-tense voice ("Registered
%(name)s" is a finished act, not a noun), because they describe one row, not a
column.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where a
translated string quotes a number the English quotes (first 8 publishers, first
100, op 19, op 23, 7-day, 24h, 90d) it keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ru_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ru_chunkA.py --apply         # writes ru.json
  python3 tooling/apply_i18n_ru_chunkA.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
RU_PATH = os.path.join(BASE, "ru.json")

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from RU below so they keep the
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
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
LATIN = re.compile(r"[A-Za-z]")
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    A middle dot is clean when it is space-separated, as it is everywhere in
    this dictionary - or when both neighbours are alphanumeric, which is
    algebraic notation (ru.json ships "x·y=k"). Anything else is a stray dot
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


def mixed_script_words(value):
    """Return every token that mixes Cyrillic and Latin letters.

    Russian transliterates most crypto terms (ордер, фид, пул), so a single
    Latin letter typed into a Cyrillic word is invisible in review and wrong
    on screen. The shipped ru.json has zero such words; this batch must not
    add the first one.
    """
    return sorted(
        {w for w in WORD.findall(value)
         if CYRILLIC.search(w) and LATIN.search(w)}
    )


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


def check_batch(en_flat, key, value, problems):
    """G1-G4, G7, G8 + punctuation hygiene for one key/value pair."""
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
            "line count changed: %s (en %d, ru %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )
    for word in mixed_script_words(value):
        problems.append("mixed-script word %r in %s" % (word, key))


def check_apostrophe(batch, problems):
    """G7 (Russian half): no value this batch writes may carry an apostrophe.

    Russian quotes with «...» - ru.json already uses it 25 times - and the 14
    ASCII apostrophes still in the file all sit inside untranslated English.
    A translated line that grew one would be the only such spelling in the
    dictionary.
    """
    for key, value in sorted(batch.items()):
        if APO_ASCII in value:
            problems.append("G7: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7: typographic apostrophe in %s" % key)


def verify():
    """Structural re-proof of the shipped file against the en master."""
    ru, en = load(RU_PATH), load(EN_PATH)
    d, e = flat(ru), flat(en)
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            check_batch(e, key, d[key], bad)
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
            bad.append(
                "suspicious code point U+%04X in %s" % (ord(hit), key)
            )
        for word in mixed_script_words(d[key]):
            bad.append("mixed-script word %r in %s" % (word, key))
    check_apostrophe(RU, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(RU) if d.get(k) == e.get(k)]
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
        and k not in RU and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(RU) - len(same), len(RU)))
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
    meta = ru.get("_meta", {})
    print("  _meta version=%r untranslated=%r translated=%d entries"
          % (meta.get("version"), meta.get("untranslated"),
             len(meta.get("translated", []))))
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
    raw = open(RU_PATH, encoding="utf-8").read()
    ru = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(ru, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: ru.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(ru))
    before_meta = json.dumps(ru["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(RU.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in ru.json: %s" % key)
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
        deep_set(ru, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(RU) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (RU and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(RU) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in ru.json: %s" % key)
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

    check_apostrophe(RU, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(ru)
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
    meta = ru["_meta"]
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
    added = sorted(k for k in RU
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

    print("ru chunk-A: %d planned, %d differ from en, %d intentionally identical"
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

    with open(RU_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ru, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/ru.json")
    return 0


RU = {
    # =========================================================== account (149)
    # The shared-account line: "active" and "owner" are the two weight types,
    # the same Latin pair auth.a_local_wallet_creates_a_brainkey_on_this_dev
    # already ships in Russian prose, so they stay Latin here.
    "account.draw_network": u"Построить сеть",
    "account.multisig_checking": u"Проверка полномочий…",
    "account.multisig_open_txbuilder": u"Открыть конструктор транзакций",
    "account.multisig_shared": (
        u"Общий аккаунт — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        u"Один ключ — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"Общий аккаунт? Предложения — на странице предложений."
    ),
    "account.multisig_unavailable": (
        u"Полномочия недоступны — предложения всё равно перечислены на "
        u"странице предложений."
    ),
    "account.multisig_view_proposals": u"Смотреть предложения",
    # Operation labels. Nominal, like the translated ones ("Создание аккаунта",
    # "Исполнение ордера") so a history column reads as a list of nouns.
    "account.op_assert_op": u"Утверждение",
    "account.op_asset_burn": u"Сжигание актива",
    "account.op_asset_issue": u"Выпуск актива",
    "account.op_asset_settle": u"Погашение актива",
    "account.op_asset_update": u"Обновление актива",
    "account.op_authority_create": u"Создание полномочия",
    "account.op_authority_delete": u"Удаление полномочия",
    "account.op_authority_update": u"Обновление полномочия",
    "account.op_balance_claim": u"Требование баланса",
    "account.op_blind_from": u"Перевод из слепой",
    "account.op_blind_to": u"Перевод в слепую",
    "account.op_blind_transfer": u"Слепой перевод",
    "account.op_claim_fees": u"Вывод комиссий",
    "account.op_claim_pool": u"Вывод из пула комиссий",
    "account.op_collateral_bid": u"Бид под залог",
    "account.op_committee_join": u"Вступление в комитет",
    "account.op_committee_update": u"Обновление члена комитета",
    "account.op_custom_op": u"Пользовательская операция",
    "account.op_deal_expired": u"Истечение сделки",
    "account.op_deal_repay": u"Погашение сделки",
    "account.op_deal_update": u"Обновление сделки",
    "account.op_debit_claim": u"Списание прямого дебита",
    "account.op_debit_create": u"Создание прямого дебита",
    "account.op_debit_delete": u"Удаление прямого дебита",
    "account.op_debit_update": u"Обновление прямого дебита",
    "account.op_execute_bid": u"Исполнение бида",
    "account.op_fba_distribute": u"Распределение FBA",
    "account.op_fee_pool_fund": u"Пополнение пула комиссий",
    "account.op_feed_producers_update": u"Обновление поставщиков фидов",
    "account.op_feed_publish": u"Публикация фида",
    "account.op_global_settle": u"Глобальное погашение",
    "account.op_htlc_create": u"Создание HTLC",
    "account.op_htlc_extend": u"Продление HTLC",
    "account.op_htlc_redeem": u"Погашение HTLC",
    "account.op_htlc_redeemed": u"Получение HTLC",
    "account.op_htlc_refund": u"Возврат HTLC",
    "account.op_issuer_update": u"Обновление эмитента",
    "account.op_offer_accept": u"Приём кредита",
    "account.op_offer_create": u"Создание кредитного предложения",
    "account.op_offer_delete": u"Удаление кредитного предложения",
    "account.op_offer_update": u"Обновление кредитного предложения",
    "account.op_order_update": u"Обновление ордера",
    "account.op_override_transfer": u"Перевод с переопределением",
    "account.op_params_update": u"Обновление глобальных параметров",
    "account.op_pool_create": u"Создание пула",
    "account.op_pool_delete": u"Удаление пула",
    "account.op_pool_deposit": u"Внесение в пул",
    "account.op_pool_swap": u"Своп в пуле",
    "account.op_pool_update": u"Обновление пула",
    "account.op_pool_withdraw": u"Вывод из пула",
    "account.op_proposal_create": u"Создание предложения",
    "account.op_proposal_delete": u"Удаление предложения",
    "account.op_proposal_update": u"Обновление предложения",
    "account.op_samet_borrow": u"Заём Same-T",
    "account.op_samet_create": u"Создание фонда Same-T",
    "account.op_samet_delete": u"Удаление фонда Same-T",
    "account.op_samet_repay": u"Возврат Same-T",
    "account.op_samet_update": u"Обновление фонда Same-T",
    "account.op_settle_cancel": u"Отмена погашения",
    "account.op_smartcoin_update": u"Обновление смарткоина",
    "account.op_ticket_create": u"Создание тикета",
    "account.op_ticket_update": u"Обновление тикета",
    "account.op_vesting_create": u"Создание вестинга",
    "account.op_vesting_withdraw": u"Вывод из вестинга",
    "account.op_witness_join": u"Вступление в заверители",
    "account.op_witness_update": u"Обновление заверителя",
    "account.op_worker_create": u"Создание работника",
    # Pager + its two notes. "turn the page" is the pager action, so the verb
    # is "листать", not "перевернуть страницу" (which reads as paper).
    "account.page_total": u"Итого на странице ≈ ",
    "account.portfolio_page": u"Страница %(page)s из %(pages)s",
    "account.prices_cover_this_page": (
        u"Цены покрывают эту страницу — листайте дальше, чтобы оценить "
        u"больше активов."
    ),
    # History one-liners: a finished act, one row, present tense is wrong.
    "account.sum_account_create": u"Зарегистрирован %(name)s",
    "account.sum_account_transfer": u"Аккаунт передан %(owner)s",
    "account.sum_account_update": u"Аккаунт обновлён: %(account)s",
    "account.sum_asset_burn": u"Сожжено %(amount)s",
    "account.sum_asset_create": u"Создан актив %(symbol)s",
    "account.sum_asset_issue": u"Выпущено %(amount)s на %(to)s",
    "account.sum_asset_settle": u"Запрошено погашение %(amount)s",
    "account.sum_asset_update": u"Обновлён актив %(asset)s",
    "account.sum_authorities": u"Обновлены полномочия %(account)s",
    "account.sum_balance_claim": u"Требование баланса на %(amount)s",
    "account.sum_bid": u"Бид %(coll)s под %(debt)s",
    "account.sum_blind": u"Слепой перевод (вход %(in)s, выход %(out)s)",
    "account.sum_call_update": (
        u"Позиция скорректирована: залог %(coll)s, долг %(debt)s"
    ),
    "account.sum_claim_fees": u"Получено комиссий %(amount)s",
    "account.sum_committee_create": u"Стал членом комитета: %(account)s",
    "account.sum_committee_update": u"Обновлён член комитета %(account)s",
    "account.sum_custom": u"Пользовательская операция от %(account)s",
    "account.sum_deal_expired": u"Срок сделки %(deal)s истёк",
    "account.sum_deal_repay": u"Погашено %(amount)s по сделке %(deal)s",
    "account.sum_deal_update": u"Обновлена сделка %(deal)s",
    "account.sum_debit_claim": u"Списано %(amount)s по прямому дебиту",
    "account.sum_debit_create": u"Разрешён дебет %(amount)s для %(to)s",
    "account.sum_debit_delete": u"Удалено разрешение на дебет %(perm)s",
    "account.sum_debit_update": u"Обновлён дебет %(amount)s для %(to)s",
    "account.sum_execute_bid": u"Исполнен бид %(coll)s под %(debt)s",
    "account.sum_fee_pool_fund": (
        u"Пул комиссий %(asset)s пополнен на %(amount)s"
    ),
    "account.sum_feed": u"Фид %(asset)s опубликован %(publisher)s",
    "account.sum_feed_producers": (
        u"Задано %(n)s поставщиков фидов для %(asset)s"
    ),
    "account.sum_fill": (
        u"Исполнено: уплачено %(pays)s, получено %(receives)s"
    ),
    "account.sum_global_settle": u"Глобально погашен %(asset)s",
    "account.sum_htlc_claimed": u"HTLC %(id)s получен",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(amount)s от %(from)s к %(to)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s продлён",
    "account.sum_htlc_redeem": u"HTLC %(id)s погашен",
    "account.sum_htlc_refund": u"HTLC %(id)s возвращён",
    "account.sum_issuer_update": u"Новый эмитент %(asset)s: %(issuer)s",
    "account.sum_offer_accept": (
        u"Занято %(amount)s под залог %(coll)s (предложение %(offer)s)"
    ),
    "account.sum_offer_create": u"Создано кредитное предложение в %(asset)s",
    "account.sum_offer_delete": u"Предложение %(offer)s удалено",
    "account.sum_offer_update": u"Предложение %(offer)s обновлено",
    "account.sum_order_cancel": u"Ордер %(order)s отменён",
    "account.sum_order_create": u"Предложено %(sell)s минимум за %(buy)s",
    "account.sum_order_update": u"Ордер %(order)s обновлён",
    "account.sum_pool_create": u"Создан пул %(a)s / %(b)s",
    "account.sum_pool_delete": u"Пул %(pool)s удалён",
    "account.sum_pool_deposit": u"Внесено %(a)s + %(b)s в пул %(pool)s",
    "account.sum_pool_swap": (
        u"Своп %(sell)s → минимум %(buy)s в пуле %(pool)s"
    ),
    "account.sum_pool_update": u"Пул %(pool)s обновлён",
    "account.sum_pool_withdraw": u"Выведено %(shares)s из пула %(pool)s",
    "account.sum_proposal_create": u"Предложено операций: %(n)s",
    "account.sum_proposal_delete": u"Предложение %(proposal)s удалено",
    "account.sum_proposal_update": u"Предложение %(proposal)s одобрено",
    "account.sum_samet_borrow": u"Занято %(amount)s из фонда %(fund)s",
    "account.sum_samet_create": u"Фонд Same-T создан на %(amount)s",
    "account.sum_samet_delete": u"Фонд Same-T %(fund)s удалён",
    "account.sum_samet_repay": u"Возвращено %(amount)s в фонд %(fund)s",
    "account.sum_samet_update": u"Фонд Same-T %(fund)s обновлён",
    "account.sum_settle_cancel": u"Погашение %(amount)s отменено",
    "account.sum_smartcoin_update": u"Смарткоин %(asset)s обновлён",
    "account.sum_ticket_create": u"Тикет %(amount)s создан",
    "account.sum_ticket_update": u"Тикет %(ticket)s обновлён",
    "account.sum_transfer": u"Перевод %(amount)s от %(from)s к %(to)s",
    "account.sum_transfer_recv": u"Получено %(amount)s от %(from)s",
    "account.sum_transfer_send": u"Отправлено %(amount)s на %(to)s",
    "account.sum_upgrade": u"Апгрейд %(account)s",
    "account.sum_vesting_create": u"Вестинг %(amount)s для %(owner)s",
    "account.sum_vesting_withdraw": u"Выведено из вестинга %(amount)s",
    "account.sum_whitelist": u"Добавлен в белый список: %(account)s",
    "account.sum_witness_create": u"Стал заверителем: %(account)s",
    "account.sum_witness_update": u"Обновлён заверитель %(account)s",
    "account.sum_worker_create": u"Создан работник «%(name)s»",

    # ====================================================== account_net (64)
    "account_net.canvas_missing": (
        u"Холст сети недоступен в этой сборке; таблица ниже всё равно "
        u"перечисляет каждую линию."
    ),
    "account_net.class_credit": u"Кредит",
    "account_net.class_credit_help": (
        u"Принятые и погашенные кредитные предложения."
    ),
    "account_net.class_debit": u"Прямой дебит",
    "account_net.class_debit_help": (
        u"Разрешения прямого дебита и списания по ним."
    ),
    "account_net.class_htlc_help": (
        u"Контракты с хеш-таймлоком и их обновления."
    ),
    # "relation" is a permission line, not a movement of value - the help text
    # says so, so the chip label stays distinguishable from "поток".
    "account_net.class_override": u"Перевод с переопределением",
    "account_net.class_override_help": (
        u"Переводы, комиссию за которые платит эмитент актива."
    ),
    "account_net.class_transfer": u"Перевод",
    "account_net.class_transfer_help": u"Прямые переводы между аккаунтами.",
    "account_net.class_vesting": u"Вестинг",
    "account_net.class_vesting_help": (
        u"Вестинговые балансы под управлением третьей стороны."
    ),
    # Graph terms: a hop is one edge traversal, a ring is the neighbourhood the
    # expansion walks. Both are ordinary Russian graph words.
    "account_net.depth_1": u"1 переход",
    "account_net.depth_2": u"2 перехода",
    "account_net.depth_label": u"Глубина",
    "account_net.detail_hint": (
        u"Нажмите на линию для подробностей; нажмите на аккаунт, чтобы "
        u"открыть его."
    ),
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · операций: %(count)s · "
        u"%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · операция: %(count)s · "
        u"%(kind)s"
    ),
    "account_net.es_bad_account": (
        u"Это имя не является аккаунтом в этой цепи."
    ),
    "account_net.es_disabled": (
        u"Общественный индекс выключен. Включите его в Настройках, чтобы "
        u"построить эту карту."
    ),
    "account_net.es_unavailable": (
        u"Общественный индекс сейчас недостижим. Повторите через минуту."
    ),
    "account_net.go": u"Построить сеть",
    "account_net.idle": u"Пока ничего не построено.",
    "account_net.intro": (
        u"Введите один или несколько аккаунтов, чтобы увидеть, кому они "
        u"переводят, у кого занимают и кому. Чтение из общественного индекса "
        u"истории; ничего не подписывается и ничего не сохраняется."
    ),
    "account_net.kind_flow": u"поток",
    "account_net.kind_relation": u"связь",
    "account_net.more_assets": u" + ещё %(n)s",
    "account_net.need_class": (
        u"Включите хотя бы один вид линий, чтобы построить сеть."
    ),
    "account_net.need_seeds": u"Введите хотя бы один аккаунт для карты.",
    "account_net.no_amount": u"без суммы",
    "account_net.ring1_label": u"Кольцо 1",
    "account_net.ring2_label": u"Кольцо 2",
    "account_net.scanning": u"Чтение общественного индекса…",
    "account_net.seeds_label": u"Аккаунты для карты",
    "account_net.stale_settings": (
        u"Настройки глубины или соседей изменились — нажмите «Построить сеть»."
    ),
    "account_net.status_credit_index": (
        u"кредитных линий разрешено из индекса: %(n)s (их предложение или "
        u"сделка исчезла из цепи)"
    ),
    "account_net.status_credit_missing": (
        u"кредитных линий пропущено: %(n)s (предложение или сделка не найдены "
        u"в цепи)"
    ),
    "account_net.status_depth": u"карта: %(depth)s",
    "account_net.status_edge_cap": u"показано %(n)s лучших линий",
    "account_net.status_expanded": u"развёрнуто: %(names)s",
    "account_net.status_expansion_scanned": (
        u"операций из индекса при развёртывании: %(n)s"
    ),
    "account_net.status_expansion_truncated": (
        u"сканирование при развёртывании ограничено самыми новыми операциями"
    ),
    "account_net.status_graph": u"аккаунтов: %(nodes)s · линий: %(edges)s",
    "account_net.status_node_cap": u"показано %(n)s лучших контрагентов",
    "account_net.status_scanned": (
        u"операций из индекса: %(scanned)s от %(n)s аккаунтов"
    ),
    "account_net.status_self": u"переводов самому себе пропущено: %(n)s",
    "account_net.status_shape": u"пропущено нечитаемых записей: %(n)s",
    "account_net.status_truncated": (
        u"по %(n)s самых новых операций на аккаунт"
    ),
    "account_net.status_unexpanded": (
        u"прямых контрагентов не развёрнуто: %(n)s"
    ),
    "account_net.status_unknown": u"не найдены: %(names)s",
    "account_net.title": u"Сеть аккаунтов",
    "account_net.twin_amount": u"Сумма",
    "account_net.twin_class": u"Тип",
    "account_net.twin_count": u"Операции",
    "account_net.twin_depth": u"Переход",
    "account_net.twin_empty": (
        u"Между этими аккаунтами нет линий в просмотренных операциях индекса."
    ),
    "account_net.twin_from": u"От",
    "account_net.twin_relation": u"Поток/связь",
    "account_net.twin_span": u"Первая → последняя",
    "account_net.twin_summary": u"Табличное представление (доступно)",
    "account_net.twin_to": u"Кому",

    # ============================================================== asset (37)
    "asset.cer_row": u"Базовый курс обмена (CER)",
    "asset.committee_fed_note": (
        u"Фид от комитета: публиковать могут все активные члены комитета."
    ),
    "asset.feed_history_title": u"История фидов",
    "asset.history_capped": (
        u"Показаны первые 8 публикаторов (ограничено ради скорости)…"
    ),
    "asset.history_days": u"Диапазон",
    "asset.history_exchange": u"Загрузка биржи и пулов…",
    "asset.history_failed": u"Не удалось загрузить историю фидов.",
    "asset.history_loading": u"Загрузка истории фидов…",
    "asset.history_pub": u"Публикатор %(i)s/%(n)s…",
    "asset.invert_btn": u"Инвертировать",
    "asset.issue_memo_no_key": (
        u"Нет memo-ключа для этого аккаунта."
    ),
    "asset.issue_memo_warning": (
        u"Добавьте memo — он хранится в цепи открытым текстом."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"Эмитент по умолчанию — аккаунт просмотра (%(id)s заблокирован, ваш "
        u"аккаунт разблокирован) — укажите любого эмитента, которым владеете. "
        u"Открыто со страницы аккаунта: вставьте имя этого аккаунта."
    ),
    "asset.loading_producers": u"Загрузка поставщиков…",
    # "Co-owner" is the same term the shared-account help body uses for the
    # second key holder, so the hint reuses it verbatim.
    "asset.multisig_body": (
        u"Если этому активу нужно больше одного подтверждения, прямая "
        u"Подпись не сработает — предложите изменение и попросите "
        u"со-владельцев одобрить (op 23)."
    ),
    "asset.multisig_coowner_hint": (
        u"Со-владелец? Предложите изменение на странице предложений и "
        u"попросите со-владельцев одобрить (op 23)."
    ),
    "asset.multisig_open_proposals": u"Смотреть предложения",
    "asset.multisig_open_txbuilder": u"Открыть конструктор транзакций",
    "asset.multisig_title": u"Общий эмитент? Предложите",
    "asset.new_issuer_field": u"Новый эмитент",
    "asset.no_history": (
        u"В этом диапазоне нет истории — публикаторы публикуют редко; "
        u"попробуйте 90д."
    ),
    "asset.no_producers": (
        u"Фиды ещё не опубликованы — поставщики появятся здесь после "
        u"публикации."
    ),
    "asset.orientation_note": u"%(m)s за %(b)s",
    "asset.owner_key_note": u"Требуется активный ключ владельца актива.",
    "asset.plot_feeds": u"Графики фидов",
    "asset.producer_col": u"Поставщик",
    "asset.producers_failed": u"Не удалось загрузить поставщиков.",
    "asset.producers_live_title": u"Поставщики фидов",
    "asset.producers_title": u"Поставщики фидов (op %(op)s)",
    "asset.publish_op19_title": u"Публикация фида (op %(op)s)",
    "asset.published_col": u"Опубликовано",
    # "Viewing as" is the phrase shell.acting_default and every *_viewing_as
    # notice already ships; this reuses it so principle #9 reads one way.
    "asset.viewing_notice": (
        u"Просмотр как %(name)s (%(id)s) — разблокируйте для подписи."
    ),
    "asset.witness_fed_note": (
        u"Фид от заверителей: публиковать могут все активные заверители."
    ),

    # ============================================================ market (48)
    "market.adjust_button": u"Скорректировать",
    "market.confirm_adjust": u"Подтвердите корректировку",
    "market.discrete_fills": u"исполнений",
    "market.discrete_no_fills": (
        u"Исполнений пока нет — разместите ордер или попробуйте другую пару."
    ),
    "market.discrete_swaps": u"свопов",
    "market.discrete_tip_account": u"Аккаунт",
    "market.discrete_tip_block": u"Блок",
    "market.discrete_tip_order": u"Ордер",
    "market.discrete_tip_price": u"Цена",
    "market.discrete_tip_time": u"Время",
    "market.discrete_tip_volume": u"Объём",
    "market.discrete_tip_volume_quote": u"Объём (котируемая)",
    "market.discrete_unavailable": (
        u"Индикаторы недоступны в дискретном режиме."
    ),
    "market.discrete_volume": u"Дискретный объём",
    "market.exchange_desk": u"Биржевой деск",
    "market.fail_update": u"Не удалось обновить.",
    "market.flt_max_price": u"Макс. цена",
    "market.flt_min_price": u"Мин. цена",
    "market.loading_pool_map": u"Загрузка карты…",
    "market.map_aria": (
        u"Рыночная сеть. Линии — рынки с исполнениями за последние 24 часа."
    ),
    "market.map_connects": (
        u"Линия соединяет два актива, если между ними была рыночная сделка за "
        u"последние 24 часа."
    ),
    "market.map_connects_fallback": (
        u"Линия соединяет два актива, если существует пополненный пул. "
        u"Торговая активность за 24ч не подтверждена (история недоступна) — "
        u"показаны пополненные пулы."
    ),
    "market.map_edge_fills": (
        u"%(desk)s · %(a)s–%(b)s · исполнений за 24ч: %(fills)s"
    ),
    "market.map_hops_empty": (
        u"Ни один рынок не исполнялся за последние 24 часа вокруг этих плеч."
    ),
    "market.map_hops_filtered": (
        u"Линия — рынок с исполнениями за последние 24 часа. Показано пар: "
        u"%(shown)s из %(total)s (минимум %(min)s исполнений за 24ч)."
    ),
    "market.map_hops_no_route": (
        u"Нет маршрута к BTS через рынки с исполнениями."
    ),
    "market.map_hops_note": (
        u"Линия — рынок с исполнениями за последние 24 часа. Показано пар: "
        u"%(pairs)s."
    ),
    "market.map_leg_ok": u"{s} соединяется с BTS",
    "market.map_leg_orphan": (
        u"ВНИМАНИЕ: у {s} нет маршрута через рынки с исполнениями!"
    ),
    "market.min_fills": u"Мин. исполнений",
    "market.no_filter_match": u"Нет исполнений под эти фильтры.",
    "market.settle_first100": (
        u"Показаны первые 100 (лимит get_settle_orders — 100)"
    ),
    "market.settle_no_cancel": (
        u"Ордера на погашение нельзя отменить — они исполняются при погашении "
        u"(после задержки принудительного погашения актива)."
    ),
    "market.tf_discrete": u"Дискретный",
    "market.update_amount": u"Сумма к продаже (новый итог) ",
    "market.update_amount_change": u"Изменение суммы",
    "market.update_bad_amount": u"Введите сумму больше нуля.",
    "market.update_bad_expiry": u"Введите срок в будущем.",
    "market.update_bad_price": u"Введите цену больше нуля.",
    "market.update_broadcasting": u"Трансляция обновления…",
    "market.update_done": u"Ордер обновлён",
    "market.update_expiry": u"Новый срок ",
    "market.update_expiry_change": u"Срок (старый → новый)",
    "market.update_no_change": (
        u"Нет изменений — измените цену, сумму или срок."
    ),
    "market.update_price": u"Новая цена ",
    "market.update_price_change": u"Цена (старая → новая)",
    "market.update_review": u"Проверка обновления",
    "market.update_title": u"Скорректировать ордер",

    # ======================================================= market_net (37)
    "market_net.asset_1_field": u"Актив 1 (любое плечо)",
    "market_net.asset_2_field": u"Актив 2 (любое плечо)",
    "market_net.band_title": u"Рыночная сеть",
    "market_net.canvas_label": (
        u"Карта рыночной сети. Нажмите Enter, чтобы открыть рынок."
    ),
    "market_net.clear_btn": u"Очистить",
    # The short column heads reuse the stats-tab wording verbatim: "Δ 24ч" is
    # market.chg_label / market.stat_chg, "Объём" is market.vol_label.
    "market_net.col_change": u"Δ 24ч",
    "market_net.col_last": u"Последняя",
    "market_net.col_market": u"Рынок",
    "market_net.col_vol": u"объём 24ч",
    "market_net.collapse": u"Свернуть",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · исполнений за 24ч: %(fills)s"
    ),
    "market_net.empty": u"Нет рынков под этот фильтр.",
    "market_net.expand": u"Развернуть",
    "market_net.list_btn": u"Список рынков",
    "market_net.loading": u"Загрузка рынков…",
    "market_net.map_empty": u"Нет рынков с недавним объёмом.",
    "market_net.map_fallback": (
        u"пар: %(pairs)s · активов: %(assets)s · исполнения за 24ч не "
        u"подтверждены"
    ),
    "market_net.map_hops_ready": (
        u"пар: %(pairs)s · активов: %(assets)s · исполнения за 24ч"
    ),
    "market_net.map_ready": u"рынков: %(markets)s · активов: %(assets)s",
    "market_net.node_card": u"%(sym)s (%(id)s) · рынков: %(n)s",
    "market_net.offline": (
        u"Сеть недоступна — показаны рынки из кэша. Повторите при подключении."
    ),
    "market_net.open_desk": u"Открыть %(id)s",
    "market_net.prompt": (
        u"Нажмите на узел актива, на линию — на рынок."
    ),
    "market_net.ramp": u"Объём 24ч: от малого к большому",
    "market_net.ramp_fills": u"Исполнения 24ч: от малых к большим",
    "market_net.selector_title": u"Выбор рынка",
    "market_net.spark_label": u"Тренд за 7 дней для %(id)s",
    "market_net.subtitle": (
        u"Ведущие рынки стакана по объёму за 24ч. Выберите строку, чтобы "
        u"открыть деск."
    ),
    "market_net.title": u"Рынки",
    "market_net.top_note": (
        u"Топ-%(shown)s из %(probed)s проверенных — по объёму за 24ч."
    ),
    "market_net.twin": u"Строки рынков (%(n)s)",
    "market_net.twin_more": (
        u"Показано %(shown)s из %(n)s рынков — сузьте фильтр, чтобы увидеть "
        u"меньше."
    ),
    "market_net.verdict_full": u"рынков: %(markets)s · активов: %(assets)s",
    "market_net.verdict_no_path": (
        u"Нет маршрута через рынки с исполнениями между %(a)s и %(b)s"
    ),
    "market_net.verdict_path": (
        u"%(a)s достигает %(b)s через %(n)s рынков с исполнениями"
    ),
    "market_net.verdict_star": u"Рынки, связанные с %(s)s: %(n)s",
    "market_net.verdict_web": u"Достижимые рынки из %(s)s: %(n)s",

    # ========================================================== settings (36)
    "settings.confirm_back": u"Назад",
    "settings.confirm_remove_action": u"Действие",
    "settings.confirm_remove_hide": (
        u"Скрыть эту ноду (останется скрытой до повторного добавления)"
    ),
    "settings.confirm_remove_result": u"Результат",
    "settings.confirm_remove_switch": u"Активная нода переключится на %(node)s",
    "settings.confirm_remove_title": u"Удалить ноду?",
    "settings.confirm_remove_unlist": u"Убрать из моего списка",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**Кнопка «Найти ноды» ищет списки нод на GitHub, затем проверяет "
        u"найденное. GitHub и проверенные ноды видят ваш сетевой адрес. "
        u"Результаты — кандидаты на вашу проверку; ничего не добавляется "
        u"автоматически."
    ),
    "settings.geo_note": (
        u"*Местоположение и провайдеры берутся с ipaddress.to (https, без "
        u"ключа) — сервис видит ваш адрес по запросу; ответы кэшируются на "
        u"этом устройстве на 24 часа."
    ),
    "settings.hist_no": u"НЕТ",
    "settings.hist_yes": u"ДА",
    "settings.language_title": u"Язык",
    # Signing section. "Extension" is the browser extension; Russian says
    # «расширение» and the word is unused elsewhere in the file, so this is
    # the batch's first spelling of it.
    "settings.sign_auto": u"Автоматически (расширение, если доступно)",
    "settings.sign_badge": (
        u"Подпись через расширение активна — подробности во Входе"
    ),
    "settings.sign_badge_local": (
        u"Подпись на этой странице — подробности во Входе"
    ),
    "settings.sign_browser": u"Всегда подписывать на этой странице",
    "settings.sign_ext": u"Всегда использовать расширение",
    "settings.sign_ext_absent": (
        u"Расширение на этом устройстве не обнаружено — подпись происходит на "
        u"этой странице."
    ),
    "settings.sign_ext_present": u"Расширение на этом устройстве обнаружено.",
    "settings.sign_guide": u"Как установить расширение",
    "settings.sign_mode_browser": u"Подпись происходит в памяти этой страницы.",
    "settings.sign_mode_ext": (
        u"Подпись подтверждается в окне расширения."
    ),
    "settings.sign_mode_ext_page": (
        u"Подпись остаётся в расширении — изолирована от сайтов."
    ),
    "settings.sign_revoke": u"Отозвать",
    "settings.sign_sites": u"Подключённые сайты",
    "settings.sign_sites_empty": (
        u"Пока нет одобренных сайтов — одобрения появятся здесь с отзывом "
        u"для каждого сайта."
    ),
    "settings.sign_sites_story_a": u"Пример: игра в кости на ",
    "settings.sign_sites_story_b": (
        u" просит играть от вашего аккаунта — одобрение добавит его сюда, "
        u"привязав только к этому аккаунту. Подпись всё равно запрашивается "
        u"каждый раз. (Эта ссылка никуда не ведёт — это вымышленный пример.)"
    ),
    "settings.sign_title": u"Подпись",
    "settings.sign_warn": (
        u"Любой скрипт, выполняющийся на этой странице, включая взломанную "
        u"размещённую копию, может прочитать ваши ключи, пока они "
        u"разблокированы. Проводите подпись через расширение или запускайте "
        u"копию, которой владеете вы."
    ),
    "settings.th_chain": u"Цепь",
    "settings.th_handshake": u"Рукопожатие",
    "settings.th_head": u"Вершина",
    "settings.th_history": u"История",
    "settings.th_location": u"Местоположение *",
    "settings.th_participation": u"Участие",
    "settings.th_ping": u"Пинг",
    "settings.th_provider": u"Провайдер *",
    "settings.theme_title": u"Тема",
}

# Keys whose Russian value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from RU. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords a Russian crypto UI keeps in Latin: HTLC, NFT, PMA, UIA, MCR,
#     SMA, EMA, BB, PSAR, get_settle_orders;
#   * network ids and sentinels the brief pins: mainnet / testnet / devnet,
#     original-blue / light / dark, "wss://…", "…", "—", "7d";
#   * pure glue a table cell or tooltip prints as data: "@ %(price)s · %(vol)s",
#     "%(desk)s · %(a)s–%(b)s · %(vol)s", "%(first)s → %(last)s", "Op", "—
#     " and the seed placeholder (real account names plus a 1.2.x id, which
#     rule 1 keeps byte-verbatim).
KEPT_ENGLISH = {
    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    # ---- asset
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
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