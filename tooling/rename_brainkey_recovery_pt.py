#!/usr/bin/env python3
"""Rename "brainkey" -> "frase de recuperação" in vanilla/locales/pt.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no brainkey word (its
    "tela ... de recuperação" is the recovery-SCREEN sense, already Portuguese).
  * seo.desc_help — no brainkey word ("recuperação" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "frase de recuperação" (fem. a/uma/esta frase),
built from this locale's OWN attested words: "frase" is attested in
"frase secreta" (`help.topic_backups_body`, `help.topic_password_body` —
the passphrase sense, never confused here) and "recuperação" in
"tela ... de recuperação" (`help.topic_translation-limitations_body`).
"frase de recuperação" is the plainest standard Portuguese crypto term;
"chave mental" (already forbidden by the glossary) rejected. The old
loanword was already feminine ("uma brainkey", "a brainkey",
"desta brainkey"), so nearly every article, adjective and pronoun stays
byte-identical — only the noun changes. "Generate new X" stays an action
label; the causal "é a única forma de recuperar a conta" link is intact;
menu.d_brainkey drops the redundant "de palavras" (uma frase already is
a word sequence).

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a brainkey-family
     word, else abort (proves we read the current dict, not en).
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint still carries the route hash and nothing else.

Usage: python3 tooling/rename_brainkey_recovery_pt.py [--apply]
Dry run (asserts only) by default; --apply writes pt.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PT = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

BRAINKEY_RE = re.compile(r"[Bb]rainkey")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "about.s1_body": (
        "As contas vivem em um cofre criptografado no seu dispositivo, e cada transação é assinada localmente antes de transmitir. Os nós aos quais você se conecta nunca veem seus segredos — e é por isso que backups são só seus: se perder a brainkey, ninguém pode recuperar seus fundos.",
        "As contas vivem em um cofre criptografado no seu dispositivo, e cada transação é assinada localmente antes de transmitir. Os nós aos quais você se conecta nunca veem seus segredos — e é por isso que backups são só seus: se perder a frase de recuperação, ninguém pode recuperar seus fundos.",
    ),
    "account.no_account_yet": (
        "A carteira está desbloqueada, mas sua chave ativa ainda não controla nenhuma conta on-chain. Registre uma ou importe uma brainkey com fundos.",
        "A carteira está desbloqueada, mas sua chave ativa ainda não controla nenhuma conta on-chain. Registre uma ou importe uma frase de recuperação com fundos.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Uma carteira local cria uma brainkey neste dispositivo e deriva as chaves owner, active e memo a partir dela. As chaves nunca saem do dispositivo; o arquivo da carteira é criptografado com sua senha.",
        "Uma carteira local cria uma frase de recuperação neste dispositivo e deriva as chaves owner, active e memo a partir dela. As chaves nunca saem do dispositivo; o arquivo da carteira é criptografado com sua senha.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Backup: sem arquivo — a brainkey da nova conta é exibida uma única vez na criação",
        "Backup: sem arquivo — a frase de recuperação da nova conta é exibida uma única vez na criação",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Backup: sim — anote a brainkey",
        "Backup: sim — anote a frase de recuperação",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Melhor segurança — fica neste navegador. Transfira-a com o backup da brainkey.",
        "Melhor segurança — fica neste navegador. Transfira-a com o backup da frase de recuperação.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Importar uma conta existente (brainkey)",
        "Importar uma conta existente (frase de recuperação)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Uma nova brainkey é gerada para a nova conta. Anote-a — ela deriva as chaves owner, active e memo.",
        "Uma nova frase de recuperação é gerada para a nova conta. Anote-a — ela deriva as chaves owner, active e memo.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Faça backup desta brainkey — é a única forma de recuperar a conta.",
        "Faça backup desta frase de recuperação — é a única forma de recuperar a conta.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Brainkey (faça backup)",
        "Frase de recuperação (faça backup)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "Não foi possível gerar uma brainkey.",
        "Não foi possível gerar uma frase de recuperação.",
    ),
    "createaccount.err_brainkey_wait": (
        "Aguarde a brainkey ser gerada primeiro.",
        "Aguarde a frase de recuperação ser gerada primeiro.",
    ),
    "createaccount.generate_new_brainkey": (
        "Gerar nova brainkey",
        "Gerar nova frase de recuperação",
    ),
    "createaccount.generating_brainkey": (
        "Gerando brainkey…",
        "Gerando frase de recuperação…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Salvar carteira com esta brainkey",
        "Salvar carteira com esta frase de recuperação",
    ),
    "createaccount.step_brainkey": (
        "Brainkey",
        "Frase de recuperação",
    ),
    "help.topic_backups_text": (
        "Sua brainkey É o backup — anote-a. Veja-a a qualquer momento no gerenciador da carteira.",
        "Sua frase de recuperação É o backup — anote-a. Veja-a a qualquer momento no gerenciador da carteira.",
    ),
    "help.topic_wallets_text": (
        "Uma carteira guarda sua brainkey e deriva as chaves owner, active e memo. Gerenciada em Carteira.",
        "Uma carteira guarda sua frase de recuperação e deriva as chaves owner, active e memo. Gerenciada em Carteira.",
    ),
    "menu.d_brainkey": (
        "Nova carteira a partir de uma brainkey de palavras.",
        "Nova carteira a partir de uma frase de recuperação.",
    ),
    "menu.d_registration": (
        "Caminhos de cadastro em nuvem, local e por brainkey.",
        "Caminhos de cadastro em nuvem, local e por frase de recuperação.",
    ),
    "menu.p_brainkey": (
        "Criar Carteira (Brainkey)",
        "Criar Carteira (Frase de recuperação)",
    ),
    "seo.desc_login": (
        "Desbloqueie sua carteira local BitShares — senha, brainkey ou chaves importadas. As chaves nunca saem deste dispositivo.",
        "Desbloqueie sua carteira local BitShares — senha, frase de recuperação ou chaves importadas. As chaves nunca saem deste dispositivo.",
    ),
    "splash.step2_d": (
        "A brainkey é gerada neste dispositivo. Anote no papel.",
        "A frase de recuperação é gerada neste dispositivo. Anote no papel.",
    ),
    "wallet.brainkey": (
        "Brainkey",
        "Frase de recuperação",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Importação de brainkey (formulário desta página abaixo)",
        " · Importação de frase de recuperação (formulário desta página abaixo)",
    ),
    "wallet.brainkey_words_placeholder": (
        "palavras da brainkey…",
        "palavras da frase de recuperação…",
    ),
    "wallet.console_single_key_note": (
        "Carteira de chave única: arquivos de backup .bin e chaves privadas avulsas (WIF) não são suportados — somente importação de brainkey.",
        "Carteira de chave única: arquivos de backup .bin e chaves privadas avulsas (WIF) não são suportados — somente importação de frase de recuperação.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Brainkey personalizada muito curta: mínimo de 50 caracteres após aparar.",
        "Frase de recuperação personalizada muito curta: mínimo de 50 caracteres após aparar.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Digite sua brainkey. Ela é conferida na chain antes de salvar qualquer coisa.",
        "Digite sua frase de recuperação. Ela é conferida na chain antes de salvar qualquer coisa.",
    ),
    "wallet.generate_new_brainkey": (
        "Gerar nova brainkey",
        "Gerar nova frase de recuperação",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "Tem um arquivo de backup .bin ou chaves privadas avulsas? Esta carteira importa somente brainkeys — descriptografia de .bin e importação de WIF não são suportadas. Nada é enviado para lugar algum.",
        "Tem um arquivo de backup .bin ou chaves privadas avulsas? Esta carteira importa somente a frase de recuperação — descriptografia de .bin e importação de WIF não são suportadas. Nada é enviado para lugar algum.",
    ),
    # NOTE (post-apply singular fix): the applied new string above uses the
    # SINGULAR "a frase de recuperação" (not the plural "frases de
    # recuperação"), so every renamed key carries the exact compound and the
    # glossary count (42) is mechanical. Edited directly with the same gates
    # re-checked by hand; the script's G2 old string is unchanged.
    "wallet.s4": (
        "Criar Carteira (Brainkey)",
        "Criar Carteira (Frase de recuperação)",
    ),
    "wallet.s6": (
        "Confirme que você anotou a brainkey primeiro.",
        "Confirme que você anotou a frase de recuperação primeiro.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "digite suas próprias palavras da brainkey…",
        "digite suas próprias palavras da frase de recuperação…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Usar brainkey personalizada",
        "Usar frase de recuperação personalizada",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Anote sua brainkey e guarde-a bem. Quem a tiver pode gastar seus fundos.",
        "Anote sua frase de recuperação e guarde-a bem. Quem a tiver pode gastar seus fundos.",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_backups_body": [
        (
            "sua brainkey É o backup, e a frase secreta sozinha não restaura nada.",
            "sua frase de recuperação É o backup, e a frase secreta sozinha não restaura nada.",
            1,
        ),
        (
            "# Sua brainkey é o backup",
            "# Sua frase de recuperação é o backup",
            1,
        ),
        (
            "toda a sua carteira deriva de forma determinística de uma brainkey — uma sequência de palavras. Anotar a brainkey faz backup de todas as contas",
            "toda a sua carteira deriva de forma determinística de uma frase de recuperação — uma sequência de palavras. Anotar a frase de recuperação faz backup de todas as contas",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "se perder a brainkey ou a senha, ninguém consegue recuperar seus fundos.",
            "se perder a frase de recuperação ou a senha, ninguém consegue recuperar seus fundos.",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "mais uma brainkey perdida significa fundos perdidos.",
            "mais uma frase de recuperação perdida significa fundos perdidos.",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— a brainkey É o backup.",
            "— a frase de recuperação É o backup.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Criar Carteira (Brainkey)](#/create-wallet-brainkey)",
            "- [Criar Carteira (Frase de recuperação)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "parta da mesma brainkey — não existem credenciais que a abram",
            "parta da mesma frase de recuperação — não existem credenciais que a abram",
            1,
        ),
        (
            "a menos que você leve a brainkey e a importe.",
            "a menos que você leve a frase de recuperação e a importe.",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Crie uma (#/create-wallet-brainkey) ou importe uma conta existente (#/existing-account) — links abaixo."


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
    raw = open(PT, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    # G1/G2: full-value keys.
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
        if BRAINKEY_RE.search(new):
            problems.append("ABORT %s: script's new string still has a brainkey word (script bug)" % key)
            continue

    # G1: snippet keys.
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

    # G6: exclusion guards — hash-only and brainkey-free keys stay untouched.
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

    # Apply.
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

    # G4: structure.
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
        open(PT, "w", encoding="utf-8").write(out)
        print("OK pt: %d full + %d snippet keys renamed to frase de recuperação" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK pt: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
