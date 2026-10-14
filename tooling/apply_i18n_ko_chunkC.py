#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n ko chunk-C: fill the SIGNING surfaces — every string the reader sees
between "you clicked something irreversible" and "it was broadcast".

Scope: exactly the 37 sections that still held English after chunks A / B1 /
B2. They are the approving, proposing, quoting and broadcasting half of the
app: the extension approval dialog (approval), the multisig story (auth), every
proposal / barter / borrow / vote / worker confirmation title, the field rows
the unlock dialogs render while the password is being typed (trade, transfer,
debit, unlockconfirm), and the read-side tables that quote those same
operations (trollbox, xrate, pool_detail, tour). Nothing outside those 37 is
touched: every key listed below is checked against en, and any other key is
REFUSED here as out of scope.

The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from ko.json, or one whose English master moved, is REFUSED;
  * KO + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

This is the Korean sibling of tooling/apply_i18n_ko_chunkB2.py and keeps its
gates one for one, including the three that were INVERTED or RELAXED for Korean
there (G7, G8, G9) — inverting them silently would be the worst kind of
copy-paste bug.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                     network/theme/dash/placeholder tokens stay byte-verbatim
                     (the same list tooling/check_i18n.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master;
                     G4b data carve-out proven, not trusted: every parenthesised
                     route, ?key=value deep link and 1.2.x object id in a value
                     this batch writes must survive byte-for-byte;
  G5  untouched      every key outside this batch keeps its exact prior value,
                     the key SET is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an unclaimed key must still equal en. Filling strings is
                     not verification, so the controller's v2 provenance /
                     verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte;
  G7  ko hygiene     no value this batch writes may carry an ASCII or
                     typographic apostrophe, an ideographic space (U+3000), a
                     Cyrillic/Han/kana/other foreign letter, or an invisible
                     code point. ko.json already ships 3,731 translated strings
                     with ZERO apostrophes (it quotes with “”, the convention
                     its own explorer.unknown_tab_prefix already uses), and a
                     Cyrillic or Han letter in a Korean string is not a typo, it
                     is a different language. Hangul is what this file is FOR,
                     so it is of course allowed. This batch is the one that
                     meets the English masters full of possessives —
                     `both sides' transfers`, `another account's vote slate` —
                     and the only correct Korean rendering of each is a rewrite
                     of the clause, never an apostrophe;
  G8  dot hygiene    INVERTED from the ja batch: Korean attaches the middle
                     dot, it does not float it. A dot with a space on either
                     side is a refusal; a dot glued to its neighbours is
                     correct, as is the algebraic x·y=k notation. The sweep runs
                     file-wide; a hit OUTSIDE the owned sections is reported as
                     PRE-EXISTING and does not gate this batch, because
                     repairing a neighbour here would be exactly the silent edit
                     the scope refusal forbids;
  G9  loanwords      every Latin token a value THIS BATCH writes is declared in
                     LOAN below, or the write is refused. A Korean crypto UI
                     prints BTS, URL, ID, WebCrypto, https and localhost, the
                     `op 22` a confirmation title quotes, the
                     `call_order_update` and `voting_account` field names, and
                     the `A` / `B` pool-leg identifiers the invert aria-label
                     names — exactly as the Japanese and Chinese files print
                     them. A fake hangul spelling ("웹소켓", "미터") would be
                     worse than the loanword. Four shapes are DATA under rule 1
                     and are stripped from the PROSE before the sweep
                     (LINK_TARGET a markdown href, ROUTE_INLINE a parenthesised
                     route, DEEP_LINK a ?key=value deep link, CHAIN_ID an object
                     id) — in this batch they are the 1.10.N proposal ids; G4/G4b
                     is what makes the carve-out checked rather than trusted.

Register: the 3,731 strings ko.json already ships are POLITE and split the way
Korean splits them — “~습니다” for statements ("거부되었습니다.",
"승인 요청을 불러오는 중입니다…") and “~십시오” for instructions addressed to
the reader ("계속하려면 잠금을 해제하십시오.", "승인하려면 지갑 비밀번호를
입력하십시오.").

This batch is the one where that split is a SAFETY property, not a style one.
A bare noun in a confirmation title ("제안 삭제(op 24)") is fine; a bare noun
where the English carries a modality loses it. Every master whose sense turns on
a verb keeps its full form with the particle in place —
approval.locked_note keeps "to approve" (승인하려면), htlc.list_sub keeps
"before expiry, or you are refunded" (만료 전에 … 환불받습니다),
borrow.bids_no_cancel keeps "they execute or expire" (체결되거나 만료됩니다),
createworker.draft… keeps "broadcasts directly — not by proposal"
(바로 브로드캐스트 … 제안이 아니라 직접 작업으로 생성됩니다),
transfer.enclosed_op_note keeps "executes only after approvals"
(승인이 끝난 뒤에만 실행됩니다). A terser rendering of any of them would change
what the screen says the reader is authorising.

Labels, column heads, tab names, confirm-dialog field labels and section titles
stay bare nouns ("수량", "주문", "포지션 조정(op 3)", "풀"), which is how a table
head and a field row read in any register — including the unlock dialogs, whose
rows are field labels and must stay short enough not to reflow the dialog.

One-term-one-spelling across the dict (the load-bearing rule of the batch, and
every decision below was checked against the 3,731 shipped strings):
  * 잠금 해제 — every uc_title in the file ("Unlock to sign" →
    "서명하려면 잠금을 해제하십시오", "Unlock to continue" →
    "계속하려면 잠금을 해제하십시오") uses the verb form common.locked_sign
    already ships; the `&` buttons ship the result form ("잠금 해제 후 서명 /
    검토 / 게시"), so no third spelling exists;
  * 승인 / 거부 — proposal.approve = "승인" and
    proposal.proposals_need_approvals… = "…거부권은 작업 24를 사용합니다"
    already fixed both halves, so the extension dialog reuses them and
    Approve/Deny/Approved/Denied are one word, not two;
  * 제안 — proposals.title = "제안", so every "(op 22)" proposal title, the
    TxBuilder Proposals link and the multisig story use it;
  * 제안자 — transfer.proposer_label ships "제안자", so
    transfer.propose_notice_locked says 제안자, not 제안하는 계정;
  * viewing-as — proposal.viewing_as and instant.preview_balances_note reuse
    viewing.notice_locked's clause VERBATIM ("%(name)s (%(id)s)로 보는 중입니다
    — …"), because the reference UI shows the same "who am I acting as" notice
    in all three places and a divergent retelling would be visible side by side;
  * confirm titles — "… 확인(op N)" is the shipped shape (htlc.confirm_create =
    "HTLC 확인", vesting.confirm_vesting_create_op_32 = "베스팅 생성 확인(op
    32)"), and the op number stays byte-verbatim, never a Korean digit;
  * 환불 / 상환 — htlc.expired_note ships "발신자에게 자동으로 환불되며" and
    htlc.redeem_title ships "상환", so htlc.list_sub uses both and nothing else;
  * raw integers — eslab.hint_donors reuses eslab.hint_holders' clause ("원시
    정수입니다 — 자산 정밀도로 나누십시오") and eslab.hint_agg's opener ("기간
    내 집계이며"), the two the ES Lab page already shows beside it;
  * 24h becomes 24시간 and hops become 홉 — market.map_connects_fallback and
    pool_net.hops ("BTS까지 %(n)s홉") already wrote it that way;
  * preflight names — the xrate column is 자산 (account.asset_th), the quote
    token is 상대 토큰 (the page's QUOTE side), and the base column sentence
    says 기준 열, matching the page's 기준/상대 vocabulary;
  * share-link needs — transfer.share_needs_to_amount reuses misc.recipient =
    "수신자" and misc.amount = "금액" rather than inventing a pair.

Particles: the shipped strings already fixed the placeholder-particle problem
with the parenthesised dual forms — "%(name)s은(는)", "%(amount)s을(를)" — and
the universal ones where no form is needed ("의", "에게"). Where a bare English
noun would have forced that machinery (xrate.unknown_token, the viewing-as
notices) this batch writes the GENITIVE instead — "이름이 %(sym)s인 풀 자산이
없습니다", "%(name)s (%(id)s)로 보는 중입니다" — which is the shorter, more
idiomatic rendering and keeps the dual form off the signing screens entirely.

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md 3.5) — and no prose number is invented. The op
numbers (3, 21, 22, 23, 24, 34, 45), the hop counts (3홉 / 6홉) and the 1.10.N
proposal id are all carried across as the same values.

Word order the code pins (worth stating, because it is the one place a naive
translation inverts): the extension dialog prints `site_prefix + origin`,
`account + accountId`, `chain + chainShort` and `expires_in + seconds`, so
those four Korean fragments must end in a COLON or a blank the value is
appended to, never in a post-nominal — "만료까지 " and "계정: " are labels, not
clauses. barter.paid_by_suffix is the same shape
(`proposal_fee_due_now_paid_by_prefix + name + paid_by_suffix + asset`), which
is why it stays the ASCII `): ` — the Korean prefix already ends "지불자: " and
needs exactly that closing paren.

Glue: xrate.remove_btn keeps its trailing space, xrate.load_failed keeps its
trailing colon, and the four approval prefixes keep their trailing space,
because in each case the separator IS the content and the code appends after it.

Empty state: `—` is the shipped Korean empty-state marker (market.stat_empty),
so assets_feed.s1 and explorer_assets.s1 keep it as data, the way chunk A kept
market.stat_empty while translating the prose around it.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_ko_chunkC.py                # dry run (asserts)
  python3 tooling/apply_i18n_ko_chunkC.py --apply        # writes ko.json
  python3 tooling/apply_i18n_ko_chunkC.py --verify       # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
KO_PATH = os.path.join(BASE, "ko.json")

# The sections this batch owns — exactly the 37 that still held English after
# chunks A / B1 / B2. Anything else belongs to another chunk and is REFUSED.
SECTIONS = frozenset((
    # --- the approving / signing half -------------------------------
    "approval", "auth", "proposal", "borrow", "vote", "createworker",
    "barter", "transfer", "credit", "debit", "htlc", "prediction",
    "instant", "unlockconfirm", "trade", "ticket", "vesting", "txbuilder",
    # --- the quoting / reading half ----------------------------------
    "trollbox", "xrate", "pool_detail", "tour", "market_ind", "nav",
    "news", "dashboard", "common", "gateway", "compat", "eslab", "misc",
    # --- single-key data sections carried over verbatim ---------------
    "createaccount", "pools", "i18n", "viewing", "assets_feed",
    "explorer_assets",
))
OWNED_SECTIONS = SECTIONS

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from KO below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# None of them live in a section this batch owns (they are all in another
# chunk's settings section); they are kept in the list so a drift anywhere in
# the file is caught.
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
# G9 data carve-outs. Four shapes are DATA under rule 1 — translating or
# "declaring" one in LOAN would be the bug, not the fix — so they are removed
# from the PROSE before the loanword sweep:
#   LINK_TARGET  a markdown href           `[지갑](#/wallet)`
#   ROUTE_INLINE a parenthesised route     `소개 페이지(#/about)`
#   DEEP_LINK    a ?key=value deep link   `?dialog=N`
#   CHAIN_ID     an object id              `1.3.x`, `1.19.66`
# The link LABEL is never stripped: that is prose, and it is what this batch
# translates. G4b below is what makes the carve-out checked rather than trusted
# — LINK_HASH already covers the first shape, and ROUTE_INLINE / DEEP_LINK /
# CHAIN_ID are compared against the English master key by key.
LINK_TARGET = re.compile(r"\]\([^)]*\)")
ROUTE_INLINE = re.compile(r"\(#/[^)]*\)")
DEEP_LINK = re.compile(r"\?[A-Za-z][A-Za-z0-9]*=[A-Za-z0-9=_&#%\-]*")
# `N` joins the tail class on purpose: 1.10.N is THE proposal-id shape this
# batch quotes, and without it the carve-out silently fails to match while the
# G4b comparison stays vacuous. It was checked against every already-translated
# key in ko.json: widening the tail to accept N changes no master/value pairing.
CHAIN_ID = re.compile(r"\d+\.\d+\.[\dxN]+")
INVISIBLE = re.compile(u"[­‍⁠﻿]")
DOT_CHARS = u"·•‧･"
APO_TYPO = u"’"
APO_ASCII = u"'"
IDEO_SPACE = u"　"
# G7: a letter from a script this file must never emit. Written as explicit
# \uXXXX escapes on purpose: typing these blocks by hand is exactly how a range
# silently swallows Hangul (U+AC00..U+D7A3) and the gate then fires on every
# Korean word in the file. The four Korean blocks below are deliberately
# ABSENT — Hangul syllables, Hangul jamo, Hangul compatibility jamo and the
# jamo-extended block are the point of this batch, not contamination.
FOREIGN = re.compile(
    u"[\u0400-\u04ff"      # Cyrillic
    u"\u0500-\u052f"        # Cyrillic supplement
    u"\u0900-\u097f"        # Devanagari
    u"\u0e00-\u0e7f"        # Thai
    u"\u0e80-\u0eff"        # Lao
    u"\u1000-\u109f"        # Myanmar
    u"\u1200-\u137f"        # Ethiopic
    u"\u1400-\u167f"        # Canadian aboriginal
    u"\u1780-\u17ff"        # Khmer
    u"\u1800-\u18af"        # Mongolian
    u"\u1a00-\u1aff"        # Tibetan / Lepcha
    u"\u1e00-\u1eff"        # Latin-Indic / Thai extra
    u"\u3040-\u30ff"        # Hiragana + Katakana
    u"\u3100-\u312f"        # Bopomofo (Chinese phonetic)
    u"\u31f0-\u31ff"        # Katakana phonetic extensions
    u"\u3400-\u4dbf"        # CJK unified ideographs extension A
    u"\u4e00-\u9fff"        # CJK unified ideographs
    u"\uf900-\ufaff"        # CJK compatibility ideographs
    u"\uff66-\uff9f"        # halfwidth kana
    u"\uff00-\uffef"        # fullwidth forms
    u"\u31c0-\u31ef"        # CJK strokes
    u"\u3200-\u32ff"        # enclosed CJK letters and months
    u"]"
)
# Hangul lives at U+1100..U+11FF (jamo), U+3130..U+318F (compatibility jamo),
# U+A960..U+A97F, U+D7B0..U+D7FF and U+AC00..U+D7A3 (syllables). None of them is
# listed above, and that omission IS the exemption — a single mis-typed range
# end would swallow U+AC00..U+D7A3 and the gate would fire on every Korean word
# in the file, so the ranges stay as escapes a reader can audit.

# G9: a Latin run inside a Korean value. A token may continue through - _ . /
# so "Same-T", "docs/vanilla-ui-dialog.md" and "BTS/USD" are one decision each.
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*")
COUNT_UNIT = re.compile(r"\d+[A-Za-z]+")

# The loanwords this batch is allowed to leave in Latin (G9). Every entry is a
# word a Korean BitShares UI prints in Latin, an operation NUMBER the confirmation
# titles quote, a chain FIELD NAME the reader compares against the node output, a
# pool-leg identifier, or a platform protocol word; anything else has to be Korean.
LOAN = frozenset((
    # The core asset symbol. Every Korean BitShares screen prints it in Latin
    # (dashboard hero, xrate's base column, the market titles), and there is no
    # hangul spelling of a ticker.
    "BTS",
    # The operation marker every confirmation title quotes: "제안 생성 확인(op
    # 22)". The number is DATA the reader checks against the node's op id, so
    # the marker rides along with it — ko.json already ships it that way in
    # vesting.confirm_vesting_create_op_32 ("베스팅 생성 확인(op 32)") and
    # misc.confirm_authority_create_op_54.
    "op",
    # Chain FIELD NAMES, quoted so the reader can match the node's own output.
    # A Korean rewrite of either would be a wrong lookup, not a translation.
    "call_order_update", "voting_account",
    # The word ko.json uses for a chain object id when it appears in prose
    # (proposal.check_the_id… = "id를 확인하십시오 — 제안은 1.10.N 형태입니다.",
    # transfer.no_memo_key_suffix = "…에게는 메모 키가 없습니다."), so the
    # multisig sentences keep it. The id SHAPE itself (1.10.N) is DATA and is
    # removed by the CHAIN_ID carve-out before this sweep runs.
    "id",
    # Indicator acronyms. ko.json's charts article already keeps them all in
    # Latin ("SMA부터 Fisher와 PSAR까지") and market.ov_sma / ov_ema / ov_bb /
    # ov_psar ship as bare Latin labels; the parents 오버레이 and 오실레이터 are
    # the shipped Korean words for the two families, so only the acronyms are
    # left here. Stochastic keeps its capital S — that is how the article and
    # the indicators menu write it.
    "SMA", "EMA", "RSI", "MACD", "Stochastic",
    # The pool's two leg identifiers. pool_detail's invert aria-label names
    # them exactly as the chart code does (side A / side B), and the buttons
    # are glyphs beside them, so the letters are data.
    "A", "B",
    # Platform protocol words from compat.insecure_hint — WebCrypto is the
    # browser API being withheld, and https / localhost are the two serving
    # contexts the message offers. ko.json already prints WebCrypto, WebSocket
    # and BigInt in Latin in compat.msg.
    "WebCrypto", "https", "localhost",
))

def suspicious(value):
    """Return the offending character, or None when the value is clean.

    Korean attaches a middle dot to its neighbours (G8), so the ja rule ("a
    dot must be space-separated") is inverted here. The one clean exception is
    algebraic notation — both neighbours alphanumeric, as in "x·y=k".
    """
    hit = INVISIBLE.search(value)
    if hit:
        return hit.group(0)
    for i, ch in enumerate(value):
        if ch in DOT_CHARS:
            before = value[i - 1] if i else u" "
            after = value[i + 1] if i + 1 < len(value) else u" "
            if before.isalnum() and after.isalnum():
                continue
            if before == u" " or after == u" ":
                return ch
    return None


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
            "line count changed: %s (en %d, ko %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    # G4b: the G9 carve-outs, proven rather than trusted. Every parenthesised
    # route, every ?key=value deep link and every object id must survive byte-
    # verbatim, because they are data the reader types or compares — a Korean
    # rewrite of `(#/about)` or `1.3.x` would be a broken link and a wrong
    # lookup, while the markdown href above is only half of that story.
    for shape, rx in (("route", ROUTE_INLINE), ("deep link", DEEP_LINK),
                      ("object id", CHAIN_ID)):
        if rx.findall(master) != rx.findall(value):
            problems.append("%s changed: %s" % (shape, key))
    if not chars:
        return
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_ko_hygiene(batch, problems):
    """G7 + G9: apostrophes, foreign scripts, undeclared Latin.

    Scoped to the values THIS BATCH writes. ko.json's other sections carry
    their own Latin tokens from earlier batches; re-auditing those here would
    make this file the owner of someone else's vocabulary.
    """
    for key, value in sorted(batch.items()):
        # Interpolations are substituted data, not prose: %(name)s and {s} must
        # never count as an undeclared loanword (G1 proves they survived).
        prose = PLACEHOLDER.sub("", value)
        prose = BRACE.sub("", prose)
        # Rule-1 data, all four shapes proven byte-verbatim by G4/G4b.
        for rx in (LINK_TARGET, ROUTE_INLINE, DEEP_LINK, CHAIN_ID):
            prose = rx.sub("", prose)
        # A count keeping its English unit suffix ("24h", "0-77") is data the
        # brief requires byte-verbatim, not prose: it cannot be half-translated
        # into "24시간" without changing the number the reader compares against
        # the range control beside it.
        prose = COUNT_UNIT.sub("", prose)
        if APO_ASCII in value:
            problems.append("G7: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7: typographic apostrophe in %s" % key)
        if IDEO_SPACE in value:
            problems.append("G7: ideographic space in %s" % key)
        hit = FOREIGN.search(value)
        if hit:
            problems.append("G7: foreign script %r in %s" % (hit.group(0), key))
        for token in sorted(set(LATIN_TOKEN.findall(prose))):
            if token not in LOAN:
                problems.append("G9: undeclared Latin token %r in %s"
                                % (token, key))


def verify():
    """Structural re-proof of the shipped file against the en master."""
    ko, en = load(KO_PATH), load(EN_PATH)
    d, e = flat(ko), flat(en)
    bad = []
    # `pre` holds file-wide sweep hits in keys this batch does NOT own. They
    # are printed loudly and never repaired here: another chunk owns them, and
    # an insert-only batch that "fixed" a neighbour would be the silent edit the
    # scope refusal exists to prevent. Only `bad` — problems this batch can
    # answer for — gates the exit code.
    pre = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(d):
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            # Structure/placeholder problems are fatal wherever they sit; only
            # the character sweep is scoped (see `pre` and the `chars` flag).
            check_batch(e, key, d[key], bad, chars=key in KO)
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
            if key in KO:
                bad.append(where)
            else:
                pre.append(where)
    check_ko_hygiene(KO, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(KO) if d.get(k) == e.get(k)]
    for k in sorted(KEPT_ENGLISH):
        if d.get(k) != e.get(k) or d.get(k) != KEPT_ENGLISH[k]:
            bad.append("kept-english key drifted: %s" % k)
    by_section = {}
    for k in same + sorted(KEPT_ENGLISH):
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1
    scope_left = [
        k for k in sorted(e)
        if k.split(".")[0] in OWNED_SECTIONS and d.get(k) == e[k]
        and k not in KO and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(KO) - len(same), len(KO)))
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
    meta = ko.get("_meta", {})
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
    raw = open(KO_PATH, encoding="utf-8").read()
    ko = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(ko, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: ko.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(ko))
    before_meta = json.dumps(ko["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(KO.items()):
        if key.split(".")[0] not in OWNED_SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in ko.json: %s" % key)
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
        deep_set(ko, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(KO) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (KO and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(KO) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in OWNED_SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in ko.json: %s" % key)
            return 1
        if value != en_flat[key]:
            print("REFUSING: kept-english value is not the English string: "
                  "%s (%r vs en %r)" % (key, value, en_flat[key]))
            return 1
    uncovered = sorted(
        k for k in en_flat
        if k.split(".")[0] in OWNED_SECTIONS
        and k not in owned and before.get(k) == en_flat[k]
    )
    if uncovered:
        print("REFUSING: %d key(s) of my sections are in neither table: %s"
              % (len(uncovered), ", ".join(uncovered[:8])))
        return 1

    check_ko_hygiene(KO, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(ko)
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
    # UNCLAIMED, which is the honest state for them - and check_i18n.py
    # separately forbids claiming its IDENTIFIERS list (shell.brand is one of
    # them, which is exactly why it is KEPT_ENGLISH rather than KO). Nothing
    # else in _meta moves - filling strings is not verification, so the
    # controller's v2 provenance/verified/high_risk fields stay untouched.
    meta = ko["_meta"]
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
    added = sorted(k for k in KO
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

    print("ko chunk-C: %d planned, %d differ from en, %d intentionally "
          "identical" % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(OWNED_SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue / "
              "sentinels - deliberately NOT claimed):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run - no files written (pass --apply)")
        return 0

    with open(KO_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ko, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/ko.json")
    return 0


KO = {
    # ============================================================== approval (20)
    # The extension wrapper's approval dialog — the one screen where a wrong
    # word is a wrong PERMISSION, so every sentence keeps its full modal form.
    # Titles are bare noun phrases (a heading), the four prefixes are labels the
    # code appends a value to, and the statuses are past-tense statements.
    "approval.account": u"계정: ",
    "approval.approve": u"승인",
    "approval.approved": u"승인되어 브로드캐스트되었습니다.",
    "approval.chain": u"체인: ",
    "approval.close": u"닫기",
    "approval.denied": u"거부되었습니다.",
    "approval.deny": u"거부",
    "approval.expires_in": u"만료까지 ",
    "approval.load_failed": u"승인 요청을 불러올 수 없습니다.",
    "approval.loading": u"승인 요청을 불러오는 중입니다…",
    # The gate itself: "to approve" is the condition the whole dialog exists to
    # satisfy, so it stays a live conditional — 승인하려면 … 입력하십시오 — and
    # not the weaker "승인을 위해", which reads as a suggestion.
    "approval.locked_note": u"세션이 잠겨 있습니다 — 승인하려면 지갑 비밀번호를 입력하십시오.",
    "approval.no_fields": u"표시할 수 있는 필드가 없습니다.",
    "approval.no_reply": u"서명자로부터 응답이 없습니다.",
    "approval.no_runtime": u"확장 기능 런타임이 없습니다.",
    "approval.password": u"비밀번호",
    # A checkbox label, so a noun phrase and not an instruction.
    "approval.remember": u"이 사이트에서 이 계정을 기억",
    "approval.site_prefix": u"사이트: ",
    "approval.title": u"서명 승인",
    "approval.unknown_intent": u"승인 요청을 찾을 수 없습니다.",
    "approval.wallet_title": u"이 지갑이 서명을 요청하고 있습니다",

    # ==================================================================== auth (7)
    # Shared / multisig accounts. The three steps are instructions the reader
    # performs in order, so each is ~십시오; the body states the rules and the
    # 1.10.N proposal id stays byte-verbatim (G4b).
    "auth.multisig_body": (
        u"이 지갑은 키 하나만 보유합니다. 공유 계정은 제안과 공동 소유자 승인이 "
        u"필요하며 제안 id(1.10.N)로 조정합니다. 조회는 공개되며 비밀번호는 "
        u"서명할 때만 필요합니다."
    ),
    # Buttons, so the 하다 form the file already ships for CTAs
    # (about.cta_trade = 거래소 열기, auth.open_accounts = 계정 열기).
    "auth.multisig_open_proposals": u"제안 보기",
    "auth.multisig_open_txbuilder": u"트랜잭션 빌더 열기",
    "auth.multisig_step_approve": (
        u"공동 소유자가 제안 페이지에서 승인하거나(op 23), 트랜잭션 빌더로 공동 "
        u"서명합니다."
    ),
    "auth.multisig_step_propose": (
        u"작업을 제안하십시오 (전송에는 전송과 제안 두 가지가 있고, 자산, 물물교환, "
        u"차입은 제안으로 연결됩니다)."
    ),
    "auth.multisig_step_share": u"1.10.N 제안 id를 공동 소유자와 공유하십시오.",
    "auth.multisig_title": u"공유 / 다중서명 계정",

    # ================================================================= barter (8)
    "barter.confirm_barter_proposal_op_22": u"물물교환 제안 확인(op %(op)s)",
    "barter.propose_barter_op_22": u"물물교환 제안(op %(op)s)",
    # The three wizard step labels are a left-to-right progression (build the
    # proposal → look at it → propose it), so bare verbs, matching the two steps
    # this file already ships as nouns (barter.building_the_proposal).
    "barter.step_build": u"구성",
    "barter.step_preview": u"미리보기",
    "barter.step_propose": u"제안",
    # The atomicity sentence is the one that says WHICH legs end up in ONE
    # proposal and who pays its fee — both are named explicitly in Korean rather
    # than left to the English beside it. "Peer A" is 당사자 A, the word
    # barter.peer_a_account already ships.
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"양방향 원자적 스왑 미리보기입니다. 먼저 미리 본 뒤 제안하면 양쪽의 이체를 "
        u"하나의 제안에 포함합니다(op %(op)s, 수수료 지불자 = 당사자 A)."
    ),
    "barter.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ================================================================= borrow (9)
    "borrow.adjust": u"조정",
    "borrow.adjust_position_op_3": u"포지션 조정(op %(op)s)",
    "borrow.bids_no_cancel": (
        u"입찰은 한 번 등록하면 취소할 수 없습니다 — 체결되거나 만료됩니다."
    ),
    "borrow.close_position": u"포지션 청산",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"마진 포지션은 담보를 바탕으로 비트자산을 빌립니다. 담보를 보태거나 빚을 "
        u"갚으면 본인 콜 오더의 작업 %(op)s (call_order_update)를 조정합니다."
    ),
    "borrow.open_a_new_position_op_3": u"새 포지션 열기(op %(op)s)",
    "borrow.repay_full": u"전액 상환",
    "borrow.settlement_bids_op_45": u"정산 입찰(op %(op)s)",
    "borrow.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ================================================================ common (2)
    # common.unknown_asset reuses barter.unknown_asset's exact string — the same
    # English sentence in two desks, so one Korean sentence. common.page_n takes
    # the suffix form tour.step_of already ships ("%(current)s / %(total)s 단계")
    # rather than a space, which would not fit a narrow pager on a phone.
    "common.page_n": u"%(n)s페이지",
    "common.unknown_asset": u"알 수 없는 자산.",

    # ================================================================= compat (1)
    # The message a reader sees when their browser is modern but the page is
    # served insecurely: the diagnosis, then the reason not to panic, then the
    # two contexts that fix it. WebCrypto / https / localhost stay Latin
    # (LOAN) — compat.msg already prints WebCrypto, WebSocket and BigInt that
    # way in the very same dialog.
    "compat.insecure_hint": (
        u"이 주소는 보안 컨텍스트가 아니므로 브라우저가 WebCrypto를 제공하지 "
        u"않습니다. 브라우저는 최신입니다 — https 또는 localhost로 제공하거나 "
        u"파일을 직접 여십시오."
    ),

    # ========================================================== createaccount (3)
    # The three registration step names, so each is a bare noun: 브레인키 is
    # wallet.brainkey's shipped word, and 이름 / 등록 are createworker.name and
    # createaccount.register_account's.
    "createaccount.step_brainkey": u"브레인키",
    "createaccount.step_name": u"이름",
    "createaccount.step_register": u"등록",

    # ============================================================== createworker (4)
    "createworker.confirm_worker_op_34": u"워커 확인(op %(op)s)",
    # The sentence that says a worker is broadcast DIRECTLY, not queued behind
    # co-owner approval — the single most consequential clause on this page, so
    # the contrast ("제안이 아니라 직접 작업으로 생성됩니다") is spelled out in
    # Korean rather than left to the English reference. Sign & Send reuses
    # common.sign_send ("서명 및 전송").
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"워커를 작성하십시오(op %(op)s). 미리보기는 실시간이며 검토 단계에서 "
        u"실시간 수수료를 고지하고, 서명 및 전송하면 작업 %(op)s를 바로 "
        u"브로드캐스트합니다 — 워커는 제안이 아니라 직접 작업으로 생성됩니다."
    ),
    "createworker.worker_preview_op_34": u"워커 미리보기(op %(op)s)",

    # ================================================================== credit (3)
    "credit.my_deals_borrower": u"내 계약(차입자)",
    "credit.no_borrower_deals": (
        u"아직 차입자 계약이 없습니다 — 제안에 대해 빌리면 계약이 표시됩니다."
    ),
    "credit.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ================================================================= dashboard (2)
    "dashboard.tagline": u"시장은 무료로 둘러보십시오 — 거래하려면 지갑을 만드십시오.",
    "dashboard.welcome": u"보유한 키로 BTS를 거래하십시오",

    # =================================================================== debit (2)
    "debit.uc_order": u"주문",
    "debit.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ==================================================================== eslab (1)
    # Reuses the two clauses the ES Lab page already ships beside it: hint_agg's
    # opener ("기간 내 집계이며") and hint_holders' raw-integer warning.
    "eslab.hint_donors": (
        u"기간 내 집계이며, 합계는 원시 정수입니다 — 자산 정밀도로 나누십시오."
    ),

    # ================================================================== gateway (2)
    # intro_a keeps its trailing space: the code concatenates intro_a and
    # intro_b into ONE paragraph, and the first half ends on the sentence that
    # says this page sends nothing.
    "gateway.intro_a": (
        u"표시된 주소로 외부 코인을 보내십시오. 이 페이지는 아무것도 전송하지 "
        u"않습니다. "
    ),
    "gateway.intro_b": (
        u"출금은 실시간 수수료 미리보기와 함께 이체에서 끝납니다."
    ),

    # ===================================================================== htlc (5)
    # The redeem-or-refund clause and the "password only at signing" clause are
    # both load-bearing (what happens to your money if the receiver never
    # redeems; when the password is asked), so neither is shortened. refunds use
    # htlc.expired_note's 환불, redemption uses htlc.redeem_title's 상환, and the
    # secret is htlc.secret_label's 비밀.
    "htlc.list_sub": (
        u"자금을 해시에 잠그십시오 — 수신자가 만료 전에 비밀 값으로 상환하거나, "
        u"그러지 않으면 본인이 환불받습니다. 누구나 읽을 수 있으며 비밀번호는 "
        u"서명할 때만 요청됩니다."
    ),
    "htlc.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ================================================================== instant (3)
    # The balances-not-checked warning is a safety statement: the preview is
    # being computed for another account, so the Korean keeps "잔액은 확인하지
    # 않았습니다" before the instruction rather than after it.
    "instant.preview_balances_note": (
        u"%(name)s (%(id)s)로 미리 보는 중입니다 — 잔액은 확인하지 않았습니다. "
        u"서명 전에 본인 잔액을 확인하려면 잠금을 해제하십시오."
    ),
    "instant.uc_title": u"서명하려면 잠금을 해제하십시오",
    "instant.unlock_sign": u"잠금 해제 후 서명",

    # =============================================================== market_ind (3)
    # "actual of requested" is reordered into the natural Korean "요청 N개 중
    # M개" — the same construction account_net/pool_net already ship — rather
    # than a slash, because this line sits beside the candle range control the
    # reader is comparing it with.
    "market_ind.count_capped": u"구간 잘림",
    "market_ind.count_note": u"%(count)s × %(bucket)s 캔들",
    "market_ind.count_partial": (
        u"요청 %(requested)s개 중 %(actual)s개 × %(bucket)s 캔들"
    ),

    # ===================================================================== nav (4)
    # The burger's compact one-word entries. 시장 / 풀 match the page names the
    # rest of the dict already ships (seo.title_markets, txbuilder.link_pools),
    # 마진 matches trade.borrow_margin, and 신용 matches account_net.class_credit.
    "nav.credit": u"신용",
    "nav.margin": u"마진",
    "nav.markets": u"시장",
    "nav.pools": u"풀",

    # ==================================================================== news (1)
    "news.explorer_blocks_and_transactions": u"체인 탐색",

    # ============================================================== pool_detail (8)
    "pool_detail.candle_capped": u"구간 잘림",
    # The middle dot is GLUED (G8): Korean attaches it. The swap count keeps
    # 건 and the candles keep 캔들, the word market_ind.candle_count ships.
    "pool_detail.candle_count": u"스왑 %(swaps)s건·캔들 %(count)s × %(bucket)s",
    "pool_detail.candle_count_partial": (
        u"스왑 %(swaps)s건·요청 %(requested)s개 중 %(actual)s개 × %(bucket)s 캔들"
    ),
    "pool_detail.invert": u"반전",
    # The aria-label names the two orientations the toggle flips between; A and
    # B are the pool's own leg identifiers and ride along in Latin (LOAN), the
    # same way the English does, so the Korean keeps the master's token order.
    "pool_detail.invert_label": u"차트 방향 반전(A당B / B당A)",
    # Reused VERBATIM from market.map_connects_fallback, which translates the
    # identical opening clause — two renderings of one sentence, one wording.
    "pool_detail.map_connects": (
        u"자금이 예치된 풀이 있고 최근 24시간 동안 거래가 있었으면 두 자산을 "
        u"선으로 연결합니다."
    ),
    "pool_detail.map_connects_fallback": (
        u"자금이 예치된 풀이 있으면 두 자산을 선으로 연결합니다. 24시간 거래 "
        u"활동은 확인되지 않았습니다(내역 사용 불가) — 자금이 예치된 풀을 "
        u"표시합니다."
    ),
    "pool_detail.map_min_swaps": u"(최소 스왑 %(min)s회)",

    # ==================================================================== pools (1)
    "pools.selector_title": u"풀 선택기",

    # =============================================================== prediction (1)
    "prediction.uc_title": u"서명하려면 잠금을 해제하십시오",

    # ================================================================= proposal (7)
    "proposal.confirm_proposal_create_op_22": u"제안 생성 확인(op %(op)s)",
    "proposal.confirm_proposal_delete_op_24": u"제안 삭제 확인(op %(op)s)",
    "proposal.delete_proposal_op_24": u"제안 삭제(op %(op)s)",
    # Reuses viewing.notice_locked's clause word for word — the reference UI
    # shows the same "acting as" notice on all three pages that carry it, and a
    # divergent retelling would be visible side by side.
    "proposal.multisig_story": (
        u"공유 계정입니까? 한 공동 소유자가 제안하고 1.10.N id를 공유하면 "
        u"나머지가 아래에서 승인합니다. 여러 작업이나 여러 기기에서 하는 일은 "
        u"트랜잭션 빌더에서 계속됩니다."
    ),
    "proposal.open_txbuilder": u"트랜잭션 빌더 열기",
    "proposal.viewing_as": (
        u"%(name)s (%(id)s)로 보는 중입니다 — 본인으로 작업하려면 잠금을 "
        u"해제하십시오."
    ),

    # ==================================================================== tour (7)
    "tour.away_note": u"거래소 데스크에 있습니다 — 열면 이 부분이 표시됩니다.",
    "tour.s1_body": (
        u"모든 페이지는 로그인 없이 공개 체인 데이터를 읽습니다. 시장을 열어 "
        u"시작하십시오 — 비밀번호는 서명할 때만 요청됩니다."
    ),
    "tour.s1_title": u"전체를 무료로 둘러보고 로컬에서 서명하십시오",
    "tour.s3_body": (
        u"가격 캔들, 거래량, 깊이와 지표 메뉴를 확인하십시오: SMA와 EMA 같은 "
        u"오버레이, RSI와 MACD, Stochastic 같은 오실레이터. 거래소를 열어 "
        u"실시간으로 보십시오."
    ),
    "tour.s3_title": u"실시간 가격 차트를 보십시오",
    # "Nothing leaves your machine until you review and sign with an unlocked
    # wallet" is the promise the practice mode makes, so the two conditions
    # (review + unlocked signature) and the timing (until then) all survive.
    "tour.s4_body": (
        u"매수·매도 패널은 연습을 위해 어떤 숫자든 받습니다. 잠금을 해제한 지갑으로 "
        u"검토하고 서명하기 전까지는 이 기기에서 아무것도 나가지 않습니다. "
        u"거래소를 열어 직접 해 보십시오."
    ),
    "tour.s4_title": u"매수와 매도를 연습하십시오",

    # =================================================================== trade (7)
    # The unlock dialog's rows. Every one is a FIELD LABEL, so all seven stay
    # bare nouns — a polite verb here would reflow the dialog the reader is
    # typing their password into. 수량 / 가격 / 주문 are the row labels
    # trade.row_amount / row_price and account.order_th already ship.
    "trade.tab_single": u"단일",
    "trade.uc_amount": u"수량",
    "trade.uc_orders": u"주문",
    "trade.uc_price": u"가격",
    "trade.uc_range": u"가격 범위",
    "trade.uc_title": u"계속하려면 잠금을 해제하십시오",
    "trade.uc_total": u"매도 총수량",

    # ================================================================ transfer (6)
    "transfer.confirm_proposal_title": u"제안 확인(op %(op)s)",
    # The clause that says the enclosed transfer does NOT execute on signature
    # but only after the approvals land — shortened to "승인 후 실행" it would
    # sound like signing alone triggers it, which is the expensive misreading.
    "transfer.enclosed_op_note": (
        u"포함된 작업: 전송(op %(op)s) — 승인이 끝난 뒤에만 실행됩니다."
    ),
    "transfer.propose_notice_locked": (
        u"잠겨 있는 동안 제안자는 %(name)s (%(id)s)로 기본 설정됩니다 — 본인으로 "
        u"작업하려면 잠금을 해제하십시오."
    ),
    "transfer.share_needs_to_amount": u"공유 가능한 링크에는 수신자와 금액이 필요합니다.",
    "transfer.uc_title": u"계속하려면 잠금을 해제하십시오",
    "transfer.unlock_sign": u"잠금 해제 후 검토",

    # ================================================================ trollbox (8)
    "trollbox.bytes_unit": u"바이트",
    "trollbox.channel_row": u"채널",
    "trollbox.fee": u"수수료",
    "trollbox.language_row": u"언어",
    "trollbox.message_row": u"메시지",
    "trollbox.post_review_title": u"메시지 검토",
    "trollbox.size_row": u"크기",
    "trollbox.unlock_post": u"잠금 해제 후 게시",

    # ================================================================= txbuilder (2)
    "txbuilder.link_proposals": u"제안",

    # =========================================================== unlockconfirm (5)
    # The modal every irreversible flow routes through: enter the password, or
    # go back. Both buttons are results, so the result form the rest of the file
    # uses ("잠금 해제 후 …") applies to the two that do it.
    "unlockconfirm.cancel": u"뒤로",
    "unlockconfirm.empty_password": u"지갑 비밀번호를 입력하십시오.",
    "unlockconfirm.password": u"비밀번호",
    "unlockconfirm.unlock_failed": u"잠금 해제에 실패했습니다.",
    "unlockconfirm.unlock_post": u"잠금 해제 후 게시",

    # ==================================================================== vote (9)
    "vote.ballot_intro": (
        u"본인의 지분으로 증인과 위원회를 선출하고 워커에 자금을 보냅니다 — 아래의 "
        u"모든 수치와 지분은 체인에서 실시간으로 읽은 값입니다."
    ),
    "vote.confirm_witness_update_op_21": u"증인 업데이트 확인(op %(op)s)",
    "vote.direct_note": u"직접 투표로 발행했습니다(voting_account %(id)s).",
    "vote.in_sync": u"투표 슬레이트가 체인과 일치합니다 — 발행할 변경 사항이 없습니다.",
    "vote.proxies_follow_another_account_s_slate_re": (
        u"프록시는 다른 계정의 투표 슬레이트를 따릅니다 — 설정하기 전에 투표가 "
        u"동작하는 방식을 읽으십시오."
    ),
    # A fragment the caller appends after an account name, so it opens with the
    # master's own space + dash and never becomes a clause of its own. The
    # "read-only" half is a permission limit, so it is stated, not implied.
    "vote.proxy_follows": (
        u" — 본인의 지분은 이 계정을 따릅니다. 아래 투표 슬레이트는 읽기 전용입니다."
    ),
    "vote.retried_prefix": (
        u"노드가 프록시 모드 %(mode)s를 거부했으므로 본인으로 투표해 발행했습니다"
        u"(voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"노드가 %(mode)s 프록시 모드를 거부했습니다 — 본인으로 한 번 더 "
        u"시도하는 중입니다…"
    ),

    # =================================================================== xrate (18)
    # The whole Cross Rates page, which no earlier chunk owned. 교차 환율 is
    # menu.p_xrates / seo.title_xrates's word for this page, 자산 is
    # account.asset_th's, and the base/quote pair is 기준/상대 — the vocabulary
    # xrate_asset_col and the market picker already use.
    "xrate.add_btn": u"열 추가",
    "xrate.asset_col": u"자산",
    "xrate.base_pinned": u"BTS는 기준 열이므로 제거할 수 없습니다.",
    "xrate.empty": u"이 체인에서 BTS로부터 3홉 이내에 있는 풀 자산이 없습니다.",
    "xrate.intro": (
        u"모든 풀 자산을 마지막 스왑 가격으로 매기고 풀 그래프를 따라 교차합니다. "
        u"서명되는 것도, 저장되는 것도 없습니다."
    ),
    # Trailing colon + space: the code appends the error after it.
    "xrate.load_failed": u"교차 환율을 불러올 수 없습니다: ",
    "xrate.loading": u"풀을 읽는 중입니다…",
    "xrate.no_route_col": u"풀 6홉 이내에서 %(sym)s로 가는 경로가 없습니다.",
    "xrate.refresh_btn": u"가격 새로고침",
    # Trailing space: the code appends the asset symbol after it.
    "xrate.remove_btn": u"제거 ",
    "xrate.retry_btn": u"다시 시도",
    "xrate.show_all": u"모든 자산 표시",
    # The middle dots are GLUED (G8), and the clause order follows the pool_net
    # status lines this file already ships (풀 %(n)s개·자산 %(m)s개).
    "xrate.status": (
        u"풀 %(pools)s개·3홉 이내 자산 %(assets)s개·풀 %(total)s개 중 "
        u"%(done)s개에 마지막 스왑 기록 있음"
    ),
    "xrate.title": u"교차 환율",
    "xrate.token_label": u"상대 토큰 추가",
    # The GENITIVE rather than %(sym)s(이)라는: shorter, and it keeps the
    # dual particle form off a page the reader is scanning for errors.
    "xrate.unknown_token": u"이름이 %(sym)s인 풀 자산이 없습니다.",
    "xrate.unpriced": u"이 경로의 구간 하나에 아직 기록된 스왑이 없습니다.",
}

# Keys whose Korean value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from KO. Each one is asserted
# to still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * brands, the badge the app calls itself, and the i18n chip label
#     (txbuilder.badge_tpl, i18n.badge_chip): a product name has no hangul
#     spelling, and ko.json already prints TxBuilder untranslated in
#     txbuilder.title's siblings and added_title;
#   * HTLC (htlc.title): the loanword chunk B1 keeps in the sitemap and
#     htlc.back_link ("HTLC로 돌아가기") already ships everywhere;
#   * Preimage (htlc.preimage_label / preimage_ph): ko.json's whole HTLC desk
#     keeps it in Latin — hash_row ("Preimage 해시"), size_row ("Preimage 크기"),
#     and the instruction copy ("잠긴 해시와 대조할 preimage를 입력하십시오.") —
#     so translating this one row label would be the odd one out on the page;
#   * ID (proposal.id, ticket.id, vesting.id): pool.id_col and explorer.id_row
#     already ship the shipped Korean "ID", and a Korean rewrite of a column
#     header that names the chain's own object id is a wrong lookup;
#   * URL (createworker.url, vote.url): createworker.proposal_url ships
#     "제안 URL " and vote.enter_a_url ships "URL을 입력하십시오." — the
#     abbreviation itself is the loanword in both;
#   * the input PLACEHOLDERS that are example DATA the reader edits rather than
#     prose: the invoice line format (misc.invoice_lines_placeholder), the
#     airdrop recipient format (ticket.airdrop_example_ph), the account-name
#     hint (viewing.dialog_placeholder) and the xrate token examples
#     (xrate.token_placeholder). A hangul "예: 커피|1.5" here would show the
#     reader a format their chain data does not use;
#   * barter.paid_by_suffix: the ASCII "): " that closes a parenthesis the
#     ALREADY-KOREAN prefix barter.proposal_fee_due_now_paid_by_prefix opened
#     ("제안 수수료(지금 지불, 지불자: ") — the code splices name and asset
#     around it, and the paren IS the content;
#   * the `—` empty-state marker (assets_feed.s1, explorer_assets.s1), the same
#     sentinel market.stat_empty and market.stat_empty already ship.
KEPT_ENGLISH = {
    # ---- data / brand / sentinel
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    "barter.paid_by_suffix": u"): ",
    "createworker.url": u"URL",
    "htlc.preimage_label": u"Preimage",
    "htlc.preimage_ph": u"preimage",
    "htlc.title": u"HTLC",
    "i18n.badge_chip": u"i18n",
    "misc.id": u"ID",
    "misc.invoice_lines_placeholder": u"coffee|1.5\ncake|2",
    "proposal.id": u"ID",
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "ticket.id": u"ID",
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "viewing.dialog_placeholder": u"account-name",
    "vesting.id": u"ID",
    "vote.url": u"URL",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
}

if __name__ == "__main__":
    sys.exit(main())