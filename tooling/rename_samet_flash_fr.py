#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in fr.json (REPLACE, not insert).

Owns: the fr Same-T -> prêt flash value replacements only.
Consumes: vanilla/locales/fr.json (ordered dict).
Side effects: overwrites fr.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-latin5 (de/es/fr/it/pt batch).

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T brand (SameT
without hyphen in the three sum_* lines counts as brand); the two
pooled-funds blurbs were already localized as "même-actif" with no English
brand, so those two assert the known localized old phrase instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT fr: {msg}", file=sys.stderr)
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
        ("samet", "title", "Fonds de prêts flash"),
        ("samet", "same_t_funds", "Fonds de prêts flash"),
        ("menu", "p_samet", "Fonds de prêts flash"),
        ("help", "topic_samet_title", "Fonds de prêts flash"),
        ("account", "op_samet_borrow", "Emprunt flash"),
        ("account", "op_samet_create", "Création de fonds de prêt flash"),
        ("account", "op_samet_delete", "Suppression de fonds de prêt flash"),
        ("account", "op_samet_repay", "Remboursement de prêt flash"),
        ("account", "op_samet_update", "Mise à jour de fonds de prêt flash"),
        ("credit", "unknown_same_t_fund", "Fonds de prêt flash inconnu."),
        ("samet", "create_hint",
         " Créez-en un depuis le formulaire de création ci-dessous — vos fonds de prêts flash s'affichent ici."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Prêts flash : emprunt et remboursement ont lieu en UNE transaction [67 emprunt + 68 remboursement] — la chaîne rejette un emprunt isolé. Les taux sont des pourcents au dénominateur 1,000,000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Fonds de prêts flash indisponibles : credit-ui.js n'a pas pu être chargé."),
        ("account", "sum_samet_create", "Fonds de prêt flash créé avec %(amount)s"),
        ("account", "sum_samet_delete", "Fonds de prêt flash %(fund)s supprimé"),
        ("account", "sum_samet_update", "Fonds de prêt flash %(fund)s mis à jour"),
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
    need_old(cur, "même-actif", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Fonds mutualisés de prêts flash avec tirages et remboursements.")
    cur = get("menu", "d_samet")
    need_old(cur, "même-actif", "menu.d_samet")
    d["menu"]["d_samet"] = "Fonds mutualisés de prêts flash et tirages."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    # Keep the original second sentence byte-identical (incl. NBSP); only
    # the first sentence subject changes.
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Les fonds de prêts flash (Same-T) regroupent un actif depuis "
                 "beaucoup de fournisseurs. " + ". ".join(parts[1:]))
    if not new_first.endswith(".") and lines[1].endswith("."):
        new_first += "."
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Fonds Same-T](#/samet)"
    new_link = "[Fonds de prêts flash](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("fr: Same-T -> prêt flash replacements applied.")


if __name__ == "__main__":
    main()
