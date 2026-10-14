#!/usr/bin/env python3
"""Rename "brainkey" -> "frase di recupero" in vanilla/locales/it.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no brainkey word (its
    "schermata ... di recupero" is the recovery-SCREEN sense, already Italian).
  * seo.desc_help — no brainkey word ("recupero" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "frase di recupero" (fem. la/una/questa frase),
built from this locale's OWN attested words: "frase" is attested throughout
the shipped dict (generic "una frase può suonare goffa",
`help.topic_translation-limitations_body`) and "recupero" in
"schermata ... di recupero" (same article). "frase di recupero" is the
plainest standard Italian crypto term; "chiave mentale" (already forbidden
by the glossary) rejected. The old loanword was already feminine
("una brainkey", "la brainkey", "questa brainkey"), so nearly every article,
adjective and pronoun stays byte-identical — only the noun changes, plus
"backup brainkey"/"parole brainkey"/"importazione brainkey" noun-adjuncts
which become "backup della frase di recupero" etc. "Generate new X" stays an
action label; the causal "è l'unico modo per recuperare l'account" link is
intact; menu.d_brainkey drops the redundant "di parole" (una frase already
is a word sequence). Short keys use ASCII apostrophes here; the two FULL
values carrying U+2019 ("ce l’abbia", "l’unico") are byte-exact below.

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a brainkey-family
     word, else abort (proves we read the current dict, not en).
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint still carries the route hash and nothing else.

Usage: python3 tooling/rename_brainkey_recovery_it.py [--apply]
Dry run (asserts only) by default; --apply writes it.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IT = os.path.join(HERE, "..", "vanilla", "locales", "it.json")

BRAINKEY_RE = re.compile(r"[Bb]rainkey")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "about.s1_body": (
        "Gli account vivono in un archivio cifrato sul Suo dispositivo e ogni transazione viene firmata localmente prima della trasmissione. I nodi a cui si connette non vedono mai i Suoi segreti — ed è anche per questo che i backup spettano solo a Lei: se perde la brainkey, nessuno potrà recuperare i Suoi fondi.",
        "Gli account vivono in un archivio cifrato sul Suo dispositivo e ogni transazione viene firmata localmente prima della trasmissione. I nodi a cui si connette non vedono mai i Suoi segreti — ed è anche per questo che i backup spettano solo a Lei: se perde la frase di recupero, nessuno potrà recuperare i Suoi fondi.",
    ),
    "account.no_account_yet": (
        "Il wallet è sbloccato ma la sua chiave attiva non controlla ancora alcun account on-chain. Ne registri uno oppure importi una brainkey finanziata.",
        "Il wallet è sbloccato ma la sua chiave attiva non controlla ancora alcun account on-chain. Ne registri uno oppure importi una frase di recupero finanziata.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Un wallet locale crea una brainkey su questo dispositivo e ne deriva le chiavi owner, active e memo. Le chiavi non lasciano mai il dispositivo; il file wallet è cifrato con la Sua password.",
        "Un wallet locale crea una frase di recupero su questo dispositivo e ne deriva le chiavi owner, active e memo. Le chiavi non lasciano mai il dispositivo; il file wallet è cifrato con la Sua password.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Backup: nessun file — la brainkey del nuovo account è mostrata una volta alla creazione",
        "Backup: nessun file — la frase di recupero del nuovo account è mostrata una volta alla creazione",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Backup: sì — annoti la brainkey",
        "Backup: sì — annoti la frase di recupero",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Massima sicurezza — resta in questo browser. Lo sposti con il backup brainkey.",
        "Massima sicurezza — resta in questo browser. Lo sposti con il backup della frase di recupero.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Importi un account esistente (brainkey)",
        "Importi un account esistente (frase di recupero)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Una nuova brainkey viene generata per il nuovo account. La annoti — ne derivano le chiavi owner, active e memo.",
        "Una nuova frase di recupero viene generata per il nuovo account. La annoti — ne derivano le chiavi owner, active e memo.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Faccia il backup di questa brainkey — è l’unico modo per recuperare l’account.",
        "Faccia il backup di questa frase di recupero — è l’unico modo per recuperare l’account.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Brainkey (ne faccia il backup)",
        "Frase di recupero (ne faccia il backup)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "Impossibile generare una brainkey.",
        "Impossibile generare una frase di recupero.",
    ),
    "createaccount.err_brainkey_wait": (
        "Attenda prima la generazione della brainkey.",
        "Attenda prima la generazione della frase di recupero.",
    ),
    "createaccount.generate_new_brainkey": (
        "Generi una nuova brainkey",
        "Generi una nuova frase di recupero",
    ),
    "createaccount.generating_brainkey": (
        "Generazione brainkey…",
        "Generazione della frase di recupero…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Salvi il wallet con questa brainkey",
        "Salvi il wallet con questa frase di recupero",
    ),
    "createaccount.step_brainkey": (
        "Brainkey",
        "Frase di recupero",
    ),
    "help.topic_backups_text": (
        "La Sua brainkey È il backup — la scriva. La visualizzi in qualsiasi momento nel gestore del wallet.",
        "La Sua frase di recupero È il backup — la scriva. La visualizzi in qualsiasi momento nel gestore del wallet.",
    ),
    "help.topic_wallets_text": (
        "Un wallet custodisce la Sua brainkey e deriva le chiavi owner, active e memo. Gestito in Wallet.",
        "Un wallet custodisce la Sua frase di recupero e deriva le chiavi owner, active e memo. Gestito in Wallet.",
    ),
    "menu.d_brainkey": (
        "Nuovo wallet da una brainkey di parole.",
        "Nuovo wallet da una frase di recupero.",
    ),
    "menu.d_registration": (
        "Percorsi di registrazione cloud, locale e brainkey.",
        "Percorsi di registrazione cloud, locale e frase di recupero.",
    ),
    "menu.p_brainkey": (
        "Crei Wallet (Brainkey)",
        "Crei Wallet (Frase di recupero)",
    ),
    "seo.desc_login": (
        "Sblocchi il Suo wallet BitShares locale — password, brainkey o chiavi importate. Le chiavi non lasciano mai questo dispositivo.",
        "Sblocchi il Suo wallet BitShares locale — password, frase di recupero o chiavi importate. Le chiavi non lasciano mai questo dispositivo.",
    ),
    "splash.step2_d": (
        "Una brainkey viene generata su questo dispositivo. La annoti su carta.",
        "Una frase di recupero viene generata su questo dispositivo. La annoti su carta.",
    ),
    "wallet.brainkey": (
        "Brainkey",
        "Frase di recupero",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Importazione brainkey (modulo di questa pagina qui sotto)",
        " · Importazione della frase di recupero (modulo di questa pagina qui sotto)",
    ),
    "wallet.brainkey_words_placeholder": (
        "parole brainkey…",
        "parole della frase di recupero…",
    ),
    "wallet.console_single_key_note": (
        "Wallet a chiave singola: file backup .bin e chiavi private nude (WIF) non supportati — solo importazione brainkey.",
        "Wallet a chiave singola: file backup .bin e chiavi private nude (WIF) non supportati — solo importazione della frase di recupero.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Brainkey personalizzata troppo corta: minimo 50 caratteri dopo il trim.",
        "Frase di recupero personalizzata troppo corta: minimo 50 caratteri dopo il trim.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Inserisca la Sua brainkey. Viene verificata contro la chain prima che qualsiasi cosa sia salvata.",
        "Inserisca la Sua frase di recupero. Viene verificata contro la chain prima che qualsiasi cosa sia salvata.",
    ),
    "wallet.generate_new_brainkey": (
        "Generi una nuova brainkey",
        "Generi una nuova frase di recupero",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "Ha invece un file backup .bin o chiavi private nude? Questo wallet importa solo brainkey — decifratura .bin e importazione WIF non supportate. Nulla viene caricato da nessuna parte.",
        "Ha invece un file backup .bin o chiavi private nude? Questo wallet importa solo la frase di recupero — decifratura .bin e importazione WIF non supportate. Nulla viene caricato da nessuna parte.",
    ),
    # NOTE (post-apply singular fix): the applied new string above uses the
    # SINGULAR "la frase di recupero" (not the plural "frasi di recupero"),
    # so every renamed key carries the exact compound and the glossary count
    # (42) is mechanical. Edited directly with the same gates re-checked by
    # hand; the script's G2 old string is unchanged.
    "wallet.s4": (
        "Crei wallet (Brainkey)",
        "Crei wallet (Frase di recupero)",
    ),
    "wallet.s6": (
        "Confermi di aver prima annotato la brainkey.",
        "Confermi di aver prima annotato la frase di recupero.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "digiti le Sue parole brainkey…",
        "digiti le Sue parole della frase di recupero…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Usi invece una brainkey personalizzata",
        "Usi invece una frase di recupero personalizzata",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Annoti la Sua brainkey e la tenga al sicuro. Chiunque ce l’abbia può spendere i Suoi fondi.",
        "Annoti la Sua frase di recupero e la tenga al sicuro. Chiunque ce l’abbia può spendere i Suoi fondi.",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_backups_body": [
        (
            "la Sua brainkey È il backup, e la passphrase da sola non ripristina nulla.",
            "la Sua frase di recupero È il backup, e la passphrase da sola non ripristina nulla.",
            1,
        ),
        (
            "# La Sua brainkey è il backup",
            "# La Sua frase di recupero è il backup",
            1,
        ),
        (
            "tutto il Suo wallet deriva in modo deterministico da una sola brainkey — una sequenza di parole. Annotare la brainkey salva ogni account",
            "tutto il Suo wallet deriva in modo deterministico da una sola frase di recupero — una sequenza di parole. Annotare la frase di recupero salva ogni account",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "se perde la brainkey o la password nessuno può recuperare i Suoi fondi.",
            "se perde la frase di recupero o la password nessuno può recuperare i Suoi fondi.",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "un refuso qui più una brainkey persa significa fondi persi.",
            "un refuso qui più una frase di recupero persa significa fondi persi.",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— la brainkey È il backup.",
            "— la frase di recupero È il backup.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Crea wallet (brainkey)](#/create-wallet-brainkey)",
            "- [Crea wallet (frase di recupero)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "riparta dalla stessa brainkey — non esistono credenziali che lo aprono",
            "riparta dalla stessa frase di recupero — non esistono credenziali che lo aprono",
            1,
        ),
        (
            "a meno che non porti con sé la brainkey e non la importi.",
            "a meno che non porti con sé la frase di recupero e non la importi.",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Ne crei uno (#/create-wallet-brainkey) o importi un account esistente (#/existing-account) — link qui sotto."


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
    raw = open(IT, encoding="utf-8").read()
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
        open(IT, "w", encoding="utf-8").write(out)
        print("OK it: %d full + %d snippet keys renamed to frase di recupero" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK it: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
