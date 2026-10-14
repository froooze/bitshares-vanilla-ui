#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/ru.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound: грант-предложение (sing) / грант-предложения (plur) / получатели грантов (recipients). Pay: выплата/оплата attested; budget бюджет attested.
Pay keeps attested pay word; budget/funding keep attested words; recipients use beneficiary word.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_ru.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

WORKER_RE = re.compile(r"работник", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Создание работника",
        "Создание грант-предложения",
    ),
    "account.sum_worker_create": (
        "Создан работник «%(name)s»",
        "Создано грант-предложение «%(name)s»",
    ),
    "createworker.confirm_worker_op_34": (
        "Подтвердите работника (op %(op)s)",
        "Подтвердите грант-предложение (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "Не удалось показать предпросмотр работника.",
        "Не удалось показать предпросмотр грант-предложения.",
    ),
    "createworker.create_worker": (
        "Создать работника",
        "Создать грант-предложение",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Черновик работника (op %(op)s). Предпросмотр живой; проверка называет живую комиссию, затем Подписать и отправить транслирует op %(op)s напрямую — работники создаются прямой операцией, а не предложением.",
        "Черновик грант-предложения (op %(op)s). Предпросмотр живой; проверка называет живую комиссию, затем Подписать и отправить транслирует op %(op)s напрямую — грант-предложения создаются прямой операцией, а не предложением.",
    ),
    "createworker.enter_a_worker_name": (
        "Введите имя работника.",
        "Введите имя грант-предложения.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "Владелец платит комиссию и получает выплату работника — используйте подконтрольный аккаунт с пожизненным членством.",
        "Владелец платит комиссию и получает выплату грант-предложения — используйте подконтрольный аккаунт с пожизненным членством.",
    ),
    "createworker.preview_worker": (
        "Предпросмотр работника",
        "Предпросмотр грант-предложения",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Публикация работника требует аккаунта с пожизненным членством — базовые аккаунты не могут оплатить эту комиссию. Владелец ниже должен уже быть улучшен.",
        "Публикация грант-предложения требует аккаунта с пожизненным членством — базовые аккаунты не могут оплатить эту комиссию. Владелец ниже должен уже быть улучшен.",
    ),
    "createworker.reading_existing_workers": (
        "Чтение существующих работников…",
        "Чтение существующих грант-предложений…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Бэкенд работника отсутствует: не удалось загрузить js/account.js или js/format.js.",
        "Бэкенд грант-предложения отсутствует: не удалось загрузить js/account.js или js/format.js.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Бэкенд работника отсутствует: не удалось загрузить js/asset-ops.js.",
        "Бэкенд грант-предложения отсутствует: не удалось загрузить js/asset-ops.js.",
    ),
    "createworker.worker_name": (
        "Имя работника ",
        "Имя грант-предложения ",
    ),
    "createworker.worker_preview_op_34": (
        "Предпросмотр работника (op %(op)s)",
        "Предпросмотр грант-предложения (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Работники",
        "Грант-предложения",
    ),
    "help.topic_voting_text": (
        "Голосуйте за заверителей, комитет, работников — или передайте голосование прокси.",
        "Голосуйте за заверителей, комитет, грант-предложения — или передайте голосование прокси.",
    ),
    "menu.d_voting": (
        "Заверители, комитет, работники и прокси.",
        "Заверители, комитет, грант-предложения и прокси.",
    ),
    "menu.p_worker": (
        "Создать работника",
        "Создать грант-предложение",
    ),
    "news.voting_witnesses_committee_workers": (
        "Голосование — заверители, комитет, работники",
        "Голосование — заверители, комитет, грант-предложения",
    ),
    "seo.desc_voting": (
        "Голосование за заверителей, членов комитета и работников BitShares. Каждый бюллетень подписывается локально на вашем устройстве.",
        "Голосование за заверителей, членов комитета и грант-предложений BitShares. Каждый бюллетень подписывается локально на вашем устройстве.",
    ),
    "vote.ballot_intro": (
        "Ваш стейк выбирает заверителей и комитет и финансирует работников — все числа и доли ниже читаются из живой цепи.",
        "Ваш стейк выбирает заверителей и комитет и финансирует грант-предложения — все числа и доли ниже читаются из живой цепи.",
    ),
    "vote.empty_hint": (
        " Записи появятся, когда чейн их несёт — работники предлагаются из #/create-worker.",
        " Записи появятся, когда чейн их несёт — грант-предложения предлагаются из #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Финансирование работников недоступно (",
        "Финансирование грант-предложений недоступно (",
    ),
    "vote.hide_legacy_label": (
        " Скрыть устаревшие предложения (всегда вкл — просроченные работники исключаются при загрузке)",
        " Скрыть устаревшие предложения (всегда вкл — просроченные грант-предложения исключаются при загрузке)",
    ),
    "vote.hide_legacy_title": (
        "Списки работников — из get_all_workers(false); просроченные строки никогда не приходят.",
        "Списки грант-предложений — из get_all_workers(false); просроченные строки никогда не приходят.",
    ),
    "vote.no_workers": (
        "Работники не найдены. В тестнетах их часто нет — это нормально, не ошибка.",
        "Грант-предложения не найдены. В тестнетах их часто нет — это нормально, не ошибка.",
    ),
    "vote.tab_workers": (
        "Работники (",
        "Грант-предложения (",
    ),
    "vote.worker_budget": (
        "Бюджет работников: —",
        "Бюджет грант-предложений: —",
    ),
    "vote.worker_budget_loading": (
        "Бюджет работников: загрузка…",
        "Бюджет грант-предложений: загрузка…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("работники выполняют оплаченные проекты", "получатели грантов выполняют оплаченные проекты", 1,),
    ],
    "help.topic_sitemap_body": [
        ("- [Создать работника](#/create-worker)", "- [Создать грант-предложение](#/create-worker)", 1,),
    ],
    "help.topic_tickets_body": [
        ("голоса за заверителей, комитет и работников через обычный бюллетень", "голоса за заверителей, комитет и грант-предложения через обычный бюллетень", 1,),
    ],
    "help.topic_vesting_body": [
        ("оплата работников, реферальные награды", "оплата грант-предложений, реферальные награды", 1,),
    ],
    "help.topic_voting_body": [
        ("и какие проекты работников получат оплату.", "и какие проекты грант-предложений получат оплату.", 1,),
        ("или работников. Вы можете снять прокси", "или грант-предложения. Вы можете снять прокси", 1,),
        ("# Работники и бюджет", "# Грант-предложения и бюджет", 1,),
        ("Работники — оплачиваемые предложения", "Грант-предложения — оплачиваемые предложения", 1,),
        ("возвратного работника,", "возвратного грант-предложения,", 1,),
        ("в статье Работники.", "в статье Грант-предложения.", 1,),
    ],
    "help.topic_workers_body": [
        ("Работники — предложения сделать", "Грант-предложения — предложения сделать", 1,),
        ("Предложенные работники собирают голоса.", "Предложенные грант-предложения собирают голоса.", 1,),
        ("возвратного работника, оно становится", "возвратного грант-предложения, оно становится", 1,),
        ("Все работники делят", "Все грант-предложения делят", 1,),
        ("вышестоящие работники уже", "вышестоящие грант-предложения уже", 1,),
    ],
}

def digd(d, key):
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
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print(f"FAIL: {P} does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WORKER_RE.search(old):
            problems.append("ABORT %s: script old has no worker word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip) and key != "help.topic_glossary_body":
                # glossary old_snip contains worker word by definition; allow generic check
                pass
            # For glossary, old_snip must contain worker word; enforce
            if key == "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            if key != "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = digd(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    after_vals = flatten(d)
    if "get_all_workers" not in after_vals["vote.hide_legacy_title"]:
        print("FAIL: get_all_workers token lost")
        return 1
    for k in ("createworker.worker_backend_missing_js_account_js_or_js_fo",
              "createworker.worker_backend_missing_js_asset_ops_js_failed"):
        if "js/" not in after_vals[k]:
            print("FAIL: file path lost in %s" % k)
            return 1
    for k in ("help.topic_sitemap_body", "vote.empty_hint"):
        if "#/create-worker" not in after_vals[k]:
            print("FAIL: route hash lost in %s" % k)
            return 1

    if set(after_vals) != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print(f"OK {P}: renamed")
    else:
        print(f"OK {P}: dry run green")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
