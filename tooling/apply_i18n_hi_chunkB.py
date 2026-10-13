#!/usr/bin/env python3
"""i18n hi chunk-B: fill the help / honesty tail hi.json still leaves in English.

Scope: ONLY the sections listed below. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key holding this batch's translation is skipped (re-runnable);
  * a key missing from hi.json, or one whose English master moved, is REFUSED;
  * HI + KEPT_ENGLISH together must account for EVERY untranslated key of the
    ten sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset and
REFUSES anything outside them; this batch REFUSES anything outside help, pool,
pool_net, explorer, seo, splash, about, shell, menu and i18n. A key that
crosses the line is a reviewer's problem, never a script's silent edit.

The `i18n` section is inside this batch's scope even though it is not one of
the nine named sections: it is seven keys, all of them the honesty surface
(badge chip/label/body/details/improve + risk_show_english /
risk_about_translations), and the brief assigns that surface here. Nothing else
lives in that section, so taking it costs no other batch anything.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/check_i18n.py checks as
                      IDENTIFIERS);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master.
                      Five values in this batch are multi-line markdown
                      articles (help.topic_backups_body 9 lines, wallets 10,
                      browser 6, about-making 5, sitemap 83, translation
                      limitations 23) whose heading structure and list shape the
                      help renderer depends on;
  G4b edge spaces   leading / trailing whitespace of the English master is
                      reproduced exactly. Six values in this batch are GLUE
                      with a load-bearing blank - " (core)", " (raw)",
                      " (virtual)", "Quote (preview): ", and the two swap
                      hints that hang under a panel heading - where a missing
                      space welds the computed value onto the label or onto the
                      sentence above it;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an untranslated key must still equal en;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  script         no Cyrillic and no CJK letter may appear in any value
                      THIS BATCH writes. Hindi is Devanagari; a stray Cyrillic
                      or Han character is a copy-paste from a sibling locale, not
                      a Hindi word. The whole file is swept and a hit OUTSIDE
                      these ten sections is reported as PRE-EXISTING rather than
                      repaired - chunk-A owns those keys;
  G7b quotes         no ASCII or typographic apostrophe in a value this batch
                      writes. Devanagari prose needs none (the file already
                      quotes with the curly pair " " - see
                      misc.invoice_query_bad_amount - and with no apostrophe
                      anywhere in the 3518 translated strings), so a stray one
                      would be the only such spelling in the dictionary. The
                      English masters DO carry apostrophes ("browser's",
                      "builders'", "asset's"), which is exactly why the rule is
                      worth asserting on the Hindi side;
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric (pool.list_sub ships
                      "x*y=k", outside this batch);
  G9  loanwords      every Latin token a value THIS BATCH writes must be
                      declared in LOAN below, or already occur in the ENGLISH
                      master of that same key (which is how DATA - a file path,
                      a platform API name, an account name - legitimately stays
                      Latin). Anything that leans on the English-source clause
                      rather than on LOAN is printed, so a reviewer can see the
                      difference instead of guessing. Hindi crypto UIs keep the
                      English word for DEX, HTLC, FBA, BitShares, BTS, API,
                      Op, GitHub, WebCrypto, BigInt - inventing a fake
                      Devanagari transliteration instead would be worse than the
                      loanword, because the reader already searches for the
                      Latin string.

Register is FORMAL (aap) - the standard for Hindi financial software - matching
the confirmed probe run and chunk-A.

Vocabulary is reused verbatim from the 3518 strings hi.json already ships and
from tooling/probe_runs/hi-runB-nemotron3.json, so this batch reads like the
rest of the dictionary: brainkey (ब्रेनकी), passphrase (पासफ़्रेज़), vault
(तिजोरी), backup (बैकअप), browser (ब्राउज़र), community (कम्युनिटी इंडेक्स),
pool (पूल), swap (स्वैप), stake (स्टेक), LP share (LP शेयर), market (मार्केट),
exchange (एक्सचेंज), desk (डेस्क), order book (ऑर्डर बुक), fee (शुल्क),
smartcoin (स्मार्टकॉइन), user-issued (यूज़र-जारी), raw (कच्चा), core (कोर),
stale (पुराना), publish (प्रकाशित करें), publisher (प्रकाशक), hop (हॉप),
orphan (अनाथ), skeleton (शामिल स्केलेटन), collapse/expand
(संकुचित करें / विस्तार करें), 3 phrases taken straight from the confirmed run
(अंग्रेज़ी संदर्भ दिखाएँ, * से चिह्नित हर पंक्ति पर अंग्रेज़ी एक टैप दूर, मशीन,
मानव जाँच).

Chunk-A's three settled spellings are inherited unchanged so one term has one
spelling across the dictionary: authority = अथॉरिटी (help sitemap
"Custom Authorities", the translation-limitations article's "hierarchical
authorities" sense is spelled the same way), extension = एक्सटेंशन (no
occurrence in this batch's English sources), period/range = अवधि (no occurrence
either). Two PRE-EXISTING splits this batch did NOT create and cannot fix from
an insert-only pass are listed in the report: menu.p_authorities says
प्राधिकरण and help.community_title says कम्युनिटी where this batch writes
अथॉरिटी and समुदाय.

Structural honesty in the footer: app.js:955-978 always appends the branch link
(the literal text "Master") AFTER the relation string, which is why every
language but ja/ko/tr leaves "Master" in Latin. Hindi puts case
postpositions after their noun, so a faithful "…-ahead-of Master" clause cannot
be spelled in the available DOM order. The relation strings are therefore
translated as direction fragments ("3 कमिट आगे") rather than as a clause that
claims a preposition it cannot place. The same reasoning covers
footer_offbranch ("अन्य शाखा"), which would otherwise say "Master" twice.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and every number the English quotes is kept
byte-verbatim (26 September 2026, 3 October, #3583, 360px, 4K, 24h, the first
100 assets, 1.2.0-style ids, the ?dialog=N deep link).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_hi_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_hi_chunkB.py --apply         # writes hi.json
  python3 tooling/apply_i18n_hi_chunkB.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
HI_PATH = os.path.join(BASE, "hi.json")

# The ten sections this batch owns. Everything else belongs to chunk-A and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool", "pool_net", "explorer", "seo", "splash", "about",
    "shell", "menu", "i18n",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from HI below so they keep the
# English bytes, and the verify pass re-asserts every one after the write. Four
# of them (the three shell brands plus the net/host footer glue) live in THIS
# batch's own shell section, so they are also listed in KEPT_ENGLISH - without
# that they would trip the "every untranslated key must be declared" refusal.
# The settings ids live outside these sections and are listed here only so a
# drift anywhere in the file is caught.
PINNED = (
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
    "shell.footer_net_host",
    "settings.network_mainnet",
    "settings.network_testnet",
    "settings.network_devnet",
    "settings.custom_placeholder",
    "settings.pending",
    "settings.dash",
    "settings.theme_original_blue",
    "settings.theme_light",
    "settings.theme_dark",
)

PLACEHOLDER = re.compile(r"%\([A-Za-z0-9_]+\)s")
BRACE = re.compile(r"\{[A-Za-z0-9_]+\}")
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")
INVISIBLE = re.compile(u"[­‍⁠﻿]")
DOT_CHARS = u"·•‧･"
APO_TYPO = u"’"
APO_ASCII = u"'"
IDEO_SPACE = u"　"
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
CJK = re.compile(u"[一-鿿぀-ヿ가-힯]")
# G9: a Latin run inside a Devanagari value. A token may continue through -
# _ . / so "Same-T", "vanilla-ui-dialog.md" and "index.html" are one decision
# each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word or symbol a Hindi crypto UI prints in Latin; anything else has to be
# Devanagari.
LOAN = frozenset((
    # --- chain / protocol vocabulary
    "BitShares",      # the chain's own name, in prose and in every SEO title;
                       # zh, ja, de, ru and pt all keep it in Latin
    "BTS",            # the core asset ticker
    "USD",            # the quote leg of the BTS/USD market desk title
    "HTLC",           # hash time-locked contract: the menu page name and every
                       # sitemap line; en/es/de/it/ko all keep it
    "Same-T",         # Same-T funds (help.topic_sitemap_body, one menu link)
    "API",            # API Lab / ES Lab (help.json already ships "API लैब")
    "LP",             # LP shares in the stake preview row (pool.shares_field
                       # already ships "LP शेयर")
    "CER",            # core exchange rate, named in explorer.feed_cer_premium;
                       # chunk-A declared the same acronym
    "Op",             # the operation-number prefixes (explorer.op_prefix) and
                       # the op badge - chunk-A declared both as loanwords
    "op",             # the " [op " badge prefix and the "op 19" family
    "Tx",             # the transaction-index prefix (explorer.tx_prefix) -
                       # 8 of the 10 other locales keep it too
    "Enter",          # a keyboard key, printed in Latin on the user's keyboard
                       # (market_net.canvas_label already ships
                       # "Enter दबाएँ")
    # --- service / platform names inside prose, never prose themselves
    "GitHub",         # the translation-problem report link
    "JavaScript",     # named in about.dlg_noscript
))
# Tokens that reached G9 only because the ENGLISH master of the same key already
# contains them. Nothing should land here permanently; the run prints whatever
# does so a reviewer can audit the distinction instead of trusting it. The ones
# this batch EXPECTS to land here are DATA - file paths (docs/vanilla-ui-dialog.md,
# index.html), platform API names (WebSocket, WebCrypto, BigInt), protocol
# spellings (localhost, http, https, LAN), the git branch label (Master) and
# the op-type ids carried inside the sitemap's link hashes (BTS_USD, api-lab,
# committee-account). Every one of them is a thing the reader must be able to
# copy out of the page, not a word to translate.
ENGLISH_SOURCE_FALLBACK = ()


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    A middle dot is clean when it is space-separated, as it is everywhere in
    this dictionary - or when both neighbours are alphanumeric, which is
    algebraic notation (hi.json ships the pool curve in prose). Anything else is
    a stray dot that will render as a different word to the reader.
    """
    hit = INVISIBLE.search(value)
    if hit:
        return hit.group(0)
    for i, ch in enumerate(value):
        if ch in DOT_CHARS:
            before = value[i - 1] if i else u" "
            after = value[i + 1] if i + 1 < len(value) else u" "
            if before == u" " and after == u" ":
                continue
            if before.isalnum() and after.isalnum():
                continue
            return ch
    return None


def edge_space(value):
    """Return the leading/trailing whitespace signature of a value."""
    return (len(value) - len(value.lstrip()),
            len(value) - len(value.rstrip()))


# --------------------------------------------------------------------------
# helpers + gates
# --------------------------------------------------------------------------
def flat(d, prefix=""):
    """Flatten a locale dict to dotted leaf keys, skipping _meta."""
    out = collections.OrderedDict()
    for k, v in d.items():
        if k == "_meta":
            continue
        if isinstance(v, dict):
            out.update(flat(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def deep_set(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def load(path):
    """Read a locale file keeping key order."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def check_batch(en_flat, key, value, problems, chars=True):
    """G1-G4, G4b, G7, G8 + punctuation hygiene for one key/value pair.

    `chars=False` runs every structural rule but leaves the character sweep to
    the caller; verify() uses it for the keys this batch does not own, where a
    stray character is a neighbour's finding to report, not this batch's.
    """
    master = en_flat[key]
    if sorted(PLACEHOLDER.findall(master)) != sorted(
        PLACEHOLDER.findall(value)
    ):
        problems.append("placeholder multiset changed: %s" % key)
    if sorted(BRACE.findall(master)) != sorted(BRACE.findall(value)):
        problems.append("brace placeholder changed: %s" % key)
    if IDENT.match(master) and master != value:
        problems.append("identifier not byte-verbatim: %s" % key)
    if key in PINNED and master != value:
        problems.append("pinned key not byte-verbatim: %s" % key)
    if master.count("\n") != value.count("\n"):
        problems.append(
            "line count changed: %s (en %d, hi %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if edge_space(master) != edge_space(value):
        problems.append(
            "edge whitespace changed: %s (en %r, hi %r)"
            % (key, edge_space(master), edge_space(value))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    if not chars:
        return
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_hi_hygiene(batch, en_flat, problems, fallback):
    """G7 + G7b + G9: script, apostrophes and undeclared Latin.

    Scoped to the values THIS BATCH writes. hi.json's other sections carry
    their own Latin tokens from earlier batches; re-auditing those here would
    make this file the owner of someone else's vocabulary.
    """
    for key, value in sorted(batch.items()):
        # Interpolations are substituted data, not prose: %(name)s and {s} must
        # never count as an undeclared loanword (G1 proves they survived).
        prose = PLACEHOLDER.sub("", value)
        prose = BRACE.sub("", prose)
        # A count keeping its English unit suffix ("24h", "360px", "4K") is data
        # the brief requires byte-verbatim, not prose.
        prose = COUNT_UNIT.sub("", prose)
        if APO_ASCII in value:
            problems.append("G7b: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7b: typographic apostrophe in %s" % key)
        if IDEO_SPACE in value:
            problems.append("G7b: ideographic space in %s" % key)
        hit = CYRILLIC.search(value)
        if hit:
            problems.append("G7: Cyrillic %r in %s" % (hit.group(0), key))
        hit = CJK.search(value)
        if hit:
            problems.append("G7: CJK %r in %s" % (hit.group(0), key))
        master_tokens = set(LATIN_TOKEN.findall(
            COUNT_UNIT.sub("", PLACEHOLDER.sub("", en_flat[key]))))
        for token in sorted(set(LATIN_TOKEN.findall(prose))):
            if token in LOAN:
                continue
            if token in master_tokens:
                fallback.append("%s: %s" % (key, token))
                continue
            problems.append("G9: undeclared Latin token %r in %s"
                            % (token, key))


def verify():
    """Structural re-proof of the shipped file against the en master."""
    hi, en = load(HI_PATH), load(EN_PATH)
    d, e = flat(hi), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: chunk-A owns them, and an
    # insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            check_batch(e, key, d[key], bad, chars=key in HI)
        if PLACEHOLDER.findall(e[key]):
            ph_filled += 1
            if sorted(PLACEHOLDER.findall(e[key])) == sorted(
                PLACEHOLDER.findall(d[key])
            ):
                ph_ok += 1
        if "\n" in e[key] or "\n" in d[key]:
            multi += 1
            if e[key].count("\n") == d[key].count("\n"):
                multi_ok += 1
        if LINK_HASH.findall(e[key]) or LINK_HASH.findall(d[key]):
            links += 1
            if LINK_HASH.findall(e[key]) == LINK_HASH.findall(d[key]):
                links_ok += 1
        hit = suspicious(d[key])
        if hit:
            where = ("suspicious code point U+%04X in %s"
                     % (ord(hit), key))
            (bad if key in HI else pre).append(where)
        hit = CYRILLIC.search(d[key])
        if hit:
            where = "Cyrillic %r in %s" % (hit.group(0), key)
            (bad if key in HI else pre).append(where)
        hit = CJK.search(d[key])
        if hit:
            where = "CJK %r in %s" % (hit.group(0), key)
            (bad if key in HI else pre).append(where)
    check_hi_hygiene(HI, e, bad, [])

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(HI) if d.get(k) == e.get(k)]
    for k in sorted(KEPT_ENGLISH):
        if d.get(k) != e.get(k) or d.get(k) != KEPT_ENGLISH[k]:
            bad.append("kept-english key drifted: %s" % k)
    by_section = {}
    for k in same + sorted(KEPT_ENGLISH):
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1
    scope_left = [
        k for k in sorted(e)
        if k.split(".")[0] in SECTIONS and d.get(k) == e[k]
        and k not in HI and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(HI) - len(same), len(HI)))
    print("  keys kept byte-identical to en on purpose: %d"
          % (len(KEPT_ENGLISH) + len(same)))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch              : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash    : %d (hashes ok: %d)"
          % (links, links_ok))
    for sec in sorted(by_section):
        print("    %-12s %d identical to en" % (sec, by_section[sec]))
    print("  keys in my sections still at en, not in this batch: %d"
          % len(scope_left))
    for k in scope_left:
        print("      %s = %r" % (k, d.get(k)))
    meta = hi.get("_meta", {})
    print("  _meta version=%r untranslated=%r translated=%d entries"
          % (meta.get("version"), meta.get("untranslated"),
             len(meta.get("translated", []))))
    honesty = sorted(k for k in e if k.startswith("i18n.") or ".confidence_" in k
                     or "translation" in k)
    print("  honesty-surface keys still identical to en: %d"
          % len([k for k in honesty if d.get(k) == e.get(k)]))
    for k in honesty:
        print("      %-46s %s" % (k, "ENGLISH" if d.get(k) == e.get(k)
                                  else "translated"))
    if pre:
        print("PRE-EXISTING, outside this batch (not touched, not fixed):")
        print("\n".join("  " + p for p in sorted(set(pre))))
    if bad:
        print("FAILURES:")
        print("\n".join(bad))
        return 1
    print("  all gates green")
    return 0


def main():
    argv = sys.argv[1:]
    if "--verify" in argv:
        return verify()
    apply = "--apply" in argv

    # G6: the on-disk formatting must survive a plain round trip, or this
    # script would reformat a file it is only supposed to fill.
    raw = open(HI_PATH, encoding="utf-8").read()
    hi = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(hi, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: hi.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(hi))
    before_meta = json.dumps(hi["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(HI.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in hi.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            continue  # already applied by an earlier run
        if cur != en_flat[key]:
            problems.append(
                "would overwrite a real translation: %s (%r)" % (key, cur)
            )
            continue
        check_batch(en_flat, key, value, problems)
        planned.append(key)
        deep_set(hi, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(HI) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (HI and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(HI) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in hi.json: %s" % key)
            return 1
        if value != en_flat[key]:
            print("REFUSING: kept-english value is not the English string: "
                  "%s (%r vs en %r)" % (key, value, en_flat[key]))
            return 1
    uncovered = sorted(
        k for k in en_flat
        if k.split(".")[0] in SECTIONS
        and k not in owned and before.get(k) == en_flat[k]
    )
    if uncovered:
        print("REFUSING: %d key(s) of my sections are in neither table: %s"
              % (len(uncovered), ", ".join(uncovered[:8])))
        return 1

    fallback = []
    check_hi_hygiene(HI, en_flat, problems, fallback)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(hi)
    for key in after:
        if key in planned:
            continue
        if after[key] != before.get(key):
            print("REFUSING: untouched key changed: %s" % key)
            return 1
    if set(after) != set(before):
        print("REFUSING: key set changed")
        return 1
    for key in PINNED:
        if key in after and after[key] != en_flat.get(key):
            print("REFUSING: pinned key drifted: %s" % key)
            return 1

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in planned if after[k] == en_flat[k]]
    by_section = {}
    for k in changed:
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1

    # G5b: _meta.translated is the v1 CLAIM "these keys are translated", and
    # tooling/check_i18n.py reads it in both directions - a claimed key that
    # still reads English is a false claim, and an unclaimed key that is no
    # longer English is an undeclared translation. So the claim moves in
    # lockstep with the bytes, for exactly the keys this batch translated. The
    # values kept byte-identical on purpose (loanwords, brands, ids, glue)
    # stay UNCLAIMED, which is the honest state for them. Nothing else in
    # _meta moves - filling strings is not verification.
    meta = hi["_meta"]
    meta_fields = set(meta)
    if meta.get("version") != 1 or meta.get("untranslated") is not False:
        print("REFUSING: _meta is not a v1 dict (version=%r untranslated=%r)"
              % (meta.get("version"), meta.get("untranslated")))
        return 1
    claimed = meta.get("translated")
    if (not isinstance(claimed, list)
            or any(not isinstance(k, str) for k in claimed)):
        print("REFUSING: _meta.translated is not a list of strings")
        return 1
    unknown = sorted(set(claimed) - set(en_flat))
    if unknown:
        print("REFUSING: _meta.translated names keys absent from en: %s"
              % ", ".join(unknown[:5]))
        return 1
    lie = sorted(k for k in claimed
                 if k in before and before[k] == en_flat[k])
    if lie:
        print("REFUSING: _meta.translated claims keys that still read "
              "English: %s" % ", ".join(lie[:5]))
        return 1
    added = sorted(k for k in HI
                   if after[k] != en_flat[k] and k not in claimed)
    meta["translated"] = sorted(set(claimed) | set(added))
    if claimed != sorted(claimed):
        print("REFUSING: _meta.translated was not sorted")
        return 1
    if set(meta) != meta_fields:
        print("REFUSING: _meta field set changed")
        return 1
    still_here = sorted(set(meta_fields) - {"translated"})
    if json.dumps(
        {k: meta[k] for k in still_here}, sort_keys=True, ensure_ascii=False
    ) != json.dumps(
        {k: json.loads(before_meta)[k] for k in still_here},
        sort_keys=True, ensure_ascii=False,
    ):
        print("REFUSING: _meta changed outside translated")
        return 1

    print("hi chunk-B: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    print("  LOAN allowlist (%d): %s" % (len(LOAN), ", ".join(sorted(LOAN))))
    if fallback:
        print("  G9 tokens that leaned on the ENGLISH SOURCE rather than on "
              "LOAN (%d distinct, audit these):" % len(set(fallback)))
        for item in sorted(set(fallback)):
            print("    %s" % item)
    else:
        print("  G9: no token needed the English-source fallback")
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue / "
              "sentinels - deliberately NOT claimed):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run - no files written (pass --apply)")
        return 0

    with open(HI_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(hi, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/hi.json")
    return 0


HI = {
    # ======================================================= honesty surface (6)
    # i18n.badge_body and i18n.risk_show_english are the confirmed probe run's
    # T20 / T19 answers UNCHANGED (tooling/probe_runs/hi-runB-nemotron3.json).
    # This is the warning a Hindi reader gets about their OWN Hindi, so it is
    # the one surface in the dictionary that must not be improvised: the exact
    # sentences that say "a machine wrote this, a human has not checked it, and
    # the English is one tap away" are the run's, byte for byte.
    "i18n.badge_body": (
        u"ये अनुवाद एक मशीन ने लिखे हैं और किसी मानव ने जाँच नहीं की। * से चिह्नित हर "
        u"पंक्ति पर अंग्रेज़ी एक टैप दूर।"
    ),
    "i18n.badge_details": u"इसका क्या अर्थ है",
    "i18n.badge_improve": u"इस अनुवाद को बेहतर बनाने हेतु सहायता करें",
    "i18n.badge_label": u"अनुवाद स्थिति: मशीन अनुवादित, मानव-सत्यापित नहीं",
    "i18n.risk_about_translations": u"इन अनुवादों के बारे में",
    "i18n.risk_show_english": u"इस पंक्ति का अंग्रेज़ी संदर्भ दिखाएँ",

    # =============================================================== help (38)
    # The confidence table. "विश्वसनीयता" (reliability) rather than a bare
    # "विश्वास" (trust), because the column rates how checked a language is.
    "help.confidence_good": u"अच्छा",
    "help.confidence_high": u"उच्च",
    "help.confidence_language": u"भाषा",
    "help.confidence_level": u"विश्वसनीयता",
    "help.confidence_moderate": u"मध्यम — कृपया सत्यापित करें",
    "help.translation_confidence_heading": u"हर भाषा कितनी विश्वसनीय है",
    "help.report_translation_link": u"अनुवाद की समस्या GitHub पर सूचित करें",
    "help.elastic": u"कम्युनिटी इंडेक्स (तृतीय-पक्ष हिस्ट्री)",
    "help.sitemap_sections": u"अनुभाग",
    "help.about_link": u"इस वॉलेट के बारे में",
    "help.topic_htlc_text": u"हैश-लॉक्ड स्वैप जो या तो भुगतान करते हैं या रिफ़ंड।",
    "help.topic_voting_text": (
        u"विटनेस, कमेटी, वर्कर को वोट दें — या प्रॉक्सी को सौंप दें।"
    ),
    # --- feed / issue teasers: same two-line shape as the English master
    "help.topic_assets-feed_title": u"मूल्य फ़ीड प्रकाशित करना",
    "help.topic_assets-feed_text": (
        u"उन बाज़ार-पेग्ड एसेट की मूल्य फ़ीड प्रकाशित करें जिनकी आप फ़ीड देते हैं।"
    ),
    "help.topic_assets-feed_body": (
        u"# मूल्य फ़ीड प्रकाशित करना\n"
        u"फ़ीड डेस्क से किसी बाज़ार-पेग्ड एसेट का सेटलमेंट मूल्य प्रकाशित करें; पुष्टि "
        u"संवाद हस्ताक्षर से पहले सटीक शुल्क दिखाता है।"
    ),
    "help.topic_assets-issue_title": u"एसेट जारी करना",
    "help.topic_assets-issue_text": (
        u"जारी डेस्क से अपने नियंत्रण के एसेट की नई आपूर्ति ढालें।"
    ),
    "help.topic_assets-issue_body": (
        u"# एसेट जारी करना\n"
        u"जारी डेस्क से अपने नियंत्रण के एसेट की नई आपूर्ति बनाएँ; राशियाँ एसेट की "
        u"परिशुद्धता का उपयोग करती हैं और पुष्टि संवाद हस्ताक्षर से पहले सटीक शुल्क "
        u"दिखाता है।"
    ),
    "help.topic_community_title": u"समुदाय",
    "help.topic_community_text": (
        u"BitShares के आसपास चैट, फ़ोरम, एक्सप्लोरर और कोड।"
    ),
    "help.topic_community_body": (
        u"# समुदाय\n"
        u"BitShares के आसपास के लोग व स्थान — होमपेज, कोड, एक्सप्लोरर, फ़ोरम और चैट "
        u"— समुदाय पेज पर हैं।"
    ),
    "help.topic_menu_title": u"साइट मेनू",
    "help.topic_menu_text": (
        u"इस वॉलेट का हर पृष्ठ, उसी तरह समूहित जैसे नेविगेशन मेनू समूहित करता है।"
    ),
    "help.topic_menu_body": (
        u"# साइट मेनू\n"
        u"मेनू पेज इस वॉलेट का हर स्क्रीन अनुभाग-दर-अनुभाग सूचीबद्ध करता है, ताकि कोई भी "
        u"डेस्क एक टैप दूर हो।"
    ),
    "help.topic_sitemap_title": u"साइट मैप",
    "help.topic_sitemap_text": (
        u"इस वॉलेट का हर पृष्ठ एक ही पेज पर: मेनू का हर पृष्ठ, साथ ही वे प्रवाह और "
        u"विवरण दृश्य जिनका कोई मेनू कार्ड नहीं।"
    ),
    "help.topic_about-making_title": u"इस वॉलेट का निर्माण",
    "help.topic_about-making_text": u"इस वॉलेट के पीछे की निर्माण कथा —",
    "help.topic_about-making_body": (
        u"# इस वॉलेट का निर्माण\n"
        u"आगे मूल निर्माण कथा दी गई है: इस वॉलेट को बनाने वाला हर प्रॉम्प्ट, 26 सितंबर "
        u"2026 को “acquire bitshares-ui” से लेकर 3 अक्टूबर के issue-1 सुधार तक, "
        u"निर्माताओं के उत्तरों सहित — बिना किसी बदलाव के सुरक्षित।\n"
        u"यह उन निर्णयों को दर्ज करती है जिन पर यह वॉलेट खड़ा है: issue #3583 और उसके "
        u"हज़ार-घंटे के जाल से बाहर निकलकर एक और React उन्नयन छोड़ना, ताकि यह वॉलेट "
        u"किसी रिलीज़-साइकल वाली चीज़ पर निर्भर न रहे; पुराने वॉलेट की तरह हर लेनदेन "
        u"स्वयं स्थानीय रूप से हस्ताक्षरित करना, उसे बाहर सौंपने के बजाय; तीन थीम, "
        u"जिनमें क्लासिक रूप मानक है; संख्याएँ मानव पदों में, कभी कच्चे चेन पूर्णांक "
        u"नहीं; पहली स्लाइस से ही फ़ोन-प्रथम लेआउट; और शुल्क लाइव चेन से पढ़े गए, कभी "
        u"अनुमानित नहीं। इसे इतिहास की तरह पढ़ें: वॉलेट इसी तरह बना।\n"
        u"# पूर्ण संवाद संग्रह\n"
        u"पूरा एक्सचेंज-दर-एक्सचेंज रिकॉर्ड परिचय पेज (#/about) पर है। सभी एक्सचेंज "
        u"देखने, कीवर्ड से छानने, या किसी एक्सचेंज तक गहरा लिंक बनाने हेतु वहाँ “पूर्ण बिल्ड "
        u"संवाद” अनुभाग फैलाएँ — ?dialog=N के साथ।"
    ),
    # --- the long-form articles. Line count and heading structure are the
    # contract the help renderer depends on (G4), so each stays 1:1.
    "help.topic_backups_body": (
        u"# जल्दी बैकअप लें, दो बार बैकअप लें\n"
        u"धन जमा करने से पहले अपने स्थानीय वॉलेट का बैकअप लें — आगे के लिए एक बैकअप "
        u"आमतौर पर पर्याप्त है, पर उसे कम से कम दो सुरक्षित स्थानों में रखें जहाँ "
        u"केवल आप पहुँच सकें।\n"
        u"इस वॉलेट में कोई बैकअप फ़ाइल नहीं है: आपकी ब्रेनकी ही बैकअप है, और केवल "
        u"पासफ़्रेज़ से कुछ भी पुनर्प्राप्त नहीं होता। शब्दों और पासफ़्रेज़ दोनों के "
        u"बिना आपके धन चले गए। पासफ़्रेज़ को कभी शब्दों के साथ न रखें।\n"
        u"# आपकी ब्रेनकी ही बैकअप है\n"
        u"यदि आपने कभी कच्ची कुंजियाँ हाथ से आयात नहीं कीं, तो आपका पूरा वॉलेट एक ही "
        u"ब्रेनकी — शब्दों की एक श्रृंखला — से निश्चित रूप से निर्धारित होता है। ब्रेनकी "
        u"लिखकर आप उस वॉलेट का हर खाता व हर धन बैकअप कर लेते हैं।\n"
        u"वॉलेट प्रबंधक में इसे देखें और कागज़ पर उतारें, जिसे किसी भी डिजिटल चीज़ से "
        u"अलग रखा जाए। संदर्भ-वॉलेट की .bin फ़ाइलें यहाँ आयात नहीं हो सकतीं — वॉलेट यह "
        u"स्क्रीन पर ही कहता है, और कोई फ़ाइल डाउनलोड मौजूद नहीं है।\n"
        u"# उन्नत: स्तरित अथॉरिटी\n"
        u"यदि आप सादी कुंजियों के बजाय भारित बहु-खाता अथॉरिटी प्रयोग करते हैं, तो केवल "
        u"कुंजी बैकअप पहुँच बहाल न कर सकता — अथॉरिटी संरचना स्वयं महत्त्वपूर्ण है।\n"
        u"अनुमति लेख फिर पढ़ें और पूरा अथॉरिटी ढाँचा दर्ज करें, केवल शब्द नहीं।"
    ),
    "help.topic_wallets_body": (
        u"# स्थानीय तिजोरी वाला वेब ऐप\n"
        u"यह एप्लिकेशन आपके ब्राउज़र में चलता है और नेटवर्क के प्रवेश-द्वार के रूप "
        u"में एक चेन नोड से बात करता है। हर रहस्य आपके ब्राउज़र की स्थानीय तिजोरी में "
        u"रहता है।\n"
        u"# कोई क्लाउड लॉगिन नहीं\n"
        u"इस वॉलेट में उपयोगकर्ता-नाम-और-पासवर्ड लॉगिन नहीं है: यहाँ हर वॉलेट एक ही "
        u"ब्राउज़र का स्थानीय है। नए ब्राउज़र या कंप्यूटर पर अपना खाता चलाने हेतु उसी "
        u"ब्रेनकी से शुरू करें — कोई अनुमति-पत्र अकेले आपको कहीं से नहीं खोलता।\n"
        u"# स्थानीय वॉलेट\n"
        u"स्थानीय वॉलेट एक ही विशिष्ट ब्राउज़र के भीतर का डेटाबेस है। जब तक आप ब्रेनकी "
        u"साथ लेकर न जाएँ व उसी आयात न करें, यह दूसरे कंप्यूटर या ब्राउज़र तक आपका "
        u"पीछा नहीं चलेगा।\n"
        u"वास्तविक धन हेतु स्थानीय वॉलेट पर भरोसा करने से पहले बैकअप लेख पढ़ें।\n"
        u"# पासवर्ड अनुशासन\n"
        u"पासवर्ड तिजोरी एन्क्रिप्ट करता है। छोटे या दोहराए गए पासवर्ड अनुमान से टूट "
        u"जाते हैं; कागज़ पर लिखा अद्वितीय पासफ़्रेज़ नहीं।\n"
        u"पासवर्ड बदलने से सब कुछ पुनः एन्क्रिप्ट होता है — पहले मौजूदा वाला "
        u"सत्यापित करें, फिर जाने से पहले पुष्टि करें कि वॉलेट अब भी अनलॉक होता है।"
    ),
    "help.topic_browser_title": u"ब्राउज़र समर्थन",
    "help.topic_browser_text": (
        u"वे ब्राउज़र जो वॉलेट चलाते हैं, और संगतता सूचना का क्या अर्थ है।"
    ),
    "help.topic_browser_body": (
        u"# पहचानी गई सुविधाएँ, कभी ब्रांड नाम नहीं\n"
        u"यह वॉलेट कभी नहीं पूछता कि आप कौन-सा ब्राउज़र चला रहे हैं — यह चार "
        u"प्लेटफ़ॉर्म सुविधाएँ जाँचता है जिनकी उसे सचमुच आवश्यकता है: WebSocket (चेन "
        u"डेटा), WebCrypto (कुंजी-भंडार), BigInt (धन गणित), और स्थानीय भंडारण "
        u"(सेटिंग्स)। चुप रहना ही पास है: आधुनिक ब्राउज़र पर कोई बैनर न दिखना यानी सब "
        u"कुछ मौजूद है।\n"
        u"# सबसे सामान्य कारण: असुरक्षित संदर्भ\n"
        u"आधुनिक ब्राउज़र WebCrypto केवल सुरक्षित संदर्भों में उपलब्ध कराते हैं: "
        u"https पेज, localhost, और खोली गई फ़ाइलें। वही ताज़ा ब्राउज़र सादे http से "
        u"परोसा जाए (उदाहरणतः कोई LAN पता) तो WebCrypto अनुपलब्ध बताता है — ब्राउज़र "
        u"ठीक है, पता नहीं। फ़ोल्डर को https या localhost से परोसें, या index.html "
        u"सीधे खोलें।\n"
        u"# फिर भी क्या चलता है\n"
        u"ब्राउज़ करना हमेशा चलता है: बैलेंस, मार्केट, एक्सप्लोरर और वोटिंग सार्वजनिक "
        u"चेन डेटा पढ़ते हैं, वॉलेट सुविधाओं की ज़रूरत नहीं। केवल स्थानीय हस्ताक्षर को "
        u"नकली हिस्सा चाहिए। सूचना हटाने से वह इस मशीन पर छिप जाती है; यह किसी पेज को "
        u"कभी अवरुद्ध नहीं करती।"
    ),
    # --- the honesty article. The phrases the brief names as load-bearing
    # (मशीन, मानव जाँच) are used here and in the i18n badge, in the same
    # register, so the header chip and this article say the same thing.
    "help.topic_translation-limitations_title": u"अनुवाद सीमाएँ",
    "help.topic_translation-limitations_text": (
        u"मशीन-भरे अनुवाद चिह्नित हैं; अंग्रेज़ी संदर्भ हमेशा एक टैप दूर है। किसी पंक्ति "
        u"को सुधारने हेतु हमारी सहायता करें।"
    ),
    "help.topic_translation-limitations_body": (
        u"मशीन-भरा चिह्नित अनुवाद एक मशीन ने लिखा है। किसी ने इसे पढ़कर यह जाँचा नहीं "
        u"कि यह वही कहता है जो अंग्रेज़ी कहती है — इसीलिए अंग्रेज़ी को छोड़कर हर भाषा "
        u"इस वॉलेट के हेडर में चिह्न चिप वहन करती है। अंग्रेज़ी वही पाठ है जिससे अन्य "
        u"अनुवाद बने, इसलिए उस पर कोई चिह्न नहीं।\n"
        u"\n"
        u"# पंक्ति पर * का क्या अर्थ है\n"
        u"हस्ताक्षर पंक्ति पर * का एक साथ दो अर्थ हैं: शब्द-चयन मशीन ने भरा है, और "
        u"मूल अंग्रेज़ी एक टैप दूर है। * दबाएँ और अंग्रेज़ी पंक्ति के ठीक नीचे वही रूप "
        u"में दिखेगी जैसे इस वॉलेट का अंग्रेज़ी मास्टर उसे रखता है — वही पाठ जिससे हर "
        u"अन्य भाषा अनुवाद हुई, उसका पुनर्लेखन नहीं।\n"
        u"\n"
        u"चिह्न पंक्ति के साथ चलता है, उसके भीतर के शब्दों के साए नहीं। * एक पूरी "
        u"अनुवादित पंक्ति चिह्नित करता है, और वॉलेट ये पंक्तियाँ एक निश्चित नियम से "
        u"चुनता है: हस्ताक्षर, अपरिवर्तनीय-क्रिया या पुनर्प्राप्ति स्क्रीन की हर पंक्ति — "
        u"एक लंबाई-सीमा तक, क्योंकि लंबा अनुच्छेद इसी लेख द्वारा आवृत है — साथ ही वह "
        u"कोई भी पंक्ति जिसका अंग्रेज़ी में खतरे का शब्द-चयन हो। इसलिए केवल id या राशि "
        u"बताने वाली पंक्ति भी वह चिह्न रखती है (ट्रांसफर का To फ़ील्ड, उदाहरणतः), और "
        u"id का उल्लेख करने वाला लंबा अनुच्छेद नहीं रखता। एक नंगा चेन मान — सेल में राशि, "
        u"कॉलम में id, एसेट प्रतीक — अनुवादित पंक्ति है ही नहीं, इसलिए वह कभी चिह्न "
        u"नहीं रखता: उसके पीछे तुलना हेतु कोई अंग्रेज़ी शब्द-चयन होता ही नहीं।\n"
        u"\n"
        u"# विश्वसनीयता स्तरों का क्या अर्थ है\n"
        u"इस वॉलेट के साथ आने वाली हर भाषा का एक रेटिंग है, नीचे दी गई तालिका में "
        u"सूचीबद्ध। उच्च का अर्थ है कि शब्द-चयन अंग्रेज़ी का निकटता से पीछा चलता है और "
        u"स्वाभाविक लगता है। अच्छा का अर्थ है कि यह उपयोग्य है, यद्यपि कोई वाक्यांश अब "
        u"भी अटप-अटप लग सकता है। मध्यम का अर्थ है कि इसे मसौदा मानकर पढ़ें और उस पर भरोसा "
        u"करने से पहले अंग्रेज़ी जाँच लें।\n"
        u"\n"
        u"नीचे हर रेटिंग वही मशीन देती है जिसने शब्द लिखे, अपना ही काम अंकित कर रही है; "
        u"किसी स्वतंत्र मानव ने उनकी जाँच नहीं की। रेटिंग बताती है कि अब तक क्या जाँचा "
        u"गया, भाषा के समग्र रूप में न कि पंक्ति-दर-पंक्ति। अंग्रेज़ी स्वयं संदर्भ है: "
        u"यह हाथ से लिखी जाती है, और हर अन्य भाषा इसी से अनुवादित है।\n"
        u"\n"
        u"# किसी शब्द-पंक्ति को सही कैसे करें\n"
        u"सुधार सूचना से शुरू होते हैं। बताएँ कि पंक्ति किस भाषा में थी, वह key दें जो "
        u"वह पंक्ति उजागर करती है, अंग्रेज़ी चिपकाएँ जो उसे कहना था, और वह शब्द-चयन "
        u"सुझाएँ जो आप उसके बजाय प्रयोग करते।\n"
        u"\n"
        u"- प्रति पंक्ति एक सूचना सुधार को लागू करना सरल रखती है।\n"
        u"- पहले हस्ताक्षर स्क्रीनों की सूचना दें: पुष्टि संवाद का कोई ग़लत वाक्य "
        u"सबसे महँगी किस्म की ग़लती है।\n"
        u"- इस लेख के अंत का लिंक प्रयोग करें। यह इस परियोजना के ट्रैकर पर अनुवादों "
        u"हेतु पहले से लेबल किया गया एक मुद्दा खोलता है, इसलिए कुछ भी दोबारा टाइप नहीं "
        u"करना पड़ता।\n"
        u"\n"
        u"# मानव-परीक्षित होने का एकमात्र रास्ता सुधार है\n"
        u"शब्द-पंक्ति को मशीन-भरा छोड़ने का कोई और कारण नहीं: न भाषा की उपयोग-आवृत्ति, "
        u"न दूसरी मशीन की पहली से सहमति, न अनुवाद-स्मृति। कोई शब्द-पंक्ति तब "
        u"मानव-परीक्षित बनती है जब कोई व्यक्ति उसे अपनी भाषा में पढ़कर स्वीकार करता है, "
        u"और कोई पंक्ति उसी भाषा हेतु मानव-परीक्षित होती है जिसकी वास्तव में जाँच हुई।\n"
        u"\n"
        u"तब तक चिह्न वहीं रहता है जहाँ है। ऐसा अनुवाद जिसे किसी ने नहीं पढ़ा, किसी "
        u"अनुवाद के न होने से बेहतर है, पर वह उसी बात के बराबर नहीं जिसके पीछे कोई "
        u"व्यक्ति खड़ा हो।"
    ),
    # --- the site map: 83 lines, 60 markdown links, seven section headings.
    # Every label is translated; every (#/hash) is byte-identical (G4). The
    # section headings mirror the burger-menu grouping keys this batch also
    # writes (menu.section_*), so the two never drift apart.
    "help.topic_sitemap_body": (
        u"इस वॉलेट का हर पृष्ठ, उसी तरह समूहित जैसे बर्गर मेनू समूहित करता है। "
        u"लिंक वाला कुछ भी सीधे खुलता है; बिना मेनू कार्ड वाले पेजों के नीचे सूचीबद्ध "
        u"विवरण दृश्य अपने मूल पृष्ठों से खुलते हैं।\n"
        u"# वॉलेट\n"
        u"- [डैशबोर्ड](#/)\n"
        u"- [मेरा खाता](#/account/me)\n"
        u"- [खाते](#/accounts)\n"
        u"- [ट्रांसफर](#/transfer)\n"
        u"- [चालान](#/invoice)\n"
        u"- [वेस्टिंग](#/vesting)\n"
        u"- [वॉलेट](#/wallet)\n"
        u"- [वॉलेट पासवर्ड बदलें](#/wallet/password)\n"
        u"- [वॉलेट बनाएँ (ब्रेनकी)](#/create-wallet-brainkey)\n"
        u"- [मौजूदा खाता आयात करें](#/existing-account)\n"
        u"- [नया खाता पंजीकृत करें](#/create-account)\n"
        u"- [लॉगिन](#/login)\n"
        u"- [पंजीकरण](#/registration)\n"
        u"- [रेफ़रल](#/referrals)\n"
        u"# ट्रेड\n"
        u"- [एक्सचेंज](#/markets)\n"
        u"- [त्वरित ट्रेड](#/instant-trade)\n"
        u"- [तरलता पूल](#/pools)\n"
        u"- [क्रॉस दरें](#/cross-rates)\n"
        u"- [उधार](#/borrow)\n"
        u"- [बार्टर](#/barter)\n"
        u"- [जमा / निकासी](#/deposit-withdraw)\n"
        u"- [Same-T फंड](#/samet)\n"
        u"- [स्पॉटलाइट](#/spotlight)\n"
        u"# कमाएँ और सुरक्षित करें\n"
        u"- [क्रेडिट ऑफ़र](#/credit-offer)\n"
        u"- [डायरेक्ट डेबिट](#/direct-debit)\n"
        u"- [HTLC](#/htlc)\n"
        u"- [टिकट](#/tickets)\n"
        u"- [एयरड्रॉप](#/airdrop)\n"
        u"- [कस्टम अथॉरिटी](#/authorities)\n"
        u"- [खाता सूचियाँ](#/lists)\n"
        u"# शासन\n"
        u"- [वोटिंग](#/voting)\n"
        u"- [प्रस्ताव](#/proposals)\n"
        u"- [वर्कर बनाएँ](#/create-worker)\n"
        u"- [भविष्यवाणी मार्केट](#/prediction)\n"
        u"# खोजें\n"
        u"- [एक्सप्लोर करें](#/explorer)\n"
        u"- [एसेट्स](#/assets)\n"
        u"- [एसेट बनाएँ](#/assets/create)\n"
        u"- [एसेट जारी करें](#/assets/issue)\n"
        u"- [फ़ीड प्रकाशित करें](#/assets/feed)\n"
        u"- [नेटवर्क शुल्क](#/explorer/fees)\n"
        u"- [ऑपरेशन](#/ops)\n"
        u"- [शीर्ष ऑपरेशन](#/top-ops)\n"
        u"- [समाचार](#/news)\n"
        u"# एक्सप्लोर करें\n"
        u"- [एक्सप्लोर करें (ब्लॉकचेन)](#/explorer)\n"
        u"- [एसेट्स](#/explorer/assets)\n"
        u"- [पूल](#/explorer/pools)\n"
        u"- [खाते](#/explorer/accounts)\n"
        u"- [विटनेस](#/explorer/witnesses)\n"
        u"- [कमेटी](#/explorer/committee)\n"
        u"- [मार्केट](#/explorer/markets)\n"
        u"- [शुल्क](#/explorer/fees)\n"
        u"- [फ़ीड](#/explorer/feeds)\n"
        u"# लैब\n"
        u"- [API लैब](#/api-lab)\n"
        u"- [ES लैब](#/es-lab)\n"
        u"- [लेनदेन निर्माता](#/txbuilder)\n"
        u"- [खाता नेटवर्क](#/account-network)\n"
        u"# व्यक्तिगत\n"
        u"- [ट्रॉलबॉक्स](#/trollbox)\n"
        u"- [पसंदीदा](#/favourites)\n"
        u"- [मूल्य अलर्ट](#/alerts)\n"
        u"- [सहायता](#/help)\n"
        u"- [अनुवाद सीमाएँ](#/help/translation-limitations)\n"
        u"- [परिचय](#/about)\n"
        u"- [समुदाय](#/community)\n"
        u"- [सेटिंग्स](#/settings)\n"
        u"# बिना मेनू कार्ड वाले पेज\n"
        u"पंजीकरण के रूपांतरण, खाता व मार्केट डेस्क, और विवरण दृश्य ऊपर के पृष्ठों से या "
        u"वॉलेट में कहीं और के लिंक से खुलते हैं।\n"
        u"- [स्थानीय पंजीकरण](#/registration/local)\n"
        u"- [क्लाउड पंजीकरण](#/registration/cloud)\n"
        u"- [उदाहरण खाता पृष्ठ](#/account/committee-account)\n"
        u"- [उदाहरण मार्केट डेस्क](#/market/BTS_USD)\n"
        u"- [उदाहरण एसेट पृष्ठ](#/asset/BTS)\n"
        u"- [उदाहरण पूल डेस्क](#/pools/1.19.66)\n"
        u"- [मेनू अवलोकन](#/menu)\n"
        u"किसी विशेष क्रेडिट ऑफ़र, डील, प्रस्ताव, ब्लॉक, लेनदेन, HTLC, भविष्यवाणी "
        u"मार्केट, ट्रांसफर प्राप्तकर्ता, चालान, गेटवे, सेटिंग्स टैब, एक्सप्लोरर टैब, या "
        u"सहायता लेख के विवरण दृश्य अपने मूल पृष्ठों से खुलते हैं और पते में id या नाम "
        u"लेते हैं।"
    ),

    # =============================================================== menu (9)
    "menu.blurb_labs": u"चेन व नोड कार्य हेतु प्रभावी औज़ार।",
    "menu.blurb_personal": u"चैट, अलर्ट और आपकी सेटिंग्स।",
    "menu.d_account_net": u"ट्रांसफर ट्रैकिंग",
    "menu.d_xrates": u"हर एसेट के पूल मूल्य, BTS तथा अन्य में।",
    "menu.p_account_net": u"खाता नेटवर्क",
    "menu.p_xrates": u"क्रॉस दरें",
    "menu.section_explore": u"खोजें",
    "menu.section_labs": u"लैब",
    "menu.section_personal": u"व्यक्तिगत",

    # ============================================================== shell (11)
    # See the module header on the Master-link DOM order. These are direction
    # fragments, not clauses: Hindi puts its case postposition after the noun,
    # and the branch link is always appended after this string.
    "shell.footer_ahead": u"%(n)s कमिट आगे",
    "shell.footer_ahead_one": u"1 कमिट आगे",
    "shell.footer_at_build": u"बिल्ड %(date)s पर",
    "shell.footer_behind": u"%(n)s कमिट पीछे",
    "shell.footer_behind_one": u"1 कमिट पीछे",
    "shell.footer_dahead": u"%(n)s आगे",
    "shell.footer_dbehind": u"%(n)s पीछे",
    "shell.footer_diverged": u"विचलित",
    "shell.footer_offbranch": u"अन्य शाखा",
    "shell.footer_sync": u"सिंक में",
    "shell.report": u"रिपोर्ट",

    # ============================================================ explorer (16)
    "explorer.assets_mode_all": u"सभी",
    "explorer.assets_mode_market": u"स्मार्टकॉइन",
    "explorer.assets_mode_prediction": u"भविष्यवाणी",
    "explorer.assets_mode_user": u"यूज़र-जारी",
    "explorer.assets_of": u"का",
    "explorer.assets_showing": u"दिखाया जा रहा है",
    "explorer.core_suffix": u" (कोर)",
    "explorer.feed_cer_premium": (
        u"कोर एक्सचेंज दर (CER) प्रीमियम (प्रकाशक-नियम अनुमान)"
    ),
    "explorer.feeds_of": u"का",
    "explorer.feeds_scanned_suffix": u"स्कैन किए गए (पहले 100 एसेट)",
    "explorer.feeds_showing": u"दिखाया जा रहा है",
    "explorer.no_assets_match": u"“%(q)s” से मेल खाता कोई एसेट नहीं।",
    "explorer.raw_mark": u" (कच्चा)",
    "explorer.stat_tpb": u"लेनदेन/ब्लॉक",
    "explorer.stat_tps": u"लेनदेन/सेकंड",
    "explorer.virtual_mark": u" (आभासी)",

    # ================================================================ pool (25)
    "pool.asset_1_field": u"एसेट 1 (कोई भी पक्ष)",
    "pool.asset_2_field": u"एसेट 2 (कोई भी पक्ष)",
    "pool.clear_btn": u"साफ़ करें",
    "pool.delete_not_empty": (
        u"खाली नहीं — हटाने से पहले %(legs)s का मान 0 होना चाहिए।"
    ),
    "pool.direct_hit": u"सीधी पूल खोज — पेजर छिपा।",
    "pool.map_core_self": u"BTS बिटशेयर्स का कोर टोकन है",
    "pool.min_swaps": u"न्यूनतम स्वैप",
    "pool.my_swaps_hint": (
        u" ऊपर के स्वैप पैनल से एक चलाएँ — इस पूल में आपके स्वैप यहाँ सूचीबद्ध होते हैं।"
    ),
    "pool.no_filter_match": u"इन छननियों से कोई स्वैप मेल नहीं खाता।",
    "pool.share_or_pool_hint": u"प्रतीक, 1.3.x, या पूल 1.19.x",
    "pool.stake_autofill_hint": (
        u"एक राशि लिखें — दूसरी पूल अनुपात पर स्वतः भरेगी।"
    ),
    "pool.stake_preview_bad": u"राशियाँ जाँचें — कोई शेयर अनुमान नहीं।",
    "pool.stake_preview_need_both": u"शेयर अनुमान हेतु दोनों राशियाँ दर्ज करें।",
    "pool.stake_preview_unavailable": u"शेयर अनुमान उपलब्ध नहीं (ऑफ़लाइन)।",
    "pool.stake_ratio_empty": u"पूल खाली है — दोनों राशियाँ हाथ से दर्ज करें।",
    "pool.stake_ratio_row": u"अनुपात (स्पॉट)",
    "pool.stake_shares_row": u"अनुमानित LP शेयर",
    "pool.swap_desk": u"स्वैप डेस्क",
    "pool.swap_mkt_preview_dash": u"मार्केट शुल्क (पूर्वावलोकन): —",
    "pool.swap_mkt_row": u"मार्केट शुल्क",
    "pool.swap_preview": u"कोट (पूर्वावलोकन): ",
    "pool.swap_preview_dash": u"कोट (पूर्वावलोकन): —",
    "pool.swaps_hint": (
        u" इस पूल में पहली एक्सचेंज के बाद स्वैप दिखेंगे — ऊपर के स्वैप पैनल से एक "
        u"चलाएँ।"
    ),
    "pool.uc_action": u"क्रिया",
    "pool.uc_title": u"जारी रखने हेतु अनलॉक करें",

    # ============================================================ pool_net (27)
    "pool_net.canvas_label": u"पूल नेटवर्क मानचित्र। BTS खोलने हेतु Enter दबाएँ।",
    "pool_net.col_a": u"एसेट 1",
    "pool_net.col_b": u"एसेट 2",
    "pool_net.col_pool": u"पूल",
    "pool_net.collapse": u"संकुचित करें",
    "pool_net.direct": u"BTS के साथ जोड़ा",
    "pool_net.empty": u"इस छननी से कोई पूल नहीं जुड़ता।",
    "pool_net.expand": u"विस्तार करें",
    "pool_net.hops": u"%(n)s हॉप BTS तक",
    "pool_net.legend": u"ब्रांड",
    "pool_net.loading": u"नेटवर्क लोड हो रहा है…",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s पूल · %(hops)s",
    "pool_net.offline": (
        u"नेटवर्क अनुपलब्ध — भेजा गया स्केलेटन दिखाया जा रहा है। जुड़ने पर पुनः "
        u"प्रयास करें।"
    ),
    "pool_net.offline_empty": (
        u"नेटवर्क अनुपलब्ध — कोई स्केलेटन पूल कैश नहीं।"
    ),
    "pool_net.orphan": u"BTS से अनाथ",
    "pool_net.partial": (
        u"लाइव अद्यतन अपूर्ण — भेजे गए पूल दिखाए जा रहे हैं।"
    ),
    "pool_net.phys": u"भौतिकी",
    "pool_net.prompt": u"एसेट हेतु नोड पर, पूल हेतु लाइन पर टैप करें।",
    "pool_net.ramp": u"पूल आकार: छोटा → बड़ा",
    "pool_net.ready": u"%(pools)s पूल · %(assets)s एसेट्स",
    "pool_net.title": u"पूल नेटवर्क",
    "pool_net.twin": u"पूल पंक्तियाँ (%(n)s)",
    "pool_net.twin_more": (
        u"%(n)s पूलों में से %(shown)s दिखाई जा रही हैं — कम देखने हेतु छननी संकीर्ण "
        u"करें।"
    ),
    "pool_net.verdict_full": u"%(pools)s पूल · %(assets)s एसेट्स",
    "pool_net.verdict_orphan": u"%(a)s और %(b)s के बीच कोई मार्ग नहीं",
    "pool_net.verdict_path": u"%(a)s, %(n)s हॉप में %(b)s तक पहुँचता है",
    "pool_net.verdict_star": u"%(s)s से जुड़े पूल: %(n)s",

    # ================================================================ seo (26)
    # Meta titles keep "BitShares" in Latin (zh, ja, de, ru and pt all do);
    # "Wallet" is translated because the rest of the dictionary translates it.
    "seo.title_about": u"परिचय — BitShares वॉलेट",
    "seo.desc_about": (
        u"इस BitShares वॉलेट के बारे में — स्थानीय कुंजियाँ, कोई पंजीकरण नहीं, "
        u"कोई ट्रैकिंग नहीं। निःशुल्क ब्राउज़ करें और स्थानीय रूप से हस्ताक्षर करें।"
    ),
    "seo.title_account": u"खाता %(name)s — BitShares वॉलेट",
    "seo.desc_account": (
        u"यह BitShares खाता देखें — बैलेंस, ऑर्डर व हिस्ट्री चेन से लाइव पढ़ी जाती "
        u"हैं। लॉगिन की आवश्यकता नहीं।"
    ),
    "seo.title_account_net": u"खाता नेटवर्क — BitShares वॉलेट",
    "seo.desc_account_net": (
        u"देखें कि कोई खाता किसे भेजता है, किसे उधार देता है और किससे उधार लेता है — "
        u"कम्युनिटी इंडेक्स से पठन। लॉगिन की आवश्यकता नहीं।"
    ),
    "seo.title_dashboard": u"डैशबोर्ड — BitShares वॉलेट",
    "seo.desc_dashboard": (
        u"BitShares डैशबोर्ड — बैलेंस, मार्केट व चेन गतिविधि एक नज़र में। निःशुल्क "
        u"ब्राउज़ करें; कुंजियाँ आपके डिवाइस पर ही रहती हैं।"
    ),
    "seo.title_explorer": u"ब्लॉकचेन एक्सप्लोरर — BitShares वॉलेट",
    "seo.desc_explorer": (
        u"BitShares ब्लॉक, लेनदेन व एसेट देखें — लाइव चेन डेटा, बिना लॉगिन ब्राउज़ "
        u"योग्य।"
    ),
    "seo.title_help": u"सहायता — BitShares वॉलेट",
    "seo.desc_help": (
        u"BitShares वॉलेट सहायता — खातों, ट्रेडिंग, वोटिंग व पुनर्प्राप्ति हेतु "
        u"मार्गदर्शिकाएँ। अटकने पर यहाँ से शुरू करें।"
    ),
    "seo.title_login": u"लॉगिन — BitShares वॉलेट",
    "seo.desc_login": (
        u"अपना स्थानीय BitShares वॉलेट अनलॉक करें — पासवर्ड, ब्रेनकी या आयात "
        u"की गई कुंजियाँ। कुंजियाँ इस डिवाइस से कभी नहीं निकलतीं।"
    ),
    "seo.title_market": u"BTS/USD एक्सचेंज — BitShares वॉलेट",
    "seo.desc_market": (
        u"BitShares ऑर्डर बुक पर BTS से USD की ट्रेड करें — लाइव बोली, माँग व "
        u"हिस्ट्री, आपके डिवाइस पर स्थानीय रूप से हस्ताक्षरित।"
    ),
    "seo.title_markets": u"मार्केट — BitShares वॉलेट",
    "seo.desc_markets": (
        u"24h मात्रा के अनुसार BitShares ऑर्डर-बुक मार्केट देखें और किसी भी जोड़े का "
        u"ट्रेडिंग डेस्क खोलें। लॉगिन की आवश्यकता नहीं।"
    ),
    "seo.title_pools": u"तरलता पूल — BitShares वॉलेट",
    "seo.desc_pools": (
        u"BitShares तरलता पूल देखें — जोड़े, बैलेंस व गतिविधि चेन से लाइव पढ़ी जाती "
        u"हैं। लॉगिन की आवश्यकता नहीं।"
    ),
    "seo.title_transfer": u"धन भेजें — BitShares वॉलेट",
    "seo.desc_transfer": (
        u"किसी भी खाते को BitShares एसेट भेजें। हर फ़ील्ड की समीक्षा करें, फिर "
        u"स्थानीय रूप से हस्ताक्षर करें — कुंजियाँ आपके डिवाइस से कभी नहीं निकलतीं।"
    ),
    "seo.title_voting": u"विटनेस को वोट दें — BitShares वॉलेट",
    "seo.desc_voting": (
        u"BitShares विटनेस, कमेटी सदस्य व वर्कर हेतु वोट दें। प्रत्येक मत आपके "
        u"डिवाइस पर स्थानीय रूप से हस्ताक्षरित है।"
    ),
    "seo.title_xrates": u"क्रॉस दरें — BitShares वॉलेट",
    "seo.desc_xrates": (
        u"प्रत्येक पूल एसेट अंतिम स्वैप मूल्यों पर BTS तथा अन्य में निर्धारित। "
        u"लॉगिन की आवश्यकता नहीं।"
    ),

    # ============================================================== splash (20)
    "splash.hero_title": (
        u"आपके ब्राउज़र में BitShares वॉलेट — इंस्टॉल करने हेतु कुछ नहीं।"
    ),
    "splash.hero_sub": u"आपकी कुंजियाँ। आपके धन, ऑन-चेन।",
    "splash.hero_sub2": u"मार्केट निःशुल्क देखें। केवल हस्ताक्षर हेतु अनलॉक करें।",
    "splash.cta_exchange": u"एक्सचेंज पर ट्रेड करें",
    "splash.pulse_title": u"लाइव चेन संख्याएँ",
    "splash.pulse_time": u"हेड समय",
    "splash.pulse_stale": u"— पुराना",
    "splash.topvol_unavailable": (
        u"शीर्ष-मार्केट मात्रा ऑफ़लाइन है — सेटिंग्स → नोड्स जाँचें।"
    ),
    "splash.cards_title": u"ट्रेड करें, पूल बनाएँ, एक्सप्लोर करें — यहाँ से शुरू करें",
    "splash.card_dex_d": u"खुले बाज़ार में खरीदें और बेचें।",
    "splash.card_pool_d": u"दो एसेट को पूल करके आय का हिस्सा कमाएँ।",
    "splash.card_explore_d": u"ब्लॉक और खाता हिस्ट्री पढ़ें।",
    "splash.card_wallet_d": u"कुंजियाँ केवल इसी डिवाइस पर रखें।",
    "splash.trust_keys_d": (
        u"हस्ताक्षर आपके डिवाइस पर स्थानीय रूप से होते हैं। कोई सर्वर कभी पासवर्ड या "
        u"कुंजी नहीं देखता।"
    ),
    "splash.step1_t": u"घूमकर देखें",
    "splash.step1_d": u"लॉगिन की आवश्यकता नहीं — पहले चेन देखें।",
    "splash.step2_t": u"वॉलेट बनाएँ",
    "splash.step2_d": (
        u"ब्रेनकी इसी डिवाइस पर बनती है। इसे कागज़ पर लिखें।"
    ),
    "splash.step3_t": u"ट्रेड / पूल / वोट",
    "splash.step3_d": (
        u"लिमिट ऑर्डर, तरलता पूल और मतपत्र — सब ऑन-चेन।"
    ),

    # =============================================================== about (20)
    "about.hero_lede": (
        u"BitShares ब्लॉकचेन हेतु एक वॉलेट — मार्केट, खाते, शासन और अन्वेषण — सादे "
        u"वेब फ़ाइलों के रूप में चलता है। कोई फ़्रेमवर्क नहीं, कोई इंस्टॉलर नहीं, "
        u"हमारे साथ कोई खाता नहीं। आपकी कुंजियाँ यह ब्राउज़र कभी नहीं छोड़तीं।"
    ),
    "about.s2_title": u"वास्तविक ऑर्डर बुक पर ट्रेड करें",
    "about.s3_title": u"बिना अपडेट वर्षों तक चलता है",
    "about.s3_body": (
        u"जिस वॉलेट यह बदलता है वह सौ पुराने पैकेजों और ऐसी टूलचेन के बोझ से मरा "
        u"जिसे कोई पुनः नहीं बना सकता। रिलीज़-साइकल निर्भरताओं से बचने हेतु बनाया "
        u"गया: कोई फ़्रेमवर्क नहीं, कोई पैकेज प्रबंधक नहीं, कोई बिल्ड चरण नहीं — वह "
        u"न्यूनतम चीज़ जो आज से दस वर्ष बाद भी ब्राउज़र में चल सके।"
    ),
    "about.s4_title": u"वही पेज, लाइव अद्यतन",
    "about.s4_body": (
        u"लौटने वाले उपयोगकर्ता तुरंत घर-सा महसूस करते हैं — क्लासिक वॉलेट जैसे वही "
        u"पेज, पैनल और शब्द — जबकि बैलेंस, बुक व कनेक्शन स्थिति जगह-जगह लाइव "
        u"अद्यतन होती रहती है। मार्केट, खाते व एसेट में क्षमादार खोज, तीन थीम, और "
        u"ऐसे लेआउट जो 360px फ़ोन से 4K ट्रेडिंग डेस्क तक काम करते हैं।"
    ),
    "about.s5_body": (
        u"चेन पूर्णांक बोलती है; आप उन्हें कभी नहीं देखते। प्रत्येक राशि अपने एसेट "
        u"के दशमलव पर, प्रत्येक प्रतिशत अपने वास्तविक मान पर, और प्रत्येक शुल्क "
        u"हस्ताक्षर से पहले लाइव चेन से पढ़ा जाता है।"
    ),
    "about.making_title": u"इस वॉलेट का निर्माण",
    "about.making_body": (
        u"आगे मूल निर्माण कथा दी गई है: इस वॉलेट को बनाने वाला हर प्रॉम्प्ट, 26 "
        u"सितंबर 2026 को “acquire bitshares-ui” से लेकर 3 अक्टूबर के issue-1 सुधार "
        u"तक, निर्माताओं के उत्तरों सहित — बिना किसी बदलाव के सुरक्षित। यह उन "
        u"निर्णयों को दर्ज करती है जिन पर यह वॉलेट खड़ा है: issue #3583 और उसके "
        u"हज़ार-घंटे के जाल से बाहर निकलकर एक और React उन्नयन छोड़ना, ताकि यह वॉलेट "
        u"किसी रिलीज़-साइकल वाली चीज़ पर निर्भर न रहे; पुराने वॉलेट की तरह हर लेनदेन "
        u"स्वयं स्थानीय रूप से हस्ताक्षरित करना, उसे बाहर सौंपने के बजाय; तीन थीम, "
        u"जिनमें क्लासिक रूप मानक है; संख्याएँ मानव पदों में, कभी कच्चे चेन पूर्णांक "
        u"नहीं; पहली स्लाइस से ही फ़ोन-प्रथम लेआउट; और शुल्क लाइव चेन से पढ़े गए, कभी "
        u"अनुमानित नहीं। इसे इतिहास की तरह पढ़ें: वॉलेट इसी तरह बना।"
    ),
    "about.dlg_heading": u"पूर्ण बिल्ड संवाद",
    "about.dlg_heading_c": u"पूर्ण बिल्ड संवाद (%(total)s)",
    "about.dlg_search_ph": u"एक्सचेंज छाँटें…",
    "about.dlg_search_clear": u"साफ़ करें",
    "about.dlg_showing": u"दिखाया जा रहा है",
    "about.dlg_showing_c": u"%(shown)s / %(total)s दर्शाए जा रहे हैं",
    "about.dlg_unavailable": u"बिल्ड-संवाद संग्रह उपलब्ध नहीं।",
    "about.dlg_noscript": (
        u"इस संग्रह हेतु JavaScript चाहिए; वही पाठ स्रोत रिपॉज़िटरी में "
        u"docs/vanilla-ui-dialog.md पर है।"
    ),
    "about.dlg_no_reply": (
        u"कोई उत्तर दर्ज नहीं — अगला प्रॉम्प्ट तुरंत आया।"
    ),
    "about.dlg_no_match": (
        u"कोई मेल खाता एक्सचेंज नहीं। सब देखने हेतु खोज साफ़ करें।"
    ),
    # The confirmed probe run's T14, unchanged.
    "about.dlg_bad_link": (
        u"अमान्य एक्सचेंज नंबर। मान्य रेंग: 1–%(total)s।"
    ),
}

# Keys deliberately left byte-identical to en, and therefore deliberately NOT
# claimed in _meta.translated. Each is asserted to still equal en after the
# write, so a later pass cannot quietly turn a deliberate loanword into an
# unclaimed drift:
#
#   * the loanwords a Hindi crypto UI keeps in Latin: menu.p_htlc (HTLC),
#     explorer.op_prefix (Op) / explorer.op_badge_prefix (" [op "), and
#     explorer.tx_prefix (Tx) - the last two because app.js concatenates them
#     straight onto an op / tx index, so a translated prefix would read as
#     "ऑपरेशन 12" in a block header where every other column head says "Op";
#   * the pure-data templates with no translatable word in them at all:
#     explorer.id_row (ID), explorer.th_mssr (MSSR), explorer.feed_mcr_mssr
#     ("MCR / MSSR"), explorer.feed_mcr_mssr_title ("mcr %(mcr)s; mssr %(mssr)s",
#     a tooltip of two field names and two raw numbers) and
#     explorer.feed_publisher_title ("%(id)s @ %(ts)s", an id and a timestamp
#     joined by the at-sign);
#   * pool_net.edge_card and pool_net.edge_nobal: a pool id, two asset symbols
#     and (for the first) two balances and two share counts, glued with middle
#     dots. Translating the separator would change what the reader sees without
#     changing a single word - the same reasoning chunk-A used for
#     market_net.edge_card;
#   * the shell brands and the net/host footer glue, which the brief pins and
#     which all ten other locales also leave in Latin;
#   * i18n.badge_chip, the literal "i18n" tag the header chip prints.
KEPT_ENGLISH = {
    # ---- explorer
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.th_mssr": u"MSSR",
    "explorer.tx_prefix": u"Tx ",
    # ---- i18n
    "i18n.badge_chip": u"i18n",
    # ---- menu
    "menu.p_htlc": u"HTLC",
    # ---- pool_net
    "pool_net.edge_card": (
        u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s"
    ),
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
}


if __name__ == "__main__":
    sys.exit(main())