#!/usr/bin/env python3
"""i18n it chunk-A: fill the account/account_net/settings/market/market_net/asset
sections of vanilla/locales/it.json that still hold the English string.

Scope: ONLY the six sections listed in SECTIONS. The chunk-B script owns the
rest of the untranslated it keys, so this script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from it.json, or one whose English master moved, is REFUSED.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route / asset symbol
                     as a WHOLE stay byte-verbatim;
  G3  pinned keys    settings.network_* / custom_placeholder / pending / dash /
                     theme_* ids, plus shell.brand and the two footer brands,
                     stay byte-verbatim;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside this batch keeps its exact prior value,
                     the key set is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an untranslated key must still equal en. Filling strings is
                     not verification, so the controller's v2 provenance /
                     verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte;
  G7  typography     no ASCII apostrophe leaks into a section it.json writes
                     with the typographic one, and no typographic apostrophe
                     leaks into a section it writes with the ASCII one. The two
                     conventions are PER SECTION and predate this pass (it.json
                     ships ' in account/asset/market/help/explorer/... and ’ in
                     about/createworker/debit/samet/ticket/wallet/...); this
                     batch matches each section rather than "fixing" it, so a
                     batch value may never mix the two inside one section.

Register: formal "Lei" (third person, imperative), matching the voice already
shipped in it.json (account.s5 "Inserisca la password per vedere il Suo
account", settings.retry "Riprovi", market.my_trades_hint "Inserisca un ordine
dai pannelli Acquisti/Venda", transfer.viewing_as "…sblocchi per agire come
Lei"). Vocabulary is reused verbatim from it.json wherever that dictionary has
already settled a word: wallet (m., loanword: "il wallet"), account (loanword),
asset (loanword), saldo, commissione (never "fee"), ordine, importo, blocco,
transazione, witness (loanword, invariant plural: "I witness"), comitato,
proxy, proposta, ticket, pool (f., loanword: "Le pool di liquidità"), swap,
stake, vesting, collaterale, smartcoin, chain (f., loanword: "la chain"),
precisione, publisher (loanword), feed, memo, brainkey (f.), nodo, rete,
book, exchange, settlement, bid, handshake, ping, DEX, HTLC, API, MPA, UIA,
FBA, NFT, PMA, MCR, CER, SMA, EMA, BB, PSAR, Δ. Nothing is invented where an
Italian crypto UI keeps the English word — the run prints every value that stays
identical to en, so a reviewer checks the list instead of guessing.

Typography: this batch's sections all use the ASCII apostrophe and a regular
space in it.json today (account 5 straight / 0 typographic, asset 10/0,
market 3/0, settings is 1 straight / 3 typographic so settings follows its own
majority). See G7.

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md §3.5) — and no prose number is invented.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_it_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_it_chunkA.py --apply         # writes it.json
  python3 tooling/apply_i18n_it_chunkA.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
IT_PATH = os.path.join(BASE, "it.json")

SECTIONS = ("account", "account_net", "settings", "market", "market_net",
            "asset")

# Keys whose value is a brand / persisted id / punctuation sentinel, not prose
# (rule 1). They are deliberately ABSENT from IT below so they keep the English
# bytes, and the verify pass re-asserts every one of them after the write.
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


APO_TYPO = u"’"
APO_ASCII = u"'"
EM = u"—"

# Multi-line Markdown bodies are written as line lists joined with "\n" so the
# line count (G4) is structural, not a count someone has to keep by hand. This
# batch fills no multi-line help body, but md() is kept so chunk B and later
# batches share the idiom.
def md(*lines):
    return "\n".join(lines)


IT = {
    # ---------------------------------------------------------------- account
    # Three words the dictionary already spells the Italian way, so they stay
    # byte-identical on purpose: "Asset", "Account", "Password " (see
    # KEPT_ENGLISH). "Login", "Membership", "Equity" and "Upgrade" are the same
    # loanwords it.json already ships elsewhere.
    "account.draw_network": u"Disegna rete",
    "account.page_total": u"Totale pagina ≈ ",
    "account.portfolio_page": u"Pagina %(page)s di %(pages)s",
    "account.prices_cover_this_page": (
        u"I prezzi coprono questa pagina — volti pagina per quotare più asset."
    ),
    "account.multisig_checking": u"Verifica delle autorità…",
    "account.multisig_open_txbuilder": u"Apra il costruttore di transazioni",
    "account.multisig_shared": (
        u"Account condiviso — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        u"Chiave singola — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"Account condiviso? Le proposte sono nella pagina proposte."
    ),
    "account.multisig_unavailable": (
        u"Autorità non disponibili — le proposte sono comunque nella pagina "
        u"proposte."
    ),
    "account.multisig_view_proposals": u"Vedi proposte",

    # The op-label table. The shape is the noun phrase the shipped labels
    # already use (account.op_asset_create "Creazione asset",
    # account.op_limit_cancel "Cancellazione ordine limite"), never a sentence.
    "account.op_assert_op": u"Asserzione",
    "account.op_asset_burn": u"Burn asset",
    "account.op_asset_issue": u"Emissione asset",
    "account.op_asset_settle": u"Settlement asset",
    "account.op_asset_update": u"Aggiornamento asset",
    "account.op_authority_create": u"Creazione autorità",
    "account.op_authority_delete": u"Eliminazione autorità",
    "account.op_authority_update": u"Aggiornamento autorità",
    "account.op_balance_claim": u"Riscossione saldo",
    "account.op_blind_from": u"Trasferimento da blind",
    "account.op_blind_to": u"Trasferimento a blind",
    "account.op_blind_transfer": u"Trasferimento blind",
    "account.op_claim_fees": u"Riscossione commissioni",
    "account.op_claim_pool": u"Riscossione pool",
    "account.op_collateral_bid": u"Bid collaterale",
    "account.op_committee_join": u"Adesione al comitato",
    "account.op_committee_update": u"Aggiornamento comitato",
    "account.op_custom_op": u"Operazione personalizzata",
    "account.op_deal_expired": u"Deal scaduto",
    "account.op_deal_repay": u"Rimborso deal",
    "account.op_deal_update": u"Aggiornamento deal",
    "account.op_debit_claim": u"Riscossione addebito diretto",
    "account.op_debit_create": u"Creazione addebito diretto",
    "account.op_debit_delete": u"Eliminazione addebito diretto",
    "account.op_debit_update": u"Aggiornamento addebito diretto",
    "account.op_execute_bid": u"Esecuzione bid",
    "account.op_fba_distribute": u"Distribuzione FBA",
    "account.op_fee_pool_fund": u"Finanziamento fee pool",
    "account.op_feed_producers_update": u"Aggiornamento produttori feed",
    "account.op_feed_publish": u"Pubblicazione feed",
    "account.op_global_settle": u"Settlement globale",
    "account.op_htlc_create": u"Creazione HTLC",
    "account.op_htlc_extend": u"Estensione HTLC",
    "account.op_htlc_redeem": u"Riscatto HTLC",
    "account.op_htlc_redeemed": u"HTLC riscattato",
    "account.op_htlc_refund": u"Rimborso HTLC",
    "account.op_issuer_update": u"Aggiornamento erogatore",
    "account.op_offer_accept": u"Accettazione credito",
    "account.op_offer_create": u"Creazione offerta di credito",
    "account.op_offer_delete": u"Eliminazione offerta di credito",
    "account.op_offer_update": u"Aggiornamento offerta di credito",
    "account.op_order_update": u"Aggiornamento ordine",
    "account.op_override_transfer": u"Trasferimento override",
    "account.op_params_update": u"Aggiornamento parametri globali",
    "account.op_pool_create": u"Creazione pool",
    "account.op_pool_delete": u"Eliminazione pool",
    "account.op_pool_deposit": u"Deposito pool",
    "account.op_pool_swap": u"Swap pool",
    "account.op_pool_update": u"Aggiornamento pool",
    "account.op_pool_withdraw": u"Prelievo pool",
    "account.op_proposal_create": u"Creazione proposta",
    "account.op_proposal_delete": u"Eliminazione proposta",
    "account.op_proposal_update": u"Aggiornamento proposta",
    "account.op_samet_borrow": u"Prestito Same-T",
    "account.op_samet_create": u"Creazione fondo Same-T",
    "account.op_samet_delete": u"Eliminazione fondo Same-T",
    "account.op_samet_repay": u"Rimborso Same-T",
    "account.op_samet_update": u"Aggiornamento fondo Same-T",
    "account.op_settle_cancel": u"Annullamento settlement",
    "account.op_smartcoin_update": u"Aggiornamento smartcoin",
    "account.op_ticket_create": u"Creazione ticket",
    "account.op_ticket_update": u"Aggiornamento ticket",
    "account.op_vesting_create": u"Creazione vesting",
    "account.op_vesting_withdraw": u"Prelievo vesting",
    "account.op_witness_join": u"Adesione come witness",
    "account.op_witness_update": u"Aggiornamento witness",
    "account.op_worker_create": u"Creazione worker",

    # History narration: impersonal third person ("Riscossi …"), the shape the
    # rest of the dictionary uses for a past event it did not witness itself
    # (vesting.balance_claimed_re_read_confirms_the_object_i "Saldo riscosso").
    "account.sum_account_create": u"Registrato %(name)s",
    "account.sum_account_transfer": u"Account trasferito a %(owner)s",
    "account.sum_account_update": u"Account aggiornato: %(account)s",
    "account.sum_asset_burn": u"Bruciati %(amount)s",
    "account.sum_asset_create": u"Creato asset %(symbol)s",
    "account.sum_asset_issue": u"Emessi %(amount)s a %(to)s",
    "account.sum_asset_settle": u"Settlement richiesto per %(amount)s",
    "account.sum_asset_update": u"Aggiornato asset %(asset)s",
    "account.sum_authorities": u"Autorità aggiornate per %(account)s",
    "account.sum_balance_claim": u"Riscossi %(amount)s",
    "account.sum_bid": u"Bid %(coll)s per %(debt)s",
    "account.sum_blind": (
        u"Trasferimento blind (%(in)s in, %(out)s out)"
    ),
    "account.sum_call_update": (
        u"Posizione aggiustata: %(coll)s collaterale, %(debt)s debito"
    ),
    "account.sum_claim_fees": u"Riscossi %(amount)s di commissioni",
    "account.sum_committee_create": (
        u"Diventato membro del comitato: %(account)s"
    ),
    "account.sum_committee_update": (
        u"Membro del comitato aggiornato: %(account)s"
    ),
    "account.sum_custom": u"Operazione personalizzata di %(account)s",
    "account.sum_deal_expired": u"Deal %(deal)s scaduto",
    "account.sum_deal_repay": u"Rimborsati %(amount)s sul deal %(deal)s",
    "account.sum_deal_update": u"Deal %(deal)s aggiornato",
    "account.sum_debit_claim": u"Riscossi addebito di %(amount)s",
    "account.sum_debit_create": (
        u"Autorizzato addebito di %(amount)s per %(to)s"
    ),
    "account.sum_debit_delete": (
        u"Eliminato permesso di addebito %(perm)s"
    ),
    "account.sum_debit_update": (
        u"Aggiornato addebito di %(amount)s per %(to)s"
    ),
    "account.sum_execute_bid": u"Bid eseguito: %(coll)s per %(debt)s",
    "account.sum_fee_pool_fund": (
        u"Fee pool di %(asset)s finanziato con %(amount)s"
    ),
    "account.sum_feed": (
        u"Feed pubblicato per %(asset)s da %(publisher)s"
    ),
    "account.sum_feed_producers": (
        u"Impostati %(n)s produttori feed per %(asset)s"
    ),
    "account.sum_fill": (
        u"Eseguito: pagati %(pays)s, ricevuti %(receives)s"
    ),
    "account.sum_global_settle": u"Settlement globale di %(asset)s",
    "account.sum_htlc_claimed": u"HTLC %(id)s riscosso",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(amount)s da %(from)s a %(to)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s esteso",
    "account.sum_htlc_redeem": u"HTLC %(id)s riscattato",
    "account.sum_htlc_refund": u"HTLC %(id)s rimborsato",
    "account.sum_issuer_update": (
        u"Nuovo erogatore per %(asset)s: %(issuer)s"
    ),
    "account.sum_offer_accept": (
        u"Presi in prestito %(amount)s contro %(coll)s (offerta %(offer)s)"
    ),
    "account.sum_offer_create": u"Creata offerta di credito in %(asset)s",
    "account.sum_offer_delete": u"Offerta %(offer)s eliminata",
    "account.sum_offer_update": u"Offerta %(offer)s aggiornata",
    "account.sum_order_cancel": u"Ordine %(order)s annullato",
    "account.sum_order_create": u"Offerti %(sell)s per almeno %(buy)s",
    "account.sum_order_update": u"Ordine %(order)s aggiornato",
    "account.sum_pool_create": u"Pool %(a)s / %(b)s creata",
    "account.sum_pool_delete": u"Pool %(pool)s eliminata",
    "account.sum_pool_deposit": (
        u"Messe in stake %(a)s + %(b)s nella pool %(pool)s"
    ),
    "account.sum_pool_swap": (
        u"Swappato %(sell)s → almeno %(buy)s nella pool %(pool)s"
    ),
    "account.sum_pool_update": u"Pool %(pool)s aggiornata",
    "account.sum_pool_withdraw": (
        u"Tolate dallo stake %(shares)s dalla pool %(pool)s"
    ),
    "account.sum_proposal_create": u"Proposta con %(n)s operazioni",
    "account.sum_proposal_delete": u"Proposta %(proposal)s eliminata",
    "account.sum_proposal_update": u"Proposta %(proposal)s approvata",
    "account.sum_samet_borrow": (
        u"Presi in prestito %(amount)s dal fondo %(fund)s"
    ),
    "account.sum_samet_create": u"Fondo SameT creato con %(amount)s",
    "account.sum_samet_delete": u"Fondo SameT %(fund)s eliminato",
    "account.sum_samet_repay": u"Rimborsati %(amount)s al fondo %(fund)s",
    "account.sum_samet_update": u"Fondo SameT %(fund)s aggiornato",
    "account.sum_settle_cancel": u"Settlement di %(amount)s annullato",
    "account.sum_smartcoin_update": u"Smartcoin %(asset)s aggiornata",
    "account.sum_ticket_create": u"Ticket %(amount)s creato",
    "account.sum_ticket_update": u"Ticket %(ticket)s aggiornato",
    "account.sum_transfer": (
        u"Trasferimento di %(amount)s da %(from)s a %(to)s"
    ),
    "account.sum_transfer_recv": u"Ricevuti %(amount)s da %(from)s",
    "account.sum_transfer_send": u"Inviati %(amount)s a %(to)s",
    "account.sum_upgrade": u"Upgrade di %(account)s",
    "account.sum_vesting_create": u"Messo in vesting %(amount)s per %(owner)s",
    "account.sum_vesting_withdraw": u"Prelevati %(amount)s in vesting",
    "account.sum_whitelist": u"Inserito %(account)s in lista",
    "account.sum_witness_create": u"Diventato witness: %(account)s",
    "account.sum_witness_update": u"Witness %(account)s aggiornato",
    "account.sum_worker_create": u"Worker \"%(name)s\" creato",

    # ------------------------------------------------------------ account_net
    "account_net.canvas_missing": (
        u"La canvas della rete non è disponibile in questa build; la tabella "
        u"qui sotto elenca comunque ogni linea."
    ),
    "account_net.class_credit": u"Credito",
    "account_net.class_credit_help": (
        u"Offerte di credito accettate e rimborsate."
    ),
    "account_net.class_debit": u"Addebito diretto",
    "account_net.class_debit_help": (
        u"Permessi di addebito diretto e prelievi."
    ),
    "account_net.class_htlc_help": (
        u"Contratti hash time-locked e i loro aggiornamenti."
    ),
    "account_net.class_override": u"Trasferimento override",
    "account_net.class_override_help": (
        u"Trasferimenti la cui commissione paga l'erogatore dell'asset."
    ),
    "account_net.class_transfer": u"Trasferimento",
    "account_net.class_transfer_help": (
        u"Trasferimenti diretti da account a account."
    ),
    "account_net.class_vesting_help": (
        u"Saldi vesting amministrati da terzi."
    ),
    "account_net.depth_1": u"1 hop",
    "account_net.depth_2": u"2 hop",
    "account_net.depth_label": u"Profondità",
    "account_net.detail_hint": (
        u"Tocchi una linea per il dettaglio; tocchi un account per aprirlo."
    ),
    "account_net.es_bad_account": (
        u"Quel nome non è un account su questa chain."
    ),
    "account_net.es_disabled": (
        u"L'indice community è spento. Lo attivi in Impostazioni per "
        u"disegnare questa mappa."
    ),
    "account_net.es_unavailable": (
        u"L'indice community non è raggiungibile adesso. Riprovi tra un "
        u"istante."
    ),
    "account_net.go": u"Disegna rete",
    "account_net.idle": u"Nulla ancora disegnato.",
    "account_net.intro": (
        u"Inserisca uno o più account per vedere a chi inviano, a chi prestano "
        u"e da cui prendono in prestito. Lettura dall'indice cronologia "
        u"community; non viene firmato né memorizzato nulla."
    ),
    "account_net.kind_flow": u"flusso",
    "account_net.kind_relation": u"relazione",
    "account_net.more_assets": u" + altri %(n)s",
    "account_net.need_class": u"Attivi almeno un tipo di linea da disegnare.",
    "account_net.need_seeds": u"Inserisca almeno un account da mappare.",
    "account_net.no_amount": u"nessun importo",
    "account_net.ring1_label": u"Anello 1",
    "account_net.ring2_label": u"Anello 2",
    "account_net.scanning": u"Lettura dell'indice community…",
    "account_net.seeds_label": u"Account da mappare",
    "account_net.stale_settings": (
        u"Le impostazioni di profondità o dei vicini sono cambiate — prema "
        u"Disegna rete."
    ),
    "account_net.status_credit_index": (
        u"%(n)s linee di credito risolte dall'indice (il loro oggetto offerta "
        u"o deal non è più in chain)"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s linee di credito saltate (offerta o deal non trovati in chain)"
    ),
    "account_net.status_depth": u"mappa %(depth)s",
    "account_net.status_edge_cap": u"prime %(n)s linee mostrate",
    "account_net.status_expanded": u"espansi: %(names)s",
    "account_net.status_expansion_scanned": (
        u"%(n)s operazioni indicizzate dalle espansioni"
    ),
    "account_net.status_expansion_truncated": (
        u"le scansioni delle espansioni sono troncate alle operazioni più "
        u"recenti"
    ),
    "account_net.status_graph": u"%(nodes)s account · %(edges)s linee",
    "account_net.status_node_cap": u"prime %(n)s controparti mostrate",
    "account_net.status_scanned": (
        u"%(scanned)s operazioni indicizzate da %(n)s account"
    ),
    "account_net.status_self": u"%(n)s trasferimenti a se stesso saltati",
    "account_net.status_shape": u"%(n)s voci illeggibili saltate",
    "account_net.status_truncated": (
        u"%(n)s operazioni più recenti per account"
    ),
    "account_net.status_unexpanded": (
        u"%(n)s controparti dirette non espanse"
    ),
    "account_net.status_unknown": u"non trovati: %(names)s",
    "account_net.title": u"Rete di account",
    "account_net.twin_amount": u"Importo",
    "account_net.twin_class": u"Tipo",
    "account_net.twin_count": u"Op",
    "account_net.twin_depth": u"Hop",
    "account_net.twin_empty": (
        u"Nessuna linea tra questi account nelle operazioni indicizzate "
        u"scansionate."
    ),
    "account_net.twin_from": u"Da",
    "account_net.twin_relation": u"Flusso/relazione",
    "account_net.twin_span": u"Primo → ultimo",
    "account_net.twin_summary": u"Vista a tabella (accessibile)",
    "account_net.twin_to": u"A",

    # --------------------------------------------------------------- settings
    "settings.confirm_back": u"Indietro",
    "settings.confirm_remove_action": u"Azione",
    "settings.confirm_remove_hide": (
        u"Nascondi questo nodo (resta nascosto finché non viene riaggiunto)"
    ),
    "settings.confirm_remove_result": u"Risultato",
    "settings.confirm_remove_switch": u"Il nodo attivo passa a %(node)s",
    "settings.confirm_remove_title": u"Rimuovere il nodo?",
    "settings.confirm_remove_unlist": u"Rimuova dalla mia lista",
    "settings.discover_note": (
        u"**Trovare nodi cerca su GitHub elenchi di nodi, poi testa ciò che "
        u"trova. GitHub e i nodi testati vedono il Suo indirizzo di rete. I "
        u"risultati sono candidati per la Sua verifica — non viene aggiunto "
        u"nulla automaticamente."
    ),
    "settings.geo_note": (
        u"*Le posizioni e i provider provengono da ipaddress.to (https, "
        u"nessuna chiave) — vede il Suo indirizzo quando richiesto; le "
        u"risposte restano in cache su questo dispositivo per 24 ore."
    ),
    "settings.hist_no": u"NO",
    "settings.hist_yes": u"SÌ",
    "settings.language_title": u"Lingua",
    "settings.sign_auto": (
        u"Automatico (estensione quando disponibile)"
    ),
    "settings.sign_badge": (
        u"Firma tramite estensione attiva — dettagli in Login"
    ),
    "settings.sign_badge_local": (
        u"Firma nella pagina — dettagli in Login"
    ),
    "settings.sign_browser": u"Firmi sempre in questa pagina",
    "settings.sign_ext": u"Usi sempre l’estensione",
    "settings.sign_ext_absent": (
        u"Nessuna estensione rilevata su questo dispositivo — le firme "
        u"avvengono in questa pagina."
    ),
    "settings.sign_ext_present": (
        u"Estensione rilevata su questo dispositivo."
    ),
    "settings.sign_guide": u"Come installare l’estensione",
    "settings.sign_mode_browser": (
        u"Le firme avvengono nella memoria di questa pagina."
    ),
    "settings.sign_mode_ext": (
        u"Le firme sono approvate nella finestra dell’estensione."
    ),
    "settings.sign_mode_ext_page": (
        u"Le firme restano nell’estensione — isolate dai siti web."
    ),
    "settings.sign_revoke": u"Revochi",
    "settings.sign_sites": u"Siti collegati",
    "settings.sign_sites_empty": (
        u"Ancora nessun sito approvato — le approvazioni compaiono qui con "
        u"revoca per sito."
    ),
    "settings.sign_sites_story_a": u"Esempio: un gioco di dadi su ",
    "settings.sign_sites_story_b": (
        u" chiede di giocare con il Suo account — approvandolo lo elenca "
        u"qui, legato solo a quell’account. Le firme chiedono comunque "
        u"conferma ogni volta. (Quel link non porta da nessuna parte — è un "
        u"esempio fittizio.)"
    ),
    "settings.sign_title": u"Firma",
    "settings.sign_warn": (
        u"Qualsiasi script che gira su questa pagina — inclusa una copia "
        u"ospitata compromessa — potrebbe leggere le Sue chiavi mentre sono "
        u"sbloccate. Faccia passare la firma dall’estensione, oppure usi una "
        u"copia che controlla Lei."
    ),
    "settings.th_chain": u"Chain",
    "settings.th_history": u"Storico",
    "settings.th_location": u"Posizione *",
    "settings.theme_dex_dark": u"DEX scuro",
    "settings.theme_title": u"Tema",
    "settings.theme_vanilla_light": u"Vanilla chiaro",

    # ----------------------------------------------------------------- market
    "market.adjust_button": u"Modifica",
    "market.confirm_adjust": u"Confermi la modifica",
    "market.discrete_fills": u"eseguiti",
    "market.discrete_no_fills": (
        u"Ancora nessun eseguito — inserisca un ordine o provi un'altra "
        u"coppia."
    ),
    "market.discrete_swaps": u"swap",
    "market.discrete_tip_block": u"Blocco",
    "market.discrete_tip_order": u"Ordine",
    "market.discrete_tip_price": u"Prezzo",
    "market.discrete_tip_time": u"Ora",
    "market.discrete_tip_volume_quote": u"Volume (quota)",
    "market.discrete_unavailable": (
        u"Indicatori non disponibili in Discrete."
    ),
    "market.discrete_volume": u"Volume discreto",
    "market.exchange_desk": u"Sezione Exchange",
    "market.fail_update": u"Aggiornamento non riuscito.",
    "market.flt_max_price": u"Prezzo max",
    "market.flt_min_price": u"Prezzo min",
    "market.loading_pool_map": u"Caricamento mappa…",
    "market.map_aria": (
        u"Rete di mercati. Le linee sono mercati che hanno avuto eseguiti "
        u"nelle ultime 24 ore."
    ),
    "market.map_connects": (
        u"Una linea collega due asset quando c'è stata un'operazione di "
        u"mercato nelle ultime 24 ore."
    ),
    "market.map_connects_fallback": (
        u"Una linea collega due asset quando esiste una pool finanziata. "
        u"L'attività di scambio su 24h non è confermata (storico non "
        u"disponibile) — mostra le pool finanziate."
    ),
    "market.map_edge_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s eseguiti/24h"
    ),
    "market.map_hops_empty": (
        u"Nessun mercato con eseguiti nelle ultime 24 ore attorno a queste "
        u"gambe."
    ),
    "market.map_hops_filtered": (
        u"Una linea è un mercato che ha avuto eseguiti nelle ultime 24 ore. "
        u"Mostra %(shown)s di %(total)s coppie (min %(min)s eseguiti/24h)."
    ),
    "market.map_hops_no_route": (
        u"Nessun percorso verso BTS attraverso mercati con eseguiti."
    ),
    "market.map_hops_note": (
        u"Una linea è un mercato che ha avuto eseguiti nelle ultime 24 ore. "
        u"%(pairs)s coppie mostrate."
    ),
    "market.map_leg_ok": u"{s} è collegato a BTS",
    "market.map_leg_orphan": (
        u"ATTENZIONE: {s} non ha un percorso di mercati con eseguiti!"
    ),
    "market.min_fills": u"Min eseguiti",
    "market.no_filter_match": (
        u"Nessun eseguito corrisponde a questi filtri."
    ),
    "market.settle_first100": (
        u"Mostra i primi 100 (limite 100 di get_settle_orders)"
    ),
    "market.settle_no_cancel": (
        u"Gli ordini di settlement non possono essere annullati — vengono "
        u"eseguiti al settlement (dopo il ritardo di force-settlement "
        u"dell'asset)."
    ),
    "market.stat_best_ask": u"Ask migliore",
    "market.stat_best_bid": u"Bid migliore",
    "market.tf_discrete": u"Discreto",
    "market.update_amount": u"Importo in vendita (nuovo totale) ",
    "market.update_amount_change": u"Variazione importo",
    "market.update_bad_amount": u"Inserisca un importo maggiore di zero.",
    "market.update_bad_expiry": u"Inserisca una scadenza nel futuro.",
    "market.update_bad_price": u"Inserisca un prezzo maggiore di zero.",
    "market.update_broadcasting": u"Trasmissione dell'aggiornamento…",
    "market.update_done": u"Ordine aggiornato",
    "market.update_expiry": u"Nuova scadenza ",
    "market.update_expiry_change": u"Scadenza (vecchia → nuova)",
    "market.update_no_change": (
        u"Nessuna modifica — modifichi prezzo, importo o scadenza."
    ),
    "market.update_price": u"Nuovo prezzo ",
    "market.update_price_change": u"Prezzo (vecchio → nuovo)",
    "market.update_review": u"Verifichi la modifica",
    "market.update_title": u"Modifica ordine",

    # ------------------------------------------------------------- market_net
    "market_net.asset_1_field": u"Asset 1 (qualsiasi gamba)",
    "market_net.asset_2_field": u"Asset 2 (qualsiasi gamba)",
    "market_net.band_title": u"Rete di mercati",
    "market_net.canvas_label": (
        u"Mappa della rete di mercati. Prema Invio per aprire il mercato."
    ),
    "market_net.clear_btn": u"Azzera",
    "market_net.col_last": u"Ultimo",
    "market_net.col_market": u"Mercato",
    "market_net.col_vol": u"vol 24h",
    "market_net.collapse": u"Comprimi",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s eseguiti/24h"
    ),
    "market_net.empty": u"Nessun mercato trovato per questo filtro.",
    "market_net.expand": u"Espandi",
    "market_net.list_btn": u"Elenca i mercati",
    "market_net.loading": u"Caricamento mercati…",
    "market_net.map_empty": u"Nessun mercato con volume recente.",
    "market_net.map_fallback": (
        u"%(pairs)s coppie · %(assets)s asset · eseguiti 24h non confermati"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s coppie · %(assets)s asset · eseguiti 24h"
    ),
    "market_net.map_ready": u"%(markets)s mercati · %(assets)s asset",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s mercati",
    "market_net.offline": (
        u"Rete non disponibile — mostra i mercati in cache. Riprovi quando la "
        u"connessione è attiva."
    ),
    "market_net.open_desk": u"Apra %(id)s",
    "market_net.prompt": (
        u"Tocchi un nodo per l'asset, una linea per il mercato."
    ),
    "market_net.ramp": u"Volume 24h: basso → alto",
    "market_net.ramp_fills": u"Eseguiti 24h: bassi → alti",
    "market_net.selector_title": u"Selettore mercati",
    "market_net.spark_label": u"Andamento a 7 giorni per %(id)s",
    "market_net.subtitle": (
        u"Migliori mercati per volume 24h. Scelga una riga per aprire la "
        u"sezione."
    ),
    "market_net.title": u"Mercati",
    "market_net.top_note": (
        u"Primi %(shown)s di %(probed)s testati — per volume 24h."
    ),
    "market_net.twin": u"Righe di mercato (%(n)s)",
    "market_net.twin_more": (
        u"Mostra %(shown)s di %(n)s mercati — restringa il filtro per "
        u"vederne meno."
    ),
    "market_net.verdict_full": u"%(markets)s mercati · %(assets)s asset",
    "market_net.verdict_no_path": (
        u"Nessun percorso di mercati con eseguiti tra %(a)s e %(b)s"
    ),
    "market_net.verdict_path": (
        u"%(a)s raggiunge %(b)s in %(n)s mercati con eseguiti"
    ),
    "market_net.verdict_star": u"Mercati che toccano %(s)s: %(n)s",
    "market_net.verdict_web": u"Mercati raggiungibili da %(s)s: %(n)s",

    # ------------------------------------------------------------------ asset
    "asset.cer_row": u"Tasso di cambio centrale (CER)",
    "asset.committee_fed_note": (
        u"Alimentato dal comitato: tutti i membri attivi del comitato possono "
        u"pubblicare."
    ),
    "asset.feed_history_title": u"Storico feed",
    "asset.history_capped": (
        u"Mostra i primi 8 publisher (limitato per velocità)…"
    ),
    "asset.history_days": u"Intervallo",
    "asset.history_exchange": u"Caricamento exchange + pool…",
    "asset.history_failed": u"Impossibile caricare lo storico feed.",
    "asset.history_loading": u"Caricamento storico feed…",
    "asset.invert_btn": u"Inverti",
    "asset.issue_memo_no_key": (
        u"Nessuna chiave memo in registro per questo account."
    ),
    "asset.issue_memo_warning": (
        u"Alleghi un memo — viene memorizzato on-chain in chiaro."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"L'erogatore predefinito è l'account osservato (%(id)s bloccato, il "
        u"Suo account sbloccato) — digiti qualsiasi erogatore che controlli. "
        u"Aperto da una pagina account, incolli qui quel nome account."
    ),
    "asset.loading_producers": u"Caricamento produttori…",
    "asset.multisig_body": (
        u"Se questo asset richiede più di un'approvazione, la firma diretta "
        u"fallisce — proponga invece la modifica e chieda ai comproprietari "
        u"di approvarla (op 23)."
    ),
    "asset.multisig_coowner_hint": (
        u"Comproprietario? Proponga la modifica nella pagina proposte e chieda "
        u"ai comproprietari di approvarla (op 23)."
    ),
    "asset.multisig_open_proposals": u"Vedi proposte",
    "asset.multisig_open_txbuilder": u"Apra il costruttore di transazioni",
    "asset.multisig_title": u"Erogatore condiviso? Proponga la modifica",
    "asset.new_issuer_field": u"Nuovo erogatore",
    "asset.no_history": (
        u"Nessuno storico in questo intervallo — i publisher pubblicano "
        u"raramente; provi 90g."
    ),
    "asset.no_producers": (
        u"Ancora nessun feed pubblicato — i produttori compaiono qui quando "
        u"pubblicano."
    ),
    "asset.owner_key_note": (
        u"Richiede la chiave active del proprietario dell'asset."
    ),
    "asset.plot_feeds": u"Tracci i feed",
    "asset.precision_field": u"Precisione (0–12)",
    "asset.producer_col": u"Produttore",
    "asset.producers_failed": u"Impossibile caricare i produttori.",
    "asset.producers_live_title": u"Produttori feed",
    "asset.producers_title": u"Produttori feed (op %(op)s)",
    "asset.publish_op19_title": u"Pubblichi feed (op %(op)s)",
    "asset.published_col": u"Pubblicato",
    "asset.viewing_notice": (
        u"Visualizza come %(name)s (%(id)s) — sblocchi per firmare."
    ),
    "asset.witness_fed_note": (
        u"Alimentato dai witness: tutti i witness attivi possono pubblicare."
    ),
}


# Keys inside this chunk's six sections whose Italian value is BYTE-IDENTICAL
# to English on purpose, listed here so the coverage of all untranslated keys
# is explicit and auditable instead of implied by their absence from IT. Each
# one is asserted to still equal en after the write, so a later pass cannot
# quietly turn a deliberate loanword into an unclaimed drift (and vice versa):
#
#   * persisted ids / punctuation sentinels (handled by PINNED),
#   * words Italian already spells the same way ("Asset", "Account", "Password",
#     "Volume", "Head", "Participation"),
#   * loanwords an Italian crypto UI keeps in English ("Login", "Membership",
#     "Equity", "Upgrade", "Exchange", "Bitasset", "Smartcoin", "MCR", "NFT",
#     "PMA", "UIA", "Op", "HTLC", "Vesting", "publisher", "swap", "hop",
#     "Handshake", "Ping", "Timeout", "Provider", "Log", "Total", "Offset",
#     "BB", "EMA", "PSAR", "SMA", "24h Δ", "Bid–Ask", "—"),
#   * pure glue: unit suffixes, " · " separator rows, arrow rows, "@ price",
#     and the account names + object id of the map seed placeholder.
KEPT_ENGLISH = {
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.custom_placeholder": u"wss://…",
    "settings.pending": u"…",
    "settings.dash": EM,
    "settings.theme_original_blue": u"original-blue",
    "settings.theme_light": u"light",
    "settings.theme_dark": u"dark",
    # Seconds glued to a number by the formatter: nothing to translate.
    "settings.age_s": u"%(n)ss",
    # "Handshake" and "Ping" name the protocol term and the command as an
    # Italian node table prints them; "Participation" is already the Italian
    # word for vote stake; "Timeout" and "Provider" are the same word.
    "settings.th_handshake": u"Handshake",
    "settings.th_head": u"Head",
    "settings.th_participation": u"Participation",
    "settings.th_ping": u"Ping",
    "settings.node_timeout": u"Timeout",
    "settings.th_provider": u"Provider *",
    "account.asset_th": u"Asset",
    "account.card_account": u"Account",
    "account.equity_tab": u"Equity",
    "account.gate_login": u"Login",
    "account.membership": u"Membership",
    "account.title": u"Account",
    "account.password_label": u"Password ",
    "account.upgrade_row_account": u"Account",
    "account.upgrade_row_upgrade": u"Upgrade",
    "market.chg_label": u"24h Δ",
    "market.discrete_tip_account": u"Account",
    "market.discrete_tip_volume": u"Volume",
    "market.log_label": u"Log",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_bidask": u"Bid–Ask",
    "market.stat_chg": u"24h Δ",
    "market.stat_empty": EM,
    "market.title": u"Exchange",
    "market.vol_label": u"Vol",
    "market.vol_log": u"Vol: Log",
    "asset.bitasset_row": u"Bitasset",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.offset_row": u"Offset",
    "asset.op_col": u"Op",
    "asset.orientation_note": u"%(m)s per %(b)s",
    "asset.smartcoin_row": u"Smartcoin",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    "asset.holders_account": u"Account",
    "asset.publisher_row": u"Publisher",
    "asset.history_pub": u"Publisher %(i)s/%(n)s…",
    "market_net.col_change": u"24h Δ",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "account_net.class_htlc": u"HTLC",
    "account_net.class_vesting": u"Vesting",
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ops · %(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s op · %(kind)s"
    ),
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
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
    """G1-G4 + G7 + punctuation hygiene for one key/value pair."""
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
            "line count changed: %s (en %d, it %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_apostrophe(batch, problems):
    """G7: a batch value may never mix the two apostrophe conventions inside
    one section, and a section the shipped dictionary writes with the ASCII
    apostrophe may not receive a typographic one (or the reverse).

    The per-section convention is read from the ALREADY SHIPPED translated
    values of it.json, not from a hand-written list, so the gate stays true if
    a later pass normalises the file. A section with no shipped evidence either
    way falls back to the ASCII majority of the dictionary.
    """
    it_flat = flat(load(IT_PATH))
    shipped = collections.defaultdict(collections.Counter)
    for key, value in it_flat.items():
        if key in batch or not isinstance(value, str):
            continue
        if APO_TYPO in value:
            shipped[key.split(".")[0]]["typo"] += 1
        if APO_ASCII in value:
            shipped[key.split(".")[0]]["ascii"] += 1
    for key, value in sorted(batch.items()):
        sec = key.split(".")[0]
        want = "typo" if shipped[sec]["typo"] > shipped[sec]["ascii"] else "ascii"
        other = APO_ASCII if want == "typo" else APO_TYPO
        if want == "typo" and APO_ASCII in value:
            problems.append(
                "G7: ASCII apostrophe in a %s section: %s" % (sec, key)
            )
        if want == "ascii" and APO_TYPO in value:
            problems.append(
                "G7: typographic apostrophe in an ASCII section: %s" % key
            )
        del other


def verify():
    """Structural re-proof of the shipped file against the en master."""
    it, en = load(IT_PATH), load(EN_PATH)
    d, e = flat(it), flat(en)
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(IT):
        if key not in d:
            bad.append("key missing from it.json: %s" % key)
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
    check_apostrophe(IT, bad)

    # Pinned ids are never in IT (they must keep the English bytes) but must
    # still equal en after the write.
    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(IT) if d.get(k) == e.get(k)]
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
        and k not in IT and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(IT) - len(same), len(IT)))
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
    meta = it.get("_meta", {})
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
    raw = open(IT_PATH, encoding="utf-8").read()
    it = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(it, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: it.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(it))
    before_meta = json.dumps(it["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(IT.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in it.json: %s" % key)
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
        deep_set(it, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # Coverage: IT + KEPT_ENGLISH must account for EVERY key of the six
    # sections, so a forgotten string shows up as a refusal instead of quietly
    # shipping English.
    both = sorted(set(IT) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (IT and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(IT) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in it.json: %s" % key)
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

    check_apostrophe(IT, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(it)
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
    meta = it["_meta"]
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
    added = sorted(k for k in IT
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

    print("it chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in SECTIONS:
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
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

    with open(IT_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(it, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/it.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())