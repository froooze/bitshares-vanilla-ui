#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n tr chunk-C: fill the SIGNING / ACTION sections tr.json still leaves in
English (approval, xrate, borrow, proposal, trollbox, vote, barter, pool_detail,
auth, tour, trade, transfer, htlc, nav, unlockconfirm, createworker, gateway,
instant, createaccount, credit, debit, market_ind, txbuilder, common,
dashboard, misc, ticket, and the one-key leftovers).

Scope: ONLY the sections listed below. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from tr.json, or one whose English master moved, is REFUSED;
  * TR + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset;
chunk-B owns help, pool, pool_net, explorer, seo, splash, about, shell, menu and
i18n's prose; this batch REFUSES anything outside its own list. A key that
crosses the line is a reviewer's problem, never a script's silent edit.

WHY THIS BATCH IS THE SAFETY-CRITICAL ONE. Most of these strings render on the
one surface where a mistranslation can COST MONEY: the unlock dialog, the
signing confirmation dialog and the fields inside it. Those dialogs are DUAL
LINE - the user reads the Turkish with the English master one tap away (the *
marker), so a wrong Turkish is checked, not obeyed silently. That cuts both
ways: a terse rendering is safer than a fluent wrong one only if the Turkish
cannot DROP information. Turkish agglutinates, so one noun carries the case
suffixes that encode who-does-what-to-whom, and dropping one changes meaning
rather than just politeness. Every string below therefore carries the full
suffix stack where the full stack carries the fact:

  * `transfer.enclosed_op_note` says the enclosed op "executes only AFTER
    approvals" - G10 pins the ORDER, because "onaylardan önce" would read as
    "you are paid before the co-owners sign", which is the exact wrong-way
    round a signing dialog must never do;
  * `transfer.propose_notice_locked` says the PROPOSER defaults to
    %(name)s WHILE LOCKED - the proposer pays the fee, so the reader must see
    whose authority is being spent, and G10 refuses "kilit açıkken";
  * `borrow.bids_no_cancel` and `xrate.base_pinned` say things CANNOT be
    cancelled / removed - irreversible facts, both pinned so no future edit can
    soften them into "iptal edilebilir";
  * `vote.retried_prefix` / `vote.retry_self` report that the node REJECTED the
    proxy mode and the vote went out as SELF - the opposite claim would tell a
    user their proxy was honoured when it was not, so both directions are
    pinned;
  * `vote.proxy_follows` states whose stake follows whom. Reversed, it becomes
    "this account follows your slate", the opposite permission, so it is
    pinned word-for-word;
  * `xrate.*` pins the HOP COUNTS (3 and 6) and the "nothing is signed, nothing
    is stored" safety claim - a rate with the wrong hop depth invents a price;
  * `htlc.list_sub` pins WHO gets refunded when nobody redeems;
  * `createworker.draft_a_worker...` pins that the preview and the quoted fee
    are LIVE (chain-priced), not estimates;
  * the password discipline (principle #9) is pinned everywhere it appears:
    reads never gate on unlock, the password is asked only at signing.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    the brands, network ids, theme ids and sentinels stay
                      byte-verbatim (the list tooling/check_i18n.py checks as
                      IDENTIFIERS, plus devnet, the two footer brands and the
                      shell brand, which that gate does not name);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master;
  G4b edge spaces   leading / trailing whitespace of the English master is
                      reproduced exactly. Six values in this batch are pure
                      GLUE with a load-bearing space - approval.account,
                      approval.chain, approval.site_prefix, approval.expires_in,
                      gateway.coin_label, htlc.hash_label, xrate.load_failed,
                      xrate.remove_btn all END with one, barter.paid_by_suffix
                      ends with '): ' and vote.proxy_follows BEGINS with ' - '
                      (an em dash) - where a missing space silently welds the
                      computed value onto the label or drops the sentence;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving
                      in lockstep with the bytes;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  script         no Devanagari, Cyrillic, CJK or Greek character may
                      appear in any value THIS BATCH writes. Turkish is Latin,
                      so the contaminated runs are the four non-Latin scripts a
                      copy-paste from a sibling locale would drag in. The whole
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
                            crypto UI keeps in Latin (WebCrypto, BTS, ...), each
                            with a reason;
                        (b) CONTINUOUS with the Turkish this dictionary SHIPS -
                            it is one of the words harvested at run time from
                            every tr.json value that differs from its English
                            master, or a Turkish inflected form of one
                            (güven -> güvenli, harita -> haritasında). The
                            harvest includes chunks A and B's ~3,700 strings,
                            so this batch inherits hesap, cüzdan, parola, öneri,
                            onay, yayın, imzala, kilit açmak and the rest of
                            their vocabulary with no re-declaration;
                        (c) a token of the ENGLISH master of that same key -
                            DATA under rule 1: an object id, an op number, a
                            field name, an indicator acronym, a placeholder
                            sample (alice,10), a currency list (USD, CNY, BTC);
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
  G10 direction     every rule sentence keeps the DIRECTION of its rule. Each
                      entry is (en substring that marks the rule, Turkish string
                      that must appear, Turkish string that would invert it).
                      Turkish has no word-order safety net here: "onaylardan
                      önce" and "onaylardan sonra" are the same words in the
                      opposite order, and only the second one is true. The pairs
                      chunks A and B proved are re-asserted here so a future
                      edit to one of those masters cannot slip past this file.

Two adaptations from chunk B this file follows, both forced by the language and
both argued there rather than inherited:

  * no apostrophe ban - Turkish orthography REQUIRES the apostrophe for a
    suffix on a proper noun or a loanword ("İşlem Oluşturucu'yu aç", "BTS'den",
    "WebCrypto'yu", "hash'e"), and this dictionary already prints it. Each
    apostrophe this batch writes is listed by the run so a reviewer can check
    the case suffix on each one;
  * G9 is a vocabulary gate, not a Latin-character gate, because every word in
    a Latin-script language would trip the latter.

Register is FORMAL (siz) - the standard for Turkish financial UIs - and the
vocabulary is reused verbatim from the strings tr.json already ships, so this
batch reads like the rest of the dictionary. The signed-off probe run
(`tooling/probe_runs/tr-runB-nemotron3.json`) is the wording authority wherever
a string in this batch is the same string it answered, so the eight signing
surfaces all read one way: `İmzalamak için kilidi açınız` is the title of every
"Unlock to sign" dialog, `Cüzdan parolanızı giriniz.` is the one password
prompt, `Parola` is the one password label, and `Onaylandı ve yayımlandı.` is
what the approval screen says after it broadcast. That is a deliberate
`yayımla` (not the `yayınla` the rest of the dictionary prefers) because the
confirmed run produced it and the brief requires its wording verbatim.

ONE TERM, ONE SPELLING. chunks A and B fixed the desk vocabulary and this
batch reuses their exact strings wherever they collide: `Devam etmek için
kilidi açın` (pool.uc_title -> trade.uc_title, transfer.uc_title), `Kilidi aç
ve incele` (trade.unlock_review -> transfer.unlock_sign), `Kilidi aç ve
zincire yaz`, `Satılacak toplam` (debit.total_field -> trade.uc_total),
`Önerileri görüntüle` (transfer.view_proposals -> auth.multisig_open_proposals),
`İşlem Oluşturucu`, `Önerileri görüntüle`, `Kilit açılamadı.`
(common.unlock_failed -> unlockconfirm.unlock_failed), `Bilinmeyen varlık.`
(barter.unknown_asset -> common.unknown_asset), `Geri`, `Onayla`, `Kapat`,
`Evet`/`Hayır`. Where the correctly spelled Turkish IS the English bytes the
key is declared in KEPT_ENGLISH instead of re-typed a second way - that is why
Transfer, Airdrop, Spotlight, Trollbox, Cross Rates, Limit, ID, URL, Delta,
Coin, Hash, Site and the pure-sentinel "—" are listed there rather than
invented.

Morphology is the part a Turkish reader notices first: a suffix agrees with the
last vowel of its stem, so hesap (a) takes back-vowel suffixes
(hesabınızda) while bakiye (e) takes front ones (bakiyeniz); case stacks
(öneren, onaylayan, imzalayan) and dropping a suffix changes meaning, not just
politeness. Where the case carries the fact - `öneren` (who proposes, and pays
the fee), `onaylayan hesap` (who approves), `ücreti ödeyen` (who pays), `size
iade edilir` (who is refunded) - the full stack is written out.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where the
English quotes a number (3 hops, 6 pool hops, 24 hours, op numbers) the
translation keeps the figure verbatim and spells the unit the way this
dictionary already spells it (`3 havuz adımı`, `son 24 saat`, `24s` for a
compact marker).

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_tr_chunkC.py                 # dry run (asserts)
  python3 tooling/apply_i18n_tr_chunkC.py --apply         # writes tr.json
  python3 tooling/apply_i18n_tr_chunkC.py --verify        # structural re-proof
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

# The sections this batch owns. Everything else belongs to chunk-A or chunk-B
# and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "approval", "xrate", "borrow", "proposal", "trollbox", "vote", "barter",
    "pool_detail", "auth", "tour", "trade", "transfer", "htlc", "nav",
    "unlockconfirm", "createworker", "gateway", "instant", "createaccount",
    "credit", "debit", "market_ind", "txbuilder", "common", "dashboard",
    "misc", "ticket", "assets_feed", "compat", "eslab", "explorer_assets",
    "i18n", "news", "pools", "prediction", "samet", "vesting",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from TR below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Most of them live outside this batch's own sections; the shell brands live in
# chunk B's, and are kept here so a drift anywhere in the file is caught.
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
# "?dialog=N" are one decision each, and through the APOSTROPHE in exactly the
# position Turkish orthography puts it - after the stem, before the case suffix
# ("Oluşturucu'yu", "WebCrypto'yu", "BTS'den") - so a suffixed proper noun stays
# ONE token and the head rule below can split it. Turkish letters are spelled
# out so a dotless i (i) is not confused with a Latin one.
TR_CHARS = u"A-Za-zÇĞİIÖŞÜçğıiöşüÂÎÛâîû"
LATIN_TOKEN = re.compile(
    u"[" + TR_CHARS + u"']" + TR_CHARS + u"0-9]*"
    u"(?:[-_./][" + TR_CHARS + u"0-9]+)*"
)
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# G10: the comparison trap. A string that tells the reader a rule must keep the
# DIRECTION of that rule. Each entry is (en substring that marks the rule,
# Turkish string that must appear, Turkish string that would invert it).
# English masters are matched so a key whose wording changes fails loudly
# instead of silently dropping the check. The first three are chunks A and B's
# proven pairs, re-asserted here so this file also guards those masters.
COMPARISONS = (
    # --- inherited, re-asserted
    ("greater than zero", u"büyük", u"küçük"),
    ("must be in the future", u"gelecekte", u"geçmişte"),
    ("small → large", u"küçük → büyük", u"büyük → küçük"),
    # --- IRREVERSIBILITY. An irreversible fact softened into its opposite is
    # the worst error this batch could ship: the reader believes they can undo
    # something the chain cannot.
    ("Bids cannot be cancelled", u"iptal edilemez", u"iptal edilebilir"),
    ("cannot be removed", u"kaldırılamaz", u"kaldırılabilir"),
    # --- ORDER. Turkish has no word-order safety net: "onaylardan önce" and
    # "onaylardan sonra" share every word.
    ("only after approvals", u"yalnızca onay", u"onaylardan önce"),
    ("direct op, not by proposal", u"öneriyle değil", u"öneriyle oluşturulur"),
    # --- AUTHORITY while locked. The proposer pays the fee; if the Turkish
    # reads as though the wallet were unlocked, the reader signs for an account
    # they did not choose.
    ("while locked", u"kilitliyken", u"kilit açıkken"),
    # --- THE VOTE FALLBACK. "published as self" vs "published as the proxy"
    # changes WHO the vote counted for; a silent flip tells a user their proxy
    # was honoured when the node refused it.
    ("published as self", u"kendi hesabı", u"vekiliniz olarak"),
    ("retrying once as self", u"kendi hesabınız", u"vekiliniz olarak"),
    # --- WHO FOLLOWS WHOM. Reversed, this becomes "this account follows your
    # slate" - the opposite permission, in a sentence whose two halves are
    # otherwise identical.
    ("your stake follows this account", u"hakedişiniz bu hesabı izler",
     u"bu hesabın hakedişi sizi izler"),
    # --- LIVE vs ESTIMATED. A fee the chain has not priced yet must never be
    # rendered as though it were; "tahmini" here would be a lie about money.
    ("Preview is live", u"canlı", u"tahmini"),
    ("quotes the live fee", u"canlı ücret", u"tahmini ücret"),
    ("with a live fee preview", u"canlı ücret", u"tahmini ücret"),
    ("live chain reads", u"canlı zincir okumaları", u"anlık görüntüler"),
    # --- WHAT WAS AND WAS NOT CHECKED.
    ("balances not checked", u"bakiyeler denetlenmedi", u"bakiyeler denetlendi"),
    ("nothing is signed", u"imzalanmaz", u"imzalanır"),
    # --- HOP DEPTH. The number IS the claim: a 3-hop route quoted as 6 hops
    # invents a price out of a pool the reader cannot trade in.
    ("within 3 hops", u"3 havuz adımı", u"6 havuz adımı"),
    ("within 6 pool hops", u"6 havuz adımı", u"3 havuz adımı"),
    # --- WHO GETS THE MONEY BACK when nobody redeems an HTLC.
    ("or you are refunded", u"size iade edilir", u"alıcıya iade"),
    # --- PRINCIPLE #9, the password discipline. Reads never gate on unlock.
    ("only signing needs the password", u"parola yalnızca imzalamak",
     u"parola her işlemde"),
    ("password asked only at signing", u"parola yalnızca imzalamak için",
     u"parola açılışta"),
    ("password is asked only at signing", u"parolanız yalnızca imzalamak",
     u"parolanız açılışta"),
    ("Browsing is public", u"Gezinme herkese açık", u"Gezinme parola ister"),
    # --- A SHARED ACCOUNT IS A PROPOSAL plus CO-OWNER APPROVALS; saying
    # anything less teaches the reader that one key can spend a shared account.
    ("proposals + co-owner approvals", u"öneri + ortak sahip onayları",
     u"tek anahtar yeter"),
    # --- DEALS APPEAR ONLY AFTER A BORROW. Flipped, it invites the reader to
    # look for a deal the chain has not created yet.
    ("deals appear after you borrow", u"ödünç aldıktan sonra",
     u"ödünç almadan önce"),
    # --- the candle window's "N of M": the GOT count over the ASKED count, on
    # both the market and the pool chart. Reversed, it would claim a window is
    # fuller than the node returned.
    ("%(actual)s of %(requested)s", u"%(actual)s / %(requested)s",
     u"%(requested)s / %(actual)s"),
    # --- THE CHART'S TWO AXES. The pair must not swap, or "Invert" would read
    # as the label for the other orientation than the one it toggles.
    ("A-per-B / B-per-A", u"A/B, B/A", u"B/A, A/B"),
)

# The loanwords this batch is allowed to leave in Latin (G9a). Every entry is a
# word a Turkish crypto UI prints in Latin; anything else has to be Turkish.
# Chunks A and B's loanwords are NOT repeated: the harvest reads the shipped
# tr.json, where those chunks already wrote them, so they pass G9b with their
# reasons on record. Only what this batch writes fresh is declared here.
LOAN = frozenset((
    # --- the core-asset ticker, which this batch's welcome line names. Chunk A
    # already shipped "BTS" (vesting, samet, menu), so this is the dictionary's
    # own spelling rather than an invention.
    "BTS",
    # --- the browser platform API compat.insecure_hint names as the thing the
    # browser withholds. Turkish articles still name it in Latin; the genitive
    # suffix arrives with an apostrophe ("WebCrypto'yu").
    "WebCrypto",
    "https",         # the scheme paired with localhost in the same sentence
    "localhost",      # a secure context a Turkish article still names in Latin
    # --- the two native-coins nouns the gateway page already prints in Latin
    # (gateway.backing_fact "Destek coin'i", gateway.coins_right_now " coin
    # şu anda."), so this batch's prose about them matches the shipped rows.
    "coin",
    # --- the two axis ORIENTATIONS of the pool chart, written the way Turkish
    # price quotes write them (B/A) rather than the English A-per-B. The G10
    # pair pins their order, so the notation being Latin costs nothing.
    "A/B",
    "B/A",
    # --- Stochastic, the indicator. Turkish technical writing transliterates
    # it as "Stokastik" next to SMA, EMA, RSI and MACD, which pass as
    # English-master tokens (rule c); transliterating one name and not the
    # other four would be the inconsistency, so this one is declared here.
    "Stokastik",
))

# Turkish words this batch introduces that tr.json does not ship yet (G9d).
# Turkish agglutinates, so each entry is a STEM: the inflected forms this batch
# writes (gösterilebilir, hatırla, reddedildi, ...) are accepted from the stem,
# exactly as a shipped stem accepts its own forms. Each entry carries the reason
# it is here, so a reviewer sees every new word this file brings in rather than
# diffing 148 strings.
NEW_VOCAB = {
    # --- the approval dialog's own verbs
    u"reddet": u"to deny: approval.deny/denied ('Reddet', 'Reddedildi.'). "
               u"tr.json ships 'reddet' only inside 'Onayla / reddet' "
               u"(proposal.approve_reject), a compound, so the bare infinitive "
               u"needs the stem declared",
    u"reddedildi": u"the evlenme (intervocalic softening) of the same stem: "
                   u"reddet -> reddedildi, where t becomes d before a vowel. "
                   u"No consonant or vowel test can see through it, so the "
                   u"inflected form is declared, as chunk B did for asıl -> "
                   u"aslı",
    u"göster": u"to show: approval.no_fields ('Gösterilebilir alan yok.'). "
               u"tr.json ships 'Gösterilen' and 'Göster:' but neither the "
               u"passive ability form nor this stem covers it",
    u"hatır": u"to remember: approval.remember ('Bu site için bu hesabı "
              u"hatırla'). The extension per-site account list has no Turkish "
              u"verb in the dictionary yet",
    u"otur": u"session: approval.locked_note ('Oturum kilitli'). tr.json ships "
             u"only the compound 'oturum açmayan' style notes; the keystore "
             u"screen needs the bare noun",
    # --- the confirm-run wording the brief pins verbatim
    u"yayımla": u"to broadcast: approval.approved must read exactly 'Onaylandı "
                u"ve yayımlandı.' because that is the confirmed probe run's "
                u"wording for 'Approved and broadcast.' The rest of the "
                u"dictionary prefers 'yayınla'; this one key keeps the probe "
                u"spelling and the difference is deliberate",
    # --- the cross-rates desk, whose nouns have no Turkish precedent
    u"sütun": u"column: the xrate desk's four column controls (add / remove / "
              u"base column). tr.json has 'sütun' in no value",
    u"rota": u"route: xrate.no_route_col and xrate.unpriced are about a PATH "
             u"through the pool graph, which is a different word from 'yol' "
             u"(the dictionary's route hint) and from 'grafik'",
    u"kote": u"quote: xrate.token_label 'Add quote token' - the finance term "
             u"Turkish trading desks already use for the quote side of a pair, "
             u"and the counterpart of this desk's 'temel sütun' (base column)",
    u"tara": u"to scan/prune: xrate.empty and xrate.show_all describe pruning "
             u"the hop-limited asset list. chunk B declared the stem for the "
             u"explorer; it is re-declared here because the harvest only sees "
             u"shipped bytes",
    # --- the shared-account (multisig) story, five strings of it
    u"bağla": u"to attach: auth.multisig_step_propose and proposal."
              u"multisig_story both say assets, barter and borrowing ATTACH to "
              u"proposals; tr.json ships 'bağ' only inside compounds "
              u"('kaynak deposu', 'bağlı olmamak')",
    u"paylaş": u"to share: auth.multisig_step_share and proposal."
               u"multisig_story hand the 1.10.N id to the co-owners. "
               u"paylaşılabilir bağlantı ships the '-ılabilir' form, which does "
               u"not extend to the plain verb",
    u"eş": u"co-: 'eş sahip' / 'eş imzalar'. Two letters, so it only ever "
           u"matches a LONGER form (declared stems may not match a bare token)",
    u"düzenle": u"to coordinate: auth.multisig_body's 'coordinated by proposal "
                u"id'. tr.json ships 'düzen' (layout) as a chunk-B declaration, "
                u"which the harvest cannot see, so the verb is declared here",
    u"seç": u"to elect: vote.ballot_intro ('Hakedişiniz tanıkları ve komiteyi "
            u"seçer') and vote.proxies_follow_... ('bir vekil atamadan önce'). "
            u"The ballot noun 'pusula' is chunk B's; the verb this batch needs "
            u"is not in the shipped dictionary",
    u"oku": u"to read: vote.proxies_follow_... ends 'read how voting works' and "
            u"becomes 'okuyun'. chunk B declared the stem without shipping it",
    u"izle": u"to follow/watch: vote.proxy_follows and "
             u"vote.proxies_follow_..., where following is a PERMISSION and not "
             u"an observation. chunk B declared the stem for the footer's "
             u"tracker; not shipped here",
    # --- plain interface vocabulary this batch needs first
    u"ters": u"reverse: pool_detail.invert / invert_label, which flip the "
             u"chart's A-per-B / B-per-A orientation. 'Ters çevir' is the "
             u"Turkish chart convention",
    u"tam": u"whole: borrow.repay_full ('Tamamını öde'), the one button that "
            u"repays a position in full rather than partially. tr.json ships "
            u"'tamamı' inside a sentence but not the stem",
    u"bağlam": u"context, compat.insecure_hint's 'güvenli bir bağlam' "
               u"(secure context) - the established Turkish term, declared "
               u"here because chunk B's declaration is not visible to the "
               u"harvest",
    u"sun": u"to serve: compat.insecure_hint ('tarayıcı WebCrypto'yu sunmaz', "
            u"'https üzerinden sunun'). tr.json ships 'sunucu' (server) as a "
            u"compound, which does not extend to the verb",
    u"son": u"last: xrate's rates are priced at their LAST swap, and "
            u"pool_detail's map legend says 'son 24 saat'. The bare temporal "
            u"adjective has to be distinguishable from 'Sonraki' (Next)",
    u"ekle": u"to add: xrate.add_btn and the 'Add quote token' label. tr.json "
             u"ships 'eklenme zamanı' / 'ekleyin' as inflections of a stem the "
             u"harvest sees only through its longer forms",
    u"çapraz": u"cross: xrate's desk crosses prices through the pool graph "
              u"('çaprazlanarak', 'Çapraz oranlar'), which is the Turkish word "
              u"the finance pages use and a different word from the dictionary's "
              u"'eşle'/çaprazlanan coin pairs",
    u"vurgula": u"to highlight: tour.away_note ('vurgulanan yeri görmek için') "
                u"points at the element the tour just pointed at, so the verb "
                u"has to be the tour's own",
    u"keşfedin": u"imperative 'explore': news.explorer_blocks_and_transactions "
                 u"is the button under the chain-explorer headline. tr.json "
                 u"ships 'Keşfet' (nav.explorer) and 'keşfedilen' nowhere, and "
                 u"this is the -in aorist of the same stem with e->i harmony, "
                 u"which a prefix test cannot see through",
    # --- the counters and window notes
    u"kırpıl": u"to truncate: market_ind.count_capped and "
               u"pool_detail.candle_capped ('pencere kırpıldı'), the note that "
               u"the candle window was cut short rather than completed",
    u"aldıktan": u"the evlenme + aorist of 'al': 'bir teklif karşılığında "
                 u"ödünç aldıktan sonra' (credit.no_borrower_deals), the "
                 u"moment deals become visible. al -> aldı -> aldıktan passes "
                 u"through a consonant softening no prefix test can follow",
    u"dolmadan": u"'before it expires': htlc.list_sub's 'süre dolmadan'. The "
                 u"stem 'dolma' is not shipped (tr.json has 'dolmuş', "
                 u"'doldu'), so the negated aorist is declared",
    # --- plain nouns the harvest only holds in a longer inflection
    u"cihaz": u"device: proposal.multisig_story's 'çok cihazlı'. tr.json ships "
              u"'cihazda' and 'cihazınızda', which do not extend to the -lı "
              u"adjective form",
    u"görül": u"to be seen: pool_detail.map_connects's 'son 24 saatte işlem "
              u"görülmüşse', the condition a map line is drawn under",
    u"çalış": u"to work/run: vote.proxies_follow_... "
              u"('oylamanın nasıl çalıştığını okuyun'). tr.json ships only "
              u"-ır / -ma shapes; chunk B declared the stem without shipping it",
    u"kip": u"mode: vote.retry_self / vote.retried_prefix name the node's proxy "
            u"MODE by name (%(mode)s is the mode string itself). tr.json ships "
            u"'kipi' only inside 'izin kipi', a compound",
    u"reddet": u"to deny: approval.deny ('Reddet'), the one button that refuses "
               u"a dApp's signature request",
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
        two letters are enough ("eş") - and they only ever match a LONGER
        form, never a bare two-letter token.
    Matching is case-insensitive because Turkish capitalises sentence starts and
    column heads ("Kabul", "Hesap") and those are the same word.
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
            # A Turkish APOSTROPHE only ever separates a proper noun or a
            # loanword stem from a case suffix - "İşlem Oluşturucu'ya",
            # "WebCrypto'yu", "BTS'den", "coin'leri", "hash'e" - and G7b has
            # already asserted the value uses the ASCII apostrophe Turkish
            # orthography requires. LATIN_TOKEN cannot span it (the apostrophe
            # is not a word character), so the head carries the whole
            # vocabulary decision and the suffix is grammar, not a word. The
            # head is checked with the SAME three pools, so an English word
            # that merely happens to sit in front of an apostrophe still falls
            # through to the English-source fallback and, failing that, to a
            # refusal.
            if APO_ASCII in token:
                head = token.split(APO_ASCII, 1)[0]
                if head and (head in LOAN
                             or turkish(head, vocab_lower, declared)):
                    continue
            if token in master_tokens:
                fallback.append("%s: %s" % (key, token))
                continue
            problems.append("G9: unaccounted token %r in %s" % (token, key))
        master = en_flat[key]
        # G10 folds case on both sides: Turkish capitalises a sentence's first
        # word, so "Kilitliyken" and "kilitliyken" are the same rule word and a
        # case-sensitive test would silently stop guarding the pair for every
        # string this batch starts with a capital. Folding widens the match, so
        # an inversion is caught either way.
        low_value = _fold(value)
        for marker, needed, inverted in COMPARISONS:
            if marker in master:
                if _fold(needed) not in low_value:
                    problems.append(
                        "G10: %s lost its rule word %r" % (key, needed)
                    )
                if _fold(inverted) in low_value:
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
    # are printed loudly and never repaired here: chunk-A and chunk-B own them,
    # and an insert-only batch that "fixed" a neighbour would be the silent
    # edit the scope refusal exists to prevent. Only `bad` - problems this
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

    print("tr chunk-C: %d planned, %d differ from en, %d intentionally identical"
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
    # ================================================= approval (20) — dApp signing
    # The extension's per-site approval surface. Sixteen of these twenty render
    # on the dual-line dialog the user reads before a signature leaves the page,
    # so every sentence keeps its full case stack: WHO holds the key, WHO is
    # asked, and what happens next.
    "approval.account": u"Hesap: ",
    "approval.approve": u"Onayla",
    # Probe run B, T10: the confirmed wording for "Approved and broadcast."
    "approval.approved": u"Onaylandı ve yayımlandı.",
    "approval.chain": u"Zincir: ",
    "approval.close": u"Kapat",
    "approval.denied": u"Reddedildi.",
    "approval.deny": u"Reddet",
    "approval.expires_in": u"Kalan süre: ",
    "approval.load_failed": u"Onay yüklenemedi.",
    "approval.loading": u"Onay yükleniyor…",
    "approval.locked_note": (
        u"Oturum kilitli — onaylamak için cüzdan parolanızı giriniz."
    ),
    "approval.no_fields": u"Gösterilebilir alan yok.",
    "approval.no_reply": u"İmzalamadan yanıt yok.",
    "approval.no_runtime": u"Eklenti çalışma zamanı eksik.",
    # Probe run B, T03: the one password label in the dictionary.
    "approval.password": u"Parola",
    "approval.remember": u"Bu site için bu hesabı hatırla",
    "approval.title": u"İmzayı onayla",
    "approval.unknown_intent": u"Onay isteği bulunamadı.",
    "approval.wallet_title": u"Bu cüzdan bir imza talebi yapıyor",

    # ================================================= unlockconfirm (5)
    # The unlock dialog every signing flow opens. Three of these five are the
    # probe run's wording verbatim (T01, T03) so the prompt reads the same
    # wherever it appears.
    "unlockconfirm.cancel": u"Geri",
    # Probe run B, T01.
    "unlockconfirm.empty_password": u"Cüzdan parolanızı giriniz.",
    "unlockconfirm.password": u"Parola",
    # EXACT reuse of common.unlock_failed — one term, one spelling.
    "unlockconfirm.unlock_failed": u"Kilit açılamadı.",
    # EXACT reuse of trollbox.unlock_post below: "Unlock & post" is ONE action
    # and must not read two ways on two dialogs.
    "unlockconfirm.unlock_post": u"Kilidi aç ve zincire yaz",

    # ============================================ *_uc_title (7) — the unlock title
    # "Unlock to sign" is the title of seven dual-line dialogs. Probe run B, T02,
    # fixed its wording; all seven print it byte-identically, because a Turkish
    # user who learns "İmzalamak için kilidi açınız" on one screen must not meet
    # a different phrase on the next.
    "barter.uc_title": u"İmzalamak için kilidi açınız",
    "borrow.uc_title": u"İmzalamak için kilidi açınız",
    "credit.uc_title": u"İmzalamak için kilidi açınız",
    "debit.uc_title": u"İmzalamak için kilidi açınız",
    "htlc.uc_title": u"İmzalamak için kilidi açınız",
    "instant.uc_title": u"İmzalamak için kilidi açınız",
    "prediction.uc_title": u"İmzalamak için kilidi açınız",

    # ================================== uc_title / unlock (trade, transfer, instant)
    # "Unlock to continue" is a different promise from "to sign" — nothing has
    # been signed yet — so it keeps chunk B's pool.uc_title spelling exactly.
    "trade.uc_title": u"Devam etmek için kilidi açın",
    "transfer.uc_title": u"Devam etmek için kilidi açın",
    # "Unlock & review" — EXACT reuse of trade.unlock_review.
    "transfer.unlock_sign": u"Kilidi aç ve incele",
    # "Unlock & sign" — same verb, same order as trade.unlock_review.
    "instant.unlock_sign": u"Kilidi aç ve imzala",

    # ========================================== transfer (4 more) — signing lines
    # The first two render inside the proposal confirmation dialog, row for row
    # beside the English master.
    "transfer.confirm_proposal_title": u"Öneriyi onayla (op %(op)s)",
    # G10: "only after approvals". The op runs AFTER the co-owners sign, never
    # before; Turkish shares every word in both directions, so the gate pins it.
    "transfer.enclosed_op_note": (
        u"Kapsanan işlem: transfer (op %(op)s) — yalnızca onaylardan sonra "
        u"gerçekleşir."
    ),
    # G10: "while locked". The proposer PAYS THE FEE, so while the wallet is
    # locked this string must name the account whose authority would be spent.
    "transfer.propose_notice_locked": (
        u"Kilitliyken öneren, varsayılan olarak %(name)s (%(id)s) olur — "
        u"kendiniz olarak işlem yapmak için kilidi açın."
    ),
    "transfer.share_needs_to_amount": (
        u"Paylaşılabilir bir bağlantı için alıcı ve tutar gerekir."
    ),

    # ============================================ borrow (6 more) — margin desk
    "borrow.adjust": u"Ayarla",
    "borrow.adjust_position_op_3": u"Pozisyonu ayarla (op %(op)s)",
    # G10: "Bids cannot be cancelled". An irreversible settlement bid written as
    # cancellable would send a user into a position they cannot leave.
    "borrow.bids_no_cancel": (
        u"Teklifler verildikten sonra iptal edilemez — ya gerçekleşirler ya da "
        u"süreleri dolar."
    ),
    "borrow.close_position": u"Pozisyonu kapat",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Marjin pozisyonları bir bitasseti teminat karşılığında ödünç alır. "
        u"Teminat eklemek veya borcu ödemek, çağrı emrinizdeki op %(op)s "
        u"(call_order_update) işlemini ayarlar."
    ),
    "borrow.open_a_new_position_op_3": u"Yeni bir pozisyon aç (op %(op)s)",
    "borrow.repay_full": u"Tamamını öde",
    "borrow.settlement_bids_op_45": u"Uzlaşma teklifleri (op %(op)s)",

    # ================================================= proposal (9) — the multisig path
    "proposal.confirm_proposal_create_op_22": (
        u"Öneri oluşturmayı onayla (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Öneri silmeyi onayla (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"Öneri sil (op %(op)s)",
    # proposal.memo is KEPT_ENGLISH: chunk A already spells this screen's own
    # memo field "Memo" twice (proposal.inner_transfer_4 "Memo (isteğe bağlı)"
    # and its error hint), and this row label sits on the same screen - see
    # KEPT_ENGLISH.
    # The shared-account story, told twice (here and auth.multisig_body). Both
    # copies carry the same three facts: one key is NOT enough, the proposal id
    # is what coordinates, and browsing stays public.
    "proposal.multisig_story": (
        u"Ortak hesap mı? Bir ortak sahip öneriyi yapar, 1.10.N kimliğini "
        u"paylaşır, kalanlar aşağıdan onaylar. Çok işlemli ya da çok cihazlı "
        u"çalışma işlem oluşturucuda devam eder."
    ),
    "proposal.open_txbuilder": u"İşlem Oluşturucu'yu aç",
    "proposal.viewing_as": (
        u"%(name)s (%(id)s) olarak görüntüleniyor — kendiniz olarak işlem "
        u"yapmak için kilidi açın."
    ),

    # ====================================================== auth (7) — multisig desk
    # G10: "proposals + co-owner approvals" — the sentence that teaches how a
    # shared account spends money must never shrink to "one key is enough".
    "auth.multisig_body": (
        u"Bu cüzdan tek bir anahtar tutar. Ortak hesaplar öneri + ortak sahip "
        u"onayları gerektirir; hepsi 1.10.N öneri kimliğiyle düzenlenir. "
        u"Gezinme herkese açıktır; parola yalnızca imzalamak için gerekir."
    ),
    # EXACT reuse of transfer.view_proposals.
    "auth.multisig_open_proposals": u"Önerileri görüntüle",
    "auth.multisig_open_txbuilder": u"İşlem Oluşturucu'yu aç",
    "auth.multisig_step_approve": (
        u"Ortak sahipler (op 23) öneri sayfasından onaylar, ya da işlem "
        u"oluşturucu üzerinden eş imzalar."
    ),
    "auth.multisig_step_propose": (
        u"İşlemi önerin (Transfer için Gönder/Öner vardır; varlıklar, takas ve "
        u"borçlanma önerilere bağlanır)."
    ),
    "auth.multisig_step_share": (
        u"1.10.N öneri kimliğini ortak sahiplerle paylaşın."
    ),
    "auth.multisig_title": u"Ortak / çok imzalı hesaplar",

    # =================================================== barter (5 more) — signing
    "barter.confirm_barter_proposal_op_22": (
        u"Takas önerisini onayla (op %(op)s)"
    ),
    "barter.propose_barter_op_22": u"Takas önerisi oluştur (op %(op)s)",
    "barter.step_build": u"Oluştur",
    "barter.step_preview": u"Önizle",
    "barter.step_propose": u"Öner",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"İki taraflı atomik takas önizlemesi. Önce önizleyin, sonra ÖNER her "
        u"iki tarafın transferlerini tek bir öneri içinde toplar (op %(op)s, "
        u"ücreti ödeyen = A Tarafı)."
    ),

    # ============================================== createworker (4) — op-34 dialogs
    "createworker.confirm_worker_op_34": u"Çalışanı onayla (op %(op)s)",
    # G10: "direct op, not by proposal" and "Preview is live" / "quotes the live
    # fee". Both facts are load-bearing: a worker is broadcast directly, and the
    # fee quoted in review is chain-priced, not an estimate.
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Bir çalışan taslağı oluşturun (op %(op)s). Önizleme canlıdır; "
        u"inceleme canlı ücreti verir, ardından İmzala ve Gönder op %(op)s "
        u"işlemini doğrudan yayınlar — çalışanlar doğrudan işlemle oluşturulur, "
        u"öneriyle değil."
    ),
    "createworker.worker_preview_op_34": u"Çalışan önizlemesi (op %(op)s)",

    # ============================================== xrate (17) — the cross-rate desk
    # Every string here feeds a PRICE. The hop counts and the safety claim are
    # pinned by G10 so a rate can never be quoted from a pool graph deeper than
    # the one the reader can trade in.
    "xrate.add_btn": u"Sütun ekle",
    "xrate.asset_col": u"Varlık",
    # G10: "cannot be removed".
    "xrate.base_pinned": u"BTS temel sütundur ve kaldırılamaz.",
    # G10: "within 3 hops".
    "xrate.empty": (
        u"Bu zincirde BTS'den 3 havuz adımı içinde havuz varlığı yok."
    ),
    # G10: "nothing is signed".
    "xrate.intro": (
        u"Her havuz varlığı, son takasındaki fiyatıyla havuz grafiği boyunca "
        u"çaprazlanarak fiyatlanır. Hiçbir şey imzalanmaz ve hiçbir şey "
        u"saklanmaz."
    ),
    "xrate.load_failed": u"Çapraz oranlar yüklenemedi: ",
    "xrate.loading": u"Havuzlar okunuyor…",
    # G10: "within 6 pool hops" — and NOT 3, which would advertise a route the
    # graph does not have.
    "xrate.no_route_col": u"%(sym)s için 6 havuz adımı içinde rota yok.",
    "xrate.refresh_btn": u"Fiyatları yenile",
    "xrate.remove_btn": u"Kaldır ",
    "xrate.retry_btn": u"Yeniden dene",
    "xrate.show_all": u"Tüm varlıkları göster",
    "xrate.status": (
        u"%(pools)s havuz · 3 havuz adımı içinde %(assets)s varlık · "
        u"%(total)s havuzun %(done)s tanesinde son takas var"
    ),
    "xrate.token_label": u"Kote tokeni ekle",
    "xrate.unknown_token": u"%(sym)s adlı bir havuz varlığı yok.",
    "xrate.unpriced": (
        u"Bu rotadaki bir bacağın henüz kayıtlı takası yok."
    ),

    # ============================================ vote (9) — the governance desk
    # G10: "published as self" / "retrying once as self" / "your stake follows
    # this account". All three describe WHO a vote counted for, and all three
    # are one word-pair away from saying the opposite.
    "vote.ballot_intro": (
        u"Hakedişiniz tanıkları ve komiteyi seçer, çalışanların bütçesini "
        u"oluşturur — aşağıdaki tüm sayılar ve paylar canlı zincir "
        u"okumalarıdır."
    ),
    "vote.confirm_witness_update_op_21": (
        u"Tanık güncellemeyi onayla (op %(op)s)"
    ),
    "vote.direct_note": (
        u"Doğrudan oylama yayınlandı (voting_account %(id)s)."
    ),
    "vote.in_sync": (
        u"Oylama listesi zincirle aynı — yayınlanacak değişiklik yok."
    ),
    "vote.proxies_follow_another_account_s_slate_re": (
        u"Vekiller başka bir hesabın oylama listesini izler — bir vekil "
        u"atamadan önce oylamanın nasıl çalıştığını okuyun."
    ),
    "vote.proxy_follows": (
        u" — hakedişiniz bu hesabı izler; aşağıdaki oylama listesi salt "
        u"okunurdur."
    ),
    "vote.retried_prefix": (
        u"Düğüm %(mode)s vekil kipini reddetti, bu yüzden oy kendi hesabı "
        u"olarak yayınlandı (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"Düğüm %(mode)s vekil kipini reddetti — bir kez kendi hesabınız olarak "
        u"yeniden deneniyor…"
    ),

    # =============================================== trollbox (8 more) — chat desk
    "trollbox.bytes_unit": u"bayt",
    "trollbox.channel_row": u"Kanal",
    "trollbox.fee": u"Ücret",
    "trollbox.language_row": u"Dil",
    "trollbox.message_row": u"Mesaj",
    "trollbox.post_review_title": u"Mesajı inceleyin",
    "trollbox.size_row": u"Boyut",
    "trollbox.unlock_post": u"Kilidi aç ve zincire yaz",

    # ================================================ htlc (3 more) — lock desk
    # G10: "or you are refunded" — the party who gets the money back when the
    # receiver never redeems. Reversed, it would tell the sender they lose the
    # funds.
    "htlc.list_sub": (
        u"Fonları bir hash'e kilitleyin — alıcı, süre dolmadan gizli ön "
        u"görüntüyle kullanır, ya da size iade edilir. Herkes okuyabilir; "
        u"parola yalnızca imzalamak için istenir."
    ),

    # ========================================= pool_detail (8) — the pool map + chart
    # G10: "A-per-B / B-per-A" keeps the two orientations in the order the
    # toggle switches between them.
    "pool_detail.candle_capped": u"pencere kırpıldı",
    "pool_detail.candle_count": (
        u"%(swaps)s takas · %(count)s × %(bucket)s mum"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s takas · %(actual)s / %(requested)s × %(bucket)s mum"
    ),
    "pool_detail.invert": u"Ters çevir",
    "pool_detail.invert_label": u"Grafik yönünü ters çevir (A/B, B/A)",
    "pool_detail.map_connects": (
        u"İki varlığı birbirine bağlayan çizgi, fonlanmış bir havuz varsa ve "
        u"son 24 saatte işlem görülmüşse çizilir."
    ),
    "pool_detail.map_connects_fallback": (
        u"İki varlığı birbirine bağlayan çizgi, fonlanmış bir havuz varsa "
        u"çizilir. Son 24 saatteki işlem etkinliği doğrulanamıyor (geçmiş "
        u"kullanılamıyor) — fonlanmış havuzlar gösteriliyor."
    ),
    "pool_detail.map_min_swaps": u"(en az %(min)s takas)",

    # ============================================ market_ind (3) — candle counter
    "market_ind.count_capped": u"pencere kırpıldı",
    "market_ind.count_note": u"%(count)s × %(bucket)s mum",
    # "%(actual)s of %(requested)s" keeps its direction as a fraction with the
    # got count over the asked count, never the reverse.
    "market_ind.count_partial": (
        u"%(actual)s / %(requested)s × %(bucket)s mum"
    ),

    # ============================================= trade (6 more) — the order desk
    "trade.tab_single": u"Tek emir",
    "trade.uc_amount": u"Tutar",
    "trade.uc_orders": u"Emirler",
    "trade.uc_price": u"Fiyat",
    "trade.uc_range": u"Fiyat aralığı",
    # EXACT reuse of debit.total_field.
    "trade.uc_total": u"Satılacak toplam",

    # ==================================================== createaccount (3) — wizard
    "createaccount.step_brainkey": u"Beyin anahtarı",
    "createaccount.step_name": u"Ad",
    "createaccount.step_register": u"Kaydet",

    # ================================================ credit (3) — the credit desk
    "credit.my_deals_borrower": u"Anlaşmalarım (ödünç alan)",
    # G10: "deals appear after you borrow".
    "credit.no_borrower_deals": (
        u"Henüz ödünç alan anlaşması yok — bir teklif karşılığında ödünç "
        u"aldıktan sonra anlaşmalar görünür."
    ),

    # ============================================== debit / ticket / misc small rows
    "debit.uc_order": u"Emir",

    # =========================================== gateway (2) — the bridge intro
    "gateway.intro_a": (
        u"Dış coin'leri gösterilen adrese gönderin. Bu sayfa hiçbir şey "
        u"göndermez. "
    ),
    # G10: "with a live fee preview".
    "gateway.intro_b": (
        u"Çekmeler, canlı ücret önizlemesiyle Transfer bölümünde tamamlanır."
    ),

    # ================================================= instant (1 more) — desk note
    # G10: "balances not checked". The preview is unsigned and unvalidated; a
    # Turkish that implied the balances had been verified would be a lie.
    "instant.preview_balances_note": (
        u"%(name)s (%(id)s) olarak önizleniyor — bakiyeler denetlenmedi. "
        u"İmzalamadan önce kendi bakiyenizi doğrulamak için kilidi açın."
    ),

    # ================================================ tour (5) — the welcome tour
    "tour.away_note": (
        u"Borsa masasında — vurgulanan yeri görmek için masayı açın."
    ),
    # G10: "password is asked only at signing" — the tour is the first thing a
    # newcomer reads, and principle #9 has to land here.
    "tour.s1_body": (
        u"Her sayfa giriş yapmadan herkese açık zincir verisini okur. Başlamak "
        u"için bir piyasa açın — parolanız yalnızca imzalamak için istenir."
    ),
    "tour.s1_title": u"Her şeyi ücretsiz gezin, yerelde imzalayın",
    "tour.s3_body": (
        u"Fiyat mumları, hacim ve derinlik, ayrıca göstergeler menüsü: SMA ve "
        u"EMA gibi üst katmanlar, RSI, MACD ve Stokastik gibi osilatörler. "
        u"Canlı görmek için borsayı açın."
    ),
    "tour.s3_title": u"Canlı fiyat grafiklerini görün",
    "tour.s4_body": (
        u"Al ve Sat panelleri deneme için her sayıyı kabul eder. Kilitli "
        u"olmayan bir cüzdanla inceleyip imzalamadan önce makinenizden hiçbir "
        u"şey çıkmaz. Denemek için borsayı açın."
    ),
    "tour.s4_title": u"Alım ve satımı deneyin",

    # ============================================== dashboard / nav / common / news
    "dashboard.tagline": (
        u"Piyasaları ücretsiz gezin — işlem yapmak için bir cüzdan oluşturun."
    ),
    "dashboard.welcome": u"Kendi anahtarlarınızla BTS işlemi yapın",
    "nav.credit": u"Kredi",
    "nav.margin": u"Marjin",
    "nav.markets": u"Piyasalar",
    "nav.pools": u"Havuzlar",
    "common.page_n": u"Sayfa %(n)s",
    # EXACT reuse of barter.unknown_asset.
    "common.unknown_asset": u"Bilinmeyen varlık.",
    "news.explorer_blocks_and_transactions": u"Zinciri keşfedin",
    "pools.selector_title": u"Havuz Seçici",

    # ============================================ txbuilder (3) — the builder's nav
    "txbuilder.badge_tpl": u"İşlem Oluşturucu (%(n)s)",
    "txbuilder.link_proposals": u"Öneriler",

    # =================================================== misc / compat / eslab
    # EXACT reuse of misc.share_needs_to_amount, which is the invoice desk's
    # copy of the same rule ("a recipient and at least one amount line").
    "eslab.hint_donors": (
        u"Pencere üzerindeki sayımlar; toplamlar ham tamsayıdır — varlık "
        u"ondalığına bölün."
    ),
    "compat.insecure_hint": (
        u"Bu adres güvenli bir bağlam değil, bu yüzden tarayıcı WebCrypto'yu "
        u"sunmaz. Tarayıcınız güncel — https veya localhost üzerinden sunun ya "
        u"da dosyayı doğrudan açın."
    ),
}

# Keys whose Turkish value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from TR. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * the two em-dash SENTINELS ("—") a column prints when a value is absent.
#     A glyph, not prose; chunk B pinned the same reasoning for the settings
#     dash;
#   * words whose CORRECT Turkish spelling IS the English bytes, because that is
#     what this dictionary already ships elsewhere: Transfer (the transfer
#     screen, nav.transfer and the TxBuilder link all say it), Airdrop,
#     Spotlight, Trollbox and Cross Rates (chunk B declared all four for the
#     menu), Limit (debit ships "Limit değişikliği"), Delta (samet ships
#     "Delta tutarı"), Coin (gateway ships "Destek coin'i"), Hash (htlc ships
#     "Hash kilidi" and "Ön görüntü hash'i"), Site, the acronyms ID and URL
#     (both pinned by tooling/check_i18n.py's IDENTIFIERS gate), and proposal's
#     own memo row - one-term-one-spelling beats dictionary-wide consistency
#     when the alternative puts two names for one field on ONE screen, and this
#     row sits beside chunk A's "Memo (isteğe bağlı)" twice;
#   * the one LOWERCASE op name, proposal.op_0 — a chain field name, printed as
#     "transfer (op 0)", and the dictionary's Turkish word for a transfer is
#     that same word;
#   * DATA placeholders a reader must recognise as samples, not prose: the
#     airdrop batch "alice,10\nbob,2.5" and the quote-currency list
#     "USD, CNY, BTC…";
#   * pure GLUE the reader must not have re-spelled mid-sentence: barter's
#     "): " (closes the "ödeyen: " prefix above it) and xrate's trailing
#     "Kaldır " / "Coin " label spaces — wait, those two ARE translated; the
#     glue kept here is only the punctuation-only "): " and the two label
#     prefixes whose word is a loanword.
KEPT_ENGLISH = {
    # ---- sentinels
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    # ---- acronyms
    "createworker.url": u"URL",
    "vesting.id": u"ID",
    "proposal.id": u"ID",
    "misc.id": u"ID",
    # ---- loanwords / brands / names
    "approval.site_prefix": u"Site: ",
    "debit.spotlight_title": u"Spotlight",
    "gateway.coin_fact": u"Coin",
    "gateway.coin_label": u"Coin ",
    "htlc.hash_field": u"Hash hex",
    "htlc.hash_label": u"Hash: ",
    "htlc.title": u"HTLC",
    "i18n.badge_chip": u"i18n",
    "instant.limit": u"Limit",
    "misc.0_transfer": u"0 = transfer",
    "nav.transfer": u"Transfer",
    "proposal.memo": u"Memo",
    "proposal.op_0": u"transfer",
    "samet.delta": u"Delta",
    "ticket.airdrop": u"Airdrop",
    "transfer.title": u"Transfer",
    "txbuilder.link_transfer": u"Transfer",
    "trollbox.title": u"Trollbox",
    "vote.url": u"URL",
    "xrate.title": u"Cross Rates",
    # ---- data samples
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
    # ---- punctuation-only glue
    "barter.paid_by_suffix": u"): ",
}


if __name__ == "__main__":
    sys.exit(main())
