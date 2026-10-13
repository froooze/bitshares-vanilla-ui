#!/usr/bin/env python3
"""i18n de chunk-B: fill every remaining `de` section of vanilla/locales/de.json
that chunk-A did not own (account, account_net, settings, market, market_net,
asset are chunk-A's and are REFUSED here as out of scope).

Scope: ONLY the sections listed in SECTIONS. Other agents are filling the rest
of the untranslated de keys concurrently, so this script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from de.json, or one whose English master moved, is REFUSED.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route / asset symbol
                     as a WHOLE stay byte-verbatim;
  G3  pinned keys    shell.brand, shell.footer_brand, shell.footer_brand_vanilla
                     plus every settings.network_*/custom_placeholder/pending/
                     dash/theme_* id stays byte-verbatim;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master — so
                     the multi-line help articles (Markdown bodies with # headings
                     and [label](#/hash) links) keep their shape, only the prose
                     and the link LABELS are German;
  G5  untouched      every key outside this batch keeps its exact prior value,
                     the key SET is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an untranslated key must still equal en. Filling strings is
                     not verification, so provenance/verified/high_risk (added by
                     the controller's v2 migration) are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Register: formal "Sie", matching the voice already shipped in de.json (see
account.s5, settings.discover_none, misc.viewing_as "entsperren Sie, um als Sie
selbst zu handeln"). Vocabulary is reused verbatim from de.json wherever that
dictionary has already settled a word: Wallet, Asset, Order, Ops, Fills, Saldo/
Guthaben, Gebühr, Vorschlag/Vorschläge, Zeuge, Komitee, Worker, Proxy, Brainkey,
Memo, SmartCoin, Pool, Swap, Stake, Ticket, Vesting, Lastschrift,
Kreditangebot, Deal, Sicherheiten, Schuld, Authority, HTLC, Feed, Settlement,
Chain, Knoten, Explorer, Dashboard, Transfer. Nothing is invented where a
German crypto UI keeps the English word (DEX, HTLC, BitShares, BTS, API, Memo,
Swap, Pool, Wallet, Dashboard, Explorer, Spotlight, Trollbox, Airdrop, Barter,
Live, House, PnL) — the run prints every value that stays identical to en, so
a reviewer can check the list instead of guessing.

High-risk keys (approval, proposal, trade, barter, vesting, vote, transfer,
credit, borrow) render DUAL-LINE inside signing dialogs with the English
reference beside them, so their wording is deliberately plain and literal: an
amount, a destination, an irreversible action or a permission is named the same
way the English names it, never softened.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_de_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_de_chunkB.py --apply         # writes de.json
  python3 tooling/apply_i18n_de_chunkB.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
DE_PATH = os.path.join(BASE, "de.json")

SECTIONS = (
    "about", "approval", "asset_ops", "assets", "assets_feed", "auth", "barter",
    "borrow", "common", "compat", "confirm", "createaccount", "createworker",
    "credit", "dashboard", "debit", "eslab", "explorer", "explorer_assets",
    "explorer_blocks", "gateway", "help", "htlc", "i18n", "instant",
    "market_book", "market_ind", "market_orders", "menu", "misc", "nav", "news",
    "notify", "pool", "pool_detail", "pool_net", "pools", "prediction",
    "proposal", "proposals_ticket", "referrals", "samet", "seo", "shell",
    "splash", "swap", "ticket", "tickets", "tour", "trade", "transfer",
    "trollbox", "txbuilder", "unlockconfirm", "vesting", "vote", "wallet",
    "xrate",
)

# Keys whose value is a brand / persisted id, not prose (rule 1). They are
# deliberately ABSENT from DE below so they keep the English bytes, and the
# verify pass re-asserts every one of them after the write.
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
# Punctuation-smuggling characters that must never appear in a translated value
# (a stray U+00B7 once shipped inside a word in the es batch). The middot and
# its lookalikes are legitimate ONLY as the " · " separator en.json uses, so
# they are checked by context rather than banned outright.
INVISIBLE = re.compile(u"[­‌‍⁠﻿]")
DOT_CHARS = u"·•‧･"


def suspicious(value):
    """Return the offending character, or None when the value is clean."""
    hit = INVISIBLE.search(value)
    if hit:
        return hit.group(0)
    for i, ch in enumerate(value):
        if ch in DOT_CHARS:
            before = value[i - 1] if i else u" "
            after = value[i + 1] if i + 1 < len(value) else u" "
            if not (before == u" " and after == u" "):
                return ch
    return None


EM = u"—"

# Multi-line Markdown bodies are written as line lists joined with "\n" so the
# line count (G4) is structural, not a count someone has to keep by hand.
def md(*lines):
    return "\n".join(lines)


DE = {
    # ---------------------------------------------------------------- about
    # The section name is shared with about.dlg_heading, so the help article
    # quotes the same German phrase the About page renders.
    "about.dlg_bad_link": (
        u"Ungültige Dialognummer. Gültiger Bereich: 1–%(total)s."
    ),
    "about.dlg_heading": u"Vollständiges Dialog-Archiv",
    "about.dlg_heading_c": u"Vollständiges Dialog-Archiv (%(total)s)",
    "about.dlg_no_match": (
        u"Keine passenden Dialoge. Löschen Sie die Suche, um alle zu sehen."
    ),
    "about.dlg_no_reply": (
        u"Keine Antwort aufgezeichnet — die nächste Eingabe folgte unmittelbar."
    ),
    "about.dlg_noscript": (
        u"Dieses Archiv benötigt JavaScript; derselbe Text steht im "
        u"Quell-Repository unter docs/vanilla-ui-dialog.md."
    ),
    "about.dlg_search_clear": u"Leeren",
    "about.dlg_search_ph": u"Dialoge filtern…",
    "about.dlg_showing": u"Anzeige",
    "about.dlg_showing_c": u"Anzeige %(shown)s / %(total)s",
    "about.dlg_unavailable": u"Build-Dialog-Archiv nicht verfügbar.",
    "about.hero_lede": (
        u"Eine Wallet für die BitShares-Blockchain — Märkte, Konten, Governance "
        u"und Erkunden — als einfache Web-Dateien. Kein Framework, kein "
        u"Installateur, kein Konto bei uns. Ihre Schlüssel verlassen diesen "
        u"Browser nie."
    ),
    "about.making_body": (
        u"Folgt die ursprüngliche Baugeschichte: jede Eingabe, die diese Wallet "
        u"geschaffen hat, von „bitshares-ui erwerben“ am 26. September 2026 bis "
        u"zur Issue-1-Korrektur am 3. Oktober, mit den Antworten der "
        u"Erbauer — unverändert erhalten. Sie hält die Entscheidungen fest, auf "
        u"denen diese Wallet steht: der Abschied von einem weiteren "
        u"React-Uplift nach Issue #3583 und seiner Tausend-Stunden-Falle, damit "
        u"diese Wallet von nichts mit Release-Zyklus abhängt; jede Transaktion "
        u"lokal signieren wie die alte Wallet, statt sie auszulagern; drei "
        u"Themes mit dem klassischen Look als Standard; Zahlen in "
        u"menschlichen Einheiten, nie rohe Chain-Ganzzahlen; Phone-First-Layouts "
        u"ab dem ersten Slice; und Gebühren aus der Live-Chain gelesen, nie "
        u"geschätzt. Lesen Sie es als Geschichte: so wurde die Wallet gebaut."
    ),
    "about.making_title": u"Die Entstehung dieser Wallet",
    "about.s2_title": u"Auf dem echten Orderbuch handeln",
    "about.s3_body": (
        u"Die Wallet, die sie ersetzt, starb unter hundert veralteten Paketen "
        u"und einer Toolchain, die niemand reproduzieren kann. Gebaut, um "
        u"Abhängigkeiten mit Release-Zyklus zu vermeiden: kein Framework, kein "
        u"Paketmanager, kein Build-Schritt — das Kleinste, das in einem Browser "
        u"auch in zehn Jahren noch läuft."
    ),
    "about.s3_title": u"Läuft jahrelang ohne Updates",
    "about.s4_body": (
        u"Zurückkehrende Nutzer fühlen sich sofort zu Hause — dieselben "
        u"Seiten, Bedienfelder und Wörter wie in der klassischen Wallet —, "
        u"während Salden, Bücher und Verbindungsstatus live an Ort und Stelle "
        u"aktualisiert werden. Verzeihende Suche über Märkte, Konten und "
        u"Assets, drei Themes und Layouts, die vom 360-px-Handy bis zum "
        u"4K-Trading-Desk funktionieren."
    ),
    "about.s4_title": u"Dieselben Seiten, Live-Updates",
    "about.s5_body": (
        u"Die Chain spricht Ganzzahlen; Sie sehen sie nie. Jeder Betrag steht an "
        u"den Dezimalstellen seines Assets, jeder Prozentwert am wahren Wert, "
        u"und jede Gebühr wird vor dem Signieren aus der Live-Chain gelesen."
    ),

    # ---------------------------------------------------------------- approval
    # Multi-sig prompt inside the extension's approval window: plain and
    # literal, because the English reference sits directly beside the German.
    "approval.account": u"Konto: ",
    "approval.approve": u"Genehmigen",
    "approval.approved": u"Genehmigt und gesendet.",
    "approval.chain": u"Chain: ",
    "approval.close": u"Schließen",
    "approval.denied": u"Abgelehnt.",
    "approval.deny": u"Ablehnen",
    "approval.expires_in": u"Läuft ab in ",
    "approval.load_failed": u"Die Genehmigung konnte nicht geladen werden.",
    "approval.loading": u"Genehmigung wird geladen…",
    "approval.locked_note": (
        u"Die Sitzung ist gesperrt — geben Sie Ihr Wallet-Passwort ein, um zu "
        u"genehmigen."
    ),
    "approval.no_fields": u"Keine anzeigbaren Felder.",
    "approval.no_reply": u"Keine Antwort vom Signierer.",
    "approval.no_runtime": u"Erweiterungs-Laufzeit fehlt.",
    "approval.password": u"Passwort",
    "approval.remember": u"Dieses Konto für diese Website merken",
    "approval.site_prefix": u"Website: ",
    "approval.title": u"Signatur genehmigen",
    "approval.unknown_intent": u"Keine Genehmigungsanfrage gefunden.",
    "approval.wallet_title": u"Diese Wallet fordert eine Signatur an",

    # ------------------------------------------------------------ small labels
    "asset_ops.title": u"Asset",
    "assets.title": u"Assets",
    # Bare em dash: the row has no content (nothing to translate).
    "assets_feed.s1": EM,

    # ---------------------------------------------------------------- auth
    "auth.multisig_body": (
        u"Diese Wallet hält einen Schlüssel. Gemeinsame Konten brauchen "
        u"Vorschläge und Genehmigungen der Miteigentümer, koordiniert über die "
        u"Vorschlags-ID (1.10.N). Stöbern ist öffentlich; nur das Signieren "
        u"verlangt das Passwort."
    ),
    "auth.multisig_open_proposals": u"Vorschläge ansehen",
    "auth.multisig_open_txbuilder": u"Transaktions-Builder öffnen",
    "auth.multisig_step_approve": (
        u"Miteigentümer genehmigen (op 23) auf der Vorschlagsseite oder "
        u"signieren mit über den Transaktions-Builder."
    ),
    "auth.multisig_step_propose": (
        u"Die Operation vorschlagen (Transfer hat Senden/Vorschlagen; Assets, "
        u"Barter und Leihen verweisen auf Vorschläge)."
    ),
    "auth.multisig_step_share": (
        u"Teilen Sie die 1.10.N-Vorschlags-ID mit den Miteigentümern."
    ),
    "auth.multisig_title": u"Gemeinsame / Multisignatur-Konten",

    # ---------------------------------------------------------------- barter
    "barter.barter": u"Barter",
    "barter.confirm_barter_proposal_op_22": (
        u"Barter-Vorschlag bestätigen (Op %(op)s)"
    ),
    # Suffix of a payer row ("… (Gebührenzahler: name): ") — pure glue.
    "barter.paid_by_suffix": u"): ",
    "barter.propose_barter_op_22": u"Barter vorschlagen (Op %(op)s)",
    "barter.step_build": u"Erstellen",
    "barter.step_preview": u"Vorschau",
    "barter.step_propose": u"Vorschlagen",
    "barter.title": u"Barter",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"Zweiseitige atomare Swap-Vorschau. Zeigen Sie zuerst die Vorschau; "
        u"VORSCHLAGEN schließt dann die Transfers beider Seiten in einen "
        u"Vorschlag ein (Op %(op)s, Gebührenzahler = Peer A)."
    ),
    "barter.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- borrow
    "borrow.adjust": u"Anpassen",
    "borrow.adjust_position_op_3": u"Position anpassen (Op %(op)s)",
    "borrow.bids_no_cancel": (
        u"Gebote lassen sich nach dem Platzieren nicht stornieren — sie werden "
        u"ausgeführt oder laufen ab."
    ),
    "borrow.close_position": u"Position schließen",
    "borrow.hdr_order": u"Order",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Margin-Positionen leihen ein Bitasset gegen Sicherheiten. Sicherheiten "
        u"aufstocken oder Schulden tilgen passt Op %(op)s (call_order_update) "
        u"an Ihrer Call-Order an."
    ),
    "borrow.open_a_new_position_op_3": u"Neue Position eröffnen (Op %(op)s)",
    "borrow.order": u"Order",
    "borrow.position": u"Position ",
    "borrow.repay_full": u"Vollständig zurückzahlen",
    "borrow.settlement_bids_op_45": u"Settlement-Gebote (Op %(op)s)",
    "borrow.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- common
    "common.page_n": u"Seite %(n)s",
    "common.unknown_asset": u"Unbekanntes Asset.",

    # ---------------------------------------------------------------- compat
    "compat.insecure_hint": (
        u"Diese Adresse ist kein sicherer Kontext, deshalb stellt der Browser "
        u"WebCrypto nicht bereit. Der Browser ist aktuell — liefern Sie über "
        u"https oder localhost aus oder öffnen Sie die Datei direkt."
    ),

    # ---------------------------------------------------------------- confirm
    "confirm.memo": u"Memo",

    # --------------------------------------------------------- createaccount
    "createaccount.step_brainkey": u"Brainkey",
    "createaccount.step_name": u"Name",
    "createaccount.step_register": u"Registrieren",

    # --------------------------------------------------------- createworker
    "createworker.confirm_worker_op_34": u"Worker bestätigen (Op %(op)s)",
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Entwerfen Sie einen Worker (Op %(op)s). Die Vorschau ist live; die "
        u"Prüfung nennt die Live-Gebühr, dann sendet Signieren & Senden Op "
        u"%(op)s direkt — Worker entstehen durch eine direkte Op, nicht durch "
        u"einen Vorschlag."
    ),
    "createworker.name": u"Name",
    "createworker.url": u"URL",
    "createworker.worker_preview_op_34": u"Worker-Vorschau (Op %(op)s)",

    # ---------------------------------------------------------------- credit
    "credit.asset": u"Asset",
    "credit.deal": u"Deal",
    "credit.deal_2": u"Deal ",
    "credit.delta": u"Delta",
    "credit.my_deals_borrower": u"Meine Deals (Kreditnehmer)",
    "credit.no_borrower_deals": (
        u"Noch keine Deals als Kreditnehmer — Deals erscheinen, sobald Sie "
        u"gegen ein Angebot leihen."
    ),
    "credit.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- dashboard
    "dashboard.tagline": (
        u"Märkte kostenlos durchsuchen — erstellen Sie eine Wallet, um zu "
        u"handeln."
    ),
    "dashboard.welcome": u"BTS mit Schlüsseln handeln, die Sie halten",

    # ---------------------------------------------------------------- debit
    "debit.spotlight_title": u"Spotlight",
    "debit.start_row": u"Start",
    "debit.uc_order": u"Order",
    "debit.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- eslab
    "eslab.hint_donors": (
        u"Zählungen über das Fenster; Summen sind rohe Ganzzahlen — durch die "
        u"Asset-Präzision teilen."
    ),
    "eslab.raw_index": u"Index",

    # ---------------------------------------------------------------- explorer
    "explorer.asset_prefix": u"Asset ",
    "explorer.asset_title": u"Asset",
    "explorer.assets_mode_all": u"Alle",
    # "SmartCoins" is the shipped de spelling (explorer.no_smartcoins).
    "explorer.assets_mode_market": u"SmartCoins",
    "explorer.assets_mode_prediction": u"Prognose",
    "explorer.assets_mode_user": u"Vom Nutzer emittiert",
    "explorer.assets_of": u"von",
    "explorer.assets_showing": u"Anzeige",
    "explorer.back_to_block_prefix": u"← Block #",
    "explorer.block_prefix": u"Block #",
    "explorer.block_title": u"Block",
    "explorer.confirm_asset": u"Asset",
    "explorer.feed_badge_live": u"LIVE",
    "explorer.feed_cer_premium": (
        u"Premium des Core-Wechselkurses (CER) (Schätzung nach der Regel des "
        u"Herausgebers)"
    ),
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.feeds_of": u"von",
    "explorer.feeds_scanned_suffix": u"gescannt (erste 100 Assets)",
    "explorer.feeds_showing": u"Anzeige",
    "explorer.head_prefix": u"Head #",
    "explorer.id_row": u"ID",
    "explorer.info_h": u"INFO",
    "explorer.live_prefix": u"Live • Block #",
    # de.json quotes user-supplied strings with „…“, never with «».
    "explorer.no_assets_match": u"Keine Assets passen zu „%(q)s“.",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_label": u"Operation",
    "explorer.op_prefix": u"Op ",
    "explorer.pill_transfer": u"Transfer",
    "explorer.short": u"Short: ",
    "explorer.stat_tps": u"Trx/s",
    "explorer.state_live": u"Live",
    "explorer.tab_blocks": u"Blockchain",
    "explorer.th_feed": u"Feed",
    "explorer.th_mssr": u"MSSR",
    "explorer.th_settlement": u"Settlement",
    "explorer.th_symbol": u"Symbol",
    "explorer.transfer": u"Transfer ",
    "explorer.tx_prefix": u"Tx ",

    "explorer_assets.s1": EM,
    "explorer_assets.title": u"Asset",
    "explorer_blocks.title": u"Block",

    # ---------------------------------------------------------------- gateway
    "gateway.coin_fact": u"Coin",
    "gateway.coin_label": u"Coin ",
    "gateway.health_ok": u"in Betrieb ",
    "gateway.intro_a": (
        u"Senden Sie externe Coins an die angezeigte Adresse. Diese Seite "
        u"sendet nichts. "
    ),
    "gateway.intro_b": (
        u"Auszahlungen werden im Transfer mit einer Live-Gebührenvorschau "
        u"abgeschlossen."
    ),
    "gateway.via": u" über ",

    # ---------------------------------------------------------------- help
    "help.about_link": u"Über diese Wallet",
    "help.code": u"Code",
    "help.community_title": u"Community",
    "help.confidence_good": u"Gut",
    "help.confidence_high": u"Hoch",
    "help.confidence_language": u"Sprache",
    "help.confidence_level": u"Konfidenz",
    "help.confidence_moderate": u"Mittel — bitte prüfen",
    "help.elastic": u"Community-Index (Historie Dritter)",
    "help.forum": u"Forum",
    "help.report_translation_link": (
        u"Melden Sie ein Übersetzungsproblem auf GitHub"
    ),
    "help.sitemap_sections": u"Bereiche",
    "help.topic_about-making_body": md(
        u"# Die Entstehung dieser Wallet",
        u"Folgt die ursprüngliche Baugeschichte: jede Eingabe, die diese "
        u"Wallet geschaffen hat, von „bitshares-ui erwerben“ am 26. September "
        u"2026 bis zur Issue-1-Korrektur am 3. Oktober, mit den Antworten der "
        u"Erbauer — unverändert erhalten.",
        u"Sie hält die Entscheidungen fest, auf denen diese Wallet steht: der "
        u"Abschied von einem weiteren React-Uplift nach Issue #3583 und seiner "
        u"Tausend-Stunden-Falle, damit diese Wallet von nichts mit "
        u"Release-Zyklus abhängt; jede Transaktion lokal signieren wie die "
        u"alte Wallet, statt sie auszulagern; drei Themes mit dem klassischen "
        u"Look als Standard; Zahlen in menschlichen Einheiten, nie rohe "
        u"Chain-Ganzzahlen; Phone-First-Layouts ab dem ersten Slice; und "
        u"Gebühren aus der Live-Chain gelesen, nie geschätzt. Lesen Sie es "
        u"als Geschichte: so wurde die Wallet gebaut.",
        u"# Das vollständige Dialog-Archiv",
        u"Die vollständige Aufzeichnung jedes einzelnen Dialogs liegt auf der "
        u"Seite Über (#/about). Öffnen Sie dort den Bereich „Vollständiges "
        u"Dialog-Archiv“, um alle Dialoge zu durchsuchen, nach Stichwort zu "
        u"filtern oder mit ?dialog=N direkt zu einem bestimmten Dialog zu "
        u"springen.",
    ),
    "help.topic_about-making_text": u"Die Baugeschichte hinter dieser Wallet —",
    "help.topic_about-making_title": u"Die Entstehung dieser Wallet",
    "help.topic_airdrop_title": u"Airdrops",
    "help.topic_assets-feed_body": md(
        u"# Preis-Feeds veröffentlichen",
        u"Veröffentlichen Sie den Settlement-Preis für ein marktgebundenes "
        u"Asset über den Feed-Desk; der Bestätigungsdialog zeigt vor dem "
        u"Signieren die genaue Gebühr.",
    ),
    "help.topic_assets-feed_text": (
        u"Veröffentlichen Sie Preis-Feeds für marktgebundene Assets, die Sie "
        u"versorgen."
    ),
    "help.topic_assets-feed_title": u"Preis-Feeds veröffentlichen",
    "help.topic_assets-issue_body": md(
        u"# Assets ausgeben",
        u"Erzeugen Sie neuen Bestand eines Assets, das Ihr Konto kontrolliert, "
        u"über den Ausgabe-Desk; Beträge nutzen die Präzision des Assets und "
        u"der Bestätigungsdialog zeigt vor dem Signieren die genaue Gebühr.",
    ),
    "help.topic_assets-issue_text": (
        u"Erzeugen Sie neuen Bestand eines Assets, das Sie kontrollieren, über "
        u"den Ausgabe-Desk."
    ),
    "help.topic_assets-issue_title": u"Assets ausgeben",
    "help.topic_backups_body": md(
        u"# Früh sichern, zweimal sichern",
        u"Machen Sie eine Sicherung Ihrer lokalen Wallet, bevor Sie sie "
        u"finanzieren — eine Sicherung genügt danach meist, bewahren Sie sie "
        u"aber an mindestens zwei sicheren Orten auf, die nur Sie erreichen.",
        u"Es gibt in dieser Wallet keine Sicherungsdatei: Ihre Brainkey IST "
        u"die Sicherung, und die Passphrase allein stellt nichts wieder her. "
        u"Ohne beides — Wörter UND Passphrase — sind Ihre Gelder weg. Bewahren "
        u"Sie die Passphrase niemals neben den Wörtern auf.",
        u"# Ihre Brainkey ist die Sicherung",
        u"Wenn Sie nie rohe Schlüssel von Hand importiert haben, leitet sich "
        u"die gesamte Wallet deterministisch aus einer Brainkey ab — einer "
        u"Zeichenkette aus Wörtern. Notieren Sie die Brainkey, sichern Sie "
        u"jedes Konto und jeden Fonds dieser Wallet.",
        u"Öffnen Sie sie in der Wallet-Verwaltung und schreiben Sie sie auf "
        u"Papier, getrennt von allem Digitalen aufbewahrt. .bin-Dateien der "
        u"Referenz-Wallet können hier nicht importiert werden — die Wallet "
        u"sagt das auf dem Bildschirm, und ein Dateidownload existiert nicht.",
        u"# Fortgeschritten: hierarchische Authorities",
        u"Wenn Sie gewichtete Multi-Konto-Authorities statt einfacher Schlüssel "
        u"verwenden, stellt eine Schlüsselsicherung allein den Zugang "
        u"möglicherweise NICHT wieder her — die Authority-Struktur selbst "
        u"zählt.",
        u"Lesen Sie den Artikel Berechtigungen erneut und notieren Sie die "
        u"vollständige Authority-Einrichtung, nicht nur die Wörter.",
    ),
    "help.topic_barter_title": u"Barter",
    "help.topic_blockchain_title": u"Blockchain",
    "help.topic_browser_body": md(
        u"# Erkannte Funktionen, nie Markennamen",
        u"Diese Wallet fragt nie, welchen Browser Sie nutzen — sie prüft die "
        u"vier Plattformfunktionen, die sie wirklich braucht: WebSocket "
        u"(Chain-Daten), WebCrypto (Schlüsselspeicher), BigInt (Geldrechnen) "
        u"und lokalen Speicher (Einstellungen). Stille heißt bestanden: kein "
        u"Hinweis auf einem modernen Browser bedeutet, dass alles vorhanden ist.",
        u"# Häufigste Ursache: unsicherer Kontext",
        u"Moderne Browser geben WebCrypto nur in sicheren Kontexten frei: "
        u"https-Seiten, localhost und direkt geöffnete Dateien. Derselbe "
        u"aktuelle Browser, der über einfaches http ausgeliefert wird (zum "
        u"Beispiel eine LAN-Adresse), meldet WebCrypto als fehlend — der "
        u"Browser ist in Ordnung, die Adresse nicht. Liefern Sie den Ordner "
        u"über https oder localhost aus oder öffnen Sie index.html direkt.",
        u"# Was weiterhin funktioniert",
        u"Stöbern funktioniert immer: Salden, Märkte, Explorer und Abstimmung "
        u"lesen öffentliche Chain-Daten ohne Wallet-Funktionen. Nur das lokale "
        u"Signieren braucht das fehlende Stück. Den Hinweis wegzutippen "
        u"versteckt ihn auf diesem Gerät; er blockiert nie eine Seite.",
    ),
    "help.topic_browser_text": (
        u"Welche Browser die Wallet ausführen und was der Kompatibilitätshinweis "
        u"bedeutet."
    ),
    "help.topic_browser_title": u"Browser-Unterstützung",
    "help.topic_community_body": md(
        u"# Community",
        u"Menschen und Orte rund um BitShares — Startseite, Code, Explorer, "
        u"Foren und Chats — stehen auf der Community-Seite.",
    ),
    "help.topic_community_text": (
        u"Chats, Foren, Explorer und Code rund um BitShares."
    ),
    "help.topic_community_title": u"Community",
    "help.topic_dashboard_title": u"Dashboard",
    "help.topic_dex-trading_title": u"Handeln",
    "help.topic_gateways_title": u"Gateways",
    "help.topic_htlc_text": (
        u"Hash-gesperrte Swaps, die entweder zahlen oder erstatten."
    ),
    "help.topic_menu_body": md(
        u"# Seitenmenü",
        u"Die Menü-Seite listet jeden Bildschirm dieser Wallet nach Bereich, "
        u"sodass jeder Desk nur einen Tippen entfernt ist.",
    ),
    "help.topic_menu_text": (
        u"Jede Seite dieser Wallet, gruppiert so, wie das Navigationsmenü sie "
        u"gruppiert."
    ),
    "help.topic_menu_title": u"Seitenmenü",
    "help.topic_sitemap_body": md(
        u"Jede Seite dieser Wallet, gruppiert so, wie das Burger-Menü sie "
        u"gruppiert. Alles mit einem Link öffnet direkt; Detailansichten unter "
        u"Seiten ohne Menükarte öffnen von ihren übergeordneten Seiten.",
        u"# Wallet",
        u"- [Dashboard](#/)",
        u"- [Mein Konto](#/account/me)",
        u"- [Konten](#/accounts)",
        u"- [Transfer](#/transfer)",
        u"- [Rechnung](#/invoice)",
        u"- [Vesting](#/vesting)",
        u"- [Wallet](#/wallet)",
        u"- [Wallet-Passwort ändern](#/wallet/password)",
        u"- [Wallet erstellen (Brainkey)](#/create-wallet-brainkey)",
        u"- [Bestehendes Konto importieren](#/existing-account)",
        u"- [Neues Konto registrieren](#/create-account)",
        u"- [Anmelden](#/login)",
        u"- [Registrierung](#/registration)",
        u"- [Empfehlungen](#/referrals)",
        u"# Handel",
        u"- [Börse](#/markets)",
        u"- [Instant-Trade](#/instant-trade)",
        u"- [Liquiditäts-Pools](#/pools)",
        u"- [Wechselkurse](#/cross-rates)",
        u"- [Leihen](#/borrow)",
        u"- [Barter](#/barter)",
        u"- [Einzahlen / Abheben](#/deposit-withdraw)",
        u"- [Same-T-Fonds](#/samet)",
        u"- [Spotlight](#/spotlight)",
        u"# Verdienen & Schützen",
        u"- [Kreditangebot](#/credit-offer)",
        u"- [Lastschrift](#/direct-debit)",
        u"- [HTLC](#/htlc)",
        u"- [Tickets](#/tickets)",
        u"- [Airdrop](#/airdrop)",
        u"- [Benutzerdefinierte Berechtigungen](#/authorities)",
        u"- [Kontolisten](#/lists)",
        u"# Governance",
        u"- [Abstimmung](#/voting)",
        u"- [Vorschläge](#/proposals)",
        u"- [Worker erstellen](#/create-worker)",
        u"- [Prognosemärkte](#/prediction)",
        u"# Entdecken",
        u"- [Explorer](#/explorer)",
        u"- [Assets](#/assets)",
        u"- [Asset erstellen](#/assets/create)",
        u"- [Asset ausgeben](#/assets/issue)",
        u"- [Feed veröffentlichen](#/assets/feed)",
        u"- [Netzwerkgebühren](#/explorer/fees)",
        u"- [Operationen](#/ops)",
        u"- [Top-Operationen](#/top-ops)",
        u"- [Neuigkeiten](#/news)",
        u"# Explorer",
        u"- [Explorer (Blockchain)](#/explorer)",
        u"- [Assets](#/explorer/assets)",
        u"- [Pools](#/explorer/pools)",
        u"- [Konten](#/explorer/accounts)",
        u"- [Zeugen](#/explorer/witnesses)",
        u"- [Komitee-Mitglieder](#/explorer/committee)",
        u"- [Märkte](#/explorer/markets)",
        u"- [Gebühren](#/explorer/fees)",
        u"- [Feeds](#/explorer/feeds)",
        u"# Labor",
        u"- [API-Labor](#/api-lab)",
        u"- [ES-Labor](#/es-lab)",
        u"- [Transaktions-Builder](#/txbuilder)",
        u"- [Kontennetzwerk](#/account-network)",
        u"# Persönlich",
        u"- [Trollbox](#/trollbox)",
        u"- [Favoriten](#/favourites)",
        u"- [Preisalarme](#/alerts)",
        u"- [Hilfe](#/help)",
        u"- [Grenzen der Übersetzung](#/help/translation-limitations)",
        u"- [Über](#/about)",
        u"- [Community](#/community)",
        u"- [Einstellungen](#/settings)",
        u"# Seiten ohne Menükarte",
        u"Registrierungsvarianten, Konto- und Markt-Desks sowie Detailansichten "
        u"öffnen von den Seiten oben oder von Links an anderer Stelle in der "
        u"Wallet.",
        u"- [Lokale Registrierung](#/registration/local)",
        u"- [Cloud-Registrierung](#/registration/cloud)",
        u"- [Beispiel-Kontoseite](#/account/committee-account)",
        u"- [Beispiel-Markt-Desk](#/market/BTS_USD)",
        u"- [Beispiel-Asset-Seite](#/asset/BTS)",
        u"- [Beispiel-Pool-Desk](#/pools/1.19.66)",
        u"- [Menüübersicht](#/menu)",
        u"Detailansichten für ein bestimmtes Kreditangebot, einen Deal, einen "
        u"Vorschlag, einen Block, eine Transaktion, einen HTLC, einen "
        u"Prognosemarkt, einen Transfer-Empfänger, eine Rechnung, ein Gateway, "
        u"einen Einstellungs-Tab, einen Explorer-Tab oder einen Hilfeartikel "
        u"öffnen von ihren übergeordneten Seiten und nehmen eine ID oder einen "
        u"Namen in der Adresse entgegen.",
    ),
    "help.topic_sitemap_text": (
        u"Jede Seite dieser Wallet auf einer Seite: jede Menü-Seite plus die "
        u"Abläufe und Detailansichten, die keine Menükarte haben."
    ),
    "help.topic_sitemap_title": u"Seitenübersicht",
    "help.topic_spotlight_title": u"Spotlight",
    "help.topic_translation-limitations_body": md(
        u"Eine als maschinell übersetzt markierte Übersetzung wurde von einer "
        u"Maschine geschrieben. Niemand hat sie gelesen und geprüft, ob sie "
        u"das sagt, was das Englische sagt — deshalb trägt jede Sprache außer "
        u"dem Englischen in der Kopfzeile dieser Wallet die Markierung. "
        u"Englisch ist der Text, aus dem die anderen übersetzt wurden, trägt "
        u"also keine Markierung.",
        u"",
        u"# Was das * auf einer Zeile bedeutet",
        u"Ein * auf einer Signaturzeile bedeutet zugleich zwei Dinge: Der Text "
        u"wurde von einer Maschine ausgefüllt, und das englische Original ist "
        u"nur einen Tippen entfernt. Tippen Sie auf das *, und das Englische "
        u"erscheint unter der Zeile genau so, wie der englische Stammtext "
        u"dieser Wallet ihn speichert — derselbe Text, aus dem jede andere "
        u"Sprache übersetzt wurde, nicht eine Umschreibung davon.",
        u"",
        u"Die Markierung folgt der Zeile, nicht den Wörtern darin. Ein * "
        u"markiert eine ganze übersetzte Zeile, und die Wallet wählt diese "
        u"Zeilen nach einer festen Regel: jede Zeile auf einem Signatur-, "
        u"irreversiblen oder Wiederherstellungs-Bildschirm — bis zu einer "
        u"Längengrenze, denn ein langer Absatz wird durch diesen Artikel "
        u"abgedeckt — plus jede Zeile, deren englisches Original Gefahrworte "
        u"trägt. Eine Zeile, die nur eine ID oder einen Betrag nennt, trägt "
        u"deshalb trotzdem eine (das An-Feld eines Transfers zum Beispiel), "
        u"ein langer Absatz, der eine ID nennt, dagegen nicht. Ein reiner "
        u"Chain-Wert — ein Betrag in einer Zelle, eine ID in einer Spalte, "
        u"ein Asset-Symbol — ist gar keine übersetzte Zeile und trägt deshalb "
        u"nie eine: dahinter steht kein englischer Text zum Vergleichen.",
        u"",
        u"# Was die Konfidenzstufen bedeuten",
        u"Jede Sprache, die diese Wallet ausliefert, trägt eine Bewertung; sie "
        u"steht in der Tabelle unten. Hoch bedeutet, dass der Text dem "
        u"Englischen genau folgt und natürlich liest. Gut bedeutet, dass er "
        u"brauchbar ist, eine Formulierung aber noch steif klingen kann. "
        u"Mittel bedeutet: Lesen Sie ihn als Entwurf und prüfen Sie das "
        u"Englische, bevor Sie sich darauf verlassen.",
        u"",
        u"Alle Bewertungen unten stammen von der Maschine, die die Texte "
        u"geschrieben hat, und bewerten ihre eigene Arbeit; niemand Unabhängiges "
        u"hat sie geprüft. Eine Bewertung beschreibt, was bisher geprüft wurde, "
        u"für die Sprache insgesamt und nicht Zeile für Zeile. Das Englische "
        u"selbst ist die Referenz: Es ist von Hand geschrieben, und jede andere "
        u"Sprache ist daraus übersetzt.",
        u"",
        u"# Wie Sie einen Text korrigieren",
        u"Korrekturen beginnen mit einer Meldung. Nennen Sie die Sprache der "
        u"Zeile, geben Sie den Schlüssel an, den diese Zeile ausweist, fügen "
        u"Sie das Englische bei, das sie sagen sollte, und schlagen Sie die "
        u"Formulierung vor, die Sie stattdessen verwenden würden.",
        u"",
        u"- Eine Meldung pro Zeile macht eine Korrektur leicht anwendbar.",
        u"- Melden Sie zuerst die Signaturbildschirme: Ein falscher Satz in "
        u"einem Bestätigungsdialog ist der teure Fall.",
        u"- Nutzen Sie den Link am Ende dieses Artikels. Er öffnet ein Issue, "
        u"das im Tracker dieses Projekts bereits für Übersetzungen "
        u"gekennzeichnet ist, es muss nichts neu eingetippt werden.",
        u"",
        u"# Korrekturen sind der einzige Weg zu von Menschen geprüft",
        u"Nichts anderes nimmt einen Text von maschinell gefüllt: nicht, wie "
        u"häufig eine Sprache genutzt wird, nicht eine zweite Maschine, die der "
        u"ersten zustimmt, nicht ein Übersetzungsspeicher. Ein Text gilt erst "
        u"als von Menschen geprüft, wenn ihn jemand in seiner eigenen Sprache "
        u"liest und annimmt, und eine Zeile gilt nur für die tatsächlich "
        u"geprüfte Sprache als geprüft.",
        u"",
        u" Bis dahin bleibt die Markierung, wo sie ist. Eine Übersetzung, die "
        u"niemand gelesen hat, ist besser als gar keine, aber nicht dasselbe "
        u"wie eine, hinter der ein Mensch steht.",
    ),
    "help.topic_translation-limitations_text": (
        u"Maschinell ausgefüllte Übersetzungen sind gekennzeichnet; die "
        u"englische Referenz ist immer einen Tippen entfernt. Helfen Sie uns, "
        u"eine Zeile zu korrigieren."
    ),
    "help.topic_translation-limitations_title": u"Grenzen der Übersetzung",
    "help.topic_voting_text": (
        u"Stimmen Sie für Zeugen, Komitee, Worker — oder geben Sie die Stimme "
        u"an einen Proxy."
    ),
    "help.topic_wallets_body": md(
        u"# Eine Web-App mit lokalem Tresor",
        u"Diese Anwendung läuft in Ihrem Browser und spricht mit einem "
        u"Chain-Knoten als Gateway zum Netzwerk. Alles Geheime bleibt im "
        u"lokalen Tresor Ihres Browsers.",
        u"# Keine Cloud-Anmeldung",
        u"Diese Wallet hat keine Anmeldung mit Benutzername und Passwort: Jede "
        u"Wallet hier ist lokal in einem Browser. Um Ihr Konto in einem neuen "
        u"Browser oder Rechner zu nutzen, beginnen Sie mit derselben Brainkey "
        u"— es gibt keine Zugangsdaten, die sie von irgendwo allein öffnen.",
        u"# Lokale Wallet",
        u"Eine lokale Wallet ist eine Datenbank in einem bestimmten Browser. "
        u"Sie folgt Ihnen nicht auf einen anderen Rechner oder Browser, "
        u"außer Sie bringen die Brainkey mit und importieren sie.",
        u"Lesen Sie den Artikel Sicherungen, bevor Sie sich für echte Gelder "
        u"auf eine lokale Wallet verlassen.",
        u"# Passwort-Disziplin",
        u"Das Passwort verschlüsselt den Tresor. Kurze oder wiederverwendete "
        u"Passwörter fallen dem Raten zum Opfer; eine eigene Passphrase auf "
        u"Papier nicht.",
        u"Eine Passwortänderung verschlüsselt alles neu — prüfen Sie zuerst "
        u"das aktuelle und bestätigen Sie dann, dass sich die Wallet noch "
        u"entsperren lässt, bevor Sie weitergehen.",
    ),
    "help.topic_wallets_title": u"Wallets",
    "help.translation_confidence_heading": (
        u"Wie zuverlässig jede Sprache ist"
    ),

    # ---------------------------------------------------------------- htlc
    "htlc.hash_label": u"Hash: ",
    "htlc.list_sub": (
        u"Sperren Sie Gelder an einen Hash — der Empfänger löst mit dem "
        u"Geheimnis vor dem Ablauf ein, sonst werden Sie erstattet. Von allen "
        u"lesbar; das Passwort wird nur beim Signieren abgefragt."
    ),
    "htlc.preimage_label": u"Preimage",
    "htlc.title": u"HTLC",
    "htlc.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- i18n
    "i18n.badge_body": (
        u"Diese Übersetzungen wurden von einer Maschine geschrieben und nicht "
        u"von einem Menschen geprüft. Mit * markierte Zeilen auf den "
        u"Signaturbildschirmen zeigen zusätzlich das englische Original."
    ),
    "i18n.badge_chip": u"i18n",
    "i18n.badge_details": u"Was das bedeutet",
    "i18n.badge_improve": u"Helfen Sie, diese Übersetzung zu verbessern",
    "i18n.badge_label": (
        u"Übersetzungsstatus: maschinell übersetzt, nicht von Menschen geprüft"
    ),
    "i18n.risk_about_translations": u"Über diese Übersetzungen",
    "i18n.risk_show_english": (
        u"Die englische Referenz für diese Zeile anzeigen"
    ),

    # ---------------------------------------------------------------- instant
    "instant.instant_trade": u"Instant-Trade",
    "instant.limit": u"Limit",
    "instant.order_prefix": u"Order ",
    "instant.preview_balances_note": (
        u"Vorschau als %(name)s (%(id)s) — Salden nicht geprüft. Entsperren "
        u"Sie, um Ihre eigenen vor dem Signieren zu prüfen."
    ),
    "instant.uc_title": u"Zum Signieren entsperren",
    "instant.unlock_sign": u"Entsperren & signieren",
    "instant.via_mid": u" über ",
    # "Trade" heads the walkthrough sentence "Trade BTS/USD …" — the loanword
    # German crypto UIs use for the action, matching the shipped "Walkthrough".
    "instant.walkthrough_trade_prefix": u"Trade ",

    # ---------------------------------------------------------------- market
    "market_book.spread_prefix": u"Spread ",
    "market_ind.count_capped": u"Fenster gekürzt",
    "market_ind.count_note": u"%(count)s × %(bucket)s Kerzen",
    "market_ind.count_partial": (
        u"%(actual)s von %(requested)s × %(bucket)s Kerzen"
    ),
    "market_orders.tape_max": u"max",

    # ---------------------------------------------------------------- menu
    "menu.blurb_labs": u"Werkzeuge für Chain- und Knotenarbeit.",
    "menu.blurb_personal": u"Chat, Alarme und Ihre Einstellungen.",
    "menu.d_account_net": u"Transfer-Verfolgung",
    "menu.d_xrates": u"Pool-Preise für jedes Asset in BTS und darüber hinaus.",
    "menu.p_account_net": u"Kontennetzwerk",
    "menu.p_airdrop": u"Airdrop",
    "menu.p_assets": u"Assets",
    "menu.p_barter": u"Barter",
    "menu.p_community": u"Community",
    "menu.p_dashboard": u"Dashboard",
    "menu.p_htlc": u"HTLC",
    "menu.p_spotlight": u"Spotlight",
    "menu.p_tickets": u"Tickets",
    "menu.p_transfer": u"Transfer",
    "menu.p_trollbox": u"Trollbox",
    "menu.p_vesting": u"Vesting",
    "menu.p_wallet": u"Wallet",
    "menu.p_xrates": u"Wechselkurse",
    "menu.section_explore": u"Entdecken",
    "menu.section_labs": u"Labor",
    "menu.section_personal": u"Persönlich",
    "menu.section_wallet": u"Wallet",

    # ---------------------------------------------------------------- misc
    "misc.asset": u"Asset",
    "misc.authority": u"Authority",
    "misc.blacklist": u"Blacklist",
    "misc.id": u"ID",
    "misc.whitelist": u"Whitelist",

    # ---------------------------------------------------------------- nav
    "nav.credit": u"Kredit",
    "nav.dashboard": u"Dashboard",
    "nav.margin": u"Margin",
    "nav.markets": u"Märkte",
    "nav.pools": u"Pools",
    "nav.transfer": u"Transfer",

    "news.explorer_blocks_and_transactions": u"Die Chain erkunden",
    "notify.quote_label": u"Quote",

    # ---------------------------------------------------------------- pool
    "pool.asset_1_field": u"Asset 1 (beliebige Seite)",
    "pool.asset_2_field": u"Asset 2 (beliebige Seite)",
    "pool.asset_a_field": u"Asset A",
    "pool.asset_b_field": u"Asset B",
    "pool.clear_btn": u"Leeren",
    "pool.delete_not_empty": (
        u"Nicht leer — %(legs)s muss vor dem Löschen 0 sein."
    ),
    "pool.direct_hit": u"Direkte Pool-Suche — Blätterregler ausgeblendet.",
    "pool.map_core_self": u"BTS ist das Core-Token von BitShares",
    "pool.min_swaps": u"Min. Swaps",
    # Leading space is glue: the hint is appended after a label.
    "pool.my_swaps_hint": (
        u" Führen Sie einen über das Swap-Panel oben aus — Ihre Swaps in "
        u"diesem Pool werden hier aufgelistet."
    ),
    "pool.no_filter_match": u"Keine Swaps passen zu diesen Filtern.",
    "pool.pool_row": u"Pool",
    "pool.share_or_pool_hint": u"Symbol, 1.3.x oder Pool 1.19.x",
    "pool.slippage_field": u"Slippage %",
    "pool.slippage_row": u"Slippage",
    "pool.spot_row": u"Spot",
    "pool.stake_autofill_hint": (
        u"Geben Sie einen Betrag ein — der andere wird automatisch zum "
        u"Pool-Verhältnis ausgefüllt."
    ),
    "pool.stake_link": u"Stake",
    "pool.stake_preview_bad": (
        u"Prüfen Sie die Beträge — keine Anteilsschätzung."
    ),
    "pool.stake_preview_need_both": (
        u"Geben Sie beide Beträge für eine Anteilsschätzung ein."
    ),
    "pool.stake_preview_unavailable": (
        u"Anteilsschätzung nicht verfügbar (offline)."
    ),
    "pool.stake_ratio_empty": (
        u"Pool ist leer — geben Sie beide Beträge von Hand ein."
    ),
    "pool.stake_ratio_row": u"Verhältnis (Spot)",
    "pool.stake_shares_row": u"Geschätzte LP-Anteile",
    "pool.stake_unstake_col": u"Stake/Unstake",
    "pool.swap_desk": u"Swap-Desk",
    "pool.swap_mkt_preview_dash": u"Marktgebühr (Vorschau): —",
    "pool.swap_mkt_row": u"Marktgebühr",
    "pool.swap_preview": u"Quote (Vorschau): ",
    "pool.swap_preview_dash": u"Quote (Vorschau): —",
    "pool.swap_stake_col": u"Swap/Stake",
    # Leading space is glue, like pool.my_swaps_hint.
    "pool.swaps_hint": (
        u" Swaps erscheinen nach dem ersten Tausch in diesem Pool — führen "
        u"Sie einen über das Swap-Panel oben aus."
    ),
    "pool.uc_action": u"Aktion",
    "pool.uc_title": u"Entsperren, um fortzufahren",

    # ------------------------------------------------------------ pool_detail
    "pool_detail.candle_capped": u"Fenster gekürzt",
    "pool_detail.candle_count": (
        u"%(swaps)s Swaps · %(count)s × %(bucket)s Kerzen"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s Swaps · %(actual)s von %(requested)s × %(bucket)s Kerzen"
    ),
    "pool_detail.invert": u"Umkehren",
    "pool_detail.invert_label": (
        u"Diagrammausrichtung umkehren (A pro B / B pro A)"
    ),
    "pool_detail.map_connects": (
        u"Eine Linie verbindet zwei Assets, wenn ein finanzierter Pool "
        u"existiert und in den letzten 24 Stunden ein Handel stattgefunden hat."
    ),
    "pool_detail.map_connects_fallback": (
        u"Eine Linie verbindet zwei Assets, wenn ein finanzierter Pool "
        u"existiert. Die 24h-Handelsaktivität ist unbestätigt (Historie nicht "
        u"verfügbar) — finanzierte Pools werden angezeigt."
    ),
    "pool_detail.map_min_swaps": u"(min. %(min)s Swaps)",

    # ---------------------------------------------------------------- pool_net
    # Mirrors chunk-A's market_net wording key for key (collapse/expand, the
    # "·" node and edge cards, the verdict lines).
    "pool_net.canvas_label": (
        u"Pool-Netzwerkkarte. Drücken Sie Enter, um BTS zu öffnen."
    ),
    "pool_net.col_a": u"Asset 1",
    "pool_net.col_b": u"Asset 2",
    "pool_net.col_pool": u"Pool",
    "pool_net.collapse": u"Einklappen",
    "pool_net.direct": u"mit BTS gepaart",
    # Pure id / amount glue, "·" separators included: byte-identical.
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.empty": u"Kein Pool berührt diesen Filter.",
    "pool_net.expand": u"Ausklappen",
    "pool_net.hops": u"%(n)s Hops zu BTS",
    "pool_net.legend": u"Marken",
    "pool_net.loading": u"Netzwerk wird geladen…",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s Pools · %(hops)s",
    "pool_net.offline": (
        u"Netzwerk nicht verfügbar — mitgelieferte Skelettdaten werden "
        u"angezeigt. Wiederholen Sie, sobald die Verbindung steht."
    ),
    "pool_net.offline_empty": (
        u"Netzwerk nicht verfügbar — keine Skelett-Pools zwischengespeichert."
    ),
    "pool_net.orphan": u"von BTS verwaist",
    "pool_net.partial": (
        u"Live-Aktualisierung unvollständig — mitgelieferte Pools werden "
        u"angezeigt."
    ),
    "pool_net.phys": u"Physik",
    "pool_net.prompt": (
        u"Tippen Sie auf einen Knoten für das Asset, auf eine Linie für den "
        u"Pool."
    ),
    "pool_net.ramp": u"Pool-Größe: klein → groß",
    "pool_net.ready": u"%(pools)s Pools · %(assets)s Assets",
    "pool_net.title": u"Pool-Netzwerk",
    "pool_net.twin": u"Pool-Zeilen (%(n)s)",
    "pool_net.twin_more": (
        u"%(shown)s von %(n)s Pools werden angezeigt — verengen Sie den "
        u"Filter, um weniger zu sehen."
    ),
    "pool_net.verdict_full": u"%(pools)s Pools · %(assets)s Assets",
    "pool_net.verdict_orphan": u"Keine Route zwischen %(a)s und %(b)s",
    "pool_net.verdict_path": u"%(a)s erreicht %(b)s in %(n)s Hops",
    "pool_net.verdict_star": u"Pools, die %(s)s berühren: %(n)s",

    "pools.selector_title": u"Pool-Auswahl",

    # ---------------------------------------------------------------- prediction
    "prediction.asset": u"Asset",
    "prediction.details": u"Details",
    "prediction.hdr_asset": u"Asset",
    "prediction.hdr_status": u"Status",
    "prediction.house": u"House",
    "prediction.pmo_governance": u"Governance",
    "prediction.pmo_name": u"Name",
    "prediction.pnl": u"PnL",
    "prediction.portfolio": u"Portfolio",
    "prediction.settlement": u"Settlement",
    "prediction.uc_title": u"Zum Signieren entsperren",

    # ---------------------------------------------------------------- proposal
    # Signing-dialog wording: plain and literal, the English reference sits
    # right beside it.
    "proposal.confirm_proposal_create_op_22": (
        u"Vorschlagserstellung bestätigen (Op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Vorschlagslöschung bestätigen (Op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"Vorschlag löschen (Op %(op)s)",
    "proposal.id": u"ID",
    "proposal.inner_ticket_2": u"Asset",
    "proposal.inner_transfer_2": u"Asset",
    "proposal.inner_transfer_4": u"Memo (optional)",
    "proposal.lock": u"Sperre",
    "proposal.memo": u"Memo",
    "proposal.multisig_story": (
        u"Gemeinsames Konto? Ein Miteigentümer schlägt vor, teilt die "
        u"1.10.N-ID, die anderen genehmigen unten. Arbeit mit mehreren "
        u"Operationen oder Geräten geht im Transaktions-Builder weiter."
    ),
    "proposal.open_txbuilder": u"Transaktions-Builder öffnen",
    "proposal.ticket": u"Ticket",
    "proposal.viewing_as": (
        u"Ansicht als %(name)s (%(id)s) — entsperren Sie, um als Sie selbst zu "
        u"handeln."
    ),

    "proposals_ticket.title": u"Tickets",

    "referrals.referrer": u"Referrer",
    "referrals.registrar": u"Registrar",

    "samet.asset": u"Asset",
    "samet.delta": u"Delta",

    # ---------------------------------------------------------------- seo
    "seo.desc_about": (
        u"Über diese BitShares-Wallet — lokale Schlüssel, keine Anmeldung, "
        u"kein Tracking. Kostenlos stöbern und lokal signieren."
    ),
    "seo.desc_account": (
        u"Dieses BitShares-Konto ansehen — Salden, Orders und Historie werden "
        u"live aus der Chain gelesen. Ohne Anmeldung."
    ),
    "seo.desc_account_net": (
        u"Aufzeichnen, an wen ein Konto sendet, an wen es verleiht und von "
        u"wem es leiht — aus dem Community-Index gelesen. Ohne Anmeldung."
    ),
    "seo.desc_dashboard": (
        u"BitShares-Dashboard — Salden, Märkte und Chain-Aktivität auf einen "
        u"Blick. Kostenlos stöbern; Schlüssel bleiben auf Ihrem Gerät."
    ),
    "seo.desc_explorer": (
        u"BitShares-Blöcke, Transaktionen und Assets erkunden — Live-Chain-"
        u"Daten, ohne Anmeldung durchsuchbar."
    ),
    "seo.desc_help": (
        u"BitShares-Wallet-Hilfe — Anleitungen zu Konten, Handel, Abstimmung "
        u"und Wiederherstellung. Fangen Sie hier an, wenn Sie stecken."
    ),
    "seo.desc_login": (
        u"Entsperren Sie Ihre lokale BitShares-Wallet — Passwort, Brainkey "
        u"oder importierte Schlüssel. Schlüssel verlassen dieses Gerät nie."
    ),
    "seo.desc_market": (
        u"BTS gegen USD im BitShares-Orderbuch handeln — Live-Bids, Asks und "
        u"Historie, lokal auf Ihrem Gerät signiert."
    ),
    "seo.desc_markets": (
        u"BitShares-Orderbuch-Märkte nach 24h-Volumen durchsuchen und den "
        u"Handels-Desk jedes Paares öffnen. Ohne Anmeldung."
    ),
    "seo.desc_pools": (
        u"BitShares-Liquiditätspools durchsuchen — Paare, Salden und "
        u"Aktivität live aus der Chain gelesen. Ohne Anmeldung."
    ),
    "seo.desc_transfer": (
        u"Senden Sie BitShares-Assets an jedes Konto. Prüfen Sie jedes Feld, "
        u"dann signieren Sie lokal — Schlüssel verlassen Ihr Gerät nie."
    ),
    "seo.desc_voting": (
        u"Stimmen Sie für BitShares-Zeugen, Komitee-Mitglieder und Worker. "
        u"Jede Stimme wird lokal auf Ihrem Gerät signiert."
    ),
    "seo.desc_xrates": (
        u"Jedes Pool-Asset in BTS und darüber hinaus zu den letzten "
        u"Swap-Preisen. Ohne Anmeldung."
    ),
    "seo.title_about": u"Über — BitShares Wallet",
    "seo.title_account": u"Konto %(name)s — BitShares Wallet",
    "seo.title_account_net": u"Kontennetzwerk — BitShares Wallet",
    "seo.title_dashboard": u"Dashboard — BitShares Wallet",
    "seo.title_explorer": u"Blockchain-Explorer — BitShares Wallet",
    "seo.title_help": u"Hilfe — BitShares Wallet",
    "seo.title_login": u"Anmelden — BitShares Wallet",
    "seo.title_market": u"BTS/USD-Börse — BitShares Wallet",
    "seo.title_markets": u"Märkte — BitShares Wallet",
    "seo.title_pools": u"Liquiditätspools — BitShares Wallet",
    "seo.title_transfer": u"Gelder senden — BitShares Wallet",
    "seo.title_voting": u"Zeugen wählen — BitShares Wallet",
    "seo.title_xrates": u"Wechselkurse — BitShares Wallet",

    # ---------------------------------------------------------------- shell
    # shell.brand / footer_brand / footer_brand_vanilla are PINNED: brand text,
    # never translated, never claimed as translated.
    "shell.dashboard": u"Dashboard",
    "shell.footer_ahead": u"%(n)s Commits vor",
    "shell.footer_ahead_one": u"1 Commit vor",
    "shell.footer_at_build": u"zum Build %(date)s",
    "shell.footer_behind": u"%(n)s Commits zurück",
    "shell.footer_behind_one": u"1 Commit zurück",
    "shell.footer_dahead": u"%(n)s voraus",
    "shell.footer_dbehind": u"%(n)s zurück",
    "shell.footer_diverged": u"abgewichen von",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    "shell.footer_offbranch": u"nicht auf Master",
    "shell.footer_sync": u"in Sync mit",

    # ---------------------------------------------------------------- splash
    "splash.card_dex_d": u"Auf dem offenen Markt kaufen und verkaufen.",
    "splash.card_explore_d": u"Blöcke und Kontohistorie lesen.",
    "splash.card_explore_t": u"Explorer",
    "splash.card_pool_d": (
        u"Verdienen Sie mit, indem Sie zwei Assets in einen Pool legen."
    ),
    "splash.card_pool_t": u"Pools",
    "splash.card_wallet_d": u"Schlüssel nur auf diesem Gerät halten.",
    "splash.card_wallet_t": u"Wallet",
    "splash.cards_title": u"Handeln, staken, erkunden — starten Sie hier",
    "splash.cta_exchange": u"An der Börse handeln",
    "splash.hero_sub": u"Ihre Schlüssel. Ihre Gelder, on-chain.",
    "splash.hero_sub2": (
        u"Märkte kostenlos durchsuchen. Nur zum Signieren entsperren."
    ),
    "splash.hero_title": (
        u"BitShares-Wallet in Ihrem Browser — nichts zu installieren."
    ),
    "splash.pulse_assets": u"Assets",
    "splash.pulse_stale": u"— veraltet",
    "splash.pulse_time": u"Head-Zeit",
    "splash.pulse_title": u"Live-Chain-Zahlen",
    "splash.step1_d": (
        u"Keine Anmeldung nötig — durchsuchen Sie zuerst die Chain."
    ),
    "splash.step1_t": u"Umsehen",
    "splash.step2_d": (
        u"Ein Brainkey wird auf diesem Gerät erzeugt. Notieren Sie ihn auf "
        u"Papier."
    ),
    "splash.step2_t": u"Wallet erstellen",
    "splash.step3_d": (
        u"Limit-Orders, Liquiditätspools und Stimmzettel — alles on-chain."
    ),
    "splash.step3_t": u"Handeln / staken / abstimmen",
    "splash.topvol_unavailable": (
        u"Top-Markt-Volumen ist offline — prüfen Sie Einstellungen → Knoten."
    ),
    "splash.trust_keys_d": (
        u"Signiert wird lokal auf Ihrem Gerät. Kein Server sieht jemals ein "
        u"Passwort oder einen Schlüssel."
    ),

    # ---------------------------------------------------------------- swap
    "swap.title": u"Swap",

    # ---------------------------------------------------------------- ticket
    "ticket.airdrop": u"Airdrop",
    # Example payload: account names and amounts, byte-verbatim by design.
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "ticket.asset": u"Asset",
    "ticket.id": u"ID",
    "ticket.ticket": u"Ticket",
    "ticket.tickets": u"Tickets",
    "tickets.title": u"Tickets",

    # ---------------------------------------------------------------- tour
    "tour.away_note": (
        u"Auf dem Börsen-Desk — öffnen Sie ihn, um dies hervorgehoben zu sehen."
    ),
    "tour.s1_body": (
        u"Jede Seite liest öffentliche Chain-Daten ohne Anmeldung. Öffnen Sie "
        u"zum Start einen Markt — Ihr Passwort wird nur beim Signieren "
        u"abgefragt."
    ),
    "tour.s1_title": u"Alles kostenlos durchsuchen, lokal signieren",
    "tour.s3_body": (
        u"Preis-Kerzen, Volumen und Tiefe sowie das Indikator-Menü: Overlays "
        u"wie SMA und EMA, Oszillatoren wie RSI, MACD und Stochastic. Öffnen "
        u"Sie die Börse, um es live zu sehen."
    ),
    "tour.s3_title": u"Live-Preischarts ansehen",
    "tour.s4_body": (
        u"Die Panels Kaufen und Verkaufen nehmen zum Üben beliebige Zahlen an. "
        u"Nichts verlässt Ihre Maschine, bis Sie mit einer entsperrten Wallet "
        u"prüfen und signieren. Öffnen Sie die Börse, um es zu probieren."
    ),
    "tour.s4_title": u"Kaufen und Verkaufen üben",

    # ---------------------------------------------------------------- trade
    # Signing-dialog wording: literal on purpose.
    "trade.co_details": u"Details",
    "trade.tab_single": u"Einzeln",
    "trade.title": u"Börse",
    "trade.uc_amount": u"Betrag",
    "trade.uc_orders": u"Orders",
    "trade.uc_price": u"Preis",
    "trade.uc_range": u"Preisbereich",
    "trade.uc_title": u"Entsperren, um fortzufahren",
    "trade.uc_total": u"Zu verkaufende Summe",

    # ---------------------------------------------------------------- transfer
    "transfer.asset_label": u"Asset ",
    # Sentinel value, not prose: kept byte-verbatim.
    "transfer.bad_asset_shape": u"bad-asset-shape",
    "transfer.confirm_proposal_title": u"Vorschlag bestätigen (Op %(op)s)",
    "transfer.enclosed_op_note": (
        u"Eingeschlossene Op: Transfer (Op %(op)s) — wird erst nach den "
        u"Genehmigungen ausgeführt."
    ),
    "transfer.memo_label": u"Memo (optional) ",
    "transfer.propose_notice_locked": (
        u"Vorschlagender ist während der Sperrung standardmäßig %(name)s "
        u"(%(id)s) — entsperren Sie, um als Sie selbst zu handeln."
    ),
    "transfer.share_needs_to_amount": (
        u"Ein teilbarer Link benötigt einen Empfänger und einen Betrag."
    ),
    "transfer.title": u"Transfer",
    "transfer.uc_title": u"Entsperren, um fortzufahren",
    "transfer.unlock_sign": u"Entsperren & prüfen",

    # ---------------------------------------------------------------- trollbox
    "trollbox.bytes_prefix": u"Bytes: ",
    "trollbox.bytes_unit": u"Bytes",
    "trollbox.channel_row": u"Kanal",
    "trollbox.fee": u"Gebühr",
    "trollbox.language_row": u"Sprache",
    "trollbox.message_row": u"Nachricht",
    "trollbox.post_review_title": u"Nachricht prüfen",
    "trollbox.size_row": u"Größe",
    "trollbox.status_live": u"Live",
    "trollbox.title": u"Trollbox",
    "trollbox.unlock_post": u"Entsperren & posten",

    # ---------------------------------------------------------------- txbuilder
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "txbuilder.chain_prefix": u"Chain: ",
    "txbuilder.link_pools": u"Pools",
    "txbuilder.link_proposals": u"Vorschläge",
    "txbuilder.link_transfer": u"Transfer",

    # ---------------------------------------------------------------- unlockconfirm
    "unlockconfirm.cancel": u"Zurück",
    "unlockconfirm.empty_password": u"Geben Sie Ihr Wallet-Passwort ein.",
    "unlockconfirm.password": u"Passwort",
    "unlockconfirm.unlock_failed": u"Entsperren fehlgeschlagen.",
    "unlockconfirm.unlock_post": u"Entsperren & posten",

    # ---------------------------------------------------------------- vesting
    "vesting.asset": u"Asset",
    "vesting.filter": u"Filter",
    "vesting.id": u"ID",
    "vesting.policy": u"Policy",
    "vesting.title": u"Vesting",
    "vesting.vesting": u"Vesting",

    # ---------------------------------------------------------------- vote
    "vote.ballot_intro": (
        u"Ihr Stake wählt Zeugen und Komitee und finanziert Worker — alle "
        u"Zählungen und Anteile unten sind Live-Lesungen der Chain."
    ),
    "vote.confirm_witness_update_op_21": (
        u"Zeugen-Update bestätigen (Op %(op)s)"
    ),
    "vote.direct_note": (
        u"Stimmen direkt veröffentlicht (voting_account %(id)s)."
    ),
    "vote.fee_core": u" (core)",
    "vote.in_sync": (
        u"Die Stimmliste stimmt mit der Chain überein — nichts zu "
        u"veröffentlichen."
    ),
    "vote.proxies_follow_another_account_s_slate_re": (
        u"Proxys folgen der Stimmliste eines anderen Kontos — lesen Sie, wie "
        u"Abstimmung funktioniert, bevor Sie einen setzen."
    ),
    "vote.proxy_follows": (
        u" — Ihr Stake folgt diesem Konto; die Stimmliste unten ist "
        u"schreibgeschützt."
    ),
    "vote.proxy_prefix": u"Proxy: ",
    "vote.proxy_row": u"Proxy",
    "vote.retried_prefix": (
        u"Der Knoten hat den Proxy-Modus %(mode)s abgelehnt, daher wurde die "
        u"Stimme als selbst veröffentlicht (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"Knoten hat den Proxy-Modus %(mode)s abgelehnt — einmal als selbst "
        u"erneut versuchen…"
    ),
    "vote.row_final": u"endgültig: ",
    "vote.url": u"URL",

    # ---------------------------------------------------------------- wallet
    "wallet.brainkey": u"Brainkey",
    "wallet.title": u"Wallet",

    # ---------------------------------------------------------------- xrate
    "xrate.add_btn": u"Spalte hinzufügen",
    "xrate.asset_col": u"Asset",
    "xrate.base_pinned": (
        u"BTS ist die Basis-Spalte und kann nicht entfernt werden."
    ),
    "xrate.empty": (
        u"Keine Pool-Assets innerhalb von 3 Hops von BTS auf dieser Chain."
    ),
    "xrate.intro": (
        u"Jedes Pool-Asset zum letzten Swap-Preis bewertet, verknüpft über das "
        u"Pool-Netzwerk. Nichts wird signiert und nichts gespeichert."
    ),
    "xrate.load_failed": u"Wechselkurse konnten nicht geladen werden: ",
    "xrate.loading": u"Pools werden gelesen…",
    "xrate.no_route_col": u"Keine Route zu %(sym)s innerhalb von 6 Pool-Hops.",
    "xrate.refresh_btn": u"Preise aktualisieren",
    "xrate.remove_btn": u"Entfernen ",
    "xrate.retry_btn": u"Wiederholen",
    "xrate.show_all": u"Alle Assets anzeigen",
    "xrate.status": (
        u"%(pools)s Pools · %(assets)s Assets innerhalb von 3 Hops · "
        u"%(done)s von %(total)s Pools haben einen letzten Swap"
    ),
    "xrate.title": u"Wechselkurse",
    "xrate.token_label": u"Quote-Token hinzufügen",
    # Example of ticker symbols, byte-verbatim.
    "xrate.token_placeholder": u"USD, CNY, BTC…",
    "xrate.unknown_token": u"Kein Pool-Asset namens %(sym)s.",
    "xrate.unpriced": (
        u"Ein Teil dieser Route hat noch keinen aufgezeichneten Swap."
    ),
}


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


def check_batch(en_flat, key, value, problems):
    """G1-G4 + punctuation hygiene for one key/value pair."""
    master = en_flat[key]
    if sorted(PLACEHOLDER.findall(master)) != sorted(
        PLACEHOLDER.findall(value)
    ):
        problems.append("placeholder multiset changed: %s" % key)
    # Single-brace interpolations ({s}) must survive verbatim too.
    if sorted(BRACE.findall(master)) != sorted(BRACE.findall(value)):
        problems.append("brace placeholder changed: %s" % key)
    if IDENT.match(master) and master != value:
        problems.append("identifier not byte-verbatim: %s" % key)
    if key in PINNED and master != value:
        problems.append("pinned key not byte-verbatim: %s" % key)
    if master.count("\n") != value.count("\n"):
        problems.append(
            "line count changed: %s (en %d, de %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def verify():
    """Structural re-proof of the shipped file against the en master."""
    de, en = load(DE_PATH), load(EN_PATH)
    d, e = flat(de), flat(en)
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(DE):
        if key not in d:
            bad.append("key missing from de.json: %s" % key)
            continue
        if key not in e:
            bad.append("key missing from en master: %s" % key)
            continue
        if d[key] != e[key]:
            check_batch(e, key, d[key], bad)
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
            bad.append(
                "suspicious code point U+%04X in %s" % (ord(hit), key)
            )

    # Pinned ids are never in DE (they must keep the English bytes) but must
    # still equal en after the write — chunk-A's settings.* keys included.
    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(DE) if d.get(k) == e.get(k)]
    by_section = {}
    for k in same:
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(DE) - len(same), len(DE)))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch              : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash    : %d (hashes ok: %d)"
          % (links, links_ok))
    print("  intentionally identical to en           : %d" % len(same))
    for sec in sorted(by_section):
        print("    %-12s %d" % (sec, by_section[sec]))
    for k in same:
        print("      %s = %r" % (k, d[k]))
    meta = de.get("_meta", {})
    print("  _meta version=%r untranslated=%r translated=%d entries"
          % (meta.get("version"), meta.get("untranslated"),
             len(meta.get("translated", []))))
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
    raw = open(DE_PATH, encoding="utf-8").read()
    de = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(de, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: de.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(de))
    before_meta = json.dumps(de["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(DE.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in de.json: %s" % key)
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
        deep_set(de, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(de)
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
    # tooling/check_i18n.py reads it in both directions — a claimed key that
    # still reads English is a false claim, and an unclaimed key that is no
    # longer English is an undeclared translation. So the claim moves in
    # lockstep with the bytes, for exactly the keys this batch translated. The
    # values kept byte-identical on purpose (loanwords, brands, ids, glue)
    # stay UNCLAIMED, which is the honest state for them. Nothing else in
    # _meta moves — filling strings is not verification, so the controller's
    # v2 provenance/verified/high_risk fields stay untouched.
    meta = de["_meta"]
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
    # Converging, not incremental: a key already at this batch's value from an
    # earlier run is claimed too, so re-running after a partial write repairs
    # the claim instead of leaving it stale.
    added = sorted(k for k in DE
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

    print("de chunk-B: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in SECTIONS:
        if by_section.get(sec):
            print("  %-12s %d" % (sec, by_section[sec]))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / brands / ids / glue / "
              "sentinels — deliberately NOT claimed):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run — no files written (pass --apply)")
        return 0

    with open(DE_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(de, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/de.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())