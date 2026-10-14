#!/usr/bin/env python3
"""Rename "brainkey" -> "frase de recuperación" in vanilla/locales/es.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no brainkey word (its
    "pantalla ... de recuperación" is the recovery-SCREEN sense, already Spanish).
  * seo.desc_help — no brainkey word ("recuperación" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "frase de recuperación" (fem. la/una/esta frase),
built from this locale's OWN attested words: "frase" is attested in
"frase de contraseña" (`help.topic_backups_body`, `help.topic_password_body` —
the passphrase sense, never confused here) and "recuperación" in
"pantalla ... de recuperación" (`help.topic_translation-limitations_body`).
"frase de recuperación" is the plainest standard Spanish crypto term;
"clave mental" (already forbidden by the glossary) rejected. Gender flips to
feminine throughout (un->una, este->esta, el->la, -o->-a endings and pronouns
lo->la); "una" in no_account_yet and "misma" in wallets_body were already fem.
"Generate new X" stays an action label; the causal "es la única forma de
recuperar la cuenta" link is intact; menu.d_brainkey drops the redundant
"de palabras" (una frase already is a word sequence).

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a brainkey-family
     word, else abort (proves we read the current dict, not en).
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint still carries the route hash and nothing else.

Usage: python3 tooling/rename_brainkey_recovery_es.py [--apply]
Dry run (asserts only) by default; --apply writes es.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ES = os.path.join(HERE, "..", "vanilla", "locales", "es.json")

BRAINKEY_RE = re.compile(r"[Bb]rainkey")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "about.s1_body": (
        "Las cuentas viven en una caja cifrada en tu dispositivo y cada transacción se firma localmente antes de transmitirse. Los nodos nunca ven tus secretos — por eso las copias son solo tuyas: si pierdes el brainkey nadie puede recuperar tus fondos.",
        "Las cuentas viven en una caja cifrada en tu dispositivo y cada transacción se firma localmente antes de transmitirse. Los nodos nunca ven tus secretos — por eso las copias son solo tuyas: si pierdes la frase de recuperación nadie puede recuperar tus fondos.",
    ),
    "account.no_account_yet": (
        "La billetera está desbloqueada pero tu clave activa aún no controla ninguna cuenta en cadena. Registra una o importa una brainkey con fondos.",
        "La billetera está desbloqueada pero tu clave activa aún no controla ninguna cuenta en cadena. Registra una o importa una frase de recuperación con fondos.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Una billetera local crea un brainkey en este dispositivo y deriva las claves owner, active y memo. Las claves nunca salen del dispositivo; el archivo de la billetera se cifra con tu contraseña.",
        "Una billetera local crea una frase de recuperación en este dispositivo y deriva las claves owner, active y memo. Las claves nunca salen del dispositivo; el archivo de la billetera se cifra con tu contraseña.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Copia de seguridad: sin archivo — el brainkey de la cuenta nueva se muestra una sola vez al crearla",
        "Copia de seguridad: sin archivo — la frase de recuperación de la cuenta nueva se muestra una sola vez al crearla",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Copia de seguridad: sí — anota el brainkey",
        "Copia de seguridad: sí — anota la frase de recuperación",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Máxima seguridad — queda en este navegador. Muévela con la copia del brainkey.",
        "Máxima seguridad — queda en este navegador. Muévela con la copia de la frase de recuperación.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Importar una cuenta existente (brainkey)",
        "Importar una cuenta existente (frase de recuperación)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Se genera un brainkey nuevo para la cuenta nueva. Anótalo — deriva las claves owner, active y memo.",
        "Se genera una frase de recuperación nueva para la cuenta nueva. Anótala — deriva las claves owner, active y memo.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Guarda este brainkey — es la única forma de recuperar la cuenta.",
        "Guarda esta frase de recuperación — es la única forma de recuperar la cuenta.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Brainkey (guárdalo)",
        "Frase de recuperación (guárdala)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "No se pudo generar un brainkey.",
        "No se pudo generar una frase de recuperación.",
    ),
    "createaccount.err_brainkey_wait": (
        "Espera a que se genere el brainkey primero.",
        "Espera a que se genere la frase de recuperación primero.",
    ),
    "createaccount.generate_new_brainkey": (
        "Generar brainkey nuevo",
        "Generar frase de recuperación nueva",
    ),
    "createaccount.generating_brainkey": (
        "Generando brainkey…",
        "Generando frase de recuperación…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Guardar billetera con este brainkey",
        "Guardar billetera con esta frase de recuperación",
    ),
    "createaccount.step_brainkey": (
        "Brainkey",
        "Frase de recuperación",
    ),
    "help.topic_backups_text": (
        "Tu brainkey ES el respaldo — anótala. Consúltala cuando quieras en el gestor de billetera.",
        "Tu frase de recuperación ES el respaldo — anótala. Consúltala cuando quieras en el gestor de billetera.",
    ),
    "help.topic_wallets_text": (
        "Una billetera guarda tu brainkey y deriva claves de propietario, activas y de memo. Gestionadas en Billetera.",
        "Una billetera guarda tu frase de recuperación y deriva claves de propietario, activas y de memo. Gestionadas en Billetera.",
    ),
    "menu.d_brainkey": (
        "Nueva billetera a partir de una brainkey de palabras.",
        "Nueva billetera a partir de una frase de recuperación.",
    ),
    "menu.d_registration": (
        "Vías de registro en la nube, local y con brainkey.",
        "Vías de registro en la nube, local y con frase de recuperación.",
    ),
    "menu.p_brainkey": (
        "Crear billetera (Brainkey)",
        "Crear billetera (Frase de recuperación)",
    ),
    "seo.desc_login": (
        "Desbloquea tu billetera BitShares local — contraseña, brainkey o claves importadas. Las claves nunca salen de este dispositivo.",
        "Desbloquea tu billetera BitShares local — contraseña, frase de recuperación o claves importadas. Las claves nunca salen de este dispositivo.",
    ),
    "splash.step2_d": (
        "Un brainkey se genera en este dispositivo. Escríbelo en papel.",
        "Una frase de recuperación se genera en este dispositivo. Escríbela en papel.",
    ),
    "wallet.brainkey": (
        "Brainkey",
        "Frase de recuperación",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Importación de brainkey (formulario de esta página, abajo)",
        " · Importación de frase de recuperación (formulario de esta página, abajo)",
    ),
    "wallet.brainkey_words_placeholder": (
        "palabras del brainkey…",
        "palabras de la frase de recuperación…",
    ),
    "wallet.console_single_key_note": (
        "Billetera de clave única: archivos .bin y claves privadas sueltas (WIF) no admitidos — solo importación por brainkey.",
        "Billetera de clave única: archivos .bin y claves privadas sueltas (WIF) no admitidos — solo importación por frase de recuperación.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Brainkey personalizado demasiado corto: 50 caracteres mínimo tras recortar.",
        "Frase de recuperación personalizada demasiado corta: 50 caracteres mínimo tras recortar.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Introduce tu brainkey. Se comprueba en la cadena antes de guardar nada.",
        "Introduce tu frase de recuperación. Se comprueba en la cadena antes de guardar nada.",
    ),
    "wallet.generate_new_brainkey": (
        "Generar brainkey nuevo",
        "Generar frase de recuperación nueva",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "¿Tienes un archivo .bin o claves privadas sueltas? Esta billetera solo importa brainkeys — descifrado .bin e importación WIF no admitidos. Nada se sube a ningún lado.",
        "¿Tienes un archivo .bin o claves privadas sueltas? Esta billetera solo importa la frase de recuperación — descifrado .bin e importación WIF no admitidos. Nada se sube a ningún lado.",
    ),
    # NOTE (post-apply singular fix): the applied new string above uses the
    # SINGULAR "la frase de recuperación" (not the plural "frases de
    # recuperación"), so every renamed key carries the exact compound and the
    # glossary count (42) is mechanical. Edited directly with the same gates
    # re-checked by hand; the script's G2 old string is unchanged.
    "wallet.s4": (
        "Crear billetera (Brainkey)",
        "Crear billetera (Frase de recuperación)",
    ),
    "wallet.s6": (
        "Confirma que anotaste el brainkey primero.",
        "Confirma que anotaste la frase de recuperación primero.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "escribe tus propias palabras de brainkey…",
        "escribe tus propias palabras de la frase de recuperación…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Usar brainkey personalizado",
        "Usar frase de recuperación personalizada",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Anota tu brainkey y guárdalo bien. Quien lo tenga puede gastar tus fondos.",
        "Anota tu frase de recuperación y guárdala bien. Quien la tenga puede gastar tus fondos.",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_backups_body": [
        (
            "tu brainkey ES la copia, y la frase de contraseña por sí sola no restaura nada.",
            "tu frase de recuperación ES la copia, y la frase de contraseña por sí sola no restaura nada.",
            1,
        ),
        (
            "# Tu brainkey es la copia de seguridad",
            "# Tu frase de recuperación es la copia de seguridad",
            1,
        ),
        (
            "toda tu billetera se deriva de forma determinista de una brainkey — una cadena de palabras. Escribir la brainkey respalda cada cuenta",
            "toda tu billetera se deriva de forma determinista de una frase de recuperación — una cadena de palabras. Escribir la frase de recuperación respalda cada cuenta",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "si pierde la brainkey o la contraseña nadie puede recuperar sus fondos.",
            "si pierde la frase de recuperación o la contraseña nadie puede recuperar sus fondos.",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "más una brainkey perdida significa fondos perdidos.",
            "más una frase de recuperación perdida significa fondos perdidos.",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— la brainkey ES el respaldo.",
            "— la frase de recuperación ES el respaldo.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Crear billetera (Brainkey)](#/create-wallet-brainkey)",
            "- [Crear billetera (Frase de recuperación)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "parte de la misma brainkey — no hay credenciales",
            "parte de la misma frase de recuperación — no hay credenciales",
            1,
        ),
        (
            "salvo que lleves la brainkey y la importes.",
            "salvo que lleves la frase de recuperación y la importes.",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Crea una (#/create-wallet-brainkey) o importa una cuenta existente (#/existing-account) — enlaces abajo."


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
    raw = open(ES, encoding="utf-8").read()
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
        open(ES, "w", encoding="utf-8").write(out)
        print("OK es: %d full + %d snippet keys renamed to frase de recuperación" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK es: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
