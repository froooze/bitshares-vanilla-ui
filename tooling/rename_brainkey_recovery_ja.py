#!/usr/bin/env python3
"""Rename "ブレインキー" -> "復旧フレーズ" in vanilla/locales/ja.json.

Scope: ONLY values carrying the backup-word-list sense (42 keys). Keys unchanged.
Excluded by design (asserted untouched, never rewritten):
  * wallet.console_hint — its only brainkey occurrence is the route hash
    `#/create-wallet-brainkey` (a code identifier; the router path stays).
  * help.topic_translation-limitations_body — no ブレインキー word (its
    復旧 is the recovery-SCREEN sense, already Japanese).
  * seo.desc_help — no ブレインキー word (復旧 is generic recovery).
  * placeholders — none of the 42 keys carry %(..)s, and the gate would abort
    if one appeared; sitemap hrefs stay byte-identical (hash kept).
  * %(op)s / op numbers — untouched (none in these keys).

Compound (per brief): "復旧フレーズ", built from this locale's OWN attested
words: "復旧" is attested in `seo.desc_help` ("復旧のガイド") and
`createaccount.back_up_this_brainkey_it_is_the_only_way_to_r`
("アカウントを復旧する唯一の方法"); "フレーズ" is attested as the tail of
"パスフレーズ" (`help.topic_backups_body`, `help.topic_password_body`,
`help.topic_wallets_body` — the passphrase sense, never confused here).
"復旧フレーズ" is the plainest own-words construction; the industry loan
"リカバリーフレーズ" (Ledger/Trezor JA) is NOT used because it introduces an
unattested katakana root — reported as low-confidence in the task report.
Particles (を/が/は/の/こそが) attach unchanged; "書き留めてください"
imperatives stay imperative; the causal "— アカウントを復旧する唯一の方法"
link is intact; placeholder examples stay short (の単語 kept);
the backup-warning ("これを知る者は誰でも資金を使用できます") stays blunt.

Safety gates (assert before write):
  G1 every target's CURRENT value contains ブレインキー, else abort.
  G2 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G3 key set + _meta deep-equal before/after; non-target values untouched.
  G4 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.
  G5 exclusion guard: console_hint still carries the route hash and nothing
     else; translation-limitations_body and seo.desc_help carry no ブレインキー.

Usage: python3 tooling/rename_brainkey_recovery_ja.py [--apply]
Dry run (asserts only) by default; --apply writes ja.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "ja.json")

BRAINKEY_RE = re.compile(r"ブレインキー")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

OLD = "ブレインキー"
NEW = "復旧フレーズ"

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

CONSOLE_HINT_OLD = " 作成（#/create-wallet-brainkey）または既存のアカウントのインポート（#/existing-account） — リンクは下にあります。"


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
        new = cur.replace(OLD, NEW)
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
        set_dig(d, key, dig(d, key).replace(OLD, NEW))

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
        print("OK ja: %d keys renamed ブレインキー -> 復旧フレーズ" % len(TARGETS))
    else:
        print("OK ja: dry run green (%d keys would change)" % len(TARGETS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
