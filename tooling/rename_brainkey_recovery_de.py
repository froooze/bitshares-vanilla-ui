#!/usr/bin/env python3
"""Rename "Brainkey" -> "Wiederherstellungsphrase" in vanilla/locales/de.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only Brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no Brainkey word (its
    "Wiederherstellungs-Bildschirm" is the recovery-SCREEN sense, already German).
  * seo.desc_help — no Brainkey word ("Wiederherstellung" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "Wiederherstellungsphrase" (fem. die), plural
"Wiederherstellungsphrasen" inside compounds (Phrasen-Import, Phrasen-Wörter),
built from this locale's OWN attested words: "Wiederherstellung" is attested in
`seo.desc_help` ("Abstimmung und Wiederherstellung") and the
"Wiederherstellungs-Bildschirm" of `help.topic_translation-limitations_body`;
"phrase" is attested as the tail of "Passphrase" (`help.topic_backups_body`,
`help.topic_password_body` — the password sense, never confused here).
"Wiederherstellungsphrase" is also the plainest standard German crypto term
(Ledger/Trezor DE use it); "Gehirnschlüssel" calque and Denglish
"Recovery-Phrase" rejected. Gender flips masc->fem throughout (den->die,
einen->eine, ihn->sie, er->sie); "derselben" in wallets_body was already fem.
menu.d_brainkey keeps the word-list gloss the de file already uses
("Wort-Brainkey" -> "Wiederherstellungsphrase aus Wörtern").

Safety gates (assert before write):
  G1 every FULL/SNIPPET target's CURRENT value contains a Brainkey-family
     word, else abort (proves we read the current dict, not en).
  G2 every FULL target's current value EQUALS the expected old string.
  G3 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G4 key set + _meta deep-equal before/after; non-target values untouched.
  G5 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G6 exclusion guard: console_hint still carries the route hash and nothing else.

Usage: python3 tooling/rename_brainkey_recovery_de.py [--apply]
Dry run (asserts only) by default; --apply writes de.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DE = os.path.join(HERE, "..", "vanilla", "locales", "de.json")

BRAINKEY_RE = re.compile(r"[Bb]rainkey")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Full-value replacements: dotted key -> (old, new).
FULL = {
    "about.s1_body": (
        "Konten leben in einem verschlüsselten Tresor auf Ihrem Gerät, und jede Transaktion wird vor dem Senden lokal signiert. Die Knoten, mit denen Sie sich verbinden, sehen Ihre Geheimnisse nie — darum sind Backups allein Ihre Sache: Verlieren Sie den Brainkey, kann niemand Ihre Gelder wiederherstellen.",
        "Konten leben in einem verschlüsselten Tresor auf Ihrem Gerät, und jede Transaktion wird vor dem Senden lokal signiert. Die Knoten, mit denen Sie sich verbinden, sehen Ihre Geheimnisse nie — darum sind Backups allein Ihre Sache: Verlieren Sie die Wiederherstellungsphrase, kann niemand Ihre Gelder wiederherstellen.",
    ),
    "account.no_account_yet": (
        "Die Wallet ist entsperrt, aber ihr aktiver Schlüssel kontrolliert noch kein On-Chain-Konto. Registrieren Sie eines oder importieren Sie einen finanzierten Brainkey.",
        "Die Wallet ist entsperrt, aber ihr aktiver Schlüssel kontrolliert noch kein On-Chain-Konto. Registrieren Sie eines oder importieren Sie eine finanzierte Wiederherstellungsphrase.",
    ),
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev": (
        "Eine lokale Wallet erzeugt einen Brainkey auf diesem Gerät und leitet daraus Owner-, Active- und Memo-Schlüssel ab. Schlüssel verlassen das Gerät nie; die Wallet-Datei ist mit Ihrem Passwort verschlüsselt.",
        "Eine lokale Wallet erzeugt eine Wiederherstellungsphrase auf diesem Gerät und leitet daraus Owner-, Active- und Memo-Schlüssel ab. Schlüssel verlassen das Gerät nie; die Wallet-Datei ist mit Ihrem Passwort verschlüsselt.",
    ),
    "auth.back_up_no_file_the_new_account_s_brainke": (
        "Backup: keine Datei — der Brainkey des neuen Kontos wird einmalig bei der Erstellung angezeigt",
        "Backup: keine Datei — die Wiederherstellungsphrase des neuen Kontos wird einmalig bei der Erstellung angezeigt",
    ),
    "auth.back_up_yes_write_down_the_brainkey": (
        "Backup: ja — notieren Sie den Brainkey",
        "Backup: ja — notieren Sie die Wiederherstellungsphrase",
    ),
    "auth.best_security_stays_in_this_browser_move": (
        "Beste Sicherheit — bleibt in diesem Browser. Übertragen Sie sie per Brainkey-Backup.",
        "Beste Sicherheit — bleibt in diesem Browser. Übertragen Sie sie per Backup der Wiederherstellungsphrase.",
    ),
    "auth.import_an_existing_account_brainkey": (
        "Bestehendes Konto importieren (Brainkey)",
        "Bestehendes Konto importieren (Wiederherstellungsphrase)",
    ),
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc": (
        "Für das neue Konto wird ein frischer Brainkey erzeugt. Notieren Sie ihn — er leitet Owner-, Active- und Memo-Schlüssel ab.",
        "Für das neue Konto wird eine frische Wiederherstellungsphrase erzeugt. Notieren Sie sie — sie leitet Owner-, Active- und Memo-Schlüssel ab.",
    ),
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r": (
        "Sichern Sie diesen Brainkey — er ist der einzige Weg, das Konto wiederherzustellen.",
        "Sichern Sie diese Wiederherstellungsphrase — sie ist der einzige Weg, das Konto wiederherzustellen.",
    ),
    "createaccount.brainkey_back_it_up": (
        "Brainkey (sichern)",
        "Wiederherstellungsphrase (sichern)",
    ),
    "createaccount.could_not_generate_a_brainkey": (
        "Brainkey konnte nicht erzeugt werden.",
        "Wiederherstellungsphrase konnte nicht erzeugt werden.",
    ),
    "createaccount.err_brainkey_wait": (
        "Warten Sie zuerst, bis der Brainkey erzeugt ist.",
        "Warten Sie zuerst, bis die Wiederherstellungsphrase erzeugt ist.",
    ),
    "createaccount.generate_new_brainkey": (
        "Neuen Brainkey erzeugen",
        "Neue Wiederherstellungsphrase erzeugen",
    ),
    "createaccount.generating_brainkey": (
        "Brainkey wird erzeugt…",
        "Wiederherstellungsphrase wird erzeugt…",
    ),
    "createaccount.save_wallet_with_this_brainkey": (
        "Wallet mit diesem Brainkey speichern",
        "Wallet mit dieser Wiederherstellungsphrase speichern",
    ),
    "createaccount.step_brainkey": (
        "Brainkey",
        "Wiederherstellungsphrase",
    ),
    "help.topic_backups_text": (
        "Ihre Brainkey IST die Sicherung — notieren Sie sie. Jederzeit im Wallet-Manager einsehbar.",
        "Ihre Wiederherstellungsphrase IST die Sicherung — notieren Sie sie. Jederzeit im Wallet-Manager einsehbar.",
    ),
    "help.topic_wallets_text": (
        "Eine Wallet hält Ihre Brainkey und leitet Eigentümer-, Aktiv- und Memo-Keys ab. Verwaltet unter Wallet.",
        "Eine Wallet hält Ihre Wiederherstellungsphrase und leitet Eigentümer-, Aktiv- und Memo-Keys ab. Verwaltet unter Wallet.",
    ),
    "menu.d_brainkey": (
        "Neue Wallet aus einem Wort-Brainkey.",
        "Neue Wallet aus einer Wiederherstellungsphrase aus Wörtern.",
    ),
    "menu.d_registration": (
        "Cloud-, lokale und Brainkey-Registrierungswege.",
        "Cloud-, lokale und Wiederherstellungsphrasen-Registrierungswege.",
    ),
    "menu.p_brainkey": (
        "Wallet erstellen (Brainkey)",
        "Wallet erstellen (Wiederherstellungsphrase)",
    ),
    "seo.desc_login": (
        "Entsperren Sie Ihre lokale BitShares-Wallet — Passwort, Brainkey oder importierte Schlüssel. Schlüssel verlassen dieses Gerät nie.",
        "Entsperren Sie Ihre lokale BitShares-Wallet — Passwort, Wiederherstellungsphrase oder importierte Schlüssel. Schlüssel verlassen dieses Gerät nie.",
    ),
    "splash.step2_d": (
        "Ein Brainkey wird auf diesem Gerät erzeugt. Notieren Sie ihn auf Papier.",
        "Eine Wiederherstellungsphrase wird auf diesem Gerät erzeugt. Notieren Sie sie auf Papier.",
    ),
    "wallet.brainkey": (
        "Brainkey",
        "Wiederherstellungsphrase",
    ),
    "wallet.brainkey_import_this_page_form_below": (
        " · Brainkey-Import (Formular dieser Seite unten)",
        " · Wiederherstellungsphrasen-Import (Formular dieser Seite unten)",
    ),
    "wallet.brainkey_words_placeholder": (
        "Brainkey-Wörter…",
        "Wiederherstellungsphrasen-Wörter…",
    ),
    "wallet.console_single_key_note": (
        "Single-Key-Wallet: .bin-Sicherungsdateien und reine Private Keys (WIF) werden nicht unterstützt — nur Brainkey-Import.",
        "Single-Key-Wallet: .bin-Sicherungsdateien und reine Private Keys (WIF) werden nicht unterstützt — nur Wiederherstellungsphrasen-Import.",
    ),
    "wallet.custom_brainkey_too_short_50_characters_minim": (
        "Eigener Brainkey zu kurz: mindestens 50 Zeichen nach dem Kürzen.",
        "Eigene Wiederherstellungsphrase zu kurz: mindestens 50 Zeichen nach dem Kürzen.",
    ),
    "wallet.enter_brainkey_checked_chain": (
        "Geben Sie Ihren Brainkey ein. Er wird gegen die Chain geprüft, bevor etwas gespeichert wird.",
        "Geben Sie Ihre Wiederherstellungsphrase ein. Sie wird gegen die Chain geprüft, bevor etwas gespeichert wird.",
    ),
    "wallet.generate_new_brainkey": (
        "Neuen Brainkey erzeugen",
        "Neue Wiederherstellungsphrase erzeugen",
    ),
    "wallet.have_a_bin_backup_file_or_bare_private_k": (
        "Haben Sie eine .bin-Sicherungsdatei oder reine Private Keys? Diese Wallet importiert nur Brainkeys — .bin-Entschlüsselung und WIF-Import werden nicht unterstützt. Nichts wird irgendwo hochgeladen.",
        "Haben Sie eine .bin-Sicherungsdatei oder reine Private Keys? Diese Wallet importiert nur Wiederherstellungsphrasen — .bin-Entschlüsselung und WIF-Import werden nicht unterstützt. Nichts wird irgendwo hochgeladen.",
    ),
    "wallet.s4": (
        "Wallet erstellen (Brainkey)",
        "Wallet erstellen (Wiederherstellungsphrase)",
    ),
    "wallet.s6": (
        "Bestätigen Sie, dass Sie den Brainkey zuerst notiert haben.",
        "Bestätigen Sie, dass Sie die Wiederherstellungsphrase zuerst notiert haben.",
    ),
    "wallet.type_your_own_brainkey_words": (
        "eigene Brainkey-Wörter eingeben…",
        "eigene Wiederherstellungsphrasen-Wörter eingeben…",
    ),
    "wallet.use_custom_brainkey_instead": (
        "Stattdessen eigenen Brainkey verwenden",
        "Stattdessen eigene Wiederherstellungsphrase verwenden",
    ),
    "wallet.write_down_brainkey_keep_safe": (
        "Notieren Sie Ihren Brainkey und bewahren Sie ihn sicher auf. Wer ihn hat, kann Ihre Gelder ausgeben.",
        "Notieren Sie Ihre Wiederherstellungsphrase und bewahren Sie sie sicher auf. Wer sie hat, kann Ihre Gelder ausgeben.",
    ),
}

# Long-body snippet replacements: dotted key -> [(old_snippet, new, count)].
SNIPPETS = {
    "help.topic_backups_body": [
        (
            "Ihre Brainkey IST die Sicherung, und die Passphrase allein stellt nichts wieder her.",
            "Ihre Wiederherstellungsphrase IST die Sicherung, und die Passphrase allein stellt nichts wieder her.",
            1,
        ),
        (
            "# Ihre Brainkey ist die Sicherung",
            "# Ihre Wiederherstellungsphrase ist die Sicherung",
            1,
        ),
        (
            "leitet sich die gesamte Wallet deterministisch aus einer Brainkey ab — einer Zeichenkette aus Wörtern. Notieren Sie die Brainkey, sichern Sie jedes Konto",
            "leitet sich die gesamte Wallet deterministisch aus einer Wiederherstellungsphrase ab — einer Zeichenkette aus Wörtern. Notieren Sie die Wiederherstellungsphrase, sichern Sie jedes Konto",
            1,
        ),
    ],
    "help.topic_bitshares_body": [
        (
            "Verlieren Sie Brainkey oder Passwort, kann niemand Ihre Gelder wiederherstellen.",
            "Verlieren Sie Wiederherstellungsphrase oder Passwort, kann niemand Ihre Gelder wiederherstellen.",
            1,
        ),
    ],
    "help.topic_password_body": [
        (
            "ein Tippfehler hier plus verlorene Brainkey heißt verlorene Gelder.",
            "ein Tippfehler hier plus verlorene Wiederherstellungsphrase heißt verlorene Gelder.",
            1,
        ),
    ],
    "help.topic_register_body": [
        (
            "— die Brainkey IST die Sicherung.",
            "— die Wiederherstellungsphrase IST die Sicherung.",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Wallet erstellen (Brainkey)](#/create-wallet-brainkey)",
            "- [Wallet erstellen (Wiederherstellungsphrase)](#/create-wallet-brainkey)",
            1,
        ),
    ],
    "help.topic_wallets_body": [
        (
            "beginnen Sie mit derselben Brainkey — es gibt keine Zugangsdaten, die sie von irgendwo allein öffnen.",
            "beginnen Sie mit derselben Wiederherstellungsphrase — es gibt keine Zugangsdaten, die sie von irgendwo allein öffnen.",
            1,
        ),
        (
            "außer Sie bringen die Brainkey mit und importieren sie.",
            "außer Sie bringen die Wiederherstellungsphrase mit und importieren sie.",
            1,
        ),
    ],
}

CONSOLE_HINT_OLD = " Erstellen Sie eine (#/create-wallet-brainkey) oder importieren Sie ein bestehendes Konto (#/existing-account) — Links unten."


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
    raw = open(DE, encoding="utf-8").read()
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
        open(DE, "w", encoding="utf-8").write(out)
        print("OK de: %d full + %d snippet keys renamed to Wiederherstellungsphrase" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK de: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
