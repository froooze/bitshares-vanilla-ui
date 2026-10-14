#!/usr/bin/env python3
"""Rename "ब्रेनकी" -> "पुनर्प्राप्ति वाक्यांश" in vanilla/locales/hi.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no ब्रेनकी word (its
    वाक्यांश is the generic-phrase sense, already Hindi).
  * seo.desc_help — no ब्रेनकी word ("पुनर्प्राप्ति" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s; sitemap hrefs stay
    byte-identical (hash kept).

Compound (per brief): "पुनर्प्राप्ति वाक्यांश" (masc.), built from this
locale's OWN attested words: "पुनर्प्राप्ति" is attested in
`createaccount.back_up_this_brainkey_it_is_the_only_way_to_r`
("खाता पुनर्प्राप्ति का यही एकमात्र तरीका") and `seo.desc_help`
("पुनर्प्राप्ति हेतु मार्गदर्शिकाएँ"); "वाक्यांश" is attested in
`help.topic_translation-limitations_body` (generic-phrase sense). The
transliteration "रिकवरी फ्रेज़" (0 hits) rejected; the pure-Hindi compound is
the plainest own-words form — reported as low-confidence in the task report
because the industry often transliterates. "मस्तिष्क कुंजी" calque (already
forbidden by the glossary) rejected.

Grammar: ब्रेनकी is feminine (नई/बनाई/छोटी/अपनी/आपकी/खोई/लिख ली/जाँची);
वाक्यांश is masculine, so every agreeing adjective/verb flips inside the 42
keys ONLY (global within targets, never outside): नई->नया, बनाई जाती है->
बनाया जाता है, बनती है->बनता है, बन रही है->बन रहा है, बनाई नहीं जा सकी->
बनाया नहीं जा सका, छोटी है->छोटा है, अपनी->अपना, आपकी->आपका, खोई->खोया,
लिख ली है->लिख लिया है, जाँची जाती है->जाँचा जाता है, की ब्रेनकी (gen)->का
पुनर्प्राप्ति वाक्यांश. "लिख लें/लिखें/बनाएँ/डालें/प्रतीक्षा करें" imperatives
stay imperative; "Generate new X" stays an action label; the causal "— खाता
पुनर्प्राप्ति का यही एकमात्र तरीका है" link is intact; placeholder examples
stay short (शब्द kept); the backup-warning ("जिसके पास यह है वह आपके फ़ंड
खर्च कर सकता है") stays blunt.

Safety gates (assert before write):
  G1 every target's CURRENT value contains ब्रेनकी, else abort.
  G2 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G3 key set + _meta deep-equal before/after; non-target values untouched.
  G4 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G5 exclusion guard: console_hint keeps the route hash; the two excluded
     keys carry no ब्रेनकी; new carries no ब्रेनकी outside hashes.

Usage: python3 tooling/rename_brainkey_recovery_hi.py [--apply]
Dry run (asserts only) by default; --apply writes hi.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

BRAINKEY_RE = re.compile(r"ब्रेनकी")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

OLD = "ब्रेनकी"
NEW = "पुनर्प्राप्ति वाक्यांश"

# Feminine -> masculine agreement fixes, applied AFTER the base replace and
# ONLY inside the 42 target keys. Ordered longest-first so a short pattern
# never shadows a longer one.
FIXES = [
    ("नई ब्रेनकी बनाई जाती है", "नया पुनर्प्राप्ति वाक्यांश बनाया जाता है"),
    ("नई ब्रेनकी बनाएँ", "नया पुनर्प्राप्ति वाक्यांश बनाएँ"),
    ("कस्टम ब्रेनकी बहुत छोटी है", "कस्टम पुनर्प्राप्ति वाक्यांश बहुत छोटा है"),
    ("ब्रेनकी बनाई नहीं जा सकी", "पुनर्प्राप्ति वाक्यांश बनाया नहीं जा सका"),
    ("ब्रेनकी बन रही है", "पुनर्प्राप्ति वाक्यांश बन रहा है"),
    ("ब्रेनकी इसी डिवाइस पर बनती है", "पुनर्प्राप्ति वाक्यांश इसी डिवाइस पर बनता है"),
    ("अपनी ब्रेनकी डालें", "अपना पुनर्प्राप्ति वाक्यांश डालें"),
    ("अपनी ब्रेनकी लिख लें", "अपना पुनर्प्राप्ति वाक्यांश लिख लें"),
    ("आपकी ब्रेनकी ही बैकअप है", "आपका पुनर्प्राप्ति वाक्यांश ही बैकअप है"),
    ("वॉलेट आपकी ब्रेनकी रखता है", "वॉलेट आपका पुनर्प्राप्ति वाक्यांश रखता है"),
    ("नए खाते की ब्रेनकी", "नए खाते का पुनर्प्राप्ति वाक्यांश"),
    ("ब्रेनकी खोई तो", "पुनर्प्राप्ति वाक्यांश खोया तो"),
    ("पहले ब्रेनकी लिख ली है", "पहले पुनर्प्राप्ति वाक्यांश लिख लिया है"),
    ("चेन से जाँची जाती है", "चेन से जाँचा जाता है"),
    ("खोई ब्रेनकी अर्थात्", "खोया पुनर्प्राप्ति वाक्यांश अर्थात्"),
    ("खोई ब्रेनकी", "खोया पुनर्प्राप्ति वाक्यांश"),
]

TARGETS = [
    "about.s1_body",
    "account.no_account_yet",
    "auth.a_local_wallet_creates_a_brainkey_on_this_dev",
    "auth.back_up_no_file_the_new_account_s_brainke",
    "auth.back_up_yes_write_down_the_brainkey",
    "auth.best_security_stays_in_this_browser_move",
    "auth.import_an_existing_account_brainkey",
    "createaccount.a_fresh_brainkey_is_generated_for_the_new_acc",
    "createaccount.back_up_this_brainkey_it_is_the_only_way_to_r",
    "createaccount.brainkey_back_it_up",
    "createaccount.could_not_generate_a_brainkey",
    "createaccount.err_brainkey_wait",
    "createaccount.generate_new_brainkey",
    "createaccount.generating_brainkey",
    "createaccount.save_wallet_with_this_brainkey",
    "createaccount.step_brainkey",
    "help.topic_backups_text",
    "help.topic_wallets_text",
    "help.topic_backups_body",
    "help.topic_bitshares_body",
    "help.topic_password_body",
    "help.topic_register_body",
    "help.topic_sitemap_body",
    "help.topic_wallets_body",
    "menu.d_brainkey",
    "menu.d_registration",
    "menu.p_brainkey",
    "seo.desc_login",
    "splash.step2_d",
    "wallet.brainkey",
    "wallet.brainkey_import_this_page_form_below",
    "wallet.brainkey_words_placeholder",
    "wallet.console_single_key_note",
    "wallet.custom_brainkey_too_short_50_characters_minim",
    "wallet.enter_brainkey_checked_chain",
    "wallet.generate_new_brainkey",
    "wallet.have_a_bin_backup_file_or_bare_private_k",
    "wallet.s4",
    "wallet.s6",
    "wallet.type_your_own_brainkey_words",
    "wallet.use_custom_brainkey_instead",
    "wallet.write_down_brainkey_keep_safe",
]

CONSOLE_HINT_OLD = " एक बनाएँ (#/create-wallet-brainkey) या मौजूदा खाता आयात करें (#/existing-account) — लिंक नीचे।"


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


def render(cur):
    new = cur.replace(OLD, NEW)
    for o, n in FIXES:
        # FIXES are written pre-replace (with ब्रेनकी); apply both the
        # pre-replace form (in case base replace missed it) and the
        # post-replace residue (feminine adjective stranded beside NEW).
        if o in cur:
            new = new.replace(o.replace(OLD, NEW), n)
            new = new.replace(o, n)
        else:
            # Residue forms: feminine marker that survived the base replace.
            residue_o = o.replace(OLD, NEW)
            if residue_o in new:
                new = new.replace(residue_o, n)
    # Generic residue sweep for any feminine agreement the table missed:
    # these pairs only occur beside the new term inside targets.
    generic = [
        ("नई पुनर्प्राप्ति वाक्यांश", "नया पुनर्प्राप्ति वाक्यांश"),
        ("अपनी पुनर्प्राप्ति वाक्यांश", "अपना पुनर्प्राप्ति वाक्यांश"),
        ("आपकी पुनर्प्राप्ति वाक्यांश", "आपका पुनर्प्राप्ति वाक्यांश"),
    ]
    for o, n in generic:
        new = new.replace(o, n)
    return new


def main():
    apply = "--apply" in sys.argv
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key in TARGETS:
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not BRAINKEY_RE.search(cur):
            problems.append("ABORT %s: current value has no brainkey-family word" % key)
            continue
        new = render(cur)
        if BRAINKEY_RE.search(HREF_RE.sub("", new)):
            problems.append("ABORT %s: new still has brainkey word outside a route hash: %r" % (key, new[:120]))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if key == "help.topic_sitemap_body":
            if HREF_RE.findall(cur) != HREF_RE.findall(new):
                problems.append("ABORT %s: sitemap href drift" % key)

    try:
        hint = dig(d, "wallet.console_hint")
        if hint != CONSOLE_HINT_OLD:
            problems.append("ABORT wallet.console_hint moved (must keep #/create-wallet-brainkey): %r" % hint)
        if "#/create-wallet-brainkey" not in hint:
            problems.append("ABORT wallet.console_hint lost its route hash")
        if BRAINKEY_RE.search(hint):
            problems.append("ABORT wallet.console_hint carries a locale brainkey word")
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

    for key in TARGETS:
        set_dig(d, key, render(dig(d, key)))

    after_keys = set(flatten(d))
    if after_keys != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    after_vals = flatten(d)
    for k, v in before_vals.items():
        if k not in TARGETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print("OK hi: %d keys renamed ब्रेनकी -> पुनर्प्राप्ति वाक्यांश (masc. agreement fixed)" % len(TARGETS))
    else:
        print("OK hi: dry run green (%d keys would change)" % len(TARGETS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
