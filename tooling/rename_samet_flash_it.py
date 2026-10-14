#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in it.json (REPLACE, not insert).

Owns: the it Same-T -> prestito flash value replacements only.
Consumes: vanilla/locales/it.json (ordered dict).
Side effects: overwrites it.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-latin5 (de/es/fr/it/pt batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T/Same-asset brand
(SameT without hyphen in the three sum_* lines counts as brand); the two
pooled-funds blurbs were already localized as "stesso asset" with no
English brand, so those two assert the known localized old phrase instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT it: {msg}", file=sys.stderr)
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
        ("samet", "title", "Fondi di prestiti flash"),
        ("samet", "same_t_funds", "Fondi di prestiti flash"),
        ("menu", "p_samet", "Fondi di prestiti flash"),
        ("help", "topic_samet_title", "Fondi di prestiti flash"),
        ("account", "op_samet_borrow", "Prestito flash"),
        ("account", "op_samet_create", "Creazione fondo di prestito flash"),
        ("account", "op_samet_delete", "Eliminazione fondo di prestito flash"),
        ("account", "op_samet_repay", "Rimborso di prestito flash"),
        ("account", "op_samet_update", "Aggiornamento fondo di prestito flash"),
        ("credit", "unknown_same_t_fund", "Fondo di prestito flash sconosciuto."),
        ("samet", "create_hint",
         " Ne crei uno dal modulo crea qui sotto — i fondi di prestiti flash posseduti sono elencati qui."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Prestiti flash: prestito e rimborso nello stesso asset avvengono in UNA transazione [67 prestito + 68 rimborso] — la chain rifiuta un prestito isolato. I tassi sono percentuali a denominatore 1.000.000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Fondi di prestiti flash non disponibili: credit-ui.js non caricato."),
        ("account", "sum_samet_create", "Fondo di prestito flash creato con %(amount)s"),
        ("account", "sum_samet_delete", "Fondo di prestito flash %(fund)s eliminato"),
        ("account", "sum_samet_update", "Fondo di prestito flash %(fund)s aggiornato"),
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
    need_old(cur, "stesso asset", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Fondi comuni di prestiti flash sullo stesso asset con prelievi e rimborsi.")
    cur = get("menu", "d_samet")
    need_old(cur, "stesso asset", "menu.d_samet")
    d["menu"]["d_samet"] = "Fondi comuni (pool) di prestiti flash sullo stesso asset ed estrazioni."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("I fondi di prestiti flash (Same-T) raccolgono un asset da molti "
                 "fornitori. " + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Fondi Same-T](#/samet)"
    new_link = "[Fondi di prestiti flash](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("it: Same-T -> prestito flash replacements applied.")


if __name__ == "__main__":
    main()
