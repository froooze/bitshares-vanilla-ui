#!/usr/bin/env python3
"""Add the i18n honesty-chip keys (plan Task 5) to all 12 vanilla locales.

Why ALL 12 and not just en.json: tooling/check_i18n.py holds key-completeness
as a HARD gate — every dict's flattened key set must equal en.json's — and its
stub-honesty rules require a non-allowlisted value to be byte-identical to the
English master. Adding these keys to en.json alone turns the gate red in 22
places (empirically verified: "key drift (missing=['i18n.badge_probe'])" plus
"non-allowlisted ... != en value (dishonest stub)"). This script therefore:

  * en.json  — the master: the key + its English value, allowlisted in
               _meta.translated (which check_i18n requires to list EVERY key).
  * es.json  — key + the ENGLISH value, NOT allowlisted. es is the one partial
               dict, and claiming an untranslated string as translated is the
               "dishonest stub"/"identical to en" failure the gate hunts.
  * the 10 stub dicts — key + the English value; their allowlist stays [] by
               contract (untranslated: true).

So every value here is an HONEST ENGLISH STUB: the keys exist, the app never
crashes on a missing key, and nothing claims to be translated that is not. The
later fill task (Task 9 / validate_translations) replaces the stub VALUES; the
keys never move. This is the same discipline as
docs/vanilla-ui-dialog.md §2 P8 ("~20 new keys x 12 dicts, stubs honestly
English") and as tooling/add_account_net_i18n.py.

The values below MUST stay byte-identical to the t() defaults at the call
sites in vanilla/js/ui/i18n-badge.js — check_i18n.py enforces both directions.

Idempotent: re-running reports existing keys and changes nothing.
"""
import io
import json
import sys

LOCALES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

# Verbatim I18n.t defaults from vanilla/js/ui/i18n-badge.js.
NEW_KEYS = {
    # The chip's face. A mechanism name, not a sentence — "i18n" is what
    # BitShares people call this layer; the aria-label carries the meaning.
    "i18n.badge_chip": "i18n",
    # The chip's accessible name: the whole warning in six words for a screen
    # reader that never opens the note.
    "i18n.badge_label": "Translation status: machine translated, not human verified",
    # The note's one warning sentence. Honest about its scope: the English
    # reference is on the lines the high-risk rule flags (RiskKeys), not "every
    # line", and no claim is made about the ones it skips.
    "i18n.badge_body": "These translations were written by a machine and have not been checked by a human. Lines marked * on the signing screens also show the original English.",
    "i18n.badge_details": "What this means",
    "i18n.badge_improve": "Help improve this translation",
}


def main():
    for code in LOCALES:
        path = "vanilla/locales/%s.json" % code
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for full, value in NEW_KEYS.items():
            section, _, key = full.partition(".")
            bucket = data.setdefault(section, {})
            if key not in bucket:
                bucket[key] = value
                changed = True
            elif bucket[key] != value:
                # es already translated it, or the master drifted: stop and
                # let a human look, rather than overwriting real work.
                print("MISMATCH %s %s: %r != %r" % (path, full, bucket[key], value))
                return 1
            if code == "en":
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