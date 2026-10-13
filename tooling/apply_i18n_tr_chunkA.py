#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n tr chunk-A: fill the six desk sections tr.json still leaves in English.

Scope: ONLY the six sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from tr.json, or one whose English master moved, is REFUSED;
  * TR + KEPT_ENGLISH together must account for EVERY untranslated key of
    the six sections, so a forgotten string is a refusal, never a silent
    English.

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
                      IDENTIFIERS, plus devnet and the two footer brands, which
                      that gate does not name);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master;
  G4b edge spaces   leading / trailing whitespace of the English master is
                      reproduced exactly. Several values in this batch are pure
                      GLUE with a load-bearing blank - "Page total ~ ",
                      "Amount for sale (new total) ", "New price ",
                      "New expiration ", "Example: a dice game at " and its
                      continuation, which begins with a space - where a missing
                      space silently welds the computed value onto the label or
                      drops the sentence together. zh/ru/hi never needed a gate
                      for the leading-space case because their alphabets do not
                      start a line the same way; the check is cheap and catches
                      the whole class, so it runs for every key;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving
                      in lockstep with the bytes: a claimed key must differ from
                      en, an untranslated key must still equal en. Filling
                      strings is not verification, so the controller's v2
                      provenance / verified / high_risk fields are never touched
                      here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  script         no Devanagari, Cyrillic, CJK or Greek character may
                      appear in any value THIS BATCH writes. Turkish is Latin,
                      so the contaminated runs are the four non-Latin scripts a
                      copy-paste from a sibling locale would drag in (this batch
                      was written with the hi, ru and zh tables open). Greek is
                      in the sweep because the one Greek character this
                      dictionary legitimately prints - the delta of the "24h Δ"
                      data glyphs - lives in KEPT_ENGLISH and in keys an earlier
                      batch already shipped; a new one inside translated prose
                      would be a silent paste. The whole file is swept and a hit
                      OUTSIDE the six sections is reported as PRE-EXISTING
                      rather than repaired - chunk-B owns those keys, and an
                      insert-only pass that "fixed" a neighbour would be exactly
                      the silent edit the scope refusal exists to prevent;
  G8  dot hygiene    a middle dot must be space-separated, as in every other
                      locale (a run of graph glyphs - %(from)s -> %(to)s . class
                      - is data, and the arrows themselves are never rewritten);
  G9  vocabulary     every Latin token a value THIS BATCH writes must be
                      accountable, because Turkish shares its script with
                      English and no script-only sweep can catch an untranslated
                      word. Turkish is also an AGGLUTINATING language, so the
                      hi/zh token test ("this looks Latin, that is suspicious")
                      has no meaning here; what is meaningful is whether a token
                      is Turkish at all. A token passes if it is
                        (a) declared in LOAN below - a domain loanword a Turkish
                            crypto UI keeps in Latin (HTLC, DEX, Same-T, ...),
                            each with a reason;
                        (b) CONTINUOUS with the Turkish this dictionary SHIPS -
                            it is one of the words harvested at run time from
                            every tr.json value that differs from its English
                            master, or a Turkish inflected form of one
                            (aguz -> aguzdan, guncelle -> guncellemeleri).
                            Continuity is what makes this a Turkish gate rather
                            than a Latin-character gate: a Turkish reader sees
                            "düğümü" and knows the stem, and only a stem the
                            dictionary has never shipped has to be declared;
                        (c) a token of the ENGLISH master of that same key -
                            DATA under rule 1: an object id, a file path, an op
                            number, a URL scheme, a placeholder-filled figure;
                        (d) declared in NEW_VOCAB below - a stem or word this
                            batch introduces that tr.json does not ship yet,
                            with a reason, so "the reader is expected to know
                            it" is a declared decision rather than a silent one.
                      Anything else is a refusal. Nothing reaches G9 silently.
                      The harvest deliberately counts ONLY values that differ
                      from their English master: a token that occurs only
                      inside a still-untranslated English string is not Turkish
                      vocabulary, and accepting it would make this gate agree
                      with exactly the silent English it exists to catch.

Two adaptations from the hi chunk-A this file follows, both forced by the
language and both argued rather than inherited:

  * hi/zh G7b bans every apostrophe, because Devanagari and Han prose need
    none. Turkish orthography REQUIRES the apostrophe for a suffix on a proper
    noun or a loanword ("BTS'e", "URL'ler"), and this dictionary already
    prints it (104 occurrences in tr.json today). So there is no apostrophe ban
    here; instead each apostrophe this batch writes is listed by the run so a
    reviewer can check the genitive case on each one.
  * hi/zh G9 is a Latin-token gate, which cannot be copied verbatim into a
    Latin-script language - there every word would trip. The gate above keeps
    the intent (no undeclared loanword, no silent English) and adds the
    vocabulary half Turkish actually needs.

Register is FORMAL (siz) - the standard for Turkish financial UIs - and the
vocabulary is reused verbatim from the strings tr.json already ships, so this
batch reads like the rest of the dictionary: hesap, cüzdan, parola, kilit
açmak, imzalamak, yayınlamak, onaylamak, miktar/tutar, bakiye, fiyat, hacim,
emir, dolum, piyasa, borsa, masa, varlık, ihraççı, yayıncı, üretici, besleme,
basım, uzlaşma, teminat, borç, kredi, teklif, anlaşma, öneri, yetki, izin,
tanık, komite, çalışan, vekil, hakediş, bilet, gizli transfer, havuz, takas,
akıllı para, düğüm, zincir, ücret, anahtar, düzenek, ağ, harita, derinlik,
adım, satır, filtre. It also reuses the two validated probe answers this
dictionary's own fixture pins - the shared-account line and the past-participle
agreement in the approved/broadcast strings.

Morphology is the part a Turkish reader notices first, so the rules are worth
stating: a suffix agrees with the last vowel of its stem, so hesap (a) takes
back-vowel suffixes (hesabınızda) while bakiye (e) takes front ones (bakiyeniz);
case stacks (hesabınızda, işlemlerinden) and dropping a suffix changes meaning,
not just politeness; and a comparison must never invert - "greater than zero"
is "sıfırdan büyük", never "sıfırdan küçük". G10 asserts the last one
mechanically for the validation strings this batch writes.

The op labels (account.op_*) follow the nominal pattern the translated ones
established - "Hesap oluşturma", "Limit emir oluşturma", "Emir dolumu" - so a
history column reads as a list of nouns. The account.sum_* history lines keep
the shipped finished voice ("... kaydedildi", "... güncellendi"), because they
describe one row that already happened, not a column of kinds.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (first 8 publishers, first 100, op 19, op 23, 7-day,
24h, 90d) the translation keeps it byte-verbatim, spelled the way this
dictionary already spells it ("24s" for 24h in the compact market columns, "90g"
for 90d in prose).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_tr_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_tr_chunkA.py --apply         # writes tr.json
  python3 tooling/apply_i18n_tr_chunkA.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
TR_PATH = os.path.join(BASE, "tr.json")

# The six sections this batch owns. Everything else belongs to chunk-B and is
# REFUSED here as out of scope.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from TR below so they keep the
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
DEVANAGARI = re.compile(u"[ऀ-ॿ]")
CYRILLIC = re.compile(u"[Ѐ-ӿ]")
CJK = re.compile(u"[一-鿿぀-ヿ가-힯]")
GREEK = re.compile(u"[Ͱ-Ͽ]")
# G9: a Latin (i.e. all) token inside a value this batch writes. A token may
# continue through - _ . / so "Same-T", "get_settle_orders" and "ipaddress.to"
# are one decision each. Turkish letters are spelled out so a dotless i (i) is
# not confused with a Latin one.
TR_CHARS = u"A-Za-zÇĞİIÖŞÜçğıiöşüÂÎÛâîû"
LATIN_TOKEN = re.compile(
    u"[" + TR_CHARS + u"][" + TR_CHARS + u"0-9]*"
    u"(?:[-_./][" + TR_CHARS + u"0-9]+)*"
)
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# G10: the comparison trap. A validation string that tells the reader a rule
# must keep the DIRECTION of that rule. Each entry is
# (en substring that marks the rule, Turkish string that must appear,
# Turkish string that would invert it). English masters are matched so a key
# whose wording changes fails loudly instead of silently dropping the check.
COMPARISONS = (
    ("greater than zero", u"büyük", u"küçük"),
    ("must be in the future", u"gelecekte", u"geçmişte"),
)

# The loanwords this batch is allowed to leave in Latin (G9a). Every entry is a
# word a Turkish crypto UI prints in Latin; anything else has to be Turkish.
LOAN = frozenset((
    # --- domain names and chain / protocol vocabulary
    "HTLC",          # hash time-locked contract; the graph chip, every op label
                     # and the htlc section header all keep it
    "FBA",           # fee-betting-algorithm distribution op
    "Same-T",        # Same-T funds; tr.json's samet section already writes it
                     # this way ("Same-T Fonları")
    "SameT",         # the same name as the English master spells it, for the
                     # three account.sum_* lines that use the bare spelling
    "BTS",           # the core asset ticker
    "BitShares",     # the chain name
    "Op",            # the operation-number column head, kept where it reads
                     # as part of a sentence
    "op",            # the "op 19" / "op %(op)s" family, kept byte-verbatim
    "DEX",           # the dark theme's name and the market type
    "Assert",        # the op whose name is a single protocol verb (op 55);
                     # Turkish has no established one-word equivalent and a
                     # wrong gloss here would name the wrong operation
    "Override",      # the transfer whose fee the asset issuer pays (op 39-41
                     # family); "override" is how every Turkish crypto UI and
                     # this project's other dictionaries name it
    "Discrete",      # the chart's named aggregation mode (market.tf_discrete)
    "Log",           # the log scale, already spelled this way by market.px_log
    "Ping",          # the node liveness column; tr.json's settings.probe_all
                     # already writes "Tümüne ping"
    "web",           # "web siteleri", the extension's isolation promise
    "Enter",         # a key on the user's keyboard, printed in Latin
    "IPv4", "IPv6",  # address-family names, if a string ever names one
    # --- service names inside prose, never prose themselves
    "ipaddress.to",  # the geo lookup behind settings.geo_note
    "https",         # the transport word in that same note
    "get_settle_orders",  # the WS method market.settle_first100 names
    # --- indicator / ticker loanwords the brief lists for every locale
    "BB", "EMA", "PSAR", "SMA",
    # --- technical acronyms. CER joins the brief's list because asset.cer_row
    # names it in a sentence and tr.json already ships four "CER baz/kotasyon"
    # field labels from an earlier batch, so the acronym is this file's
    # established spelling, not an invention.
    "MCR", "MSSR", "CER", "NFT", "URI", "URL", "PMA", "UIA", "ID",
))

# Turkish words this batch introduces that tr.json does not ship yet (G9d).
# Turkish agglutinates, so each entry is a STEM: the inflected forms this batch
# writes (çizmek, çizilmedi, Genişlet ...) are accepted from the stem, exactly
# as a shipped stem accepts its own forms. Each entry carries the reason it is
# here, so a reviewer sees every new word this file brings in rather than
# diffing 395 strings. Short stems are declared on purpose and matched only
# against longer forms, which is why a two-letter entry such as "eş" below
# cannot swallow an unrelated word.
NEW_VOCAB = {
    # --- the account / market network map: draw, map, expand, neighbours
    u"ağ": u"network; tr.json ships 'Ağ' but the stem is two letters, so its "
           u"accusative (Ağı çiz) needs declaring - the button label of both "
           u"network views",
    u"çiz": u"draw (the map): Ağı çiz / çizmek / çizilmedi; the network views' "
           u"only action verb",
    u"harita": u"map (the graph view); the dictionary ships grafik/sparkline "
               u"but not the noun this view is titled with",
    u"genişlet": u"expand (graph neighbours, market rows); every locale keeps "
                 u"the expand/collapse pair in its own script",
    u"komşu": u"neighbour, the graph term for an account one hop out",
    u"değiş": u"changed, the stale-settings notice",
    u"çevre": u"around, the hops-empty notice about the legs' surroundings",
    u"okun": u"unreadable, the shape-skipping status line",
    u"kısıt": u"truncated, the expansion-scan notice",
    u"ilişki": u"relation, the second account-network chip kind",
    u"saklan": u"stored, the read-only promise in the account-network intro",
    u"çıkış": u"out, the blind-transfer legend's out leg (the dictionary ships "
              u"'çıkışı' from the pool A->B column)",
    u"sağlayıcı": u"provider, the node table's column head",
    u"sıkış": u"handshake, the node table's column head",
    u"barındır": u"hosted (a compromised hosted copy), the signing warning",
    u"kopya": u"copy, the same warning: a copy of this page you control",
    u"oku": u"read (your keys), the same warning",
    u"imzala": u"sign, the same warning's 'route signing through the "
               u"extension'",
    u"aldıklarını": u"the -dık relative form of 'al' in the intro's 'kimden "
                    u"borç aldıklarını'; the two-letter stem is too short to "
                    u"declare as a stem, so the form this batch writes is",
    # --- history one-liners (finished acts)
    u"yürüt": u"execute, the execute-bid op label and its history line",
    u"dağıt": u"distribute, the FBA distribution op label",
    u"yak": u"burn, the asset-burn history line (the dictionary ships "
            u"'yakma' for the reserve screen, never the perfective)",
    u"iste": u"request / ask, the settle-request history line and the geo "
             u"provider note",
    u"bağla": u"vest (funds under a release policy), the vesting history line",
    # --- panels, buttons and labels
    u"tuval": u"canvas, the account-network canvas note",
    u"hız": u"speed, the capped feed-history notice",
    u"eş": u"co- (co-owner); the shared-issuer hint names the second key holder",
    u"seyrek": u"rarely, the no-history notice about inactive publishers",
    u"temizle": u"clear, the market-network clear button (the dictionary ships "
                u"only the 'temizleyin' hint form)",
    u"önbellek": u"cache, the offline notice and the geo-provider note",
    u"eğilim": u"trend, the sparkline column label",
    u"eriş": u"reachable, the verdict_web line (the dictionary ships only "
             u"'erişilemez' for an unreachable node)",
    u"eylem": u"action, the remove-node confirm dialog's column head",
    u"kur": u"install, the 'how to install the extension' guide link",
    u"bellek": u"memory, the in-page signing mode",
    u"yalıt": u"isolated, the extension signing mode's promise",
    u"zar": u"dice, the fictional connected-site example",
    u"kurgusal": u"fictional, the honesty clause at the end of that example",
    u"oyna": u"play, the same fictional example",
    u"sefer": u"time (every time), the same example's 'signatures still prompt'",
}


def suspicious(value):
    """Return the offending character, or None when the value is clean.

    A middle dot is clean when it is space-separated, as it is everywhere in
    this dictionary - or when both neighbours are alphanumeric, which is
    algebraic notation. Anything else is a stray dot that will render as a
    different word to the reader.
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


def harvest_vocab(tr_flat, en_flat):
    """Collect every word the dictionary already ships IN TURKISH.

    Only values that differ from their English master count. That is the point
    of the harvest: a token that only occurs inside a still-untranslated
    English string must NOT count as established Turkish vocabulary, or G9
    would accept exactly the silent English it exists to catch.
    """
    vocab = set()
    for key, value in tr_flat.items():
        if value == en_flat.get(key):
            continue
        vocab.update(LATIN_TOKEN.findall(value))
    return vocab


# Turkish suffixation can change the LAST CONSONANT of a stem, not only append:
# "bellek" + -inde is "belleğinde" and "önbellek" + -e is "önbelleğe". A plain
# prefix test would reject those two, so the final consonant is compared through
# this softening map instead.
SOFTENING = {
    u"k": u"ğ", u"c": u"ç", u"p": u"f",
    u"t": u"s", u"s": u"s", u"g": u"ğ",
}


def _fold(text):
    """Lower-case for comparison, with the Turkish dotted capital mapped to i.

    Only the DOTTED capital is pre-mapped; the other diacritics stay, because
    the softening test below compares consonants and would lose its meaning if
    ö/ü/ş decomposed into o/u/s.
    """
    return text.replace(u"İ", u"i").replace(u"I", u"i").lower()


def _extends(low, word):
    """True when `low` is `word` plus a suffix, allowing final softening."""
    n = len(word)
    if len(low) <= n:
        return False
    if low[:n] == word:
        return True
    return (n >= 2 and low[:n - 1] == word[:-1]
            and word[-1] in SOFTENING and low[n - 1] == SOFTENING[word[-1]])


def turkish(token, harvested, declared):
    """True when `token` is a shipped or declared Turkish word, in any case.

    Turkish agglutinates suffixes onto the stem, so a case-stacked word such as
    "düğümden" or "işlemlerinden" is the SAME vocabulary decision as "düğüm" and
    "işlem". Requiring every suffixed form to be declared by hand would bury the
    handful of decisions that matter under two hundred permutations of the same
    ten stems. Two pools with different lengths:
      * harvested words (from the shipped dictionary) need three letters or
        more before they may match by prefix - "ar" or "de" would otherwise
        match half the language by accident;
      * declared words are this file's own decision, recorded with a reason, so
        two letters are enough ("eş", "ağ") - and they only ever match a LONGER
        form, never a bare two-letter token.
    Matching is case-insensitive because Turkish capitalises sentence starts and
    column heads ("Genişlet", "Ağı") and those are the same word.
    """
    low = _fold(token)
    if low in harvested:
        return True
    if any(len(w) >= 3 and _extends(low, w) for w in harvested):
        return True
    if low in declared:
        return True
    return any(len(w) >= 2 and _extends(low, w) for w in declared)


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
            "line count changed: %s (en %d, tr %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if edge_space(master) != edge_space(value):
        problems.append(
            "edge whitespace changed: %s (en %r, tr %r)"
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


def check_tr_hygiene(batch, en_flat, vocab, problems, fallback, apostrophes):
    """G7 + G9 + G10: script, vocabulary accountability and comparison direction.

    Scoped to the values THIS BATCH writes. tr.json's other sections carry
    their own vocabulary from earlier batches; re-auditing those here would make
    this file the owner of someone else's words.
    """
    vocab_lower = set(_fold(t) for t in vocab)
    declared = set(_fold(w) for w in NEW_VOCAB)
    for key, value in sorted(batch.items()):
        # Interpolations are substituted data, not prose: %(name)s and {s} must
        # never count as vocabulary (G1 proves they survived).
        prose = PLACEHOLDER.sub("", value)
        prose = BRACE.sub("", prose)
        # A count keeping its English unit suffix ("24h", "90d") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # inside a compact column head without breaking the number the reader
        # compares against the control beside it.
        prose = COUNT_UNIT.sub("", prose)
        if APO_TYPO in value:
            problems.append("G7b: typographic apostrophe in %s" % key)
        if APO_ASCII in value:
            # Turkish orthography WANTS this apostrophe (a suffix on a proper
            # noun or a loanword), so it is reported for a human eye rather than
            # refused. See the header.
            apostrophes.append("%s: %r" % (key, value))
        if IDEO_SPACE in value:
            problems.append("G7b: ideographic space in %s" % key)
        for name, rx in (("Devanagari", DEVANAGARI), ("Cyrillic", CYRILLIC),
                         ("CJK", CJK), ("Greek", GREEK)):
            hit = rx.search(value)
            if hit:
                problems.append(
                    "G7: %s %r in %s" % (name, hit.group(0), key)
                )
        master_tokens = set(LATIN_TOKEN.findall(
            COUNT_UNIT.sub("", PLACEHOLDER.sub("", en_flat[key]))))
        for token in sorted(set(LATIN_TOKEN.findall(prose))):
            if token in LOAN:
                continue
            if turkish(token, vocab_lower, declared):
                continue
            if token in master_tokens:
                fallback.append("%s: %s" % (key, token))
                continue
            problems.append("G9: unaccounted token %r in %s" % (token, key))
        master = en_flat[key]
        for marker, needed, inverted in COMPARISONS:
            if marker in master:
                if needed not in value:
                    problems.append(
                        "G10: %s lost its rule word %r" % (key, needed)
                    )
                if inverted in value:
                    problems.append(
                        "G10: %s INVERTS its comparison with %r"
                        % (key, inverted)
                    )


def verify():
    """Structural re-proof of the shipped file against the en master."""
    tr, en = load(TR_PATH), load(EN_PATH)
    d, e = flat(tr), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: chunk-B owns them, and an
    # insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` - problems this batch can
    # answer for - gates the exit code.
    pre = []
    # Structure is answerable for every key this batch OWNS (translated, or
    # kept English on purpose). The CHARACTER sweep is narrower: it asks "did
    # this batch introduce a stray script here?", and a key that is byte-
    # identical to its English master by declaration cannot have introduced
    # anything - that is what the "24h Δ" data glyph in KEPT_ENGLISH is.
    owned = set(TR) | set(KEPT_ENGLISH)
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
            check_batch(e, key, d[key], bad, chars=key in owned)
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
            (bad if key in TR else pre).append(where)
        for name, rx in (("Cyrillic", CYRILLIC), ("CJK", CJK),
                         ("Greek", GREEK)):
            hit = rx.search(d[key])
            if hit:
                where = "%s %r in %s" % (name, hit.group(0), key)
                (bad if key in TR else pre).append(where)
    fallback, apos = [], []
    check_tr_hygiene(TR, e, harvest_vocab(d, e), bad, fallback, apos)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(TR) if d.get(k) == e.get(k)]
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
        and k not in TR and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(TR) - len(same), len(TR)))
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
    meta = tr.get("_meta", {})
    print("  _meta version=%r untranslated=%r translated=%d entries"
          % (meta.get("version"), meta.get("untranslated"),
             len(meta.get("translated", []))))
    if pre:
        print("PRE-EXISTING, outside this batch's translated values (a "
              "deliberate English byte - a declared KEPT_ENGLISH data glyph, "
              "or another batch's key; not touched, not fixed):")
        print("\n".join("  " + p for p in sorted(set(pre))))
    if fallback:
        print("  G9 tokens that leaned on the ENGLISH SOURCE (data), audit:")
        for item in sorted(set(fallback)):
            print("    %s" % item)
    if apos:
        print("  G7b-report: apostrophes this batch writes (Turkish genitive):")
        for item in sorted(set(apos)):
            print("    %s" % item)
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
    raw = open(TR_PATH, encoding="utf-8").read()
    tr = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(tr, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: tr.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(tr))
    before_meta = json.dumps(tr["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(TR.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in tr.json: %s" % key)
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
        deep_set(tr, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(TR) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (TR and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(TR) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in tr.json: %s" % key)
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

    fallback, apos = [], []
    check_tr_hygiene(TR, en_flat, harvest_vocab(before, en_flat),
                     problems, fallback, apos)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(tr)
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
    meta = tr["_meta"]
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
    added = sorted(k for k in TR
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

    print("tr chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    print("  LOAN allowlist (%d): %s" % (len(LOAN), ", ".join(sorted(LOAN))))
    print("  NEW_VOCAB declared (%d): %s"
          % (len(NEW_VOCAB), ", ".join(sorted(NEW_VOCAB))))
    if fallback:
        print("  G9 tokens that leaned on the ENGLISH SOURCE rather than on "
              "the Turkish harvest / LOAN / NEW_VOCAB (audit these):")
        for item in sorted(set(fallback)):
            print("    %s" % item)
    else:
        print("  G9: no token needed the English-source fallback")
    if apos:
        print("  G7b-report: apostrophes this batch writes (Turkish genitive "
              "case - check each):")
        for item in sorted(set(apos)):
            print("    %s" % item)
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue / "
              "sentinels - deliberately NOT claimed):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run - no files written (pass --apply)")
        return 0

    with open(TR_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(tr, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/tr.json")
    return 0


TR = {
    # =========================================================== account (143)
    # The shared-account line is the fixture's T11 answer verbatim: four
    # placeholders, an em dash and a middle dot, and the "active / owner" weight
    # pair the wallet already spells "etkin / sahip" everywhere else.
    "account.draw_network": u"Ağı çiz",
    "account.multisig_checking": u"Yetkiler denetleniyor…",
    "account.multisig_open_txbuilder": u"İşlem oluşturucuyu aç",
    "account.multisig_shared": (
        u"Ortak hesap — etkin %(ath)s/%(an)s · sahip %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        u"Tek anahtar — etkin %(ath)s/%(an)s · sahip %(oth)s/%(on)s."
    ),
    # Turkish drops the possessive rather than stacking "öneriler öneriler
    # sayfasında"; the pointer stays just as findable.
    "account.multisig_single_hint": (
        u"Ortak hesap mı? Bu işlemler öneriler sayfasında."
    ),
    "account.multisig_unavailable": (
        u"Yetkiler alınamıyor — öneriler yine de öneriler sayfasında "
        u"listelenir."
    ),
    "account.multisig_view_proposals": u"Önerileri görüntüle",
    # Operation labels. Nominal, like the translated ones ("Hesap oluşturma",
    # "Limit emir oluşturma", "Emir dolumu") so a history column reads as a list
    # of nouns.
    "account.op_asset_burn": u"Varlık yakma",
    "account.op_asset_issue": u"Varlık basımı",
    "account.op_asset_settle": u"Varlık uzlaşması",
    "account.op_asset_update": u"Varlık güncelleme",
    "account.op_authority_create": u"Yetki oluşturma",
    "account.op_authority_delete": u"Yetki silme",
    "account.op_authority_update": u"Yetki güncelleme",
    "account.op_balance_claim": u"Bakiye talebi",
    # The blind legs are named by direction so the trio reads as one transfer -
    # the three lines the vesting table already ships.
    "account.op_blind_from": u"Gizli hesaptan transfer",
    "account.op_blind_to": u"Gizli hesaba transfer",
    "account.op_blind_transfer": u"Gizli transfer",
    "account.op_claim_fees": u"Ücret talebi",
    "account.op_claim_pool": u"Havuz talebi",
    "account.op_collateral_bid": u"Teminat teklifi",
    "account.op_committee_join": u"Komiteye katılım",
    "account.op_committee_update": u"Komite güncelleme",
    "account.op_custom_op": u"Özel işlem",
    "account.op_deal_expired": u"Anlaşma bitişi",
    "account.op_deal_repay": u"Anlaşma geri ödemesi",
    "account.op_deal_update": u"Anlaşma güncelleme",
    "account.op_debit_claim": u"Doğrudan borçlandırma talebi",
    "account.op_debit_create": u"Doğrudan borçlandırma oluşturma",
    "account.op_debit_delete": u"Doğrudan borçlandırma silme",
    "account.op_debit_update": u"Doğrudan borçlandırma güncelleme",
    "account.op_execute_bid": u"Teklif yürütme",
    "account.op_fba_distribute": u"FBA dağıtımı",
    "account.op_fee_pool_fund": u"Ücret havuzu fonlaması",
    "account.op_feed_producers_update": u"Besleme üreticileri güncelleme",
    "account.op_feed_publish": u"Besleme yayınlama",
    "account.op_global_settle": u"Global uzlaşma",
    "account.op_htlc_create": u"HTLC oluşturma",
    "account.op_htlc_extend": u"HTLC uzatma",
    "account.op_htlc_redeem": u"HTLC kullanma",
    "account.op_htlc_redeemed": u"HTLC kullanıldı",
    "account.op_htlc_refund": u"HTLC iadesi",
    "account.op_issuer_update": u"İhraççı güncelleme",
    "account.op_offer_accept": u"Kredi kabulü",
    "account.op_offer_create": u"Kredi teklifi oluşturma",
    "account.op_offer_delete": u"Kredi teklifi silme",
    "account.op_offer_update": u"Kredi teklifi güncelleme",
    "account.op_order_update": u"Emir güncelleme",
    "account.op_override_transfer": u"Override transferi",
    "account.op_params_update": u"Genel parametre güncelleme",
    "account.op_pool_create": u"Havuz oluşturma",
    "account.op_pool_delete": u"Havuz silme",
    "account.op_pool_deposit": u"Havuz yatırması",
    "account.op_pool_swap": u"Havuz takası",
    "account.op_pool_update": u"Havuz güncelleme",
    "account.op_pool_withdraw": u"Havuzdan çekme",
    "account.op_proposal_create": u"Öneri oluşturma",
    "account.op_proposal_delete": u"Öneri silme",
    "account.op_proposal_update": u"Öneri güncelleme",
    "account.op_samet_borrow": u"Same-T borçlanma",
    "account.op_samet_create": u"Same-T fon oluşturma",
    "account.op_samet_delete": u"Same-T fon silme",
    "account.op_samet_repay": u"Same-T geri ödeme",
    "account.op_samet_update": u"Same-T fon güncelleme",
    "account.op_settle_cancel": u"Uzlaşma iptali",
    "account.op_smartcoin_update": u"Akıllı para güncelleme",
    "account.op_ticket_create": u"Bilet oluşturma",
    "account.op_ticket_update": u"Bilet güncelleme",
    "account.op_vesting_create": u"Hakediş oluşturma",
    "account.op_vesting_withdraw": u"Hakediş çekme",
    "account.op_witness_join": u"Tanığa katılım",
    "account.op_witness_update": u"Tanık güncelleme",
    "account.op_worker_create": u"Çalışan oluşturma",
    # Pager + its note. The trailing space on page_total is load-bearing: a
    # computed figure follows it (G4b proves it survives).
    "account.page_total": u"Sayfa toplamı ≈ ",
    "account.portfolio_page": u"Sayfa %(page)s / %(pages)s",
    "account.prices_cover_this_page": (
        u"Fiyatlar bu sayfayı kapsar — daha fazla varlık için sayfayı "
        u"değiştirin."
    ),
    # History one-liners: a finished act, one row, so every line ends in the
    # perfective ("... kaydedildi", "... güncellendi") the way the shipped
    # strings do - not the noun the way the op labels do.
    "account.sum_account_create": u"%(name)s kaydedildi",
    "account.sum_account_transfer": u"Hesap %(owner)s kişisine aktarıldı",
    "account.sum_account_update": u"Hesap güncellendi: %(account)s",
    "account.sum_asset_burn": u"%(amount)s yakıldı",
    "account.sum_asset_create": u"Varlık %(symbol)s oluşturuldu",
    "account.sum_asset_issue": u"%(to)s kişisine %(amount)s basıldı",
    "account.sum_asset_settle": u"%(amount)s için uzlaşma istendi",
    "account.sum_asset_update": u"Varlık %(asset)s güncellendi",
    "account.sum_authorities": u"%(account)s için yetkiler güncellendi",
    "account.sum_balance_claim": u"%(amount)s talep edildi",
    "account.sum_bid": u"%(debt)s karşılığında %(coll)s teklifi verildi",
    "account.sum_blind": u"Gizli transfer (%(in)s giriş, %(out)s çıkış)",
    "account.sum_call_update": (
        u"Pozisyon ayarlandı: %(coll)s teminat, %(debt)s borç"
    ),
    "account.sum_claim_fees": u"Ücret olarak %(amount)s talep edildi",
    "account.sum_committee_create": u"Komite üyesi oldu: %(account)s",
    "account.sum_committee_update": u"Komite üyesi %(account)s güncellendi",
    "account.sum_custom": u"%(account)s tarafından özel işlem",
    "account.sum_deal_expired": u"Anlaşma %(deal)s süresi doldu",
    "account.sum_deal_repay": u"Anlaşma %(deal)s için %(amount)s geri ödendi",
    "account.sum_deal_update": u"Anlaşma %(deal)s güncellendi",
    "account.sum_debit_claim": u"%(amount)s doğrudan borçlandırma talep edildi",
    "account.sum_debit_create": (
        u"%(to)s için %(amount)s doğrudan borçlandırma yetkilendirildi"
    ),
    "account.sum_debit_delete": u"Doğrudan borçlandırma izni %(perm)s silindi",
    "account.sum_debit_update": (
        u"%(to)s için %(amount)s doğrudan borçlandırma güncellendi"
    ),
    "account.sum_execute_bid": (
        u"%(debt)s karşılığında %(coll)s teklifi yürütüldü"
    ),
    "account.sum_fee_pool_fund": (
        u"%(asset)s ücret havuzu %(amount)s ile fonlandı"
    ),
    "account.sum_feed": (
        u"%(publisher)s tarafından %(asset)s için besleme yayınlandı"
    ),
    "account.sum_feed_producers": (
        u"%(asset)s için %(n)s besleme üreticisi ayarlandı"
    ),
    "account.sum_fill": u"Dolum: %(pays)s ödendi, %(receives)s alındı",
    "account.sum_global_settle": u"%(asset)s global uzlaşmaya alındı",
    "account.sum_htlc_claimed": u"HTLC %(id)s talep edildi",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(from)s kişisinden %(to)s kişisine %(amount)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s uzatıldı",
    "account.sum_htlc_redeem": u"HTLC %(id)s kullanıldı",
    "account.sum_htlc_refund": u"HTLC %(id)s iade edildi",
    "account.sum_issuer_update": u"%(asset)s için yeni ihraççı: %(issuer)s",
    "account.sum_offer_accept": (
        u"%(coll)s karşılığında %(amount)s ödünç alındı (teklif %(offer)s)"
    ),
    "account.sum_offer_create": u"%(asset)s cinsinden kredi teklifi oluşturuldu",
    "account.sum_offer_delete": u"Teklif %(offer)s silindi",
    "account.sum_offer_update": u"Teklif %(offer)s güncellendi",
    "account.sum_order_cancel": u"Emir %(order)s iptal edildi",
    "account.sum_order_create": u"En az %(buy)s karşılığında %(sell)s verildi",
    "account.sum_order_update": u"Emir %(order)s güncellendi",
    "account.sum_pool_create": u"%(a)s / %(b)s havuzu oluşturuldu",
    "account.sum_pool_delete": u"Havuz %(pool)s silindi",
    "account.sum_pool_deposit": u"Havuz %(pool)s içine %(a)s + %(b)s yatırıldı",
    "account.sum_pool_swap": (
        u"Havuz %(pool)s içinde %(sell)s → en az %(buy)s takas edildi"
    ),
    "account.sum_pool_update": u"Havuz %(pool)s güncellendi",
    "account.sum_pool_withdraw": u"Havuz %(pool)s içinden %(shares)s çekildi",
    "account.sum_proposal_create": u"%(n)s işlem önerildi",
    "account.sum_proposal_delete": u"Öneri %(proposal)s silindi",
    "account.sum_proposal_update": u"Öneri %(proposal)s onaylandı",
    "account.sum_samet_borrow": u"Fon %(fund)s içinden %(amount)s ödünç alındı",
    "account.sum_samet_create": u"%(amount)s tutarında Same-T fon oluşturuldu",
    "account.sum_samet_delete": u"Same-T fon %(fund)s silindi",
    "account.sum_samet_repay": u"Fon %(fund)s içine %(amount)s geri ödendi",
    "account.sum_samet_update": u"Same-T fon %(fund)s güncellendi",
    "account.sum_settle_cancel": u"%(amount)s için uzlaşma iptal edildi",
    "account.sum_smartcoin_update": u"Akıllı para %(asset)s güncellendi",
    "account.sum_ticket_create": u"%(amount)s tutarında bilet oluşturuldu",
    "account.sum_ticket_update": u"Bilet %(ticket)s güncellendi",
    "account.sum_transfer": (
        u"%(from)s kişisinden %(to)s kişisine %(amount)s transferi"
    ),
    "account.sum_transfer_recv": u"%(from)s kişisinden %(amount)s alındı",
    "account.sum_transfer_send": u"%(to)s kişisine %(amount)s gönderildi",
    "account.sum_upgrade": u"%(account)s yükseltildi",
    "account.sum_vesting_create": u"%(owner)s için %(amount)s hakedişe bağlandı",
    "account.sum_vesting_withdraw": u"Hakedişten %(amount)s çekildi",
    "account.sum_whitelist": u"%(account)s listeye eklendi",
    "account.sum_witness_create": u"Tanık oldu: %(account)s",
    "account.sum_witness_update": u"Tanık %(account)s güncellendi",
    "account.sum_worker_create": u"“%(name)s” adlı çalışan oluşturuldu",

    # ====================================================== account_net (58)
    "account_net.canvas_missing": (
        u"Ağ tuvali bu derlemede kullanılamıyor; aşağıdaki tablo yine de her "
        u"satırı listeler."
    ),
    "account_net.class_credit": u"Kredi",
    "account_net.class_credit_help": u"Kabul edilen ve geri ödenen kredi "
                                  u"teklifleri.",
    "account_net.class_debit": u"Doğrudan Borçlandırma",
    "account_net.class_debit_help": (
        u"Doğrudan borçlandırma izinleri ve çekimleri."
    ),
    "account_net.class_htlc_help": (
        u"Hash zaman kilitli sözleşmeler ve güncellemeleri."
    ),
    # "relation" is a permission line, not a movement of value - the help text
    # says so, so the chip label stays distinguishable from "akış".
    "account_net.class_override": u"Override transferi",
    "account_net.class_override_help": (
        u"Ücretini varlık ihraççısının ödediği transferler."
    ),
    "account_net.class_transfer_help": u"Hesaplar arası doğrudan transferler.",
    "account_net.class_vesting": u"Hakediş",
    "account_net.class_vesting_help": (
        u"Üçüncü bir tarafın yönettiği hakediş bakiyeleri."
    ),
    # Graph terms: a hop is one edge traversal and the pool map already ships
    # "{s}, BTS'e {n} adımda bağlı", so both reuse adım.
    "account_net.depth_1": u"1 adım",
    "account_net.depth_2": u"2 adım",
    "account_net.depth_label": u"Derinlik",
    "account_net.detail_hint": (
        u"Ayrıntısı için bir satıra dokunun; açmak için bir hesaba dokunun."
    ),
    # Turkish does not mark the plural on a counted noun phrase after a numeral
    # in a table cell, so the "ops" / "op" pair collapses to one form here.
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s işlem · "
        u"%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s işlem · "
        u"%(kind)s"
    ),
    "account_net.es_bad_account": u"Bu ad bu zincirde bir hesap değil.",
    "account_net.es_disabled": (
        u"Topluluk dizini kapalı. Bu haritayı çizmek için Ayarlar "
        u"bölümünden açın."
    ),
    "account_net.es_unavailable": (
        u"Topluluk dizinine şu anda erişilemiyor. Birazdan yeniden deneyin."
    ),
    "account_net.go": u"Ağı çiz",
    "account_net.idle": u"Henüz hiçbir şey çizilmedi.",
    "account_net.intro": (
        u"Bir veya daha fazla hesap girin; kime para gönderdiklerini, kime "
        u"borç verdiklerini ve kimden borç aldıklarını görün. Topluluk geçmiş "
        u"dizininden okunur; hiçbir şey imzalanmaz ve hiçbir şey saklanmaz."
    ),
    "account_net.kind_flow": u"akış",
    "account_net.kind_relation": u"ilişki",
    "account_net.more_assets": u" + %(n)s tane daha",
    "account_net.need_class": u"Çizmek için en az bir tür satırı açın.",
    "account_net.need_seeds": u"Haritalamak için en az bir hesap girin.",
    "account_net.no_amount": u"tutar yok",
    "account_net.ring1_label": u"Halka 1",
    "account_net.ring2_label": u"Halka 2",
    "account_net.scanning": u"Topluluk dizini okunuyor…",
    "account_net.seeds_label": u"Haritalanacak hesaplar",
    "account_net.stale_settings": (
        u"Derinlik ya da komşu ayarı değişti — Ağı çiz düğmesine basın."
    ),
    "account_net.status_credit_index": (
        u"Dizinden çözülen %(n)s kredi satırı (teklif ya da anlaşma nesnesi "
        u"zincirden kayıp)"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s kredi satırı atlandı (teklif ya da anlaşma zincirde "
        u"bulunamadı)"
    ),
    "account_net.status_depth": u"%(depth)s harita",
    "account_net.status_edge_cap": u"ilk %(n)s satır gösteriliyor",
    "account_net.status_expanded": u"genişletilen: %(names)s",
    "account_net.status_expansion_scanned": (
        u"genişletmelerden %(n)s dizinlenmiş işlem"
    ),
    "account_net.status_expansion_truncated": (
        u"genişletme taramaları en yeni işlemlere kısıtlandı"
    ),
    "account_net.status_graph": u"%(nodes)s hesap · %(edges)s satır",
    "account_net.status_node_cap": u"ilk %(n)s karşı taraf gösteriliyor",
    "account_net.status_scanned": (
        u"%(n)s hesaptan %(scanned)s dizinlenmiş işlem"
    ),
    "account_net.status_self": u"%(n)s kendi kendine transfer atlandı",
    "account_net.status_shape": u"%(n)s okunamayan kayıt atlandı",
    "account_net.status_truncated": u"hesap başına en yeni %(n)s işlem",
    "account_net.status_unexpanded": u"%(n)s doğrudan karşı taraf genişletilmedi",
    "account_net.status_unknown": u"bulunamadı: %(names)s",
    "account_net.title": u"Hesap Ağı",
    "account_net.twin_amount": u"Tutar",
    "account_net.twin_class": u"Tür",
    "account_net.twin_count": u"İşlem",
    "account_net.twin_depth": u"Adım",
    "account_net.twin_empty": (
        u"Taranan dizinlenmiş işlemlerde bu hesaplar arasında satır yok."
    ),
    "account_net.twin_from": u"Gönderen",
    "account_net.twin_relation": u"Akış/ilişki",
    "account_net.twin_span": u"İlk → son",
    "account_net.twin_summary": u"Tablo görünümü (erişilebilir)",
    "account_net.twin_to": u"Alıcı",

    # ============================================================== asset (34)
    "asset.cer_row": u"Çekirdek kotasyon oranı (CER)",
    "asset.committee_fed_note": (
        u"Komite beslemesi: etkin tüm komite üyeleri yayınlayabilir."
    ),
    "asset.feed_history_title": u"Besleme geçmişi",
    "asset.history_capped": u"İlk 8 yayıncı gösteriliyor (hız için sınırlı)…",
    "asset.history_days": u"Aralık",
    "asset.history_exchange": u"Borsa + havuzlar yükleniyor…",
    "asset.history_failed": u"Besleme geçmişi yüklenemedi.",
    "asset.history_loading": u"Besleme geçmişi yükleniyor…",
    "asset.history_pub": u"Yayıncı %(i)s/%(n)s…",
    "asset.invert_btn": u"Ters çevir",
    "asset.issue_memo_no_key": u"Bu hesap için kayıtlı not anahtarı yok.",
    "asset.issue_memo_warning": (
        u"Not ekleyin — zincir üstünde açık metin olarak saklanır."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"İhraççı varsayılan olarak görüntülenen hesaptır (%(id)s kilitli, "
        u"kendi hesabınız açık) — kontrol ettiğiniz herhangi bir ihraççı yazın. "
        u"Bir hesap sayfasından açıldıysa o hesap adını buraya yapıştırın."
    ),
    "asset.loading_producers": u"Üreticiler yükleniyor…",
    # "Eş sahip" is the same term the shared-issuer hint uses for the second
    # key holder, so both reuse it verbatim.
    "asset.multisig_body": (
        u"Bu varlık birden fazla onay gerektiriyorsa doğrudan İmzala "
        u"başarısız olur — bunun yerine değişikliği önerin ve eş sahiplerden "
        u"onay isteyin (op 23)."
    ),
    "asset.multisig_coowner_hint": (
        u"Eş sahip mi? Değişikliği öneriler sayfasında önerin ve eş "
        u"sahiplerden onay isteyin (op 23)."
    ),
    "asset.multisig_open_proposals": u"Önerileri görüntüle",
    "asset.multisig_open_txbuilder": u"İşlem oluşturucuyu aç",
    "asset.multisig_title": u"Ortak ihraççı mı? Önerin",
    "asset.new_issuer_field": u"Yeni ihraççı",
    "asset.no_history": (
        u"Bu aralıkta geçmiş yok — yayıncılar seyrek yayınlıyor; 90g deneyin."
    ),
    "asset.no_producers": (
        u"Henüz besleme yayınlanmadı — üreticiler yayın yaptığında burada "
        u"görünür."
    ),
    "asset.orientation_note": u"%(b)s karşılığında %(m)s",
    "asset.owner_key_note": u"Varlık sahibinin etkin anahtarı gerekir.",
    "asset.plot_feeds": u"Beslemeleri çiz",
    "asset.producer_col": u"Üretici",
    "asset.producers_failed": u"Üreticiler yüklenemedi.",
    "asset.producers_live_title": u"Besleme üreticileri",
    "asset.producers_title": u"Besleme üreticileri (op %(op)s)",
    "asset.publish_op19_title": u"Besleme yayınla (op %(op)s)",
    "asset.published_col": u"Yayınlandı",
    # "… olarak görüntüleniyor" is the phrase every viewing-as notice already
    # ships, so principle #9 reads one way across the app.
    "asset.viewing_notice": (
        u"%(name)s (%(id)s) olarak görüntüleniyor — imzalamak için kilidi "
        u"açın."
    ),
    "asset.witness_fed_note": (
        u"Tanık beslemesi: etkin tüm tanıklar yayınlayabilir."
    ),

    # ============================================================ market (50)
    "market.adjust_button": u"Ayarla",
    "market.confirm_adjust": u"Ayarı onayla",
    "market.discrete_fills": u"dolum",
    "market.discrete_no_fills": (
        u"Henüz dolum yok — bir emir girin ya da başka bir çift deneyin."
    ),
    "market.discrete_swaps": u"takas",
    "market.discrete_tip_account": u"Hesap",
    "market.discrete_tip_block": u"Blok",
    "market.discrete_tip_order": u"Emir",
    "market.discrete_tip_price": u"Fiyat",
    "market.discrete_tip_time": u"Zaman",
    "market.discrete_tip_volume": u"Hacim",
    "market.discrete_tip_volume_quote": u"Hacim (kotasyon)",
    "market.discrete_unavailable": u"Discrete modunda göstergeler kullanılamıyor.",
    "market.discrete_volume": u"Discrete hacmi",
    "market.exchange_desk": u"Borsa Masası",
    "market.fail_update": u"Güncelleme başarısız.",
    "market.flt_max_price": u"Azami fiyat",
    "market.flt_min_price": u"Asgari fiyat",
    "market.loading_pool_map": u"Harita yükleniyor…",
    "market.map_aria": (
        u"Piyasa ağı. Satırlar son 24 saatte işlem gören piyasalardır."
    ),
    "market.map_connects": (
        u"Son 24 saatte iki varlık arasında piyasa işlemi olduysa bir satır "
        u"ikisini birbirine bağlar."
    ),
    "market.map_connects_fallback": (
        u"Fonlu bir havuz varsa bir satır iki varlığı birbirine bağlar. 24 "
        u"saatlik işlem hareketi doğrulanamıyor (geçmiş kullanılamıyor) — "
        u"fonlu havuzlar gösteriliyor."
    ),
    "market.map_edge_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24s %(fills)s dolum"
    ),
    "market.map_hops_empty": (
        u"Bu bacakların çevresinde son 24 saatte işlem gören piyasa yok."
    ),
    "market.map_hops_filtered": (
        u"Bir satır son 24 saatte işlem gören piyasadır. %(total)s çiftten "
        u"%(shown)s tanesi gösteriliyor (en az 24s %(min)s dolum)."
    ),
    # No apostrophe: Turkish says "ulaşılamıyor", and the genitive of a ticker
    # ("BTS'e") is the one place an apostrophe would be correct.
    "market.map_hops_no_route": (
        u"İşlem gören piyasalar üzerinden BTS yoluna ulaşılamıyor."
    ),
    "market.map_hops_note": (
        u"Bir satır son 24 saatte işlem gören piyasadır. %(pairs)s çift "
        u"gösteriliyor."
    ),
    "market.map_leg_ok": u"{s} BTS ile bağlantılı",
    "market.map_leg_orphan": (
        u"UYARI: {s} için işlem gören piyasalardan bir yol yok!"
    ),
    "market.min_fills": u"En az dolum",
    "market.no_filter_match": u"Bu filtrelerle eşleşen dolum yok.",
    "market.settle_first100": u"İlk 100 gösteriliyor (get_settle_orders sınırı 100)",
    "market.settle_no_cancel": (
        u"Uzlaşma emirleri iptal edilemez — uzlaşma anında yürütülürler "
        u"(varlığın zorunlu uzlaşma gecikmesinden sonra)."
    ),
    # The three trailing spaces are load-bearing: an input follows them (G4b).
    "market.update_amount": u"Satılacak tutar (yeni toplam) ",
    "market.update_amount_change": u"Tutar değişimi",
    # G10: "greater than zero" stays sıfırdan büyük, the way transfer.amount_positive
    # already ships it. Never sıfırdan küçük - that would invert the rule.
    "market.update_bad_amount": u"Sıfırdan büyük bir tutar girin.",
    "market.update_bad_expiry": u"Gelecekte bir vade girin.",
    "market.update_bad_price": u"Sıfırdan büyük bir fiyat girin.",
    "market.update_broadcasting": u"Güncelleme yayınlanıyor…",
    "market.update_done": u"Emir güncellendi",
    "market.update_expiry": u"Yeni vade ",
    "market.update_expiry_change": u"Vade (eski → yeni)",
    "market.update_no_change": (
        u"Değişiklik yok — fiyatı, tutarı ya da vadeyi düzenleyin."
    ),
    "market.update_price": u"Yeni fiyat ",
    "market.update_price_change": u"Fiyat (eski → yeni)",
    "market.update_review": u"Güncellemeyi incele",
    "market.update_title": u"Emri ayarla",

    # ======================================================= market_net (33)
    "market_net.asset_1_field": u"Varlık 1 (herhangi bir bacak)",
    "market_net.asset_2_field": u"Varlık 2 (herhangi bir bacak)",
    "market_net.band_title": u"Piyasa ağı",
    "market_net.canvas_label": (
        u"Piyasa ağı haritası. Piyasayı açmak için Enter tuşuna basın."
    ),
    "market_net.clear_btn": u"Temizle",
    # The short column heads reuse the stats-tab wording verbatim: "24s hacim"
    # is market.stat_vol, and col_change stays the data glyph every other locale
    # also leaves alone.
    "market_net.col_last": u"Son",
    "market_net.col_market": u"Piyasa",
    "market_net.col_vol": u"24s hacim",
    "market_net.collapse": u"Daralt",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · 24s %(fills)s dolum"
    ),
    "market_net.empty": u"Bu filtre için piyasa bulunamadı.",
    "market_net.expand": u"Genişlet",
    "market_net.list_btn": u"Piyasaları listele",
    "market_net.loading": u"Piyasalar yükleniyor…",
    "market_net.map_empty": u"Yakın zamanda hacmi olan piyasa yok.",
    "market_net.map_fallback": (
        u"%(pairs)s çift · %(assets)s varlık · 24s dolum doğrulanmadı"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s çift · %(assets)s varlık · 24s dolum"
    ),
    "market_net.map_ready": u"%(markets)s piyasa · %(assets)s varlık",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s piyasa",
    "market_net.offline": (
        u"Ağ kullanılamıyor — önbelleğe alınmış piyasalar gösteriliyor. "
        u"Bağlandığınızda yeniden deneyin."
    ),
    "market_net.open_desk": u"%(id)s aç",
    "market_net.prompt": u"Varlık için düğüme, piyasa için satıra dokunun.",
    "market_net.ramp": u"24s hacim: düşük → yüksek",
    "market_net.ramp_fills": u"24s dolum: düşük → yüksek",
    "market_net.selector_title": u"Piyasa Seçici",
    "market_net.spark_label": u"%(id)s için 7 günlük eğilim",
    "market_net.subtitle": (
        u"24s hacmine göre en iyi emir defteri piyasaları. Masayı açmak için "
        u"bir satır seçin."
    ),
    "market_net.title": u"Piyasalar",
    "market_net.top_note": (
        u"Yoklanan %(probed)s içinden ilk %(shown)s — 24s hacmine göre."
    ),
    "market_net.twin": u"Piyasa satırları (%(n)s)",
    "market_net.twin_more": (
        u"%(n)s piyasadan %(shown)s tanesi gösteriliyor — daha az görmek "
        u"için filtreyi daraltın."
    ),
    "market_net.verdict_full": u"%(markets)s piyasa · %(assets)s varlık",
    "market_net.verdict_no_path": (
        u"%(a)s ile %(b)s arasında işlem gören piyasalardan bir yol yok"
    ),
    "market_net.verdict_path": (
        u"%(a)s, %(n)s işlem gören piyasa içinde %(b)s yoluna ulaşıyor"
    ),
    "market_net.verdict_star": u"%(s)s ile temas eden piyasalar: %(n)s",
    "market_net.verdict_web": u"%(s)s üzerinden erişilebilen piyasalar: %(n)s",

    # ========================================================== settings (44)
    "settings.confirm_back": u"Geri",
    "settings.confirm_remove_action": u"Eylem",
    "settings.confirm_remove_hide": (
        u"Bu düğümü gizle (yeniden eklenene kadar gizli kalır)"
    ),
    "settings.confirm_remove_result": u"Sonuç",
    "settings.confirm_remove_switch": u"Etkin düğüm %(node)s olur",
    "settings.confirm_remove_title": u"Düğüm kaldırılsın mı?",
    "settings.confirm_remove_unlist": u"Listemden kaldır",
    # The discover/geo notes keep the leading * or ** the markdown renderer
    # keys the paragraph on, exactly as the English does.
    "settings.discover_note": (
        u"**Düğüm bulma, GitHub üzerinde düğüm listeleri arar, sonra "
        u"bulduklarını yoklar. GitHub ve yoklanan düğümler ağ adresinizi "
        u"görür. Sonuçlar incelemeniz için adaylardır — hiçbir şey otomatik "
        u"eklenmez."
    ),
    "settings.geo_note": (
        u"*Konumlar ve sağlayıcılar ipaddress.to (https, anahtar yok) "
        u"üzerinden gelir — istendiğinde adresinizi görür; yanıtlar bu "
        u"cihazda 24 saat önbelleğe alınır."
    ),
    "settings.hist_no": u"HAYIR",
    "settings.hist_yes": u"EVET",
    "settings.language_title": u"Dil",
    # Signing section. Eklenti is this batch's first spelling of the browser
    # extension in tr.json; Giriş is the spelling account.gate_login already
    # ships; onay reuses the proposal wording, geri al the revoke wording.
    "settings.sign_auto": u"Otomatik (varsa eklenti)",
    "settings.sign_badge": u"Eklentiyle imzalama etkin — ayrıntılar Girişte",
    "settings.sign_badge_local": u"Sayfa içi imzalama — ayrıntılar Girişte",
    "settings.sign_browser": u"Her zaman bu sayfada imzala",
    "settings.sign_ext": u"Her zaman eklentiyi kullan",
    "settings.sign_ext_absent": (
        u"Bu cihazda eklenti bulunamadı — imzalar bu sayfada gerçekleşir."
    ),
    "settings.sign_ext_present": u"Bu cihazda eklenti bulundu.",
    "settings.sign_guide": u"Eklenti nasıl kurulur",
    "settings.sign_mode_browser": u"İmzalar bu sayfanın belleğinde gerçekleşir.",
    "settings.sign_mode_ext": u"İmzalar eklenti penceresinde onaylanır.",
    "settings.sign_mode_ext_page": (
        u"İmzalar eklentide kalır — web sitelerinden yalıtılmıştır."
    ),
    "settings.sign_revoke": u"Geri al",
    "settings.sign_sites": u"Bağlı siteler",
    "settings.sign_sites_empty": (
        u"Henüz onaylanan site yok — onaylar burada, site bazında geri alma "
        u"seçeneğiyle listelenir."
    ),
    # The trailing space on story_a is load-bearing: story_b begins with one
    # too (G4b proves both survive).
    "settings.sign_sites_story_a": u"Örnek: bir zar oyunu ",
    "settings.sign_sites_story_b": (
        u" sizin hesabınızla oynamanızı ister — onaylarsanız burada, yalnızca "
        u"o hesaba bağlı olarak listeler. İmzalar yine de her seferinde "
        u"sorulur. (Bu bağlantı hiçbir yere gitmez — kurgusal bir örnektir.)"
    ),
    "settings.sign_title": u"İmzalama",
    "settings.sign_warn": (
        u"Bu sayfada çalışan her betik — ele geçirilmiş bir barındırma "
        u"kopyası dahil — kilit açıkken anahtarlarınızı okuyabilir. "
        u"İmzalamayı eklenti üzerinden yaptırın ya da kontrol ettiğiniz bir "
        u"kopya çalıştırın."
    ),
    # Node-table column heads. Konum / Sağlayıcı reuse the geo-note wording;
    # Uç is the chain tip the node list talks about.
    "settings.th_chain": u"Zincir",
    "settings.th_handshake": u"El sıkışma",
    "settings.th_head": u"Uç",
    "settings.th_history": u"Geçmiş",
    "settings.th_location": u"Konum *",
    "settings.th_participation": u"Katılım",
    "settings.th_provider": u"Sağlayıcı *",
    "settings.theme_title": u"Tema",
}

# Keys whose Turkish value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from TR. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Turkish crypto UI keeps in Latin: HTLC, NFT, NFT
#     URI, MCR, PMA, UIA, Assert (op 55), Override (the transfer whose fee the
#     issuer pays), Ping (the node column; settings.probe_all already writes
#     "Tümüne ping"), the indicator tickers BB / EMA / PSAR / SMA, Discrete
#     (the chart's named aggregation mode) and Log (the price scale, already
#     spelled this way by market.px_log and market.vol_log);
#   * words whose CORRECT Turkish spelling IS the English bytes: Transfer is
#     this dictionary's Turkish word for a transfer (the transfer screen, the
#     TxBuilder link and the market's "Transfer" chip all ship it), and Bitasset
#     is its Turkish name for the asset class (a dozen "Bitasset ..." labels
#     already ship). Translating them again would change nothing, so they are
#     declared identical rather than re-typed;
#   * network ids, theme ids and sentinels the brief pins: mainnet / testnet /
#     devnet, original-blue / light / dark, "wss://…", "…", "—";
#   * the "24h Δ" data glyphs (market_net.col_change) and the "7d" window
#     marker - a number, a unit and the Greek delta, which the stats tab, the
#     volume column and the map legend all print the same way (tr.json already
#     ships "24s Δ" for market.chg_label and market.stat_chg);
#   * pure glue a table cell or edge card prints as data: "@ %(price)s ·
#     %(vol)s", "%(desk)s · %(a)s–%(b)s · %(vol)s", "@ %(price)s", "—",
#     "%(first)s → %(last)s" - translating the space inside a glue string would
#     change what the reader sees, so it stays English;
#   * the seed placeholder, which is real account names plus a 1.2.x id and so
#     is DATA under rule 1.
KEPT_ENGLISH = {
    # ---- account
    "account.op_assert_op": u"Assert",
    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    "account_net.class_transfer": u"Transfer",
    # ---- asset
    # "Bitasset" is this dictionary's Turkish name for the asset class (the
    # asset screen already ships "Bitasset seçenekleri", "Bitasset güncellendi"
    # a dozen times), so the correctly translated row label IS the English
    # bytes. Same reasoning for "Transfer" below and "Ping" at the bottom.
    "asset.bitasset_row": u"Bitasset",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.nft_uri_field": u"NFT URI",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    # ---- market
    "market.log_label": u"Log",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_empty": u"—",
    "market.tf_discrete": u"Discrete",
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
    "settings.th_ping": u"Ping",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",
}


if __name__ == "__main__":
    sys.exit(main())