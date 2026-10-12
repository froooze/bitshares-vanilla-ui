#!/usr/bin/env python3
"""add_translation_limitations_i18n.py — add the Task 6 keys to all 12 dicts.

Adds the translation-limitations help article keys and the two RiskText
literals (the asterisk button's accessible name and the article link's label)
to every vanilla/locales/*.json, plus the en.json _meta.translated inventory.

INSERT-ONLY, and that is the whole point of this script existing separately
from tooling/i18n_add_keys.py: the older batch inserter self-heals every key it
knows back to the values recorded in ITS OWN source, so re-running it after a
later translation batch has overwritten those keys silently reverts real
translations to English (verified on de/es/fr/... : ~290 lines each). This one
writes a key only when it is missing or already equal to the English value it
carries; a value that has been translated is left alone and reported.

Non-en dicts keep English (honest stubs, never machine-translated) and stay out
of their allowlists, exactly like every other unverified key: check_i18n.py
rejects a "translation" identical to English.

Stdlib only. Usage: python3 tooling/add_translation_limitations_i18n.py
Exits non-zero if a dict is missing an anchor or a key would be rewritten.
"""
import io
import json
import sys

LOCALES = ["en", "de", "es", "fr", "it", "ja", "ko", "ru", "tr", "zh", "hi", "pt"]

# {namespace: (anchor, {short key: english value})} applied in this order, so a
# later batch can anchor on a key an earlier one just created. Values are
# byte-identical to the t() defaults in help-ui.js / risk-text.js.
BATCHES = [
    ("help", "topic_sitemap_body", {
        "topic_translation-limitations_title": "Translation limitations",
        "topic_translation-limitations_text": "Machine-filled translations are labeled; the English reference is always one tap away. Help us fix a line.",
        "topic_translation-limitations_body": (
            "A translation marked machine-filled was written by a machine. Nobody has read it "
            "to check that it says what the English says — which is why the language you are "
            "reading now carries the marker chip in this wallet's header.\n\n"
            "# What the * on a line means\n"
            "A * on a signing line means two things at once: the wording was filled by a "
            "machine, and the original English is one tap away. Tap the * and the English "
            "appears under the line exactly as this wallet's English master stores it — the "
            "same text every other language was translated from, not a paraphrase of it.\n\n"
            "Amounts, object ids, asset symbols and prices never carry a *. They are chain "
            "data rather than sentences, so there is no English wording behind them to compare "
            "against. A * therefore always marks a sentence a person should read before "
            "signing.\n\n"
            "# What the confidence levels mean\n"
            "Every language this wallet ships carries one rating, listed in the table below. "
            "High means the wording tracks the English closely and reads naturally. Good means "
            "it is usable, though a phrase may still read awkwardly. Moderate means read it as a "
            "draft and check the English before you rely on it.\n\n"
            "A rating describes what has been checked so far, for the language as a whole rather "
            "than line by line. English itself is the reference: it is written by hand, and "
            "every other language is translated from it.\n\n"
            "# How to correct a string\n"
            "Corrections start with a report. Say which language the line was in, give the key "
            "that line discloses, paste the English it was supposed to say, and suggest the "
            "wording you would use instead.\n\n"
            "- One report per line keeps a fix easy to apply.\n"
            "- Report the signing screens first: a wrong sentence on a confirm dialog is the "
            "costly kind.\n"
            "- Use the link at the end of this article. It opens an issue already labelled for "
            "translations on this project's tracker, so nothing has to be retyped.\n\n"
            "# Corrections are the only path to human reviewed\n"
            "Nothing else moves a string off machine-filled: not how often a language is used, "
            "not a second machine agreeing with the first, not a translation memory. A string "
            "becomes human reviewed when a person reads it in its own language and accepts it, "
            "and a line is human reviewed only for the language that was actually checked.\n\n"
            "Until then the marker stays where it is. A translation nobody has read beats no "
            "translation at all, but it is not the same thing as one a person stood behind."
        ),
    }),
    ("help", "topic_translation-limitations_body", {
        "translation_confidence_heading": "How confident each language is",
        "confidence_language": "Language",
        "confidence_level": "Confidence",
        "confidence_high": "High",
        "confidence_good": "Good",
        "confidence_moderate": "Moderate — please verify",
        "report_translation_link": "Report a translation problem on GitHub",
    }),
    ("i18n", "badge_improve", {
        "risk_show_english": "Show the English reference for this line",
        "risk_about_translations": "About these translations",
    }),
]


def insert_after(section, anchor, shorts):
    """Insert the missing short keys after `anchor`, keeping the rest in order.

    Returns (section, inserted, rewritten). A key that already holds a DIFFERENT
    value is never overwritten: it was translated by a human, so this script
    has no business touching it.
    """
    rebuilt, inserted, rewritten = {}, [], []
    for key, val in section.items():
        rebuilt[key] = val
        if key in shorts and rebuilt[key] != shorts[key]:
            rewritten.append(key)
        if key == anchor:
            for short, v in shorts.items():
                if short not in section:
                    rebuilt[short] = v
                    inserted.append(short)
    return rebuilt, inserted, rewritten


# STUB_SYNC: the sitemap gains ONE page (AGENTS.md §7 rule 10 lists every
# routable page). The sitemap body is an English string in en.json and an
# honest English stub in the other 11 (none of them allowlists it), so the new
# line is a declared DELTA rather than a third full copy of the body: insert it
# after the Help line. Refuses for a non-en dict that allowlists the key — that
# would be a real translation, which no script may overwrite.
SYNC_KEY = "help.topic_sitemap_body"
SYNC_AFTER = "- [Help](#/help)\n"
SYNC_LINE = "- [Translation limitations](#/help/translation-limitations)\n"


def sync_sitemap(body, code, allowlisted):
    """Return (new body, changed). Raises SystemExit on a bad precondition."""
    if SYNC_LINE in body:
        return body, False
    if SYNC_AFTER not in body:
        print("%s: %s has no %r anchor — update this script, do not guess"
              % (code, SYNC_KEY, SYNC_AFTER.strip()))
        raise SystemExit(1)
    if code != "en" and allowlisted:
        print("%s: %s is allowlisted (a real translation) — a translator must add "
              "the line, not this script" % (code, SYNC_KEY))
        raise SystemExit(1)
    return body.replace(SYNC_AFTER, SYNC_AFTER + SYNC_LINE, 1), True


def main():
    for code in LOCALES:
        path = "vanilla/locales/%s.json" % code
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        for ns, anchor, shorts in BATCHES:
            section = data.get(ns)
            if not isinstance(section, dict):
                print("%s: namespace %s missing" % (path, ns))
                return 1
            if anchor not in section and not all(k in section for k in shorts):
                print("%s: anchor %s.%s MISSING" % (path, ns, anchor))
                return 1
            section, inserted, rewritten = insert_after(section, anchor, shorts)
            data[ns] = section
            if rewritten:
                print("%s: REFUSING to rewrite %s (already translated: %s)"
                      % (path, ns, rewritten))
                return 1
        body, changed = sync_sitemap(data["help"]["topic_sitemap_body"], code,
                                    SYNC_KEY in (data["_meta"].get("translated") or []))
        data["help"]["topic_sitemap_body"] = body
        if code == "en":
            inv = data["_meta"]["translated"]
            for ns, _, shorts in BATCHES:
                for short in shorts:
                    full = "%s.%s" % (ns, short)
                    if full not in inv:
                        inv.append(full)
            inv.sort()
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated %s%s" % (path, "" if changed else " (sitemap already listed the article)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
