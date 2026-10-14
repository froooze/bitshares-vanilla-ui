#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in pt.json (REPLACE, not insert).

Owns: the pt Same-T -> empréstimo flash value replacements only.
Consumes: vanilla/locales/pt.json (ordered dict).
Side effects: overwrites pt.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-latin5 (de/es/fr/it/pt batch). Brazilian você register.

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T brand (SameT
without hyphen in the three sum_* lines counts as brand); the two
pooled-funds blurbs were already localized as "mesmo ativo" with no
English brand, so those two assert the known localized old phrase instead.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT pt: {msg}", file=sys.stderr)
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
        ("samet", "title", "Fundos de empréstimos flash"),
        ("samet", "same_t_funds", "Fundos de empréstimos flash"),
        ("menu", "p_samet", "Fundos de empréstimos flash"),
        ("help", "topic_samet_title", "Fundos de empréstimos flash"),
        ("account", "op_samet_borrow", "Empréstimo flash"),
        ("account", "op_samet_create", "Criação de fundo de empréstimo flash"),
        ("account", "op_samet_delete", "Exclusão de fundo de empréstimo flash"),
        ("account", "op_samet_repay", "Pagamento de empréstimo flash"),
        ("account", "op_samet_update", "Atualização de fundo de empréstimo flash"),
        ("credit", "unknown_same_t_fund", "Fundo de empréstimo flash desconhecido."),
        ("samet", "create_hint",
         " Crie um no formulário de criação abaixo — fundos de empréstimos flash próprios aparecem aqui."),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "Empréstimos flash: empréstimo e pagamento ocorrem em UMA transação [67 empréstimo + 68 pagamento] — a chain rejeita um empréstimo isolado. As taxas são porcentuais com denominador 1.000.000."),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "Fundos de empréstimos flash indisponíveis: falha ao carregar credit-ui.js."),
        ("account", "sum_samet_create", "Fundo de empréstimo flash criado com %(amount)s"),
        ("account", "sum_samet_delete", "Fundo de empréstimo flash %(fund)s excluído"),
        ("account", "sum_samet_update", "Fundo de empréstimo flash %(fund)s atualizado"),
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
    need_old(cur, "mesmo ativo", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "Fundos agrupados de empréstimos flash, com saques e pagamentos.")
    cur = get("menu", "d_samet")
    need_old(cur, "mesmo ativo", "menu.d_samet")
    # Old pt blurb also mistranslated draws as "sorteios"; fix to "saques".
    d["menu"]["d_samet"] = "Fundos agrupados de empréstimos flash e saques."

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    parts = lines[1].split(". ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("Fundos de empréstimos flash (Same-T) agrupam um ativo de muitos "
                 "fornecedores. " + ". ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Fundos Same-T](#/samet)"
    new_link = "[Fundos de empréstimos flash](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("pt: Same-T -> empréstimo flash replacements applied.")


if __name__ == "__main__":
    main()
