#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in ru.json (REPLACE, not insert).

Owns: the ru Same-T -> флеш-займ value replacements only.
Consumes: vanilla/locales/ru.json (ordered dict).
Side effects: overwrites ru.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-ru-tr-hi.

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T/Same-asset brand;
the two pooled-funds blurbs were already localized with no English brand
(одноактивные / одного актива), so those two assert the known localized
old phrase instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT ru: {msg}", file=sys.stderr)
    sys.exit(1)


def need_brand(cur, label):
    if not isinstance(cur, str) or not BRAND_RE.search(cur):
        abort(f"{label} current value lacks Same-T/Same-asset brand: {cur!r}")


def need_old(cur, needle, label):
    if not isinstance(cur, str) or needle not in cur:
        abort(f"{label} current value lacks expected old phrase {needle!r}: {cur!r}")


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    reps = [
        ("samet", "title", "Фонды флеш-займов"),
        ("samet", "same_t_funds", "Фонды флеш-займов"),
        ("menu", "p_samet", "Фонды флеш-займов"),
        ("help", "topic_samet_title", "Фонды флеш-займов"),
        ("account", "op_samet_borrow", "Флеш-займ"),
        ("account", "op_samet_create", "Создание фонда флеш-займа"),
        ("account", "op_samet_delete", "Удаление фонда флеш-займа"),
        ("account", "op_samet_repay", "Возврат флеш-займа"),
        ("account", "op_samet_update", "Обновление фонда флеш-займа"),
        ("credit", "unknown_same_t_fund", "Неизвестный фонд флеш-займа."),
        ("samet", "create_hint",
         " Создайте его в форме создания ниже — собственные фонды флеш-займов появятся здесь."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Флеш-займы: заём и возврат происходят в ОДНОЙ транзакции [67 заём + 68 возврат] — цепь отклоняет одиночный заём. Ставки — проценты со знаменателем 1 000 000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Фонды флеш-займов недоступны: не удалось загрузить credit-ui.js."),
        ("account", "sum_samet_create",
         "Фонд флеш-займа создан на %(amount)s"),
        ("account", "sum_samet_delete",
         "Фонд флеш-займа %(fund)s удалён"),
        ("account", "sum_samet_update",
         "Фонд флеш-займа %(fund)s обновлён"),
    ]
    for sec, key, new in reps:
        cur = get(sec, key)
        need_brand(cur, f"{sec}.{key}")
        if "%(amount)s" in cur and "%(amount)s" not in new:
            abort(f"{sec}.{key} would drop %(amount)s placeholder")
        if "%(fund)s" in cur and "%(fund)s" not in new:
            abort(f"{sec}.{key} would drop %(fund)s placeholder")
        if key == "create_hint" and not new.startswith(" "):
            abort("create_hint lost load-bearing leading space")
        d[sec][key] = new

    cur = get("help", "topic_samet_text")
    need_old(cur, "одноактив", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Пулированные фонды флеш-займов с займами и возвратами.")
    cur = get("menu", "d_samet")
    need_old(cur, "одного актива", "menu.d_samet")
    d["menu"]["d_samet"] = "Объединённые фонды флеш-займов и займы."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Фонды флеш-займов (Same-T) собирают один актив от многих "
                 "поставщиков. " + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Same-T фонды](#/samet)"
    new_link = "[Фонды флеш-займов](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    if "#/samet" not in new_link:
        abort("sitemap new link lost #/samet hash")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("ru: Same-T -> флеш-займ replacements applied.")


if __name__ == "__main__":
    main()
