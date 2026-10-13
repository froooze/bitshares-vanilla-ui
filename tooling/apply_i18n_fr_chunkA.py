#!/usr/bin/env python3
"""i18n fr chunk-A: fill the account/account_net/settings/market/market_net/asset
sections of vanilla/locales/fr.json that still hold the English string.

Scope: ONLY the six sections listed in SECTIONS. The chunk-B script owns the
rest of the untranslated fr keys, so this script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from fr.json, or one whose English master moved, is REFUSED.

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
                     the key SET is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an untranslated key must still equal en. Filling strings is
                     not verification, so the controller's v2 provenance /
                     verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Register: formal "vous", matching the voice already shipped in fr.json
(account.s5 "Saisissez votre mot de passe…", settings.discover_none
"Aucun nouveau nœud trouvé…", barter.viewing_as "déverrouillez pour agir avec
votre compte"). Vocabulary is reused verbatim from fr.json wherever that
dictionary has already settled a word: portefeuille (wallet), compte
(account), solde (balance), actif (asset), carnet d'ordres (orderbook), ordre
limite (limit order), frais (fee), opération, transaction, bloc, mémo,
brainkey, témoin (witness), comité, worker, proxy, slate, vesting, proposition,
ticket, HTLC, pool, swap, collatéral, smartcoin, précision, part, nœud (node),
chaîne (chain), flux (feed), règlement (settlement), passerelle (gateway),
parrain (referrer), registrar, faucet. Nothing is invented where a French
crypto UI keeps the English word (DEX, HTLC, BitShares, BTS, API, Memo, Swap,
Proxy, Smartcoin, URL, Pools, Pool, Airdrop, Spotlight, Trollbox, Brainkey,
Ticket, Worker, Vesting, Spot, Slippage, PnL, House) — the run prints every
value that stays identical to en, so a reviewer checks the list instead of
guessing.

Typography: this batch's sections (account, account_net, settings, market,
market_net, asset) all use the ASCII apostrophe and a REGULAR space before the
high punctuation in fr.json today (account 25 straight / 0 typographic, asset
14/0, settings 6/0, market 13/0), so nothing here introduces the typographic
apostrophe or U+00A0. Chunk B keeps the other convention per section.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_fr_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_fr_chunkA.py --apply         # writes fr.json
  python3 tooling/apply_i18n_fr_chunkA.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
FR_PATH = os.path.join(BASE, "fr.json")

SECTIONS = ("account", "account_net", "settings", "market", "market_net",
            "asset")

# Keys whose value is a brand / persisted id / punctuation sentinel, not prose
# (rule 1). They are deliberately ABSENT from FR below so they keep the English
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


EM = u"—"

# Multi-line Markdown bodies are written as line lists joined with "\n" so the
# line count (G4) is structural, not a count someone has to keep by hand.
def md(*lines):
    return "\n".join(lines)


FR = {
    # ---------------------------------------------------------------- settings
    # settings.network_* / theme_* / pending / dash / custom_placeholder are
    # PINNED: persisted ids and sentinels, never translated.
    "settings.hist_yes": u"OUI",
    "settings.hist_no": u"NON",
    "settings.geo_note": (
        u"*Les localisations et fournisseurs viennent d'ipaddress.to (https, "
        u"aucune clé) — il voit votre adresse lorsqu'on le sollicite ; les "
        u"réponses sont mises en cache sur cet appareil pendant 24 heures."
    ),
    "settings.th_chain": u"Chaîne",
    # "Handshake" / "Ping" stay English: they name the protocol term and the
    # command as a French node table prints them (de.json and es.json do the
    # same). Flagged in the identical-to-en list, not silently claimed.
    "settings.th_head": u"Tête",
    "settings.th_history": u"Historique",
    "settings.th_location": u"Localisation *",
    # "Participation" is already the French word for vote stake: identical.
    "settings.th_provider": u"Fournisseur *",
    "settings.confirm_back": u"Retour",
    "settings.confirm_remove_hide": (
        u"Masquer ce nœud (reste masqué jusqu'à ce qu'il soit réajouté)"
    ),
    "settings.confirm_remove_result": u"Résultat",
    "settings.confirm_remove_switch": u"Le nœud actif bascule vers %(node)s",
    "settings.confirm_remove_title": u"Retirer le nœud ?",
    "settings.confirm_remove_unlist": u"Retirer de ma liste",
    "settings.theme_title": u"Thème",
    "settings.theme_classic": u"Classique",
    "settings.theme_vanilla_light": u"Vanilla clair",
    "settings.theme_dex_dark": u"DEX sombre",
    "settings.discover_note": (
        u"**Trouver des nœuds cherche des listes de nœuds sur GitHub, puis "
        u"sonde ce qu'il trouve. GitHub et les nœuds sondés voient votre "
        u"adresse réseau. Les résultats sont des candidats à votre examen — "
        u"rien n'est ajouté automatiquement."
    ),
    # "%(n)ss" is a unit suffix glued to a number: nothing to translate.
    "settings.language_title": u"Langue",
    "settings.sign_title": u"Signature",
    "settings.sign_auto": u"Automatique (extension si disponible)",
    "settings.sign_ext": u"Toujours utiliser l'extension",
    "settings.sign_ext_absent": (
        u"Aucune extension détectée sur cet appareil — les signatures ont "
        u"lieu dans cette page."
    ),
    "settings.sign_ext_present": u"Extension détectée sur cet appareil.",
    "settings.sign_browser": u"Toujours signer dans cette page",
    "settings.sign_mode_ext_page": (
        u"Les signatures restent dans l'extension — isolées des sites web."
    ),
    "settings.sign_mode_ext": (
        u"Les signatures sont approuvées dans la fenêtre de l'extension."
    ),
    "settings.sign_mode_browser": (
        u"Les signatures ont lieu dans la mémoire de cette page."
    ),
    "settings.sign_warn": (
        u"Tout script exécuté sur cette page — y compris une copie hébergée "
        u"compromise — pourrait lire vos clés tant qu'elles sont "
        u"déverrouillées. Faites passer la signature par l'extension, ou "
        u"utilisez une copie que vous contrôlez."
    ),
    "settings.sign_guide": u"Comment installer l'extension",
    "settings.sign_sites": u"Sites connectés",
    "settings.sign_sites_story_a": u"Exemple : un jeu de dés sur ",
    "settings.sign_sites_story_b": (
        u" demande à jouer avec votre compte — l'approuver le liste ici, lié à "
        u"ce seul compte. Les signatures demandent toujours confirmation. "
        u"(Ce lien ne mène nulle part — c'est un exemple fictif.)"
    ),
    "settings.sign_sites_empty": (
        u"Aucun site approuvé pour l'instant — les approbations apparaissent "
        u"ici avec révocation par site."
    ),
    "settings.sign_revoke": u"Révoquer",
    "settings.sign_badge": (
        u"Signature par extension active — détails dans Connexion"
    ),
    "settings.sign_badge_local": (
        u"Signature dans la page — détails dans Connexion"
    ),

    # ---------------------------------------------------------------- account
    # Operation labels follow the noun-phrase shape already shipped in
    # fr.json (account.op_limit_create "Création d'ordre limite").
    "account.op_assert_op": u"Assertion",
    "account.op_asset_burn": u"Destruction d'actif",
    "account.op_asset_issue": u"Émission d'actif",
    "account.op_asset_settle": u"Règlement d'actif",
    "account.op_asset_update": u"Mise à jour d'actif",
    "account.op_authority_create": u"Création d'autorité",
    "account.op_authority_delete": u"Suppression d'autorité",
    "account.op_authority_update": u"Mise à jour d'autorité",
    "account.op_balance_claim": u"Réclamation de solde",
    "account.op_blind_from": u"Transfert depuis aveugle",
    "account.op_blind_to": u"Transfert vers aveugle",
    "account.op_blind_transfer": u"Transfert aveugle",
    "account.op_claim_fees": u"Réclamation de frais",
    "account.op_claim_pool": u"Réclamation de pool",
    "account.op_collateral_bid": u"Offre de collatéral",
    "account.op_committee_join": u"Adhésion au comité",
    "account.op_committee_update": u"Mise à jour de comité",
    "account.op_custom_op": u"Opération personnalisée",
    "account.op_deal_expired": u"Deal expiré",
    "account.op_deal_repay": u"Remboursement de deal",
    "account.op_deal_update": u"Mise à jour de deal",
    "account.op_debit_claim": u"Réclamation de prélèvement direct",
    "account.op_debit_create": u"Création de prélèvement direct",
    "account.op_debit_delete": u"Suppression de prélèvement direct",
    "account.op_debit_update": u"Mise à jour de prélèvement direct",
    "account.op_execute_bid": u"Exécution d'offre",
    "account.op_fba_distribute": u"Distribution FBA",
    "account.op_fee_pool_fund": u"Alimentation du pool de frais",
    "account.op_feed_producers_update": u"Mise à jour des producteurs de flux",
    "account.op_feed_publish": u"Publication de flux",
    "account.op_global_settle": u"Règlement global",
    "account.op_htlc_create": u"Création de HTLC",
    "account.op_htlc_extend": u"Prolongation de HTLC",
    "account.op_htlc_redeem": u"Rachat de HTLC",
    "account.op_htlc_redeemed": u"HTLC racheté",
    "account.op_htlc_refund": u"Remboursement de HTLC",
    "account.op_issuer_update": u"Mise à jour de l'émetteur",
    "account.op_offer_accept": u"Acceptation de crédit",
    "account.op_offer_create": u"Création d'offre de crédit",
    "account.op_offer_delete": u"Suppression d'offre de crédit",
    "account.op_offer_update": u"Mise à jour d'offre de crédit",
    "account.op_order_update": u"Mise à jour d'ordre",
    "account.op_override_transfer": u"Transfert prioritaire",
    "account.op_params_update": u"Mise à jour des paramètres globaux",
    "account.op_pool_create": u"Création de pool",
    "account.op_pool_delete": u"Suppression de pool",
    "account.op_pool_deposit": u"Dépôt dans le pool",
    "account.op_pool_swap": u"Swap dans le pool",
    "account.op_pool_update": u"Mise à jour du pool",
    "account.op_pool_withdraw": u"Retrait du pool",
    "account.op_proposal_create": u"Création de proposition",
    "account.op_proposal_delete": u"Suppression de proposition",
    "account.op_proposal_update": u"Mise à jour de proposition",
    "account.op_samet_borrow": u"Emprunt Same-T",
    "account.op_samet_create": u"Création de fonds Same-T",
    "account.op_samet_delete": u"Suppression de fonds Same-T",
    "account.op_samet_repay": u"Remboursement Same-T",
    "account.op_samet_update": u"Mise à jour de fonds Same-T",
    "account.op_settle_cancel": u"Annulation de règlement",
    "account.op_smartcoin_update": u"Mise à jour du smartcoin",
    "account.op_ticket_create": u"Création de ticket",
    "account.op_ticket_update": u"Mise à jour de ticket",
    "account.op_vesting_create": u"Création de vesting",
    "account.op_vesting_withdraw": u"Retrait de vesting",
    "account.op_witness_join": u"Adhésion comme témoin",
    "account.op_witness_update": u"Mise à jour de témoin",
    "account.op_worker_create": u"Création de worker",

    # History one-liners: French, past participle on the end (matching the
    # shipped trade/vesting summaries "Exécuté : … payés, … reçus").
    "account.page_total": u"Total de la page ≈ ",
    "account.portfolio_page": u"Page %(page)s sur %(pages)s",
    "account.sum_account_create": u"%(name)s enregistré",
    "account.sum_account_transfer": u"Compte transféré à %(owner)s",
    "account.sum_account_update": u"Compte mis à jour : %(account)s",
    "account.sum_asset_burn": u"%(amount)s détruits",
    "account.sum_asset_create": u"Actif %(symbol)s créé",
    "account.sum_asset_issue": u"%(amount)s émis à %(to)s",
    "account.sum_asset_settle": u"Règlement de %(amount)s demandé",
    "account.sum_asset_update": u"Actif %(asset)s mis à jour",
    "account.sum_authorities": u"Autorités de %(account)s mises à jour",
    "account.sum_balance_claim": u"%(amount)s réclamés",
    "account.sum_bid": u"Offre de %(coll)s contre %(debt)s",
    "account.sum_blind": u"Transfert aveugle (%(in)s entrants, %(out)s sortants)",
    "account.sum_call_update": (
        u"Position ajustée : %(coll)s de collatéral, %(debt)s de dette"
    ),
    "account.sum_claim_fees": u"%(amount)s de frais réclamés",
    "account.sum_committee_create": u"Devenu membre du comité : %(account)s",
    "account.sum_committee_update": u"Membre du comité %(account)s mis à jour",
    "account.sum_custom": u"Opération personnalisée par %(account)s",
    "account.sum_deal_expired": u"Deal %(deal)s expiré",
    "account.sum_deal_repay": u"%(amount)s remboursés sur le deal %(deal)s",
    "account.sum_deal_update": u"Deal %(deal)s mis à jour",
    "account.sum_debit_claim": u"Prélèvement de %(amount)s réclamé",
    "account.sum_debit_create": (
        u"Prélèvement de %(amount)s autorisé pour %(to)s"
    ),
    "account.sum_debit_delete": (
        u"Autorisation de prélèvement %(perm)s supprimée"
    ),
    "account.sum_debit_update": (
        u"Prélèvement de %(amount)s mis à jour pour %(to)s"
    ),
    "account.sum_execute_bid": u"Offre exécutée : %(coll)s pour %(debt)s",
    "account.sum_fee_pool_fund": (
        u"Pool de frais de %(asset)s alimenté avec %(amount)s"
    ),
    "account.sum_feed": u"Flux publié pour %(asset)s par %(publisher)s",
    "account.sum_feed_producers": (
        u"%(n)s producteurs de flux définis pour %(asset)s"
    ),
    "account.sum_fill": u"Exécuté : %(pays)s payés, %(receives)s reçus",
    "account.sum_global_settle": u"%(asset)s réglé globalement",
    "account.sum_htlc_claimed": u"HTLC %(id)s réclamé",
    "account.sum_htlc_create": u"HTLC %(id)s : %(amount)s de %(from)s vers %(to)s",
    "account.sum_htlc_extend": u"HTLC %(id)s prolongé",
    "account.sum_htlc_redeem": u"HTLC %(id)s racheté",
    "account.sum_htlc_refund": u"HTLC %(id)s remboursé",
    "account.sum_issuer_update": u"Nouvel émetteur pour %(asset)s : %(issuer)s",
    "account.sum_offer_accept": (
        u"%(amount)s empruntés contre %(coll)s (offre %(offer)s)"
    ),
    "account.sum_offer_create": u"Offre de crédit créée en %(asset)s",
    "account.sum_offer_delete": u"Offre %(offer)s supprimée",
    "account.sum_offer_update": u"Offre %(offer)s mise à jour",
    "account.sum_order_cancel": u"Ordre %(order)s annulé",
    "account.sum_order_create": u"%(sell)s offerts pour au moins %(buy)s",
    "account.sum_order_update": u"Ordre %(order)s mis à jour",
    "account.sum_pool_create": u"Pool %(a)s / %(b)s créé",
    "account.sum_pool_delete": u"Pool %(pool)s supprimé",
    "account.sum_pool_deposit": u"%(a)s + %(b)s stakés dans le pool %(pool)s",
    "account.sum_pool_swap": (
        u"%(sell)s swappés contre au moins %(buy)s dans le pool %(pool)s"
    ),
    "account.sum_pool_update": u"Pool %(pool)s mis à jour",
    "account.sum_pool_withdraw": u"%(shares)s retirés du pool %(pool)s",
    "account.sum_proposal_create": u"%(n)s opérations proposées",
    "account.sum_proposal_delete": u"Proposition %(proposal)s supprimée",
    "account.sum_proposal_update": u"Proposition %(proposal)s approuvée",
    "account.sum_samet_borrow": u"%(amount)s empruntés au fonds %(fund)s",
    "account.sum_samet_create": u"Fonds SameT créé avec %(amount)s",
    "account.sum_samet_delete": u"Fonds SameT %(fund)s supprimé",
    "account.sum_samet_repay": u"%(amount)s remboursés au fonds %(fund)s",
    "account.sum_samet_update": u"Fonds SameT %(fund)s mis à jour",
    "account.sum_settle_cancel": u"Règlement de %(amount)s annulé",
    "account.sum_smartcoin_update": u"Smartcoin %(asset)s mis à jour",
    "account.sum_ticket_create": u"Ticket %(amount)s créé",
    "account.sum_ticket_update": u"Ticket %(ticket)s mis à jour",
    "account.sum_transfer": u"Transfert de %(amount)s de %(from)s vers %(to)s",
    "account.sum_transfer_recv": u"%(amount)s reçus de %(from)s",
    "account.sum_transfer_send": u"%(amount)s envoyés à %(to)s",
    "account.sum_upgrade": u"%(account)s surclassé",
    "account.sum_vesting_create": u"%(amount)s mis en vesting pour %(owner)s",
    "account.sum_vesting_withdraw": u"%(amount)s en vesting retirés",
    "account.sum_whitelist": u"%(account)s listé",
    "account.sum_witness_create": u"Devenu témoin : %(account)s",
    "account.sum_witness_update": u"Témoin %(account)s mis à jour",
    # fr.json quotes user input with “ … ” (uri.*, auth.*, explorer.*).
    "account.sum_worker_create": u"Worker “%(name)s” créé",
    "account.prices_cover_this_page": (
        u"Les prix couvrent cette page — tournez la page pour évaluer plus "
        u"d'actifs."
    ),
    "account.multisig_checking": u"Vérification des autorités…",
    "account.multisig_single": (
        u"Clé unique — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_shared": (
        u"Compte partagé — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"Compte partagé ? Les propositions se trouvent sur la page des "
        u"propositions."
    ),
    "account.multisig_unavailable": (
        u"Autorités indisponibles — les propositions restent listées sur la "
        u"page des propositions."
    ),
    "account.multisig_view_proposals": u"Voir les propositions",
    "account.multisig_open_txbuilder": (
        u"Ouvrir le constructeur de transactions"
    ),
    "account.draw_network": u"Tracer le réseau",

    # ------------------------------------------------------------ account_net
    "account_net.title": u"Réseau de comptes",
    "account_net.intro": (
        u"Saisissez un ou plusieurs comptes pour voir à qui ils envoient, à "
        u"qui ils prêtent et de qui ils empruntent. Lu dans l'index "
        u"d'historique communautaire ; rien n'est signé et rien n'est stocké."
    ),
    "account_net.seeds_label": u"Comptes à cartographier",
    "account_net.go": u"Tracer le réseau",
    "account_net.idle": u"Rien de tracé pour l'instant.",
    "account_net.scanning": u"Lecture de l'index communautaire…",
    "account_net.need_seeds": u"Saisissez au moins un compte à cartographier.",
    "account_net.need_class": u"Activez au moins un type de ligne à tracer.",
    "account_net.canvas_missing": (
        u"Le canevas du réseau est indisponible dans cette version ; le "
        u"tableau ci-dessous liste toutes les lignes."
    ),
    "account_net.class_transfer": u"Transfert",
    "account_net.class_transfer_help": u"Transferts directs de compte à compte.",
    "account_net.class_credit": u"Crédit",
    "account_net.class_credit_help": (
        u"Offres de crédit acceptées et remboursées."
    ),
    "account_net.class_override": u"Transfert prioritaire",
    "account_net.class_override_help": (
        u"Transferts dont l'émetteur de l'actif paie les frais."
    ),
    "account_net.class_debit": u"Prélèvement direct",
    "account_net.class_debit_help": (
        u"Autorisations et retraits de prélèvement direct."
    ),
    "account_net.class_htlc_help": (
        u"Contrats à verrouillage temporel par hachage et leurs mises à jour."
    ),
    "account_net.class_vesting_help": (
        u"Soldes de vesting qu'un tiers administre."
    ),
    "account_net.status_scanned": (
        u"%(scanned)s opérations indexées de %(n)s compte(s)"
    ),
    "account_net.status_graph": u"%(nodes)s comptes · %(edges)s lignes",
    "account_net.status_truncated": (
        u"%(n)s opérations les plus récentes par compte"
    ),
    "account_net.status_node_cap": u"%(n)s contreparties principales affichées",
    "account_net.status_edge_cap": u"%(n)s lignes principales affichées",
    "account_net.status_self": u"%(n)s transferts à soi-même ignorés",
    "account_net.status_shape": u"%(n)s entrées illisibles ignorées",
    "account_net.status_credit_missing": (
        u"%(n)s lignes de crédit ignorées (offre ou deal introuvable sur la "
        u"chaîne)"
    ),
    "account_net.status_unknown": u"introuvables : %(names)s",
    "account_net.detail_hint": (
        u"Touchez une ligne pour son détail ; touchez un compte pour l'ouvrir."
    ),
    "account_net.kind_flow": u"flux",
    "account_net.no_amount": u"aucun montant",
    "account_net.more_assets": u" + %(n)s de plus",
    "account_net.twin_summary": u"Vue tableau (accessible)",
    "account_net.twin_from": u"De",
    "account_net.twin_to": u"À",
    "account_net.twin_class": u"Type",
    "account_net.twin_relation": u"Flux/relation",
    "account_net.twin_amount": u"Montant",
    "account_net.twin_span": u"Premier → dernier",
    "account_net.twin_empty": (
        u"Aucune ligne entre ces comptes dans les opérations indexées analysées."
    ),
    "account_net.es_disabled": (
        u"L'index communautaire est désactivé. Activez-le dans les Paramètres "
        u"pour tracer cette carte."
    ),
    "account_net.es_bad_account": u"Ce nom n'est pas un compte sur cette chaîne.",
    "account_net.es_unavailable": (
        u"L'index communautaire est momentanément injoignable. Réessayez dans "
        u"un instant."
    ),
    "account_net.status_credit_index": (
        u"%(n)s lignes de crédit résolues depuis l'index (leur objet offre ou "
        u"deal a disparu de la chaîne)"
    ),
    "account_net.depth_label": u"Profondeur",
    "account_net.depth_1": u"1 saut",
    "account_net.depth_2": u"2 sauts",
    "account_net.ring1_label": u"Anneau 1",
    "account_net.ring2_label": u"Anneau 2",
    "account_net.stale_settings": (
        u"Les réglages de profondeur ou de voisinage ont changé — appuyez sur "
        u"Tracer le réseau."
    ),
    "account_net.status_depth": u"carte %(depth)s",
    "account_net.status_expanded": u"étendus : %(names)s",
    "account_net.status_unexpanded": (
        u"%(n)s contreparties directes non étendues"
    ),
    "account_net.status_expansion_scanned": (
        u"%(n)s opérations indexées issues des extensions"
    ),
    "account_net.status_expansion_truncated": (
        u"analyses d'extension limitées aux opérations les plus récentes"
    ),
    "account_net.twin_depth": u"Saut",

    # ---------------------------------------------------------------- market
    "market.title": u"Bourse",
    "market.tf_discrete": u"Discret",
    "market.discrete_fills": u"exécutions",
    "market.discrete_unavailable": u"Indicateurs indisponibles en Discret.",
    "market.discrete_no_fills": (
        u"Aucune exécution pour l'instant — passez un ordre ou essayez une "
        u"autre paire."
    ),
    "market.discrete_volume": u"Volume discret",
    "market.loading_pool_map": u"Chargement de la carte…",
    "market.settle_first100": (
        u"Affichage des 100 premiers (get_settle_orders limit 100)"
    ),
    "market.settle_no_cancel": (
        u"Les ordres de règlement ne peuvent pas être annulés — ils "
        u"s'exécutent au règlement (après le délai de règlement forcé de "
        u"l'actif)."
    ),
    "market.flt_min_price": u"Prix min",
    "market.flt_max_price": u"Prix max",
    "market.no_filter_match": (
        u"Aucune exécution ne correspond à ces filtres."
    ),
    "market.adjust_button": u"Ajuster",
    "market.update_title": u"Ajuster l'ordre",
    "market.update_price": u"Nouveau prix ",
    "market.update_amount": u"Montant à vendre (nouveau total) ",
    "market.update_expiry": u"Nouvelle expiration ",
    "market.update_review": u"Vérifier la mise à jour",
    "market.update_no_change": (
        u"Aucun changement — modifiez le prix, le montant ou l'expiration."
    ),
    "market.update_price_change": u"Prix (ancien → nouveau)",
    "market.update_amount_change": u"Variation du montant",
    "market.update_expiry_change": u"Expiration (ancienne → nouvelle)",
    "market.confirm_adjust": u"Confirmer l'ajustement",
    "market.update_bad_price": u"Saisissez un prix supérieur à zéro.",
    "market.update_bad_amount": u"Saisissez un montant supérieur à zéro.",
    "market.update_bad_expiry": u"Saisissez une expiration dans le futur.",
    "market.update_broadcasting": u"Diffusion de la mise à jour…",
    "market.update_done": u"Ordre mis à jour",
    "market.fail_update": u"Échec de la mise à jour.",
    "market.exchange_desk": u"Bureau de bourse",
    "market.discrete_tip_time": u"Heure",
    "market.discrete_tip_price": u"Prix",
    "market.discrete_tip_account": u"Compte",
    "market.discrete_tip_order": u"Ordre",
    "market.discrete_tip_block": u"Bloc",
    "market.map_connects": (
        u"Une ligne relie deux actifs lorsqu'un échange de marché a eu lieu au "
        u"cours des 24 dernières heures."
    ),
    "market.map_connects_fallback": (
        u"Une ligne relie deux actifs lorsqu'un pool approvisionné existe. "
        u"L'activité d'échange sur 24 h n'est pas confirmée (historique "
        u"indisponible) — affichage des pools approvisionnés."
    ),
    "market.map_hops_note": (
        u"Une ligne est un marché qui a été exécuté au cours des 24 dernières "
        u"heures. %(pairs)s paires affichées."
    ),
    "market.map_hops_no_route": (
        u"Aucune route vers BTS par les marchés exécutés."
    ),
    "market.map_hops_empty": (
        u"Aucun marché exécuté au cours des 24 dernières heures autour de ces "
        u"jambes."
    ),
    "market.map_aria": (
        u"Réseau de marchés. Les lignes sont les marchés exécutés au cours des "
        u"24 dernières heures."
    ),
    "market.map_edge_fills": u"%(desk)s · %(a)s–%(b)s · %(fills)s exéc./24h",
    "market.map_hops_filtered": (
        u"Une ligne est un marché qui a été exécuté au cours des 24 dernières "
        u"heures. Affichage de %(shown)s paires sur %(total)s (min %(min)s "
        u"exéc./24h)."
    ),
    "market.min_fills": u"Exéc. min",
    "market.map_leg_ok": u"{s} est connecté à BTS",
    "market.map_leg_orphan": (
        u"AVERTISSEMENT : {s} n'a pas de route par les marchés exécutés !"
    ),

    # ------------------------------------------------------------ market_net
    "market_net.title": u"Marchés",
    "market_net.subtitle": (
        u"Principaux marchés à carnet d'ordres par volume 24 h. Choisissez "
        u"une ligne pour ouvrir le bureau."
    ),
    "market_net.asset_1_field": u"Actif 1 (n'importe quelle jambe)",
    "market_net.asset_2_field": u"Actif 2 (n'importe quelle jambe)",
    "market_net.list_btn": u"Lister les marchés",
    "market_net.clear_btn": u"Effacer",
    "market_net.loading": u"Chargement des marchés…",
    "market_net.empty": u"Aucun marché trouvé pour ce filtre.",
    "market_net.offline": (
        u"Réseau indisponible — affichage des marchés en cache. Réessayez une "
        u"fois connecté."
    ),
    "market_net.col_market": u"Marché",
    "market_net.col_last": u"Dernier",
    "market_net.col_vol": u"Vol. 24h",
    "market_net.top_note": (
        u"Top %(shown)s sur %(probed)s sondés — par volume 24 h."
    ),
    "market_net.band_title": u"Réseau de marchés",
    "market_net.collapse": u"Réduire",
    "market_net.expand": u"Développer",
    "market_net.open_desk": u"Ouvrir %(id)s",
    "market_net.spark_label": u"Tendance sur 7 jours pour %(id)s",
    "market_net.selector_title": u"Sélecteur de marchés",
    "market_net.map_ready": u"%(markets)s marchés · %(assets)s actifs",
    "market_net.map_empty": u"Aucun marché avec un volume récent.",
    "market_net.verdict_full": u"%(markets)s marchés · %(assets)s actifs",
    "market_net.verdict_star": u"Marchés touchant %(s)s : %(n)s",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s marchés",
    "market_net.twin": u"Lignes de marché (%(n)s)",
    "market_net.twin_more": (
        u"Affichage de %(shown)s marchés sur %(n)s — réduisez le filtre pour "
        u"en voir moins."
    ),
    "market_net.canvas_label": (
        u"Carte du réseau de marchés. Appuyez sur Entrée pour ouvrir le marché."
    ),
    "market_net.prompt": (
        u"Touchez un nœud pour l'actif, une ligne pour le marché."
    ),
    "market_net.ramp": u"Volume 24 h : faible → élevé",
    "market_net.map_hops_ready": (
        u"%(pairs)s paires · %(assets)s actifs · exéc. 24h"
    ),
    "market_net.map_fallback": (
        u"%(pairs)s paires · %(assets)s actifs · exéc. 24h non confirmées"
    ),
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s exéc./24h"
    ),
    "market_net.verdict_path": (
        u"%(a)s atteint %(b)s en %(n)s marchés exécutés"
    ),
    "market_net.verdict_no_path": (
        u"Aucune route par marchés exécutés entre %(a)s et %(b)s"
    ),
    "market_net.ramp_fills": u"Exéc. 24 h : faible → élevée",
    "market_net.verdict_web": u"Marchés accessibles depuis %(s)s : %(n)s",

    # ----------------------------------------------------------------- asset
    "asset.cer_row": u"Taux de change central (CER)",
    "asset.producers_title": u"Producteurs de flux (op %(op)s)",
    "asset.publish_op19_title": u"Publier le flux (op %(op)s)",
    "asset.viewing_notice": (
        u"Affichage en tant que %(name)s (%(id)s) — déverrouillez pour signer."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"L'émetteur par défaut est le compte consulté (%(id)s verrouillé, "
        u"votre compte déverrouillé) — saisissez n'importe quel émetteur que "
        u"vous contrôlez. Ouvert depuis une page de compte, collez-y ce nom de "
        u"compte."
    ),
    "asset.multisig_title": u"Émetteur partagé ? Proposez-le",
    "asset.multisig_body": (
        u"Si cet actif exige plus d'une approbation, la signature directe "
        u"échoue — proposez plutôt la modification et demandez aux "
        u"copropriétaires de l'approuver (op 23)."
    ),
    "asset.multisig_open_proposals": u"Voir les propositions",
    "asset.multisig_open_txbuilder": (
        u"Ouvrir le constructeur de transactions"
    ),
    "asset.multisig_coowner_hint": (
        u"Copropriétaire ? Proposez la modification sur la page des "
        u"propositions et demandez aux copropriétaires de l'approuver (op 23)."
    ),
    "asset.new_issuer_field": u"Nouvel émetteur",
    "asset.issue_memo_warning": (
        u"Joignez un mémo — il est stocké sur la chaîne en clair."
    ),
    "asset.issue_memo_no_key": (
        u"Aucune clé memo enregistrée pour ce compte."
    ),
    "asset.owner_key_note": (
        u"Nécessite la clé active du propriétaire de l'actif."
    ),
    "asset.producers_live_title": u"Producteurs de flux",
    "asset.loading_producers": u"Chargement des producteurs…",
    "asset.producers_failed": u"Impossible de charger les producteurs.",
    "asset.no_producers": (
        u"Aucun flux publié pour l'instant — les producteurs apparaissent ici "
        u"dès qu'ils publient."
    ),
    "asset.witness_fed_note": (
        u"Alimenté par les témoins : tous les témoins actifs peuvent publier."
    ),
    "asset.committee_fed_note": (
        u"Alimenté par le comité : tous les membres actifs du comité peuvent "
        u"publier."
    ),
    "asset.producer_col": u"Producteur",
    "asset.published_col": u"Publié",
    "asset.feed_history_title": u"Historique des flux",
    "asset.history_days": u"Plage",
    "asset.plot_feeds": u"Tracer les flux",
    "asset.no_history": (
        u"Aucun historique sur cette plage — les éditeurs publient rarement ; "
        u"essayez 90 j."
    ),
    "asset.history_loading": u"Chargement de l'historique des flux…",
    "asset.history_capped": (
        u"Affichage des 8 premiers éditeurs (plafonné pour la vitesse)…"
    ),
    "asset.history_pub": u"Éditeur %(i)s/%(n)s…",
    "asset.history_exchange": u"Chargement de la bourse et des pools…",
    "asset.history_failed": (
        u"Impossible de charger l'historique des flux."
    ),
    "asset.invert_btn": u"Inverser",
    "asset.orientation_note": u"%(m)s par %(b)s",
}


# Keys inside this chunk's six sections whose French value is BYTE-IDENTICAL to
# English on purpose, listed here so the coverage of all 405 untranslated keys
# is explicit and auditable instead of implied by their absence from FR. Each
# one is asserted to still equal en after the write, so a later pass cannot
# quietly turn a deliberate loanword into an unclaimed drift (and vice versa):
#
#   * persisted ids / punctuation sentinels (handled by PINNED),
#   * words French already spells the same way ("Action", "Total", "Prix",
#     "Description", "Participation", "Relation"…),
#   * loanwords a French crypto UI keeps in English ("HTLC", "Vesting",
#     "Smartcoin", "Bitasset", "MCR", "MSSR", "NFT", "Op", "swaps", "quote"),
#   * indicator acronyms (BB, EMA, PSAR, SMA),
#   * pure glue: unit suffixes, " · " separator rows, arrow rows, "@ price",
#     and the "Ops" table column.
KEPT_ENGLISH = {
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.th_handshake": u"Handshake",
    "settings.th_participation": u"Participation",
    "settings.th_ping": u"Ping",
    "settings.confirm_remove_action": u"Action",
    "settings.custom_placeholder": u"wss://…",
    "settings.theme_original_blue": u"original-blue",
    "settings.theme_light": u"light",
    "settings.theme_dark": u"dark",
    "settings.pending": u"…",
    "settings.dash": EM,
    # Seconds glued to a number by the formatter: nothing to translate.
    "settings.age_s": u"%(n)ss",
    "account.total": u"Total ≈ ",
    "market.col_action": u"Action",
    "market.log_label": u"Log",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_empty": EM,
    "market.th_total": u"Total",
    "market.discrete_swaps": u"swaps",
    "market.discrete_tip_volume": u"Volume",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "asset.bitasset_row": u"Bitasset",
    "asset.description_row": u"Description",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.op_col": u"Op",
    "asset.smartcoin_row": u"Smartcoin",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
    "market_net.col_change": u"24h Δ",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "account_net.class_htlc": u"HTLC",
    "account_net.class_vesting": u"Vesting",
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ops · %(kind)s"
    ),
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.kind_relation": u"relation",
    "account_net.twin_count": u"Ops",
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s op · %(kind)s"
    ),
    # Account names + an object id, and the quote-asset volume tooltip whose
    # "quote" is the loanword this dictionary already ships elsewhere.
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    "market.discrete_tip_volume_quote": u"Volume (quote)",
}


# After a self-review pass one operation label read stiffly in French and was
# reworded. Insert-only is kept intact by DECLARING the superseded wording here:
# this script may replace a value only when the shipped value is byte-identical
# to the old wording declared below, i.e. only a value this same batch wrote.
# Anything else — English, or another agent's translation — is still refused.
REVISED = {
    "account.op_witness_join": (
        u"Adhésion de témoin",          # superseded by this batch
        u"Adhésion comme témoin",       # shipped
    ),
    # "échangés" read as the EXCHANGE venue in French, which is the very word
    # the exchange row of docs/i18n-glossary/fr.md reserves for it; the shipped
    # history wording is the loanword verb ("Swappé." in pool.swapped).
    "account.sum_pool_swap": (
        u"%(sell)s échangés contre au moins %(buy)s dans le pool %(pool)s",
        u"%(sell)s swappés contre au moins %(buy)s dans le pool %(pool)s",
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
            "line count changed: %s (en %d, fr %d)"
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
    fr, en = load(FR_PATH), load(EN_PATH)
    d, e = flat(fr), flat(en)
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for key in sorted(FR):
        if key not in d:
            bad.append("key missing from fr.json: %s" % key)
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

    # Pinned ids are never in FR (they must keep the English bytes) but must
    # still equal en after the write.
    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(FR) if d.get(k) == e.get(k)]
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
        and k not in FR and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(FR) - len(same), len(FR)))
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
    meta = fr.get("_meta", {})
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
    raw = open(FR_PATH, encoding="utf-8").read()
    fr = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(fr, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: fr.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(fr))
    before_meta = json.dumps(fr["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, (old, new) in sorted(REVISED.items()):
        if key not in before:
            print("REFUSING: revised key not in fr.json: %s" % key)
            return 1
        if before[key] not in (en_flat[key], old, new):
            print("REFUSING: would overwrite a value this batch did not "
                  "write: %s (%r)" % (key, before[key]))
            return 1
        if before[key] == new:
            continue
        if before[key] != old:
            print("REFUSING: %s does not hold the declared superseded "
                  "wording (%r)" % (key, before[key]))
            return 1
        check_batch(en_flat, key, new, problems)
        planned.append(key)
        deep_set(fr, key, new)
    for key, value in sorted(FR.items()):
        if key in REVISED:
            continue  # owned by the REVISED loop above, on the same bytes
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in fr.json: %s" % key)
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
        deep_set(fr, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # Coverage: FR + KEPT_ENGLISH must account for EVERY key of the six
    # sections, so a forgotten string shows up as a refusal instead of quietly
    # shipping English.
    both = sorted(set(FR) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (FR and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(FR) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in fr.json: %s" % key)
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

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(fr)
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
    meta = fr["_meta"]
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
    added = sorted(k for k in FR
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

    print("fr chunk-A: %d planned, %d differ from en, %d intentionally identical"
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

    with open(FR_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(fr, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/fr.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
