#!/usr/bin/env python3
"""i18n ru chunk-C: every signing/UX section ru.json still leaves English.

Scope: the 43 sections listed below - approval, xrate, proposal, borrow,
settings, trade, trollbox, vote, barter, pool_detail, auth, i18n, tour,
transfer, market, unlockconfirm, asset, createworker, instant, nav,
account_net, createaccount, credit, debit, gateway, htlc, market_ind,
market_net, common, dashboard, eslab, pool_net, prediction, ticket, txbuilder,
apilab, assets_feed, compat, confirm, explorer_assets, misc, news, pools and
vesting. chunk-A owns account/market/market_net/asset/settings/account_net,
B1 owns help/pool_net; both REFUSE anything outside themselves, and so does
this one. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ru.json, or one whose English master moved, is REFUSED;
  * RU + KEPT_ENGLISH together must account for EVERY untranslated key of the
    43 sections, so a forgotten string is a refusal, never a silent English.

This is the SAFETY-CRITICAL batch. Most of these strings render DUAL-LINE
inside a signing confirmation dialog: the reader sees the Russian line with an
English reference one tap away, an asterisk and a link to the warning. So
wherever a misreading could hide an amount, a destination, an irreversible
action or a permission, the plainer and more literal Russian wins over the more
idiomatic one. "Удалить предложение", not a softened verb; "Итого к продаже",
not a summary word; "Разблокировать для подписи", not a friendlier synonym.
A reader comparing two lines must never have to guess which one hides the
number. The verb forms match the already-translated neighbours of the SAME
flow (misc.confirm_authority_delete_op_56 "Подтвердите удаление полномочия",
credit.confirm_offer_delete "Подтвердите удаление оффера",
proposal.review "Проверка", borrow.review_adjust "Проверка настройки"), so a
dialog title never contradicts the button that opened it.

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
  G7  script + quotes  no word in ru.json mixes Cyrillic and Latin letters
                      (the homoglyph a transliterated loanword invites - "ордер"
                      is impossible in the shipped file and stays that way), and
                      no value this batch writes may carry an ASCII or
                      typographic apostrophe: Russian quotes with «...», and
                      vote.proxies_follow_another_account_s_slate_re is the one
                      English apostrophe this batch has to re-spell rather than
                      copy. This is the Russian sibling of chunk-A's and B1's
                      gate, and it bites hardest on the multisig prose, where
                      "co-owner's" and "another account's" appear in English;
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric. That one exception is
                      load-bearing: ru.json already ships "x·y=k" in
                      pool_detail.pool_curve, outside this batch, and the
                      file-wide sweep in verify() would otherwise fail on
                      someone else's honest formula.

Vocabulary is reused verbatim from the part of ru.json that is already
translated, so this batch reads like the rest of the dictionary. Measured over
the shipped file: стейк (stake, 34 strings), смарткоин (23), залог (50),
ордер (120), прокси (21), бюллетень (slate, 7), комиссия (fee), перевод
(transfer), предложение (proposal), заверитель (witness), комитет, работник
(worker), эмитент, тикет, вестинг, кошелёк, нода, цепь, деск, стакан, фид,
мемо (27), брейнкей (31). Loanwords stay exactly as a Russian crypto UI writes
them - DEX, HTLC, BitShares, BTS, API, NFT, PMA, UIA, MCR, SMA, EMA, PSAR, PnL,
URL, ID, Fill or Kill, TxBuilder, Spotlight-as-Спотлайт - and the run prints
every value that stays identical to en so a reviewer checks the list instead
of guessing.

The honesty surface (i18n.badge_*, i18n.risk_*) IS translated here: it is the
warning a Russian reader gets about their own Russian, so leaving it English
would mean the one string that admits the text is machine-written is the one
string no Russian speaker can read. i18n.risk_show_english is an aria-label
spoken aloud at EVERY signing line, so it is the shortest string in the batch
("Показать английский оригинал строки", 33 characters against English's 40).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ru_chunkC.py                 # dry run (asserts)
  python3 tooling/apply_i18n_ru_chunkC.py --apply         # writes ru.json
  python3 tooling/apply_i18n_ru_chunkC.py --verify        # structural re-proof
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

# The 43 sections this batch owns. Everything else belongs to another batch and
# is REFUSED here as out of scope.
SECTIONS = frozenset((
    "account_net", "apilab", "approval", "asset", "assets_feed", "auth",
    "barter", "borrow", "common", "compat", "confirm", "createaccount",
    "createworker", "credit", "dashboard", "debit", "eslab",
    "explorer_assets", "gateway", "htlc", "i18n", "instant", "market",
    "market_ind", "market_net", "misc", "nav", "news", "pool_detail",
    "pool_net", "pools", "prediction", "proposal", "settings", "ticket",
    "tour", "trade", "transfer", "trollbox", "txbuilder", "unlockconfirm",
    "vesting", "vote", "xrate",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). settings.* IS in this batch's sections, so the list is no longer
# a file-wide watchdog here: it is the reason all nine settings keys sit in
# KEPT_ENGLISH instead of being translated one by one.
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
    add the first one. It matters most in the multisig and cross-rate prose,
    where English tokens (op, call_order_update, stake) sit next to Russian
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
        print("    %-16s %d identical to en" % (sec, by_section[sec]))
    print("  keys in my sections still at en, not in this batch: %d"
          % len(scope_left))
    for k in scope_left:
        print("      %s = %r" % (k, d.get(k)))
    honesty = [k for k in sorted(e)
               if k.startswith("i18n.") and d.get(k) == e[k]]
    print("  honesty keys (i18n.*) still reading English: %d %s"
          % (len(honesty), honesty))
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
    # UNCLAIMED, which is the honest state for them - and it is load-bearing
    # for settings.network_devnet, which tooling/check_i18n.py does NOT list
    # among its IDENTIFIERS, so claiming it would read as a false claim.
    # Nothing else in _meta moves - filling strings is not verification, so the
    # controller's v2 provenance/verified/high_risk fields stay untouched.
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

    print("ru chunk-C: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-16s %d" % (sec, by_section.get(sec, 0)))
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
    # ============================================================ approval (20)
    # The extension-wrapper approval screen (deliberately deferred, per
    # AGENTS.md 10.7): the strings exist, the screen does not. They are still
    # SIGNING chrome - Approve is the button that lets a site spend - so the
    # verbs stay plain and literal: Одобрить / Отклонить, never a softened
    # "разрешить" that could read as "allow".
    "approval.account": u"Аккаунт: ",
    "approval.approve": u"Одобрить",
    "approval.approved": u"Одобрено и отправлено.",
    # "Chain:" - the SAME English string txbuilder.chain_prefix already renders
    # as "Сеть:". That one is kept and flagged: «Сеть» elsewhere in ru.json is
    # the NETWORK (borrow.network, transfer.row_network), so «Цепь» is the
    # unambiguous Russian for the ledger and this batch does not add a second
    # sense to the word. glossary/ru.md lists txbuilder.chain_prefix as the
    # counter-example to align.
    "approval.chain": u"Цепь: ",
    "approval.close": u"Закрыть",
    "approval.denied": u"Отклонено.",
    "approval.deny": u"Отклонить",
    "approval.expires_in": u"Истекает через ",
    "approval.load_failed": u"Не удалось загрузить одобрение.",
    "approval.loading": u"Загрузка одобрения…",
    "approval.locked_note": (
        u"Сессия заблокирована — введите пароль кошелька, чтобы одобрить."
    ),
    "approval.no_fields": u"Нет полей для показа.",
    "approval.no_reply": u"Нет ответа от подписанта.",
    "approval.no_runtime": u"Среда расширения недоступна.",
    "approval.password": u"Пароль",
    "approval.remember": u"Запомнить этот аккаунт для этого сайта",
    "approval.site_prefix": u"Сайт: ",
    "approval.title": u"Одобрить подпись",
    "approval.unknown_intent": u"Запрос на одобрение не найден.",
    "approval.wallet_title": u"Этот кошелёк просит подпись",

    # ================================================================= auth (7)
    # Mirrors the already-translated account.multisig_* and asset.multisig_*
    # twins word for word ("Общий аккаунт", "Смотреть предложения", "Открыть
    # конструктор транзакций", "со-владельцы") so the three multisig panels
    # cannot contradict each other. G7: the English "another account's" and
    # "co-owner's" apostrophes are not carried over - Russian does not need
    # them, and the dictionary has none.
    "auth.multisig_body": (
        u"В этом кошельке один ключ. Общим аккаунтам нужны предложения и "
        u"одобрения со-владельцев, координация — по id предложения "
        u"(1.10.N). Просмотр публичен; пароль нужен только для подписи."
    ),
    "auth.multisig_open_proposals": u"Смотреть предложения",
    "auth.multisig_open_txbuilder": u"Открыть конструктор транзакций",
    "auth.multisig_step_approve": (
        u"Со-владельцы одобряют (op 23) на странице предложений или "
        u"подписывают вместе через конструктор транзакций."
    ),
    "auth.multisig_step_propose": (
        u"Предложите операцию (в Переводе есть Отправить и Предложить; "
        u"активы, бартер и заём ссылаются на предложения)."
    ),
    "auth.multisig_step_share": (
        u"Передайте со-владельцам id предложения 1.10.N."
    ),
    "auth.multisig_title": u"Общие аккаунты и мультиподпись",

    # =============================================================== barter (7)
    # DUAL-LINE signing chrome. "Peer A" becomes «Сторона A» because that is
    # what the two legs are already called in this flow (barter.side_a,
    # barter.peer_a_account) - a reader must not have to learn a third name for
    # the same side while deciding who pays the fee.
    "barter.confirm_barter_proposal_op_22": (
        u"Подтвердите предложение бартера (op %(op)s)"
    ),
    "barter.propose_barter_op_22": u"Предложить бартер (op %(op)s)",
    "barter.step_build": u"Собрать",
    "barter.step_preview": u"Предпросмотр",
    "barter.step_propose": u"Предложить",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"Предпросмотр двустороннего атомарного свопа. Сначала "
        u"предпросмотр, потом ПРЕДЛОЖЕНИЕ вкладывает переводы обеих сторон "
        u"в одно предложение (op %(op)s, плательщик комиссии = Сторона A)."
    ),
    "barter.uc_title": u"Разблокировать для подписи",

    # =============================================================== borrow (9)
    # DUAL-LINE signing chrome: an irreversible on-chain position change.
    # "Adjust" is «Скорректировать», the same verb borrow.adjust_broadcast and
    # market.adjust_button already ship, and the op name stays in English
    # (call_order_update) because it is the serializer's own field name.
    "borrow.adjust": u"Скорректировать",
    "borrow.adjust_position_op_3": u"Скорректировать позицию (op %(op)s)",
    "borrow.bids_no_cancel": (
        u"Биды нельзя отменить после размещения — они исполняются или истекают."
    ),
    "borrow.close_position": u"Закрыть позицию",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Маржинальные позиции занимают битассет под залог. Пополнение "
        u"залога или погашение долга корректирует op %(op)s "
        u"(call_order_update) в вашем колл-ордере."
    ),
    "borrow.open_a_new_position_op_3": u"Открыть новую позицию (op %(op)s)",
    "borrow.repay_full": u"Погасить полностью",
    "borrow.settlement_bids_op_45": u"Биды погашения (op %(op)s)",
    "borrow.uc_title": u"Разблокировать для подписи",

    # =============================================================== credit (3)
    "credit.my_deals_borrower": u"Мои сделки (заёмщик)",
    "credit.no_borrower_deals": (
        u"Сделок заёмщика пока нет — сделки появятся после займа по офферу."
    ),
    "credit.uc_title": u"Разблокировать для подписи",

    # ================================================================ debit (3)
    "debit.spotlight_title": u"Спотлайт",
    "debit.uc_order": u"Ордер",
    "debit.uc_title": u"Разблокировать для подписи",

    # ============================================================= prediction (1)
    "prediction.uc_title": u"Разблокировать для подписи",

    # ================================================================ trade (9)
    # DUAL-LINE signing chrome: the unlock dialog's own field terms, which sit
    # beside an amount and a price. «Итого к продаже» is the literal total,
    # matching market.update_amount "Сумма к продаже" - a summary word here
    # would be exactly the place a reader could misread what leaves the account.
    "trade.tab_single": u"Одиночные",
    "trade.uc_amount": u"Сумма",
    "trade.uc_orders": u"Ордера",
    "trade.uc_price": u"Цена",
    "trade.uc_range": u"Диапазон цен",
    "trade.uc_title": u"Разблокировать, чтобы продолжить",
    "trade.uc_total": u"Итого к продаже",

    # ============================================================= transfer (7)
    # DUAL-LINE signing chrome. transfer.unlock_sign is the button that opens
    # the review, so it must say what it does: «Разблокировать и проверить»,
    # matching trade.unlock_review and the «Проверка» family
    # (proposal.review, credit.review_*).
    "transfer.confirm_proposal_title": u"Подтвердите предложение (op %(op)s)",
    "transfer.enclosed_op_note": (
        u"Вложенная операция: перевод (op %(op)s) — исполняется только после "
        u"одобрений."
    ),
    "transfer.propose_notice_locked": (
        u"Предлагающий по умолчанию %(name)s (%(id)s), пока заблокировано — "
        u"разблокируйте, чтобы действовать от своего имени."
    ),
    "transfer.share_needs_to_amount": (
        u"Для ссылки нужны получатель и сумма."
    ),
    "transfer.uc_title": u"Разблокировать, чтобы продолжить",
    "transfer.unlock_sign": u"Разблокировать и проверить",

    # =============================================================== unlock (5)
    # The password dialog. unlockconfirm.unlock_post is shared with the
    # trollbox post button, so both say «Разблокировать и опубликовать».
    "unlockconfirm.cancel": u"Назад",
    "unlockconfirm.empty_password": u"Введите пароль кошелька.",
    "unlockconfirm.password": u"Пароль",
    "unlockconfirm.unlock_failed": u"Разблокировка не удалась.",
    "unlockconfirm.unlock_post": u"Разблокировать и опубликовать",

    # ========================================================== createworker (3)
    "createworker.confirm_worker_op_34": (
        u"Подтвердите работника (op %(op)s)"
    ),
    # The one long signing instruction in the batch. It tells the reader that
    # op 34 broadcasts DIRECTLY, not through a proposal - the difference
    # between a reversible multisig action and an immediate one - so the
    # sentence keeps the English order and keeps both op numbers.
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Черновик работника (op %(op)s). Предпросмотр живой; проверка "
        u"называет живую комиссию, затем Подписать и отправить транслирует "
        u"op %(op)s напрямую — работники создаются прямой операцией, а не "
        u"предложением."
    ),
    "createworker.worker_preview_op_34": u"Предпросмотр работника (op %(op)s)",

    # ============================================================== proposal (10)
    # DUAL-LINE signing chrome. Deleting a proposal is irreversible, so
    # delete_proposal_op_24 keeps the plainest possible verb, the same one
    # misc.confirm_authority_delete_op_56 and proposal.remove already use.
    # The two suffixes are appended to a bare proposal id, so they keep their
    # leading space and their trailing ": ".
    "proposal.active_suffix": u" (активное): ",
    "proposal.confirm_proposal_create_op_22": (
        u"Подтвердите создание предложения (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Подтвердите удаление предложения (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"Удалить предложение (op %(op)s)",
    "proposal.multisig_story": (
        u"Общий аккаунт? Один со-владелец предлагает, передаёт id 1.10.N, "
        u"остальные одобряют ниже. Работу с несколькими операциями или с "
        u"нескольких устройств продолжайте в конструкторе транзакций."
    ),
    "proposal.open_txbuilder": u"Открыть конструктор транзакций",
    "proposal.owner_suffix": u" (владелец): ",
    "proposal.raw_prefix": u"сырой: ",
    "proposal.viewing_as": (
        u"Просмотр как %(name)s (%(id)s) — разблокируйте, чтобы действовать "
        u"от своего имени."
    ),

    # ================================================================= vote (8)
    # The proxy mode strings are the most dangerous in the batch: they are the
    # only place the reader is told WHOSE stake signed. "self" stays an
    # explicit «от себя» rather than a pronoun that could hide the account,
    # and the voting_account id is kept where the English keeps it.
    # slate is «бюллетень» (vote.sent_middle), stake is «стейк».
    "vote.ballot_intro": (
        u"Ваш стейк выбирает заверителей и комитет и финансирует работников — "
        u"все числа и доли ниже читаются из живой цепи."
    ),
    "vote.confirm_witness_update_op_21": (
        u"Подтвердите обновление заверителя (op %(op)s)"
    ),
    "vote.direct_note": (
        u"Голосование опубликовано напрямую (voting_account %(id)s)."
    ),
    "vote.in_sync": (
        u"Бюллетень совпадает с цепью — публиковать нечего."
    ),
    "vote.proxies_follow_another_account_s_slate_re": (
        u"Прокси следуют бюллетеню другого аккаунта — прочитайте, как "
        u"работает голосование, прежде чем задать прокси."
    ),
    "vote.proxy_follows": (
        u" — ваш стейк следует за этим аккаунтом; бюллетень ниже только для "
        u"чтения."
    ),
    "vote.retried_prefix": (
        u"Нода отклонила режим прокси %(mode)s, поэтому голос опубликован от "
        u"себя (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"Нода отклонила режим прокси %(mode)s — повтор один раз от себя…"
    ),

    # ============================================================== createacct (3)
    # The registration wizard's three step names. «Брейнкей» rather than
    # "Brainkey": ru.json already says брейнкей in 31 strings (chunk-A's
    # auth.d_brainkey_help and menu.p_brainkey among them), and a wizard that
    # spelled it two ways on one screen would be the reader's first proof that
    # the translation is machine-made.
    "createaccount.step_brainkey": u"Брейнкей",
    "createaccount.step_name": u"Имя",
    "createaccount.step_register": u"Зарегистрировать",

    # ================================================================= tour (7)
    # Marketing copy, so the register is the imperative the tour already uses
    # (tour.s2_title "Выберите рынок", tour.s5_title "Продолжайте изучать").
    "tour.away_note": (
        u"На биржевом деске — откройте его, чтобы увидеть эту подсветку."
    ),
    "tour.s1_body": (
        u"Каждая страница читает публичные данные цепи без входа. Откройте "
        u"рынок, чтобы начать — пароль спрашивается только при подписи."
    ),
    "tour.s1_title": u"Смотрите всё бесплатно, подписывайте локально",
    "tour.s3_body": (
        u"Свечи цены, объём и глубина, а также меню индикаторов: наложения "
        u"вроде SMA и EMA, осцилляторы вроде RSI, MACD и Стохастика. "
        u"Откройте биржу, чтобы увидеть это вживую."
    ),
    "tour.s3_title": u"Смотрите живые графики цен",
    "tour.s4_body": (
        u"Панели Покупка и Продажа принимают любые числа для тренировки. "
        u"Ничего не покидает вашу машину, пока вы не проверите и не "
        u"подпишете разблокированным кошельком. Откройте биржу, чтобы "
        u"попробовать."
    ),
    "tour.s4_title": u"Потренируйтесь покупать и продавать",

    # =================================================================== i18n (6)
    # THE HONESTY SURFACE, and the whole reason this batch exists for these
    # seven keys: the string that admits the text is machine-written must be
    # readable by the person it warns. Left in English it would be the one
    # line no Russian speaker can check.
    # i18n.risk_show_english is an aria-label spoken aloud at EVERY signing
    # line, so it is deliberately the shortest string here (33 characters
    # against the English 40) - a long label would be read out on every tap.
    "i18n.badge_body": (
        u"Эти переводы написаны машиной и не проверены человеком. Строки, "
        u"помеченные * на экранах подписи, показывают также оригинал на "
        u"английском."
    ),
    "i18n.badge_details": u"Что это значит",
    "i18n.badge_improve": u"Помогите улучшить этот перевод",
    "i18n.badge_label": (
        u"Статус перевода: переведено машиной, не проверено человеком"
    ),
    "i18n.risk_about_translations": u"Об этих переводах",
    "i18n.risk_show_english": u"Показать английский оригинал строки",

    # ================================================================= xrate (17)
    # The cross-rate desk (read-only, no signing). "hop" is «переход» per
    # chunk-A's account_net.depth_1 "1 переход" and pool_net.hops. The three
    # numbers a reader might mistake for each other - pools, assets, pools
    # holding a last swap - stay in the English order with the same "·"
    # separators, so the status line reads the same way as the map legends
    # beside it.
    "xrate.add_btn": u"Добавить столбец",
    "xrate.asset_col": u"Актив",
    "xrate.base_pinned": u"BTS — базовый столбец, его нельзя удалить.",
    "xrate.empty": (
        u"Нет активов пулов в пределах 3 переходов от BTS в этой сети."
    ),
    "xrate.intro": (
        u"Каждый актив пула оценён по его последнему свопу, пересчитан через "
        u"граф пулов. Ничего не подписывается и ничего не сохраняется."
    ),
    "xrate.load_failed": u"Не удалось загрузить кросс-курсы: ",
    "xrate.loading": u"Чтение пулов…",
    "xrate.no_route_col": (
        u"Нет маршрута к %(sym)s в пределах 6 переходов по пулам."
    ),
    "xrate.refresh_btn": u"Обновить цены",
    "xrate.remove_btn": u"Убрать ",
    "xrate.retry_btn": u"Повторить",
    "xrate.show_all": u"Показать все активы",
    "xrate.status": (
        u"%(pools)s пулов · %(assets)s активов в пределах 3 переходов · "
        u"%(done)s из %(total)s пулов имеют последний своп"
    ),
    "xrate.title": u"Кросс-курсы",
    "xrate.token_label": u"Добавить котируемый токен",
    "xrate.unknown_token": u"Нет актива пула с именем %(sym)s.",
    "xrate.unpriced": (
        u"У одного плеча этого маршрута ещё нет записанного свопа."
    ),

    # ============================================================== trollbox (9)
    "trollbox.bytes_unit": u"байт",
    "trollbox.channel_row": u"Канал",
    "trollbox.fee": u"Комиссия",
    "trollbox.language_row": u"Язык",
    "trollbox.message_row": u"Сообщение",
    "trollbox.post_review_title": u"Проверьте сообщение",
    "trollbox.size_row": u"Размер",
    "trollbox.title": u"Троллбокс",
    "trollbox.unlock_post": u"Разблокировать и опубликовать",

    # ========================================================== pool_detail (7)
    # map_connects_fallback is byte-for-byte the already-translated
    # market.map_connects_fallback: two graph legends that say different things
    # would make one of them a lie.
    "pool_detail.candle_capped": u"окно обрезано",
    "pool_detail.candle_count": (
        u"%(swaps)s свопов · %(count)s × %(bucket)s свечей"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s свопов · %(actual)s из %(requested)s × %(bucket)s свечей"
    ),
    "pool_detail.invert": u"Инвертировать",
    "pool_detail.invert_label": (
        u"Инвертировать ориентацию графика (A-на-B / B-на-A)"
    ),
    "pool_detail.map_connects": (
        u"Линия соединяет два актива, если есть пополненный пул и была "
        u"сделка за последние 24 часа."
    ),
    "pool_detail.map_connects_fallback": (
        u"Линия соединяет два актива, если существует пополненный пул. "
        u"Торговая активность за 24ч не подтверждена (история недоступна) — "
        u"показаны пополненные пулы."
    ),
    "pool_detail.map_min_swaps": u"(мин. %(min)s свопов)",

    # ============================================================ market_ind (3)
    # The truncated-window warning: it hides how much history is missing, so
    # it stays a short literal noun phrase rather than a softener.
    "market_ind.count_capped": u"окно обрезано",
    "market_ind.count_note": u"%(count)s × %(bucket)s свечей",
    "market_ind.count_partial": (
        u"%(actual)s из %(requested)s × %(bucket)s свечей"
    ),

    # ============================================================ market_net (1)
    "market_net.col_spark": u"7д",

    # ========================================================= createaccount (0)
    # (see the wizard step names above)

    # ============================================================== dashboard (2)
    "dashboard.tagline": (
        u"Смотрите рынки бесплатно — создайте кошелёк, чтобы торговать."
    ),
    "dashboard.welcome": u"Торгуйте BTS ключами, которые храните у себя",

    # ==================================================================== nav (4)
    "nav.credit": u"Кредит",
    "nav.margin": u"Маржа",
    "nav.markets": u"Рынки",
    "nav.pools": u"Пулы",

    # ================================================================= news (1)
    "news.explorer_blocks_and_transactions": u"Обзор цепи",

    # ================================================================= apilab (1)
    "apilab.title": u"API-лаборатория",

    # ================================================================= eslab (2)
    "eslab.hint_donors": (
        u"Подсчёты за окно; итоги — raw целые числа: делите на точность "
        u"актива."
    ),
    "eslab.title": u"ES-лаборатория",

    # ================================================================== pools (1)
    "pools.selector_title": u"Выбор пула",

    # ================================================================ instant (3)
    # preview_balances_note is a SAFETY line: it says the balances on screen
    # were NOT checked. It must not be shortened into a reassurance.
    "instant.preview_balances_note": (
        u"Предпросмотр как %(name)s (%(id)s) — балансы не проверены. "
        u"Разблокируйте, чтобы проверить свои, до подписи."
    ),
    "instant.uc_title": u"Разблокировать для подписи",
    "instant.unlock_sign": u"Разблокировать и подписать",

    # ================================================================= htlc (2)
    "htlc.list_sub": (
        u"Заблокируйте средства под хеш — получатель погасит секретом до "
        u"истечения, иначе вам вернут средства. Читает кто угодно; пароль "
        u"спрашивается только при подписании."
    ),
    "htlc.uc_title": u"Разблокировать для подписи",

    # ================================================================= confirm (1)
    # A signing-row TERM, printed dual-line beside its value. «Мемо» is what
    # transfer.memo_label and debit.memo_field already call it; «заметка»
    # (proposal.memo) is the wallet's word for a private note and would read
    # as a different field next to an encrypted payload.
    "confirm.memo": u"Мемо",

    # =============================================================== gateway (3)
    # intro_a ends in a space because it is concatenated with intro_b; the
    # "this page sends nothing" clause is the safety half and is kept even
    # though it makes the sentence longer.
    "gateway.intro_a": (
        u"Отправляйте внешние монеты на показанный адрес. Эта страница "
        u"ничего не отправляет. "
    ),
    "gateway.intro_b": (
        u"Выводы заканчиваются в Переводе с живым предпросмотром комиссии."
    ),
    "gateway.raw_prefix": u"сырой: ",

    # ================================================================ compat (1)
    "compat.insecure_hint": (
        u"Этот адрес — не безопасный контекст, поэтому браузер не даёт доступ "
        u"к WebCrypto. Браузер актуален — отдайте по https или через "
        u"localhost либо откройте файл напрямую."
    ),

    # ================================================================ common (2)
    "common.page_n": u"Страница %(n)s",
    "common.unknown_asset": u"Неизвестный актив.",

    # =============================================================== txbuilder (1)
    "txbuilder.link_proposals": u"Предложения",
}

# Keys whose Russian value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from RU. Each one is asserted
# to still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift. Four groups:
#
#   * DATA / sentinels - nothing to translate. settings.* are the pinned
#     network/theme/dash/placeholder tokens (G3); the two graph edge cards and
#     the price edge are placeholder pairs joined by «·» and «–» (the same call
#     chunk-A made for market_net.edge_card and B1 for pool_net.edge_card);
#     transfer.bad_asset_shape and ticket.airdrop_example_ph are machine
#     sentinels an error handler compares against, and instant.bad_asset_
#     shape_for_fee_asset already keeps the first one in Latin inside Russian
#     prose, proving the split is pre-existing and deliberate.
#   * ACRONYMS that name an on-chain concept or a formula - HTLC, NFT, PMA,
#     UIA, MCR, SMA, EMA, PSAR, BB, PnL - matching the already-translated
#     asset.nft_title_field "Заголовок NFT", asset.mcr_field "MCR, %" and
#     market.ov_* neighbourhood.
#   * LABELS a Russian crypto UI spells in English - ID (vesting.balance_id,
#     debit.perm_id_field), URL, TxBuilder, i18n (the chip's own text), Fill or
#     Kill (es translated it, but es also translated DEX-agnostic order-type
#     jargon everywhere else; Russian exchanges write FOK in Latin).
#   * Example payloads - account_net.seeds_placeholder (a comma list of real
#     ids/names), xrate.token_placeholder (a comma list of tickers).
#
# Two sections end up entirely untranslated and that is correct, not an
# oversight: settings (nine pinned tokens) and pool_net (two data cards B1
# already ruled on).
KEPT_ENGLISH = {
    # ---- settings: pinned ids, theme ids and sentinels (G3)
    "settings.custom_placeholder": u"wss://…",
    "settings.dash": u"—",
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.pending": u"…",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",

    # ---- data glue: placeholder pairs joined by «·» / «–», nothing to say
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",

    # ---- machine sentinels an error handler compares against
    "barter.paid_by_suffix": u"): ",
    "transfer.bad_asset_shape": u"bad-asset-shape",
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",

    # ---- empty-state dashes (the wallet's own «—» for "no value")
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    "market.stat_empty": u"—",

    # ---- acronyms naming an on-chain concept or a formula
    "account_net.class_htlc": u"HTLC",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    "htlc.title": u"HTLC",
    "instant.fill_or_kill": u"Fill or Kill",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "prediction.pnl": u"PnL",
    "trade.fok_label": u"Fill or kill ",
    "trade.row_fok": u"Fill or Kill",

    # ---- labels a Russian crypto UI spells in English
    "createworker.url": u"URL",
    "i18n.badge_chip": u"i18n",
    "misc.id": u"ID",
    "proposal.id": u"ID",
    "ticket.id": u"ID",
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "vesting.id": u"ID",
    "vote.url": u"URL",

    # ---- example payloads a user is meant to overwrite
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
}


if __name__ == "__main__":
    sys.exit(main())