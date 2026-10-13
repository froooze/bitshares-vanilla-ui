#!/usr/bin/env python3
"""i18n ru chunk-B1: fill the help and pool_net sections ru.json still leaves English.

Scope: ONLY the two sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ru.json, or one whose English master moved, is REFUSED;
  * RU + KEPT_ENGLISH together must account for EVERY untranslated key of the
    two sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset and
REFUSES anything outside them; this batch REFUSES anything outside help and
pool_net. A key that crosses the line is a reviewer's problem, never a script's
silent edit.

Safety gates asserted before anything is written (see main()):

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
                      load-bearing here, because the nine help bodies and the
                      sitemap list are markdown: a sitemap whose "# Wallet"
                      heading or whose 60+ "#/hash" targets lost a line would
                      silently drop a page from the article;
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
                      English. This is the Russian sibling of chunk-A's gate, and
                      it bites twice here: the English about-making body owns the
                      only `builders'` in the help section, and any Russian
                      rewrite of it must reach for «...» instead.

G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: ru.json already ships "x·y=k" in
                      pool_detail.pool_curve, outside this batch's two sections,
                      and the file-wide sweep in verify() would otherwise fail on
                      someone else's honest formula.

Vocabulary is reused verbatim from the part of ru.json that is already
translated, so this batch reads like the rest of the dictionary instead of like
a second dictionary. From chunk-A: аккаунт, актив, баланс, ордер, исполнение,
цена, залог, пул, своп, стейк, полномочие, кошелёк, нода, цепь, деск, стакан,
фид, вестинг, смарткоин, тикет, заверитель, комитет, работник, эмитент,
ончейн, браузер, брейнкей, стенд. Nothing is invented where a Russian crypto UI
keeps the English word - DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy,
Smartcoin, Pool, Brainkey, Feed, React - and the run prints every value that
stays identical to en so a reviewer checks the list instead of guessing.

The sitemap body mirrors the already-translated `menu.p_*` / `menu.section_*`
labels wherever one exists (Дашборд, Мой аккаунт, Пулы ликвидности, API-лаборатория,
Top операций, ...), because the article is a map OF that menu and a link whose
label disagrees with the button beside it is a worse defect than a wording
variance. Three page names have no Russian menu label yet (Cross Rates,
Account Network, and the Discover / Labs / Personal section titles) - they are
translated here on their own merits and listed in the report, so the follow-up
batch that owns the `menu` section can either match them or leave them.

The nine bodies keep the English line-for-line shape: every `#` heading is a
line of its own, every paragraph one line, the three bullet lists three lines.
Apostrophes in the English masters (builders', another's, project's) are
replaced by «...», never carried over (G7).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ru_chunkB1.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ru_chunkB1.py --apply         # writes ru.json
  python3 tooling/apply_i18n_ru_chunkB1.py --verify        # structural re-proof
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

# The two sections this batch owns. Everything else belongs to another batch and
# is REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool_net",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). None of them lives in help or pool_net, so the list is the
# file-wide watchdog shared with chunk-A: if a later pass ever moves one of these
# into this batch's sections, the write is refused instead of translated.
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
    add the first one. It matters most in the help bodies, where English names
    (WebSocket, WebCrypto, BigInt, index.html, .bin) sit next to Russian
    sentences and the temptation is to glue them on with a hyphen.
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

    print("ru chunk-B1: %d planned, %d differ from en, %d intentionally identical"
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
    # ============================================================== help (38)
    # Shared chrome strings of the help section. The confidence trio is a table
    # column, so the three ratings agree with «Надёжность» (feminine) rather
    # than with the language or the translation, which are masculine.
    "help.about_link": u"О проекте",
    "help.confidence_good": u"Хорошая",
    "help.confidence_high": u"Высокая",
    "help.confidence_language": u"Язык",
    "help.confidence_level": u"Надёжность",
    "help.confidence_moderate": u"Средняя — проверьте",
    "help.translation_confidence_heading": (
        u"Насколько надёжен перевод каждого языка"
    ),
    # "Community index" is already «общественный индекс» in ru.json (help.eslab,
    # help.topic_history-index_title), so this directory heading reuses it.
    "help.elastic": u"Общественный индекс (сторонняя история)",
    "help.report_translation_link": (
        u"Сообщить о проблеме в переводе на GitHub"
    ),
    "help.sitemap_sections": u"Разделы",

    # --------------------------------------------------------- help: titles
    "help.topic_about-making_title": u"Как делался этот кошелёк",
    "help.topic_assets-feed_title": u"Публикация ценовых фидов",
    "help.topic_assets-issue_title": u"Выпуск активов",
    "help.topic_browser_title": u"Поддержка браузеров",
    "help.topic_community_title": u"Сообщество",
    "help.topic_menu_title": u"Меню сайта",
    "help.topic_sitemap_title": u"Карта сайта",
    "help.topic_translation-limitations_title": u"Ограничения перевода",

    # ---------------------------------------------------------- help: texts
    # The index blurbs: one short line each, imperative voice like every
    # translated neighbour. «деск» is chunk-A vocabulary (Биржевой деск).
    "help.topic_about-making_text": u"История создания этого кошелька —",
    "help.topic_assets-feed_text": (
        u"Публикуйте ценовые фиды для привязанных к рынку активов, которые "
        u"вы публикуете."
    ),
    "help.topic_assets-issue_text": (
        u"Выпускайте новый объём актива под своим контролем с экрана выпуска."
    ),
    "help.topic_browser_text": (
        u"Какие браузеры запускают кошелёк и что означает уведомление о "
        u"совместимости."
    ),
    "help.topic_community_text": (
        u"Чаты, форумы, обозреватели и код вокруг BitShares."
    ),
    "help.topic_htlc_text": (
        u"Свопы с хеш-блокировкой: либо платёж, либо возврат."
    ),
    "help.topic_menu_text": (
        u"Все страницы этого кошелька, сгруппированные так же, как в меню "
        u"навигации."
    ),
    "help.topic_sitemap_text": (
        u"Все страницы этого кошелька на одной странице: каждая страница меню "
        u"плюс сценарии и подробные виды, у которых нет карточки меню."
    ),
    "help.topic_translation-limitations_text": (
        u"Машинные переводы помечены; английский оригинал всегда в одном "
        u"нажатии. Помогите нам исправить строку."
    ),
    "help.topic_voting_text": (
        u"Голосуйте за заверителей, комитет, работников — или передайте "
        u"голосование прокси."
    ),

    # --------------------------------------------------------- help: bodies
    # Longest body in the batch. 83 lines / 82 newlines, every "#" heading its
    # own line, all 60+ "#/hash" targets byte-verbatim: a lost line here would
    # delete a page from the article, a rewritten hash would 404.
    "help.topic_sitemap_body": (
        u"Все страницы этого кошелька, сгруппированные так же, как "
        u"бургер-меню. Всё, у чего есть ссылка, открывается сразу; подробные "
        u"виды из раздела «Страницы без карточки меню» открываются со своих "
        u"родительских страниц.\n"
        u"# Кошелёк\n"
        u"- [Дашборд](#/)\n"
        u"- [Мой аккаунт](#/account/me)\n"
        u"- [Аккаунты](#/accounts)\n"
        u"- [Перевод](#/transfer)\n"
        u"- [Счёт](#/invoice)\n"
        u"- [Вестинг](#/vesting)\n"
        u"- [Кошелёк](#/wallet)\n"
        u"- [Смена пароля кошелька](#/wallet/password)\n"
        u"- [Создать кошелёк (брейнкей)](#/create-wallet-brainkey)\n"
        u"- [Импорт существующего аккаунта](#/existing-account)\n"
        u"- [Регистрация нового аккаунта](#/create-account)\n"
        u"- [Вход](#/login)\n"
        u"- [Регистрация](#/registration)\n"
        u"- [Рефералы](#/referrals)\n"
        u"# Торговля\n"
        u"- [Биржа](#/markets)\n"
        u"- [Мгновенная торговля](#/instant-trade)\n"
        u"- [Пулы ликвидности](#/pools)\n"
        u"- [Кросс-курсы](#/cross-rates)\n"
        u"- [Займ](#/borrow)\n"
        u"- [Бартер](#/barter)\n"
        u"- [Депозит / Вывод](#/deposit-withdraw)\n"
        u"- [Same-T фонды](#/samet)\n"
        u"- [Спотлайт](#/spotlight)\n"
        u"# Заработок и защита\n"
        u"- [Кредитное предложение](#/credit-offer)\n"
        u"- [Прямой дебит](#/direct-debit)\n"
        u"- [HTLC](#/htlc)\n"
        u"- [Тикеты](#/tickets)\n"
        u"- [Аирдроп](#/airdrop)\n"
        u"- [Кастомные полномочия](#/authorities)\n"
        u"- [Списки аккаунтов](#/lists)\n"
        u"# Управление\n"
        u"- [Голосование](#/voting)\n"
        u"- [Предложения](#/proposals)\n"
        u"- [Создать работника](#/create-worker)\n"
        u"- [Рынки предсказаний](#/prediction)\n"
        u"# Обзор\n"
        u"- [Обозреватель](#/explorer)\n"
        u"- [Активы](#/assets)\n"
        u"- [Создать актив](#/assets/create)\n"
        u"- [Выпустить актив](#/assets/issue)\n"
        u"- [Публикация фида](#/assets/feed)\n"
        u"- [Сетевые комиссии](#/explorer/fees)\n"
        u"- [Операции](#/ops)\n"
        u"- [Топ операций](#/top-ops)\n"
        u"- [Новости](#/news)\n"
        u"# Обозреватель\n"
        u"- [Обозреватель (блокчейн)](#/explorer)\n"
        u"- [Активы](#/explorer/assets)\n"
        u"- [Пулы](#/explorer/pools)\n"
        u"- [Аккаунты](#/explorer/accounts)\n"
        u"- [Заверители](#/explorer/witnesses)\n"
        u"- [Комитет](#/explorer/committee)\n"
        u"- [Рынки](#/explorer/markets)\n"
        u"- [Комиссии](#/explorer/fees)\n"
        u"- [Фиды](#/explorer/feeds)\n"
        u"# Лаборатории\n"
        u"- [API-лаборатория](#/api-lab)\n"
        u"- [ES-лаборатория](#/es-lab)\n"
        u"- [Конструктор транзакций](#/txbuilder)\n"
        u"- [Сеть аккаунтов](#/account-network)\n"
        u"# Личное\n"
        u"- [Троллбокс](#/trollbox)\n"
        u"- [Избранное](#/favourites)\n"
        u"- [Ценовые алерты](#/alerts)\n"
        u"- [Помощь](#/help)\n"
        u"- [Ограничения перевода](#/help/translation-limitations)\n"
        u"- [О проекте](#/about)\n"
        u"- [Сообщество](#/community)\n"
        u"- [Настройки](#/settings)\n"
        u"# Страницы без карточки меню\n"
        u"Варианты регистрации, дески аккаунтов и рынков, а также подробные "
        u"виды открываются со страниц выше или по ссылкам в других местах "
        u"кошелька.\n"
        u"- [Локальная регистрация](#/registration/local)\n"
        u"- [Облачная регистрация](#/registration/cloud)\n"
        u"- [Пример страницы аккаунта](#/account/committee-account)\n"
        u"- [Пример торгового деска](#/market/BTS_USD)\n"
        u"- [Пример страницы актива](#/asset/BTS)\n"
        u"- [Пример деска пула](#/pools/1.19.66)\n"
        u"- [Обзор меню](#/menu)\n"
        u"Подробные виды конкретного кредитного предложения, сделки, "
        u"предложения, блока, транзакции, HTLC, прогнозного рынка, получателя "
        u"перевода, счёта, шлюза, вкладки настроек, вкладки обозревателя или "
        u"статьи помощи открываются со своих родительских страниц и берут id "
        u"или имя из адреса."
    ),
    # 23 lines / 22 newlines: heading, blank, heading, para, blank, para, blank,
    # heading, para, blank, para, blank, heading, para, blank, bullet x3,
    # blank, heading, para, blank, para. The * on a line is the machine-filled
    # marker chip, so the prose has to explain what the reader sees.
    "help.topic_translation-limitations_body": (
        u"Перевод, помеченный как машинный, написан машиной. Его никто не "
        u"читал, чтобы убедиться, что он значит то же, что английский, — "
        u"поэтому каждый язык, кроме английского, несёт метку в шапке этого "
        u"кошелька. Английский — текст, с которого переведены остальные, "
        u"поэтому метки у него нет.\n"
        u"\n"
        u"# Что означает звёздочка на строке\n"
        u"Звёздочка * на строке подписи означает сразу две вещи: формулировку "
        u"заполнила машина, а английский оригинал в одном нажатии. Нажмите на "
        u"*, и английский появится под строкой в точности так, как его хранит "
        u"английский мастер этого кошелька, — это тот самый текст, с которого "
        u"переведены все остальные языки, а не пересказ этого текста.\n"
        u"\n"
        u"Метка стоит на строке, а не внутри неё. * отмечает одну целую "
        u"переведённую строку, а кошелёк выбирает такие строки по "
        u"фиксированному правилу: каждая строка на экране подписи, "
        u"необратимого действия или восстановления — до ограничения длины, "
        u"потому что длинный абзац покрыт этой статьёй, — плюс любая строка в "
        u"любом месте, чей английский текст содержит предупреждающие "
        u"формулировки. Поэтому строка, которая только называет id или сумму, "
        u"метку всё же несёт (поле «Кому» в переводе, например), а длинный "
        u"абзац, упоминающий id, — нет. Голое значение из цепи — сумма в "
        u"ячейке, id в столбце, символ актива — переведённой строкой вообще "
        u"не является, поэтому метки не несёт: за ним нет английской "
        u"формулировки, с которой можно сравнить.\n"
        u"\n"
        u"# Что означают уровни надёжности\n"
        u"У каждого языка, который поставляет этот кошелёк, одна оценка, и "
        u"она указана в таблице ниже. Высокая означает, что формулировка "
        u"близко следует за английским и читается естественно. Хорошая "
        u"означает, что перевод пригоден, хотя отдельная фраза может звучать "
        u"неловко. Средняя означает — считайте перевод черновиком и сверяйтесь "
        u"с английским, прежде чем полагаться на него.\n"
        u"\n"
        u"Все оценки ниже выставляет та же машина, которая написала строки, "
        u"оценивая собственную работу; никто независимо их не проверял. "
        u"Оценка описывает, что проверено на данный момент, для языка в целом, "
        u"а не построчно. Сам английский — эталон: он написан вручную, и все "
        u"остальные языки переведены с него.\n"
        u"\n"
        u"# Как исправить строку\n"
        u"Исправление начинается с сообщения. Укажите, на каком языке была "
        u"строка, приведите ключ, который она раскрывает, вставьте английский "
        u"текст, который она должна была передать, и предложите свою "
        u"формулировку.\n"
        u"\n"
        u"- Одно сообщение на строку — так исправление легко применить.\n"
        u"- Сначала сообщайте об экранах подписи: неверная фраза в окне "
        u"подтверждения обходится дороже всего.\n"
        u"- Используйте ссылку в конце этой статьи. Она открывает задачу, уже "
        u"помеченную как перевод, в трекере этого проекта, так что переписывать "
        u"ничего не нужно.\n"
        u"\n"
        u"# Только исправления ведут к проверке человеком\n"
        u"Ничто другое не снимает отметку машинного перевода: ни частота "
        u"использования языка, ни вторая машина, согласная с первой, ни память "
        u"переводов. Строка становится проверенной человеком, когда живой "
        u"человек читает её на своём языке и принимает, и проверка действует "
        u"только для того языка, который действительно проверили.\n"
        u"\n"
        u"До тех пор метка остаётся на месте. Непрочитанный перевод лучше, "
        u"чем никакого перевода, но это не то же самое, что перевод, за "
        u"который отвечает человек."
    ),
    # 5 lines. The English quotes two literals ("acquire bitshares-ui", "Full
    # build dialog") with ASCII double quotes; Russian uses «...» (G7 keeps the
    # apostrophe rule honest elsewhere). The route (#/about) and the query
    # (?dialog=N) stay byte-verbatim.
    "help.topic_about-making_body": (
        u"# Как делался этот кошелёк\n"
        u"Ниже — исходная история создания: каждый запрос, который создал "
        u"этот кошелёк, от «acquire bitshares-ui» 26 сентября 2026 года до "
        u"исправления issue-1 3 октября, вместе с ответами создателей — "
        u"сохранённая без правок.\n"
        u"В ней записаны решения, на которых стоит этот кошелёк: отказ от "
        u"очередного апгрейда React после issue #3583 и его ловушки в тысячу "
        u"часов, так что кошелёк не зависит ни от чего с циклом релизов; "
        u"подпись каждой транзакции локально, как в старом кошельке, а не "
        u"передача её наружу; три темы с классическим оформлением по "
        u"умолчанию; числа в человеческих единицах, а не сырые целочисленные "
        u"значения цепи; вёрстка сначала под телефон, начиная с первого "
        u"слайса; и комиссии, читаемые с живой цепи, а не оцениваемые. "
        u"Читайте это как историю: так был построен кошелёк.\n"
        u"# Полный архив диалогов\n"
        u"Полная запись всех обменов репликами живёт на странице «О проекте» "
        u"(#/about). Разверните там раздел «Полный диалог создания», чтобы "
        u"просмотреть все обмены, отфильтровать по слову или перейти к "
        u"конкретному обмену через ?dialog=N."
    ),
    # 9 lines. The last line sends the reader to the Permissions article, whose
    # ru.json title is «Разрешения»; the brainkey line echoes the index blurb
    # help.topic_backups_text («Ваш брейнкей И ЕСТЬ бэкап»).
    "help.topic_backups_body": (
        u"# Сделайте бэкап заранее и дважды\n"
        u"Сделайте бэкап локального кошелька до пополнения — дальше обычно "
        u"хватает одной копии, но храните её как минимум в двух надёжных "
        u"местах, доступных только вам.\n"
        u"Файла бэкапа в этом кошельке нет: ваш брейнкей И ЕСТЬ бэкап, а одна "
        u"фраза сама по себе ничего не восстанавливает. Без слов И фразы "
        u"средства потеряны. Никогда не храните фразу рядом со словами.\n"
        u"# Ваш брейнкей и есть бэкап\n"
        u"Если вы никогда не импортировали сырые ключи вручную, весь кошелёк "
        u"детерминированно выводится из одного брейнкея — строки слов. "
        u"Записав брейнкей, вы сохраняете все аккаунты и средства этого "
        u"кошелька.\n"
        u"Посмотрите его в менеджере кошелька и перепишите на бумагу, храня её "
        u"отдельно от всего цифрового. .bin-файлы эталонного кошелька "
        u"импортировать сюда нельзя — кошелёк говорит об этом на экране, и "
        u"скачивания файла не существует.\n"
        u"# Продвинутое: иерархические полномочия\n"
        u"Если вы используете взвешенные полномочия на несколько аккаунтов "
        u"вместо обычных ключей, одного бэкапа ключей может НЕ хватить — "
        u"важна сама структура полномочий.\n"
        u"Перечитайте статью «Разрешения» и запишите всю настройку "
        u"полномочий, а не только слова."
    ),
    # 7 lines. The four platform features keep their English spec names - they
    # are identifiers the reader may paste into about:blank and test - and the
    # schemes http/https stay verbatim.
    "help.topic_browser_body": (
        u"# Проверяются возможности, а не названия браузеров\n"
        u"Этот кошелёк никогда не спрашивает, каким браузером вы "
        u"пользуетесь, — он проверяет четыре возможности платформы, которые "
        u"ему действительно нужны: WebSocket (данные цепи), WebCrypto "
        u"(хранилище ключей), BigInt (денежная математика) и локальное "
        u"хранилище (настройки). Отсутствие баннера — это успех: на "
        u"современном браузере нет уведомления, значит, всё на месте.\n"
        u"# Самая частая причина: небезопасный контекст\n"
        u"Современные браузеры открывают WebCrypto только в безопасном "
        u"контексте: страницы https, localhost и открытые файлы. Тот же "
        u"актуальный браузер, отданный по обычному http (например, по адресу "
        u"в локальной сети), сообщает, что WebCrypto отсутствует, — с "
        u"браузером всё в порядке, с адресом нет. Отдавайте папку по https "
        u"или через localhost либо откройте index.html напрямую.\n"
        u"# Что по-прежнему работает\n"
        u"Просмотр работает всегда: балансы, рынки, обозреватель и "
        u"голосование читают публичные данные цепи без возможностей кошелька. "
        u"Только локальной подписи не хватает отсутствующей детали. Закрытие "
        u"уведомления скрывает его на этом устройстве; страницу оно никогда не "
        u"блокирует."
    ),
    # 10 lines. The vault paragraphs reuse the wording the already-translated
    # help.topic_password_body established («локальное хранилище», «уникальная
    # фраза, записанная на бумаге»), so the two articles cannot contradict.
    "help.topic_wallets_body": (
        u"# Веб-приложение с локальным хранилищем\n"
        u"Это приложение работает в вашем браузере и общается с нодой цепи "
        u"как со шлюзом в сеть. Всё секретное остаётся в локальном хранилище "
        u"браузера.\n"
        u"# Без облачного входа\n"
        u"У этого кошелька нет входа по имени пользователя и паролю: каждый "
        u"кошелёк здесь местный, привязанный к одному браузеру. Чтобы "
        u"пользоваться своим аккаунтом в новом браузере или на новом "
        u"компьютере, начните с того же брейнкея — учётных данных, которые "
        u"открыли бы его откуда угодно сами по себе, не существует.\n"
        u"# Локальный кошелёк\n"
        u"Локальный кошелёк — это база данных внутри одного конкретного "
        u"браузера. Он не переедет на другой компьютер или в другой браузер, "
        u"если только вы не перенесли брейнкей и не импортировали его.\n"
        u"Прочитайте статью «Резервные копии», прежде чем опираться на "
        u"локальный кошелёк с настоящими средствами.\n"
        u"# Дисциплина пароля\n"
        u"Пароль шифрует хранилище. Короткие или повторные пароли падают от "
        u"подбора; уникальная фраза, записанная на бумаге, — нет.\n"
        u"Смена пароля перешифровывает всё — сначала проверьте текущий, потом "
        u"убедитесь, что кошелёк всё ещё разблокируется, и только после этого "
        u"уходите."
    ),
    "help.topic_community_body": (
        u"# Сообщество\n"
        u"Люди и места вокруг BitShares — домашняя страница, код, "
        u"обозреватели, форумы и чаты — живут на странице Сообщества."
    ),
    "help.topic_menu_body": (
        u"# Меню сайта\n"
        u"Страница «Меню» перечисляет все экраны этого кошелька по разделам, "
        u"поэтому до любого деска — одно нажатие."
    ),
    "help.topic_assets-feed_body": (
        u"# Публикация ценовых фидов\n"
        u"Публикуйте расчётную цену привязанного к рынку актива с экрана "
        u"публикации фида; окно подтверждения показывает точную комиссию до "
        u"подписи."
    ),
    "help.topic_assets-issue_body": (
        u"# Выпуск активов\n"
        u"Создавайте новый объём актива, которым управляет ваш аккаунт, с "
        u"экрана выпуска; суммы используют точность актива, а окно "
        u"подтверждения показывает точную комиссию до подписи."
    ),

    # ========================================================== pool_net (27)
    # Vocabulary mirrors the already-translated market_net twin in ru.json:
    # Свернуть / Развернуть, Загрузка …, узел/линия, «·» glue. «переход» is
    # chunk-A's word for a graph hop (account_net.depth_1 «1 переход»).
    "pool_net.canvas_label": (
        u"Карта сети пулов. Нажмите Enter, чтобы открыть BTS."
    ),
    "pool_net.col_a": u"Актив 1",
    "pool_net.col_b": u"Актив 2",
    "pool_net.col_pool": u"Пул",
    "pool_net.collapse": u"Свернуть",
    "pool_net.direct": u"в паре с BTS",
    "pool_net.empty": u"Нет пулов под этот фильтр.",
    "pool_net.expand": u"Развернуть",
    "pool_net.hops": u"%(n)s переходов до BTS",
    # "Brands" here is the colour grouping of the palette (BTS, committee
    # smartcoins, other) in the legend, NOT the footer brand link — the
    # Russian crypto spelling for a token family is «бренд».
    "pool_net.legend": u"Бренды",
    "pool_net.loading": u"Загрузка сети…",
    "pool_net.node_card": u"%(sym)s (%(id)s) · пулов: %(n)s · %(hops)s",
    # The "shipped skeleton" is data/pools.json, bundled in the repo — the same
    # thing market_net.offline calls «рынки из кэша», so the honest Russian is
    # the data that came with the wallet, named as such.
    "pool_net.offline": (
        u"Сеть недоступна — показаны пулы, вложенные в кошелёк. Повторите "
        u"при подключении."
    ),
    "pool_net.offline_empty": (
        u"Сеть недоступна — вложенные пулы не закешированы."
    ),
    "pool_net.orphan": u"оторван от BTS",
    "pool_net.partial": (
        u"Живое обновление неполно — показаны вложенные пулы."
    ),
    "pool_net.phys": u"Физика",
    "pool_net.prompt": (
        u"Нажмите на узел актива, на линию — на пул."
    ),
    "pool_net.ramp": u"Размер пула: от малого к большому",
    "pool_net.ready": u"пулов: %(pools)s · активов: %(assets)s",
    "pool_net.title": u"Сеть пулов",
    "pool_net.twin": u"Строки пулов (%(n)s)",
    "pool_net.twin_more": (
        u"Показано %(shown)s из %(n)s пулов — сузьте фильтр, чтобы увидеть "
        u"меньше."
    ),
    "pool_net.verdict_full": u"пулов: %(pools)s · активов: %(assets)s",
    "pool_net.verdict_orphan": u"Нет маршрута между %(a)s и %(b)s",
    "pool_net.verdict_path": u"%(a)s достигает %(b)s за %(n)s переходов",
    "pool_net.verdict_star": u"Пулы, связанные с %(s)s: %(n)s",
}

# Keys whose Russian value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from RU. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * pure glue a tooltip prints as data: the two edge cards, which are nothing
#     but placeholder pairs separated by «·» and «–» plus a balance formula
#     ("%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s" and its
#     balance-less twin). No prose means nothing to translate — the same call
#     chunk-A made for market_net.edge_card.
# No loanword survives here: unlike chunk-A's HTLC/NFT/PSAR cells, every
# pool_net string carried prose, so all 27 translated and only the two data
# templates stay Latin.
KEPT_ENGLISH = {
    # ---- pool_net
    "pool_net.edge_card": (
        u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s"
    ),
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
}


if __name__ == "__main__":
    sys.exit(main())