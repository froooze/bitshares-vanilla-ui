#!/usr/bin/env python3
"""Honest wallet/backup help bodies (issue #2, help-text half).

Rewrites help.topic_wallets_body + help.topic_backups_body in all 12
vanilla/locales/*.json to match BODY_DEFAULTS in
vanilla/js/views/help-ui.js: the old bodies promised a backup-file
download/restore and a cloud username+password login, neither of which
exists (wallet-ui.js + auth-ui.js say so on screen; grep finds no
createObjectURL/Blob/.bin path anywhere in vanilla/js).

Non-English dicts receive the corrected English (honest stubs until
translators refine them); keys stay allowlisted per the add_*_i18n.py
precedent. check_i18n.py enforces both directions afterward.

Idempotent: re-running reports unchanged keys and changes nothing
mismatched values abort loudly instead of overwriting.
"""
import io
import json
import sys

LOCALES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

WALLETS_BODY = (
    "# A web app with a local vault\n"
    "This application runs in your browser and talks to a chain node as its gateway to the network. Everything secret stays in your browser's local vault.\n"
    "# No cloud login\n"
    "This wallet has no username-and-password login: every wallet here is local to one browser. To use your account on a new browser or computer, start from the same brainkey — there are no credentials that open it from anywhere on their own.\n"
    "# Local wallet\n"
    "A local wallet is a database inside one specific browser. It will not follow you to another computer or browser unless you carry the brainkey over and import it.\n"
    "See the Backups article before you rely on a local wallet for real funds.\n"
    "# Password discipline\n"
    "The password encrypts the vault. Short or reused passwords fall to guessing; a unique passphrase written on paper does not.\n"
    "Changing the password re-encrypts everything — verify the current one first, then confirm the wallet still unlocks before you walk away."
)

BACKUPS_BODY = (
    "# Back up early, back up twice\n"
    "Make a backup of your local wallet before you fund it — one backup is usually enough going forward, but keep it in at least two secure places only you can reach.\n"
    "There is no backup file in this wallet: your brainkey IS the backup, and the passphrase alone restores nothing. Without both the words AND the passphrase your funds are gone. Never store the passphrase next to the words.\n"
    "# Your brainkey is the backup\n"
    "If you never imported raw keys by hand, your whole wallet derives deterministically from one brainkey — a string of words. Writing down the brainkey backs up every account and fund in that wallet.\n"
    "View it in the wallet manager and copy it to paper, stored separately from anything digital. Reference-wallet .bin files cannot be imported here — the wallet says so on screen, and no file download exists.\n"
    "# Advanced: hierarchical authorities\n"
    "If you use weighted multi-account authorities instead of plain keys, a key backup alone may NOT restore access — the authority structure itself matters.\n"
    "Re-read the Permissions article and record the full authority setup, not just the words."
)

NEW_VALUES = {
    "help.topic_wallets_body": WALLETS_BODY,
    "help.topic_backups_body": BACKUPS_BODY,
}


def main():
    for code in LOCALES:
        path = "vanilla/locales/%s.json" % code
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for full, value in NEW_VALUES.items():
            section, _, key = full.partition(".")
            bucket = data.setdefault(section, {})
            # Deliberate rewrite (not add): the old bodies promised a backup
            # file and cloud login that do not exist, in every language.
            # Non-English translations of false text are voided back to
            # honest English stubs here; translators redo these two articles
            # from the corrected English (see commit message).
            if bucket.get(key) != value:
                bucket[key] = value
                changed = True
            inv = data["_meta"]["translated"]
            if full not in inv:
                inv.append(full)
                changed = True
        data["_meta"]["translated"] = sorted(data["_meta"]["translated"])
        if changed:
            with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print(("updated " if changed else "unchanged ") + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
