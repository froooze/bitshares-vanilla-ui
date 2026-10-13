#!/usr/bin/env python3
"""i18n de chunk-A: fill the account/account_net/settings/market/market_net/asset
sections of vanilla/locales/de.json.

Scope: ONLY the six sections listed in SECTIONS. Other agents are filling the
rest of the de dictionary concurrently, so this script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from de.json, or one whose English master moved, is REFUSED.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim (they are also listed in KEPT_ENGLISH);
  G3  pinned keys    settings.network_*, settings.custom_placeholder,
                     settings.pending, settings.dash, settings.theme_* stay
                     byte-verbatim;
  G4  structure      same line count, same markdown link hashes (#/...) for
                     every filled key;
  G5  untouched      every key outside SECTIONS keeps its exact prior value,
                     and _meta keeps its v1 shape (version 1, untranslated
                     false) with `translated` gaining exactly the keys this
                     batch newly translated — nothing else in _meta moves, and
                     --fix-meta is never run here: filling strings is not a
                     trust claim, and claiming a key whose value still reads
                     English is the lie v1 exists to forbid;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Register: formal "Sie", matching the voice already shipped in de.json (see
e.g. account.s5, settings.discover_none, viewings "entsperren Sie, um als
Sie selbst zu handeln"). Vocabulary is reused verbatim from de.json wherever
that dictionary has already settled a word: Wallet, Asset, Order, Fills,
Guthaben/Saldo, Knoten, Chain, Vorschlag, Zeuge, Komitee, Worker, Proxy,
Vesting, Claim, Pool, Swap, Stake, Ticket, Same-T-Fonds, Kreditangebot, Deal,
Sicherheiten, Schuld, Lastschrift, Authority, HTLC, Memo, Smartcoin. Nothing is
invented where a German crypto UI keeps the English word (see the
intentionally-identical list the run prints).

This script never runs git (other agents share this worktree); use
--diff <baseline.json> with a plain file copy to prove that only this batch
changed.

Usage:
  python3 tooling/apply_i18n_de_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_de_chunkA.py --apply         # writes de.json
  python3 tooling/apply_i18n_de_chunkA.py --verify        # structural re-proof
  python3 tooling/apply_i18n_de_chunkA.py --diff BASE.json  # before/after
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

SECTIONS = ("account", "account_net", "settings", "market", "market_net", "asset")

# Keys whose value is an identifier / id / persisted setting id (rule 1).
PINNED = (
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

DE = {
    # ---------------------------------------------------------------- account_net
    "account_net.title": u"Kontennetzwerk",
    "account_net.intro": (
        u"Geben Sie ein oder mehrere Konten ein, um zu sehen, an wen sie "
        u"senden, an wen sie verleihen und von wem sie leihen. Wird aus dem "
        u"Community-Historienindex gelesen; nichts wird signiert und nichts "
        u"wird gespeichert."
    ),
    "account_net.seeds_label": u"Zu kartierende Konten",
    # Account names + an object id: byte-verbatim.
    "account_net.seeds_placeholder": "committee-account, alice, 1.2.42",
    "account_net.go": u"Netzwerk zeichnen",
    "account_net.idle": u"Noch nichts gezeichnet.",
    "account_net.scanning": u"Community-Index wird gelesen…",
    "account_net.need_seeds": u"Geben Sie mindestens ein Konto zum Kartieren ein.",
    "account_net.need_class": (
        u"Aktivieren Sie mindestens eine Linienart zum Zeichnen."
    ),
    "account_net.canvas_missing": (
        u"Die Netzwerk-Leinwand ist in diesem Build nicht verfügbar; die "
        u"Tabelle unten listet weiterhin jede Linie."
    ),
    "account_net.class_transfer": u"Transfer",
    "account_net.class_transfer_help": u"Direkte Transfers von Konto zu Konto.",
    "account_net.class_credit": u"Kredit",
    "account_net.class_credit_help": (
        u"Angenommene und zurückgezahlte Kreditangebote."
    ),
    "account_net.class_override": u"Override-Transfer",
    "account_net.class_override_help": (
        u"Transfers, deren Gebühr der Asset-Emittent zahlt."
    ),
    "account_net.class_debit": u"Lastschrift",
    "account_net.class_debit_help": u"Lastschrift-Berechtigungen und Abhebungen.",
    "account_net.class_htlc": "HTLC",
    "account_net.class_htlc_help": (
        u"Hash-zeitgesperrte Kontrakte und ihre Aktualisierungen."
    ),
    "account_net.class_vesting": u"Vesting",
    "account_net.class_vesting_help": (
        u"Vesting-Salden, die eine dritte Partei verwaltet."
    ),
    "account_net.status_scanned": (
        u"%(scanned)s indexierte Operationen aus %(n)s Konten"
    ),
    "account_net.status_graph": u"%(nodes)s Konten · %(edges)s Linien",
    "account_net.status_truncated": u"neueste %(n)s Operationen pro Konto",
    "account_net.status_node_cap": u"erste %(n)s Gegenparteien angezeigt",
    "account_net.status_edge_cap": u"erste %(n)s Linien angezeigt",
    "account_net.status_self": u"%(n)s Selbstübertragungen übersprungen",
    "account_net.status_shape": u"%(n)s unlesbare Einträge übersprungen",
    "account_net.status_credit_missing": (
        u"%(n)s Kreditlinien übersprungen (Angebot oder Deal nicht auf der "
        u"Chain gefunden)"
    ),
    "account_net.status_credit_index": (
        u"%(n)s Kreditlinien aus dem Index aufgelöst (das zugehörige Angebots- "
        u"oder Deal-Objekt ist nicht mehr auf der Chain)"
    ),
    "account_net.status_unknown": u"nicht gefunden: %(names)s",
    "account_net.detail_hint": (
        u"Tippen Sie auf eine Linie für deren Details; tippen Sie auf ein "
        u"Konto, um es zu öffnen."
    ),
    # Pure placeholder/separator glue — nothing to translate.
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ops · %(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s op · %(kind)s"
    ),
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.kind_flow": u"Fluss",
    "account_net.kind_relation": u"Beziehung",
    "account_net.no_amount": u"kein Betrag",
    "account_net.more_assets": u" + %(n)s weitere",
    "account_net.twin_summary": u"Tabellenansicht (barrierefrei)",
    "account_net.twin_from": u"Von",
    "account_net.twin_to": u"Nach",
    "account_net.twin_class": u"Art",
    "account_net.twin_relation": u"Fluss/Beziehung",
    "account_net.twin_amount": u"Betrag",
    "account_net.twin_count": u"Ops",
    "account_net.twin_span": u"Von → Bis",
    "account_net.twin_empty": (
        u"Keine Linien zwischen diesen Konten in den gescannten indexierten "
        u"Operationen."
    ),
    "account_net.es_disabled": (
        u"Der Community-Index ist ausgeschaltet. Schalten Sie ihn in den "
        u"Einstellungen ein, um diese Karte zu zeichnen."
    ),
    "account_net.es_bad_account": (
        u"Dieser Name ist kein Konto auf dieser Chain."
    ),
    "account_net.es_unavailable": (
        u"Der Community-Index ist gerade nicht erreichbar. Versuchen Sie es "
        u"gleich noch einmal."
    ),
    "account_net.depth_label": u"Tiefe",
    "account_net.depth_1": u"1 Hop",
    "account_net.depth_2": u"2 Hops",
    "account_net.ring1_label": u"Ring 1",
    "account_net.ring2_label": u"Ring 2",
    "account_net.twin_depth": u"Hop",
    "account_net.stale_settings": (
        u"Tiefe oder Nachbarn wurden geändert — drücken Sie auf Netzwerk "
        u"zeichnen."
    ),
    "account_net.status_depth": u"Karte: %(depth)s",
    "account_net.status_expanded": u"erweitert: %(names)s",
    "account_net.status_unexpanded": (
        u"%(n)s direkte Gegenparteien nicht erweitert"
    ),
    "account_net.status_expansion_scanned": (
        u"%(n)s indexierte Operationen aus Erweiterungen"
    ),
    "account_net.status_expansion_truncated": (
        u"Erweiterungs-Scans auf die neuesten Operationen gekürzt"
    ),

    # ---------------------------------------------------------------- market_net
    "market_net.title": u"Märkte",
    "market_net.subtitle": (
        u"Top-Orderbuch-Märkte nach 24h-Volumen. Wählen Sie eine Zeile, um "
        u"den Desk zu öffnen."
    ),
    "market_net.asset_1_field": u"Asset 1 (beliebige Seite)",
    "market_net.asset_2_field": u"Asset 2 (beliebige Seite)",
    "market_net.list_btn": u"Märkte auflisten",
    "market_net.clear_btn": u"Leeren",
    "market_net.loading": u"Märkte werden geladen…",
    "market_net.empty": u"Keine Märkte für diesen Filter gefunden.",
    "market_net.offline": (
        u"Netzwerk nicht verfügbar — zwischengespeicherte Märkte werden "
        u"angezeigt. Wiederholen Sie, sobald die Verbindung steht."
    ),
    "market_net.col_market": u"Markt",
    "market_net.col_last": u"Letzter",
    "market_net.col_change": u"24h Δ",
    "market_net.col_vol": u"24h-Vol",
    "market_net.col_spark": "7d",
    "market_net.top_note": (
        u"Top %(shown)s von %(probed)s geprüften — nach 24h-Volumen."
    ),
    "market_net.band_title": u"Marktnetzwerk",
    "market_net.collapse": u"Einklappen",
    "market_net.expand": u"Ausklappen",
    "market_net.open_desk": u"%(id)s öffnen",
    "market_net.spark_label": u"7-Tage-Trend für %(id)s",
    "market_net.selector_title": u"Marktauswahl",
    "market_net.map_ready": u"%(markets)s Märkte · %(assets)s Assets",
    "market_net.map_empty": u"Keine Märkte mit aktuellem Volumen.",
    "market_net.verdict_full": u"%(markets)s Märkte · %(assets)s Assets",
    "market_net.verdict_star": u"Märkte, die %(s)s berühren: %(n)s",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s Märkte",
    # Placeholder/separator glue — nothing to translate.
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "market_net.twin": u"Marktzeilen (%(n)s)",
    "market_net.twin_more": (
        u"%(shown)s von %(n)s Märkten werden angezeigt — verengen Sie den "
        u"Filter, um weniger zu sehen."
    ),
    "market_net.canvas_label": (
        u"Karte des Marktnetzwerks. Drücken Sie Enter, um den Markt zu öffnen."
    ),
    "market_net.prompt": (
        u"Tippen Sie auf einen Knoten für das Asset, auf eine Linie für den "
        u"Markt."
    ),
    "market_net.ramp": u"24h-Volumen: niedrig → hoch",
    "market_net.map_hops_ready": (
        u"%(pairs)s Paare · %(assets)s Assets · 24h-Fills"
    ),
    "market_net.map_fallback": (
        u"%(pairs)s Paare · %(assets)s Assets · 24h-Fills unbestätigt"
    ),
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s Fills/24h"
    ),
    "market_net.verdict_path": (
        u"%(a)s erreicht %(b)s in %(n)s gefüllten Märkten"
    ),
    "market_net.verdict_no_path": (
        u"Keine Route über gefüllte Märkte zwischen %(a)s und %(b)s"
    ),
    "market_net.ramp_fills": u"24h-Fills: niedrig → hoch",
    "market_net.verdict_web": u"Von %(s)s erreichbare Märkte: %(n)s",

    # ---------------------------------------------------------------- asset
    "asset.backing_field": u"Backing (1.3.N)",
    "asset.bitasset_row": u"Bitasset",
    "asset.cer_row": u"Core-Wechselkurs (CER)",
    "asset.flags_title": u"Berechtigungen",
    "asset.mcr_row": "MCR",
    "asset.nft_row": "NFT",
    "asset.offset_row": u"Offset",
    "asset.op_col": "Op",
    "asset.producers_title": u"Feed-Produzenten (op %(op)s)",
    "asset.publish_op19_title": u"Feed veröffentlichen (op %(op)s)",
    "asset.smartcoin_row": u"Smartcoin",
    "asset.symbol_field": u"Symbol (A-Z0-9.)",
    "asset.tab_pma": "PMA",
    "asset.tab_uia": "UIA",
    "asset.viewing_notice": (
        u"Ansicht als %(name)s (%(id)s) — entsperren Sie, um zu signieren."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"Der Emittent ist standardmäßig das Ansichtskonto (%(id)s gesperrt, "
        u"Ihr Konto entsperrt) — geben Sie einen beliebigen Emittenten ein, "
        u"den Sie kontrollieren. Wenn Sie diese Seite von einer Kontoseite "
        u"geöffnet haben, fügen Sie hier den Kontonamen ein."
    ),
    "asset.multisig_title": u"Gemeinsamer Emittent? Als Vorschlag einreichen",
    "asset.multisig_body": (
        u"Wenn dieses Asset mehr als eine Genehmigung braucht, schlägt das "
        u"direkte Signieren fehl — reichen Sie die Änderung stattdessen als "
        u"Vorschlag ein und bitten Sie die Miteigentümer um Genehmigung "
        u"(op 23)."
    ),
    "asset.multisig_open_proposals": u"Vorschläge ansehen",
    "asset.multisig_open_txbuilder": u"Transaktions-Builder öffnen",
    "asset.multisig_coowner_hint": (
        u"Miteigentümer? Reichen Sie die Änderung auf der Vorschlagsseite "
        u"ein und bitten Sie die Miteigentümer um Genehmigung (op 23)."
    ),
    "asset.new_issuer_field": u"Neuer Emittent",
    "asset.issue_memo_warning": (
        u"Hängen Sie ein Memo an — es wird on-chain im Klartext gespeichert."
    ),
    "asset.issue_memo_no_key": (
        u"Für dieses Konto ist kein Memo-Key hinterlegt."
    ),
    "asset.owner_key_note": (
        u"Erfordert den aktiven Schlüssel des Asset-Eigentümers."
    ),
    "asset.producers_live_title": u"Feed-Produzenten",
    "asset.loading_producers": u"Produzenten werden geladen…",
    "asset.producers_failed": u"Produzenten konnten nicht geladen werden.",
    "asset.no_producers": (
        u"Noch keine Feeds veröffentlicht — Produzenten erscheinen hier, "
        u"sobald sie veröffentlichen."
    ),
    "asset.witness_fed_note": (
        u"Zeugen-Feed: alle aktiven Zeugen dürfen veröffentlichen."
    ),
    "asset.committee_fed_note": (
        u"Komitee-Feed: alle aktiven Komitee-Mitglieder dürfen veröffentlichen."
    ),
    "asset.producer_col": u"Produzent",
    "asset.published_col": u"Veröffentlicht",
    "asset.feed_history_title": u"Feed-Historie",
    "asset.history_days": u"Zeitraum",
    "asset.plot_feeds": u"Feeds darstellen",
    "asset.no_history": (
        u"Keine Historie in diesem Zeitraum — Herausgeber veröffentlichen "
        u"selten; versuchen Sie 90 T."
    ),
    "asset.history_loading": u"Feed-Historie wird geladen…",
    "asset.history_capped": (
        u"Die ersten 8 Herausgeber werden angezeigt (Limit für "
        u"Geschwindigkeit)…"
    ),
    "asset.history_pub": u"Herausgeber %(i)s/%(n)s…",
    "asset.history_exchange": u"Börse + Pools werden geladen…",
    "asset.history_failed": u"Feed-Historie konnte nicht geladen werden.",
    "asset.invert_btn": u"Umkehren",
    "asset.orientation_note": u"%(m)s pro %(b)s",

    # ---------------------------------------------------------------- settings
    "settings.network_devnet": "devnet",
    "settings.network_mainnet": "mainnet",
    "settings.network_testnet": "testnet",
    "settings.custom_placeholder": u"wss://…",
    "settings.pending": u"…",
    "settings.dash": EM,
    "settings.theme_original_blue": "original-blue",
    "settings.theme_light": "light",
    "settings.theme_dark": "dark",
    "settings.theme_label": u"Theme ",
    "settings.theme_title": u"Theme",
    "settings.hist_yes": u"JA",
    "settings.hist_no": u"NEIN",
    "settings.geo_note": (
        u"*Standorte und Anbieter stammen von ipaddress.to (https, ohne "
        u"Schlüssel) — Ihre Adresse wird bei der Abfrage gesehen; Antworten "
        u"werden 24 Stunden auf diesem Gerät zwischengespeichert."
    ),
    "settings.th_chain": u"Chain",
    "settings.th_handshake": u"Handshake",
    "settings.th_head": u"Kopf",
    "settings.th_history": u"Historie",
    "settings.th_location": u"Standort *",
    "settings.th_participation": u"Teilnahme",
    "settings.th_ping": u"Ping",
    "settings.th_provider": u"Anbieter *",
    "settings.confirm_back": u"Zurück",
    "settings.confirm_remove_action": u"Aktion",
    "settings.confirm_remove_hide": (
        u"Diesen Knoten ausblenden (bleibt verborgen, bis er wieder "
        u"hinzugefügt wird)"
    ),
    "settings.confirm_remove_result": u"Ergebnis",
    "settings.confirm_remove_switch": u"Der aktive Knoten wechselt zu %(node)s",
    "settings.confirm_remove_title": u"Knoten entfernen?",
    "settings.confirm_remove_unlist": u"Aus meiner Liste entfernen",
    "settings.discover_note": (
        u"**Knoten finden durchsucht GitHub nach Knotenlisten und prüft dann, "
        u"was es findet. GitHub und die geprüften Knoten sehen Ihre "
        u"Netzwerkadresse. Die Ergebnisse sind Kandidaten zur Prüfung — es "
        u"wird nichts automatisch hinzugefügt."
    ),
    "settings.age_s": u"%(n)s s",
    "settings.language_title": u"Sprache",
    "settings.sign_title": u"Signieren",
    "settings.sign_auto": u"Automatisch (Erweiterung, wenn verfügbar)",
    "settings.sign_ext": u"Immer die Erweiterung verwenden",
    "settings.sign_ext_absent": (
        u"Auf diesem Gerät wurde keine Erweiterung erkannt — Signaturen "
        u"entstehen auf dieser Seite."
    ),
    "settings.sign_ext_present": (
        u"Erweiterung auf diesem Gerät erkannt."
    ),
    "settings.sign_browser": u"Immer auf dieser Seite signieren",
    "settings.sign_mode_ext_page": (
        u"Signaturen bleiben in der Erweiterung — von Websites isoliert."
    ),
    "settings.sign_mode_ext": (
        u"Signaturen werden im Erweiterungsfenster bestätigt."
    ),
    "settings.sign_mode_browser": (
        u"Signaturen entstehen im Speicher dieser Seite."
    ),
    "settings.sign_warn": (
        u"Jedes Skript, das auf dieser Seite läuft — auch eine kompromittierte "
        u"gehostete Kopie — kann Ihre Schlüssel lesen, solange sie entsperrt "
        u"sind. Lassen Sie über die Erweiterung signieren, oder betreiben Sie "
        u"eine Kopie, die Sie kontrollieren."
    ),
    "settings.sign_guide": u"So installieren Sie die Erweiterung",
    "settings.sign_sites": u"Verbundene Websites",
    "settings.sign_sites_story_a": u"Beispiel: ein Würfelspiel auf ",
    "settings.sign_sites_story_b": (
        u" möchte als Ihr Konto spielen — eine Genehmigung listet es hier "
        u"auf, gebunden nur an dieses Konto. Signaturen werden weiterhin "
        u"jedes Mal abgefragt. (Der Link führt nirgendwohin — es ist ein frei "
        u"erfundenes Beispiel.)"
    ),
    "settings.sign_sites_empty": (
        u"Noch keine Websites genehmigt — Genehmigungen erscheinen hier mit "
        u"Widerruf pro Website."
    ),
    "settings.sign_revoke": u"Widerrufen",
    "settings.sign_badge": (
        u"Signieren mit Erweiterung aktiv — Details unter Anmelden"
    ),
    "settings.sign_badge_local": (
        u"Signieren auf dieser Seite — Details unter Anmelden"
    ),

    # ---------------------------------------------------------------- market
    "market.charts": u"Charts",
    "market.col_order": u"Order",
    "market.log_label": u"Log",
    "market.ov_bb": "BB",
    "market.ov_ema": "EMA",
    "market.ov_psar": "PSAR",
    "market.ov_sma": "SMA",
    "market.stat_bidask": u"Bid–Ask",
    "market.stat_chg": u"24h Δ",
    "market.stat_empty": EM,
    "market.tf_discrete": u"Diskret",
    "market.discrete_fills": u"Fills",
    "market.discrete_swaps": u"Swaps",
    "market.discrete_unavailable": (
        u"Indikatoren in der diskreten Ansicht nicht verfügbar."
    ),
    "market.discrete_no_fills": (
        u"Noch keine Fills — platzieren Sie eine Order oder versuchen Sie ein "
        u"anderes Paar."
    ),
    "market.discrete_volume": u"Diskretes Volumen",
    "market.th_block": u"Block",
    "market.trades_title": u"Trades",
    "market.chg_label": u"24h Δ",
    "market.overlays_group": u"Overlays",
    "market.plots_group": u"Diagramme",
    "market.vol_log": u"Vol: Log",
    "market.vol_lin": u"Vol: Linear",
    "market.vol_label": u"Vol",
    "market.loading_pool_map": u"Karte wird geladen…",
    "market.settle_first100": (
        u"Die ersten 100 werden angezeigt (Limit von get_settle_orders: 100)"
    ),
    "market.settle_no_cancel": (
        u"Settlement-Orders können nicht storniert werden — sie werden beim "
        u"Settlement ausgeführt (nach der Force-Settlement-Verzögerung des "
        u"Assets)."
    ),
    "market.flt_min_price": u"Min. Preis",
    "market.flt_max_price": u"Max. Preis",
    "market.no_filter_match": u"Keine Fills passen zu diesen Filtern.",
    "market.adjust_button": u"Anpassen",
    "market.update_title": u"Order anpassen",
    "market.update_price": u"Neuer Preis ",
    "market.update_amount": u"Zu verkaufender Betrag (neue Summe) ",
    "market.update_expiry": u"Neuer Ablauf ",
    "market.update_review": u"Update prüfen",
    "market.update_no_change": (
        u"Keine Änderungen — bearbeiten Sie Preis, Betrag oder Ablauf."
    ),
    "market.update_price_change": u"Preis (alt → neu)",
    "market.update_amount_change": u"Betragsänderung",
    "market.update_expiry_change": u"Ablauf (alt → neu)",
    "market.confirm_adjust": u"Anpassung bestätigen",
    "market.update_bad_price": u"Geben Sie einen Preis größer als null ein.",
    "market.update_bad_amount": u"Geben Sie einen Betrag größer als null ein.",
    "market.update_bad_expiry": u"Geben Sie einen Ablauf in der Zukunft ein.",
    "market.update_broadcasting": u"Update wird gesendet…",
    "market.update_done": u"Order aktualisiert",
    "market.fail_update": u"Update fehlgeschlagen.",
    "market.exchange_desk": u"Börsen-Desk",
    "market.discrete_tip_time": u"Zeit",
    "market.discrete_tip_price": u"Preis",
    "market.discrete_tip_volume": u"Volumen",
    "market.discrete_tip_volume_quote": u"Volumen (Quote)",
    "market.discrete_tip_account": u"Konto",
    "market.discrete_tip_order": u"Order",
    "market.discrete_tip_block": u"Block",
    "market.map_connects": (
        u"Eine Linie verbindet zwei Assets, wenn in den letzten 24 Stunden "
        u"ein Markttrade stattgefunden hat."
    ),
    "market.map_connects_fallback": (
        u"Eine Linie verbindet zwei Assets, wenn ein finanzierter Pool "
        u"existiert. Die 24h-Trade-Aktivität ist unbestätigt (Historie nicht "
        u"verfügbar) — finanzierte Pools werden angezeigt."
    ),
    "market.map_hops_note": (
        u"Eine Linie ist ein Markt, der in den letzten 24 Stunden gefüllt hat. "
        u"%(pairs)s Paare werden angezeigt."
    ),
    "market.map_hops_no_route": u"Keine Route zu BTS über gefüllte Märkte.",
    "market.map_hops_empty": (
        u"In den letzten 24 Stunden hat rund um diese Seiten kein Markt "
        u"gefüllt."
    ),
    "market.map_aria": (
        u"Marktnetzwerk. Linien sind Märkte, die in den letzten 24 Stunden "
        u"gefüllt haben."
    ),
    "market.map_edge_fills": u"%(desk)s · %(a)s–%(b)s · %(fills)s Fills/24h",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.map_hops_filtered": (
        u"Eine Linie ist ein Markt, der in den letzten 24 Stunden gefüllt hat. "
        u"%(shown)s von %(total)s Paaren werden angezeigt (min. %(min)s "
        u"Fills/24h)."
    ),
    "market.min_fills": u"Min. Fills",
    "market.map_leg_ok": u"{s} verbindet sich mit BTS",
    "market.map_leg_orphan": (
        u"WARNUNG: {s} hat keine Route über gefüllte Märkte!"
    ),

    # ---------------------------------------------------------------- account
    "account.asset_th": u"Asset",
    "account.order_th": u"Order",
    "account.page_total": u"Seitengesamt ≈ ",
    "account.portfolio_page": u"Seite %(page)s von %(pages)s",
    "account.prices_cover_this_page": (
        u"Die Preise decken diese Seite ab — blättern Sie weiter, um mehr "
        u"Assets zu bewerten."
    ),
    "account.multisig_checking": u"Authorities werden geprüft…",
    "account.multisig_single": (
        u"Einzelschlüssel — aktiv %(ath)s/%(an)s · Eigentümer "
        u"%(oth)s/%(on)s."
    ),
    "account.multisig_shared": (
        u"Gemeinsames Konto — aktiv %(ath)s/%(an)s · Eigentümer "
        u"%(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"Gemeinsames Konto? Vorschläge finden Sie auf der Vorschlagsseite."
    ),
    "account.multisig_unavailable": (
        u"Authorities nicht verfügbar — Vorschläge werden weiterhin auf der "
        u"Vorschlagsseite aufgelistet."
    ),
    "account.multisig_view_proposals": u"Vorschläge ansehen",
    "account.multisig_open_txbuilder": u"Transaktions-Builder öffnen",
    "account.draw_network": u"Netzwerk zeichnen",
    "account.upgrade_row_upgrade": u"Upgrade",
    "account.op_unknown": u"Operation #%(n)s",
    # Operation labels: "<noun> <action>" compounds with a hyphen, matching the
    # ten already-shipped account.op_* values (Konto-Erstellung, Konto-Update,
    # Asset-Erstellung, Call-Order-Update, Limit-Order-Storno, …).
    "account.op_assert_op": u"Assert-Plan",
    "account.op_asset_burn": u"Asset-Burn",
    "account.op_asset_issue": u"Asset-Ausgabe",
    "account.op_asset_settle": u"Asset-Settlement",
    "account.op_asset_update": u"Asset-Update",
    "account.op_authority_create": u"Authority-Erstellung",
    "account.op_authority_delete": u"Authority-Löschung",
    "account.op_authority_update": u"Authority-Update",
    "account.op_balance_claim": u"Saldo-Claim",
    "account.op_blind_from": u"Verblendeter Transfer (von)",
    "account.op_blind_to": u"Verblendeter Transfer (an)",
    "account.op_blind_transfer": u"Verblendeter Transfer",
    "account.op_claim_fees": u"Gebühren-Claim",
    "account.op_claim_pool": u"Pool-Claim",
    "account.op_collateral_bid": u"Sicherheiten-Gebot",
    "account.op_committee_join": u"Komitee-Beitritt",
    "account.op_committee_update": u"Komitee-Update",
    "account.op_custom_op": u"Benutzerdefinierte Operation",
    "account.op_deal_expired": u"Deal abgelaufen",
    "account.op_deal_repay": u"Deal-Rückzahlung",
    "account.op_deal_update": u"Deal-Update",
    "account.op_debit_claim": u"Lastschrift-Claim",
    "account.op_debit_create": u"Lastschrift-Erstellung",
    "account.op_debit_delete": u"Lastschrift-Löschung",
    "account.op_debit_update": u"Lastschrift-Update",
    "account.op_execute_bid": u"Gebot ausführen",
    "account.op_fba_distribute": u"FBA-Verteilung",
    "account.op_fee_pool_fund": u"Gebühren-Pool-Aufstockung",
    "account.op_feed_producers_update": u"Feed-Produzenten-Update",
    "account.op_feed_publish": u"Feed-Veröffentlichung",
    "account.op_global_settle": u"Globales Settlement",
    "account.op_htlc_create": u"HTLC-Erstellung",
    "account.op_htlc_extend": u"HTLC-Verlängerung",
    "account.op_htlc_redeem": u"HTLC-Einlösung",
    "account.op_htlc_redeemed": u"HTLC eingelöst",
    "account.op_htlc_refund": u"HTLC-Rückerstattung",
    "account.op_issuer_update": u"Emittenten-Update",
    "account.op_offer_accept": u"Kreditannahme",
    "account.op_offer_create": u"Kreditangebot-Erstellung",
    "account.op_offer_delete": u"Kreditangebot-Löschung",
    "account.op_offer_update": u"Kreditangebot-Update",
    "account.op_order_update": u"Order-Update",
    "account.op_override_transfer": u"Override-Transfer",
    "account.op_params_update": u"Update der globalen Parameter",
    "account.op_pool_create": u"Pool-Erstellung",
    "account.op_pool_delete": u"Pool-Löschung",
    "account.op_pool_deposit": u"Pool-Einzahlung",
    "account.op_pool_swap": u"Pool-Swap",
    "account.op_pool_update": u"Pool-Update",
    "account.op_pool_withdraw": u"Pool-Auszahlung",
    "account.op_proposal_create": u"Vorschlags-Erstellung",
    "account.op_proposal_delete": u"Vorschlags-Löschung",
    "account.op_proposal_update": u"Vorschlags-Update",
    "account.op_samet_borrow": u"Same-T-Leihen",
    "account.op_samet_create": u"Same-T-Fonds-Erstellung",
    "account.op_samet_delete": u"Same-T-Fonds-Löschung",
    "account.op_samet_repay": u"Same-T-Rückzahlung",
    "account.op_samet_update": u"Same-T-Fonds-Update",
    "account.op_settle_cancel": u"Settlement abgebrochen",
    "account.op_smartcoin_update": u"Smartcoin-Update",
    "account.op_ticket_create": u"Ticket-Erstellung",
    "account.op_ticket_update": u"Ticket-Update",
    "account.op_vesting_create": u"Vesting-Erstellung",
    "account.op_vesting_withdraw": u"Vesting-Auszahlung",
    "account.op_witness_join": u"Zeugen-Beitritt",
    "account.op_witness_update": u"Zeugen-Update",
    "account.op_worker_create": u"Worker-Erstellung",
    # History one-liners: German present tense, matching the shipped trade /
    # vesting summaries ("Ausgeführt: … bezahlt, … erhalten").
    "account.sum_account_create": u"Hat %(name)s registriert",
    "account.sum_account_transfer": (
        u"Hat das Konto an %(owner)s übertragen"
    ),
    "account.sum_account_update": u"Konto aktualisiert: %(account)s",
    "account.sum_asset_burn": u"Hat %(amount)s verbrannt",
    "account.sum_asset_create": u"Hat das Asset %(symbol)s erstellt",
    "account.sum_asset_issue": u"Hat %(amount)s an %(to)s ausgegeben",
    "account.sum_asset_settle": (
        u"Hat das Settlement von %(amount)s beantragt"
    ),
    "account.sum_asset_update": u"Hat das Asset %(asset)s aktualisiert",
    "account.sum_authorities": (
        u"Hat die Authorities von %(account)s aktualisiert"
    ),
    "account.sum_balance_claim": u"Hat %(amount)s geclaimt",
    "account.sum_bid": u"Hat %(coll)s für %(debt)s geboten",
    "account.sum_blind": (
        u"Verblendeter Transfer (%(in)s ein, %(out)s aus)"
    ),
    "account.sum_call_update": (
        u"Position angepasst: %(coll)s Sicherheiten, %(debt)s Schuld"
    ),
    "account.sum_claim_fees": u"Hat %(amount)s Gebühren geclaimt",
    "account.sum_committee_create": u"Komitee-Mitglied geworden: %(account)s",
    "account.sum_committee_update": (
        u"Hat das Komitee-Mitglied %(account)s aktualisiert"
    ),
    "account.sum_custom": u"Benutzerdefinierte Operation von %(account)s",
    "account.sum_deal_expired": u"Deal %(deal)s abgelaufen",
    "account.sum_deal_repay": (
        u"Hat %(amount)s für den Deal %(deal)s zurückgezahlt"
    ),
    "account.sum_deal_update": u"Hat den Deal %(deal)s aktualisiert",
    "account.sum_debit_claim": u"Hat %(amount)s Lastschrift geclaimt",
    "account.sum_debit_create": (
        u"Hat %(amount)s Lastschrift für %(to)s autorisiert"
    ),
    "account.sum_debit_delete": (
        u"Hat die Lastschrift-Berechtigung %(perm)s gelöscht"
    ),
    "account.sum_debit_update": (
        u"Hat %(amount)s Lastschrift für %(to)s aktualisiert"
    ),
    "account.sum_execute_bid": u"Hat das Gebot %(coll)s für %(debt)s ausgeführt",
    "account.sum_fee_pool_fund": (
        u"Hat den Gebühren-Pool von %(asset)s mit %(amount)s aufgestockt"
    ),
    "account.sum_feed": (
        u"Feed für %(asset)s von %(publisher)s veröffentlicht"
    ),
    "account.sum_feed_producers": (
        u"Hat %(n)s Feed-Produzenten für %(asset)s gesetzt"
    ),
    "account.sum_fill": u"Ausgeführt: %(pays)s bezahlt, %(receives)s erhalten",
    "account.sum_global_settle": u"Hat %(asset)s global gesettelt",
    "account.sum_htlc_claimed": u"HTLC %(id)s geclaimt",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(amount)s von %(from)s an %(to)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s verlängert",
    "account.sum_htlc_redeem": u"HTLC %(id)s eingelöst",
    "account.sum_htlc_refund": u"HTLC %(id)s erstattet",
    "account.sum_issuer_update": u"Neuer Emittent für %(asset)s: %(issuer)s",
    "account.sum_offer_accept": (
        u"Hat %(amount)s gegen %(coll)s geliehen (Angebot %(offer)s)"
    ),
    "account.sum_offer_create": u"Hat ein Kreditangebot in %(asset)s erstellt",
    "account.sum_offer_delete": u"Hat das Angebot %(offer)s gelöscht",
    "account.sum_offer_update": u"Hat das Angebot %(offer)s aktualisiert",
    "account.sum_order_cancel": u"Hat die Order %(order)s storniert",
    "account.sum_order_create": (
        u"Hat %(sell)s für mindestens %(buy)s angeboten"
    ),
    "account.sum_order_update": u"Hat die Order %(order)s aktualisiert",
    "account.sum_pool_create": u"Hat den Pool %(a)s / %(b)s erstellt",
    "account.sum_pool_delete": u"Hat den Pool %(pool)s gelöscht",
    "account.sum_pool_deposit": (
        u"Hat %(a)s + %(b)s in den Pool %(pool)s gestakt"
    ),
    "account.sum_pool_swap": (
        u"Hat im Pool %(pool)s %(sell)s → mindestens %(buy)s getauscht"
    ),
    "account.sum_pool_update": u"Hat den Pool %(pool)s aktualisiert",
    "account.sum_pool_withdraw": (
        u"Hat %(shares)s aus dem Pool %(pool)s entstakt"
    ),
    "account.sum_proposal_create": u"Hat %(n)s Operationen vorgeschlagen",
    "account.sum_proposal_delete": u"Hat den Vorschlag %(proposal)s gelöscht",
    "account.sum_proposal_update": u"Hat den Vorschlag %(proposal)s genehmigt",
    "account.sum_samet_borrow": (
        u"Hat %(amount)s aus dem Fonds %(fund)s geliehen"
    ),
    "account.sum_samet_create": (
        u"Hat einen Same-T-Fonds mit %(amount)s erstellt"
    ),
    "account.sum_samet_delete": u"Hat den Same-T-Fonds %(fund)s gelöscht",
    "account.sum_samet_repay": (
        u"Hat %(amount)s an den Fonds %(fund)s zurückgezahlt"
    ),
    "account.sum_samet_update": u"Hat den Same-T-Fonds %(fund)s aktualisiert",
    "account.sum_settle_cancel": (
        u"Hat das Settlement von %(amount)s abgebrochen"
    ),
    "account.sum_smartcoin_update": u"Hat die Smartcoin %(asset)s aktualisiert",
    "account.sum_ticket_create": u"Hat das Ticket %(amount)s erstellt",
    "account.sum_ticket_update": u"Hat das Ticket %(ticket)s aktualisiert",
    "account.sum_transfer": u"Transfer %(amount)s von %(from)s an %(to)s",
    "account.sum_transfer_recv": u"Hat %(amount)s von %(from)s erhalten",
    "account.sum_transfer_send": u"Hat %(amount)s an %(to)s gesendet",
    "account.sum_upgrade": u"Hat %(account)s upgegradet",
    "account.sum_vesting_create": u"Hat %(amount)s für %(owner)s gevestet",
    "account.sum_vesting_withdraw": (
        u"Hat %(amount)s aus dem Vesting ausgezahlt"
    ),
    "account.sum_whitelist": u"Hat %(account)s auf die Liste gesetzt",
    "account.sum_witness_create": u"Zeuge geworden: %(account)s",
    "account.sum_witness_update": u"Hat den Zeugen %(account)s aktualisiert",
    "account.sum_worker_create": u'Hat den Worker „%(name)s“ erstellt',
}

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


def deep_get(d, dotted):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def deep_set(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def load(path):
    return json.loads(
        open(path, encoding="utf-8").read(),
        object_pairs_hook=collections.OrderedDict,
    )


def check_batch(en_flat, values, problems):
    """G1-G4 + punctuation hygiene for one key/value pair."""
    key = values[0]
    value = values[1]
    if sorted(PLACEHOLDER.findall(en_flat[key])) != sorted(
        PLACEHOLDER.findall(value)
    ):
        problems.append("placeholder multiset changed: %s" % key)
    # Single-brace interpolations ({s}) must survive verbatim too.
    if sorted(BRACE.findall(en_flat[key])) != sorted(BRACE.findall(value)):
        problems.append("brace placeholder changed: %s" % key)
    if IDENT.match(en_flat[key]) and en_flat[key] != value:
        problems.append("identifier not byte-verbatim: %s" % key)
    if key in PINNED and en_flat[key] != value:
        problems.append("pinned key not byte-verbatim: %s" % key)
    if en_flat[key].count("\n") != value.count("\n"):
        problems.append("line count changed: %s" % key)
    if LINK_HASH.findall(en_flat[key]) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    hit = suspicious(value)
    if hit:
        problems.append("suspicious code point U+%04X in %s"
                        % (ord(hit), key))


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
        if d[key] != e.get(key):
            check_batch(e, (key, d[key]), bad)
        if PLACEHOLDER.findall(e.get(key, "")):
            ph_filled += 1
            if sorted(PLACEHOLDER.findall(e[key])) == sorted(
                PLACEHOLDER.findall(d[key])
            ):
                ph_ok += 1
        if "\n" in e.get(key, "") or "\n" in d[key]:
            multi += 1
            if e[key].count("\n") == d[key].count("\n"):
                multi_ok += 1
        if LINK_HASH.findall(e.get(key, "")) or LINK_HASH.findall(d[key]):
            links += 1
            if LINK_HASH.findall(e[key]) == LINK_HASH.findall(d[key]):
                links_ok += 1
        hit = suspicious(d[key])
        if hit:
            bad.append("suspicious code point U+%04X in %s" % (ord(hit), key))

    same = [k for k in sorted(DE) if d.get(k) == e.get(k)]
    by_section = {}
    for k in same:
        by_section[k.split(".")[0]] = by_section.get(k.split(".")[0], 0) + 1
    scope_left = [
        k for k in sorted(e)
        if k.split(".")[0] in SECTIONS and d.get(k) == e[k] and k not in DE
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(DE) - len(same), len(DE)))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch               : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash     : %d (hashes ok: %d)"
          % (links, links_ok))
    print("  intentionally identical to en            : %d" % len(same))
    for sec in SECTIONS:
        print("    %-12s %d" % (sec, by_section.get(sec, 0)))
    for k in same:
        print("      %s = %r" % (k, d[k]))
    print("  in-scope keys still equal to en and NOT "
          "in this batch: %d" % len(scope_left))
    for k in scope_left:
        print("    %s" % k)
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


def diff(baseline_path):
    """Before/after proof against a plain file copy (never git)."""
    base = load(baseline_path)
    now = load(DE_PATH)
    en = load(EN_PATH)
    b, n, e = flat(base), flat(now), flat(en)
    changed = [k for k in sorted(n) if b.get(k) != n[k]]
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for k in changed:
        check_batch(e, (k, n[k]), bad)
        if PLACEHOLDER.findall(b[k]):
            ph_filled += 1
            if sorted(PLACEHOLDER.findall(b[k])) == sorted(
                PLACEHOLDER.findall(n[k])
            ):
                ph_ok += 1
        if b[k].count("\n") or n[k].count("\n"):
            multi += 1
            if b[k].count("\n") == n[k].count("\n"):
                multi_ok += 1
        if LINK_HASH.findall(b[k]) or LINK_HASH.findall(n[k]):
            links += 1
            if LINK_HASH.findall(b[k]) == LINK_HASH.findall(n[k]):
                links_ok += 1
    outside = [k for k in n if k not in DE and n[k] != b.get(k)]
    if outside:
        bad.append("keys outside this batch changed: %d (%s)"
                   % (len(outside), ", ".join(outside[:5])))
    if set(n) != set(b):
        bad.append("key set changed")
    bm, nm = base.get("_meta", {}), now.get("_meta", {})
    meta_shape = (
        bm.get("version") == nm.get("version")
        and bm.get("untranslated") == nm.get("untranslated")
    )
    gained = sorted(set(nm.get("translated", [])) - set(bm.get("translated", [])))
    lost = sorted(set(bm.get("translated", [])) - set(nm.get("translated", [])))
    if not meta_shape:
        bad.append("_meta version/untranslated changed")
    if lost:
        bad.append("_meta.translated lost %d key(s): %s"
                   % (len(lost), ", ".join(lost[:5])))
    not_translated = [k for k in gained if k not in DE or n[k] == e.get(k)]
    if not_translated:
        bad.append("_meta.translated claims %d key(s) this batch did not "
                   "translate: %s" % (len(not_translated),
                                      ", ".join(not_translated[:5])))
    if nm.get("version") != 1:
        bad.append("_meta.version is not 1")
    if nm.get("untranslated") is not False:
        bad.append("_meta.untranslated is not false")
    if nm.get("translated") != sorted(nm.get("translated", [])):
        bad.append("_meta.translated is not sorted")

    print("diff: %d values differ from %s (%d of them in this batch's %d)"
          % (len(changed), os.path.basename(baseline_path),
             sum(1 for k in changed if k in DE), len(DE)))
    print("  placeholder-bearing strings changed    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values changed               : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values with markdown link hashes         : %d (hashes ok: %d)"
          % (links, links_ok))
    print("  values changed outside this batch       : %d" % len(outside))
    print("  _meta v1 shape kept (version/untranslated): %s "
          "(version=%r untranslated=%r)"
          % (meta_shape, nm.get("version"), nm.get("untranslated")))
    print("  _meta.translated                        : %d -> %d "
          "(+this batch only: %d, lost: %d)"
          % (len(bm.get("translated", [])), len(nm.get("translated", [])),
             len(gained), len(lost)))
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
    if "--diff" in argv:
        return diff(argv[argv.index("--diff") + 1])
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
            problems.append("would overwrite a real translation: %s (%r)"
                            % (key, cur))
            continue
        check_batch(en_flat, (key, value), problems)
        planned.append(key)
        deep_set(de, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside the six sections moved, and _meta keeps its v1 shape.
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

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in sorted(DE) if after[k] == en_flat[k]]

    # G5b: _meta.translated is the v1 CLAIM "these keys are translated", and
    # tooling/check_i18n.py reads it in both directions — a claimed key that
    # still reads English is a false claim, and an unclaimed key that is no
    # longer English is a dishonest stub. So the claim moves in lockstep with
    # the bytes, for exactly the keys this batch translated. The 63 values kept
    # byte-identical on purpose (loanwords, ids, glue) stay UNCLAIMED, which is
    # the honest state for them. Nothing else in _meta moves, and the shape
    # stays v1 -- this is not a provenance upgrade.
    meta = de["_meta"]
    before_meta = dict(meta)
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
                 if k in before and after[k] == en_flat[k])
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
    if sorted(before_meta["translated"]) != before_meta["translated"]:
        print("REFUSING: _meta.translated was not sorted")
        return 1
    if set(meta) != set(before_meta):
        print("REFUSING: _meta field set changed")
        return 1

    by_section = {}
    for k in changed:
        sec = k.split(".")[0]
        by_section[sec] = by_section.get(sec, 0) + 1

    print("de chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in SECTIONS:
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / bare ids / symbols / glue):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run — no files written (pass --apply)")
        return 0

    with open(DE_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(de, indent=2, ensure_ascii=False))
        f.write("\n")
    print("wrote vanilla/locales/de.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
