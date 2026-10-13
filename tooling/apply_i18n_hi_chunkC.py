#!/usr/bin/env python3
"""i18n hi chunk-C: fill the signing / desk tail hi.json still leaves in English.

Scope: ONLY the thirty-eight sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key holding this batch's translation is skipped (re-runnable);
  * a key missing from hi.json, or one whose English master moved, is REFUSED;
  * HI + KEPT_ENGLISH together must account for EVERY untranslated key of the
    thirty-eight sections, so a forgotten string is a refusal, never a silent
    English.

chunk-A owns account, account_net, settings, market, market_net and asset;
chunk-B owns help, pool, pool_net, explorer, seo, splash, about, shell, menu
and i18n. This batch owns everything else that was still English - which is the
SIGNING surface first (approval, auth/multisig, barter, borrow, credit, debit,
htlc, instant, prediction, proposal, transfer, trade, txbuilder, unlockconfirm,
vote), then the read-only desks that surround it (xrate, pool_detail, tour,
trollbox, dashboard, nav, ...) and the shared widgets (common, forms hints).
`i18n.badge_chip` is re-declared here only because chunk-B already shipped it as
deliberately English and this batch's coverage gate needs to account for it.

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
                      Two values in this batch are multi-line - but both are
                      KEPT_ENGLISH data samples (misc.invoice_lines_placeholder
                      "coffee|1.5\ncake|2", ticket.airdrop_example_ph
                      "alice,10\nbob,2.5"), so this batch writes no multi-line
                      value at all and the gate is a regression tripwire;
  G4b edge spaces   leading / trailing whitespace of the English master is
                      reproduced exactly. TEN values in this batch are GLUE with
                      a load-bearing blank - approval.account / chain /
                      site_prefix / expires_in, barter.paid_by_suffix,
                      proposal.raw_prefix, vote.fee_core, vote.proxy_follows,
                      xrate.load_failed, xrate.remove_btn, gateway.intro_a -
                      where a missing space welds the computed value onto the
                      label or onto the sentence above it;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an unclaimed key must still equal en;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  script         no Cyrillic and no CJK letter may appear in any value
                      THIS BATCH writes. Hindi is Devanagari; a stray Cyrillic
                      or Han character is a copy-paste from a sibling locale, not
                      a Hindi word. The whole file is swept and a hit OUTSIDE
                      these thirty-eight sections is reported as PRE-EXISTING
                      rather than repaired - chunks A/B own those keys;
  G7b quotes         no ASCII or typographic apostrophe in a value this batch
                      writes. Two ENGLISH masters in scope carry one
                      (barter.two_sided_atomic_swap... "both sides' transfers",
                      vote.proxies_follow_another_account... "account's vote
                      slate"); Hindi puts the case after the noun, so both are
                      re-spelled with a postposition and no apostrophe. The
                      whole file already has no apostrophe in any translated
                      string, so a stray one would be the only such spelling in
                      the dictionary;
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale - except inside an algebraic notation where both
                      neighbours are alphanumeric (pool.list_sub ships
                      "x*y=k", outside this batch). Three values here carry a
                      middle dot (pool_detail.candle_count,
                      pool_detail.candle_count_partial, xrate.status) and all
                      three keep the English separator;
  G9  loanwords      every Latin token a value THIS BATCH writes must be
                      declared in LOAN below, or already occur in the ENGLISH
                      master of that same key (which is how DATA - a field name,
                      an object id - legitimately stays Latin). Anything that
                      leans on the English-source clause rather than on LOAN is
                      printed, so a reviewer can see the difference instead of
                      guessing. Hindi crypto UIs keep the English word for DEX,
                      HTLC, API, ES, SMA/EMA/RSI/MACD, WebCrypto - inventing a
                      fake Devanagari transliteration instead would be worse
                      than the loanword, because the reader already searches for
                      the Latin string.

Register is FORMAL (aap) - the standard for Hindi financial software - matching
the confirmed probe run and chunks A and B.

Vocabulary is reused verbatim from the 3718 strings hi.json already ships and
from tooling/probe_runs/hi-runB-nemotron3.json, so this batch reads like the
rest of the dictionary rather than inventing a second dialect:

  * the six probe-run answers that match a key in this batch are used
    byte-for-byte: T02 "हस्ताक्षर हेतु अनलॉक करें" (all seven *_uc_title
    "Unlock to sign" keys), T01 "अपना वॉलेट पासवर्ड डालें।", T03/T04 "पासवर्ड" /
    "हैश एल्गोरिदम", T10 "स्वीकृत और प्रसारित।";
  * pool.uc_title already ships "जारी रखने हेतु अनलॉक करें", so trade.uc_title
    and transfer.uc_title ("Unlock to continue") reuse it verbatim;
  * trade.unlock_review ships "अनलॉक और समीक्षा करें", which is exactly what
    transfer.unlock_sign ("Unlock & review") asks for;
  * market.map_connects / market.map_connects_fallback already ship the
    "निधि-पूर्ण पूल ... एक लाइन दो एसेट्स को जोड़ती है" sentence pair, and
    pool_detail.map_connects / _fallback carry the IDENTICAL English strings, so
    this batch reuses that Hindi instead of coining a third wording;
  * viewing.notice_locked already ships the exact shape proposal.viewing_as
    needs, and borrow.barter.transfer.credit all ship the same "— ... अनलॉक
    करें।" tail;
  * the X की पुष्टि करें (op N) family (misc, vesting, proposal) sets the shape
    for every confirm_* title here; proposal.unlock, proposal.approve, create-
    account.name, debit's "ऑर्डर" and trollbox's "भाषा" set the rest.

Numbers: no amount is retyped in a translated string - a bare value is `Format`'s
job (AGENTS.md 3.5) - and every number the English quotes is kept byte-verbatim
(op 3 / 22 / 23 / 24 / 34 / 45, 1.10.N, 3 hops, 6 pool hops, 24h, 1024, 5000).

Direction is the load-bearing part of this batch and is spelled out rather than
compressed. Hindi drops postpositions, so each of these keeps the marker that
carries the truth:

  * "cannot be cancelled - they execute or expire" -> "रद्द नहीं की जा सकतीं —
    या तो निष्पादित होती हैं या समाप्त हो जाती हैं" (an explicit दो-विकल्प, so
    the reader cannot read "execute" as the only outcome);
  * "executes only after approvals" -> "केवल अनुमोदनों के बाद ही निष्पादित होता
    है" (the ही is what forbids "before");
  * "Proposer defaults to X while locked" -> "लॉक रहने पर प्रस्तावक X रहता
    है" (किस X ने signing नहीं कहा);
  * "workers are created by direct op, NOT by proposal" -> "प्रस्ताव से नहीं,
    सीधे op से बनते हैं";
  * "the node rejected proxy mode, so the vote was published as self" -> "नोड
    ने ... अस्वीकार कर दिया, इसलिए मत स्वयं के रूप में प्रकाशित किया गया" (the
    cause sits before the consequence, with इसलिए);
  * "Previewing as X - balances not checked" -> "बैलेंस जाँचे नहीं गए हैं"
    (जाँचे, not जाँच; and the imperative to unlock comes AFTER, as in English);
  * "No route to X within 6 pool hops" -> "X तक 6 पूल हॉप के भीतर कोई मार्ग
    नहीं" (मार्ग is the noun, कोई ... नहीं the negation - "कोई मार्ग नहीं", never
    "मार्ग नहीं" alone);
  * "A leg on this route has no recorded swap yet" -> "इस मार्ग की एक लेग का
    अभी तक कोई दर्ज स्वैप नहीं है" (अभी तक bounds the "yet").

Two strings the brief names as comparison traps have no counterpart in this
batch's slice: no string here compares an amount with zero, so the
"शून्य से अधिक" vs "कम" inversion has nothing to get wrong. Where a count IS
partial ("%(actual)s of %(requested)s") the Hindi is "X में से Y", which keeps
the numerator and denominator attached to their own placeholders so a wrong
order cannot silently reverse a count.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_hi_chunkC.py                 # dry run (asserts)
  python3 tooling/apply_i18n_hi_chunkC.py --apply         # writes hi.json
  python3 tooling/apply_i18n_hi_chunkC.py --verify        # structural re-proof
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

# The thirty-eight sections this batch owns. Everything else belongs to chunk-A
# (six sections) and chunk-B (ten sections) and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "apilab", "approval", "assets_feed", "auth", "barter", "borrow", "common",
    "compat", "createaccount", "createworker", "credit", "dashboard", "debit",
    "eslab", "explorer_assets", "gateway", "htlc", "i18n", "instant",
    "market_ind", "misc", "nav", "news", "pool_detail", "pools", "prediction",
    "proposal", "ticket", "tour", "trade", "transfer", "trollbox", "txbuilder",
    "unlockconfirm", "vesting", "viewing", "vote", "xrate",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from HI below so they keep the
# English bytes, and the verify pass re-asserts every one after the write. None
# of them live in this batch's own sections except i18n.badge_chip, which is
# therefore also listed in KEPT_ENGLISH. The chunk-A/B sections are listed here
# only so a drift anywhere in the file is caught.
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
# _ . / so "Same-T", "call_order_update" and "voting_account" are one decision
# each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word or symbol a Hindi crypto UI prints in Latin; anything else has to be
# Devanagari.
LOAN = frozenset((
    # --- chain / protocol vocabulary
    "BTS",            # the core asset ticker (xrate.base_pinned, xrate.empty,
                       # xrate.title's own sentence) - chunk-A declared it too
    "op",             # the operation marker in every "(op %(op)s)" confirm
                       # title and in the two prose notes that name it - both
                       # chunks declared it as a loanword
    "call_order_update",  # the BitShares operation name borrow.margin_positions
                       # spells out so the reader can match it in the chain
    # --- desk / lab names
    "API",            # API Lab (apilab.title); the help article chunk-B wrote
                       # already links "[API लैब](#/api-lab)"
    "ES",             # ES Lab (eslab.title), same reason
    # --- the barter wizard's own step button, named in CAPITALS by English
    "PROPOSE",        # barter.two_sided_atomic_swap... names the button the
                       # reader has to press; the button itself is "प्रस्तावित
                       # करें", so the Latin here is the on-screen step name
    # --- indicator names a chart reader looks up in Latin
    "SMA",            # tour.s3_body
    "EMA",            # tour.s3_body
    "RSI",            # tour.s3_body
    "MACD",           # tour.s3_body
    # --- platform names inside compat prose, never prose themselves
    "WebCrypto",      # compat.insecure_hint names the API the browser withholds
    "localhost",      # ... and the second origin that unlocks it
    "https",          # ... and the scheme to serve under
    # --- single-letter leg labels of a pool / barter side. barter.side_a and
    # barter.side_b already ship "पक्ष A" / "पक्ष B", so A and B stay Latin.
    "A",              # pool_detail.invert_label
    "B",              # pool_detail.invert_label, and the fee-payer in barter
    # --- the chain field name printed verbatim inside two voting notes, so the
    # reader can grep the node for it
    "voting_account",
    # --- the Graphene placeholder-object-id suffix, as in 1.10.N: a token, not
    # a word, and the id it decorates is already quoted in full
    "N",
    "x",             # the same, in 1.3.x (common.symbol_or_id_hint)
    # --- "id" is the object-id field name. It is NOT prose: the shipped
    # dictionary already writes "प्रस्ताव id", "बैलेंस id", "खाता या प्राधिकरण
    # id" - a Devanagari word for it would break the correspondence with the
    # chain's own column names, so it stays Latin here as it does everywhere.
    "id",
))
# Tokens that reached G9 only because the ENGLISH master of the same key already
# contains them. Nothing should land here permanently; the run prints whatever
# does so a reviewer can audit the distinction instead of trusting it. LOAN
# above is written so this list is expected to stay EMPTY - every Latin run in
# this batch is either a declared loanword or a declared chain identifier.
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
    # are printed loudly and never repaired here: chunks A/B own them, and an
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
          % len([k for k in honesty if d.get(k) == e[k]]))
    for k in honesty:
        print("      %-46s %s" % (k, "ENGLISH" if d.get(k) == e[k]
                                  else "translated"))
    # The signing surface is the point of this batch: list anything still at
    # English so a reviewer sees the residue without diffing the file.
    signing = sorted(k for k in e
                     if k.split(".")[0] in SECTIONS
                     and ("_uc_" in k or k.endswith(".uc_title")
                          or k.startswith("approval.")
                          or k.startswith("proposal.")
                          or k.startswith("vote.")
                          or k.startswith("transfer.")
                          or k.startswith("unlockconfirm."))
                     and d.get(k) == e[k])
    print("  signing-surface keys still identical to en: %d" % len(signing))
    for k in signing:
        print("      %-46s ENGLISH" % k)
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
    # values kept byte-identical on purpose (loanwords, brands, ids, glue,
    # data samples) stay UNCLAIMED, which is the honest state for them. Nothing
    # else in _meta moves - filling strings is not verification.
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

    print("hi chunk-C: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-16s %d" % (sec, by_section.get(sec, 0)))
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
    # ============================================================== approval (20)
    # The extension-wrapper approval dialog: the one place a site asks this
    # wallet to sign, so the wording is deliberately flat and complete. T10 of
    # the confirmed probe run is used byte-for-byte.
    "approval.account": u"खाता: ",
    "approval.approve": u"अनुमोदन करें",
    "approval.approved": u"स्वीकृत और प्रसारित।",
    "approval.chain": u"चेन: ",
    "approval.close": u"बंद करें",
    "approval.deny": u"अस्वीकृत करें",
    "approval.denied": u"अस्वीकृत।",
    "approval.expires_in": u"समाप्त होने में ",
    "approval.load_failed": u"अनुमोदन लोड नहीं हो सका।",
    "approval.loading": u"अनुमोदन लोड हो रहा है…",
    "approval.locked_note": (
        u"सत्र लॉक है — अनुमोदन हेतु अपना वॉलेट पासवर्ड डालें।"
    ),
    "approval.no_fields": u"कोई दिखाने योग्य फ़ील्ड नहीं।",
    "approval.no_reply": u"साइनर से कोई उत्तर नहीं मिला।",
    "approval.no_runtime": u"एक्सटेंशन रनटाइम अनुपलब्ध।",
    "approval.password": u"पासवर्ड",
    "approval.remember": u"इस साइट हेतु यह खाता याद रखें",
    "approval.site_prefix": u"साइट: ",
    "approval.title": u"हस्ताक्षर अनुमोदित करें",
    "approval.unknown_intent": u"कोई अनुमोदन अनुरोध नहीं मिला।",
    "approval.wallet_title": u"यह वॉलेट हस्ताक्षर का अनुरोध कर रहा है",

    # ================================================================= auth (7)
    # Multisig: three ordered steps plus the body. "Co-owner" is सह-स्वामी
    # (the same word the asset section already ships for the same idea), and
    # the closing clause keeps the reading order intact - public browsing, then
    # the password only at signing.
    "auth.multisig_body": (
        u"यह वॉलेट एक ही कुंजी रखता है। साझा खातों हेतु प्रस्ताव + सह-स्वामी अनुमोदन "
        u"चाहिए, जिनका समन्वय प्रस्ताव id (1.10.N) से होता है। ब्राउज़िंग सार्वजनिक "
        u"है; पासवर्ड केवल हस्ताक्षर हेतु चाहिए।"
    ),
    "auth.multisig_open_proposals": u"प्रस्ताव देखें",
    "auth.multisig_open_txbuilder": u"लेनदेन निर्माता खोलें",
    "auth.multisig_step_approve": (
        u"सह-स्वामी प्रस्ताव पेज पर (op 23) अनुमोदन करते हैं, या लेनदेन निर्माता से "
        u"सह-हस्ताक्षर करते हैं।"
    ),
    "auth.multisig_step_propose": (
        u"ऑपरेशन प्रस्तावित करें (ट्रांसफर में भेजें/प्रस्तावित करें है; एसेट, बार्टर "
        u"और उधार प्रस्तावों से जुड़ते हैं)।"
    ),
    "auth.multisig_step_share": u"1.10.N प्रस्ताव id सह-स्वामियों के साथ साझा करें।",
    "auth.multisig_title": u"साझा / मल्टीसिग खाते",

    # ================================================================ barter (8)
    # The step names are the wizard's own tab labels. barter.propose_encloses_both
    # (already translated) supplies the "शुल्क-भुगतानकर्ता" wording, so the two
    # sentences about the same mechanism read identically.
    "barter.confirm_barter_proposal_op_22": (
        u"बार्टर प्रस्ताव की पुष्टि करें (op %(op)s)"
    ),
    "barter.propose_barter_op_22": u"बार्टर प्रस्तावित करें (op %(op)s)",
    "barter.step_build": u"बनाएँ",
    "barter.step_preview": u"प्रीव्यू",
    "barter.step_propose": u"प्रस्तावित करें",
    # "both sides' transfers" -> "दोनों पक्षों के ट्रांसफर": the postposition does
    # the possessive work an apostrophe would do in English.
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"दोनों पक्षों वाला एटॉमिक स्वैप प्रीव्यू। पहले प्रीव्यू देखें, फिर PROPOSE "
        u"दोनों पक्षों के ट्रांसफर एक ही प्रस्ताव में op के रूप में संलग्न करता है "
        u"(op %(op)s, शुल्क-भुगतानकर्ता = पीयर A)।"
    ),
    "barter.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # ================================================================ borrow (9)
    "borrow.adjust": u"समायोजन करें",
    "borrow.adjust_position_op_3": u"पोज़ीशन समायोजित करें (op %(op)s)",
    # Irreversibility. "या तो ... या" keeps both outcomes explicit so the reader
    # cannot take "execute" as the only one.
    "borrow.bids_no_cancel": (
        u"बोलियाँ लगाने के बाद रद्द नहीं की जा सकतीं — वे या तो निष्पादित होती हैं "
        u"या समाप्त हो जाती हैं।"
    ),
    "borrow.close_position": u"पोज़ीशन बंद करें",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"मार्जिन पोज़ीशन कोलैटरल के विरुद्ध बिटएसेट उधार लेती हैं। कोलैटरल बढ़ाने "
        u"या कर्ज़ चुकाने पर आपके कॉल ऑर्डर पर op %(op)s (call_order_update) "
        u"समायोजित होता है।"
    ),
    "borrow.open_a_new_position_op_3": u"नई पोज़ीशन खोलें (op %(op)s)",
    "borrow.repay_full": u"पूर्ण रूप से चुकाएँ",
    "borrow.settlement_bids_op_45": u"सेटलमेंट बोलियाँ (op %(op)s)",
    "borrow.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # ================================================================ common (5)
    "common.name_or_id_hint": u"नाम या 1.2.N",
    "common.page_n": u"पेज %(n)s",
    "common.symbol_or_id_hint": u"प्रतीक या 1.3.x",
    "common.unknown_asset": u"अज्ञात एसेट।",
    "common.unlock_failed": u"अनलॉक असफल।",

    # ================================================================ compat (1)
    "compat.insecure_hint": (
        u"यह पता सुरक्षित संदर्भ नहीं है, इसलिए ब्राउज़र WebCrypto उपलब्ध नहीं कराता। "
        u"ब्राउज़र अद्यतन है — https या localhost से परोसें, या फ़ाइल सीधे खोलें।"
    ),

    # ========================================================== createaccount (3)
    "createaccount.step_brainkey": u"ब्रेनकी",
    "createaccount.step_name": u"नाम",
    "createaccount.step_register": u"पंजीकृत करें",

    # =========================================================== createworker (4)
    "createworker.confirm_worker_op_34": u"वर्कर की पुष्टि करें (op %(op)s)",
    # The load-bearing clause is the LAST one and it is the one that must not be
    # lost: workers are created by a direct op, NOT by proposal. Hindi keeps the
    # contrast explicit with "प्रस्ताव से नहीं, सीधे op से".
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"वर्कर का मसौदा तैयार करें (op %(op)s)। प्रीव्यू लाइव है; समीक्षा में लाइव शुल्क "
        u"बताया जाता है, फिर साइन और भेजें op %(op)s को सीधे प्रसारित करता है — वर्कर "
        u"प्रस्ताव से नहीं, सीधे op से बनते हैं।"
    ),
    "createworker.worker_preview_op_34": u"वर्कर प्रीव्यू (op %(op)s)",

    # =============================================================== credit (3)
    "credit.my_deals_borrower": u"मेरे डील (उधारकर्ता)",
    "credit.no_borrower_deals": (
        u"अभी कोई उधारकर्ता डील नहीं — किसी ऑफ़र के विरुद्ध उधार लेने के बाद डील "
        u"दिखाई देती हैं।"
    ),
    "credit.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # ============================================================ dashboard (2)
    "dashboard.tagline": u"मार्केट निःशुल्क देखें — ट्रेड हेतु वॉलेट बनाएँ।",
    "dashboard.welcome": u"उन कुंजियों से BTS में ट्रेड करें जो आपके पास हैं",

    # ================================================================= debit (2)
    "debit.uc_order": u"ऑर्डर",
    "debit.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # ================================================================= eslab (2)
    "eslab.hint_donors": (
        u"विंडो पर गिनती; कुल रॉ पूर्णांक हैं — एसेट परिशुद्धता से भाग दें।"
    ),
    "eslab.title": u"ES लैब",

    # ========================================================= explorer_assets (1)

    # =============================================================== gateway (2)
    "gateway.intro_a": (
        u"बाहरी कॉइन दिखाए गए पते पर भेजें। यह पेज कुछ नहीं भेजता। "
    ),
    "gateway.intro_b": (
        u"निकासी ट्रांसफर में लाइव शुल्क पूर्वावलोकन के साथ पूरी होती है।"
    ),

    # ================================================================== htlc (3)
    "htlc.list_sub": (
        u"धन को किसी हैश में लॉक करें — प्राप्तकर्ता समाप्ति से पहले गुप्त शब्द से "
        u"रिडीम करता है, या आपको रिफ़ंड मिलता है। कोई भी पढ़ सकता है; पासवर्ड केवल "
        u"हस्ताक्षर हेतु माँगा जाता है।"
    ),
    "htlc.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # =================================================================== i18n (1)
    # The literal tag the header chip prints; chunk-B already declared it.

    # =============================================================== instant (3)
    # "balances not checked" is a warning, so it is a completed statement
    # ("जाँचे नहीं गए हैं"), not a noun phrase the reader could scan past.
    "instant.preview_balances_note": (
        u"%(name)s (%(id)s) के रूप में पूर्वावलोकन कर रहे हैं — बैलेंस जाँचे नहीं "
        u"गए हैं। हस्ताक्षर से पहले अपने बैलेंस की पुष्टि हेतु अनलॉक करें।"
    ),
    "instant.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",
    "instant.unlock_sign": u"अनलॉक करें और साइन करें",

    # ============================================================ market_ind (3)
    "market_ind.count_capped": u"विंडो परिसीमित",
    "market_ind.count_note": u"%(count)s × %(bucket)s कैंडल",
    "market_ind.count_partial": (
        u"%(requested)s में से %(actual)s × %(bucket)s कैंडल"
    ),

    # ================================================================== misc (2)

    # ==================================================================== nav (4)
    "nav.credit": u"क्रेडिट",
    "nav.margin": u"मार्जिन",
    "nav.markets": u"मार्केट",
    "nav.pools": u"पूल",

    # ================================================================== news (1)
    "news.explorer_blocks_and_transactions": u"चेन एक्सप्लोर करें",

    # ============================================================ pool_detail (8)
    "pool_detail.candle_capped": u"विंडो परिसीमित",
    "pool_detail.candle_count": u"%(swaps)s स्वैप · %(count)s × %(bucket)s कैंडल",
    "pool_detail.candle_count_partial": (
        u"%(swaps)s स्वैप · %(requested)s में से %(actual)s × %(bucket)s कैंडल"
    ),
    "pool_detail.invert": u"उलटें",
    "pool_detail.invert_label": u"चार्ट की दिशा उलटें (A-प्रति-B / B-प्रति-A)",
    # Reused verbatim from market.map_connects / market.map_connects_fallback,
    # which ship the IDENTICAL English strings, so the market map and the pool
    # desk describe the same rule in the same words.
    "pool_detail.map_connects": (
        u"जब कोई निधि-पूर्ण पूल मौजूद हो और पिछले 24 घंटे में कोई ट्रेड हुआ हो, तो "
        u"एक लाइन दो एसेट्स को जोड़ती है।"
    ),
    "pool_detail.map_connects_fallback": (
        u"जब कोई निधि-पूर्ण पूल मौजूद हो, तो एक लाइन दो एसेट्स को जोड़ती है। 24घंटे "
        u"की ट्रेड गतिविधि की पुष्टि नहीं है (हिस्ट्री अनुपलब्ध) — निधि-पूर्ण पूल "
        u"दिखाए जा रहे हैं।"
    ),
    "pool_detail.map_min_swaps": u"(न्यूनतम %(min)s स्वैप)",

    # ================================================================= pools (1)
    "pools.selector_title": u"पूल चयनकर्ता",

    # ============================================================ prediction (1)
    "prediction.uc_title": u"हस्ताक्षर हेतु अनलॉक करें",

    # ============================================================== proposal (9)
    "proposal.confirm_proposal_create_op_22": (
        u"प्रस्ताव निर्माण की पुष्टि करें (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"प्रस्ताव हटाने की पुष्टि करें (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"प्रस्ताव हटाएँ (op %(op)s)",
    "proposal.multisig_story": (
        u"साझा खाता? एक सह-स्वामी प्रस्तावित करता है, 1.10.N id साझा करता है, शेष "
        u"लोग नीचे अनुमोदन करते हैं। बहु-ऑपरेशन या बहु-डिवाइस कार्य लेनदेन निर्माता "
        u"में जारी रखा जाता है।"
    ),
    "proposal.open_txbuilder": u"लेनदेन निर्माता खोलें",
    "proposal.raw_prefix": u"कच्चा: ",
    "proposal.viewing_as": (
        u"%(name)s (%(id)s) के रूप में देख रहे हैं — स्वयं के रूप में कार्य करने के "
        u"लिए अनलॉक करें।"
    ),

    # ================================================================= ticket (2)

    # ================================================================== tour (7)
    "tour.away_note": (
        u"यह एक्सचेंज डेस्क पर चिह्नित दिखेगा — इसे खोल लें।"
    ),
    "tour.s1_body": (
        u"हर पेज लॉगिन के बिना सार्वजनिक चेन डेटा पढ़ता है। शुरू करने हेतु कोई "
        u"मार्केट खोलें — आपका पासवर्ड केवल हस्ताक्षर के समय माँगा जाता है।"
    ),
    "tour.s1_title": u"सब कुछ निःशुल्क देखें, स्थानीय रूप से हस्ताक्षर करें",
    "tour.s3_body": (
        u"मूल्य कैंडल, मात्रा और गहराई, साथ ही इंडिकेटर मेनू: SMA और EMA जैसे "
        u"ओवरले, तथा RSI, MACD और स्टोकास्टिक जैसे ऑसिलेटर। लाइव देखने हेतु "
        u"एक्सचेंज खोलें।"
    ),
    "tour.s3_title": u"लाइव मूल्य चार्ट देखें",
    "tour.s4_body": (
        u"अभ्यास हेतु खरीदें और बेचें पैनल कोई भी संख्या स्वीकार करते हैं। जब तक "
        u"आप अनलॉक वॉलेट से समीक्षा करके हस्ताक्षर नहीं करते, कुछ भी आपकी मशीन से "
        u"बाहर नहीं जाता। आज़माने हेतु एक्सचेंज खोलें।"
    ),
    "tour.s4_title": u"खरीदना और बेचना अभ्यास करें",

    # ================================================================= trade (7)
    "trade.tab_single": u"सिंगल",
    "trade.uc_amount": u"राशि",
    "trade.uc_orders": u"ऑर्डर",
    "trade.uc_price": u"मूल्य",
    "trade.uc_range": u"मूल्य सीमा",
    "trade.uc_title": u"जारी रखने हेतु अनलॉक करें",
    "trade.uc_total": u"बेचने की कुल राशि",

    # ============================================================== transfer (6)
    "transfer.confirm_proposal_title": u"प्रस्ताव की पुष्टि करें (op %(op)s)",
    # "only after approvals" -> "केवल अनुमोदनों के बाद ही": the ही is what forbids
    # the reader taking it as "before".
    "transfer.enclosed_op_note": (
        u"संलग्न op: ट्रांसफर (op %(op)s) — केवल अनुमोदनों के बाद ही निष्पादित होता "
        u"है।"
    ),
    # "Proposer defaults to X while locked" -> "लॉक रहने पर प्रस्तावक X रहता है":
    # it says who signs, not who merely appears in a field.
    "transfer.propose_notice_locked": (
        u"लॉक रहने पर प्रस्तावक %(name)s (%(id)s) रहता है — स्वयं के रूप में कार्य "
        u"करने हेतु अनलॉक करें।"
    ),
    "transfer.share_needs_to_amount": (
        u"साझा करने योग्य लिंक हेतु प्राप्तकर्ता और राशि चाहिए।"
    ),
    "transfer.uc_title": u"जारी रखने हेतु अनलॉक करें",
    "transfer.unlock_sign": u"अनलॉक और समीक्षा करें",

    # ============================================================== trollbox (8)
    "trollbox.bytes_unit": u"बाइट्स",
    "trollbox.channel_row": u"चैनल",
    "trollbox.fee": u"शुल्क",
    "trollbox.language_row": u"भाषा",
    "trollbox.message_row": u"संदेश",
    "trollbox.post_review_title": u"संदेश की समीक्षा करें",
    "trollbox.size_row": u"आकार",
    "trollbox.unlock_post": u"अनलॉक करें और पोस्ट करें",

    # ============================================================== txbuilder (5)
    "txbuilder.link_pools": u"पूल",
    "txbuilder.link_proposals": u"प्रस्ताव",
    "txbuilder.link_transfer": u"ट्रांसफर",
    "txbuilder.link_voting": u"वोटिंग",

    # ========================================================== unlockconfirm (5)
    # T01 of the confirmed probe run, byte-for-byte.
    "unlockconfirm.cancel": u"वापस",
    "unlockconfirm.empty_password": u"अपना वॉलेट पासवर्ड डालें।",
    "unlockconfirm.password": u"पासवर्ड",
    "unlockconfirm.unlock_failed": u"अनलॉक असफल।",
    "unlockconfirm.unlock_post": u"अनलॉक करें और पोस्ट करें",

    # ================================================================ vesting (1)

    # =============================================================== viewing (1)
    # A format sample: chain account names are ASCII, so a Devanagari example
    # would be a name nobody can type. Kept in Latin on purpose.

    # ================================================================= vote (10)
    "vote.ballot_intro": (
        u"आपकी स्टेक विटनेस व कमेटी का चुनाव करती है और वर्करों को धन देती है — "
        u"नीचे दी गई हर गिनती व हिस्सा लाइव चेन पठन है।"
    ),
    "vote.confirm_witness_update_op_21": (
        u"विटनेस अद्यतन की पुष्टि करें (op %(op)s)"
    ),
    "vote.direct_note": (
        u"वोटिंग सीधे प्रकाशित की गई (voting_account %(id)s)।"
    ),
    "vote.fee_core": u" (कोर)",
    "vote.in_sync": (
        u"वोट स्लेट चेन से मेल खाती है — प्रकाशित करने हेतु कोई परिवर्तन नहीं है।"
    ),
    # "another account's vote slate" -> "किसी अन्य खाते के वोट स्लेट": the
    # postposition replaces the apostrophe and keeps the ownership explicit,
    # which is the whole warning.
    "vote.proxies_follow_another_account_s_slate_re": (
        u"प्रॉक्सी किसी अन्य खाते के वोट स्लेट का अनुसरण करते हैं — कोई प्रॉक्सी सेट "
        u"करने से पहले पढ़ लें कि वोटिंग किस प्रकार कार्य करती है।"
    ),
    "vote.proxy_follows": (
        u" — आपकी स्टेक इस खाते का अनुसरण करती है; नीचे दी गई वोट स्लेट केवल-पठन "
        u"है।"
    ),
    # Cause before consequence, joined by इसलिए: the reader must not miss that
    # the vote went out as SELF, not through the proxy.
    "vote.retried_prefix": (
        u"नोड ने %(mode)s प्रॉक्सी मोड अस्वीकार कर दिया, इसलिए मत स्वयं के रूप में "
        u"प्रकाशित किया गया (voting_account %(id)s)।"
    ),
    "vote.retry_self": (
        u"नोड ने %(mode)s प्रॉक्सी मोड अस्वीकार कर दिया — स्वयं के रूप में एक बार "
        u"पुनः प्रयास किया जा रहा है…"
    ),

    # ================================================================= xrate (18)
    "xrate.add_btn": u"कॉलम जोड़ें",
    "xrate.asset_col": u"एसेट",
    "xrate.base_pinned": u"BTS आधार कॉलम है और इसे हटाया नहीं जा सकता।",
    "xrate.empty": u"इस चेन पर BTS से 3 हॉप के भीतर कोई पूल एसेट नहीं।",
    "xrate.intro": (
        u"हर पूल एसेट उसके अंतिम स्वैप मूल्य पर आँका गया है और पूल ग्राफ़ से आर-पार "
        u"गिना गया है। कुछ भी हस्ताक्षरित नहीं होता और कुछ भी संग्रहीत नहीं होता।"
    ),
    "xrate.load_failed": u"क्रॉस दरें लोड नहीं हो सकें: ",
    "xrate.loading": u"पूल पढ़े जा रहे हैं…",
    # "No route to X within 6 pool hops": कोई ... नहीं keeps the negation bound
    # to the noun, and the hop count stays with the pool qualifier.
    "xrate.no_route_col": u"%(sym)s तक 6 पूल हॉप के भीतर कोई मार्ग नहीं।",
    "xrate.refresh_btn": u"मूल्य ताज़ा करें",
    "xrate.remove_btn": u"हटाएँ ",
    "xrate.retry_btn": u"पुनः प्रयास करें",
    "xrate.show_all": u"सभी एसेट दिखाएँ",
    "xrate.status": (
        u"%(pools)s पूल · 3 हॉप के भीतर %(assets)s एसेट · %(total)s पूलों में से "
        u"%(done)s के पास अंतिम स्वैप है"
    ),
    "xrate.title": u"क्रॉस दरें",
    "xrate.token_label": u"कोट प्रतीक जोड़ें",
    "xrate.unknown_token": u"%(sym)s नाम का कोई पूल एसेट नहीं।",
    # A missing price is a data gap on ONE leg of a route; अभी तक bounds "yet"
    # and "इस मार्ग की एक लेग" keeps the leg, not the whole route.
    "xrate.unpriced": u"इस मार्ग की एक लेग का अभी तक कोई दर्ज स्वैप नहीं है।",

    # ================================================================= apilab (1)
    # The help article chunk-B shipped already links this desk as "[API लैब]
    # (#/api-lab)", so the page title reuses that exact spelling.
    "apilab.title": u"API लैब",
}

# Keys deliberately left byte-identical to en, and therefore deliberately NOT
# claimed in _meta.translated. Each is asserted to still equal en after the
# write, so a later pass cannot quietly turn a deliberate keep into an
# unclaimed drift:
#
#   * the acronyms a chain UI prints in Latin: misc.id / proposal.id /
#     ticket.id / vesting.id ("ID", the column head - explorer.id_row is the
#     precedent chunk-B kept for the same reason), createworker.url / vote.url
#     ("URL"), htlc.title ("HTLC" - menu.p_htlc is chunk-B's precedent), and
#     proposal.n_a ("n/a");
#   * the two bare em dashes assets_feed.s1 / explorer_assets.s1 are: a
#     "no data yet" cell with no word to translate, so translating it would
#     invent content the reference UI does not have;
#   * i18n.badge_chip, the literal "i18n" tag the header chip prints
#     (already declared by chunk-B);
#   * viewing.dialog_placeholder, a FORMAT SAMPLE, not prose: chain account
#     names are ASCII, so "खाता-नाम" would show a name shape the chain cannot
#     accept - the same reasoning as the auth.account_name login labels;
#   * the two multi-line DATA SAMPLES a textarea pre-fills:
#     misc.invoice_lines_placeholder ("coffee|1.5\ncake|2") and
#     ticket.airdrop_example_ph ("alice,10\nbob,2.5"). These are literal input
#     examples - translating "coffee" to "चाय" would make the sample useless;
#   * txbuilder.badge_tpl, the product name TxBuilder, which six other keys in
#     the same section already keep in Latin (add_transfer, added_title,
#     add_vote, add_deposit, empty, and this one);
#   * xrate.token_placeholder, a list of ticker EXAMPLES ("USD, CNY, BTC…")
#     that the reader types verbatim;
#   * barter.paid_by_suffix (") (" + "): "), which is pure punctuation glued
#     after an account name and contains no translatable word - translating the
#     separator would change what the reader sees without changing a word, the
#     same reasoning chunk-B used for pool_net.edge_card.
KEPT_ENGLISH = {
    # ---- assets_feed / explorer_assets
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    # ---- barter
    "barter.paid_by_suffix": u"): ",
    # ---- createworker / vote
    "createworker.url": u"URL",
    "vote.url": u"URL",
    # ---- htlc
    "htlc.title": u"HTLC",
    # ---- i18n
    "i18n.badge_chip": u"i18n",
    # ---- the two multi-line DATA SAMPLES a textarea pre-fills
    "misc.invoice_lines_placeholder": u"coffee|1.5\ncake|2",
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    # ---- misc / proposal / ticket / vesting
    "misc.id": u"ID",
    "proposal.id": u"ID",
    "proposal.n_a": u"n/a",
    "ticket.id": u"ID",
    "vesting.id": u"ID",
    # ---- txbuilder
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    # ---- viewing
    "viewing.dialog_placeholder": u"account-name",
    # ---- xrate
    "xrate.token_placeholder": u"USD, CNY, BTC…",
}


if __name__ == "__main__":
    sys.exit(main())