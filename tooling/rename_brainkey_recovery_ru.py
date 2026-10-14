#!/usr/bin/env python3
"""Rename brainkey -> "фраза восстановления" in vanilla/locales/ru.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys: 36 FULL +
6 snippet bodies). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no брейнке word.
  * seo.desc_help — no брейнке word ("восстановлению" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s; sitemap hrefs stay
    byte-identical (hash kept).

Compound (per brief): "фраза восстановления" (fem.), built from this locale's
OWN attested words: "восстанов-" is attested in `seo.desc_help`
("восстановлению") and `createaccount.back_up_this_brainkey_it_is_the_only_way_to_r`
("восстановить аккаунт"); "фраза" is attested in `help.topic_backups_body`
("одна фраза сама по себе") and `help.topic_password_text` ("новой фразой" —
the passphrase sense, never confused here). "фраза восстановления" is the
plainest standard Russian crypto term (сид-фраза rejected as jargon);
"ключ-в-голове" calque (already forbidden by the glossary) rejected.
Masculine брейнкей -> feminine фраза throughout: этот->эту, свой->своя/свою,
новый->новая/новую, свежий->свежая, пополненный->пополненную,
словесного->словесной, этим->этой, одного->одной, того же->той же,
он/его/него->она/её/неё, Ваш/ваш->Ваша/ваша, короткий->короткая,
потерянный->потерянная. "запишите/введите/сохраните" imperatives stay
imperative; "Сгенерировать новую ..." stays an action label; the causal
"— это единственный способ восстановить аккаунт" link is intact; placeholder
examples stay short (слова kept); the backup-warning ("Любой, у кого она
есть, может потратить ваши средства") stays blunt.

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a брейнке-family
     word ([Бб]рейнке catches брейнкей/брейнкея/брейнкеем/брейнкеи), else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint keeps the route hash; the two excluded
     keys carry no брейнке.

Usage: python3 tooling/rename_brainkey_recovery_ru.py [--apply]
Dry run (asserts only) by default; --apply writes ru.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

BRAINKEY_RE = re.compile(r"[Бб]рейнке")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "about.s1_body": (
        "Аккаунты живут в зашифрованном хранилище на вашем устройстве, и каждая транзакция подписывается локально до отправки. Ноды, к которым вы подключаетесь, никогда не видят ваших секретов — поэтому резервные копии только ваши: потеряете брейнкей, и средства никто не восстановит.",
        "Аккаунты живут в зашифрованном хранилище на вашем устройстве, и каждая транзакция подписывается локально до отправки. Ноды, к которым вы подключаетесь, никогда не видят ваших секретов — поэтому резервные копии только ваши: потеряете фразу восстановления, и средства никто не восстановит.",
    ),
    "account.no_account_yet": (
        "Кошелёк разблокирован, но его активный ключ пока не управляет ни одним ончейн-аккаунтом. Зарегистрируйте один или импортируйте пополненный брейнкей.",
        "Кошелёк разблокирован, но его активный ключ пока не управляет ни одним ончейн-аккаунтом. Зарегистрируйте один или импортируйте пополненную фразу восстановления.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Локальный кошелёк создаёт брейнкей на этом устройстве и выводит из него owner-, active- и memo-ключи. Ключи никогда не покидают устройство; файл кошелька зашифрован вашим паролем.",
        "Локальный кошелёк создаёт фразу восстановления на этом устройстве и выводит из неё owner-, active- и memo-ключи. Ключи никогда не покидают устройство; файл кошелька зашифрован вашим паролем.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Резервная копия: без файла — брейнкей нового аккаунта показывается один раз при создании",
        "Резервная копия: без файла — фраза восстановления нового аккаунта показывается один раз при создании",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Резервная копия: да — запишите брейнкей",
        "Резервная копия: да — запишите фразу восстановления",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Лучшая безопасность — остаётся в этом браузере. Перенесите его с резервной копией брейнкея.",
        "Лучшая безопасность — остаётся в этом браузере. Перенесите его с резервной копией фразы восстановления.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Импорт существующего аккаунта (брейнкей)",
        "Импорт существующего аккаунта (фраза восстановления)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Для нового аккаунта генерируется свежий брейнкей. Запишите его — из него выводятся owner-, active- и memo-ключи.",
        "Для нового аккаунта генерируется свежая фраза восстановления. Запишите её — из неё выводятся owner-, active- и memo-ключи.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Сохраните этот брейнкей — это единственный способ восстановить аккаунт.",
        "Сохраните эту фразу восстановления — это единственный способ восстановить аккаунт.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Брейнкей (сохраните его)",
        "Фраза восстановления (сохраните её)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "Не удалось сгенерировать брейнкей.",
        "Не удалось сгенерировать фразу восстановления.",
    ),
    "createaccount.err_brainkey_wait": (
        "Сначала дождитесь генерации брейнкея.",
        "Сначала дождитесь генерации фразы восстановления.",
    ),
    "createaccount.generate_new_brainkey": (
        "Сгенерировать новый брейнкей",
        "Сгенерировать новую фразу восстановления",
    ),
    "createaccount.generating_brainkey": (
        "Генерация брейнкея…",
        "Генерация фразы восстановления…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Сохранить кошелёк с этим брейнкеем",
        "Сохранить кошелёк с этой фразой восстановления",
    ),
    "createaccount.step_brainkey": (
        "Брейнкей",
        "Фраза восстановления",
    ),
    "help.topic_backups_text": (
        "Ваш брейнкей И ЕСТЬ бэкап — запишите его. Посмотреть можно в любой момент в менеджере кошелька.",
        "Ваша фраза восстановления И ЕСТЬ бэкап — запишите её. Посмотреть можно в любой момент в менеджере кошелька.",
    ),
    "help.topic_wallets_text": (
        "Кошелёк хранит ваш брейнкей и выводит ключи owner, active и memo. Управление — в разделе Кошелёк.",
        "Кошелёк хранит вашу фразу восстановления и выводит ключи owner, active и memo. Управление — в разделе Кошелёк.",
    ),
    "menu.d_brainkey": (
        "Новый кошелёк из словесного брейнкея.",
        "Новый кошелёк из словесной фразы восстановления.",
    ),
    "menu.d_registration": (
        "Облачная, локальная регистрация и через брейнкей.",
        "Облачная, локальная регистрация и через фразу восстановления.",
    ),
    "menu.p_brainkey": (
        "Создать кошелёк (брейнкей)",
        "Создать кошелёк (фраза восстановления)",
    ),
    "seo.desc_login": (
        "Разблокировка локального кошелька BitShares — пароль, брейнкей или импортированные ключи. Ключи не покидают это устройство.",
        "Разблокировка локального кошелька BitShares — пароль, фраза восстановления или импортированные ключи. Ключи не покидают это устройство.",
    ),
    "splash.step2_d": (
        "Брейнкей создаётся на этом устройстве. Запишите его на бумаге.",
        "Фраза восстановления создаётся на этом устройстве. Запишите её на бумаге.",
    ),
    "wallet.brainkey": (
        "Брейнкей",
        "Фраза восстановления",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Импорт брейнкея (форма ниже на этой странице)",
        " · Импорт фразы восстановления (форма ниже на этой странице)",
    ),
    "wallet.brainkey_words_placeholder": (
        "слова брейнкея…",
        "слова фразы восстановления…",
    ),
    "wallet.console_single_key_note": (
        "Кошелёк с одним ключом: .bin-файлы резервных копий и голые приватные ключи (WIF) не поддерживаются — только импорт брейнкея.",
        "Кошелёк с одним ключом: .bin-файлы резервных копий и голые приватные ключи (WIF) не поддерживаются — только импорт фразы восстановления.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Свой брейнкей слишком короткий: минимум 50 символов после обрезки.",
        "Своя фраза восстановления слишком короткая: минимум 50 символов после обрезки.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Введите свой брейнкей. Он сверяется с цепочкой перед сохранением.",
        "Введите свою фразу восстановления. Она сверяется с цепочкой перед сохранением.",
    ),
    "wallet.generate_new_brainkey": (
        "Сгенерировать новый брейнкей",
        "Сгенерировать новую фразу восстановления",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "Есть вместо этого .bin-файл резервной копии или голые приватные ключи? Этот кошелёк импортирует только брейнкеи — расшифровка .bin и импорт WIF не поддерживаются. Ничего никуда не загружается.",
        "Есть вместо этого .bin-файл резервной копии или голые приватные ключи? Этот кошелёк импортирует только фразы восстановления — расшифровка .bin и импорт WIF не поддерживаются. Ничего никуда не загружается.",
    ),
    "wallet.s4": (
        "Создать кошелёк (брейнкей)",
        "Создать кошелёк (фраза восстановления)",
    ),
    "wallet.s6": (
        "Подтвердите, что сначала записали брейнкей.",
        "Подтвердите, что сначала записали фразу восстановления.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "введите свои слова брейнкея…",
        "введите свои слова фразы восстановления…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Использовать свой брейнкей",
        "Использовать свою фразу восстановления",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Запишите свой брейнкей и храните в безопасности. Любой, у кого он есть, может потратить ваши средства.",
        "Запишите свою фразу восстановления и храните в безопасности. Любой, у кого она есть, может потратить ваши средства.",
    ),
}

SNIPPETS = {
    "help.topic_backups_body": [
        (
            "ваш брейнкей И ЕСТЬ бэкап",
            "ваша фраза восстановления И ЕСТЬ бэкап",
            1,
        ),
        (
            "# Ваш брейнкей и есть бэкап",
            "# Ваша фраза восстановления и есть бэкап",
            1,
        ),
        (
            "из одного брейнкея — строки слов",
            "из одной фразы восстановления — строки слов",
            1,
        ),
        (
            "Записав брейнкей, вы сохраняете",
            "Записав фразу восстановления, вы сохраняете",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "потеряете брейнкей или пароль",
            "потеряете фразу восстановления или пароль",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "потерянный брейнкей означают",
            "потерянная фраза восстановления означают",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— брейнкей И ЕСТЬ бэкап.",
            "— фраза восстановления И ЕСТЬ бэкап.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Создать кошелёк (брейнкей)](#/create-wallet-brainkey)",
            "- [Создать кошелёк (фраза восстановления)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "с того же брейнкея —",
            "с той же фразы восстановления —",
            1,
        ),
        (
            "не перенесли брейнкей и не импортировали его",
            "не перенесли фразу восстановления и не импортировали её",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Создайте его (#/create-wallet-brainkey) или импортируйте существующий аккаунт (#/existing-account) — ссылки ниже."


def dig(d, key):
    node = d
    for seg in key.split("."):
        node = node[seg]
    return node


def set_dig(d, key, value):
    segs = key.split(".")
    node = d
    for seg in segs[:-1]:
        node = node[seg]
    node[segs[-1]] = value


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def main():
    apply = "--apply" in sys.argv
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not BRAINKEY_RE.search(cur):
            problems.append("ABORT %s: current value has no brainkey-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not BRAINKEY_RE.search(old):
            problems.append("ABORT %s: script's old string has no brainkey word (script bug)" % key)
            continue
        if BRAINKEY_RE.search(HREF_RE.sub("", new)):
            problems.append("ABORT %s: script's new string still has a brainkey word outside a hash (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not BRAINKEY_RE.search(cur):
            problems.append("ABORT %s: current value has no brainkey-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not BRAINKEY_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no brainkey word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))
            if BRAINKEY_RE.search(HREF_RE.sub("", new_snip)):
                problems.append("ABORT %s: snippet new still has brainkey word outside a route hash: %r" % (key, new_snip))

    try:
        hint = dig(d, "wallet.console_hint")
        if hint != CONSOLE_HINT_OLD:
            problems.append("ABORT wallet.console_hint moved (must keep #/create-wallet-brainkey): %r" % hint)
        if "#/create-wallet-brainkey" not in hint:
            problems.append("ABORT wallet.console_hint lost its route hash")
    except KeyError:
        problems.append("missing key wallet.console_hint")
    for key in ("help.topic_translation-limitations_body", "seo.desc_help"):
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if BRAINKEY_RE.search(cur):
            problems.append("ABORT %s: unexpectedly carries a brainkey word" % key)

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    after_keys = set(flatten(d))
    if after_keys != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    after_vals = flatten(d)
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print("OK ru: %d full + %d snippet keys renamed to фраза восстановления" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ru: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
