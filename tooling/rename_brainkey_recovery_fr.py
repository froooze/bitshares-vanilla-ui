#!/usr/bin/env python3
"""Rename "brainkey" -> "phrase de récupération" in vanilla/locales/fr.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no brainkey word (its
    "écran ... de récupération" is the recovery-SCREEN sense, already French).
  * seo.desc_help — no brainkey word ("récupération" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "phrase de récupération" (fem. la/une/cette phrase),
built from this locale's OWN attested words: "phrase" is attested in
"phrase secrète" (`help.topic_backups_body`, `help.topic_password_body` —
the passphrase sense, never confused here), "récupération" in "écran ...
de récupération" (`help.topic_translation-limitations_body`) and
"récupération de flux" (`help.topic_news_body`), and "mots"/"suite de mots"
for the word-list gloss (glossary fr.md). "phrase de récupération" is the
plainest standard French crypto term; "clé mentale" (already forbidden by the
glossary) rejected. Gender flips masc->fem throughout (un->une, le->la,
ce->cette, nouveau->nouvelle, il->elle and -é->-ée participles); "votre" and
"même" are neutral. "il n'existe aucun identifiant" keeps "il" (it is the
identifiant, not the phrase). Typography follows each region's own file
convention: ASCII apostrophes in short keys, U+2019 in help bodies.
menu.d_brainkey drops the redundant "de mots" (une phrase already is words).

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a brainkey-family
     word, else abort (proves we read the current dict, not en).
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint still carries the route hash and nothing else.

Usage: python3 tooling/rename_brainkey_recovery_fr.py [--apply]
Dry run (asserts only) by default; --apply writes fr.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "..", "vanilla", "locales", "fr.json")

BRAINKEY_RE = re.compile(r"[Bb]rainkey")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "about.s1_body": (
        "Les comptes reposent dans un coffre chiffré sur votre appareil, et chaque transaction est signée localement avant diffusion. Les nœuds auxquels vous vous connectez ne voient jamais vos secrets — c'est aussi pourquoi les sauvegardes n'appartiennent qu'à vous : perdez le brainkey et personne ne pourra récupérer vos fonds.",
        "Les comptes reposent dans un coffre chiffré sur votre appareil, et chaque transaction est signée localement avant diffusion. Les nœuds auxquels vous vous connectez ne voient jamais vos secrets — c'est aussi pourquoi les sauvegardes n'appartiennent qu'à vous : perdez la phrase de récupération et personne ne pourra récupérer vos fonds.",
    ),
    "account.no_account_yet": (
        "Le portefeuille est déverrouillé mais sa clé active ne contrôle encore aucun compte on-chain. Enregistrez-en un ou importez un brainkey approvisionné.",
        "Le portefeuille est déverrouillé mais sa clé active ne contrôle encore aucun compte on-chain. Enregistrez-en un ou importez une phrase de récupération approvisionnée.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Un portefeuille local crée un brainkey sur cet appareil et en dérive les clés owner, active et memo. Les clés ne quittent jamais l'appareil ; le fichier du portefeuille est chiffré avec votre mot de passe.",
        "Un portefeuille local crée une phrase de récupération sur cet appareil et en dérive les clés owner, active et memo. Les clés ne quittent jamais l'appareil ; le fichier du portefeuille est chiffré avec votre mot de passe.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Sauvegarde : aucun fichier — le brainkey du nouveau compte est affiché une seule fois à la création",
        "Sauvegarde : aucun fichier — la phrase de récupération du nouveau compte est affichée une seule fois à la création",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Sauvegarde : oui — notez le brainkey",
        "Sauvegarde : oui — notez la phrase de récupération",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Sécurité maximale — reste dans ce navigateur. Déplacez-le avec la sauvegarde du brainkey.",
        "Sécurité maximale — reste dans ce navigateur. Déplacez-le avec la sauvegarde de la phrase de récupération.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Importer un compte existant (brainkey)",
        "Importer un compte existant (phrase de récupération)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Un nouveau brainkey est généré pour le nouveau compte. Notez-le — il en dérive les clés owner, active et memo.",
        "Une nouvelle phrase de récupération est générée pour le nouveau compte. Notez-la — elle en dérive les clés owner, active et memo.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Sauvegardez ce brainkey — c'est le seul moyen de récupérer le compte.",
        "Sauvegardez cette phrase de récupération — c'est le seul moyen de récupérer le compte.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Brainkey (sauvegardez-le)",
        "Phrase de récupération (sauvegardez-la)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "Impossible de générer un brainkey.",
        "Impossible de générer une phrase de récupération.",
    ),
    "createaccount.err_brainkey_wait": (
        "Attendez d'abord que le brainkey soit généré.",
        "Attendez d'abord que la phrase de récupération soit générée.",
    ),
    "createaccount.generate_new_brainkey": (
        "Générer un nouveau brainkey",
        "Générer une nouvelle phrase de récupération",
    ),
    "createaccount.generating_brainkey": (
        "Génération du brainkey…",
        "Génération de la phrase de récupération…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Enregistrer le portefeuille avec ce brainkey",
        "Enregistrer le portefeuille avec cette phrase de récupération",
    ),
    "createaccount.step_brainkey": (
        "Brainkey",
        "Phrase de récupération",
    ),
    "help.topic_backups_text": (
        "Votre brainkey EST la sauvegarde — notez-le. Consultez-le à tout moment dans le gestionnaire de portefeuille.",
        "Votre phrase de récupération EST la sauvegarde — notez-la. Consultez-la à tout moment dans le gestionnaire de portefeuille.",
    ),
    "help.topic_wallets_text": (
        "Un portefeuille contient votre brainkey et dérive les clés owner, active et memo. Géré sous Portefeuille.",
        "Un portefeuille contient votre phrase de récupération et dérive les clés owner, active et memo. Géré sous Portefeuille.",
    ),
    "menu.d_brainkey": (
        "Nouveau portefeuille à partir d'un brainkey de mots.",
        "Nouveau portefeuille à partir d'une phrase de récupération.",
    ),
    "menu.d_registration": (
        "Parcours d'inscription cloud, local et brainkey.",
        "Parcours d'inscription cloud, local et phrase de récupération.",
    ),
    "menu.p_brainkey": (
        "Créer un portefeuille (Brainkey)",
        "Créer un portefeuille (Phrase de récupération)",
    ),
    "seo.desc_login": (
        "Déverrouillez votre portefeuille BitShares local — mot de passe, brainkey ou clés importées. Les clés ne quittent jamais cet appareil.",
        "Déverrouillez votre portefeuille BitShares local — mot de passe, phrase de récupération ou clés importées. Les clés ne quittent jamais cet appareil.",
    ),
    "splash.step2_d": (
        "Un brainkey est généré sur cet appareil. Notez-le sur papier.",
        "Une phrase de récupération est générée sur cet appareil. Notez-la sur papier.",
    ),
    "wallet.brainkey": (
        "Brainkey",
        "Phrase de récupération",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Import du brainkey (formulaire de cette page ci-dessous)",
        " · Import de la phrase de récupération (formulaire de cette page ci-dessous)",
    ),
    "wallet.brainkey_words_placeholder": (
        "mots du brainkey…",
        "mots de la phrase de récupération…",
    ),
    "wallet.console_single_key_note": (
        "Portefeuille à clé unique : fichiers de sauvegarde .bin et clés privées nues (WIF) non pris en charge — import du brainkey uniquement.",
        "Portefeuille à clé unique : fichiers de sauvegarde .bin et clés privées nues (WIF) non pris en charge — import de la phrase de récupération uniquement.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Brainkey personnalisé trop court : 50 caractères au minimum après nettoyage.",
        "Phrase de récupération personnalisée trop courte : 50 caractères au minimum après nettoyage.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Saisissez votre brainkey. Il est vérifié sur la chaîne avant tout enregistrement.",
        "Saisissez votre phrase de récupération. Elle est vérifiée sur la chaîne avant tout enregistrement.",
    ),
    "wallet.generate_new_brainkey": (
        "Générer un nouveau brainkey",
        "Générer une nouvelle phrase de récupération",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "Vous avez plutôt un fichier de sauvegarde .bin ou des clés privées nues ? Ce portefeuille n'importe que des brainkeys — le déchiffrement .bin et l'import WIF ne sont pas pris en charge. Rien n'est téléversé nulle part.",
        "Vous avez plutôt un fichier de sauvegarde .bin ou des clés privées nues ? Ce portefeuille n'importe que la phrase de récupération — le déchiffrement .bin et l'import WIF ne sont pas pris en charge. Rien n'est téléversé nulle part.",
    ),
    # NOTE (post-apply singular fix): the applied new string above uses the
    # SINGULAR "la phrase de récupération" (not the plural "des phrases de
    # récupération"), so every renamed key carries the exact compound and the
    # glossary count (42) is mechanical. Edited directly with the same gates
    # re-checked by hand; the script's G2 old string is unchanged.
    "wallet.s4": (
        "Créer un portefeuille (Brainkey)",
        "Créer un portefeuille (Phrase de récupération)",
    ),
    "wallet.s6": (
        "Confirmez que vous avez d'abord noté le brainkey.",
        "Confirmez que vous avez d'abord noté la phrase de récupération.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "saisissez vos propres mots de brainkey…",
        "saisissez vos propres mots de la phrase de récupération…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Utiliser plutôt un brainkey personnalisé",
        "Utiliser plutôt une phrase de récupération personnalisée",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Notez votre brainkey et conservez-le en lieu sûr. Quiconque le possède peut dépenser vos fonds.",
        "Notez votre phrase de récupération et conservez-la en lieu sûr. Quiconque la possède peut dépenser vos fonds.",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
# NOTE: help bodies use the typographic apostrophe U+2019 (d’un, n’existe);
# short keys above use the ASCII apostrophe. Both are byte-exact here.
SNIPPETS = {
    "help.topic_backups_body": [
        (
            "votre brainkey EST la sauvegarde, et la phrase secrète seule ne restaure rien.",
            "votre phrase de récupération EST la sauvegarde, et la phrase secrète seule ne restaure rien.",
            1,
        ),
        (
            "# Votre brainkey est la sauvegarde",
            "# Votre phrase de récupération est la sauvegarde",
            1,
        ),
        (
            "tout votre portefeuille dérive de manière déterministe d’un seul brainkey — une suite de mots. Noter le brainkey sauvegarde chaque compte et chaque fonds de ce portefeuille.\nAffichez-le dans le gestionnaire de portefeuille et recopiez-le sur papier",
            "tout votre portefeuille dérive de manière déterministe d’une seule phrase de récupération — une suite de mots. Noter la phrase de récupération sauvegarde chaque compte et chaque fonds de ce portefeuille.\nAffichez-la dans le gestionnaire de portefeuille et recopiez-la sur papier",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "perdez le brainkey ou le mot de passe et personne ne pourra récupérer vos fonds.",
            "perdez la phrase de récupération ou le mot de passe et personne ne pourra récupérer vos fonds.",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "une faute ici plus un brainkey perdu signifie fonds perdus.",
            "une faute ici plus une phrase de récupération perdue signifie fonds perdus.",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— le brainkey EST la sauvegarde.",
            "— la phrase de récupération EST la sauvegarde.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Créer un portefeuille (Brainkey)](#/create-wallet-brainkey)",
            "- [Créer un portefeuille (Phrase de récupération)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "repartez du même brainkey — il n’existe aucun identifiant",
            "repartez de la même phrase de récupération — il n’existe aucun identifiant",
            1,
        ),
        (
            "à moins que vous ne transportiez le brainkey et ne l’importiez.",
            "à moins que vous ne transportiez la phrase de récupération et ne l’importiez.",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Créez-en un (#/create-wallet-brainkey) ou importez un compte existant (#/existing-account) — liens ci-dessous."


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
    raw = open(FR, encoding="utf-8").read()
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
        open(FR, "w", encoding="utf-8").write(out)
        print("OK fr: %d full + %d snippet keys renamed to phrase de récupération" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK fr: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
