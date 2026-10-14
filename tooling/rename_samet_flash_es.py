#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in es.json (REPLACE, not insert).

Owns: the es Same-T -> préstamo flash value replacements only.
Consumes: vanilla/locales/es.json (ordered dict).
Side effects: overwrites es.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-latin5 (de/es/fr/it/pt batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T/Same-asset brand;
the two pooled-funds blurbs (menu.d_samet, help.topic_samet_text) were
already localized as "mismo activo" with no English brand, so those two
assert the known localized old phrase instead (still a replace-guard, not
an insert-overwrite).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT es: {msg}", file=sys.stderr)
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
        ("samet", "title", "Fondos de préstamos flash"),
        ("samet", "same_t_funds", "Fondos de préstamos flash"),
        ("menu", "p_samet", "Fondos de préstamos flash"),
        ("help", "topic_samet_title", "Fondos de préstamos flash"),
        ("account", "op_samet_borrow", "Préstamo flash"),
        ("account", "op_samet_create", "Creación de fondo de préstamo flash"),
        ("account", "op_samet_delete", "Eliminación de fondo de préstamo flash"),
        ("account", "op_samet_repay", "Devolución de préstamo flash"),
        ("account", "op_samet_update", "Actualización de fondo de préstamo flash"),
        ("credit", "unknown_same_t_fund", "Fondo de préstamo flash desconocido."),
        ("samet", "create_hint",
         " Crea uno desde el formulario de creación de abajo — tus fondos de préstamos flash aparecen aquí."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Préstamos flash: el préstamo y la devolución ocurren en UNA transacción [67 préstamo + 68 devolución] — la cadena rechaza un préstamo aislado. Las tasas son porcentajes con denom 1.000.000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Fondos de préstamos flash no disponibles: no se pudo cargar credit-ui.js."),
        ("account", "sum_samet_create",
         "Creó el fondo de préstamo flash con %(amount)s"),
        ("account", "sum_samet_delete",
         "Eliminó el fondo de préstamo flash %(fund)s"),
        ("account", "sum_samet_update",
         "Actualizó el fondo de préstamo flash %(fund)s"),
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

    # Blurbs already localized (no English brand): guard on known old phrase.
    cur = get("help", "topic_samet_text")
    need_old(cur, "mismo activo", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Fondos agrupados de préstamos flash con disposiciones y devoluciones.")
    cur = get("menu", "d_samet")
    need_old(cur, "mismo activo", "menu.d_samet")
    d["menu"]["d_samet"] = "Fondos agrupados de préstamos flash y disposiciones."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Los fondos de préstamos flash (Same-T) mancomunan un activo de muchos "
                 "proveedores. " + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Fondos Same-T](#/samet)"
    new_link = "[Fondos de préstamos flash](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("es: Same-T -> préstamo flash replacements applied.")


if __name__ == "__main__":
    main()
