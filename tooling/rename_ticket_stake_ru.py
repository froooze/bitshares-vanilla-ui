#!/usr/bin/env python3
"""Rename vote-locked "тикет" -> "голосовой стейк" in vanilla/locales/ru.json.

Compound (per brief): sing "голосовой стейк", plur "голосовые стейки".
Vote half "голосовой" is verbatim from menu.d_tickets ("Стейк с голосовой
блокировкой"); stake half "стейк" verbatim from vote.ballot_intro
("Ваш стейк"), pool.confirm_stake ("Подтвердите стейк"), menu.d_tickets.
Both words decline (masc. adj + masc. noun): голосового стейка (gen),
голосовых стейков (gen plur), etc. — each key below carries the case its
syntax needs. Do NOT reuse the ballot word бюллетень (different concept).

Bare "стейк/стейки" where the sentence already says vote: title + body
line 1 keep their "vote-локом" and take bare стейки.

Keys unchanged. Placeholders byte-identical. Route "#/tickets" unchanged.
No event-admission sense in ru.json (assets-uia uses "билеты на события",
a different root — asserted intact, never rewritten).

Gates G1-G5: same as rename_ticket_stake_de.py.
Usage: python3 tooling/rename_ticket_stake_ru.py [--apply]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

TICKET_RE = re.compile("[Тт]икет")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_ticket_create": (
        "Создание тикета",
        "Создание голосового стейка",
    ),
    "account.op_ticket_update": (
        "Обновление тикета",
        "Обновление голосового стейка",
    ),
    "account.sum_ticket_create": (
        "Тикет %(amount)s создан",
        "Голосовой стейк %(amount)s создан",
    ),
    "account.sum_ticket_update": (
        "Тикет %(ticket)s обновлён",
        "Голосовой стейк %(ticket)s обновлён",
    ),
    "help.topic_tickets_title": (
        "Тикеты с vote-локом",
        "Стейки с vote-локом",
    ),
    "menu.p_tickets": (
        "Тикеты",
        "Голосовые стейки",
    ),
    "proposal.err_downgrade_unproven": (
        "Понижение тикетов не проверено — выберите текущий лок или более длинный.",
        "Понижение голосовых стейков не проверено — выберите текущий лок или более длинный.",
    ),
    "proposal.err_unknown_ticket": (
        "Неизвестный тикет.",
        "Неизвестный голосовой стейк.",
    ),
    "proposal.inner_ticket_amount_must_be_0": (
        "Сумма внутр. тикета должна быть > 0.",
        "Сумма внутр. голосового стейка должна быть > 0.",
    ),
    "proposal.op_57": (
        "создание тикета",
        "создание голосового стейка",
    ),
    "proposal.op_58": (
        "обновление тикета",
        "обновление голосового стейка",
    ),
    "proposal.ticket": (
        "Тикет",
        "Голосовой стейк",
    ),
    "proposals_ticket.title": (
        "Тикеты",
        "Голосовые стейки",
    ),
    "ticket.confirm_ticket_create_op_57": (
        "Подтвердите создание тикета (op 57)",
        "Подтвердите создание голосового стейка (op 57)",
    ),
    "ticket.confirm_ticket_update_op_58": (
        "Подтвердите изменение тикета (op 58)",
        "Подтвердите изменение голосового стейка (op 58)",
    ),
    "ticket.could_not_build_the_ticket_check_account_asse": (
        "Не удалось построить тикет (проверьте аккаунт, актив и сумму).",
        "Не удалось построить голосовой стейк (проверьте аккаунт, актив и сумму).",
    ),
    "ticket.could_not_load_tickets": (
        "Не удалось загрузить тикеты.",
        "Не удалось загрузить голосовые стейки.",
    ),
    "ticket.create_ticket": (
        "Создать тикет",
        "Создать голосовой стейк",
    ),
    "ticket.loading_my_tickets": (
        "Загрузка моих тикетов…",
        "Загрузка моих голосовых стейков…",
    ),
    "ticket.loading_tickets": (
        "Загрузка тикетов…",
        "Загрузка голосовых стейков…",
    ),
    "ticket.my_tickets": (
        "Мои тикеты",
        "Мои голосовые стейки",
    ),
    "ticket.review_ticket": (
        "Проверка тикета",
        "Проверка голосового стейка",
    ),
    "ticket.ticket": (
        "Тикет",
        "Голосовой стейк",
    ),
    "ticket.ticket_amount_must_be_0": (
        "Сумма тикета должна быть > 0.",
        "Сумма голосового стейка должна быть > 0.",
    ),
    "ticket.ticket_created_and_re_read_on_chain": (
        "Тикет создан и перечитан в цепочке.",
        "Голосовой стейк создан и перечитан в цепочке.",
    ),
    "ticket.ticket_updated_and_re_read_on_chain": (
        "Тикет обновлён и перечитан в цепочке.",
        "Голосовой стейк обновлён и перечитан в цепочке.",
    ),
    "ticket.tickets": (
        "Тикеты",
        "Голосовые стейки",
    ),
    "ticket.tickets_cannot_be_deleted_no_delete_op_exists": (
        "Тикеты нельзя удалить (операции удаления не существует) — строки выше постоянны.",
        "Голосовые стейки нельзя удалить (операции удаления не существует) — строки выше постоянны.",
    ),
    "ticket.tickets_lock_funds_for_vote_weight_there_is_n": (
        "Тикеты блокируют средства для веса голоса. Операции удаления нет, поэтому каждая строка тикета постоянна.",
        "Голосовые стейки блокируют средства для веса голоса. Операции удаления нет, поэтому каждая строка голосового стейка постоянна.",
    ),
    "tickets.title": (
        "Тикеты",
        "Голосовые стейки",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "ходы пулов, тикеты, чат.",
            "ходы пулов, голосовые стейки, чат.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Тикеты](#/tickets)",
            "- [Голосовые стейки](#/tickets)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "Тикеты с vote-локом превращают стейк плюс время в вес голоса",
            "Стейки с vote-локом превращают стейк плюс время в вес голоса",
            1,
        ),
        (
            "Создайте тикет из ликвидного стейка, пополните и заберите обратно, когда лок кончится.",
            "Создайте голосовой стейк из ликвидного стейка, пополните и заберите обратно, когда лок кончится.",
            1,
        ),
        (
            "Вес тикета питает голоса за заверителей",
            "Вес голосового стейка питает голоса за заверителей",
            1,
        ),
    ],
}


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
    raw = open(LOC, encoding="utf-8").read()
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
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder change" % key)
            continue
        if not TICKET_RE.search(old):
            problems.append("ABORT %s: script old has no ticket word" % key)
            continue
    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not TICKET_RE.search(cur):
            problems.append("ABORT %s: no ticket-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not TICKET_RE.search(old_snip):
                problems.append("ABORT %s: snippet w/o ticket: %r" % (key, old_snip))
                continue
            if cur.count(old_snip) != count:
                problems.append("ABORT %s: snippet x%d != %d: %r" % (key, cur.count(old_snip), count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change" % key)
    excl = dig(d, "help.topic_assets-uia_body")
    if "билеты на события" not in excl:
        problems.append("ABORT help.topic_assets-uia_body: event sense changed unexpectedly")
    if "тикет" in excl.lower():
        problems.append("ABORT help.topic_assets-uia_body: vote-locked word leaked into event body")
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

    if set(flatten(d)) != before_keys:
        print("FAIL: key drift")
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
        open(LOC, "w", encoding="utf-8").write(out)
        print("OK ru: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ru: dry run green (%d full + %d snippet)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
