#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n tr chunk-B: fill the help / pool / explorer / surface sections tr.json
still leaves in English, plus the honesty surface (i18n.*, help.confidence_*,
the translation-limitations article).

Scope: ONLY the sections listed below. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from tr.json, or one whose English master moved, is REFUSED;
  * TR + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset and
REFUSES anything outside them; this batch REFUSES anything outside help, pool,
pool_net, explorer, seo, splash, about, shell, menu and i18n. A key that
crosses the line is a reviewer's problem, never a script's silent edit.

WHY `i18n` IS IN SCOPE: the brief names the honesty surface explicitly
(`i18n.badge_*`, `i18n.risk_*`, `help.confidence_*`, the
translation-limitations article) and asks for it to be confirmed no longer
English. Those are the chip in the header, the * marker on signing lines, and
the article that explains them: three renderings of ONE warning, so they are
translated in the same batch and worded from the same four phrases the
confirmed probe run produced (`bir makine tarafından oluşturuldu`,
`insan denetiminden geçmedi`, `İngilizce aslı bir dokunuş uzakta`,
`İngilizce karşılığı gösteriniz`). `i18n.badge_chip` ("i18n") stays Latin like
in every other locale - it is the chip's own glyph, not prose.

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
                      reproduced exactly. Four values in this batch are pure
                      GLUE with a load-bearing blank - pool.my_swaps_hint and
                      pool.swaps_hint BEGIN with a space (they continue the
                      sentence their panel printed), pool.swap_preview and
                      explorer.transfer END with one - where a missing space
                      silently welds the computed value onto the label or drops
                      the sentence together;
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
                      was written with the de, es and zh tables open). The whole
                      file is swept and a hit OUTSIDE the owned sections is
                      reported as PRE-EXISTING rather than repaired - another
                      chunk owns those keys, and an insert-only pass that
                      "fixed" a neighbour would be exactly the silent edit the
                      scope refusal exists to prevent;
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
                            crypto UI keeps in Latin (HTLC, commit, WebCrypto,
                            ...), each with a reason;
                        (b) CONTINUOUS with the Turkish this dictionary SHIPS -
                            it is one of the words harvested at run time from
                            every tr.json value that differs from its English
                            master, or a Turkish inflected form of one
                            (güven -> güvenli, harita -> haritasında). The
                            harvest includes chunk-A's 362 strings, so this
                            batch inherits aguz -> aguzdan and the rest of its
                            declared stems with no re-declaration;
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

Two adaptations from chunk A this file follows, both forced by the language and
both argued there rather than inherited:

  * no apostrophe ban - Turkish orthography REQUIRES the apostrophe for a
    suffix on a proper noun or a loanword ("BTS'e", "BitShares'in",
    "İngilizce'yi"), and this dictionary already prints it. Each apostrophe this
    batch writes is listed by the run so a reviewer can check the genitive case
    on each one;
  * G9 is a vocabulary gate, not a Latin-character gate, because every word in
    a Latin-script language would trip the latter.

Register is FORMAL (siz) - the standard for Turkish financial UIs - and the
vocabulary is reused verbatim from the strings tr.json already ships, so this
batch reads like the rest of the dictionary: hesap, cüzdan, parola, kilit açmak,
imzalamak, yayınlamak, onaylamak, miktar/tutar, bakiye, fiyat, hacim, emir,
dolum, piyasa, borsa, masa, varlık, ihraççı, yayıncı, üretici, besleme, basım,
uzlaşma, teminat, borç, kredi, teklif, anlaşma, öneri, yetki, izin, tanık,
komite, çalışan, vekil, hakediş, bilet, gizli transfer, havuz, takas, akıllı
para, düğüm, zincir, ücret, anahtar, düzenek, ağ, harita, derinlik, adım,
satır, filtre, gezgin, panel, özet.

ONE TERM, ONE SPELLING. chunk A fixed the desk vocabulary and this batch
reuses its exact strings wherever they collide: `Genişlet`/`Daralt`,
`Temizle`, `Ağı çiz`, `Piyasa ağı`, `Varlık 1 (herhangi bir bacak)`,
`Piyasa ücreti`, `Adım`, `Eylem`, `adımda bağlı`, `temas eden`,
`daraltın`, `dokunun`. Where chunk A's sibling outside this batch already
ships a term (`Transfer`, `Airdrop`, `Spotlight`, `Trollbox`, `Cross Rates`,
`Bitasset`), the correctly spelled Turkish IS the English bytes and the key is
declared in KEPT_ENGLISH instead of re-typed a second way.

Morphology is the part a Turkish reader notices first, so the rules are worth
stating: a suffix agrees with the last vowel of its stem, so hesap (a) takes
back-vowel suffixes (hesabınızda) while bakiye (e) takes front ones
(bakiyeniz); case stacks (hesabınızda, işlemlerinden) and dropping a suffix
changes meaning, not just politeness; and a comparison must never invert.
G10 asserts the last one mechanically, and this batch adds the ramp pair
(`small → large` must stay `küçük → büyük`, never the reverse) because
pool_net.ramp is the one inverted-looking string in this batch.

The honesty surface (i18n.*, help.confidence_*, the translation-limitations
article) is the warning a Turkish reader gets about their OWN Turkish, so it is
written in plain factual register with no marketing tone and no euphemism:
"bir makine tarafından oluşturuldu", "insan denetiminden geçmedi",
"İngilizce aslı bir dokunuş uzakta", "İngilizce karşılığını gösteriniz" - the
four phrases the confirmed probe run produced, reused verbatim so one warning
reads one way across the chip, the star marker and the article.

Long markdown bodies (help, about, splash) keep the English line count and
heading count, and in `[label](#/hash)` the LABEL is translated while the HASH
stays byte-verbatim - the sitemap alone carries 71 of them. Sitemap labels
reuse the shipped menu.p_* strings (`Hesabım`, `Panel`, `Likidite Havuzları`,
`Yönetim`, ...) so the burger menu and the site map name a page the same way.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (26 September 2026, 3 October, 100 assets, 360px, 4K,
24h) the translation keeps the figure and spells the unit the way this
dictionary already spells it (`son 24 saat` for prose, `24s` for a compact
column head).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_tr_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_tr_chunkB.py --apply         # writes tr.json
  python3 tooling/apply_i18n_tr_chunkB.py --verify        # structural re-proof
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

# The sections this batch owns. Everything else belongs to chunk-A or to a
# later chunk and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool", "pool_net", "explorer", "seo", "splash", "about", "shell",
    "menu", "i18n",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from TR below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live outside this batch's own sections (settings); the shell
# brands live inside it and are kept in the list so a drift anywhere in the
# file is caught.
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
# continue through - _ . / so "index.html", "docs/vanilla-ui-dialog.md" and
# "?dialog=N" are one decision each. Turkish letters are spelled out so a
# dotless i (i) is not confused with a Latin one.
TR_CHARS = u"A-Za-zÇĞİIÖŞÜçğıiöşüÂÎÛâîû"
LATIN_TOKEN = re.compile(
    u"[" + TR_CHARS + u"][" + TR_CHARS + u"0-9]*"
    u"(?:[-_./][" + TR_CHARS + u"0-9]+)*"
)
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# G10: the comparison trap. A string that tells the reader a rule must keep the
# DIRECTION of that rule. Each entry is (en substring that marks the rule,
# Turkish string that must appear, Turkish string that would invert it).
# English masters are matched so a key whose wording changes fails loudly
# instead of silently dropping the check. chunk A proved the validation pair;
# this batch adds the ramp pair, because pool_net.ramp is the only string here
# whose Turkish could plausibly come out reversed.
COMPARISONS = (
    ("greater than zero", u"büyük", u"küçük"),
    ("must be in the future", u"gelecekte", u"geçmişte"),
    ("small → large", u"küçük → büyük", u"büyük → küçük"),
)

# The loanwords this batch is allowed to leave in Latin (G9a). Every entry is a
# word a Turkish crypto UI prints in Latin; anything else has to be Turkish.
# chunk A's 34 are NOT repeated: the harvest reads the shipped tr.json, where
# chunk A already wrote them, so they pass G9b with their reasons on record.
LOAN = frozenset((
    # --- git / build vocabulary the footer and the build story name
    "commit",         # the footer's ahead/behind counts ("3 commit önde");
                      # Turkish developers say commit, like every git UI
    "Master",         # the git BRANCH the footer links to: a name, i.e. data
    "issue",          # a GitHub issue; the build story names #3583 and
                      # "issue 1", and Turkish developer speech keeps it Latin
    "React",          # the framework the build story walks away from, the
                      # same class of proper noun as BitShares or DEX
    # --- the platform APIs the browser-support article probes by name
    # (websocket / webcrypto / bigint are already harvested, but they are
    #  named in ALL CAPS in the article, so the decision is recorded here too)
    "WebSocket", "WebCrypto", "BigInt",
    "http",           # named beside https in the insecure-context section
    "https",
    "localhost",      # a secure context a Turkish article still names in Latin
    # --- interface nouns Turkish UIs print in Latin
    "hamburger",      # the burger menu; the sitemap article names the same
                      # control Turkish menus call "hamburger menü"
    "platform",       # the browser article probes four platform features; Turkish
                      # borrows this word unchanged, like "hizmet" for service
    "LP",             # liquidity-provider shares; tr.json already ships
                      # "LP payları" from the pool desk, so this file's
                      # spelling is the dictionary's, not an invention
    "Stake",          # the pool desk's own verb: pool.confirm_stake and
                      # friends already ship "Stake" as the Turkish word
    # --- inherited from chunk A, still declared so a reviewer reading THIS
    #     file sees the full Latin surface of the honesty and map screens
    "HTLC", "Same-T", "BTS", "BitShares", "DEX", "MCR", "MSSR", "CER", "NFT",
    "UIA", "ID", "URL", "URI", "Enter",
))

# Turkish words this batch introduces that tr.json does not ship yet (G9d).
# Turkish agglutinates, so each entry is a STEM: the inflected forms this batch
# writes (düzeltme, düzeltti, Düzelt ...) are accepted from the stem, exactly
# as a shipped stem accepts its own forms. Each entry carries the reason it is
# here, so a reviewer sees every new word this file brings in rather than
# diffing 208 strings. Short stems are declared on purpose and matched only
# against longer forms, which is why a two-letter entry such as "ağ" below
# cannot swallow an unrelated word.
NEW_VOCAB = {
    # --- chunk A's two-letter stems, reused here rather than reinvented:
    # Ağ / ağın / ağa for the network views, "eriş" for "reachable", "besle"
    # for the feed verb (tr.json ships only its -me noun forms, so the bare
    # stem has to be declared before a shorter form like "beslediğiniz" passes)
    u"ağ": u"network; chunk A declared this two-letter stem, this batch "
           u"reuses it for the pool network's own naming instead of inventing "
           u"a second word for the same thing",
    u"eriş": u"reachable; chunk A declared it, the access sentence in the "
             u"backups article needs it as a bare stem",
    u"besle": u"to feed (a price feed); tr.json ships only the -me noun forms "
              u"('besleme', 'beslemeli'), which a shorter form cannot extend",
    # --- the honesty surface (the four phrases the confirmed run produced)
    u"çevir": u"translate / translation: 'makine doldurulmuş çeviri', 'Çeviri "
              u"sınırları'. The dictionary had no Turkish word for translation "
              u"at all - the honesty article cannot be written without one, and "
              u"declaring the stem covers çeviri, çevrildiği, çevrilir",
    u"denetim": u"human review: 'insan denetiminden geçmedi' is one of the "
                u"four confirmed-run phrases this batch must reuse",
    u"dokunuş": u"tap: 'İngilizce aslı bir dokunuş uzakta' is one of the four "
                u"confirmed-run phrases this batch must reuse",
    u"uzak": u"far: the tail of that same confirmed-run phrase (uzakta)",
    u"düzey": u"level, the confidence scale's word: 'güven düzeyi' in the "
             u"article heading, the confidence table head and the per-language "
             u"rating - one term for all three keys",
    u"düzelt": u"fix / correct, the heading and the closing promise of the "
               u"translation-limitations article",
    u"paragraf": u"paragraph, twice in the translation-limitations article "
                 u"(the length cap and the marker rule)",
    u"asıl": u"original: tr.json ships 'asıl', but neither 'aslı' nor "
             u"'aslında' extends it, and the article needs both",
    u"puan": u"rating / score: the confidence article's 'grades its own work'",
    u"ölçüt": u"yardstick: 'İngilizcenin kendisi ölçüttür'",
    u"dizgi": u"a translated string, the unit the honesty article counts",
    u"makale": u"article: the help article that explains the markers",
    u"anla": u"understand, in the heading 'ne anlama gelir'",
    u"yıldız": u"the * marker the reader taps on a signing line",
    u"söz": u"word; also covers 'sözcük' (the danger-wording rule)",
    u"izle": u"watch / follow: 'izleme', 'izlediği', 'izleyicisinde' - the "
             u"footer's tracker and the article's English-tracker",
    u"sakla": u"store / keep, the article's 'as it stores the English'",
    u"getir": u"restore, twice: the passphrase alone restores nothing, and a "
              u"key backup alone may not restore access",
    u"kelime": u"keyword, the dialog archive's filter",
    u"kolay": u"easy, in the same bullet",
    u"kapsa": u"cover, the length cap that makes the article itself the "
              u"reference for a long paragraph",
    u"geç": u"to pass (a review, a test): the honesty article's central "
            u"promise, 'insan denetiminden geçer / geçmiştir / geçmedi'",
    u"söyle": u"say, the reporting instructions ('söyleyin', 'söylemesi')",
    # --- the build story and the about dialog archive
    u"diyalog": u"the build dialog's transcript: about.dlg_* names it, and "
                u"the help article that points at it must name it the same way",
    u"arşiv": u"archive; tr.json ships 'arşivler' but not the stem, so the "
              u"singular needs declaring (arşivi, arşivin, arşivler)",
    u"yapılış": u"the noun this project uses for a build: 'Bu cüzdanın "
                u"yapılışı' (the About making-of title) and 'yapılış "
                u"diyaloğu'",
    u"yönetici": u"the wallet manager; tr.json ships only the inflected "
                 u"'yöneticisinde', and the backups article needs the stem",
    u"bağ": u"two-letter stem for 'bağlı olmamak' (the build story's promise "
            u"that the wallet depends on nothing) and for 'bağlantı' forms",
    u"derle": u"build / compile: 'derleme adımı yok', 'derleme tarihi', the "
              u"footer's build-date note and the build story's toolchain",
    u"depo": u"repository, the noscript notice's 'kaynak deposu'",
    u"çerçeve": u"framework: the rot report's central noun, named in the "
                u"About lede and the build story",
    u"kur": u"install / build: 'kurulum yok', 'Sürüm döngüsü "
            u"bağımlılıklarından kaçınmak için kuruldu'",
    # --- plain interface and article vocabulary this batch needs first
    u"marka": u"brand: the pool map's legend head and the browser article's "
              u"'asla marka adları'",
    u"düzen": u"layout: the phone-first layouts the build story promises and "
              u"the About page's phone-to-4K claim",
    u"bağlam": u"context, the browser article's 'güvenli olmayan bağlam' "
               u"(secure context) - the established Turkish term for it",
    u"prim": u"premium, the explorer's CER premium row",
    u"doğal": u"natural, the confidence article's 'reads naturally'",
    u"tuhaf": u"awkward, the confidence article's 'a phrase may still read "
              u"awkwardly' - the honest word, not a softer one",
    u"istem": u"prompt: the build story's 'every prompt that created this "
              u"wallet' and the dialog archive's unanswered-prompt note",
    u"biçim": u"form: 'as it stores it' (biçimiyle), 'deterministically' "
              u"(belirli biçimde)",
    u"dizi": u"a string, the brainkey's 'bir dizi kelime'",
    u"yeter": u"enough: the backups article's 'one backup is usually enough'",
    u"sor": u"ask: the browser article's 'never asks which browser you use'",
    u"sun": u"serve, the browser article's instructions for serving the folder",
    u"klasör": u"folder, the same instructions",
    u"sık": u"frequent, the browser article's 'the most common cause'",
    u"tara": u"scan, the explorer's 'scanned (first 100 assets)'",
    u"telefon": u"phone, the phone-first layouts the build story promises",
    u"tuzak": u"trap, the build story's 'thousand-hour trap'",
    u"vazgeç": u"walk away from, the build story's decision to leave React",
    u"özgün": u"original / raw, the build story's and the marker's wording",
    u"öl": u"to die, the build story's plain sentence about the wallet it "
           u"replaces",
    u"yıl": u"year: 'on yıl sonra' in the About build story",
    u"yüz": u"hundred: 'a hundred stale packages'",
    u"çalış": u"to run: 'çalışabilecek', 'çalışabilen' - tr.json ships only "
              u"the -ır / -ma shapes",
    u"konuş": u"to speak, the About trust row's 'the chain speaks integers'",
    u"otur": u"to sit at, the same row's 'every amount sits at its decimals'",
    u"esnek": u"forgiving, the About page's 'forgiving search'",
    u"ev": u"home, 'feel at home'",
    u"lütfen": u"please, the confidence table's 'Moderate - please verify'",
    u"kart": u"card, the sitemap's 'pages without a menu card'",
    u"hücre": u"cell, the article's 'an amount in a cell'",
    u"pusula": u"ballot, the voting desk's 'oy pusulası'",
    u"kurtar": u"to recover, 'recovery screen' in the browser article and "
               u"'recovery' in the help meta description",
    u"ol": u"the Turkish copula: tr.json ships only -ur / -du / -duğu shapes "
           u"of it, so a negative or infinitive form (olmamak, olmamasından) "
           u"needs the bare stem declared",
    u"ön": u"ahead of / in front of, the footer's 'N commit önde'",
    u"gez": u"to browse: gezin, gezilebilir, gezdiren - tr.json ships the "
            u"noun 'gezg[in]' but not the verb's stem",
    u"eşle": u"to pair: 'paired with BTS'; tr.json ships -şen / -şiyor shapes",
    u"dağıt": u"to distribute: 'shipped skeleton' is 'dağıtımda gelen', and "
              u"chunk A ships the noun 'dağıtımı', which no shorter form "
              u"extends",
    u"iskelet": u"skeleton, the offline placeholder the wallet ships with",
    u"özgür": u"free, 'browse freely' in the meta descriptions",
    u"aç": u"to open: 'credentials that open it' - tr.json ships only "
           u"'açık' and 'açılır' shapes",
    u"Eylül": u"September, a calendar month in the build story's date; a "
              u"proper noun, so it stays in Latin script like BTS and "
              u"BitShares",
    u"Ekim": u"October, the build story's second date; same reason",
    u"hâlâ": u"still: 'on yıl sonra hâlâ' (the About build story) - the "
            u"circumflex form tr.json does not ship yet",
    u"kasa": u"the local vault / keystore: 'Yerel kasalı bir web uygulaması' "
            u"and the browser article's four platform features",
    u"aslı": u"the possessive of 'asıl' (original): Turkish vowel mutation "
            u"turns asıl into aslı, which the gate's CONSONANT softening map "
            u"cannot see, so the mutated form is declared",
    u"aslında": u"the same mutation (asıl -> aslında, 'actually')",
    u"bellek": u"memory: the article's 'çeviri belleği' (translation memory); "
              u"chunk A declared the stem, this batch needs it too",
    u"cümle": u"sentence, the reporting bullet about a wrong sentence on a "
              u"confirm dialog",
    u"oku": u"to read: 'okunabilir', 'okuyup'; chunk A declared the stem",
    u"çevril": u"the rounded-vowel continuation of çevir (çevrilir, "
              u"çevrildiği): Turkish vowel harmony after r turns the next vowel "
              u"into i, which a prefix test cannot see",
    u"yarat": u"to create, the build story's 'every prompt that created this "
             u"wallet' (garan)",
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
# "bekle" + -yor is "bekliyor" is not a suffix, but "kolay" + -la is "kolayla"
# and "harita" + "-da" keeps the t. A plain prefix test would reject those, so
# the final consonant is compared through this softening map instead.
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
    "dokunuşta" or "işlemlerinden" is the SAME vocabulary decision as "dokunuş"
    and "işlem". Requiring every suffixed form to be declared by hand would
    bury the handful of decisions that matter under two hundred permutations of
    the same ten stems. Two pools with different lengths:
      * harvested words (from the shipped dictionary) need three letters or
        more before they may match by prefix - "ar" or "de" would otherwise
        match half the language by accident;
      * declared words are this file's own decision, recorded with a reason, so
        two letters are enough ("ağ", "bağ") - and they only ever match a LONGER
        form, never a bare two-letter token.
    Matching is case-insensitive because Turkish capitalises sentence starts and
    column heads ("Keşfet", "Ağı") and those are the same word.
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
        # A count keeping its English unit suffix ("24h", "360px") is data the
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
    # are printed loudly and never repaired here: chunk-A and the later chunks
    # own them, and an insert-only batch that "fixed" a neighbour would be the
    # silent edit the scope refusal exists to prevent. Only `bad` - problems this
    # batch can answer for - gates the exit code.
    pre = []
    # Structure is answerable for every key this batch OWNS (translated, or
    # kept English on purpose). The CHARACTER sweep is narrower: it asks "did
    # this batch introduce a stray script here?", and a key that is byte-
    # identical to its English master by declaration cannot have introduced
    # anything.
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
              "or another chunk's key; not touched, not fixed):")
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

    print("tr chunk-B: %d planned, %d differ from en, %d intentionally identical"
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
    # ================================================= honesty surface (i18n, 6)
    # The chip in the header. Its text is the same warning as the article, so
    # it borrows the article's two central phrases verbatim: the translation was
    # WRITTEN by a machine and has NOT PASSED human review.
    "i18n.badge_body": (
        u"Bu çeviriler bir makine tarafından oluşturuldu ve insan denetiminden "
        u"geçmedi. İmzalama ekranlarında * ile işaretli satırlar özgün "
        u"İngilizceyi de gösterir."
    ),
    "i18n.badge_details": u"Bunun anlamı",
    "i18n.badge_improve": u"Bu çeviriyi iyileştirmeye yardım edin",
    # "doğrulanmadı" rather than "denetlenmedi": the verified flag is the one
    # this wallet ships, and makine çevirdi / insan doğrulamadı keeps the
    # subject of each clause explicit.
    "i18n.badge_label": (
        u"Çeviri durumu: makine çevirdi, insan doğrulamadı"
    ),
    "i18n.risk_about_translations": u"Bu çeviriler hakkında",
    # The star marker on a signing line; chunk A's probe vocabulary already
    # carries "İngilizce karşılığı gösteriniz", and this is that same button.
    "i18n.risk_show_english": (
        u"Bu satırın İngilizce karşılığını gösteriniz"
    ),

    # ========================================================== about (18)
    "about.dlg_heading": u"Tüm yapılış diyaloğu",
    "about.dlg_heading_c": u"Tüm yapılış diyaloğu (%(total)s)",
    "about.dlg_no_reply": (
        u"Yanıt yok — sonraki istem hemen ardından geldi."
    ),
    "about.dlg_noscript": (
        u"Bu arşiv JavaScript ister; aynı metin kaynak depodaki "
        u"docs/vanilla-ui-dialog.md dosyasında durur."
    ),
    "about.dlg_search_clear": u"Temizle",
    "about.dlg_search_ph": u"Değişimleri filtreleyin…",
    "about.dlg_showing": u"Gösterilen",
    "about.dlg_showing_c": u"Gösterilen %(shown)s / %(total)s",
    "about.dlg_unavailable": u"Yapılış diyaloğu arşivi kullanılamıyor.",
    # The lede states the same three promises the trust row makes; "düz web
    # dosyaları" is the honest description of a folder a static server hands
    # over, and it is why no installer exists.
    "about.hero_lede": (
        u"BitShares blokzinciri için bir cüzdan — piyasalar, hesaplar, yönetim "
        u"ve keşif — düz web dosyaları olarak çalışır. Çerçeve yok, kurulum "
        u"yok, kayıt yok. Anahtarlarınız bu tarayıcıdan asla çıkmaz."
    ),
    # Same paragraph as help.topic_about-making_body below, minus the headings
    # and the dialog-archive section the article adds.
    "about.making_body": (
        u"Aşağıdaki, cüzdanın özgün yapılış kaydıdır: bu cüzdanı yaratan her "
        u"istemi, 26 Eylül 2026 tarihindeki \"bitshares-ui edin\" isteminden "
        u"3 Ekim'deki issue-1 düzeltmesine kadar, geliştiricilerin yanıtlarıyla "
        u"birlikte — hiçbirine dokunulmadan korunmuş olarak. "
        u"Bu cüzdanın temelini oluşturan kararları da kaydeder: issue #3583 ve onun bin "
        u"saatlik tuzağından sonra bir React yükseltmesinden daha fazlasından "
        u"vazgeçmek, böylece cüzdan sürüm döngüsü olan hiçbir şeye bağımlı "
        u"değil; işlemleri dışarı vermek yerine eski cüzdan gibi yerelde "
        u"imzalamak; klasik görünümü varsayılan yapan üç tema; sayıları insan "
        u"terimleriyle, asla çıplak zincir tam sayılarıyla değil; ilk adımdan "
        u"başlayarak telefona öncelik veren düzenler; ve ücretleri asla tahmin "
        u"etmeyip canlı zincirden okumak. Bunu bir tarih olarak okuyun: cüzdan "
        u"böyle yapıldı."
    ),
    "about.making_title": u"Bu cüzdanın yapılışı",
    "about.s2_title": u"Gerçek emir defterinde alım satım",
    "about.s3_body": (
        u"Yerini alan cüzdan, yüz bayat paketin ve kimsenin yeniden "
        u"üretemediği bir araç zincirinin altında öldü. Sürüm döngüsü "
        u"bağımlılıklarından kaçınmak için kuruldu: çerçeve yok, paket "
        u"yöneticisi yok, derleme adımı yok — on yıl sonra hâlâ bir tarayıcıda "
        u"çalışabilecek en küçük şey."
    ),
    "about.s3_title": u"Yıllarca güncellemesiz çalışır",
    "about.s4_body": (
        u"Geri dönen kullanıcılar kendini anında evinde hisseder — klasik "
        u"cüzdanla aynı sayfalar, paneller ve kelimeler — buna karşılık "
        u"bakiyeler, defterler ve bağlantı durumu yerinde canlı güncellenir. "
        u"Piyasa, hesap ve varlıklarda esnek arama, üç tema ve 360px telefondan "
        u"4K alım satım masasına kadar çalışan düzenler."
    ),
    "about.s4_title": u"Aynı sayfalar, canlı güncellemeler",
    "about.s5_body": (
        u"Zincir tam sayılarla konuşur; siz onları asla görmezsiniz. Her tutar "
        u"varlığının ondalık basamağına oturur, her yüzde gerçek değerine gelir "
        u"ve her ücret imzadan önce canlı zincirden okunur."
    ),

    # ======================================================== explorer (11 +7)
    "explorer.assets_mode_all": u"Tümü",
    "explorer.assets_mode_market": u"Akıllı paralar",
    "explorer.assets_mode_prediction": u"Tahmin",
    "explorer.assets_mode_user": u"Kullanıcı ihraçlı",
    # "of" as a slash: the count line reads "Gösterilen: Tümü — 5 / 12", and a
    # Turkish numeric range with a separator needs no genitive suffix. zh and
    # ja solved the same glue the same way.
    "explorer.assets_of": u"/",
    "explorer.assets_showing": u"Gösterilen",
    # CER is the chain's core exchange rate; the premium is what a publisher's
    # feed reports above it, estimated by the publisher-rule check.
    "explorer.feed_cer_premium": (
        u"Çekirdek kotasyon oranı (CER) primi (yayıncı kuralı tahmini)"
    ),
    "explorer.feeds_of": u"/",
    "explorer.feeds_scanned_suffix": u"tarandı (ilk 100 varlık)",
    "explorer.feeds_showing": u"Gösterilen",
    "explorer.no_assets_match": u'"%(q)s" ile eşleşen varlık yok.',

    # =========================================================== menu (10 +6)
    "menu.blurb_labs": u"Zincir ve düğüm işleri için güçlü araçlar.",
    "menu.blurb_personal": u"Sohbet, uyarılar ve kendi ayarlarınız.",
    "menu.d_account_net": u"transfer izleme",
    "menu.d_xrates": (
        u"BTS ve ötesinde her varlığın havuz fiyatları."
    ),
    # Account Network is account_net.title's own Turkish ("Hesap Ağı"), not a
    # second spelling; the Labs desks keep their shipped desk names.
    "menu.p_account_net": u"Hesap Ağı",
    "menu.p_apilab": u"API Laboratuvarı",
    "menu.p_eslab": u"ES Laboratuvarı",
    "menu.section_explore": u"Keşfet",
    "menu.section_labs": u"Laboratuvarlar",
    "menu.section_personal": u"Kişisel",

    # ===================================================== pool_net (27 +2)
    "pool_net.canvas_label": (
        u"Havuz ağı haritası. BTS'yi açmak için Enter tuşuna basın."
    ),
    "pool_net.col_a": u"Varlık 1",
    "pool_net.col_b": u"Varlık 2",
    "pool_net.col_pool": u"Havuz",
    "pool_net.collapse": u"Daralt",
    "pool_net.direct": u"BTS ile eşlenmiş",
    "pool_net.empty": u"Bu filtreye dokunan havuz yok.",
    "pool_net.expand": u"Genişlet",
    # "adımda" is the hop word account_net and pool.map_a_hops already ship.
    "pool_net.hops": u"BTS'e %(n)s adım",
    "pool_net.legend": u"Markalar",
    "pool_net.loading": u"Ağ yükleniyor…",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s havuz · %(hops)s",
    "pool_net.offline": (
        u"Ağ kullanılamıyor — dağıtımda gelen iskelet gösteriliyor. "
        u"Bağlandığınızda yeniden deneyin."
    ),
    "pool_net.offline_empty": (
        u"Ağ kullanılamıyor — önbelleğe alınmış iskelet havuzu yok."
    ),
    "pool_net.orphan": u"BTS ile bağlantısı yok",
    "pool_net.partial": (
        u"Canlı güncelleme eksik — dağıtımda gelen havuzlar gösteriliyor."
    ),
    "pool_net.phys": u"Fizik",
    "pool_net.prompt": (
        u"Varlık için düğüme, havuz için çizgiye dokunun."
    ),
    # G10: small → large must stay küçük → büyük, never the reverse.
    "pool_net.ramp": u"Havuz boyutu: küçük → büyük",
    "pool_net.ready": u"%(pools)s havuz · %(assets)s varlık",
    "pool_net.title": u"Havuz ağı",
    "pool_net.twin": u"Havuz satırları (%(n)s)",
    "pool_net.twin_more": (
        u"%(n)s havuzdan %(shown)s tanesi gösteriliyor — daha az görmek "
        u"için filtreyi daraltın."
    ),
    "pool_net.verdict_full": u"%(pools)s havuz · %(assets)s varlık",
    "pool_net.verdict_orphan": u"%(a)s ile %(b)s arasında yol yok",
    "pool_net.verdict_path": u"%(a)s, %(b)s varlığına %(n)s adımda ulaşıyor",
    "pool_net.verdict_star": u"%(s)s ile temas eden havuzlar: %(n)s",

    # ============================================================ pool (25 +2)
    "pool.asset_1_field": u"Varlık 1 (herhangi bir bacak)",
    "pool.asset_2_field": u"Varlık 2 (herhangi bir bacak)",
    "pool.clear_btn": u"Temizle",
    "pool.delete_not_empty": (
        u"Boş değil — silmeden önce %(legs)s 0 göstermeli."
    ),
    "pool.direct_hit": u"Doğrudan havuz araması — sayfalayıcı gizli.",
    "pool.map_core_self": u"BTS, BitShares'in çekirdek tokenidir.",
    "pool.min_swaps": u"En az takas",
    # Leading space is load-bearing: the panel printed the sentence this line
    # continues (G4b proves it survives).
    "pool.my_swaps_hint": (
        u" Yukarıdaki Takas panelinden bir tane çalıştırın — bu havuzdaki "
        u"takaslarınız burada listelenir."
    ),
    "pool.no_filter_match": u"Bu filtrelerle eşleşen takas yok.",
    "pool.spot_row": u"Anlık fiyat",
    "pool.stake_autofill_hint": (
        u"Bir tutar yazın — diğeri havuz oranında kendini doldurur."
    ),
    "pool.stake_preview_bad": (
        u"Tutarları denetleyin — pay tahmini yok."
    ),
    "pool.stake_preview_need_both": (
        u"Pay tahmini için iki tutarı da girin."
    ),
    "pool.stake_preview_unavailable": u"Pay tahmini kullanılamıyor (çevrimdışı).",
    "pool.stake_ratio_empty": (
        u"Havuz boş — iki tutarı elle girin."
    ),
    "pool.stake_ratio_row": u"Oran (anlık)",
    "pool.stake_shares_row": u"Tahmini LP payları",
    "pool.swap_desk": u"Takas Masası",
    "pool.swap_mkt_preview_dash": u"Piyasa ücreti (önizleme): —",
    "pool.swap_mkt_row": u"Piyasa ücreti",
    "pool.swap_preview": u"Teklif (önizleme): ",
    "pool.swap_preview_dash": u"Teklif (önizleme): —",
    # Leading space again: this line continues the panel's own sentence.
    "pool.swaps_hint": (
        u" Bu havuzdaki ilk takastan sonra takaslar görünür — yukarıdaki "
        u"Takas panelinden bir tane çalıştırın."
    ),
    "pool.uc_action": u"Eylem",
    "pool.uc_title": u"Devam etmek için kilidi açın",

    # =========================================================== seo (26)
    # Every title ends in the same brand line, "BitShares Cüzdanı": Cüzdan is
    # this dictionary's own Turkish word for wallet (the transfer screen, the
    # wallet manager and menu.p_password all ship it), so the brand reads in
    # Turkish rather than in a half-translated string.
    "seo.desc_about": (
        u"Bu BitShares cüzdanı hakkında — yerel anahtarlar, kayıt yok, izleme "
        u"yok. Özgürce gezin, yerelde imzalayın."
    ),
    "seo.desc_account": (
        u"Bu BitShares hesabını görüntüleyin — bakiyeler, emirler ve geçmiş "
        u"canlı olarak zincirden okunur. Giriş gerekmez."
    ),
    "seo.desc_account_net": (
        u"Bir hesabın kime gönderdiğini, kime borç verdiğini ve kimden borç "
        u"aldığını haritalayın — topluluk dizininden okunur. Giriş gerekmez."
    ),
    "seo.desc_dashboard": (
        u"BitShares paneli — bakiyeler, piyasalar ve zincir hareketi bir "
        u"bakışta. Özgürce gezin; anahtarlar cihazınızda kalır."
    ),
    "seo.desc_explorer": (
        u"BitShares bloklarını, işlemlerini ve varlıklarını inceleyin — canlı "
        u"zincir verisi, girişsiz gezilebilir."
    ),
    "seo.desc_help": (
        u"BitShares cüzdan yardımı — hesaplar, alım satım, oylama ve kurtarma "
        u"kılavuzları. Takıldığınızda buradan başlayın."
    ),
    "seo.desc_login": (
        u"Yerel BitShares cüzdanınızın kilidini açın — parola, beyin anahtarı "
        u"ya da içe aktarılmış anahtarlar. Anahtarlar bu cihazdan asla çıkmaz."
    ),
    "seo.desc_market": (
        u"BitShares emir defterinde BTS karşılığı USD alıp satın — canlı alış, "
        u"satış ve geçmiş, cihazınızda yerel olarak imzalanır."
    ),
    "seo.desc_markets": (
        u"BitShares emir defteri piyasalarını son 24 saatlik hacme göre "
        u"gezin ve her çiftin alım satım masasını açın. Giriş gerekmez."
    ),
    "seo.desc_pools": (
        u"BitShares likidite havuzlarını gezin — çiftler, bakiyeler ve "
        u"hareket canlı olarak zincirden okunur. Giriş gerekmez."
    ),
    "seo.desc_transfer": (
        u"BitShares varlıklarını herhangi bir hesaba gönderin. Her alanı "
        u"denetleyin, sonra yerelde imzalayın — anahtarlar cihazınızdan asla "
        u"çıkmaz."
    ),
    "seo.desc_voting": (
        u"BitShares tanıklarına, komite üyelerine ve çalışanlara oy verin. "
        u"Her oy pusulası cihazınızda yerel olarak imzalanır."
    ),
    "seo.desc_xrates": (
        u"Her havuz varlığının BTS ve ötesi cinsinden son takas fiyatları. "
        u"Giriş gerekmez."
    ),
    "seo.title_about": u"Hakkında — BitShares Cüzdanı",
    "seo.title_account": u"Hesap %(name)s — BitShares Cüzdanı",
    "seo.title_account_net": u"Hesap Ağı — BitShares Cüzdanı",
    "seo.title_dashboard": u"Panel — BitShares Cüzdanı",
    "seo.title_explorer": u"Blokzincir Gezgini — BitShares Cüzdanı",
    "seo.title_help": u"Yardım — BitShares Cüzdanı",
    "seo.title_login": u"Giriş — BitShares Cüzdanı",
    "seo.title_market": u"BTS/USD Borsası — BitShares Cüzdanı",
    "seo.title_markets": u"Piyasalar — BitShares Cüzdanı",
    "seo.title_pools": u"Likidite Havuzları — BitShares Cüzdanı",
    "seo.title_transfer": u"Fon gönder — BitShares Cüzdanı",
    "seo.title_voting": u"Tanıklara oy ver — BitShares Cüzdanı",
    "seo.title_xrates": u"Cross Rates — BitShares Cüzdanı",

    # ========================================================= shell (11 +3)
    "shell.footer_ahead": u"%(n)s commit önde",
    "shell.footer_ahead_one": u"1 commit önde",
    "shell.footer_at_build": u"derleme tarihi %(date)s",
    "shell.footer_behind": u"%(n)s commit geride",
    "shell.footer_behind_one": u"1 commit geride",
    "shell.footer_dahead": u"%(n)s önde",
    "shell.footer_dbehind": u"%(n)s geride",
    "shell.footer_diverged": u"ayrıldı:",
    "shell.footer_offbranch": u"Master üzerinde değil",
    "shell.footer_sync": u"eşit",

    # ========================================================= splash (20)
    "splash.card_dex_d": u"Açık piyasada alın ve satın.",
    "splash.card_explore_d": u"Blokları ve hesap geçmişini okuyun.",
    "splash.card_pool_d": u"İki varlığı havuzlayarak payınızı alın.",
    "splash.card_wallet_d": u"Anahtarları yalnızca bu cihazda tutun.",
    "splash.cards_title": u"Alım satım, havuz, keşif — buradan başlayın",
    "splash.cta_exchange": u"Borsada alım satım yapın",
    "splash.hero_sub": u"Anahtarlarınız sizin. Fonlarınız, zincir üstünde.",
    "splash.hero_sub2": u"Piyasaları ücretsiz gezin. Yalnızca imzalamak için kilidi açın.",
    "splash.hero_title": (
        u"Tarayıcınızdaki BitShares cüzdanı — kurulacak hiçbir şey yok."
    ),
    "splash.pulse_stale": u"— bayat",
    "splash.pulse_time": u"Baş blok zamanı",
    "splash.pulse_title": u"Canlı zincir sayıları",
    "splash.step1_d": u"Giriş gerekmez — önce zinciri gezin.",
    "splash.step1_t": u"Biraz gezin",
    "splash.step2_d": (
        u"Bir beyin anahtarı bu cihazda üretilir. Kâğıda yazın."
    ),
    "splash.step2_t": u"Cüzdan oluşturun",
    "splash.step3_d": (
        u"Limit emirler, likidite havuzları ve oy pusulaları — hepsi zincir "
        u"üstünde."
    ),
    "splash.step3_t": u"Al / havuzla / oy ver",
    "splash.topvol_unavailable": (
        u"En yüksek piyasa hacmi çevrimdışı — Ayarlar → Düğümler bölümünü "
        u"kontrol edin."
    ),
    "splash.trust_keys_d": (
        u"İmzalama cihazınızda yerel olarak olur. Hiçbir sunucu bir parolayı "
        u"ya da bir anahtarı asla görmez."
    ),

    # =========================================================== help (39+1)
    "help.about_link": u"Bu cüzdan hakkında",
    # The confidence table's three ratings. Turkish ships "Güvenlik: Yüksek"
    # and "Güvenlik: Orta" already (auth.security_*), so the scale reuses
    # them: Yüksek / İyi / Orta.
    "help.confidence_good": u"İyi",
    "help.confidence_high": u"Yüksek",
    "help.confidence_language": u"Dil",
    "help.confidence_level": u"Güven",
    "help.confidence_moderate": u"Orta — lütfen doğrulayınız",
    "help.elastic": u"Topluluk dizini (üçüncü taraf geçmişi)",
    # "Forum" IS the Turkish word and needs no genitive here, so it is declared
    # identical to English below (KEPT_ENGLISH) rather than re-typed.
    "help.report_translation_link": (
        u"Bir çeviri sorununu GitHub'da bildirin"
    ),
    "help.sitemap_sections": u"Bölümler",
    "help.translation_confidence_heading": u"Her dilin güven düzeyi",
    # The build story, article form: the same two paragraphs About carries,
    # under headings, plus the pointer to the dialog archive.
    "help.topic_about-making_body": (
        u"# Bu cüzdanın yapılışı\n"
        u"Aşağıdaki, cüzdanın özgün yapılış kaydıdır: bu cüzdanı yaratan her "
        u"istemi, 26 Eylül 2026 tarihindeki \"bitshares-ui edin\" isteminden "
        u"3 Ekim'deki issue-1 düzeltmesine kadar, geliştiricilerin yanıtlarıyla "
        u"birlikte — hiçbirine dokunulmadan korunmuş olarak.\n"
        u"Bu cüzdanın temelini oluşturan kararları da kaydeder: issue #3583 ve onun bin "
        u"saatlik tuzağından sonra bir React yükseltmesinden daha fazlasından "
        u"vazgeçmek, böylece cüzdan sürüm döngüsü olan hiçbir şeye bağımlı "
        u"değil; işlemleri dışarı vermek yerine eski cüzdan gibi yerelde "
        u"imzalamak; klasik görünümü varsayılan yapan üç tema; sayıları insan "
        u"terimleriyle, asla çıplak zincir tam sayılarıyla değil; ilk adımdan "
        u"başlayarak telefona öncelik veren düzenler; ve ücretleri asla tahmin "
        u"etmeyip canlı zincirden okumak. Bunu bir tarih olarak okuyun: cüzdan "
        u"böyle yapıldı.\n"
        u"# Tüm yapılış diyaloğu arşivi\n"
        u"Değişim değişim eksiksiz kayıt Hakkında sayfasında (#/about) durur. "
        u"Tüm değişimlere göz atmak, anahtar kelimeyle filtrelemek ya da belirli "
        u"bir değişime ?dialog=N ile doğrudan bağlanmak için sayfadaki \"Tüm "
        u"yapılış diyaloğu\" bölümünü genişletin."
    ),
    "help.topic_about-making_text": u"Bu cüzdanın yapılış kaydı —",
    "help.topic_about-making_title": u"Bu cüzdanın yapılışı",
    "help.topic_assets-feed_body": (
        u"# Fiyat beslemesi yayınlama\n"
        u"Piyasaya endeksli bir varlığın uzlaşma fiyatını Besleme masasından "
        u"yayınlayın; onay penceresi imzadan önce tam ücreti gösterir."
    ),
    "help.topic_assets-feed_text": (
        u"Beslediğiniz piyasaya endeksli varlıklar için fiyat beslemesi "
        u"yayınlayın."
    ),
    "help.topic_assets-feed_title": u"Fiyat beslemesi yayınlama",
    "help.topic_assets-issue_body": (
        u"# Varlık basımı\n"
        u"Hesabınızın kontrol ettiği bir varlığın yeni arzını Basma masasından "
        u"oluşturun; tutarlar varlığın hassasiyetini kullanır ve onay penceresi "
        u"imzadan önce tam ücreti gösterir."
    ),
    "help.topic_assets-issue_text": (
        u"Kontrol ettiğiniz varlığın yeni arzını Basma masasından basın."
    ),
    "help.topic_assets-issue_title": u"Varlık basımı",
    "help.topic_backups_body": (
        u"# Erken yedekleyin, iki kez yedekleyin\n"
        u"Yerel cüzdanınızı fonlamadan önce yedeğini alın — sonrası için tek "
        u"yedek genellikle yeterlidir, ama yedeği yalnızca sizin erişebildiğiniz "
        u"en az iki güvenli yerde tutun.\n"
        u"Bu cüzdanda yedek dosyası yoktur: beyin anahtarınızın kendisi yedeğidir "
        u"ve parola tek başına hiçbir şeyi geri getirmez. Kelimelerle parolayı "
        u"birlikte tutmazsanız fonlarınız gider. Parolayı asla kelimelerin "
        u"yanında saklamayın.\n"
        u"# Beyin anahtarınız yedeğin ta kendisidir\n"
        u"Ham anahtarları elle hiç içe aktarmadıysanız cüzdanınızın tamamı tek "
        u"bir beyin anahtarından belirli biçimde türetilir — bir dizi kelime. "
        u"Beyin anahtarını yazmak, o cüzdandaki her hesabı ve her fonu yedekler.\n"
        u"Cüzdan yöneticisinde görüntüleyin ve dijital olan her şeyden ayrı "
        u"tutularak kâğıda kopyalayın. Referans cüzdanın .bin dosyaları buraya "
        u"içe aktarılamaz — cüzdan bunu ekranda söyler ve hiçbir dosya "
        u"indirmesi yoktur.\n"
        u"# Gelişmiş: çok düzeyli yetkiler\n"
        u"Düz anahtarlar yerine ağırlıklı çok hesaplı yetkiler kullanıyorsanız "
        u"yalnızca anahtar yedeği erişimi geri getirmeyebilir — yetki yapısının "
        u"kendisi önemlidir.\n"
        u"İzinler makalesini yeniden okuyun ve yalnızca kelimeleri değil, "
        u"eksiksiz yetki kurulumunu kaydedin."
    ),
    "help.topic_browser_body": (
        u"# Yoklanan özellikler, asla marka adları\n"
        u"Bu cüzdan hangi tarayıcıyı kullandığınızı asla sormaz — kullandığı "
        u"dört platform özelliğini yoklar: WebSocket (zincir "
        u"verisi), WebCrypto (kasa), BigInt (para matematiği) ve yerel depolama "
        u"(ayarlar). Modern bir tarayıcıda uyarı olmaması her şeyin hazır "
        u"olduğu anlamına gelir.\n"
        u"# En sık neden: güvenli olmayan bağlam\n"
        u"Modern tarayıcılarda WebCrypto yalnızca güvenli bağlamlarda açılır: "
        u"https sayfaları, localhost ve açılan dosyalar. Aynı güncel tarayıcı "
        u"düz http üzerinden sunulduğunda (örneğin yerel ağdaki bir adres) "
        u"WebCrypto eksik bildirir — sorun tarayıcıda değil, adreste. Klasörü "
        u"https ya da localhost üzerinden sunun ya da index.html dosyasını "
        u"doğrudan açın.\n"
        u"# Yine de çalışır\n"
        u"Gezinme her zaman çalışır: bakiyeler, piyasalar, gezgin ve oylama "
        u"cüzdan özellikleri olmadan herkese açık zincir verisini okur. Yalnızca "
        u"yerel imzalama eksik parçaya ihtiyaç duyar. Bildirimi kapatmak onu bu "
        u"makinede gizler; hiçbir sayfayı engellemez."
    ),
    "help.topic_browser_text": (
        u"Cüzdanı hangi tarayıcılar çalıştırır ve uyumluluk bildirimi ne "
        u"anlama gelir."
    ),
    "help.topic_browser_title": u"Tarayıcı desteği",
    "help.topic_community_body": (
        u"# Topluluk\n"
        u"BitShares çevresindeki insanlar ve yerler — ana sayfa, kod, gezginler, "
        u"forumlar ve sohbetler — Topluluk sayfasında yaşar."
    ),
    "help.topic_community_text": (
        u"BitShares çevresinde sohbetler, forumlar, gezginler ve kod."
    ),
    "help.topic_community_title": u"Topluluk",
    "help.topic_htlc_text": (
        u"Ya ödeyen ya da iade eden hash kilitli takaslar."
    ),
    "help.topic_menu_body": (
        u"# Site menüsü\n"
        u"Menü sayfası bu cüzdandaki her ekranı bölümlere göre listeler, "
        u"böylece her masa tek dokunuş uzaktadır."
    ),
    "help.topic_menu_text": (
        u"Bu cüzdandaki her sayfa, gezinme menüsünün gruplandığı gibi."
    ),
    "help.topic_menu_title": u"Site menüsü",
    # 71 links: every LABEL is the shipped menu.p_* string (so the burger menu
    # and the site map name a page the same way); every HASH is byte-verbatim.
    "help.topic_sitemap_body": (
        u"Bu cüzdandaki her sayfa, hamburger menüsünün gruplandığı gibi "
        u"gruplanmıştır. Bağlantısı olan her şey doğrudan açılır; Menü kartı "
        u"olmayan sayfalar başlığı altında listelenen ayrıntı görünümleri kendi "
        u"üst sayfalarından açılır.\n"
        u"# Cüzdan\n"
        u"- [Panel](#/)\n"
        u"- [Hesabım](#/account/me)\n"
        u"- [Hesaplar](#/accounts)\n"
        u"- [Transfer](#/transfer)\n"
        u"- [Fatura](#/invoice)\n"
        u"- [Hakediş](#/vesting)\n"
        u"- [Cüzdan](#/wallet)\n"
        u"- [Cüzdan parolasını değiştir](#/wallet/password)\n"
        u"- [Cüzdan Oluştur (Beyin anahtarı)](#/create-wallet-brainkey)\n"
        u"- [Mevcut hesabı içe aktar](#/existing-account)\n"
        u"- [Yeni hesap kaydet](#/create-account)\n"
        u"- [Giriş](#/login)\n"
        u"- [Kayıt](#/registration)\n"
        u"- [Referanslar](#/referrals)\n"
        u"# Alım Satım\n"
        u"- [Borsa](#/markets)\n"
        u"- [Anında Alım Satım](#/instant-trade)\n"
        u"- [Likidite Havuzları](#/pools)\n"
        u"- [Cross Rates](#/cross-rates)\n"
        u"- [Borç Alma](#/borrow)\n"
        u"- [Takas Pazarı](#/barter)\n"
        u"- [Yatır / Çek](#/deposit-withdraw)\n"
        u"- [Same-T Fonları](#/samet)\n"
        u"- [Spotlight](#/spotlight)\n"
        u"# Kazanç ve Koruma\n"
        u"- [Kredi Teklifi](#/credit-offer)\n"
        u"- [Doğrudan Borçlandırma](#/direct-debit)\n"
        u"- [HTLC](#/htlc)\n"
        u"- [Biletler](#/tickets)\n"
        u"- [Airdrop](#/airdrop)\n"
        u"- [Özel Yetkiler](#/authorities)\n"
        u"- [Hesap Listeleri](#/lists)\n"
        u"# Yönetim\n"
        u"- [Oylama](#/voting)\n"
        u"- [Öneriler](#/proposals)\n"
        u"- [Çalışan Oluştur](#/create-worker)\n"
        u"- [Tahmin Piyasaları](#/prediction)\n"
        u"# Keşfet\n"
        u"- [Keşfet](#/explorer)\n"
        u"- [Varlıklar](#/assets)\n"
        u"- [Varlık Oluştur](#/assets/create)\n"
        u"- [Varlık Bas](#/assets/issue)\n"
        u"- [Besleme Yayınla](#/assets/feed)\n"
        u"- [Ağ ücretleri](#/explorer/fees)\n"
        u"- [İşlemler](#/ops)\n"
        u"- [Popüler İşlemler](#/top-ops)\n"
        u"- [Haberler](#/news)\n"
        u"# Gezgin\n"
        u"- [Keşfet (Blokzincir)](#/explorer)\n"
        u"- [Varlıklar](#/explorer/assets)\n"
        u"- [Havuzlar](#/explorer/pools)\n"
        u"- [Hesaplar](#/explorer/accounts)\n"
        u"- [Tanıklar](#/explorer/witnesses)\n"
        u"- [Komite](#/explorer/committee)\n"
        u"- [Piyasalar](#/explorer/markets)\n"
        u"- [Ücretler](#/explorer/fees)\n"
        u"- [Beslemeler](#/explorer/feeds)\n"
        u"# Laboratuvarlar\n"
        u"- [API Laboratuvarı](#/api-lab)\n"
        u"- [ES Laboratuvarı](#/es-lab)\n"
        u"- [İşlem Oluşturucu](#/txbuilder)\n"
        u"- [Hesap Ağı](#/account-network)\n"
        u"# Kişisel\n"
        u"- [Trollbox](#/trollbox)\n"
        u"- [Favoriler](#/favourites)\n"
        u"- [Fiyat Uyarıları](#/alerts)\n"
        u"- [Yardım](#/help)\n"
        u"- [Çeviri sınırları](#/help/translation-limitations)\n"
        u"- [Hakkında](#/about)\n"
        u"- [Topluluk](#/community)\n"
        u"- [Ayarlar](#/settings)\n"
        u"# Menü kartı olmayan sayfalar\n"
        u"Kayıt türleri, hesap ve piyasa masaları ile ayrıntı görünümleri "
        u"yukarıdaki sayfalardan ya da cüzdandaki başka bağlantılardan açılır.\n"
        u"- [Yerel kayıt](#/registration/local)\n"
        u"- [Bulut kaydı](#/registration/cloud)\n"
        u"- [Örnek hesap sayfası](#/account/committee-account)\n"
        u"- [Örnek piyasa masası](#/market/BTS_USD)\n"
        u"- [Örnek varlık sayfası](#/asset/BTS)\n"
        u"- [Örnek havuz masası](#/pools/1.19.66)\n"
        u"- [Menü özeti](#/menu)\n"
        u"Belirli bir kredi teklifi, anlaşma, öneri, blok, işlem, HTLC, tahmin "
        u"piyasası, transfer alıcısı, fatura, geçit, ayarlar sekmesi, gezgin "
        u"sekmesi ya da yardım makalesi için ayrıntı görünümleri kendi üst "
        u"sayfalarından açılır ve adresine bir kimlik ya da ad alır."
    ),
    "help.topic_sitemap_text": (
        u"Bu cüzdandaki her sayfa tek sayfada: her menü sayfası ve menü kartı "
        u"olmayan akışlar ile ayrıntı görünümleri."
    ),
    "help.topic_sitemap_title": u"Site haritası",
    "help.topic_translation-limitations_body": (
        u"Makine doldurulmuş işaretli bir çeviri bir makine tarafından "
        u"oluşturuldu. Bunun İngilizce ne dediğini denetlemek için onu hiçbir "
        u"insan okumadı — bu yüzden İngilizce dışındaki her dil, bu cüzdanın "
        u"başlığındaki işaret etiketini taşır. İngilizce, diğerlerinin "
        u"çevrildiği metindir; bu yüzden işaret taşımaz.\n"
        u"\n"
        u"# Bir satırdaki yıldız ne anlama gelir\n"
        u"Bir imzalama satırındaki yıldız aynı anda iki şey anlatır: metni bir "
        u"makine doldurdu ve İngilizce aslı bir dokunuş uzakta. Yıldıza "
        u"dokunun, İngilizce bu cüzdanın İngilizce aslında sakladığı biçimiyle "
        u"satırın altında görünür — diğer her dilin çevrildiği metin, onun "
        u"yeniden yazımı değil.\n"
        u"\n"
        u"İşaret satırı izler, satırın içindeki kelimeleri değil. Yıldız bir "
        u"bütün çeviri satırını işaretler ve cüzdan bu satırları sabit bir "
        u"kuralla seçer: imzalama, geri döndürülemez işlem ya da kurtarma "
        u"ekranlarındaki her satır — bir uzunluk sınırına kadar, çünkü uzun bir "
        u"paragraf onun yerine bu makaleyle kapsanır — ayrıca her yerde "
        u"İngilizcesi riskli sözcük taşıyan satırlar. Yalnızca bir kimlik ya da "
        u"tutar adı geçen bir satır bile işareti taşır (transferdeki Alıcı alanı "
        u"buna örnektir), bir kimlikten söz eden uzun paragraf taşımaz. "
        u"Çıplak bir zincir değeri — bir hücredeki tutar, bir sütundaki kimlik, "
        u"bir varlık sembolü — zaten çeviri satırı değildir, bu yüzden hiç işaret "
        u"taşımaz: arkasında karşılaştırılacak bir İngilizce metin yoktur.\n"
        u"\n"
        u"# Güven düzeyleri ne anlama gelir\n"
        u"Bu cüzdanın gönderdiği her dil tek bir güven düzeyiyle gelir; düzey "
        u"aşağıdaki tabloda listelenir. Yüksek, metnin İngilizceyi yakından ve "
        u"doğal biçimde izlediği anlamına gelir. İyi, metnin kullanılabilir "
        u"olduğu anlamına gelir, ancak bir ifade yine de tuhaf okunabilir. Orta, "
        u"metni bir taslak gibi okuyup buna güvenmeden önce İngilizcesini "
        u"denetlemeniz gerektiği anlamına gelir.\n"
        u"\n"
        u"Aşağıdaki düzeylerin her biri, metinleri yazan makinenin kendi işini "
        u"puanlamasıdır; bağımsız hiç kimse denetlemedi. Bir düzey, bir "
        u"dilin bütünü için şimdiye kadar hangi şeyin denetlendiğini anlatır, "
        u"satır satır değil. İngilizcenin kendisi ölçüttür: elle yazılmıştır ve "
        u"diğer her dil İngilizceden çevrilir.\n"
        u"\n"
        u"# Bir dizgiyi nasıl düzeltirsiniz\n"
        u"Düzeltmeler bir bildirimle başlar. Satırın hangi dilde olduğunu "
        u"söyleyin, o satırın açıkladığı anahtarı verin, söylemesi gereken "
        u"İngilizceyi ekleyin ve yerine kendi kullanacağınız ifadeyi önerin.\n"
        u"\n"
        u"- Her satır için tek bildirim, bir düzeltmeyi kolaylaştırır.\n"
        u"- Önce imzalama ekranlarını bildirin: onay penceresindeki yanlış bir "
        u"cümle pahalı olan türdür.\n"
        u"- Bu makalenin sonundaki bağlantıyı kullanın. Bu projenin izleyicisinde "
        u"çeviriler için zaten etiketlenmiş bir kayıt açar, böylece hiçbir şeyi "
        u"yeniden yazmanız gerekmez.\n"
        u"\n"
        u"# Düzeltme, insan denetiminden geçmenin tek yoludur\n"
        u"Bir dizgiyi makine doldurulmuştan çıkaran hiçbir şey yoktur: ne dilin "
        u"ne kadar çok kullanıldığı, ne ikinci bir makinenin birincisini "
        u"onaylaması, ne de bir çeviri belleği. Bir dizgi, bir kişi onu kendi "
        u"dilinde okuyup kabul ettiğinde insan denetiminden geçer; bir satır "
        u"yalnızca gerçekten denetlenen dil için insan denetiminden "
        u"geçmiştir.\n"
        u"\n"
        u"O zamana kadar işaret yerinde kalır. Hiçbir insanın okumadığı bir "
        u"çeviri, hiç çeviri olmamasından iyidir; ama bir kişinin onayladığı "
        u"çeviriyle aynı şey değildir."
    ),
    "help.topic_translation-limitations_text": (
        u"Makine doldurulmuş çeviriler etiketlenir; İngilizce aslı bir dokunuş "
        u"uzaktadır. Bir satırı düzeltmemize yardım edin."
    ),
    "help.topic_translation-limitations_title": u"Çeviri sınırları",
    "help.topic_voting_text": (
        u"Tanıklara, komiteye ve çalışanlara oy verin — ya da vekile devredin."
    ),
    "help.topic_wallets_body": (
        u"# Yerel kasalı bir web uygulaması\n"
        u"Bu uygulama tarayıcınızda çalışır ve ağa geçit olarak bir zincir "
        u"düğümüyle konuşur. Gizli olan her şey tarayıcınızın yerel kasasında "
        u"kalır.\n"
        u"# Bulut girişi yok\n"
        u"Bu cüzdanda kullanıcı adı ve parola girişi yoktur: buradaki her cüzdan "
        u"tek bir tarayıcıya yereldir. Hesabınızı yeni bir tarayıcıda ya da "
        u"bilgisayarda kullanmak için aynı beyin anahtarıyla başlayın — onu "
        u"kendi başına her yerden açan kimlik bilgileri yoktur.\n"
        u"# Yerel cüzdan\n"
        u"Yerel cüzdan, belirli bir tarayıcının içindeki bir veritabanıdır. "
        u"Beyin anahtarınızı alıp içe aktarmadıkça başka bir bilgisayarda ya da "
        u"tarayıcıda açılmaz.\n"
        u"Gerçek fonlar için yerel bir cüzdana güvenmeden önce Yedekler "
        u"makalesine bakın.\n"
        u"# Parola disiplini\n"
        u"Parola kasayı şifreler. Kısa ya da yeniden kullanılan bir parola "
        u"tahminle ele geçer; kâğıda yazılmış benzersiz bir parola değil.\n"
        u"Parolayı değiştirmek her şeyi yeniden şifreler — önce mevcut parolayı "
        u"doğrulayın, sonra gitmeden önce cüzdanın yine açıldığını doğrulayın."
    ),
}

# Keys whose Turkish value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from TR. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords and acronyms a Turkish crypto UI keeps in Latin: HTLC, Stake
#     (the pool desk's own verb - pool.confirm_stake already ships it),
#     Airdrop, Spotlight, Trollbox, Cross Rates, ID, MCR, MSSR, and the chip's
#     own glyph "i18n" that every locale keeps;
#   * words whose CORRECT Turkish spelling IS the English bytes: Transfer is
#     this dictionary's Turkish word for a transfer (the transfer screen, the
#     TxBuilder link, nav.transfer and the market's Transfer chip all ship
#     it) and Forum is the Turkish word the help link needs. Translating them
#     again would change nothing, so they are declared identical rather than
#     re-typed;
#   * brands the brief pins: shell.brand, the two footer brands;
#   * the two footer brands and the network/theme ids and sentinels, which are
#     DATA (a chain id, a branch name, a "—");
#   * pure glue a table cell, a title attribute or a node card prints as data:
#     "%(net)s - %(host)s", "mcr %(mcr)s; mssr %(mssr)s", "%(id)s @ %(ts)s",
#     "%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
#     "%(pool)s · %(a)s–%(b)s" - translating the space inside a glue string
#     would change what the reader sees, so it stays English;
#   * the share-asset placeholder "symbol, 1.3.x, or pool 1.19.x", which is real
#     asset ids and so is DATA under rule 1.
KEPT_ENGLISH = {
    # ---- i18n
    "i18n.badge_chip": u"i18n",
    # ---- explorer
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.pill_transfer": u"Transfer",
    # The trailing space is load-bearing: the symbol follows it (G4b).
    "explorer.transfer": u"Transfer ",
    "explorer.th_mssr": u"MSSR",
    # ---- help
    "help.forum": u"Forum",
    "help.topic_spotlight_title": u"Spotlight",
    # ---- menu
    "menu.p_airdrop": u"Airdrop",
    "menu.p_htlc": u"HTLC",
    "menu.p_spotlight": u"Spotlight",
    "menu.p_transfer": u"Transfer",
    "menu.p_trollbox": u"Trollbox",
    "menu.p_xrates": u"Cross Rates",
    # ---- pool
    "pool.share_or_pool_hint": u"symbol, 1.3.x, or pool 1.19.x",
    "pool.stake_link": u"Stake",
    # ---- pool_net
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
}


if __name__ == "__main__":
    sys.exit(main())
