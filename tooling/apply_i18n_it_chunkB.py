#!/usr/bin/env python3
"""i18n it chunk-B: fill every remaining `it` section of vanilla/locales/it.json
that chunk-A did not own (account, account_net, settings, market, market_net and
asset are chunk-A's and are REFUSED here as out of scope).

Scope: ONLY the sections listed in SECTIONS. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from it.json, or one whose English master moved, is REFUSED;
  * IT + KEPT_ENGLISH together must account for EVERY untranslated key of the
    listed sections, so a forgotten string is a refusal, never a silent English.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand and the two footer brands stay byte-verbatim;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master - so
                     the multi-line help articles (Markdown bodies with # headings
                     and [label](#/hash) links) keep their shape, only the prose
                     and the link LABELS are Italian;
  G5  untouched      every key outside this batch keeps its exact prior value,
                     the key SET is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an untranslated key must still equal en. Filling strings is
                     not verification, so the controller's v2 provenance /
                     verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte;
  G7  typography     no ASCII apostrophe leaks into a section it.json writes
                     with the typographic one, and no typographic apostrophe
                     leaks into a section it writes with the ASCII one - the
                     two conventions are PER SECTION and predate this pass
                     (it.json ships ' in account/asset/explorer/help/pool/... and
                     the typographic one in about/createworker/debit/samet/
                     ticket/wallet/...), so each batch value must match the
                     section it lands in.

Register: formal "Lei" (third person, imperative), matching the voice already
shipped in it.json (account.s5 "Inserisca la password per vedere il Suo
account", common.network_unavailable "Controlli Impostazioni -> Nodi e
riprovi", transfer.viewing_as "...sblocchi per agire come Lei"). Vocabulary is
reused verbatim from it.json wherever that dictionary has already settled a
word: wallet (m., loanword), account (loanword), asset (loanword), saldo,
commissione (never "fee"), ordine, importo, blocco, transazione, witness
(loanword, invariant plural), comitato, proxy, proposta, ticket, pool (f.,
loanword), swap, stake, vesting, collaterale, smartcoin, chain (f., loanword),
precisione, publisher (loanword), feed, memo, brainkey (f.), nodo, rete, book,
exchange, settlement, bid, short, house, listing, whitelist, blacklist, policy,
delta, plus the indicator names DEX/HTLC/API/MPA/UIA/FBA/NFT/PMA/MCR/MSSR/CER/
SMA/EMA/BB/PSAR/PnL/VWAP. Nothing is invented where an Italian crypto UI keeps
the English word - the run prints every value that stays identical to en, so a
reviewer checks the list instead of guessing.

High-risk keys (transfer, auth, unlockconfirm, vesting, createworker,
createaccount, htlc, samet, credit, debit, ticket, vote, txbuilder, approval,
proposal, wallet, gateway, i18n.*) render DUAL-LINE inside signing dialogs with
the English reference beside them, so their wording is deliberately plain and
literal: an amount, a destination, an irreversible action or a permission is
named the way the English names it, never softened.

The honesty surface (i18n.badge_*, i18n.risk_*, help.confidence_*, the
#/help/translation-limitations article and its heading) is TRANSLATED, not left
English: it is the warning an Italian reader gets about their own Italian, and
an Italian reader is exactly the person who needs it.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where a
translated string quotes a number the English quotes (1-%(total)s, 360px, 4K,
op 14/19/22/23/24/34/45, 1.10.N, 1.3.x, 1.19.x, 1.2.N) it keeps it
byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_it_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_it_chunkB.py --apply         # writes it.json
  python3 tooling/apply_i18n_it_chunkB.py --verify        # structural re-proof
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

# Every section EXCEPT chunk-A's six. Keeping the list as "everything but" is
# deliberate: a section added to it.json later is this batch's by default and
# shows up as an uncovered-key refusal, never as silently-shipped English.
CHUNK_A_SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
))


def _sections():
    """Section names present in en.json, minus chunk-A's six."""
    en = json.load(open(EN_PATH, encoding="utf-8"))
    names = set()

    def walk(d):
        for k, v in d.items():
            if k == "_meta":
                continue
            if isinstance(v, dict):
                names.add(k)
                walk(v)
    walk(en)
    return tuple(sorted(names - CHUNK_A_SECTIONS))


SECTIONS = _sections()

# Keys whose value is a brand, not prose (rule 1). They are deliberately
# ABSENT from IT below so they keep the English bytes, and the verify pass
# re-asserts every one of them after the write.
PINNED = (
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
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
NL = "\n"

# Multi-line Markdown bodies are written as line lists joined with "\n" so the
# line count (G4) is structural, not a count someone has to keep by hand.
def md(*lines):
    return NL.join(lines)


IT = {
    # ------------------------------------------------------------------ about
    # Typographic section (about ships ' in every shipped string).
    "about.dlg_bad_link": u"Numero di scambio non valido. Intervallo valido: 1–%(total)s.",
    "about.dlg_heading": u"Dialogo completo di costruzione",
    "about.dlg_heading_c": u"Dialogo completo di costruzione (%(total)s)",
    "about.dlg_no_match": (
        u"Nessuno scambio corrispondente. Azzeri la ricerca per vedere tutto."
    ),
    "about.dlg_no_reply": (
        u"Nessuna risposta registrata — l’invito successivo è arrivato subito "
        u"dopo."
    ),
    "about.dlg_noscript": (
        u"Questo archivio richiede JavaScript; lo stesso testo si trova in "
        u"docs/vanilla-ui-dialog.md nel repository sorgente."
    ),
    "about.dlg_search_clear": u"Azzera",
    "about.dlg_search_ph": u"Filtri gli scambi…",
    "about.dlg_showing": u"Mostra",
    "about.dlg_showing_c": u"Mostra %(shown)s / %(total)s",
    "about.dlg_unavailable": (
        u"Archivio del dialogo di costruzione non disponibile."
    ),
    "about.hero_lede": (
        u"Un wallet per la blockchain BitShares — mercati, account, governance "
        u"ed esplorazione — in semplici file web. Nessun framework, nessun "
        u"installer, nessun account da noi. Le Sue chiavi non lasciano mai "
        u"questo browser."
    ),
    # NOT a multi-line body: about.making_body is the About dialog's single
    # paragraph (the Markdown multi-line twin is help.topic_about-making_body).
    "about.making_body": (
        u"Quello che segue è la storia originale della costruzione: ogni invito "
        u"che ha creato questo wallet, da “acquire bitshares-ui” del 26 "
        u"settembre 2026 alla correzione del problema 1 del 3 ottobre, con le "
        u"risposte di chi lo ha costruito — conservate senza ritocco. Consigna "
        u"le decisioni su cui si regge questo wallet: rinunciare a un altro "
        u"uplift di React dopo il problema #3583 e la sua trappola delle mille "
        u"ore, così che questo wallet non dipenda da nulla che abbia un ciclo di "
        u"versione; firmare ogni transazione in locale come il vecchio wallet "
        u"invece di delegarla; tre temi con l’aspetto classico come default; "
        u"numeri in termini umani, mai interi grezzi della chain; layout "
        u"pensati prima per il telefono dalla prima tranche; e commissioni lette "
        u"dalla chain live, mai stimate. Lo legga come storia: ecco come è "
        u"stato costruito il wallet."
    ),
    "about.making_title": u"La costruzione di questo wallet",
    "about.s2_title": u"Negozi sul vero book ordini",
    "about.s3_body": (
        u"Il wallet che sostituisce è morto sotto un centinaio di pacchetti "
        u"scaduti e una toolchain che nessuno può riprodurre. Costruito per "
        u"evitare dipendenze con ciclo di versione: nessun framework, nessun "
        u"package manager, nessuna build — la cosa più piccola che possa "
        u"ancora girare in un browser tra dieci anni."
    ),
    "about.s3_title": u"Funziona per anni senza aggiornamenti",
    "about.s4_body": (
        u"Chi torna si sente subito a casa — le stesse pagine, gli stessi "
        u"pannelli e le stesse parole del wallet classico — mentre saldi, book "
        u"e stato della connessione si aggiornano sul posto. Ricerca "
        u"tollerante su mercati, account e asset, tre temi e layout che "
        u"funzionano da un telefono da 360px a una postazione di trading 4K."
    ),
    "about.s4_title": u"Le stesse pagine, aggiornamenti live",
    "about.s5_body": (
        u"La chain parla in interi; Lei non li vede mai. Ogni importo è alla "
        u"precisione del suo asset, ogni percentuale al suo valore reale e "
        u"ogni commissione è letta dalla chain live prima che Lei firmi."
    ),

    # ----------------------------------------------------------------- about UI

    # --------------------------------------------------------------- approval
    # Signing-adjacent: plain, literal wording.
    "approval.account": u"Account: ",
    "approval.approve": u"Approvi",
    "approval.approved": u"Approvata e trasmessa.",
    "approval.chain": u"Chain: ",
    "approval.close": u"Chiudi",
    "approval.denied": u"Negata.",
    "approval.deny": u"Neghi",
    "approval.expires_in": u"Scade tra ",
    "approval.load_failed": u"Impossibile caricare l'approvazione.",
    "approval.loading": u"Caricamento approvazione…",
    "approval.locked_note": (
        u"La sessione è bloccata — inserisca la password del Suo wallet per "
        u"approvare."
    ),
    "approval.no_fields": u"Nessun campo visualizzabile.",
    "approval.no_reply": u"Nessuna risposta dal firmatario.",
    "approval.no_runtime": u"Runtime dell'estensione mancante.",
    "approval.password": u"Password",
    "approval.remember": u"Ricordi questo account per questo sito",
    "approval.site_prefix": u"Sito: ",
    "approval.title": u"Approvi la firma",
    "approval.unknown_intent": u"Nessuna richiesta di approvazione trovata.",
    "approval.wallet_title": u"Questo wallet richiede una firma",

    # ------------------------------------------------------------------- auth
    "auth.multisig_body": (
        u"Questo wallet detiene una sola chiave. Gli account condivisi "
        u"richiedono proposte e approvazioni dei comproprietari, coordinate "
        u"tramite l'id di proposta (1.10.N). La consultazione è pubblica; solo "
        u"la firma richiede la password."
    ),
    "auth.multisig_open_proposals": u"Vedi proposte",
    "auth.multisig_open_txbuilder": u"Apra il costruttore di transazioni",
    "auth.multisig_step_approve": (
        u"I comproprietari approvano (op 23) nella pagina proposte, oppure "
        u"firmano insieme tramite il costruttore di transazioni."
    ),
    "auth.multisig_step_propose": (
        u"Proponga l'operazione (Trasferimento ha Invia/Propone; asset, "
        u"baratto e prestito rimandano alle proposte)."
    ),
    "auth.multisig_step_share": (
        u"Condivida l'id di proposta 1.10.N con i comproprietari."
    ),
    "auth.multisig_title": u"Account condivisi / multisig",

    # ----------------------------------------------------------------- barter
    "barter.confirm_barter_proposal_op_22": (
        u"Confermi la proposta di baratto (op %(op)s)"
    ),
    "barter.paid_by_suffix": u"): ",
    "barter.propose_barter_op_22": u"Proponga un baratto (op %(op)s)",
    "barter.step_build": u"Costruisci",
    "barter.step_preview": u"Anteprima",
    "barter.step_propose": u"Proponi",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"Anteprima dello swap atomico bilaterale. Prima l'anteprima, poi "
        u"PROPONE racchiude in una sola proposta i trasferimenti di entrambi "
        u"i lati (op %(op)s, pagatore commissione = Peer A)."
    ),
    "barter.uc_title": u"Sblocchi per firmare",

    # ----------------------------------------------------------------- borrow
    "borrow.account": u"Account",
    "borrow.adjust": u"Modifica",
    "borrow.adjust_position_op_3": u"Modifica posizione (op %(op)s)",
    "borrow.bids_no_cancel": (
        u"I bid non possono essere annullati una volta inseriti — vengono "
        u"eseguiti o scadono."
    ),
    "borrow.close_position": u"Chiuda posizione",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Le posizioni a margine prendono in prestito un bitasset contro "
        u"collaterale. Aggiungere collaterale o rimborsare il debito modifica "
        u"l'op %(op)s (call_order_update) sul Suo ordine call."
    ),
    "borrow.open_a_new_position_op_3": (
        u"Apra una nuova posizione (op %(op)s)"
    ),
    "borrow.repay_full": u"Rimborsi interamente",
    "borrow.settlement_bids_op_45": u"Bid di settlement (op %(op)s)",
    "borrow.title": u"Prestito",
    "borrow.uc_title": u"Sblocchi per firmare",

    # ----------------------------------------------------------------- common
    "common.page_n": u"Pagina %(n)s",
    "common.unknown_asset": u"Asset sconosciuto.",

    # ----------------------------------------------------------------- compat
    "compat.insecure_hint": (
        u"Questo indirizzo non è un contesto sicuro, quindi il browser non "
        u"espone WebCrypto. Il browser è aggiornato — serva la cartella su "
        u"https o localhost, oppure apra direttamente il file."
    ),

    # ---------------------------------------------------------------- confirm
    "confirm.memo": u"Memo",

    # ----------------------------------------------------------- createaccount
    # Typographic section.
    "createaccount.step_name": u"Nome",
    "createaccount.step_register": u"Registra",

    # ----------------------------------------------------------- createworker
    # Typographic section.
    "createworker.confirm_worker_op_34": u"Confermi il worker (op %(op)s)",
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Scriva un worker (op %(op)s). L’anteprima è live; la verifica cita "
        u"la commissione live, poi Firmi e invii trasmette direttamente l’op "
        u"%(op)s — i worker sono creati con op diretta, non con una proposta."
    ),
    "createworker.worker_preview_op_34": u"Anteprima del worker (op %(op)s)",

    # ----------------------------------------------------------------- credit
    "credit.borrower": u"Mutuatario",
    "credit.my_deals_borrower": u"I miei deal (mutuatario)",
    "credit.no_borrower_deals": (
        u"Ancora nessun deal come mutuatario — i deal compaiono dopo un "
        u"prestito contro un'offerta."
    ),
    "credit.uc_title": u"Sblocchi per firmare",

    # -------------------------------------------------------------- dashboard
    "dashboard.tagline": (
        u"Sfogli i mercati gratis — crei un wallet per negoziare."
    ),
    "dashboard.welcome": u"Negozi BTS con le chiavi che detiene",

    # ------------------------------------------------------------------ debit
    "debit.uc_order": u"Ordine",
    "debit.uc_title": u"Sblocchi per firmare",

    # ------------------------------------------------------------------ eslab
    "eslab.hint_donors": (
        u"Conteggi sulla finestra; i totali sono interi grezzi — divida per "
        u"la precisione dell’asset."
    ),

    # --------------------------------------------------------------- explorer
    "explorer.assets_mode_all": u"Tutti",
    "explorer.assets_mode_market": u"SmartCoins",
    "explorer.assets_mode_prediction": u"Previsione",
    "explorer.assets_mode_user": u"Emessi da utenti",
    "explorer.assets_of": u"di",
    "explorer.assets_showing": u"Mostra",
    "explorer.feed_cer_premium": (
        u"Premio del tasso di cambio centrale (CER) (stima secondo la regola "
        u"del publisher)"
    ),
    "explorer.feeds_of": u"di",
    "explorer.feeds_scanned_suffix": u"analizzati (primi 100 asset)",
    "explorer.feeds_showing": u"Mostra",
    "explorer.no_assets_match": u"Nessun asset corrisponde a “%(q)s”.",
    "explorer.raw_mark": u" (grezzo)",

    # -------------------------------------------------------- explorer_assets

    # ---------------------------------------------------------------- gateway
    "gateway.intro_a": (
        u"Invii le monete esterne all'indirizzo mostrato. Questa pagina non "
        u"invia nulla. "
    ),
    "gateway.intro_b": (
        u"I prelievi si completano in Trasferimento con un'anteprima live "
        u"della commissione."
    ),
    "gateway.raw_prefix": u"grezzo: ",

    # ------------------------------------------------------------------- htlc
    "htlc.hash_field": u"Hash esadecimale",
    "htlc.list_sub": (
        u"Bloccate fondi su un hash — il destinatario li riscatta con il "
        u"segreto prima della scadenza, altrimenti le vengono rimborsati. "
        u"Leggibile da chiunque; la password viene richiesta solo alla firma."
    ),
    "htlc.uc_title": u"Sblocchi per firmare",

    # -------------------------------------------------------------------- i18n
    # The honesty surface: what an Italian reader is told about their own
    # Italian. Translated, not left English.
    "i18n.badge_body": (
        u"Queste traduzioni sono state scritte da una macchina e non sono "
        u"state verificate da una persona. Le righe contrassegnate con * sulle "
        u"schermate di firma mostrano anche l'originale in inglese."
    ),
    "i18n.badge_details": u"Cosa significa",
    "i18n.badge_improve": u"Aiuti a migliorare questa traduzione",
    "i18n.badge_label": (
        u"Stato della traduzione: tradotta da una macchina, non verificata da "
        u"una persona"
    ),
    "i18n.risk_about_translations": u"Informazioni su queste traduzioni",
    "i18n.risk_show_english": (
        u"Mostra il riferimento inglese per questa riga"
    ),

    # ---------------------------------------------------------------- instant
    "instant.preview_balances_note": (
        u"Anteprima come %(name)s (%(id)s) — saldi non verificati. Sblocchi "
        u"per convalidare i Suoi prima di firmare."
    ),
    "instant.uc_title": u"Sblocchi per firmare",
    "instant.unlock_sign": u"Sblocchi e firmi",

    # ------------------------------------------------------- market sub-views
    "market_ind.count_capped": u"finestra troncata",
    "market_ind.count_note": u"%(count)s × %(bucket)s candele",
    "market_ind.count_partial": (
        u"%(actual)s di %(requested)s × %(bucket)s candele"
    ),

    # ------------------------------------------------------------------- misc

    # -------------------------------------------------------------------- nav
    "nav.credit": u"Credito",
    "nav.margin": u"Margine",
    "nav.markets": u"Mercati",
    "nav.pools": u"Pool",

    # ------------------------------------------------------------------- news
    "news.explorer_blocks_and_transactions": u"Esplori la chain",

    # ----------------------------------------------------------------- notify
    "notify.quote_label": u"Quota",

    # ------------------------------------------------------------------- menu
    "menu.blurb_labs": u"Strumenti potenti per il lavoro su chain e nodi.",
    "menu.blurb_personal": u"Chat, avvisi e le Sue impostazioni.",
    "menu.d_account_net": u"monitoraggio dei trasferimenti",
    "menu.d_xrates": u"Prezzi delle pool per ogni asset in BTS e oltre.",
    "menu.p_account_net": u"Rete di account",
    "menu.p_borrow": u"Prestito",
    "menu.p_xrates": u"Cross Rate",
    "menu.section_explore": u"Scoprire",
    "menu.section_labs": u"Laboratori",
    "menu.section_personal": u"Personale",

    # ------------------------------------------------------------------- pool
    "pool.asset_1_field": u"Asset 1 (qualsiasi gamba)",
    "pool.asset_2_field": u"Asset 2 (qualsiasi gamba)",
    "pool.asset_a_field": u"Asset A",
    "pool.asset_b_field": u"Asset B",
    "pool.clear_btn": u"Azzera",
    "pool.delete_not_empty": (
        u"Non vuota — %(legs)s deve leggere 0 prima dell'eliminazione."
    ),
    "pool.direct_hit": u"Ricerca diretta della pool — il pager è nascosto.",
    "pool.map_core_self": u"BTS è il token core di BitShares",
    "pool.min_swaps": u"Min swap",
    "pool.my_swaps_hint": (
        u" Ne avvii uno dal pannello Swap qui sopra — i Suoi swap in questa "
        u"pool sono elencati qui."
    ),
    "pool.no_filter_match": u"Nessuno swap corrisponde a questi filtri.",
    "pool.share_or_pool_hint": u"simbolo, 1.3.x, oppure pool 1.19.x",
    "pool.stake_autofill_hint": (
        u"Digiti un importo — l'altro si compila automaticamente al rapporto "
        u"della pool."
    ),
    "pool.stake_preview_bad": (
        u"Controlli gli importi — nessuna stima delle quote."
    ),
    "pool.stake_preview_need_both": (
        u"Inserisca entrambi gli importi per una stima delle quote."
    ),
    "pool.stake_preview_unavailable": (
        u"Stima delle quote non disponibile (offline)."
    ),
    "pool.stake_ratio_empty": (
        u"La pool è vuota — inserisca entrambi gli importi a mano."
    ),
    "pool.stake_ratio_row": u"Rapporto (spot)",
    "pool.stake_shares_row": u"Quote LP stimate",
    "pool.swap_desk": u"Sezione Swap",
    "pool.swap_mkt_preview_dash": u"Commissione di mercato (anteprima): —",
    "pool.swap_mkt_row": u"Commissione di mercato",
    "pool.swap_preview": u"Quotazione (anteprima): ",
    "pool.swap_preview_dash": u"Quotazione (anteprima): —",
    "pool.swaps_hint": (
        u" Gli swap compaiono dopo il primo scambio in questa pool — ne "
        u"avvii uno dal pannello Swap qui sopra."
    ),
    "pool.uc_action": u"Azione",
    "pool.uc_title": u"Sblocchi per continuare",

    # ------------------------------------------------------------ pool_detail
    "pool_detail.candle_capped": u"finestra troncata",
    "pool_detail.candle_count": (
        u"%(swaps)s swap · %(count)s × %(bucket)s candele"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s swap · %(actual)s di %(requested)s × %(bucket)s candele"
    ),
    "pool_detail.invert": u"Inverti",
    "pool_detail.invert_label": (
        u"Inverti l'orientamento del grafico (A per B / B per A)"
    ),
    "pool_detail.map_connects": (
        u"Una linea collega due asset quando esiste una pool finanziata e "
        u"c'è stata un'operazione nelle ultime 24 ore."
    ),
    "pool_detail.map_connects_fallback": (
        u"Una linea collega due asset quando esiste una pool finanziata. "
        u"L'attività di scambio su 24h non è confermata (storico non "
        u"disponibile) — mostra le pool finanziate."
    ),
    "pool_detail.map_min_swaps": u"(min %(min)s swap)",

    # --------------------------------------------------------------- pool_net
    "pool_net.canvas_label": (
        u"Mappa della rete di pool. Prema Invio per aprire BTS."
    ),
    "pool_net.collapse": u"Comprimi",
    "pool_net.direct": u"accoppiata con BTS",
    "pool_net.empty": u"Nessuna pool corrisponde a questo filtro.",
    "pool_net.expand": u"Espandi",
    "pool_net.hops": u"%(n)s hop verso BTS",
    "pool_net.legend": u"Brand",
    "pool_net.loading": u"Caricamento rete…",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pool · %(hops)s",
    "pool_net.offline": (
        u"Rete non disponibile — mostra lo scheletro incluso. Riprovi quando "
        u"la connessione è attiva."
    ),
    "pool_net.offline_empty": (
        u"Rete non disponibile — nessuno scheletro di pool in cache."
    ),
    "pool_net.orphan": u"orfana da BTS",
    "pool_net.partial": (
        u"Aggiornamento live incompleto — mostra le pool incluse."
    ),
    "pool_net.phys": u"Fisica",
    "pool_net.prompt": (
        u"Tocchi un nodo per l'asset, una linea per la pool."
    ),
    "pool_net.ramp": u"Dimensione delle pool: piccola → grande",
    "pool_net.ready": u"%(pools)s pool · %(assets)s asset",
    "pool_net.title": u"Rete di pool",
    "pool_net.twin": u"Righe di pool (%(n)s)",
    "pool_net.twin_more": (
        u"Mostra %(shown)s di %(n)s pool — restringa il filtro per vederne "
        u"meno."
    ),
    "pool_net.verdict_full": u"%(pools)s pool · %(assets)s asset",
    "pool_net.verdict_orphan": u"Nessun percorso tra %(a)s e %(b)s",
    "pool_net.verdict_path": u"%(a)s raggiunge %(b)s in %(n)s hop",
    "pool_net.verdict_star": u"Pool che toccano %(s)s: %(n)s",

    # ------------------------------------------------------------------ pools
    "pools.selector_title": u"Selettore di pool",

    # ------------------------------------------------------------ prediction
    "prediction.desk_suffix": u" sezione",
    "prediction.uc_title": u"Sblocchi per firmare",

    # --------------------------------------------------------------- proposal
    "proposal.confirm_proposal_create_op_22": (
        u"Confermi la creazione della proposta (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Confermi l'eliminazione della proposta (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"Elimini la proposta (op %(op)s)",
    "proposal.multisig_story": (
        u"Account condiviso? Un comproprietario propone, condivide l'id "
        u"1.10.N, gli altri approvano qui sotto. Il lavoro multi-operazione o "
        u"multi-dispositivo continua nel costruttore di transazioni."
    ),
    "proposal.open_txbuilder": u"Apra il costruttore di transazioni",
    "proposal.viewing_as": (
        u"Visualizza come %(name)s (%(id)s) — sblocchi per agire come Lei."
    ),

    # -------------------------------------------------------------- referrals

    # ------------------------------------------------------------------ samet

    # -------------------------------------------------------------------- seo
    "seo.desc_about": (
        u"Informazioni su questo wallet BitShares — chiavi locali, nessuna "
        u"registrazione, nessun tracciamento. Sfogli pure e firmi in locale."
    ),
    "seo.desc_account": (
        u"Vedi questo account BitShares — saldi, ordini e storico letti live "
        u"dalla chain. Nessun login richiesto."
    ),
    "seo.desc_account_net": (
        u"Mappa a chi un account invia, a chi presta e da cui prende in "
        u"prestito — letta dall'indice community. Nessun login richiesto."
    ),
    "seo.desc_dashboard": (
        u"Dashboard BitShares — saldi, mercati e attività della chain a colpo "
        u"d'occhio. Sfogli pure; le chiavi restano sul Suo dispositivo."
    ),
    "seo.desc_explorer": (
        u"Esplori blocchi, transazioni e asset di BitShares — dati live della "
        u"chain, sfogliabili senza login."
    ),
    "seo.desc_help": (
        u"Aiuto del wallet BitShares — guide per account, trading, voto e "
        u"recupero. Cominci da qui quando è bloccato."
    ),
    "seo.desc_login": (
        u"Sblocchi il Suo wallet BitShares locale — password, brainkey o "
        u"chiavi importate. Le chiavi non lasciano mai questo dispositivo."
    ),
    "seo.desc_market": (
        u"Negozi BTS contro USD sul book ordini BitShares — bid, ask e "
        u"storico live, firmati in locale sul Suo dispositivo."
    ),
    "seo.desc_markets": (
        u"Sfogli i mercati del book ordini BitShares per volume 24h e apra la "
        u"sezione di trading di qualsiasi coppia. Nessun login richiesto."
    ),
    "seo.desc_pools": (
        u"Sfogli le pool di liquidità BitShares — coppie, saldi e attività "
        u"letti live dalla chain. Nessun login richiesto."
    ),
    "seo.desc_transfer": (
        u"Invii asset BitShares a qualsiasi account. Verifichi ogni campo, poi "
        u"firmi in locale — le chiavi non lasciano mai il Suo dispositivo."
    ),
    "seo.desc_voting": (
        u"Voti i witness, i membri del comitato e i worker di BitShares. "
        u"Ogni scheda è firmata in locale sul Suo dispositivo."
    ),
    "seo.desc_xrates": (
        u"Ogni asset di pool quotato in BTS e oltre agli ultimi prezzi di "
        u"swap. Nessun login richiesto."
    ),
    "seo.title_about": u"Informazioni — BitShares Wallet",
    "seo.title_account": u"Account %(name)s — BitShares Wallet",
    "seo.title_account_net": u"Rete di account — BitShares Wallet",
    "seo.title_dashboard": u"Dashboard — BitShares Wallet",
    "seo.title_explorer": u"Explorer della blockchain — BitShares Wallet",
    "seo.title_help": u"Aiuto — BitShares Wallet",
    "seo.title_login": u"Login — BitShares Wallet",
    "seo.title_market": u"Exchange BTS/USD — BitShares Wallet",
    "seo.title_markets": u"Mercati — BitShares Wallet",
    "seo.title_pools": u"Pool di liquidità — BitShares Wallet",
    "seo.title_transfer": u"Invio fondi — BitShares Wallet",
    "seo.title_voting": u"Voto ai witness — BitShares Wallet",
    "seo.title_xrates": u"Cross Rate — BitShares Wallet",

    # ------------------------------------------------------------------ shell
    "shell.footer_ahead": u"%(n)s commit avanti di",
    "shell.footer_ahead_one": u"1 commit avanti di",
    "shell.footer_at_build": u"alla build del %(date)s",
    "shell.footer_behind": u"%(n)s commit indietro",
    "shell.footer_behind_one": u"1 commit indietro",
    "shell.footer_dahead": u"%(n)s avanti",
    "shell.footer_dbehind": u"%(n)s indietro",
    "shell.footer_diverged": u"divergente da",
    "shell.footer_offbranch": u"non su Master",
    "shell.footer_sync": u"sincronizzato con",

    # ----------------------------------------------------------------- splash
    "splash.card_dex_d": u"Compri e venda sul mercato aperto.",
    "splash.card_explore_d": u"Legga i blocchi e lo storico degli account.",
    "splash.card_pool_d": u"Guadagni una quota mettendo in pool due asset.",
    "splash.card_wallet_d": (
        u"Conservi le chiavi solo su questo dispositivo."
    ),
    "splash.cards_title": u"Negozi, metti in pool, esplora — cominci da qui",
    "splash.cta_exchange": u"Negozi sull'exchange",
    "splash.hero_sub": u"Le Sue chiavi. I Suoi fondi, on-chain.",
    "splash.hero_sub2": u"Sfogli i mercati gratis. Sblocchi solo per firmare.",
    "splash.hero_title": (
        u"Wallet BitShares nel Suo browser — nulla da installare."
    ),
    "splash.pulse_stale": u"— obsoleto",
    "splash.pulse_time": u"Ora del blocco head",
    "splash.pulse_title": u"Numeri live della chain",
    "splash.step1_d": u"Nessun login richiesto — prima sfogli la chain.",
    "splash.step1_t": u"Dò un'occhiata",
    "splash.step2_d": (
        u"Una brainkey viene generata su questo dispositivo. La annoti su carta."
    ),
    "splash.step2_t": u"Crei un wallet",
    "splash.step3_d": (
        u"Ordini limite, pool di liquidità e schede — tutto on-chain."
    ),
    "splash.step3_t": u"Negozi / pool / vota",
    "splash.topvol_unavailable": (
        u"Il volume dei principali mercati è offline — controlli Impostazioni "
        u"→ Nodi."
    ),
    "splash.trust_keys_d": (
        u"La firma avviene in locale sul Suo dispositivo. Nessun server vede "
        u"mai una password o una chiave."
    ),

    # ----------------------------------------------------------------- ticket

    # ------------------------------------------------------------------- tour
    "tour.away_note": (
        u"Sulla sezione Exchange — la apra per vedere questo evidenziato."
    ),
    "tour.s1_body": (
        u"Ogni pagina legge dati pubblici della chain senza login. Apra un "
        u"mercato per iniziare — la password viene richiesta solo alla firma."
    ),
    "tour.s1_title": u"Sfogli tutto gratis, firmi in locale",
    "tour.s3_body": (
        u"Candele di prezzo, volume e profondità più il menu degli indicatori: "
        u"overlay come SMA ed EMA, oscillatori come RSI, MACD e Stochastic. "
        u"Apra l’exchange per vederlo dal vivo."
    ),
    "tour.s3_title": u"Veda i grafici dei prezzi dal vivo",
    "tour.s4_body": (
        u"I pannelli Acquisti e Venda accettano qualsiasi numero per fare "
        u"pratica. Nulla lascia la Sua macchina finché non verifica e firma "
        u"con un wallet sbloccato. Apra l’exchange per provare."
    ),
    "tour.s4_title": u"Si alleni ad acquistare e vendere",

    # ------------------------------------------------------------------ trade
    "trade.tab_single": u"Singolo",
    "trade.uc_amount": u"Importo",
    "trade.uc_orders": u"Ordini",
    "trade.uc_price": u"Prezzo",
    "trade.uc_range": u"Intervallo di prezzo",
    "trade.uc_title": u"Sblocchi per continuare",
    "trade.uc_total": u"Totale da vendere",

    # --------------------------------------------------------------- transfer
    # High risk: plain, literal, dual-line next to the English reference.
    "transfer.confirm_proposal_title": u"Confermi la proposta (op %(op)s)",
    "transfer.enclosed_op_note": (
        u"Op inclusa: trasferimento (op %(op)s) — viene eseguito solo dopo le "
        u"approvazioni."
    ),
    "transfer.propose_notice_locked": (
        u"Il proponente predefinito è %(name)s (%(id)s) mentre è bloccato — "
        u"sblocchi per agire come Lei."
    ),
    "transfer.share_needs_to_amount": (
        u"Un link condivisibile richiede un destinatario e un importo."
    ),
    "transfer.uc_title": u"Sblocchi per continuare",
    "transfer.unlock_sign": u"Sblocchi e verifichi",

    # -------------------------------------------------------------- trollbox
    "trollbox.bytes_unit": u"byte",
    "trollbox.channel_row": u"Canale",
    "trollbox.fee": u"Commissione",
    "trollbox.language_row": u"Lingua",
    "trollbox.message_row": u"Messaggio",
    "trollbox.post_review_title": u"Verifichi il messaggio",
    "trollbox.size_row": u"Dimensione",
    "trollbox.unlock_post": u"Sblocchi e pubblichi",

    # ------------------------------------------------------------- txbuilder
    "txbuilder.link_proposals": u"Proposte",

    # --------------------------------------------------------- unlockconfirm
    "unlockconfirm.cancel": u"Indietro",
    "unlockconfirm.empty_password": u"Inserisca la password del Suo wallet.",
    "unlockconfirm.unlock_failed": u"Sblocco non riuscito.",
    "unlockconfirm.unlock_post": u"Sblocchi e pubblichi",

    # ---------------------------------------------------------------- vesting

    # ------------------------------------------------------------------- vote
    "vote.ballot_intro": (
        u"Il Suo stake elegge witness e comitato e finanzia i worker — tutti i "
        u"conteggi e le quote qui sotto sono letture live della chain."
    ),
    "vote.confirm_witness_update_op_21": (
        u"Confermi l'aggiornamento del witness (op %(op)s)"
    ),
    "vote.direct_note": (
        u"Voto pubblicato direttamente (voting_account %(id)s)."
    ),
    "vote.in_sync": (
        u"La slate di voto corrisponde alla chain — nulla da pubblicare."
    ),
    "vote.proxies_follow_another_account_s_slate_re": (
        u"I proxy seguono la slate di voto di un altro account — legga come "
        u"funziona il voto prima di impostarne uno."
    ),
    "vote.proxy_follows": (
        u" — il Suo stake segue questo account; la slate di voto qui sotto è "
        u"in sola lettura."
    ),
    "vote.retried_prefix": (
        u"Il nodo ha rifiutato la modalità proxy %(mode)s, quindi il voto è "
        u"stato pubblicato come proprio (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"Il nodo ha rifiutato la modalità proxy %(mode)s — nuovo tentativo "
        u"come proprio…"
    ),

    # ----------------------------------------------------------------- wallet

    # ------------------------------------------------------------------ xrate
    "xrate.add_btn": u"Aggiungi colonna",
    "xrate.base_pinned": (
        u"BTS è la colonna base e non può essere rimossa."
    ),
    "xrate.empty": (
        u"Nessun asset di pool entro 3 hop da BTS su questa chain."
    ),
    "xrate.intro": (
        u"Ogni asset di pool quotato all'ultimo suo swap, incrociato attraverso "
        u"il grafo delle pool. Non viene firmato né memorizzato nulla."
    ),
    "xrate.load_failed": u"Impossibile caricare i cross rate: ",
    "xrate.loading": u"Lettura delle pool…",
    "xrate.no_route_col": u"Nessun percorso verso %(sym)s entro 6 hop di pool.",
    "xrate.refresh_btn": u"Aggiorni i prezzi",
    "xrate.remove_btn": u"Rimuova ",
    "xrate.retry_btn": u"Riprovi",
    "xrate.show_all": u"Mostri tutti gli asset",
    "xrate.status": (
        u"%(pools)s pool · %(assets)s asset entro 3 hop · %(done)s di %(total)s "
        u"pool hanno un ultimo swap"
    ),
    "xrate.title": u"Cross Rate",
    "xrate.token_label": u"Aggiungi token di quotazione",
    "xrate.unknown_token": u"Nessun asset di pool denominato %(sym)s.",
    "xrate.unpriced": (
        u"Una gamba di questo percorso non ha ancora uno swap registrato."
    ),
}
# --------------------------------------------------------------------- help
# The help articles render beside the English master and are the one place a
# reader learns the app's rules, so the prose is plain factual Italian with no
# marketing tone. Headings are translated; every [label](#/hash) keeps its hash
# byte-verbatim (G4 re-checks the hash list against en).
HELP = {
    "help.about_link": u"Informazioni su questo wallet",
    "help.confidence_good": u"Buona",
    "help.confidence_high": u"Alta",
    "help.confidence_language": u"Lingua",
    "help.confidence_level": u"Affidabilità",
    "help.confidence_moderate": u"Media — verifichi",
    "help.docs_dev": u"Documentazione sviluppatore BitShares (docs.bitshares.dev)",
    "help.docs_org": u"Documentazione BitShares (docs.bitshares.org)",
    "help.elastic": u"Indice community (storico di terze parti)",
    "help.report_translation_link": (
        u"Segnali un problema di traduzione su GitHub"
    ),
    "help.sitemap_sections": u"Sezioni",
    "help.translation_confidence_heading": (
        u"Quanto è affidabile ciascuna lingua"
    ),
    # The Markdown twin of about.making_body: same story, five lines, with the
    # archive paragraph at the end. Line count is structural (G4).
    "help.topic_about-making_body": md(
        u"# La costruzione di questo wallet",
        u"Quello che segue è la storia originale della costruzione: ogni invito "
        u"che ha creato questo wallet, da “acquire bitshares-ui” del 26 "
        u"settembre 2026 alla correzione del problema 1 del 3 ottobre, con le "
        u"risposte di chi lo ha costruito — conservate senza ritocco.",
        u"Consigna le decisioni su cui si regge questo wallet: rinunciare a un "
        u"altro uplift di React dopo il problema #3583 e la sua trappola delle "
        u"mille ore, così che questo wallet non dipenda da nulla che abbia un "
        u"ciclo di versione; firmare ogni transazione in locale come il vecchio "
        u"wallet invece di delegarla; tre temi con l'aspetto classico come "
        u"default; numeri in termini umani, mai interi grezzi della chain; "
        u"layout pensati prima per il telefono dalla prima tranche; e "
        u"commissioni lette dalla chain live, mai stimate. Lo legga come "
        u"storia: ecco come è stato costruito il wallet.",
        u"# L'archivio completo dei dialoghi",
        u"La registrazione completa, scambio per scambio, si trova nella pagina "
        u"Informazioni (#/about). Apra lì la sezione Dialogo completo di "
        u"costruzione per sfogliare tutti gli scambi, filtrarli per parola "
        u"chiave o aprire in profondità uno scambio preciso con ?dialog=N.",
    ),
    "help.topic_about-making_text": (
        u"La storia della costruzione di questo wallet —"
    ),
    "help.topic_about-making_title": u"La costruzione di questo wallet",
    "help.topic_assets-feed_body": md(
        u"# Pubblicare feed di prezzo",
        u"Pubblichi il prezzo di settlement di un asset ancorato al mercato "
        u"dalla sezione Feed; il dialogo di conferma mostra la commissione "
        u"esatta prima che Lei firmi.",
    ),
    "help.topic_assets-feed_text": (
        u"Pubblichi feed di prezzo per gli asset ancorati al mercato che Lei "
        u"alimenta."
    ),
    "help.topic_assets-feed_title": u"Pubblicare feed di prezzo",
    "help.topic_assets-issue_body": md(
        u"# Emettere asset",
        u"Crei nuova fornitura di un asset che il Suo account controlla dalla "
        u"sezione Emissione; gli importi usano la precisione dell'asset e il "
        u"dialogo di conferma mostra la commissione esatta prima che Lei firmi.",
    ),
    "help.topic_assets-issue_text": (
        u"Crei nuova fornitura di un asset che controlla dalla sezione Emissione."
    ),
    "help.topic_assets-issue_title": u"Emettere asset",
    "help.topic_backups_body": md(
        u"# Salvatelo presto, salvalo due volte",
        u"Faccia un backup del Suo wallet locale prima di finanziarlo — un solo "
        u"backup di solito basta per andare avanti, ma lo conservi in almeno "
        u"due posti sicuri cui solo Lei può accedere.",
        u"In questo wallet non c'è alcun file di backup: la Sua brainkey È il "
        u"backup, e la passphrase da sola non ripristina nulla. Senza le parole "
        u"E la passphrase i Suoi fondi sono perduti. Non riponga mai la "
        u"passphrase accanto alle parole.",
        u"# La Sua brainkey è il backup",
        u"Se non ha mai importato chiavi grezze a mano, tutto il Suo wallet "
        u"deriva in modo deterministico da una sola brainkey — una sequenza di "
        u"parole. Annotare la brainkey salva ogni account e ogni fondo di quel "
        u"wallet.",
        u"La veda nel gestore wallet e la copi su carta, conservata separata da "
        u"qualsiasi cosa digitale. I file .bin del wallet di riferimento non "
        u"possono essere importati qui — il wallet lo dice a schermo e non "
        u"esiste alcun download di file.",
        u"# Avanzato: gerarchie di authority",
        u"Se usa authority a peso su più account invece delle semplici chiavi, "
        u"un backup delle sole chiavi può NON ripristinare l'accesso — conta "
        u"anche la struttura delle authority.",
        u"Rilegga l'articolo Permessi e annoti la configurazione completa delle "
        u"authority, non solo le parole.",
    ),
    "help.topic_browser_body": md(
        u"# Funzioni rilevate, mai nomi di marca",
        u"Questo wallet non chiede mai quale browser usa — testa le quattro "
        u"funzioni di piattaforma di cui ha davvero bisogno: WebSocket (dati "
        u"della chain), WebCrypto ( archivio delle chiavi), BigInt (calcoli "
        u"monetari) e lo storage locale (impostazioni). Il silenzio è un "
        u"esito positivo: nessun avviso su un browser moderno significa che "
        u"tutto è presente.",
        u"# La causa più comune: contesto non sicuro",
        u"I browser moderni espongono WebCrypto solo in contesti sicuri: pagine "
        u"https, localhost e file aperti. Lo stesso browser aggiornato servito "
        u"in http semplice (per esempio un indirizzo di rete locale) segnala "
        u"WebCrypto mancante — il browser è a posto, l'indirizzo no. Serva la "
        u"cartella su https o localhost, oppure apra direttamente index.html.",
        u"# Cosa funziona comunque",
        u"La consultazione funziona sempre: saldi, mercati, explorer e voto "
        u"leggono dati pubblici della chain senza alcuna funzione di wallet. "
        u"Solo la firma locale ha bisogno dell'elemento mancante. Chiudere "
        u"l'avviso lo nasconde su questa macchina; non blocca mai una pagina.",
    ),
    "help.topic_browser_text": (
        u"Quali browser eseguono il wallet e cosa significa l'avviso di "
        u"compatibilità."
    ),
    "help.topic_browser_title": u"Supporto dei browser",
    "help.topic_community_body": md(
        u"# Community",
        u"Le persone e i luoghi intorno a BitShares — homepage, codice, "
        u"explorer, forum e chat — si trovano nella pagina Community.",
    ),
    "help.topic_community_text": (
        u"Chat, forum, explorer e codice intorno a BitShares."
    ),
    "help.topic_htlc_text": (
        u"Swap bloccati su hash che pagano o rimborsano."
    ),
    "help.topic_menu_body": md(
        u"# Menu del sito",
        u"La pagina Menu elenca ogni schermata di questo wallet per sezione, "
        u"così ogni sezione è a un tocco di distanza.",
    ),
    "help.topic_menu_text": (
        u"Ogni pagina di questo wallet, raggruppata come la raggruppa il menu "
        u"di navigazione."
    ),
    "help.topic_menu_title": u"Menu del sito",
    # The 83-line sitemap: one line per page, link LABELS translated, link
    # HASHES byte-verbatim (G4 re-checks the hash list against en). The nine
    # group headings match the Italian menu.section_* names.
    "help.topic_sitemap_body": md(
        u"Ogni pagina di questo wallet, raggruppata come la raggruppa il menu "
        u"hamburger. Tutto ciò che ha un link si apre direttamente; le viste "
        u"dettagliate elencate sotto Pagine senza scheda di menu si aprono "
        u"dalle pagine madri.",
        u"# Wallet",
        u"- [Dashboard](#/)",
        u"- [Il mio account](#/account/me)",
        u"- [Account](#/accounts)",
        u"- [Trasferimento](#/transfer)",
        u"- [Fattura](#/invoice)",
        u"- [Vesting](#/vesting)",
        u"- [Wallet](#/wallet)",
        u"- [Cambia la password del wallet](#/wallet/password)",
        u"- [Crea wallet (brainkey)](#/create-wallet-brainkey)",
        u"- [Importa un account esistente](#/existing-account)",
        u"- [Registra un nuovo account](#/create-account)",
        u"- [Login](#/login)",
        u"- [Registrazione](#/registration)",
        u"- [Referral](#/referrals)",
        u"# Trading",
        u"- [Exchange](#/markets)",
        u"- [Trading istantaneo](#/instant-trade)",
        u"- [Pool di liquidità](#/pools)",
        u"- [Cross Rate](#/cross-rates)",
        u"- [Prestito](#/borrow)",
        u"- [Baratto](#/barter)",
        u"- [Deposito / Prelievo](#/deposit-withdraw)",
        u"- [Fondi Same-T](#/samet)",
        u"- [Spotlight](#/spotlight)",
        u"# Guadagni e protegga",
        u"- [Offerta di credito](#/credit-offer)",
        u"- [Addebito diretto](#/direct-debit)",
        u"- [HTLC](#/htlc)",
        u"- [Ticket](#/tickets)",
        u"- [Airdrop](#/airdrop)",
        u"- [Authority personalizzate](#/authorities)",
        u"- [Liste di account](#/lists)",
        u"# Governi",
        u"- [Voto](#/voting)",
        u"- [Proposte](#/proposals)",
        u"- [Crea un worker](#/create-worker)",
        u"- [Mercati di previsione](#/prediction)",
        u"# Scoprire",
        u"- [Explorer](#/explorer)",
        u"- [Asset](#/assets)",
        u"- [Crea asset](#/assets/create)",
        u"- [Emetti asset](#/assets/issue)",
        u"- [Pubblichi feed](#/assets/feed)",
        u"- [Commissioni di rete](#/explorer/fees)",
        u"- [Operazioni](#/ops)",
        u"- [Operazioni principali](#/top-ops)",
        u"- [Notizie](#/news)",
        u"# Explorer",
        u"- [Explorer (Blockchain)](#/explorer)",
        u"- [Asset](#/explorer/assets)",
        u"- [Pool](#/explorer/pools)",
        u"- [Account](#/explorer/accounts)",
        u"- [Witness](#/explorer/witnesses)",
        u"- [Comitato](#/explorer/committee)",
        u"- [Mercati](#/explorer/markets)",
        u"- [Commissioni](#/explorer/fees)",
        u"- [Feed](#/explorer/feeds)",
        u"# Laboratori",
        u"- [API Lab](#/api-lab)",
        u"- [ES Lab](#/es-lab)",
        u"- [Costruttore di transazioni](#/txbuilder)",
        u"- [Rete di account](#/account-network)",
        u"# Personale",
        u"- [Trollbox](#/trollbox)",
        u"- [Preferiti](#/favourites)",
        u"- [Avvisi di prezzo](#/alerts)",
        u"- [Aiuto](#/help)",
        u"- [Limiti della traduzione](#/help/translation-limitations)",
        u"- [Informazioni](#/about)",
        u"- [Community](#/community)",
        u"- [Impostazioni](#/settings)",
        u"# Pagine senza scheda di menu",
        u"Le varianti di registrazione, le sezioni account e mercato e le viste "
        u"dettagliate si aprono dalle pagine qui sopra o dai link altrove nel "
        u"wallet.",
        u"- [Registrazione locale](#/registration/local)",
        u"- [Registrazione Cloud](#/registration/cloud)",
        u"- [Pagina account di esempio](#/account/committee-account)",
        u"- [Sezione mercato di esempio](#/market/BTS_USD)",
        u"- [Pagina asset di esempio](#/asset/BTS)",
        u"- [Sezione pool di esempio](#/pools/1.19.66)",
        u"- [Panoramica del menu](#/menu)",
        u"Le viste dettagliate di una specifica offerta di credito, deal, "
        u"proposta, blocco, transazione, HTLC, mercato di previsione, "
        u"destinatario di trasferimento, fattura, gateway, scheda di "
        u"impostazioni, scheda dell'explorer o articolo di aiuto si aprono "
        u"dalle pagine madri e prendono un id o un nome nell'indirizzo.",
    ),
    "help.topic_sitemap_text": (
        u"Ogni pagina di questo wallet in una sola pagina: ogni pagina di menu "
        u"più i flussi e le viste dettagliate che non hanno una scheda di menu."
    ),
    "help.topic_sitemap_title": u"Mappa del sito",
    "help.topic_translation-limitations_body": md(
        u"Una traduzione contrassegnata come scritta da una macchina è stata "
        u"scritta da una macchina. Nessuno l'ha letta per verificare che dica "
        u"ciò che dice l'inglese — per questo ogni lingua tranne l'inglese "
        u"porta il contrassegno nell'intestazione di questo wallet. L'inglese "
        u"è il testo da cui le altre sono state tradotte, quindi non porta "
        u"nessun contrassegno.",
        u"",
        u"# Cosa significa il * su una riga",
        u"Un * su una riga di firma significa due cose insieme: la formulazione "
        u"è stata riempita da una macchina e l'inglese originale è a un tocco "
        u"di distanza. Tocchi il * e l'inglese compare sotto la riga esattamente "
        u"come lo memorizza il master inglese di questo wallet — lo stesso testo "
        u"da cui ogni altra lingua è stata tradotta, non una parafrasi.",
        u"",
        u"Il contrassegno segue la riga, non le parole contenute. Un * "
        u"contraddistingue un'intera riga tradotta, e il wallet sceglie quelle "
        u"righe secondo una regola fissa: ogni riga di una schermata di firma, "
        u"di azione irreversibile o di recupero — fino a un limite di lunghezza, "
        u"perché un paragrafo lungo è coperto da questo articolo invece — più "
        u"qualsiasi riga, ovunque si trovi, il cui inglese contiene un "
        u"avvertimento di pericolo. Quindi una riga che nomina solo un id o un "
        u"importo ne porta comunque uno (per esempio il campo A di un "
        u"trasferimento), mentre un paragrafo lungo che cita un id non lo "
        u"porta. Un valore grezzo della chain — un importo in una cella, un id "
        u"in una colonna, il simbolo di un asset — non è affatto una riga "
        u"tradotta, quindi non ne porta mai: dietro non c'è alcuna formulazione "
        u"inglese da confrontare.",
        u"",
        u"# Cosa significano i livelli di affidabilità",
        u"Ogni lingua che questo wallet distribuisce ha una valutazione, "
        u"elencata nella tabella qui sotto. Alta significa che la "
        u"formulazione segue da vicino l'inglese e si legge naturalmente. "
        u"Buona significa che è utilizzabile, anche se una frase può suonare "
        u"ancora goffa. Media significa leggerla come bozza e controllare "
        u"l'inglese prima di farvi affidamento.",
        u"",
        u"Tutte le valutazioni qui sotto sono la macchina che ha scritto le "
        u"strings che valuta il proprio lavoro; nessuno indipendente le ha "
        u"verificate. Una valutazione descrive che cosa è stato controllato "
        u"finora, per la lingua nel suo complesso e non riga per riga. "
        u"L'inglese stesso è il riferimento: è scritto a mano e ogni altra "
        u"lingua è tradotta da esso.",
        u"",
        u"# Come correggere una stringa",
        u"Le correzioni cominciano da una segnalazione. Dica in quale lingua "
        u"era la riga, fornisca la chiave che quella riga dichiara, incolli "
        u"l'inglese che avrebbe dovuto dire e proponga la formulazione che "
        u"userebbe al suo posto.",
        u"",
        u"- Una segnalazione per riga rende la correzione facile da applicare.",
        u"- Segnali prima le schermate di firma: una frase sbagliata in un "
        u"dialogo di conferma è il caso costoso.",
        u"- Usi il link in fondo a questo articolo. Apre una segnalazione già "
        u"etichettata per le traduzioni nel tracker di questo progetto, quindi "
        u"non c'è nulla da riscrivere.",
        u"",
        u"# Le correzioni sono l'unica strada verso la revisione umana",
        u"Nient' altro porta una stringa fuori dallo stato « scritta da una "
        u"macchina»: non quanto spesso una lingua viene usata, non una seconda "
        u"macchina che concorda con la prima, non una memoria di traduzione. "
        u"Una stringa diventa riletta da una persona quando qualcuno la legge "
        u"nella propria lingua e la accetta, e una riga è riletta solo per la "
        u"lingua che è stata davvero controllata.",
        u"",
        u"Finché resta così, il contrassegno rimane dov'è. Una traduzione che "
        u"nessuno ha letto è comunque meglio di nessuna traduzione, ma non è la "
        u"stessa cosa di una che una persona ha sottoscritto.",
    ),
    "help.topic_translation-limitations_text": (
        u"Le traduzioni scritte da una macchina sono contrassegnate; il "
        u"riferimento inglese è sempre a un tocco di distanza. Ci aiuti a "
        u"correggere una riga."
    ),
    "help.topic_translation-limitations_title": u"Limiti della traduzione",
    "help.topic_voting_text": (
        u"Voti witness, comitato, worker — oppure deleghi a un proxy."
    ),
    "help.topic_wallets_body": md(
        u"# Un'app web con un archivio locale",
        u"Questa applicazione gira nel Suo browser e parla con un nodo della "
        u"chain, che fa da gateway verso la rete. Tutto ciò che è segreto "
        u"resta nell'archivio locale del Suo browser.",
        u"# Nessun login cloud",
        u"Questo wallet non ha un login con nome utente e password: ogni wallet "
        u"qui è locale a un solo browser. Per usare il Suo account su un "
        u"browser o un computer nuovo, riparta dalla stessa brainkey — non "
        u"esistono credenziali che lo aprono da sole ovunque esse vengano da.",
        u"# Wallet locale",
        u"Un wallet locale è un database dentro un browser specifico. Non la "
        u"segue su un altro computer o browser a meno che non porti con sé la "
        u"brainkey e non la importi.",
        u"Legga l'articolo Backup prima di fare affidamento su un wallet locale "
        u"per fondi reali.",
        u"# Disciplina della password",
        u"La password cifra l'archivio. Password corte o riutilizzate cedono "
        u"alla deducibilità; una passphrase unica annotata su carta no.",
        u"Cambiare la password ricifra tutto — verifichi prima quella attuale, "
        u"poi confermi che il wallet si sblocchi ancora prima di andarsene.",
    ),
}
# Keys whose Italian value is BYTE-IDENTICAL to English on purpose, listed here
# so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from IT. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift (and vice versa):
#
#   * brands (shell.brand, the two footer brands — PINNED),
#   * words Italian already spells the same way ("Account", "Asset", "Base",
#     "Info", "Forum", "Homepage", "Live", "max", "no", "Low", "Policy",
#     "Slippage", "Spot", "Stake", "Spread", "Volume", "Delta", "ID", "URL",
#     "Community", "Dashboard", "Menu", "Wallet", "Password", "Owner", "Blacklist",
#     "Whitelist", "Listing", "Head", "Blockchain", "Exit"),
#   * loanwords an Italian crypto UI keeps in English ("DEX", "HTLC", "API",
#     "ES Lab", "Airdrop", "Spotlight", "Trollbox", "Trollbox", "Escrow",
#     "brainkey", "smartcoin", "pool", "swap", "stake", "vesting", "ticket",
#     "proposal" as Deal, "house", "short", "lock", "whitelist", "Exchange",
#     "Feed", "Memo", "MPA", "UIA", "NFT", "CER", "MCR", "MSSR", "PnL", "VWAP",
#     "Δ", "Settle", "Settled", "Settlement", "Bitasset", "smartcoin", "Priority"),
#   * indicator acronyms (BB, EMA, PSAR, SMA) and numeric sentinels (—),
#   * pure glue: the transfer pair delimiter "): ", unit suffixes, " · " separator
#     rows, arrow rows, "@ price", the bare example payload "alice,10\nbob,2.5"
#     and the pair-symbol hint.
KEPT_ENGLISH = {
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "apilab.title": u"API Lab",
    "asset_ops.title": u"Asset",
    "assets_feed.s1": EM,
    "swap.title": u"Swap",
    "explorer_assets.s1": EM,
    "explorer_assets.title": u"Asset",
    "eslab.title": u"ES Lab",
    "auth.login": u"Login",
    "auth.password": u"Password ",
    "createaccount.account": u"Account",
    "createaccount.password": u"Password ",
    "createaccount.step_brainkey": u"Brainkey",
    "createworker.owner": u"Owner",
    "createworker.url": u"URL",
    "credit.account": u"Account",
    "credit.asset": u"Asset",
    "credit.deal": u"Deal",
    "credit.deal_2": u"Deal ",
    "credit.delta": u"Delta",
    "credit.no": u"no",
    "debit.spotlight_title": u"Spotlight",
    "explorer.asset_prefix": u"Asset ",
    "explorer.asset_title": u"Asset",
    "explorer.confirm_asset": u"Asset",
    "explorer.core_suffix": u" (core)",
    "explorer.fee_pool": u"Fee pool",
    "explorer.feed_badge_live": u"LIVE",
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.head_prefix": u"Head #",
    "explorer.id_row": u"ID",
    "explorer.info_h": u"INFO",
    "explorer.markets_sort_vol_asc": u"Volume ↑",
    "explorer.markets_sort_vol_desc": u"Volume ↓",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.price_base": u"base ",
    "explorer.short": u"Short: ",
    "explorer.stat_tps": u"Trx/s",
    "explorer.state_live": u"Live",
    "explorer.tab_blocks": u"Blockchain",
    "explorer.th_feed": u"Feed",
    "explorer.th_mssr": u"MSSR",
    "explorer.th_settlement": u"Settlement",
    "explorer.th_witness": u"Witness",
    "explorer.tx_prefix": u"Tx ",
    "explorer.witness_row": u"Witness",
    "gateway.health_ok": u"ok ",
    "htlc.hash_label": u"Hash: ",
    "htlc.preimage_label": u"Preimage",
    "htlc.preimage_ph": u"preimage",
    "htlc.title": u"HTLC",
    "i18n.badge_chip": u"i18n",
    "instant.no": u"No",
    "instant.per_mid": u" per ",
    "market_book.spread_prefix": u"Spread ",
    "market_book.title": u"Exchange",
    "market_charts.title": u"Exchange",
    "market_orders.tape_max": u"max",
    "market_orders.title": u"Exchange",
    "misc.account": u"Account",
    "misc.asset": u"Asset",
    "misc.blacklist": u"Blacklist",
    "misc.id": u"ID",
    "misc.listing": u"Listing",
    "misc.no": u"no",
    "misc.whitelist": u"Whitelist",
    "nav.account": u"Account",
    "nav.dashboard": u"Dashboard",
    "nav.exchange": u"Exchange",
    "notify.base_label": u"Base",
    "menu.p_airdrop": u"Airdrop",
    "menu.p_apilab": u"API Lab",
    "menu.p_community": u"Community",
    "menu.p_dashboard": u"Dashboard",
    "menu.p_eslab": u"ES Lab",
    "menu.p_exchange": u"Exchange",
    "menu.p_htlc": u"HTLC",
    "menu.p_login": u"Login",
    "menu.p_spotlight": u"Spotlight",
    "menu.p_trollbox": u"Trollbox",
    "menu.p_vesting": u"Vesting",
    "menu.p_wallet": u"Wallet",
    "menu.section_wallet": u"Wallet",
    "menu.title": u"Menu",
    "pool.pool_row": u"Pool",
    "pool.slippage_field": u"Slippage %",
    "pool.slippage_row": u"Slippage",
    "pool.spot_row": u"Spot",
    "pool.stake_link": u"Stake",
    "pool.stake_title": u"Stake / unstake",
    "pool.stake_unstake_col": u"Stake/Unstake",
    "pool.swap_stake_col": u"Swap/Stake",
    "pool_net.col_a": u"Asset 1",
    "pool_net.col_b": u"Asset 2",
    "pool_net.col_pool": u"Pool",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "prediction.asset": u"Asset",
    "prediction.hdr_asset": u"Asset",
    "prediction.house": u"House",
    "prediction.pmo_governance": u"Governance",
    "prediction.pnl": u"PnL",
    "prediction.settle": u"Settle",
    "prediction.settled": u"Settled",
    "prediction.settlement": u"Settlement",
    "proposal.account": u"Account",
    "proposal.active_suffix": u" (active): ",
    "proposal.id": u"ID",
    "proposal.inner_ticket_0": u"Account",
    "proposal.inner_ticket_2": u"Asset",
    "proposal.inner_transfer_2": u"Asset",
    "proposal.lock": u"Lock",
    "proposal.memo": u"Memo",
    "proposal.no": u"no",
    "proposal.op_7": u"whitelist",
    "proposal.owner_suffix": u" (owner): ",
    "proposal.ticket": u"Ticket",
    "referrals.account": u"Account ",
    "referrals.referrer": u"Referrer",
    "referrals.registrar": u"Registrar",
    "samet.account": u"Account",
    "samet.asset": u"Asset",
    "samet.delta": u"Delta",
    "samet.owner": u"Owner",
    "shell.dashboard": u"Dashboard",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    "shell.menu": u"Menu",
    "splash.card_dex_t": u"Exchange",
    "splash.card_explore_t": u"Explorer",
    "splash.card_wallet_t": u"Wallet",
    "ticket.account": u"Account",
    "ticket.airdrop": u"Airdrop",
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "ticket.asset": u"Asset",
    "ticket.id": u"ID",
    "ticket.owner": u"Owner",
    "ticket.ticket": u"Ticket",
    "trade.no": u"No",
    "transfer.asset_label": u"Asset ",
    "transfer.password_label": u"Password ",
    "trollbox.status_live": u"Live",
    "trollbox.title": u"Trollbox",
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "txbuilder.chain_prefix": u"Chain: ",
    "unlockconfirm.password": u"Password",
    "vesting.account": u"Account",
    "vesting.asset": u"Asset",
    "vesting.id": u"ID",
    "vesting.policy": u"Policy",
    "vesting.title": u"Vesting",
    "vesting.vesting": u"Vesting",
    "vote.account_row": u"Account",
    "vote.fee_core": u" (core)",
    "vote.password_label": u"Password ",
    "vote.proxy_prefix": u"Proxy: ",
    "vote.proxy_row": u"Proxy",
    "vote.url": u"URL",
    "vote.witness": u"Witness",
    "wallet.brainkey": u"Brainkey",
    "wallet.password": u"Password",
    "wallet.title": u"Wallet",
    "xrate.asset_col": u"Asset",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
    "help.community_title": u"Community",
    "help.forum": u"Forum",
    "help.homepage": u"Homepage",
    "help.link_exp_lovable": u"BitShares Explorer (lovable.app)",
    "help.topic_api-lab_title": u"API Lab",
    "help.topic_blockchain_title": u"Blockchain",
    "help.topic_community_title": u"Community",
    "help.topic_dashboard_title": u"Dashboard",
    "help.topic_es-lab_title": u"ES Lab",
    "help.topic_spotlight_title": u"Spotlight",
}
IT.update(HELP)

# --------------------------------------------------------------------------
# helpers + gates
# --------------------------------------------------------------------------
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

    print("it chunk-B: %d planned, %d differ from en, %d intentionally identical"
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