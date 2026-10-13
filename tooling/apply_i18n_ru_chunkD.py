#!/usr/bin/env python3
"""i18n ru chunk-D: finish the LAST seven sections ru.json still leaves English.

Scope: ONLY the seven sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ru.json, or one whose English master moved, is REFUSED;
  * RU + KEPT_ENGLISH together must account for EVERY untranslated key of the
    seven sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account/account_net/settings/market/market_net/asset, chunk-B1 owns
help/pool_net, chunk-C owns the signing + UX sections, and each REFUSES anything
outside itself. This is the last Russian batch: after it, the seven sections
below are the only ones left, so nothing in the dictionary is English by
accident - what is left is English by decision, and each decision is written
down in KEPT_ENGLISH where a reviewer can read it instead of guessing.

Safety gates asserted before anything is written (see main()), inherited
verbatim from chunk-B1 so a structural break cannot slip in under a new name:

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                     network/theme/dash/placeholder tokens stay byte-verbatim
                     (the same list tooling/validate_translations.py checks);
                     none of them lives in this batch's sections, so the list
                     is here to catch drift anywhere in the file;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master -
                     load-bearing twice here: about.making_body is a markdown
                     body stored as one long line, and a [label](#/hash) link
                     inside one loses a hash to 404 if the label is reflowed
                     carelessly (the menu bodies carry #/route targets);
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
                     typographic apostrophe: Russian quotes with «...». It bites
                     here too - seo.desc_markets is the only English master in
                     these seven sections carrying an ASCII apostrophe
                     ("any pair's"), and about.making_body carries both ASCII
                     double quotes ("acquire bitshares-ui") and a possessive
                     ("builders'"); both become «...».

  G8  dot hygiene    a middle dot must be space-separated, as in every other
                     locale - except inside an algebraic notation where both
                     neighbours are alphanumeric (ru.json ships "x*y=k" in
                     pool.list_sub, outside this batch, and the file-wide sweep
                     in verify() would otherwise fail on someone else's honest
                     formula).

Vocabulary is reused verbatim from the three earlier Russian batches so this
one reads like the rest of the dictionary instead of like a fourth dictionary.
From chunk-A/B/C: аккаунт, актив, баланс, ордер, бид, аска, книга ордеров,
стакан, деск, цена, комиссия, залог, пул, пулы ликвидности, своп, стейк,
анстейк, LP-доли, долевой актив, смарткоин, кошелёк, нода, цепь, чейн, фид,
заверитель, комитет, работник, прокси, бюллетень, брейнкей, вестинг, тикет,
полномочие, мемо, голосование, обзор, обозреватель. Nothing is invented where
a Russian crypto UI keeps the English word - DEX, HTLC, BitShares, BTS, API,
Memo, Swap, Proxy, Smartcoin, Pool, ID, MCR, MSSR, core - and the run prints
every value that stays identical to en so a reviewer checks the list instead of
guessing. Each of those is also written into KEPT_ENGLISH, which is the
difference between English-on-purpose and English-by-omission.

Three cross-batch decisions worth stating up front, because they are the ones a
later pass is most likely to "fix" into a contradiction:

  1. about.making_body reuses chunk-B1's help.topic_about-making_body wording
     verbatim (same story, joined into the single line the about page stores).
     Two languages' readers see the same sentences, and the Russian «...» quote
     rule (G7) is applied to both.
  2. explorer.core_suffix stays Latin " (core)" because its immediate sibling
     explorer.fund_amount_label already shipped "Сумма (core, в человеческом
     виде — напр. 0.1)" - the same screen, the same word, two spellings would be
     the reader's first proof of machine translation. The gloss "кор-актив" is
     still available where English says "core asset" (pool.map_core_aria).
  3. explorer.raw_mark becomes " (сырой)" rather than staying Latin "raw": its
     nearest sibling in the same domain is pool.a_to_b_col «Выход A→B (сырой)».
     The remaining Latin "raw" in ru.json (eslab.hint_holders) is a different
     screen and a different register; it is listed here as the known outlier,
     not as a third name for the same thing.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ru_chunkD.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ru_chunkD.py --apply         # writes ru.json
  python3 tooling/apply_i18n_ru_chunkD.py --verify        # structural re-proof
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

# The seven sections this batch owns. Everything else belongs to an earlier
# batch and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "pool", "explorer", "seo", "splash", "about", "shell", "menu",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). Only shell.brand actually lives in this batch's sections; the
# rest is the file-wide watchdog shared with chunks A/B/C, so a later pass that
# moves one of them into these sections is refused instead of translated.
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


def mixed_script_words(value):
    """Return every token that mixes Cyrillic and Latin letters.

    Russian transliterates most crypto terms (ордер, фид, пул), so a single
    Latin letter typed into a Cyrillic word is invisible in review and wrong
    on screen. The shipped ru.json has zero such words; this batch must not add
    the first one. It matters most where English product names sit next to
    Russian sentences (BTS, React, WebSocket, JavaScript, pool-ui.js), because
    the temptation is to glue them on with a hyphen.
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

    Russian quotes with «...» - ru.json already uses it 25+ times - and the
    ASCII apostrophes still in the file all sit inside untranslated English.
    A translated line that grew one would be the only such spelling in the
    dictionary. seo.desc_markets ("any pair's") and about.making_body
    ("builders'") are the two masters in this batch that test the rule.
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
    # UNCLAIMED, which is the honest state for them - and required, because
    # shell.brand is in check_i18n.py's IDENTIFIERS set and claiming it would
    # register as a false translation claim. Nothing else in _meta moves:
    # filling strings is not verification, so the controller's v2
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

    print("ru chunk-D: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue - "
              "deliberately NOT claimed):")
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
    # ============================================================== pool (30)
    # Vocabulary mirrors the already-translated pool twin: стейк, анстейк,
    # своп, LP-доли, долевой актив, рыночная комиссия, котировка.
    "pool.asset_1_field": u"Актив 1 (любое плечо)",
    "pool.asset_2_field": u"Актив 2 (любое плечо)",
    "pool.clear_btn": u"Очистить",
    # %(legs)s is a comma-joined list of asset SYMBOLS read by the guard, so
    # the noun is singular and the number is whatever the list holds.
    "pool.delete_not_empty": (
        u"Не пусто — %(legs)s должно показывать 0 перед удалением."
    ),
    "pool.direct_hit": u"Прямой поиск пула — постраничная навигация скрыта.",
    # «кор-токен» extends the shipped «кор-актив» (pool.map_core_aria) to the
    # token itself; BTS is a brand and stays Latin.
    "pool.map_core_self": u"BTS — кор-токен BitShares",
    "pool.min_swaps": u"Мин. свопов",
    # The two leading-space hints concatenate onto an empty-state line
    # (pool.no_swaps / pool.no_my_exchanges), so the leading space is kept.
    "pool.my_swaps_hint": (
        u" Запустите своп на панели свопов выше — ваши свопы в этом пуле "
        u"перечислены здесь."
    ),
    "pool.no_filter_match": u"Свопы не подходят под эти фильтры.",
    # 1.3.x / 1.19.x are object-id prefixes the reader pastes: byte-verbatim.
    "pool.share_or_pool_hint": u"символ, 1.3.x или пул 1.19.x",
    "pool.stake_autofill_hint": (
        u"Введите одну сумму — вторая подставится по курсу пула."
    ),
    "pool.stake_preview_bad": u"Проверьте суммы — оценка долей недоступна.",
    "pool.stake_preview_need_both": (
        u"Введите обе суммы для оценки долей."
    ),
    "pool.stake_preview_unavailable": u"Оценка долей недоступна (офлайн).",
    "pool.stake_ratio_empty": (
        u"Пул пуст — введите обе суммы вручную."
    ),
    "pool.stake_ratio_row": u"Курс (спот)",
    "pool.stake_shares_row": u"Оценка LP-долей",
    "pool.swap_desk": u"Деск свопов",
    "pool.swap_mkt_preview_dash": u"Рыночная комиссия (предпросмотр): —",
    "pool.swap_mkt_row": u"Рыночная комиссия",
    # Trailing space kept: the live path appends the computed quote to it.
    "pool.swap_preview": u"Котировка (предпросмотр): ",
    "pool.swap_preview_dash": u"Котировка (предпросмотр): —",
    "pool.swaps_hint": (
        u" Свопы появятся после первого обмена в этом пуле — запустите его "
        u"на панели свопов выше."
    ),
    # Signing-dialog ROW TERM (pool-ui.js rows: [[term, op title]]). «Действие»
    # matches the already-translated explorer.actions «ДЕЙСТВИЯ»; the value in
    # the row is an operation title, which the glossary's «операция» names —
    # see the report's low-confidence list before human-verifying this pair.
    "pool.uc_action": u"Действие",
    "pool.uc_title": u"Разблокировать, чтобы продолжить",

    # ========================================================== explorer (12)
    # The four asset-type filter chips: short nouns, matching the page's own
    # «Пользовательские активы» (explorer.no_smartcoins).
    "explorer.assets_mode_all": u"Все",
    "explorer.assets_mode_market": u"Смарткоины",
    "explorer.assets_mode_prediction": u"Прогнозные рынки",
    "explorer.assets_mode_user": u"Пользовательские",
    # "Showing: N из M" — identical construction to explorer.markets_*.
    "explorer.assets_showing": u"Показано",
    "explorer.assets_of": u"из",
    "explorer.feeds_showing": u"Показано",
    "explorer.feeds_of": u"из",
    "explorer.feeds_scanned_suffix": u"просканировано (первые 100 активов)",
    # core_exchange_rate is the on-chain field name and stays Latin, exactly as
    # explorer.feed_cer_missing already spells it. The glossary's mandated word
    # for the publisher ROLE is «публикатор» (chunk-C decision), which is why
    # this string says публикатора and not издателя.
    "explorer.feed_cer_premium": (
        u"Премия core_exchange_rate (CER) (оценка по правилу публикатора)"
    ),
    # ASCII double quotes become «...» (G7's Russian half).
    "explorer.no_assets_match": u"Активов по запросу «%(q)s» нет.",
    # Same root, same sense as pool.a_to_b_col «Выход A→B (сырой)».
    "explorer.raw_mark": u" (сырой)",

    # ================================================================ seo (26)
    # Meta descriptions are factual and short; "BitShares Wallet" is the
    # product name and becomes «кошелёк BitShares» everywhere, so the title
    # suffix never mixes two spellings. shell.brand itself stays Latin.
    "seo.title_about": u"О проекте — кошелёк BitShares",
    "seo.title_account": u"Аккаунт %(name)s — кошелёк BitShares",
    "seo.title_account_net": u"Сеть аккаунтов — кошелёк BitShares",
    "seo.title_dashboard": u"Дашборд — кошелёк BitShares",
    "seo.title_explorer": u"Обозреватель блокчейна — кошелёк BitShares",
    "seo.title_help": u"Помощь — кошелёк BitShares",
    "seo.title_login": u"Вход — кошелёк BitShares",
    "seo.title_market": u"Биржа BTS/USD — кошелёк BitShares",
    "seo.title_markets": u"Рынки — кошелёк BitShares",
    "seo.title_pools": u"Пулы ликвидности — кошелёк BitShares",
    # Matches transfer.title «Перевод» and menu.p_transfer «Перевод».
    "seo.title_transfer": u"Перевод — кошелёк BitShares",
    "seo.title_voting": u"Голосование за заверителей — кошелёк BitShares",
    "seo.title_xrates": u"Кросс-курсы — кошелёк BitShares",
    "seo.desc_about": (
        u"О кошельке BitShares — локальные ключи, без регистрации и без слежки. "
        u"Смотрите всё свободно, подписывайте локально."
    ),
    "seo.desc_account": (
        u"Просмотр аккаунта BitShares — балансы, ордера и история читаются с "
        u"цепи вживую. Вход не нужен."
    ),
    "seo.desc_account_net": (
        u"Сеть переводов аккаунта: кому он переводит, у кого занимает и кому "
        u"даёт в долг — из общественного индекса. Вход не нужен."
    ),
    "seo.desc_dashboard": (
        u"Дашборд BitShares — балансы, рынки и активность цепи одним взглядом. "
        u"Смотрите свободно; ключи остаются на вашем устройстве."
    ),
    "seo.desc_explorer": (
        u"Обзор блоков, транзакций и активов BitShares — живые данные цепи, "
        u"доступны без входа."
    ),
    "seo.desc_help": (
        u"Помощь по кошельку BitShares — руководства по аккаунтам, торговле, "
        u"голосованию и восстановлению. Начните отсюда, если затрудняетесь."
    ),
    "seo.desc_login": (
        u"Разблокировка локального кошелька BitShares — пароль, брейнкей или "
        u"импортированные ключи. Ключи не покидают это устройство."
    ),
    "seo.desc_market": (
        u"Торговля BTS за USD в книге ордеров BitShares — живые биды, аски и "
        u"история, подпись локально на вашем устройстве."
    ),
    # The only ASCII apostrophe in these seven sections ("any pair's") — the
    # Russian rewrites the possessive around the noun and needs none.
    "seo.desc_markets": (
        u"Рынки BitShares по книгам ордеров и объёму за 24 ч — откройте "
        u"торговый деск любой пары. Вход не нужен."
    ),
    "seo.desc_pools": (
        u"Пулы ликвидности BitShares — пары, балансы и активность читаются с "
        u"цепи вживую. Вход не нужен."
    ),
    "seo.desc_transfer": (
        u"Отправка активов BitShares на любой аккаунт. Проверьте каждое поле, "
        u"затем подпишите локально — ключи не покидают ваше устройство."
    ),
    "seo.desc_voting": (
        u"Голосование за заверителей, членов комитета и работников BitShares. "
        u"Каждый бюллетень подписывается локально на вашем устройстве."
    ),
    "seo.desc_xrates": (
        u"Цены всех активов пулов в BTS и не только, по последним ценам "
        u"свопов. Вход не нужен."
    ),

    # ============================================================= splash (20)
    # The dashboard hero + cards + pulse band. The already-translated
    # splash.trust_* siblings set the register: plain, factual, second person.
    "splash.hero_title": (
        u"Кошелёк BitShares в вашем браузере — ничего устанавливать не нужно."
    ),
    "splash.hero_sub": u"Ваши ключи. Ваши средства ончейн.",
    "splash.hero_sub2": u"Рынки — без ограничений. Разблокируйте только для подписи.",
    "splash.cta_exchange": u"Торговать на бирже",
    "splash.cards_title": u"Торговля, пулы, обзор — начните отсюда",
    "splash.card_dex_d": u"Покупка и продажа на открытом рынке.",
    "splash.card_explore_d": u"Чтение блоков и истории аккаунтов.",
    "splash.card_pool_d": u"Доход от объединения двух активов в пул.",
    "splash.card_wallet_d": u"Ключи хранятся только на этом устройстве.",
    "splash.pulse_title": u"Живые числа цепи",
    # Grid cell label; its neighbour splash.pulse_head is «Головной блок», so
    # the timestamp of that same block is spelled out rather than abbreviated.
    "splash.pulse_time": u"Время головного блока",
    # Stale glyph for a missed chain call — a status word, so neuter.
    "splash.pulse_stale": u"— устарело",
    "splash.topvol_unavailable": (
        u"Топ-объём рынка недоступен — проверьте Настройки → Ноды."
    ),
    "splash.step1_t": u"Осмотритесь",
    "splash.step1_d": u"Вход не нужен — сначала посмотрите цепь.",
    "splash.step2_t": u"Создайте кошелёк",
    "splash.step2_d": (
        u"Брейнкей создаётся на этом устройстве. Запишите его на бумаге."
    ),
    "splash.step3_t": u"Торговля / пул / голосование",
    "splash.step3_d": (
        u"Лимитные ордера, пулы ликвидности и бюллетени — всё ончейн."
    ),
    "splash.trust_keys_d": (
        u"Подпись происходит локально на вашем устройстве. Ни один сервер не "
        u"видит ни пароля, ни ключа."
    ),

    # ============================================================== about (19)
    # The about page: hero + six feature blocks + the build-dialog archive.
    # s1_title, s1_body, s2_body, s5_title, s6_title, s6_body and the CTA keys
    # already shipped in an earlier pass, so s2_title here must read as the
    # headline over «Стаканы, пулы ликвидности…» (about.s2_body).
    "about.hero_lede": (
        u"Кошелёк для блокчейна BitShares — рынки, аккаунты, управление и "
        u"обзор — работающий как обычные веб-файлы. Без фреймворка, без "
        u"установщика, без учётной записи у нас. Ваши ключи никогда не "
        u"покидают этот браузер."
    ),
    "about.making_title": u"Как делался этот кошелёк",
    # Same story as chunk-B1's help.topic_about-making_body, joined into the
    # single line this page stores. Wording is reused verbatim from it so the
    # article and the about page cannot disagree; the English "builders'"
    # becomes "создателей" and "acquire bitshares-ui" gets «...» (G7).
    "about.making_body": (
        u"Ниже — исходная история создания: каждый запрос, который создал "
        u"этот кошелёк, от «acquire bitshares-ui» 26 сентября 2026 года до "
        u"исправления issue-1 3 октября, вместе с ответами создателей — "
        u"сохранённая без правок. В ней записаны решения, на которых стоит "
        u"этот кошелёк: отказ от очередного апгрейда React после issue #3583 и "
        u"его ловушки в тысячу часов, так что кошелёк не зависит ни от чего с "
        u"циклом релизов; подпись каждой транзакции локально, как в старом "
        u"кошельке, а не передача её наружу; три темы с классическим "
        u"оформлением по умолчанию; числа в человеческих единицах, а не сырые "
        u"целочисленные значения цепи; вёрстка сначала под телефон, начиная с "
        u"первого слайса; и комиссии, читаемые с живой цепи, а не "
        u"оцениваемые. Читайте это как историю: так был построен кошелёк."
    ),
    "about.s2_title": u"Торговля по настоящему стакану",
    "about.s3_title": u"Работает годами без обновлений",
    "about.s3_body": (
        u"Кошелёк, который он заменяет, умер под тяжестью сотни устаревших "
        u"пакетов и инструментов, которые никто не может воспроизвести. "
        u"Сделанный так, чтобы не зависеть ни от чего с циклом релизов: без "
        u"фреймворка, без пакетного менеджера, без шага сборки — самое малое, "
        u"что ещё способно работать в браузере через десять лет."
    ),
    "about.s4_title": u"Те же страницы, живые обновления",
    "about.s4_body": (
        u"Вернувшиеся пользователи сразу чувствуют себя как дома — те же "
        u"страницы, панели и слова, что и в классическом кошельке, — при том "
        u"что балансы, стаканы и статус подключения обновляются на месте. "
        u"Прощающийся поиск по рынкам, аккаунтам и активам, три темы и вёрстка, "
        u"которая работает от телефона на 360px до торгового деска на 4K."
    ),
    "about.s5_body": (
        u"Цепь говорит целыми числами; вы их не видите. Каждая сумма стоит в "
        u"разрядности своего актива, каждый процент — в своём настоящем "
        u"значении, а каждая комиссия читается с живой цепи до подписи."
    ),
    # ---- build-dialog archive chrome (about-ui.js)
    "about.dlg_heading": u"Полный диалог создания",
    "about.dlg_heading_c": u"Полный диалог создания (%(total)s)",
    "about.dlg_no_reply": (
        u"Ответ не записан — следующий запрос шёл сразу же."
    ),
    "about.dlg_noscript": (
        u"Этот архив требует JavaScript; тот же текст лежит в "
        u"docs/vanilla-ui-dialog.md в репозитории исходного кода."
    ),
    "about.dlg_search_clear": u"Очистить",
    "about.dlg_search_ph": u"Фильтр обменов…",
    "about.dlg_showing": u"Показано",
    "about.dlg_showing_c": u"Показано %(shown)s / %(total)s",
    "about.dlg_unavailable": u"Архив диалога создания недоступен.",

    # ============================================================== shell (11)
    # Footer build-info ladder. Every relation fragment is printed BEFORE the
    # appended "Master" branch link (app.js paintVersion), so each Russian form
    # is built to read well in front of a proper noun.
    "shell.footer_sync": u"синхронно с",
    "shell.footer_diverged": u"расхождение с",
    "shell.footer_dahead": u"%(n)s вперёд",
    "shell.footer_dbehind": u"%(n)s позади",
    "shell.footer_ahead": u"%(n)s коммитов впереди от",
    "shell.footer_ahead_one": u"1 коммит впереди от",
    "shell.footer_behind": u"%(n)s коммитов позади",
    "shell.footer_behind_one": u"1 коммит позади",
    # Inside the parens after the relation: "(на момент сборки 2026-10-01)".
    "shell.footer_at_build": u"на момент сборки %(date)s",
    "shell.footer_offbranch": u"не на ветке Master",
    # REPORT links to the Community page — a verb-noun button, not a label.
    "shell.report": u"СООБЩИТЬ",

    # =============================================================== menu (9)
    # The three section titles match the headings chunk-B1 already wrote into
    # the sitemap article, so the map and the button cannot disagree.
    "menu.section_explore": u"Обзор",
    "menu.section_labs": u"Лаборатории",
    "menu.section_personal": u"Личное",
    "menu.blurb_labs": u"Мощные инструменты для работы с цепью и нодами.",
    "menu.blurb_personal": u"Чат, алерты и настройки.",
    # Page names chunk-B1 had to invent for the sitemap: Cross Rates became
    # «Кросс-курсы» and Account Network «Сеть аккаунтов» there; account_net.title
    # already shipped «Сеть аккаунтов», so both halves agree.
    "menu.p_xrates": u"Кросс-курсы",
    "menu.p_account_net": u"Сеть аккаунтов",
    "menu.d_xrates": u"Цены пулов для каждого актива в BTS и не только.",
    "menu.d_account_net": u"отслеживание переводов",
}


# Keys whose Russian value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from RU. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift. Twelve keys, in four groups:
#
#   1. BRANDS, three: shell.brand and the two all-caps footer brand strings.
#      shell.brand is pinned by rule 1 of the brief AND by
#      tooling/validate_translations.py's VERBATIM_KEYS and
#      tooling/check_i18n.py's IDENTIFIERS; the footer pair is the same logo
#      text CSS uppercases, so transliteration would only produce
#      «БИТШЕЙРЕС ВАНИЛЛА УИ». A brand is not prose.
#   2. LOANWORDS a Russian crypto UI keeps in Latin, four: HTLC (the menu
#      label names the protocol), ID (a column header; «ID пула» and
#      «ID блока» already ship in ru.json), and the two on-chain ratio
#      acronyms MCR / MSSR with their raw-value tooltip.
#   3. DATA GLUE with no prose, two: the publisher tooltip is
#      "%(id)s @ %(ts)s" — an id, an @ and a timestamp — and the footer host
#      line is "%(net)s - %(host)s" — a network id (which is itself pinned
#      English) around a hostname. There is nothing to translate in either, so
#      they stay ASCII exactly as the two pool_net edge cards did in chunk-B1.
#   4. THE ONE JUDGEMENT CALL, one: explorer.core_suffix " (core)". Its
#      sibling on the same screen, explorer.fund_amount_label, already shipped
#      "Сумма (core, в человеческом виде — напр. 0.1)" with the word left
#      Latin, so the short suffix matches it rather than introducing a second
#      spelling of one term on one screen. "кор-актив" remains the gloss
#      wherever English says "core asset" (pool.map_core_aria).
KEPT_ENGLISH = {
    # ---- 1. brands
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    # ---- 2. Latin loanwords / acronyms
    "menu.p_htlc": u"HTLC",
    "explorer.id_row": u"ID",
    "explorer.th_mssr": u"MSSR",
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    # ---- 3. data glue, no prose
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    # ---- 4. the judgement call (see the comment above)
    "explorer.core_suffix": u" (core)",
}


if __name__ == "__main__":
    sys.exit(main())