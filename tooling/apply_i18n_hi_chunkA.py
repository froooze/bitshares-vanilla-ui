#!/usr/bin/env python3
"""i18n hi chunk-A: fill the six desk sections hi.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from hi.json, or one whose English master moved, is REFUSED;
  * HI + KEPT_ENGLISH together must account for EVERY untranslated key of the
    six sections, so a forgotten string is a refusal, never a silent English.

chunk-B owns the help/pool/explorer tail and REFUSES anything outside it; this
batch REFUSES anything outside account, account_net, settings, market,
market_net and asset. A key that crosses the line is a reviewer's problem,
never a script's silent edit.

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
                      every filled key, measured against the ENGLISH master;
  G4b edge spaces   leading / trailing whitespace of the English master is
                      reproduced exactly. Five values in this batch are pure
                      GLUE with a load-bearing blank - "Page total ~ ",
                      "Amount for sale (new total) ", "New price ", "New
                      expiration ", "Example: a dice game at " and " + %(n)s
                      more" - where a missing trailing space silently welds
                      the computed value onto the label. zh/ru never needed a
                      gate for this because their alphabets do not end a line
                      the same way; the check is cheap and catches the whole
                      class, so it runs for every key;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an untranslated key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  script         no Cyrillic and no CJK letter may appear in any value
                      THIS BATCH writes. Hindi is Devanagari; a stray Cyrillic
                      or Han character is a copy-paste from a sibling locale
                      (this batch was written with the zh and ru tables open),
                      not a Hindi word. The whole file is swept for both and a
                      hit OUTSIDE the six sections is reported as PRE-EXISTING
                      rather than repaired - chunk-B owns those keys, and an
                      insert-only pass that "fixed" a neighbour would be exactly
                      the silent edit the scope refusal exists to prevent.
  G7b quotes         no ASCII or typographic apostrophe in a value this batch
                      writes. Devanagari prose needs none (the file already
                      quotes with the curly pair " " - see
                      misc.invoice_query_bad_amount - and with no apostrophe
                      anywhere in the 3150 translated strings), so a stray one
                      would be the only such spelling in the dictionary;
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric (pool.list_sub ships
                      "x*y=k" in Devanagari-adjacent form, outside this batch's
                      six sections);
  G9  loanwords      every Latin token a value THIS BATCH writes must be
                      declared in LOAN below, or already occur in the ENGLISH
                      master of that same key (which is how DATA - an account
                      name, a file path, an op number - legitimately stays
                      Latin). Any token that leans on the English-source clause
                      rather than on LOAN is printed, so a reviewer can see the
                      difference instead of guessing. Hindi crypto UIs keep the
                      English word for DEX, HTLC, FBA, BitShares, BTS, API,
                      Op, GitHub, Memo, Proxy, Swap, Smartcoin, Pool,
                      Brainkey, Enter, Same-T - inventing a fake Devanagari
                      transliteration instead would be worse than the loanword,
                      because the reader already searches for the Latin string.
                      The gate is batch-scoped on purpose: the rest of hi.json
                      carries Latin tokens from earlier batches, and
                      re-litigating those is not this file's job.

Register is FORMAL (aap) - the standard for Hindi financial software - and the
vocabulary is reused verbatim from the 3150 strings hi.json already ships, so
this batch reads like the rest of the dictionary instead of like a second
dictionary: khata (खाता), wallet (वॉलेट), password (पासवर्ड), unlock (अनलॉक),
sign / signature (हस्ताक्षर), broadcast (प्रसारित as a past act, प्रसारण as the
noun - both already in the file), amount (राशि), balance (बैलेंस), price (मूल्य),
volume (मात्रा), order (ऑर्डर), limit order (लिमिट ऑर्डर), fill (फिल), market
(मार्केट), exchange (एक्सचेंज), desk (डेस्क), pool (पूल), swap (स्वैप), stake /
unstake (स्टेक / अनस्टेक), liquidity (तरलता), proposal (प्रस्ताव), approve /
approved (अनुमोदन / अनुमोदित), witness (विटनेस), committee (कमेटी), worker
(वर्कर), proxy (प्रॉक्सी), smartcoin (स्मार्टकॉइन), feed (फ़ीड), feed producer
(फ़ीड उत्पादक), publisher (प्रकाशक), issuer (जारीकर्ता), precision
(परिशुद्धता), settlement (सेटलमेंट), collateral (कोलैटरल), debt (कर्ज़), credit
offer (क्रेडिट ऑफ़र), borrower (उधारकर्ता), acceptable (स्वीकार्य),
auto-disable (स्वतः-अक्षम), direct debit (डायरेक्ट डेबिट), permission (अनुमति),
authorized (अधिकृत), vesting (वेस्टिंग), blind (ब्लाइंड), ticket (टिकट), memo
(मेमो), node (नोड), chain (चेन), fee (शुल्क), counterparty (प्रतिपक्ष),
expiration (समाप्ति), theme (थीम), language (भाषा), deposit (जमा), withdrawal
(निकासी), redeem (मोचन), refund (रिफ़ंड), hash (हैश), timelock (टाइमलॉक).
एक्सटेंशन ("extension", settings.sign_*) and कोलैटरल-बोली are this batch's first
spellings of those two words in hi.json, the way 扩展 was zh's and
расширение ru's.

The op labels (account.op_*) follow the nominal pattern the six already
translated ones established - "Account create" ships as "खाता निर्माण", "Limit
order create" as "लिमिट ऑर्डर निर्माण", "Fill order" as "फिल ऑर्डर" - so a history
column reads as a list of nouns. The account.sum_* history lines keep the
shipped finished-voice ("Registered %(name)s" is a finished act, not a noun),
because they describe one row, not a column.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (first 8 publishers, first 100, op 19, op 23, 7-day,
24h, 90d) the translation keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_hi_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_hi_chunkA.py --apply         # writes hi.json
  python3 tooling/apply_i18n_hi_chunkA.py --verify        # structural re-proof
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

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from HI below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live in this batch's own settings section; the shell brands live
# outside it and are kept in the list so a drift anywhere in the file is caught.
PINNED = (
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
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
# _ . / so "Same-T", "get_settle_orders" and "ipaddress.to" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Hindi crypto UI prints in Latin; anything else has to be Devanagari.
LOAN = frozenset((
    # --- domain names and chain / protocol vocabulary
    "HTLC",          # hash time-locked contract; the graph chip and every op
                     # label keep it, as do the en/es/de/it/ko dictionaries
    "FBA",           # fee-betting-algorithm distribution op
    "Same-T",        # Same-T funds; hi.json's help article already writes it
                     # this way ("Same-T फंड अनेक आपूर्तिकर्ताओं से...")
    "SameT",         # the same name as the English master spells it, for the
                     # three account.sum_* lines that use the bare spelling
    "BTS",           # the core asset ticker
    "Op",            # the operation-number column head (asset.op_col); de, es,
                     # fr, it, pt and ko all keep it too
    "op",            # the "op 19" / "op %(op)s" family, kept byte-verbatim
    "GitHub",        # the discovery endpoint and the version check
    "Enter",         # a keyboard key, printed in Latin on the user's keyboard
                     # (pool.map_core_aria already ships "Enter दबाएँ")
    # --- service names inside prose, never prose themselves
    "ipaddress.to",  # the geo lookup behind settings.geo_note
    "https",         # the transport word in that same note
    "get_settle_orders",  # the WS method market.settle_first100 names
    # --- indicator / ticker loanwords the brief lists for every locale
    "BB", "EMA", "PSAR", "SMA",
    # --- technical acronyms. CER joins the brief's list because asset.cer_row
    # names it in a sentence and hi.json already ships four "CER आधार/कोट"
    # field labels from an earlier batch, so the acronym is this file's
    # established spelling, not an invention.
    "MCR", "CER", "NFT", "URI", "PMA", "UIA",
))
# Tokens that reached G9 only because the ENGLISH master of the same key already
# contains them. Nothing should land here; the run prints whatever does so a
# reviewer can audit the distinction instead of trusting it.
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
        # A count keeping its English unit suffix ("24h", "90d") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # into "24घंटे" inside a compact column head without breaking the
        # number the reader compares against the control beside it.
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
    # are printed loudly and never repaired here: chunk-B owns them, and an
    # insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` - problems this batch can
    # answer for - gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
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
            if key in HI:
                bad.append(where)
            else:
                pre.append(where)
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
    # values kept byte-identical on purpose (loanwords, brands, ids, glue) stay
    # UNCLAIMED, which is the honest state for them and is also what the
    # IDENTIFIERS gate requires. Nothing else in _meta moves - filling strings
    # is not verification, so the controller's v2 provenance/verified/high_risk
    # fields stay untouched.
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

    print("hi chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    print("  LOAN allowlist (%d): %s" % (len(LOAN), ", ".join(sorted(LOAN))))
    if fallback:
        print("  G9 tokens that leaned on the ENGLISH SOURCE rather than on "
              "LOAN (audit these):")
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
    # =========================================================== account (148)
    # The shared-account line: "active" and "owner" are the two weight types,
    # and the confirmed hi probe run already spells both सक्रिय and स्वामी -
    # the same pair vesting.owner and auth's permission help use - so the line
    # reuses them verbatim.
    "account.draw_network": u"नेटवर्क बनाएँ",
    "account.lookup_placeholder": u"खाता-नाम",
    "account.multisig_checking": u"प्राधिकरण जाँचे जा रहे हैं…",
    "account.multisig_open_txbuilder": u"लेनदेन निर्माता खोलें",
    "account.multisig_shared": (
        u"साझा खाता — सक्रिय %(ath)s/%(an)s · स्वामी %(oth)s/%(on)s।"
    ),
    "account.multisig_single": (
        u"एकल कुंजी — सक्रिय %(ath)s/%(an)s · स्वामी %(oth)s/%(on)s।"
    ),
    "account.multisig_single_hint": (
        u"साझा खाता? प्रस्ताव प्रस्ताव पृष्ठ पर हैं।"
    ),
    "account.multisig_unavailable": (
        u"प्राधिकरण अनुपलब्ध — प्रस्ताव फिर भी प्रस्ताव पृष्ठ पर सूचीबद्ध हैं।"
    ),
    "account.multisig_view_proposals": u"प्रस्ताव देखें",
    # Operation labels. Nominal, like the translated ones ("खाता निर्माण",
    # "लिमिट ऑर्डर निर्माण", "फिल ऑर्डर") so a history column reads as a list of
    # nouns.
    "account.op_assert_op": u"एसर्ट",
    "account.op_asset_burn": u"एसेट बर्न",
    "account.op_asset_issue": u"एसेट जारी",
    "account.op_asset_settle": u"एसेट सेटल",
    "account.op_asset_update": u"एसेट अपडेट",
    "account.op_authority_create": u"अथॉरिटी निर्माण",
    "account.op_authority_delete": u"अथॉरिटी हटाना",
    "account.op_authority_update": u"अथॉरिटी अपडेट",
    "account.op_balance_claim": u"बैलेंस दावा",
    # The blind legs are named by direction so the pair reads as one transfer:
    # ब्लाइंड से ट्रांसफर / ब्लाइंड को ट्रांसफर / ब्लाइंड ट्रांसफर - the same
    # three lines the vesting help article already ships.
    "account.op_blind_from": u"ब्लाइंड से ट्रांसफर",
    "account.op_blind_to": u"ब्लाइंड को ट्रांसफर",
    "account.op_blind_transfer": u"ब्लाइंड ट्रांसफर",
    "account.op_claim_fees": u"शुल्क दावा",
    "account.op_claim_pool": u"शुल्क पूल दावा",
    "account.op_collateral_bid": u"कोलैटरल बोली",
    "account.op_committee_join": u"कमेटी में जुड़ाव",
    "account.op_committee_update": u"कमेटी अपडेट",
    "account.op_custom_op": u"कस्टम ऑपरेशन",
    "account.op_deal_expired": u"डील समाप्त",
    "account.op_deal_repay": u"डील चुकौती",
    "account.op_deal_update": u"डील अपडेट",
    "account.op_debit_claim": u"डायरेक्ट डेबिट दावा",
    "account.op_debit_create": u"डायरेक्ट डेबिट निर्माण",
    "account.op_debit_delete": u"डायरेक्ट डेबिट हटाना",
    "account.op_debit_update": u"डायरेक्ट डेबिट अपडेट",
    "account.op_execute_bid": u"बोली निष्पादन",
    "account.op_fba_distribute": u"FBA वितरण",
    "account.op_fee_pool_fund": u"शुल्क पूल फंडिंग",
    "account.op_feed_producers_update": u"फ़ीड उत्पादक अपडेट",
    "account.op_feed_publish": u"फ़ीड प्रकाशन",
    "account.op_global_settle": u"वैश्विक सेटल",
    "account.op_htlc_create": u"HTLC निर्माण",
    "account.op_htlc_extend": u"HTLC विस्तार",
    "account.op_htlc_redeem": u"HTLC मोचन",
    "account.op_htlc_redeemed": u"HTLC मोचा गया",
    "account.op_htlc_refund": u"HTLC रिफ़ंड",
    "account.op_issuer_update": u"जारीकर्ता अपडेट",
    "account.op_offer_accept": u"क्रेडिट स्वीकार",
    "account.op_offer_create": u"क्रेडिट ऑफ़र निर्माण",
    "account.op_offer_delete": u"क्रेडिट ऑफ़र हटाना",
    "account.op_offer_update": u"क्रेडिट ऑफ़र अपडेट",
    "account.op_order_update": u"ऑर्डर अपडेट",
    "account.op_override_transfer": u"ओवरराइड ट्रांसफर",
    "account.op_params_update": u"वैश्विक पैरामीटर अपडेट",
    "account.op_pool_create": u"पूल निर्माण",
    "account.op_pool_delete": u"पूल हटाना",
    "account.op_pool_deposit": u"पूल जमा",
    "account.op_pool_swap": u"पूल स्वैप",
    "account.op_pool_update": u"पूल अपडेट",
    "account.op_pool_withdraw": u"पूल निकासी",
    "account.op_proposal_create": u"प्रस्ताव निर्माण",
    "account.op_proposal_delete": u"प्रस्ताव हटाना",
    "account.op_proposal_update": u"प्रस्ताव अपडेट",
    "account.op_samet_borrow": u"Same-T उधार",
    "account.op_samet_create": u"Same-T फंड निर्माण",
    "account.op_samet_delete": u"Same-T फंड हटाना",
    "account.op_samet_repay": u"Same-T चुकौती",
    "account.op_samet_update": u"Same-T फंड अपडेट",
    "account.op_settle_cancel": u"सेटल रद्द",
    "account.op_smartcoin_update": u"स्मार्टकॉइन अपडेट",
    "account.op_ticket_create": u"टिकट निर्माण",
    "account.op_ticket_update": u"टिकट अपडेट",
    "account.op_vesting_create": u"वेस्टिंग निर्माण",
    "account.op_vesting_withdraw": u"वेस्टिंग निकासी",
    "account.op_witness_join": u"विटनेस में जुड़ाव",
    "account.op_witness_update": u"विटनेस अपडेट",
    "account.op_worker_create": u"वर्कर निर्माण",
    # Pager + its note. The trailing space on page_total is load-bearing: a
    # computed figure follows it (G4b proves it survives).
    "account.page_total": u"पृष्ठ कुल ≈ ",
    "account.portfolio_page": u"पृष्ठ %(page)s / %(pages)s",
    "account.prices_cover_this_page": (
        u"मूल्य इस पृष्ठ को कवर करते हैं — अधिक एसेट्स का मूल्य देखने हेतु पृष्ठ बदलें।"
    ),
    # History one-liners: a finished act, one row, so every line reads as
    # something that already happened ("... हुआ / किया गया") rather than as a
    # noun the way the op labels do.
    "account.sum_account_create": u"%(name)s पंजीकृत हुआ",
    "account.sum_account_transfer": u"खाता %(owner)s को हस्तांतरित किया गया",
    "account.sum_account_update": u"खाता अपडेट हुआ: %(account)s",
    "account.sum_asset_burn": u"%(amount)s बर्न किए गए",
    "account.sum_asset_create": u"एसेट %(symbol)s बनाया गया",
    "account.sum_asset_issue": u"%(to)s को %(amount)s जारी किए गए",
    "account.sum_asset_settle": u"%(amount)s का सेटल अनुरोध किया गया",
    "account.sum_asset_update": u"एसेट %(asset)s अपडेट हुआ",
    "account.sum_authorities": u"%(account)s की प्राधिकरण अपडेट हुई",
    "account.sum_balance_claim": u"%(amount)s का दावा हुआ",
    "account.sum_bid": u"बोली: %(coll)s कोलैटरल, %(debt)s कर्ज़",
    "account.sum_blind": u"ब्लाइंड ट्रांसफर (%(in)s अंदर, %(out)s बाहर)",
    "account.sum_call_update": (
        u"पोज़ीशन समायोजित: %(coll)s कोलैटरल, %(debt)s कर्ज़"
    ),
    "account.sum_claim_fees": u"%(amount)s शुल्क का दावा हुआ",
    "account.sum_committee_create": u"कमेटी सदस्य बने: %(account)s",
    "account.sum_committee_update": u"कमेटी सदस्य %(account)s अपडेट हुआ",
    "account.sum_custom": u"%(account)s द्वारा कस्टम ऑपरेशन",
    "account.sum_deal_expired": u"डील %(deal)s की समाप्ति हो गई",
    "account.sum_deal_repay": u"डील %(deal)s पर %(amount)s चुकाए गए",
    "account.sum_deal_update": u"डील %(deal)s अपडेट हुई",
    "account.sum_debit_claim": u"%(amount)s डेबिट का दावा हुआ",
    "account.sum_debit_create": u"%(to)s हेतु %(amount)s डेबिट प्राधिकृत",
    "account.sum_debit_delete": u"डेबिट अनुमति %(perm)s हटाई गई",
    "account.sum_debit_update": u"%(to)s हेतु %(amount)s डेबिट अपडेट हुआ",
    "account.sum_execute_bid": u"बोली निष्पादित: %(coll)s कोलैटरल, %(debt)s कर्ज़",
    "account.sum_fee_pool_fund": (
        u"%(asset)s के शुल्क पूल में %(amount)s जमा किए गए"
    ),
    "account.sum_feed": u"%(publisher)s द्वारा %(asset)s की फ़ीड प्रकाशित",
    "account.sum_feed_producers": (
        u"%(asset)s हेतु %(n)s फ़ीड उत्पादक निर्धारित"
    ),
    "account.sum_fill": u"फिल: %(pays)s दिए, %(receives)s प्राप्त",
    "account.sum_global_settle": u"%(asset)s का वैश्विक सेटल हुआ",
    "account.sum_htlc_claimed": u"HTLC %(id)s का दावा हुआ",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(from)s से %(to)s को %(amount)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s का विस्तार हुआ",
    "account.sum_htlc_redeem": u"HTLC %(id)s मोचा गया",
    "account.sum_htlc_refund": u"HTLC %(id)s रिफ़ंड हुआ",
    "account.sum_issuer_update": u"%(asset)s का नया जारीकर्ता: %(issuer)s",
    "account.sum_offer_accept": (
        u"%(coll)s के विरुद्ध %(amount)s उधार लिए गए (ऑफ़र %(offer)s)"
    ),
    "account.sum_offer_create": u"%(asset)s में क्रेडिट ऑफ़र बनाया गया",
    "account.sum_offer_delete": u"ऑफ़र %(offer)s हटाया गया",
    "account.sum_offer_update": u"ऑफ़र %(offer)s अपडेट हुआ",
    "account.sum_order_cancel": u"ऑर्डर %(order)s रद्द किया गया",
    "account.sum_order_create": u"%(sell)s प्रस्तुत, कम से कम %(buy)s हेतु",
    "account.sum_order_update": u"ऑर्डर %(order)s अपडेट हुआ",
    "account.sum_pool_create": u"पूल %(a)s / %(b)s बनाया गया",
    "account.sum_pool_delete": u"पूल %(pool)s हटाया गया",
    "account.sum_pool_deposit": u"पूल %(pool)s में %(a)s + %(b)s स्टेक किए गए",
    "account.sum_pool_swap": (
        u"पूल %(pool)s में %(sell)s का स्वैप → कम से कम %(buy)s"
    ),
    "account.sum_pool_update": u"पूल %(pool)s अपडेट हुआ",
    "account.sum_pool_withdraw": u"पूल %(pool)s से %(shares)s अनस्टेक किए गए",
    "account.sum_proposal_create": u"%(n)s ऑपरेशन प्रस्तावित",
    "account.sum_proposal_delete": u"प्रस्ताव %(proposal)s हटाया गया",
    "account.sum_proposal_update": u"प्रस्ताव %(proposal)s अनुमोदित",
    "account.sum_samet_borrow": u"फंड %(fund)s से %(amount)s उधार लिए गए",
    "account.sum_samet_create": u"Same-T फंड %(amount)s के साथ बनाया गया",
    "account.sum_samet_delete": u"Same-T फंड %(fund)s हटाया गया",
    "account.sum_samet_repay": u"फंड %(fund)s को %(amount)s चुकाए गए",
    "account.sum_samet_update": u"Same-T फंड %(fund)s अपडेट हुआ",
    "account.sum_settle_cancel": u"%(amount)s का सेटल रद्द किया गया",
    "account.sum_smartcoin_update": u"स्मार्टकॉइन %(asset)s अपडेट हुआ",
    "account.sum_ticket_create": u"टिकट %(amount)s बनाया गया",
    "account.sum_ticket_update": u"टिकट %(ticket)s अपडेट हुआ",
    "account.sum_transfer": u"ट्रांसफर: %(from)s से %(to)s को %(amount)s",
    "account.sum_transfer_recv": u"%(from)s से %(amount)s प्राप्त",
    "account.sum_transfer_send": u"%(to)s को %(amount)s भेजे गए",
    "account.sum_upgrade": u"%(account)s का अपग्रेड हुआ",
    "account.sum_vesting_create": u"%(owner)s हेतु %(amount)s वेस्ट किए गए",
    "account.sum_vesting_withdraw": u"वेस्टेड %(amount)s निकाले गए",
    "account.sum_whitelist": u"%(account)s सूचीबद्ध किया गया",
    "account.sum_witness_create": u"विटनेस बने: %(account)s",
    "account.sum_witness_update": u"विटनेस %(account)s अपडेट हुआ",
    "account.sum_worker_create": u"वर्कर “%(name)s” बनाया गया",

    # ====================================================== account_net (61)
    "account_net.canvas_missing": (
        u"इस बिल्ड में नेटवर्क कैनवस अनुपलब्ध है; नीचे तालिका हर लाइन फिर भी "
        u"सूचीबद्ध करती है।"
    ),
    "account_net.class_credit": u"क्रेडिट",
    "account_net.class_credit_help": u"स्वीकृत और चुकाए गए क्रेडिट ऑफ़र।",
    "account_net.class_debit": u"डायरेक्ट डेबिट",
    "account_net.class_debit_help": u"डायरेक्ट-डेबिट अनुमतियाँ और निकासियाँ।",
    "account_net.class_htlc_help": u"हैश टाइम-लॉक्ड अनुबंध और उनके अपडेट।",
    # "relation" is a permission line, not a movement of value - the help text
    # says so, so the chip label stays distinguishable from "प्रवाह".
    "account_net.class_override": u"ओवरराइड ट्रांसफर",
    "account_net.class_override_help": (
        u"वे ट्रांसफर जिनका शुल्क एसेट जारीकर्ता देता है।"
    ),
    "account_net.class_transfer": u"ट्रांसफर",
    "account_net.class_transfer_help": u"खातों के बीच प्रत्यक्ष ट्रांसफर।",
    "account_net.class_vesting": u"वेस्टिंग",
    "account_net.class_vesting_help": (
        u"वेस्टिंग बैलेंस जिन्हें कोई तृतीय पक्ष प्रबंधित करता है।"
    ),
    # Graph terms: a hop is one edge traversal, a ring is the neighbourhood the
    # expansion walks. hi.json's pool map already says "{s} से BTS तक {n} हॉप्स",
    # so both reuse हॉप.
    "account_net.depth_1": u"1 हॉप",
    "account_net.depth_2": u"2 हॉप",
    "account_net.depth_label": u"गहराई",
    "account_net.detail_hint": (
        u"विवरण हेतु किसी लाइन पर टैप करें; खोलने हेतु किसी खाते पर टैप करें।"
    ),
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ऑपरेशन · "
        u"%(kind)s"
    ),
    # Hindi does not mark the plural on a counted noun-phrase after a numeral
    # in a table cell, so the "ops" / "op" pair collapses to one form here -
    # the same decision the zh batch made.
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ऑपरेशन · "
        u"%(kind)s"
    ),
    "account_net.es_bad_account": u"यह नाम इस चेन पर कोई खाता नहीं है।",
    "account_net.es_disabled": (
        u"सामुदायिक इंडेक्स बंद है। यह मानचित्र बनाने हेतु सेटिंग्स में इसे "
        u"चालू करें।"
    ),
    "account_net.es_unavailable": (
        u"सामुदायिक इंडेक्स अभी पहुँच से बाहर है। कुछ देर बाद पुनः प्रयास करें।"
    ),
    "account_net.go": u"नेटवर्क बनाएँ",
    "account_net.idle": u"अभी कुछ नहीं बनाया गया।",
    "account_net.intro": (
        u"यह देखने हेतु एक या अधिक खाते दर्ज करें कि वे किसे भेजते हैं, किसे "
        u"उधार देते हैं और किससे उधार लेते हैं। सामुदायिक हिस्ट्री इंडेक्स से "
        u"पठन; कुछ भी हस्ताक्षरित नहीं होता और कुछ भी संग्रहीत नहीं होता।"
    ),
    "account_net.kind_flow": u"प्रवाह",
    "account_net.kind_relation": u"संबंध",
    "account_net.more_assets": u" + %(n)s और",
    "account_net.need_class": u"बनाने हेतु कम से कम एक प्रकार की लाइन चालू करें।",
    "account_net.need_seeds": u"मानचित्र हेतु कम से कम एक खाता दर्ज करें।",
    "account_net.no_amount": u"कोई राशि नहीं",
    "account_net.ring1_label": u"रिंग 1",
    "account_net.ring2_label": u"रिंग 2",
    "account_net.scanning": u"सामुदायिक इंडेक्स पढ़ा जा रहा है…",
    "account_net.seeds_label": u"मानचित्र हेतु खाते",
    "account_net.stale_settings": (
        u"गहराई या पड़ोसी सेटिंग बदली — “नेटवर्क बनाएँ” दबाएँ।"
    ),
    "account_net.status_credit_index": (
        u"इंडेक्स से %(n)s क्रेडिट लाइनें हल हुईं (उनका ऑफ़र या डील ऑब्जेक्ट "
        u"चेन से गायब है)"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s क्रेडिट लाइनें छोड़ी गईं (ऑफ़र या डील चेन पर नहीं मिला)"
    ),
    "account_net.status_depth": u"%(depth)s मानचित्र",
    "account_net.status_edge_cap": u"शीर्ष %(n)s लाइनें दिखाई जा रही हैं",
    "account_net.status_expanded": u"विस्तारित: %(names)s",
    "account_net.status_expansion_scanned": (
        u"विस्तार से %(n)s अनुक्रमित ऑपरेशन"
    ),
    "account_net.status_expansion_truncated": (
        u"विस्तार स्कैन नवीनतम ऑपरेशनों तक सीमित"
    ),
    "account_net.status_graph": u"%(nodes)s खाते · %(edges)s लाइनें",
    "account_net.status_node_cap": u"शीर्ष %(n)s प्रतिपक्ष दिखाए जा रहे हैं",
    "account_net.status_scanned": (
        u"%(n)s खातों से %(scanned)s अनुक्रमित ऑपरेशन"
    ),
    "account_net.status_self": u"%(n)s स्व-ट्रांसफर छोड़े गए",
    "account_net.status_shape": u"%(n)s अपठनीय प्रविष्टियाँ छोड़ी गईं",
    "account_net.status_truncated": u"प्रति खाता नवीनतम %(n)s ऑपरेशन",
    "account_net.status_unexpanded": u"%(n)s प्रत्यक्ष प्रतिपक्ष विस्तारित नहीं",
    "account_net.status_unknown": u"नहीं मिला: %(names)s",
    "account_net.title": u"खाता नेटवर्क",
    "account_net.twin_amount": u"राशि",
    "account_net.twin_class": u"प्रकार",
    "account_net.twin_count": u"ऑपरेशन",
    "account_net.twin_depth": u"हॉप",
    "account_net.twin_empty": (
        u"स्कैन किए गए अनुक्रमित ऑपरेशनों में इन खातों के बीच कोई लाइन नहीं।"
    ),
    "account_net.twin_from": u"प्रेषक",
    "account_net.twin_relation": u"प्रवाह/संबंध",
    "account_net.twin_span": u"पहला → अंतिम",
    "account_net.twin_summary": u"सारणी दृश्य (सुलभ)",
    "account_net.twin_to": u"प्राप्तकर्ता",

    # ============================================================== asset (34)
    "asset.cer_row": u"कोर एक्सचेंज दर (CER)",
    "asset.committee_fed_note": (
        u"कमेटी-फ़ीड: सक्रिय कमेटी सदस्य सभी प्रकाशित कर सकते हैं।"
    ),
    "asset.feed_history_title": u"फ़ीड हिस्ट्री",
    "asset.history_capped": (
        u"पहले 8 प्रकाशक दिखाए जा रहे हैं (गति हेतु सीमित)…"
    ),
    "asset.history_days": u"अवधि",
    "asset.history_exchange": u"एक्सचेंज + पूल लोड हो रहे हैं…",
    "asset.history_failed": u"फ़ीड हिस्ट्री लोड नहीं हो सकी।",
    "asset.history_loading": u"फ़ीड हिस्ट्री लोड हो रही है…",
    "asset.history_pub": u"प्रकाशक %(i)s/%(n)s…",
    "asset.invert_btn": u"उल्टा करें",
    "asset.issue_memo_no_key": u"इस खाते हेतु कोई मेमो कुंजी दर्ज नहीं।",
    "asset.issue_memo_warning": (
        u"मेमो संलग्न करें — यह ऑन-चेन प्लेनटेक्स्ट संग्रहीत होता है।"
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"जारीकर्ता डिफ़ॉल्ट रूप से देख-ए-जाने वाले खाते पर होता है (%(id)s "
        u"लॉक, आपका खाता अनलॉक) — ऐसा कोई भी जारीकर्ता टाइप करें जिस पर आपका "
        u"नियंत्रण हो। खाता पृष्ठ से खुलने पर, वह खाता नाम यहाँ चिपकाएँ।"
    ),
    "asset.loading_producers": u"उत्पादक लोड हो रहे हैं…",
    # "Co-owner" is the same term the shared-account hint uses for the second
    # key holder, so both reuse सह-स्वामी verbatim.
    "asset.multisig_body": (
        u"यदि इस एसेट हेतु एक से अधिक अनुमोदन आवश्यक हैं, तो प्रत्यक्ष हस्ताक्षर "
        u"विफल होगा — इसके बजाय परिवर्तन प्रस्तावित करें और सह-स्वामियों से अनुमोदन "
        u"कहें (op 23)।"
    ),
    "asset.multisig_coowner_hint": (
        u"सह-स्वामी? प्रस्ताव पृष्ठ पर परिवर्तन प्रस्तावित करें और सह-स्वामियों "
        u"से अनुमोदन कहें (op 23)।"
    ),
    "asset.multisig_open_proposals": u"प्रस्ताव देखें",
    "asset.multisig_open_txbuilder": u"लेनदेन निर्माता खोलें",
    "asset.multisig_title": u"साझा जारीकर्ता? इसे प्रस्तावित करें",
    "asset.new_issuer_field": u"नया जारीकर्ता",
    "asset.no_history": (
        u"इस अवधि में कोई हिस्ट्री नहीं — प्रकाशक शायद ही प्रकाशित करते हैं; "
        u"90d आज़माएँ।"
    ),
    "asset.no_producers": (
        u"अभी कोई फ़ीड प्रकाशित नहीं — प्रकाशन के बाद उत्पादक यहाँ दिखेंगे।"
    ),
    "asset.orientation_note": u"प्रति %(b)s %(m)s",
    "asset.owner_key_note": u"इसके लिए एसेट स्वामी की सक्रिय कुंजी आवश्यक है।",
    "asset.plot_feeds": u"फ़ीड प्लॉट करें",
    "asset.producer_col": u"उत्पादक",
    "asset.producers_failed": u"उत्पादक लोड नहीं हो सके।",
    "asset.producers_live_title": u"फ़ीड उत्पादक",
    "asset.producers_title": u"फ़ीड उत्पादक (op %(op)s)",
    "asset.publish_op19_title": u"फ़ीड प्रकाशित करें (op %(op)s)",
    "asset.published_col": u"प्रकाशित",
    # "Viewing as" is the phrase shell.acting_default and every *_viewing_as
    # notice already ships as "… के रूप में देख रहे हैं"; this reuses it so
    # principle #9 reads one way.
    "asset.viewing_notice": (
        u"%(name)s (%(id)s) के रूप में देख रहे हैं — हस्ताक्षर हेतु अनलॉक करें।"
    ),
    "asset.witness_fed_note": (
        u"विटनेस-फ़ीड: सक्रिय विटनेस सभी प्रकाशित कर सकते हैं।"
    ),

    # ============================================================ market (50)
    "market.adjust_button": u"समायोजित करें",
    "market.confirm_adjust": u"समायोजन की पुष्टि करें",
    "market.discrete_fills": u"फिल",
    "market.discrete_no_fills": (
        u"अभी कोई फिल नहीं — ऑर्डर लगाएँ या दूसरी जोड़ी आज़माएँ।"
    ),
    "market.discrete_swaps": u"स्वैप",
    "market.discrete_tip_account": u"खाता",
    "market.discrete_tip_block": u"ब्लॉक",
    "market.discrete_tip_order": u"ऑर्डर",
    "market.discrete_tip_price": u"मूल्य",
    "market.discrete_tip_time": u"समय",
    "market.discrete_tip_volume": u"मात्रा",
    "market.discrete_tip_volume_quote": u"मात्रा (कोट)",
    "market.discrete_unavailable": u"डिस्क्रीट में संकेतक अनुपलब्ध।",
    "market.discrete_volume": u"डिस्क्रीट मात्रा",
    "market.exchange_desk": u"एक्सचेंज डेस्क",
    "market.fail_update": u"अपडेट विफल।",
    "market.flt_max_price": u"अधिकतम मूल्य",
    "market.flt_min_price": u"न्यूनतम मूल्य",
    "market.loading_pool_map": u"मानचित्र लोड हो रहा है…",
    "market.map_aria": (
        u"मार्केट नेटवर्क। लाइनें वे मार्केट हैं जिनमें पिछले 24 घंटे में फिल हुए।"
    ),
    "market.map_connects": (
        u"जब पिछले 24 घंटे में दो एसेट्स के बीच मार्केट ट्रेड हुआ हो, तो एक "
        u"लाइन दो एसेट्स को जोड़ती है।"
    ),
    "market.map_connects_fallback": (
        u"जब कोई निधि-पूर्ण पूल मौजूद हो, तो एक लाइन दो एसेट्स को जोड़ती है। "
        u"24घंटे की ट्रेड गतिविधि की पुष्टि नहीं है (हिस्ट्री अनुपलब्ध) — "
        u"निधि-पूर्ण पूल दिखाए जा रहे हैं।"
    ),
    "market.map_edge_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24घंटे %(fills)s फिल"
    ),
    "market.map_hops_empty": (
        u"इन पक्षों के आसपास पिछले 24 घंटे में कोई मार्केट नहीं भरा।"
    ),
    "market.map_hops_filtered": (
        u"एक लाइन वह मार्केट है जिसमें पिछले 24 घंटे में फिल हुए। %(total)s "
        u"जोड़ियों में से %(shown)s दिखाई जा रही हैं (न्यूनतम 24घंटे %(min)s "
        u"फिल)।"
    ),
    "market.map_hops_no_route": u"भरे गए मार्केटों से BTS तक कोई मार्ग नहीं।",
    "market.map_hops_note": (
        u"एक लाइन वह मार्केट है जिसमें पिछले 24 घंटे में फिल हुए। %(pairs)s "
        u"जोड़ियाँ दिखाई जा रही हैं।"
    ),
    "market.map_leg_ok": u"{s} BTS से जुड़ता है",
    "market.map_leg_orphan": (
        u"चेतावनी: {s} का भरे गए मार्केटों से कोई मार्ग नहीं!"
    ),
    "market.min_fills": u"न्यूनतम फिल",
    "market.no_filter_match": u"इन फ़िल्टरों से कोई फिल मेल नहीं खाता।",
    "market.settle_first100": (
        u"पहली 100 दिखाई जा रही हैं (get_settle_orders सीमा 100)"
    ),
    "market.settle_no_cancel": (
        u"सेटलमेंट ऑर्डर रद्द नहीं किए जा सकते — वे सेटलमेंट के समय निष्पादित "
        u"होते हैं (एसेट के बल-सेटलमेंट विलंब के बाद)।"
    ),
    "market.tf_discrete": u"डिस्क्रीट",
    # The three trailing spaces are load-bearing: an input follows them (G4b).
    "market.update_amount": u"बिक्री हेतु राशि (नया कुल) ",
    "market.update_amount_change": u"राशि परिवर्तन",
    "market.update_bad_amount": u"शून्य से अधिक राशि दर्ज करें।",
    "market.update_bad_expiry": u"भविष्य की समाप्ति दर्ज करें।",
    "market.update_bad_price": u"शून्य से अधिक मूल्य दर्ज करें।",
    "market.update_broadcasting": u"अपडेट प्रसारित हो रहा है…",
    "market.update_done": u"ऑर्डर अपडेट हुआ",
    "market.update_expiry": u"नई समाप्ति ",
    "market.update_expiry_change": u"समाप्ति (पुरानी → नई)",
    "market.update_no_change": (
        u"कोई बदलाव नहीं — मूल्य, राशि या समाप्ति संपादित करें।"
    ),
    "market.update_price": u"नया मूल्य ",
    "market.update_price_change": u"मूल्य (पुराना → नया)",
    "market.update_review": u"अपडेट की समीक्षा करें",
    "market.update_title": u"ऑर्डर समायोजित करें",

    # ======================================================= market_net (36)
    "market_net.asset_1_field": u"एसेट 1 (कोई भी पक्ष)",
    "market_net.asset_2_field": u"एसेट 2 (कोई भी पक्ष)",
    "market_net.band_title": u"मार्केट नेटवर्क",
    "market_net.canvas_label": (
        u"मार्केट नेटवर्क मानचित्र। मार्केट खोलने हेतु Enter दबाएँ।"
    ),
    "market_net.clear_btn": u"साफ़ करें",
    # The short column heads reuse the stats-tab wording verbatim: "24h मात्रा"
    # is market.stat_vol, and col_change / chg_label / stat_chg stay the
    # "24h Δ" data glyphs every other locale also leaves alone.
    "market_net.col_last": u"अंतिम",
    "market_net.col_market": u"मार्केट",
    "market_net.col_vol": u"24h मात्रा",
    "market_net.collapse": u"संकुचित करें",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24घंटे %(fills)s फिल"
    ),
    "market_net.empty": u"इस फ़िल्टर हेतु कोई मार्केट नहीं मिला।",
    "market_net.expand": u"विस्तार करें",
    "market_net.list_btn": u"मार्केट सूचीबद्ध करें",
    "market_net.loading": u"मार्केट लोड हो रहे हैं…",
    "market_net.map_empty": u"हाल की मात्रा वाला कोई मार्केट नहीं।",
    "market_net.map_fallback": (
        u"%(pairs)s जोड़ियाँ · %(assets)s एसेट्स · 24घंटे फिल की पुष्टि नहीं"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s जोड़ियाँ · %(assets)s एसेट्स · 24घंटे फिल"
    ),
    "market_net.map_ready": u"%(markets)s मार्केट · %(assets)s एसेट्स",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s मार्केट",
    "market_net.offline": (
        u"नेटवर्क अनुपलब्ध — कैश किए गए मार्केट दिखाए जा रहे हैं। जुड़ने पर पुनः "
        u"प्रयास करें।"
    ),
    "market_net.open_desk": u"%(id)s खोलें",
    "market_net.prompt": (
        u"एसेट हेतु नोड पर, मार्केट हेतु लाइन पर टैप करें।"
    ),
    "market_net.ramp": u"24घंटे मात्रा: कम → अधिक",
    "market_net.ramp_fills": u"24घंटे फिल: कम → अधिक",
    "market_net.selector_title": u"मार्केट चयनकर्ता",
    "market_net.spark_label": u"%(id)s हेतु 7-दिनीय रुझान",
    "market_net.subtitle": (
        u"24घंटे मात्रा के अनुसार शीर्ष ऑर्डर-बुक मार्केट। डेस्क खोलने हेतु पंक्ति "
        u"चुनें।"
    ),
    "market_net.title": u"मार्केट",
    "market_net.top_note": (
        u"24घंटे मात्रा के अनुसार जाँचे गए %(probed)s में से शीर्ष %(shown)s।"
    ),
    "market_net.twin": u"मार्केट पंक्तियाँ (%(n)s)",
    "market_net.twin_more": (
        u"%(n)s मार्केटों में से %(shown)s दिखाई जा रही हैं — कम देखने हेतु "
        u"फ़िल्टर संकीर्ण करें।"
    ),
    "market_net.verdict_full": u"%(markets)s मार्केट · %(assets)s एसेट्स",
    "market_net.verdict_no_path": (
        u"%(a)s और %(b)s के बीच भरे गए मार्केटों से कोई मार्ग नहीं"
    ),
    "market_net.verdict_path": (
        u"%(a)s, %(n)s भरे गए मार्केटों में %(b)s तक पहुँचता है"
    ),
    "market_net.verdict_star": u"%(s)s से जुड़े मार्केट: %(n)s",
    "market_net.verdict_web": u"%(s)s से पहुँचने योग्य मार्केट: %(n)s",

    # ========================================================== settings (48)
    "settings.age_s": u"%(n)s सेकंड",
    "settings.confirm_back": u"वापस",
    "settings.confirm_remove_action": u"कार्रवाई",
    "settings.confirm_remove_hide": (
        u"यह नोड छिपाएँ (पुनः जोड़ने तक छिपा रहेगा)"
    ),
    "settings.confirm_remove_result": u"परिणाम",
    "settings.confirm_remove_switch": u"सक्रिय नोड %(node)s पर जाएगा",
    "settings.confirm_remove_title": u"नोड हटाएँ?",
    "settings.confirm_remove_unlist": u"मेरी सूची से हटाएँ",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**नोड खोजें GitHub पर नोड सूचियाँ खोजता है, फिर जो मिलता है उसकी "
        u"जाँच करता है। GitHub और जाँचे गए नोड आपका नेटवर्क पता देखते हैं। "
        u"परिणाम आपकी समीक्षा हेतु उम्मीदवार हैं — कुछ भी स्वतः नहीं जोड़ा जाता।"
    ),
    "settings.geo_note": (
        u"*स्थान और प्रदाता ipaddress.to (https, कोई कुंजी नहीं) से आते हैं — "
        u"यह पूछे पर आपका पता देखता है; उत्तर इस डिवाइस पर 24 घंटे कैश रहते "
        u"हैं।"
    ),
    "settings.hist_no": u"नहीं",
    "settings.hist_yes": u"हाँ",
    "settings.language_title": u"भाषा",
    # Signing section. एक्सटेंशन is this batch's first spelling of the browser
    # extension in hi.json (the way 扩展 was zh's and расширение ru's);
    # लॉगिन is the spelling account.gate_login already ships; अनुमोदन reuses
    # the proposal wording and निरस्त the signing-approval wording.
    "settings.sign_auto": u"स्वचालित (उपलब्ध होने पर एक्सटेंशन)",
    "settings.sign_badge": u"एक्सटेंशन हस्ताक्षर सक्रिय — विवरण लॉगिन में",
    "settings.sign_badge_local": u"इस पृष्ठ पर हस्ताक्षर — विवरण लॉगिन में",
    "settings.sign_browser": u"हमेशा इस पृष्ठ पर हस्ताक्षर करें",
    "settings.sign_ext": u"हमेशा एक्सटेंशन का उपयोग करें",
    "settings.sign_ext_absent": (
        u"इस डिवाइस पर कोई एक्सटेंशन नहीं मिला — हस्ताक्षर इस पृष्ठ पर होंगे।"
    ),
    "settings.sign_ext_present": u"इस डिवाइस पर एक्सटेंशन मिला।",
    "settings.sign_guide": u"एक्सटेंशन कैसे संस्थापित करें",
    "settings.sign_mode_browser": u"हस्ताक्षर इस पृष्ठ की मेमोरी में होते हैं।",
    "settings.sign_mode_ext": u"हस्ताक्षर एक्सटेंशन विंडो में अनुमोदित होते हैं।",
    "settings.sign_mode_ext_page": (
        u"हस्ताक्षर एक्सटेंशन में ही रहते हैं — वेबसाइटों से पृथक।"
    ),
    "settings.sign_revoke": u"निरस्त करें",
    "settings.sign_sites": u"जुड़े हुए साइट",
    "settings.sign_sites_empty": (
        u"अभी कोई साइट अनुमोदित नहीं — अनुमोदन यहाँ प्रति-साइट निरस्ती सहित "
        u"दिखेंगे।"
    ),
    # The trailing space on story_a is load-bearing: story_b follows it (G4b).
    "settings.sign_sites_story_a": u"उदाहरण: किसी साइट पर डाइस गेम ",
    "settings.sign_sites_story_b": (
        u" आपके खाते से खेलने का अनुरोध करता है — अनुमोदन इसे यहाँ सूचीबद्ध करेगा, "
        u"केवल उसी खाते से बँधा। फिर भी हस्ताक्षर हर बार पूछे जाते हैं। (वह "
        u"लिंक कहीं नहीं जाता — यह काल्पनिक उदाहरण है।)"
    ),
    "settings.sign_title": u"हस्ताक्षर",
    "settings.sign_warn": (
        u"इस पृष्ठ पर चलने वाला कोई भी स्क्रिप्ट — संक्रमित होस्ट कॉपी सहित — "
        u"अनलॉक रहने पर आपकी कुंजियाँ पढ़ सकता है। हस्ताक्षर एक्सटेंशन से करवाएँ, "
        u"या ऐसी कॉपी चलाएँ जिस पर आपका नियंत्रण हो।"
    ),
    # Node-table column heads. स्थान / प्रदाता reuse the geo-note wording the
    # settings help article already ships; पिंग is settings.probe_all's verb.
    "settings.th_chain": u"चेन",
    "settings.th_handshake": u"हैंडशेक",
    "settings.th_head": u"हेड",
    "settings.th_history": u"हिस्ट्री",
    "settings.th_location": u"स्थान *",
    "settings.th_participation": u"भागीदारी",
    "settings.th_ping": u"पिंग",
    "settings.th_provider": u"प्रदाता *",
    "settings.theme_title": u"थीम",
}

# Keys whose Hindi value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from HI. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Hindi crypto UI keeps in Latin: HTLC, NFT, URI,
#     MCR, PMA, UIA, the indicator tickers BB / EMA / PSAR / SMA, Op (the
#     operation-number column head - de, es, fr, it, pt and ko all keep it);
#   * network ids, theme ids and sentinels the brief pins: mainnet / testnet /
#     devnet, original-blue / light / dark, "wss://…", "…", "—", "7d";
#   * the "24h Δ" data glyphs (market.chg_label, market.stat_chg,
#     market_net.col_change) - a number, a unit and the Greek delta, which the
#     stats tab, the volume column and the map legend all print the same way;
#   * pure glue a table cell or edge card prints as data: "@ %(price)s ·
#     %(vol)s", "%(desk)s · %(a)s–%(b)s · %(vol)s", "%(first)s → %(last)s",
#     "@ %(price)s", "—" - translating the space inside a glue string would
#     change what the reader sees, so it stays English;
#   * the seed placeholder, which is real account names plus a 1.2.x id and so
#     is DATA under rule 1.
KEPT_ENGLISH = {
    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    # ---- asset
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.nft_uri_field": u"NFT URI",
    "asset.op_col": u"Op",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    # ---- market
    "market.chg_label": u"24h Δ",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_chg": u"24h Δ",
    "market.stat_empty": u"—",
    # ---- market_net
    "market_net.col_change": u"24h Δ",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    # ---- settings
    "settings.custom_placeholder": u"wss://…",
    "settings.dash": u"—",
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.pending": u"…",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",
}


if __name__ == "__main__":
    sys.exit(main())
