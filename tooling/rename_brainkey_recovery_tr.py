#!/usr/bin/env python3
"""Rename "beyin anahtarı" -> "kurtarma ifadesi" in vanilla/locales/tr.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no beyin anahtarı word.
  * seo.desc_help — no beyin anahtarı word ("kurtarma" is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s; sitemap hrefs stay
    byte-identical (hash kept).

Compound (per brief): "kurtarma ifadesi", built from this locale's OWN
attested words: "kurtarma" is attested in `seo.desc_help`
("kurtarma kılavuzları") and
`createaccount.back_up_this_brainkey_it_is_the_only_way_to_r`
("hesabı kurtarmanın tek yolu"); "ifade" is attested in
`help.topic_translation-limitations_body` ("bir ifade yine de tuhaf
okunabilir" — the phrase/expression sense) and the verb "ifade eder"
(`help.topic_accounts-permissions_body`). "kurtarma ifadesi" is the plainest
standard Turkish crypto term (Ledger TR uses it); "akıl anahtarı" (already
forbidden by the glossary) rejected. "kelime/kelimeler" (words) is kept where
the English says words (`wallet.brainkey_words_placeholder`
"kurtarma ifadesi kelimeleri…", `menu.d_brainkey`
"Beyin anahtarı kelimeleriyle" -> "Kurtarma ifadesi kelimeleriyle").
"yazın" imperatives stay imperative; "Yeni ... üret" stays an action label;
the causal "— hesabı kurtarmanın tek yolu budur" link is intact; placeholder
examples stay short; the backup-warning ("Sahip olan fonlarınızı
harcayabilir") stays blunt.

Inflections (all 11 surface forms, longest-first, case kept): nominative
anahtarı->ifadesi, accusative anahtarını->ifadesini, genitive anahtarının->
ifadesinin, instrumental anahtarıyla->ifadesiyle, ablative anahtarından->
ifadesinden, 2nd-person anahtarınız->ifadeniz, anahtarınızı->ifadenizi,
anahtarınızın->ifadenizin — each with its Beyin/beyin capitalisation.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a beyin-anahtar form, else abort.
  G2 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged;
     new carries no beyin-anahtar outside hashes.
  G3 key set + _meta deep-equal before/after; non-target values untouched.
  G4 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G5 exclusion guard: console_hint keeps the route hash; the two excluded
     keys carry no beyin-anahtar.

Usage: python3 tooling/rename_brainkey_recovery_tr.py [--apply]
Dry run (asserts only) by default; --apply writes tr.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "tr.json")

BRAINKEY_RE = re.compile(r"beyin\s+anahtar", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

# Longest-first so "anahtarınızın" never half-matches "anahtarınız".
REPS = [
    ("Beyin anahtarınızın", "Kurtarma ifadenizin"),
    ("beyin anahtarınızın", "kurtarma ifadenizin"),
    ("Beyin anahtarınızı", "Kurtarma ifadenizi"),
    ("beyin anahtarınızı", "kurtarma ifadenizi"),
    ("Beyin anahtarınız", "Kurtarma ifadeniz"),
    ("beyin anahtarınız", "kurtarma ifadeniz"),
    ("beyin anahtarından", "kurtarma ifadesinden"),
    ("Beyin anahtarının", "Kurtarma ifadesinin"),
    ("beyin anahtarının", "kurtarma ifadesinin"),
    ("beyin anahtarıyla", "kurtarma ifadesiyle"),
    ("Beyin anahtarıyla", "Kurtarma ifadesiyle"),
    ("Beyin anahtarını", "Kurtarma ifadesini"),
    ("beyin anahtarını", "kurtarma ifadesini"),
    ("Beyin anahtarı", "Kurtarma ifadesi"),
    ("beyin anahtarı", "kurtarma ifadesi"),
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

CONSOLE_HINT_OLD = " Oluşturun (#/create-wallet-brainkey) veya mevcut hesabı içe aktarın (#/existing-account) — bağlantılar aşağıda."


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
    new = cur
    for o, n in REPS:
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
            problems.append("ABORT %s: new still has brainkey word outside a route hash" % key)
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
        print("OK tr: %d keys renamed beyin anahtarı -> kurtarma ifadesi (11 forms)" % len(TARGETS))
    else:
        print("OK tr: dry run green (%d keys would change)" % len(TARGETS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
