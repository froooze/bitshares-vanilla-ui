#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in de.json (REPLACE, not insert).

Owns: the de Same-T -> Flash-Loan value replacements only.
Consumes: vanilla/locales/de.json (ordered dict).
Side effects: overwrites de.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-latin5 (de/es/fr/it/pt batch).

Each replacement asserts the CURRENT value contains the Same-T/Same-asset
brand (any case) before replacing, and aborts loudly otherwise. No
insert-overwrite: a missing brand means the file changed under us.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT de: {msg}", file=sys.stderr)
    sys.exit(1)


def need_brand(cur, label):
    if not isinstance(cur, str) or not BRAND_RE.search(cur):
        abort(f"{label} current value lacks Same-T/Same-asset brand: {cur!r}")


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    # (section, key, new_value) — titles / ops / misc. All currents carry brand.
    reps = [
        ("samet", "title", "Flash-Loan-Fonds"),
        ("samet", "same_t_funds", "Flash-Loan-Fonds"),
        ("menu", "p_samet", "Flash-Loan-Fonds"),
        ("help", "topic_samet_title", "Flash-Loan-Fonds"),
        ("account", "op_samet_borrow", "Flash-Loan-Leihen"),
        ("account", "op_samet_create", "Flash-Loan-Fonds-Erstellung"),
        ("account", "op_samet_delete", "Flash-Loan-Fonds-Löschung"),
        ("account", "op_samet_repay", "Flash-Loan-Rückzahlung"),
        ("account", "op_samet_update", "Flash-Loan-Fonds-Update"),
        ("credit", "unknown_same_t_fund", "Unbekannter Flash-Loan-Fonds."),
        ("help", "topic_samet_text",
         "Gepoolte Flash-Loan-Fonds (gleiches Asset) mit Ziehungen und Rückzahlungen."),
        ("menu", "d_samet", "Gebündelte Flash-Loan-Fonds (gleiches Asset) und Ziehungen."),
        ("samet", "create_hint",
         " Erstellen Sie einen über das Erstellungsformular unten — eigene Flash-Loan-Fonds werden hier aufgelistet."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Flash-Loans: Leihen und Zurückzahlen im gleichen Asset erfolgen in EINER Transaktion [67 Leihen + 68 Zurückzahlen] — die Chain lehnt ein einzelnes Leihen ab. Sätze sind Prozent mit Nenner 1.000.000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Flash-Loan-Fonds nicht verfügbar: credit-ui.js konnte nicht geladen werden."),
        ("account", "sum_samet_create",
         "Hat einen Flash-Loan-Fonds mit %(amount)s erstellt"),
        ("account", "sum_samet_delete",
         "Hat den Flash-Loan-Fonds %(fund)s gelöscht"),
        ("account", "sum_samet_update",
         "Hat den Flash-Loan-Fonds %(fund)s aktualisiert"),
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

    # help.topic_samet_body: replace FIRST content line only, keep rest.
    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Flash-Loan-Fonds (Same-T) poolen ein Asset vieler Lieferanten. "
                 + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    # help.topic_sitemap_body: replace ONLY the samet link label.
    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Same-T-Fonds](#/samet)"
    new_link = "[Flash-Loan-Fonds](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    if "#/samet" not in new_link:
        abort("sitemap new link lost #/samet hash")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("de: Same-T -> Flash-Loan replacements applied.")


if __name__ == "__main__":
    main()
