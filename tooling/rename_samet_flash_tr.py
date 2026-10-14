#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in tr.json (REPLACE, not insert).

Owns: the tr Same-T -> flash kredi value replacements only.
Consumes: vanilla/locales/tr.json (ordered dict).
Side effects: overwrites tr.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-ru-tr-hi.

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T/Same-asset brand;
the two pooled-funds blurbs were already localized as aynı-varlık with no
English brand, so those two assert the known localized old phrase instead.
Formal siz register; vowel harmony + case stacking preserved; no comparison
inverted.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "tr.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT tr: {msg}", file=sys.stderr)
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
        ("samet", "title", "Flash kredi fonları"),
        ("samet", "same_t_funds", "Flash kredi fonları"),
        ("menu", "p_samet", "Flash kredi fonları"),
        ("help", "topic_samet_title", "Flash kredi fonları"),
        ("account", "op_samet_borrow", "Flash kredi borçlanma"),
        ("account", "op_samet_create", "Flash kredi fon oluşturma"),
        ("account", "op_samet_delete", "Flash kredi fon silme"),
        ("account", "op_samet_repay", "Flash kredi geri ödeme"),
        ("account", "op_samet_update", "Flash kredi fon güncelleme"),
        ("credit", "unknown_same_t_fund", "Bilinmeyen flash kredi fonu."),
        ("samet", "create_hint",
         " Aşağıdaki oluşturma formundan oluşturun — sahip olduğunuz flash kredi fonları burada listelenir."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Flash krediler: borçlanma ve geri ödeme TEK işlemde olur [67 borçlanma + 68 geri ödeme] — zincir tek başına borçlanmayı reddeder. Oranlar paydası 1.000.000 olan yüzdedir."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Flash kredi fonları kullanılamıyor: credit-ui.js yüklenemedi."),
        ("account", "sum_samet_create",
         "%(amount)s tutarında flash kredi fon oluşturuldu"),
        ("account", "sum_samet_delete",
         "Flash kredi fon %(fund)s silindi"),
        ("account", "sum_samet_update",
         "Flash kredi fon %(fund)s güncellendi"),
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
    need_old(cur, "aynı varlık", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Çekim ve geri ödemeli havuzlu flash kredi fonları.")
    cur = get("menu", "d_samet")
    need_old(cur, "aynı-varlık", "menu.d_samet")
    d["menu"]["d_samet"] = "Havuzlu flash kredi fonları ve çekimler."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Flash kredi fonları (Same-T) birçok tedarikçiden tek "
                 "varlığı havuzlar. " + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Same-T Fonları](#/samet)"
    new_link = "[Flash kredi fonları](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    if "#/samet" not in new_link:
        abort("sitemap new link lost #/samet hash")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("tr: Same-T -> flash kredi replacements applied.")


if __name__ == "__main__":
    main()
