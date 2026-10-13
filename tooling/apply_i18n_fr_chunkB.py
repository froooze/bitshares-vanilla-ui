#!/usr/bin/env python3
"""i18n fr chunk-B: fill every remaining `fr` section of vanilla/locales/fr.json
that chunk-A did not own (account, account_net, settings, market, market_net,
asset are chunk-A's and are REFUSED here as out of scope).

Scope: ONLY the sections listed in SECTIONS. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from fr.json, or one whose English master moved, is REFUSED;
  * FR + KEPT_ENGLISH together must account for EVERY untranslated key of the
    listed sections, so a forgotten string is a refusal, never a silent English.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                     single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                     byte-verbatim;
  G3  pinned keys    shell.brand, shell.footer_brand, shell.footer_brand_vanilla
                     stay byte-verbatim;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master — so
                     the multi-line help articles (Markdown bodies with # headings
                     and [label](#/hash) links) keep their shape, only the prose
                     and the link LABELS are French;
  G5  untouched      every key outside this batch keeps its exact prior value,
                     the key SET is unchanged, and _meta keeps its v1 shape
                     (version 1, untranslated false) with `translated` moving in
                     lockstep with the bytes: a claimed key must differ from en,
                     an untranslated key must still equal en. Filling strings is
                     not verification, so the controller's v2 provenance /
                     verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte;
  G7  typography     no ASCII apostrophe leaks into a section fr.json writes
                     with the typographic one, and no typographic apostrophe
                     leaks into a section it writes with the ASCII one — the
                     two conventions are per-section and must not mix inside a
                     section. Also the French spacing rule: in a typographic
                     section the high punctuation gets U+00A0 before it, which
                     is applied here rather than typed by hand (see
                     NBSP_BEFORE) so it cannot be forgotten line by line.

Register: formal "vous", matching the voice already shipped in fr.json
(account.s5 "Saisissez votre mot de passe…", barter.viewing_as "déverrouillez
pour agir avec votre compte", transfer.viewing_as_committee "le mot de passe
n'est demandé qu'à la signature"). Vocabulary is reused verbatim from fr.json
wherever that dictionary has already settled a word: portefeuille, compte,
solde, actif, carnet d'ordres, ordre limite, frais, opération, transaction,
bloc, mémo, brainkey, témoin, comité, worker, proxy, slate, vesting,
proposition, ticket, HTLC, pool, swap, collatéral, smartcoin, précision, part,
nœud, chaîne, flux, règlement, passerelle, parrain, registrar, faucet,
déverrouiller, vérifier. Nothing is invented where a French crypto UI keeps
the English word (DEX, HTLC, BitShares, BTS, API, Memo, Swap, Proxy,
Smartcoin, Pools, Pool, Stake, Airdrop, Spotlight, Trollbox, Brainkey, Ticket,
Vesting, Worker, Delta, Deal, Spot, PnL, House, Board) — the run prints every
value that stays identical to en, so a reviewer checks the list instead of
guessing.

High-risk keys (transfer, auth, unlockconfirm, vesting, createworker,
createaccount, htlc, samet, credit, debit, ticket, vote, txbuilder, approval,
proposals_ticket, wallet, gateway, i18n.*) render DUAL-LINE inside signing
dialogs with the English reference beside them, so their wording is
deliberately plain and literal: an amount, a destination, an irreversible
action or a permission is named the way the English names it, never softened.

Numbers: no amount is retyped in a translated string — a bare value is
`Format`'s job (AGENTS.md §3.5) — and no prose number is invented.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_fr_chunkB.py                 # dry run (asserts)
  python3 tooling/apply_i18n_fr_chunkB.py --apply         # writes fr.json
  python3 tooling/apply_i18n_fr_chunkB.py --verify        # structural re-proof
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

SECTIONS = (
    "about", "approval", "assets_feed", "auth", "barter", "borrow", "common",
    "compat", "createaccount", "createworker", "credit", "dashboard", "debit",
    "eslab", "explorer", "explorer_assets", "gateway", "help", "htlc", "i18n",
    "instant", "market_book", "market_ind", "market_orders", "menu", "misc",
    "nav", "news", "notify", "pool", "pool_detail", "pool_net", "pools",
    "prediction", "proposal", "proposals_ticket", "referrals", "samet", "seo",
    "shell", "splash", "swap", "ticket", "tickets", "tour", "trade",
    "transfer", "trollbox", "txbuilder", "unlockconfirm", "vesting", "vote",
    "wallet", "xrate",
)

# Keys whose value is a brand, not prose (rule 1). They are deliberately
# ABSENT from FR below so they keep the English bytes, and the verify pass
# re-asserts every one of them after the write.
PINNED = (
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
)

# Sections fr.json already writes with the typographic apostrophe (U+2019) and
# the U+00A0 before the high punctuation (explorer 34/20, help 80/160,
# proposal 30/14, trade 22/10, transfer 12/11, gateway 17/7, misc 28/8,
# htlc 5/6, instant 14/8, prediction 14/5, vesting 10/5, barter 6/9,
# credit 12/4). Every OTHER section uses the ASCII apostrophe and a plain
# space (account 25/0, market 13/0, asset 14/0, pool 14/0, vote 13/0, …).
TYPO_SECTIONS = frozenset((
    "approval", "barter", "credit", "explorer", "gateway", "help", "htlc",
    "i18n", "instant", "proposal", "trade", "transfer",
))

PLACEHOLDER = re.compile(r"%\([A-Za-z0-9_]+\)s")
BRACE = re.compile(r"\{[A-Za-z0-9_]+\}")
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")
# French spacing rule for a typographic section: U+00A0 (not a plain space)
# before ':' and ';'. Applied programmatically by frenchize() so it cannot be
# forgotten line by line, and never before '?' or '!' — '?dialog=N' in the
# About article is a query string, not punctuation.
NBSP_BEFORE = re.compile(u"(?<= )([:;])")
# Punctuation-smuggling characters that must never appear in a translated value
# (a stray U+00B7 once shipped inside a word in the es batch). The middot and
# its lookalikes are legitimate ONLY as the " · " separator en.json uses, so
# they are checked by context rather than banned outright.
INVISIBLE = re.compile(u"[­‌‍⁠﻿]")
DOT_CHARS = u"·•‧･"

APO_TYPO = u"’"
NBSP = u" "


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


def frenchize(key, value):
    """Apply the per-section French spacing rule (see NBSP_BEFORE)."""
    if key.split(".")[0] in TYPO_SECTIONS:
        return NBSP_BEFORE.sub(NBSP + "\\1", value)
    return value


EM = u"—"

# Multi-line Markdown bodies are written as line lists joined with "\n" so the
# line count (G4) is structural, not a count someone has to keep by hand.
def md(*lines):
    return "\n".join(lines)


FR = {
    # ------------------------------------------------------------------- nav
    "nav.credit": u"Crédit",
    "nav.margin": u"Marge",
    "nav.markets": u"Marchés",

    # ----------------------------------------------------------------- shell
    "shell.footer_ahead": u"%(n)s commits d'avance de",
    "shell.footer_ahead_one": u"1 commit d'avance de",
    "shell.footer_at_build": u"à la compilation du %(date)s",
    "shell.footer_behind": u"%(n)s commits derrière",
    "shell.footer_behind_one": u"1 commit derrière",
    "shell.footer_dahead": u"%(n)s d'avance",
    "shell.footer_dbehind": u"%(n)s derrière",
    "shell.footer_diverged": u"divergé de",
    "shell.footer_offbranch": u"pas sur Master",
    "shell.footer_sync": u"synchronisé avec",

    # ------------------------------------------------------------- dashboard
    "dashboard.welcome": u"Négociez des BTS avec des clés que vous détenez",
    "dashboard.tagline": (
        u"Parcourez les marchés gratuitement — créez un portefeuille pour "
        u"négocier."
    ),

    # --------------------------------------------------------------- barter
    # Typographic section.
    "barter.confirm_barter_proposal_op_22": (
        u"Confirmer la proposition de troc (op %(op)s)"
    ),
    "barter.step_build": u"Construire",
    "barter.step_preview": u"Aperçu",
    "barter.step_propose": u"Proposer",
    "barter.propose_barter_op_22": u"Proposer un troc (op %(op)s)",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"Aperçu d’un swap atomique à double sens. Prévisualisez d’abord, puis "
        u"PROPOSER inclut les transferts des deux parties dans une seule "
        u"proposition (op %(op)s, payeur des frais = pair A)."
    ),
    "barter.uc_title": u"Déverrouiller pour signer",

    # ---------------------------------------------------------------- borrow
    "borrow.adjust_position_op_3": u"Ajuster la position (op %(op)s)",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Les positions sur marge empruntent un bitasset contre du collatéral. "
        u"Recharger le collatéral ou rembourser la dette ajuste l'op %(op)s "
        u"(call_order_update) sur votre ordre d'appel."
    ),
    # "Position " is the French word already: byte-identical on purpose.
    "borrow.settlement_bids_op_45": u"Offres de règlement (op %(op)s)",
    "borrow.open_a_new_position_op_3": (
        u"Ouvrir une nouvelle position (op %(op)s)"
    ),
    "borrow.adjust": u"Ajuster",
    "borrow.repay_full": u"Rembourser en totalité",
    "borrow.close_position": u"Clôturer la position",
    "borrow.bids_no_cancel": (
        u"Les offres ne peuvent pas être annulées une fois placées — elles "
        u"s'exécutent ou expirent."
    ),
    "borrow.uc_title": u"Déverrouiller pour signer",

    # ---------------------------------------------------------------- credit
    # Typographic section.
    "credit.my_deals_borrower": u"Mes deals (emprunteur)",
    "credit.no_borrower_deals": (
        u"Aucun deal d’emprunteur pour l’instant — les deals apparaissent "
        u"après un emprunt contre une offre."
    ),
    "credit.uc_title": u"Déverrouiller pour signer",

    # ----------------------------------------------------------------- debit
    "debit.perm_col": u"Autorisation",
    "debit.uc_title": u"Déverrouiller pour signer",
    "debit.uc_order": u"Ordre",

    # -------------------------------------------------------------- explorer
    # Typographic section.
    "explorer.assets_mode_prediction": u"Prédiction",
    "explorer.assets_mode_user": u"Émis par l’utilisateur",
    "explorer.assets_of": u"de",
    "explorer.assets_showing": u"Affichage de",
    "explorer.feed_cer_premium": (
        u"Prime du taux de change central (CER) (estimation selon la règle de "
        u"l’éditeur)"
    ),
    "explorer.feeds_scanned_suffix": u"analysés (100 premiers actifs)",
    "explorer.feeds_of": u"de",
    "explorer.feeds_showing": u"Affichage de",
    "explorer.no_assets_match": u"Aucun actif ne correspond à “%(q)s”.",
    "explorer.assets_mode_all": u"Tous",

    # --------------------------------------------------------------- gateway
    # Typographic section.
    "gateway.intro_a": (
        u"Envoyez les monnaies externes à l’adresse affichée. Cette page "
        u"n’envoie rien."
    ),
    "gateway.intro_b": (
        u"Les retraits se terminent dans Transfert avec un aperçu des frais en "
        u"direct."
    ),

    # ------------------------------------------------------------------ htlc
    # Typographic section.
    "htlc.list_sub": (
        u"Verrouillez des fonds derrière un hachage — le destinataire les "
        u"rachète avec le secret avant l’expiration, sinon vous êtes "
        u"remboursé. Lisible par tous ; le mot de passe n’est demandé qu’à la "
        u"signature."
    ),
    "htlc.direction": u"Sens",
    "htlc.uc_title": u"Déverrouiller pour signer",

    # ----------------------------------------------------------- market_book
    "market_ind.count_note": u"%(count)s × %(bucket)s bougies",
    "market_ind.count_partial": u"%(actual)s sur %(requested)s × %(bucket)s bougies",
    "market_ind.count_capped": u"fenêtre tronquée",

    # ---------------------------------------------------------- pool_detail
    "pool_detail.invert": u"Inverser",
    "pool_detail.invert_label": (
        u"Inverser l'orientation du graphique (A par B / B par A)"
    ),
    "pool_detail.map_connects": (
        u"Une ligne relie deux actifs lorsqu'un pool approvisionné existe et "
        u"qu'un échange a eu lieu au cours des 24 dernières heures."
    ),
    "pool_detail.map_connects_fallback": (
        u"Une ligne relie deux actifs lorsqu'un pool approvisionné existe. "
        u"L'activité d'échange sur 24 h n'est pas confirmée (historique "
        u"indisponible) — affichage des pools approvisionnés."
    ),
    "pool_detail.candle_count": (
        u"%(swaps)s swaps · %(count)s × %(bucket)s bougies"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s swaps · %(actual)s sur %(requested)s × %(bucket)s bougies"
    ),
    "pool_detail.candle_capped": u"fenêtre tronquée",

    # ----------------------------------------------------------------- pools
    "pools.selector_title": u"Sélecteur de pools",

    # ----------------------------------------------------------------- trade
    # Typographic section.
    "trade.tab_single": u"Unique",
    "trade.uc_title": u"Déverrouiller pour continuer",
    "trade.uc_amount": u"Montant",
    "trade.uc_price": u"Prix",
    "trade.uc_orders": u"Ordres",
    "trade.uc_range": u"Plage de prix",
    "trade.uc_total": u"Total à vendre",

    # -------------------------------------------------------------- transfer
    # Typographic section; signing wording, deliberately literal.
    "transfer.unlock_sign": u"Déverrouiller et vérifier",
    "transfer.confirm_proposal_title": (
        u"Confirmer la proposition (op %(op)s)"
    ),
    "transfer.enclosed_op_note": (
        u"Op incluse : transfert (op %(op)s) — ne s’exécute qu’après les "
        u"approbations."
    ),
    "transfer.propose_notice_locked": (
        u"Le proposant par défaut est %(name)s (%(id)s) tant que le "
        u"portefeuille est verrouillé — déverrouillez pour agir vous-même."
    ),
    "transfer.share_needs_to_amount": (
        u"Un lien partageable exige un destinataire et un montant."
    ),
    "transfer.uc_title": u"Déverrouiller pour continuer",

    # ------------------------------------------------------------------ auth
    "auth.multisig_title": u"Comptes partagés / multisig",
    "auth.multisig_body": (
        u"Ce portefeuille détient une seule clé. Les comptes partagés exigent "
        u"des propositions et des approbations des copropriétaires, "
        u"coordonnées par l'id de proposition (1.10.N). La consultation est "
        u"publique ; seule la signature exige le mot de passe."
    ),
    "auth.multisig_step_propose": (
        u"Proposez l'opération (Transfert a Envoyer/Proposer ; les actifs, le "
        u"troc et l'emprunt renvoient aux propositions)."
    ),
    "auth.multisig_step_share": (
        u"Partagez l'id de proposition 1.10.N avec les copropriétaires."
    ),
    "auth.multisig_step_approve": (
        u"Les copropriétaires approuvent (op 23) sur la page des propositions, "
        u"ou cosignent via le constructeur de transactions."
    ),
    "auth.multisig_open_proposals": u"Voir les propositions",
    "auth.multisig_open_txbuilder": (
        u"Ouvrir le constructeur de transactions"
    ),

    # --------------------------------------------------------- createaccount
    "createaccount.step_name": u"Nom",
    "createaccount.step_register": u"Enregistrer",

    # ---------------------------------------------------------- createworker
    "createworker.confirm_worker_op_34": (
        u"Confirmer le worker (op %(op)s)"
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Rédigez un worker (op %(op)s). L'aperçu est en direct ; la "
        u"vérification cite les frais en direct, puis Signer et envoyer diffuse "
        u"directement l'op %(op)s — les workers sont créés par op directe, pas "
        u"par proposition."
    ),
    "createworker.worker_preview_op_34": (
        u"Aperçu du worker (op %(op)s)"
    ),

    # ----------------------------------------------------------------- help
    "help.about_link": u"À propos de ce portefeuille",
    "help.topic_about-making_text": (
        u"L’histoire de la construction de ce portefeuille —"
    ),
    "help.topic_about-making_title": u"La construction de ce portefeuille",
    "help.topic_dex-trading_title": u"Négociation",
    "help.topic_browser_text": (
        u"Quels navigateurs exécutent le portefeuille, et ce que signifie "
        u"l’avis de compatibilité."
    ),
    "help.topic_browser_title": u"Prise en charge des navigateurs",
    "help.topic_voting_text": (
        u"Votez pour les témoins, le comité, les workers — ou déléguez à un "
        u"proxy."
    ),
    "help.topic_wallets_body": md(
        u"# Une application web avec un coffre local",
        u"Cette application tourne dans votre navigateur et parle à un nœud de "
        u"la chaîne, qui lui sert de passerelle vers le réseau. Tout ce qui "
        u"est secret reste dans le coffre local de votre navigateur.",
        u"# Aucune connexion cloud",
        u"Ce portefeuille n’a pas de connexion par nom d’utilisateur et mot de "
        u"passe : chaque portefeuille ici est local à un seul navigateur. Pour "
        u"utiliser votre compte sur un nouveau navigateur ou un autre "
        u"ordinateur, repartez du même brainkey — il n’existe aucun identifiant "
        u"qui l’ouvre à lui seul, d’où qu’il vienne.",
        u"# Portefeuille local",
        u"Un portefeuille local est une base de données dans un navigateur "
        u"précis. Il ne vous suit pas sur un autre ordinateur ou navigateur, à "
        u"moins que vous ne transportiez le brainkey et ne l’importiez.",
        u"Lisez l’article Sauvegardes avant de compter sur un portefeuille "
        u"local pour des fonds réels.",
        u"# Discipline du mot de passe",
        u"Le mot de passe chiffre le coffre. Les mots de passe courts ou "
        u"réutilisés cèdent à l’essai ; une phrase secrète unique notée sur "
        u"papier, non.",
        u"Changer le mot de passe rechiffre tout — vérifiez d’abord l’actuel, "
        u"puis confirmez que le portefeuille se déverrouille toujours avant de "
        u"partir.",
    ),
    "help.topic_backups_body": md(
        u"# Sauvegardez tôt, sauvegardez deux fois",
        u"Faites une sauvegarde de votre portefeuille local avant de "
        u"l’approvisionner — une sauvegarde suffit généralement ensuite, mais "
        u"conservez-la en au moins deux endroits sûrs que vous seul pouvez "
        u"atteindre.",
        u"Il n’y a aucun fichier de sauvegarde dans ce portefeuille : votre "
        u"brainkey EST la sauvegarde, et la phrase secrète seule ne restaure "
        u"rien. Sans les mots ET la phrase secrète, vos fonds sont perdus. Ne "
        u"rangez jamais la phrase secrète à côté des mots.",
        u"# Votre brainkey est la sauvegarde",
        u"Si vous n’avez jamais importé de clés brutes à la main, tout votre "
        u"portefeuille dérive de manière déterministe d’un seul brainkey — une "
        u"suite de mots. Noter le brainkey sauvegarde chaque compte et chaque "
        u"fonds de ce portefeuille.",
        u"Affichez-le dans le gestionnaire de portefeuille et recopiez-le sur "
        u"papier, rangé séparément de tout ce qui est numérique. Les fichiers "
        u".bin du portefeuille de référence ne peuvent pas être importés ici — "
        u"le portefeuille le dit à l’écran, et aucun téléchargement de fichier "
        u"n’existe.",
        u"# Avancé : hiérarchies d’autorités",
        u"Si vous utilisez des autorités pondérées multi-comptes plutôt que de "
        u"simples clés, une sauvegarde des seules clés peut NE PAS restaurer "
        u"l’accès — la structure d’autorité elle-même compte.",
        u"Relisez l’article Autorisations et notez la configuration complète "
        u"des autorités, pas seulement les mots.",
    ),
    "help.topic_about-making_body": md(
        u"# La construction de ce portefeuille",
        u"Ce qui suit est l’histoire originale de la construction : chaque "
        u"invite qui a créé ce portefeuille, de l’acquisition de bitshares-ui le "
        u"26 septembre 2026 à la correction du problème 1 le 3 octobre, avec les "
        u"réponses des auteurs — conservées sans retouche.",
        u"Elle consigne les décisions sur lesquelles repose ce portefeuille : "
        u"se détourner d’une nouvelle mise à niveau de React après le problème "
        u"#3583 et son piège de mille heures, afin que ce portefeuille ne "
        u"dépende de rien ayant un cycle de version ; signer chaque transaction "
        u"localement comme le vieux portefeuille au lieu de la déléguer ; trois "
        u"thèmes avec le look classique par défaut ; des nombres en termes "
        u"humains, jamais des entiers bruts de la chaîne ; des mises en page "
        u"pensées d’abord pour le téléphone dès la première tranche ; et des "
        u"frais lus depuis la chaîne en direct, jamais estimés. Lisez cela "
        u"comme une histoire : voici comment le portefeuille a été construit.",
        u"# L’archive complète des dialogues",
        u"L’enregistrement complet, échange par échange, se trouve sur la page "
        u"À propos (#/about). Dépliez-y la section Dialogue complet de "
        u"construction pour parcourir tous les échanges, filtrer par mot-clé, "
        u"ou ouvrir en profondeur un échange précis avec ?dialog=N.",
    ),
    "help.topic_htlc_text": (
        u"Swaps verrouillés par hachage qui paient ou remboursent."
    ),
    "help.elastic": u"Index communautaire (historique tiers)",
    "help.topic_browser_body": md(
        u"# Des fonctions détectées, jamais des noms de marque",
        u"Ce portefeuille ne demande jamais quel navigateur vous utilisez — il "
        u"teste les quatre fonctions de plateforme dont il a réellement besoin : "
        u"WebSocket (données de la chaîne), WebCrypto (coffre de clés), BigInt "
        u"(calculs monétaires) et le stockage local (paramètres). Le silence "
        u"vaut réussite : aucun bandeau sur un navigateur moderne signifie que "
        u"tout est présent.",
        u"# La cause la plus fréquente : contexte non sécurisé",
        u"Les navigateurs modernes n’exposent WebCrypto que dans des contextes "
        u"sécurisés : pages https, localhost et fichiers ouverts. Le même "
        u"navigateur à jour servi en http simple (une adresse de réseau local, "
        u"par exemple) signale WebCrypto manquant — le navigateur est bon, "
        u"l’adresse ne l’est pas. Servez le dossier en https ou sur localhost, "
        u"ou ouvrez index.html directement.",
        u"# Ce qui fonctionne toujours",
        u"La consultation fonctionne toujours : soldes, marchés, explorateur et "
        u"vote lisent des données publiques de la chaîne sans aucune fonction "
        u"de portefeuille. Seule la signature locale a besoin de l’élément "
        u"manquant. Masquer l’avis le cache sur cette machine ; il ne bloque "
        u"jamais une page.",
    ),
    "help.topic_assets-feed_title": u"Publier des flux de prix",
    "help.topic_assets-feed_text": (
        u"Publiez des flux de prix pour les actifs ancrés au marché que vous "
        u"alimentez."
    ),
    "help.topic_assets-feed_body": md(
        u"# Publier des flux de prix",
        u"Publiez le prix de règlement d’un actif ancré au marché depuis le "
        u"bureau de flux ; le dialogue de confirmation affiche les frais "
        u"exacts avant votre signature.",
    ),
    "help.topic_assets-issue_title": u"Émettre des actifs",
    "help.topic_assets-issue_text": (
        u"Créez une nouvelle offre d’un actif que vous contrôlez depuis le "
        u"bureau d’émission."
    ),
    "help.topic_assets-issue_body": md(
        u"# Émettre des actifs",
        u"Créez une nouvelle offre d’un actif que votre compte contrôle depuis "
        u"le bureau d’émission ; les montants utilisent la précision de "
        u"l’actif et le dialogue de confirmation affiche les frais exacts avant "
        u"votre signature.",
    ),
    "help.topic_community_title": u"Communauté",
    "help.topic_community_text": (
        u"Discussions, forums, explorateurs et code autour de BitShares."
    ),
    "help.topic_community_body": md(
        u"# Communauté",
        u"Les personnes et les lieux autour de BitShares — page d’accueil, code, "
        u"explorateurs, forums et discussions — se trouvent sur la page "
        u"Communauté.",
    ),
    "help.topic_menu_title": u"Menu du site",
    "help.topic_menu_text": (
        u"Chaque page de ce portefeuille, regroupée comme le menu de "
        u"navigation les regroupe."
    ),
    "help.topic_menu_body": md(
        u"# Menu du site",
        u"La page Menu liste tous les écrans de ce portefeuille par section, "
        u"si bien que n’importe quel bureau est à une toucher d’accès.",
    ),
    "help.topic_sitemap_title": u"Plan du site",
    "help.topic_sitemap_text": (
        u"Chaque page de ce portefeuille sur une seule page : chaque page de "
        u"menu plus les parcours et vues détaillées qui n’ont pas de carte de "
        u"menu."
    ),
    # The 83-line sitemap: one line per page, link LABELS translated, link
    # HASHES byte-verbatim (G4 re-checks the hash list against en).
    "help.topic_sitemap_body": md(
        u"Chaque page de ce portefeuille, regroupée comme le menu hamburger les "
        u"regroupe. Tout ce qui porte un lien s’ouvre directement ; les vues "
        u"détaillées listées sous Pages sans carte de menu s’ouvrent depuis "
        u"leurs pages parentes.",
        u"# Portefeuille",
        u"- [Tableau de bord](#/)",
        u"- [Mon compte](#/account/me)",
        u"- [Comptes](#/accounts)",
        u"- [Transfert](#/transfer)",
        u"- [Facture](#/invoice)",
        u"- [Vesting](#/vesting)",
        u"- [Portefeuille](#/wallet)",
        u"- [Changer le mot de passe du portefeuille](#/wallet/password)",
        u"- [Créer un portefeuille (Brainkey)](#/create-wallet-brainkey)",
        u"- [Importer un compte existant](#/existing-account)",
        u"- [Enregistrer un nouveau compte](#/create-account)",
        u"- [Connexion](#/login)",
        u"- [Inscription](#/registration)",
        u"- [Parrainages](#/referrals)",
        u"# Négocier",
        u"- [Bourse](#/markets)",
        u"- [Trade instantané](#/instant-trade)",
        u"- [Pools de liquidité](#/pools)",
        u"- [Taux de change](#/cross-rates)",
        u"- [Emprunter](#/borrow)",
        u"- [Troc](#/barter)",
        u"- [Dépôt / Retrait](#/deposit-withdraw)",
        u"- [Fonds Same-T](#/samet)",
        u"- [Spotlight](#/spotlight)",
        u"# Gagner & Protéger",
        u"- [Offre de crédit](#/credit-offer)",
        u"- [Prélèvement direct](#/direct-debit)",
        u"- [HTLC](#/htlc)",
        u"- [Tickets](#/tickets)",
        u"- [Airdrop](#/airdrop)",
        u"- [Autorités personnalisées](#/authorities)",
        u"- [Listes de comptes](#/lists)",
        u"# Gouverner",
        u"- [Vote](#/voting)",
        u"- [Propositions](#/proposals)",
        u"- [Créer un worker](#/create-worker)",
        u"- [Marchés de prédiction](#/prediction)",
        u"# Découvrir",
        u"- [Explorer](#/explorer)",
        u"- [Actifs](#/assets)",
        u"- [Créer un actif](#/assets/create)",
        u"- [Émettre un actif](#/assets/issue)",
        u"- [Publier un flux](#/assets/feed)",
        u"- [Frais réseau](#/explorer/fees)",
        u"- [Opérations](#/ops)",
        u"- [Top opérations](#/top-ops)",
        u"- [Actualités](#/news)",
        u"# Explorer",
        u"- [Explorer (Blockchain)](#/explorer)",
        u"- [Actifs](#/explorer/assets)",
        u"- [Pools](#/explorer/pools)",
        u"- [Comptes](#/explorer/accounts)",
        u"- [Témoins](#/explorer/witnesses)",
        u"- [Comité](#/explorer/committee)",
        u"- [Marchés](#/explorer/markets)",
        u"- [Frais](#/explorer/fees)",
        u"- [Flux](#/explorer/feeds)",
        u"# Labos",
        u"- [Labo API](#/api-lab)",
        u"- [Labo ES](#/es-lab)",
        u"- [Constructeur de transactions](#/txbuilder)",
        u"- [Réseau de comptes](#/account-network)",
        u"# Personnel",
        u"- [Trollbox](#/trollbox)",
        u"- [Favoris](#/favourites)",
        u"- [Alertes de prix](#/alerts)",
        u"- [Aide](#/help)",
        u"- [Limites de la traduction](#/help/translation-limitations)",
        u"- [À propos](#/about)",
        u"- [Communauté](#/community)",
        u"- [Paramètres](#/settings)",
        u"# Pages sans carte de menu",
        u"Les variantes d’inscription, les bureaux de compte et de marché, et "
        u"les vues détaillées s’ouvrent depuis les pages ci-dessus ou depuis "
        u"les liens ailleurs dans le portefeuille.",
        u"- [Inscription locale](#/registration/local)",
        u"- [Inscription cloud](#/registration/cloud)",
        u"- [Page de compte exemple](#/account/committee-account)",
        u"- [Bureau de marché exemple](#/market/BTS_USD)",
        u"- [Page d’actif exemple](#/asset/BTS)",
        u"- [Bureau de pool exemple](#/pools/1.19.66)",
        u"- [Vue d’ensemble du menu](#/menu)",
        u"Les vues détaillées d’une offre de crédit, d’un deal, d’une "
        u"proposition, d’un bloc, d’une transaction, d’un HTLC, d’un marché de "
        u"prédiction, d’un destinataire de transfert, d’une facture, d’une "
        u"passerelle, d’un onglet de paramètres, d’un onglet de l’explorateur "
        u"ou d’un article d’aide s’ouvrent depuis leurs pages parentes et "
        u"prennent un id ou un nom dans l’adresse.",
    ),
    "help.topic_translation-limitations_title": u"Limites de la traduction",
    "help.topic_translation-limitations_text": (
        u"Les traductions remplies par une machine sont signalées ; la "
        u"référence anglaise est toujours à une toucher d’accès. Aidez-nous à "
        u"corriger une ligne."
    ),
    "help.topic_translation-limitations_body": md(
        u"Une traduction marquée comme remplie par une machine a été écrite par "
        u"une machine. Personne ne l’a lue pour vérifier qu’elle dit ce que "
        u"dit l’anglais — c’est pourquoi toutes les langues sauf l’anglais "
        u"portent la pastille de marque dans l’en-tête de ce portefeuille. "
        u"L’anglais est le texte dont les autres ont été traduits, il ne porte "
        u"donc aucune marque.",
        u"",
        u"# Ce que signifie le * sur une ligne",
        u"Un * sur une ligne de signature signifie deux choses à la fois : la "
        u"formulation a été remplie par une machine, et l’anglais d’origine est "
        u"à une toucher d’accès. Touchez le * et l’anglais apparaît sous la "
        u"ligne exactement tel que le texte maître anglais de ce portefeuille "
        u"le stocke — le même texte dont toutes les autres langues ont été "
        u"traduites, et non une paraphrase.",
        u"",
        u"La marque suit la ligne, pas les mots qu’elle contient. Un * marque "
        u"une ligne traduite entière, et le portefeuille choisit ces lignes "
        u"selon une règle fixe : toute ligne d’un écran de signature, d’action "
        u"irréversible ou de récupération — jusqu’à un plafond de longueur, car "
        u"un long paragraphe est couvert par cet article à la place — plus "
        u"toute ligne, où qu’elle soit, dont l’anglais porte un avertissement. "
        u"Ainsi une ligne qui ne mentionne qu’un id ou qu’un montant en porte "
        u"quand même une (le champ Vers d’un transfert, par exemple), et un "
        u"long paragraphe qui mentionne un id n’en porte pas. Une valeur brute "
        u"de la chaîne — un montant dans une cellule, un id dans une colonne, "
        u"un symbole d’actif — n’est pas du tout une ligne traduite, elle ne "
        u"porte donc jamais de marque : il n’y a pas de formulation anglaise "
        u"derrière elle à comparer.",
        u"",
        u"# Ce que signifient les niveaux de confiance",
        u"Chaque langue livrée avec ce portefeuille porte une note, indiquée "
        u"dans le tableau ci-dessous. Élevée signifie que la formulation suit "
        u"de près l’anglais et se lit naturellement. Bonne signifie qu’elle est "
        u"utilisable, même si une phrase peut encore sonner maladroite. Moyenne "
        u"signifie de la lire comme un brouillon et de vérifier l’anglais avant "
        u"de vous y fier.",
        u"",
        u"Toutes les notes ci-dessous sont la machine qui a écrit les textes en "
        u"évaluant son propre travail ; personne d’indépendant ne les a "
        u"auditées. Une note décrit ce qui a été vérifié jusqu’ici, pour la "
        u"langue dans son ensemble et non ligne par ligne. L’anglais lui-même est "
        u"la référence : il est écrit à la main, et chaque autre langue est "
        u"traduite à partir de lui.",
        u"",
        u"# Comment corriger un texte",
        u"Les corrections commencent par un signalement. Indiquez la langue de "
        u"la ligne, donnez la clé que cette ligne indique, collez l’anglais "
        u"qu’elle aurait dû dire et proposez la formulation que vous "
        u"utiliseriez à la place.",
        u"",
        u"- Un signalement par ligne rend la correction facile à appliquer.",
        u"- Signalez d’abord les écrans de signature : une phrase erronée dans "
        u"un dialogue de confirmation est le cas coûteux.",
        u"- Utilisez le lien à la fin de cet article. Il ouvre un problème "
        u"déjà étiqueté pour les traductions dans le gestionnaire de ce "
        u"projet, il n’y a donc rien à retaper.",
        u"",
        u"# Les corrections sont le seul chemin vers une relecture humaine",
        u"Rien d’autre ne fait sortir un texte du statut « rempli par une "
        u"machine » : ni la fréquence d’usage d’une langue, ni une seconde "
        u"machine qui valide la première, ni une mémoire de traduction. Un "
        u"texte devient relu par un humain lorsque quelqu’un le lit dans sa "
        u"langue et l’accepte, et une ligne n’est relue que pour la langue qui "
        u"a réellement été vérifiée.",
        u"",
        u"D’ici là, la marque reste en place. Une traduction que personne n’a "
        u"lue vaut mieux que pas de traduction du tout, mais ce n’est pas la "
        u"même chose qu’une traduction qu’une personne a cautionnée.",
    ),
    "help.translation_confidence_heading": (
        u"Le niveau de confiance de chaque langue"
    ),
    "help.confidence_language": u"Langue",
    "help.confidence_level": u"Confiance",
    "help.confidence_high": u"Élevée",
    "help.confidence_good": u"Bonne",
    "help.confidence_moderate": u"Moyenne — à vérifier",
    "help.report_translation_link": (
        u"Signaler un problème de traduction sur GitHub"
    ),

    # -------------------------------------------------------------- instant
    # Typographic section.
    "instant.preview_balances_note": (
        u"Aperçu en tant que %(name)s (%(id)s) — soldes non vérifiés. "
        u"Déverrouillez pour valider les vôtres avant de signer."
    ),
    "instant.uc_title": u"Déverrouiller pour signer",
    "instant.unlock_sign": u"Déverrouiller et signer",

    # ----------------------------------------------------------------- news
    "news.explorer_blocks_and_transactions": u"Explorer la chaîne",

    # ----------------------------------------------------------- prediction
    "prediction.uc_title": u"Déverrouiller pour signer",

    # ------------------------------------------------------------- proposal
    # Typographic section; signing wording, deliberately literal.
    "proposal.confirm_proposal_create_op_22": (
        u"Confirmer la création de proposition (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Confirmer la suppression de proposition (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": (
        u"Supprimer la proposition (op %(op)s)"
    ),
    "proposal.viewing_as": (
        u"Affichage en tant que %(name)s (%(id)s) — déverrouillez pour agir "
        u"vous-même."
    ),
    "proposal.n_a": u"n/d",
    "proposal.multisig_story": (
        u"Compte partagé ? Un copropriétaire propose, partage l’id 1.10.N, les "
        u"autres approuvent ci-dessous. Le travail multi-opérations ou "
        u"multi-appareils continue dans le constructeur de transactions."
    ),
    "proposal.open_txbuilder": (
        u"Ouvrir le constructeur de transactions"
    ),

    # ----------------------------------------------------------------- vote
    "vote.direct_note": (
        u"Vote publié directement (voting_account %(id)s)."
    ),
    "vote.in_sync": (
        u"La slate de vote correspond à la chaîne — rien à publier."
    ),
    "vote.proxy_follows": (
        u" — votre stake suit ce compte ; la slate de vote ci-dessous est en "
        u"lecture seule."
    ),
    "vote.retried_prefix": (
        u"Le nœud a rejeté le mode proxy %(mode)s, le vote a donc été publié "
        u"comme propre (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"Le nœud a rejeté le mode proxy %(mode)s — nouvelle tentative une fois "
        u"comme propre…"
    ),
    "vote.confirm_witness_update_op_21": (
        u"Confirmer la mise à jour du témoin (op %(op)s)"
    ),
    "vote.proxies_follow_another_account_s_slate_re": (
        u"Les proxies suivent la slate de vote d'un autre compte — lisez "
        u"comment fonctionne le vote avant d'en définir un."
    ),
    "vote.ballot_intro": (
        u"Votre stake élit les témoins et le comité et finance les workers — "
        u"tous les décomptes et parts ci-dessous sont des lectures en direct "
        u"de la chaîne."
    ),

    # ----------------------------------------------------------------- pool
    "pool.direct_hit": u"Recherche directe de pool — pagination masquée.",
    "pool.asset_1_field": u"Actif 1 (n'importe quelle jambe)",
    "pool.asset_2_field": u"Actif 2 (n'importe quelle jambe)",
    "pool.clear_btn": u"Effacer",
    "pool.share_or_pool_hint": u"symbole, 1.3.x, ou pool 1.19.x",
    "pool.stake_autofill_hint": (
        u"Saisissez un montant — l'autre se remplit automatiquement au ratio "
        u"du pool."
    ),
    "pool.stake_ratio_empty": (
        u"Le pool est vide — saisissez les deux montants à la main."
    ),
    "pool.stake_shares_row": u"Parts LP estimées",
    "pool.stake_preview_need_both": (
        u"Saisissez les deux montants pour estimer les parts."
    ),
    "pool.stake_preview_unavailable": (
        u"Estimation des parts indisponible (hors ligne)."
    ),
    "pool.stake_preview_bad": (
        u"Vérifiez les montants — aucune estimation des parts."
    ),
    "pool.swaps_hint": (
        u" Les swaps apparaissent après le premier swap dans ce pool — "
        u"lancez-en un depuis le panneau Swap ci-dessus."
    ),
    "pool.my_swaps_hint": (
        u" Lancez-en un depuis le panneau Swap ci-dessus — vos swaps dans ce "
        u"pool s'affichent ici."
    ),
    "pool.swap_preview_dash": u"Devis (aperçu) : —",
    "pool.swap_preview": u"Devis (aperçu) : ",
    "pool.swap_mkt_preview_dash": u"Frais de marché (aperçu) : —",
    "pool.swap_mkt_row": u"Frais de marché",
    "pool.delete_not_empty": (
        u"Non vide — %(legs)s doit afficher 0 avant la suppression."
    ),
    "pool.no_filter_match": u"Aucun swap ne correspond à ces filtres.",
    "pool.swap_desk": u"Bureau de swap",
    "pool.uc_title": u"Déverrouiller pour continuer",
    "pool.map_core_self": u"BTS est le jeton de base de BitShares",
    "pool.min_swaps": u"Swaps min",

    # ------------------------------------------------------------ txbuilder
    "txbuilder.link_proposals": u"Propositions",

    # ----------------------------------------------------------------- tour
    "tour.s1_title": u"Parcourez tout gratuitement, signez localement",
    "tour.s1_body": (
        u"Chaque page lit des données publiques de la chaîne sans connexion. "
        u"Ouvrez un marché pour commencer — votre mot de passe n'est demandé "
        u"qu'à la signature."
    ),
    "tour.s3_title": u"Voir les graphiques de prix en direct",
    "tour.s3_body": (
        u"Bougies de prix, volume et profondeur, plus le menu des indicateurs : "
        u"superpositions comme SMA et EMA, oscillateurs comme RSI, MACD et "
        u"Stochastic. Ouvrez la bourse pour le voir en direct."
    ),
    "tour.s4_title": u"S'entraîner à acheter et à vendre",
    "tour.s4_body": (
        u"Les panneaux Acheter et Vendre acceptent n'importe quels nombres pour "
        u"s'entraîner. Rien ne quitte votre machine tant que vous n'avez pas "
        u"vérifié et signé avec un portefeuille déverrouillé. Ouvrez la bourse "
        u"pour essayer."
    ),
    "tour.away_note": (
        u"Sur le bureau de bourse — ouvrez-le pour voir ceci mis en évidence."
    ),

    # --------------------------------------------------------------- compat
    "compat.insecure_hint": (
        u"Cette adresse n'est pas un contexte sécurisé, le navigateur retient "
        u"donc WebCrypto. Le navigateur est à jour — servez le dossier en "
        u"https ou sur localhost, ou ouvrez le fichier directement."
    ),

    # ------------------------------------------------------------- trollbox
    "trollbox.post_review_title": u"Vérifier le message",
    "trollbox.unlock_post": u"Déverrouiller et publier",
    "trollbox.size_row": u"Taille",
    "trollbox.channel_row": u"Canal",
    "trollbox.language_row": u"Langue",
    "trollbox.fee": u"Frais",
    "trollbox.bytes_unit": u"octets",

    # --------------------------------------------------------------- splash
    "splash.hero_title": (
        u"Portefeuille BitShares dans votre navigateur — rien à installer."
    ),
    "splash.hero_sub": u"Vos clés. Vos fonds, sur la chaîne.",
    "splash.cta_exchange": u"Négocier sur la bourse",
    "splash.pulse_title": u"Nombres de la chaîne en direct",
    "splash.pulse_time": u"Heure du bloc de tête",
    "splash.topvol_unavailable": (
        u"Le volume des principaux marchés est hors ligne — vérifiez "
        u"Paramètres → Nœuds."
    ),
    "splash.cards_title": u"Négociez, fournissez, explorez — commencez ici",
    "splash.card_dex_d": u"Achetez et vendez sur le marché ouvert.",
    "splash.card_pool_d": u"Gagnez une part en fournissant deux actifs.",
    "splash.card_explore_d": u"Lisez les blocs et l'historique des comptes.",
    "splash.card_wallet_d": u"Conservez les clés sur cet appareil uniquement.",
    "splash.trust_keys_d": (
        u"La signature a lieu localement sur votre appareil. Aucun serveur ne "
        u"voit jamais un mot de passe ou une clé."
    ),
    "splash.step1_t": u"Explorez",
    "splash.step1_d": (
        u"Aucune connexion requise — parcourez d'abord la chaîne."
    ),
    "splash.step2_t": u"Créez un portefeuille",
    "splash.step2_d": (
        u"Un brainkey est généré sur cet appareil. Notez-le sur papier."
    ),
    "splash.step3_t": u"Négocier / fournir / voter",
    "splash.step3_d": (
        u"Ordres limites, pools de liquidité et bulletins — tout sur la chaîne."
    ),
    "splash.hero_sub2": (
        u"Parcourez les marchés gratuitement. Déverrouillez seulement pour "
        u"signer."
    ),
    "splash.pulse_stale": u"— obsolète",

    # ---------------------------------------------------------------- eslab
    "eslab.hint_donors": (
        u"Décomptes sur la fenêtre ; les totaux sont des entiers bruts — "
        u"divisez par la précision de l'actif."
    ),

    # ----------------------------------------------------------------- menu
    "menu.section_explore": u"Découvrir",
    "menu.section_labs": u"Labos",
    "menu.blurb_labs": (
        u"Outils puissants pour le travail sur la chaîne et les nœuds."
    ),
    "menu.section_personal": u"Personnel",
    "menu.blurb_personal": u"Discussion, alertes et votre configuration.",
    "menu.p_account_net": u"Réseau de comptes",
    "menu.d_account_net": u"suivi des transferts",
    "menu.p_xrates": u"Taux de change",
    "menu.d_xrates": (
        u"Prix des pools pour chaque actif en BTS et au-delà."
    ),

    # ---------------------------------------------------------------- about
    "about.hero_lede": (
        u"Un portefeuille pour la blockchain BitShares — marchés, comptes, "
        u"gouvernance et exploration — sous forme de simples fichiers web. "
        u"Aucun framework, aucun installeur, aucun compte chez nous. Vos clés "
        u"ne quittent jamais ce navigateur."
    ),
    "about.s2_title": u"Négociez sur le vrai carnet d'ordres",
    "about.s3_title": u"Fonctionne pendant des années sans mise à jour",
    "about.s3_body": (
        u"Le portefeuille qu'il remplace est mort sous une centaine de paquets "
        u"périmés et une chaîne d'outils que personne ne peut reproduire. "
        u"Construit pour éviter les dépendances à cycle de version : aucun "
        u"framework, aucun gestionnaire de paquets, aucune étape de build — la "
        u"plus petite chose qui puisse encore tourner dans un navigateur dans "
        u"dix ans."
    ),
    "about.s4_title": u"Les mêmes pages, mises à jour en direct",
    "about.s4_body": (
        u"Les utilisateurs revenants se sentent chez eux immédiatement — les "
        u"mêmes pages, panneaux et mots que le portefeuille classique — tandis "
        u"que les soldes, les carnets et l'état de connexion se mettent à jour "
        u"en direct. Une recherche indulgente sur les marchés, comptes et "
        u"actifs, trois thèmes, et des mises en page qui fonctionnent d'un "
        u"téléphone de 360 px à un bureau de trading 4K."
    ),
    "about.s5_body": (
        u"La chaîne parle en entiers ; vous ne les voyez jamais. Chaque montant "
        u"est placé aux décimales de son actif, chaque pourcentage à sa valeur "
        u"réelle, et chaque frais est lu depuis la chaîne en direct avant que "
        u"vous ne signiez."
    ),
    "about.making_title": u"La construction de ce portefeuille",
    "about.making_body": (
        u"Ce qui suit est l'histoire originale de la construction : chaque "
        u"invite qui a créé ce portefeuille, de l'acquisition de bitshares-ui le "
        u"26 septembre 2026 à la correction du problème 1 le 3 octobre, avec les "
        u"réponses des auteurs — conservées sans retouche. Elle consigne les "
        u"décisions sur lesquelles repose ce portefeuille : se détourner d'une "
        u"nouvelle mise à niveau de React après le problème #3583 et son piège "
        u"de mille heures, afin que ce portefeuille ne dépende de rien ayant "
        u"un cycle de version ; signer chaque transaction localement comme le "
        u"vieux portefeuille au lieu de la déléguer ; trois thèmes avec le look "
        u"classique par défaut ; des nombres en termes humains, jamais des "
        u"entiers bruts de la chaîne ; des mises en page pensées d'abord pour "
        u"le téléphone dès la première tranche ; et des frais lus depuis la "
        u"chaîne en direct, jamais estimés. Lisez cela comme une histoire : "
        u"voici comment le portefeuille a été construit."
    ),
    "about.dlg_heading": u"Dialogue complet de construction",
    "about.dlg_search_ph": u"Filtrer les échanges…",
    "about.dlg_search_clear": u"Effacer",
    "about.dlg_showing": u"Affichage de",
    "about.dlg_unavailable": (
        u"Archive des dialogues de construction indisponible."
    ),
    "about.dlg_noscript": (
        u"Cette archive nécessite JavaScript ; le même texte se trouve dans "
        u"docs/vanilla-ui-dialog.md dans le dépôt source."
    ),
    "about.dlg_no_reply": (
        u"Aucune réponse enregistrée — l'invite suivante a suivi immédiatement."
    ),
    "about.dlg_no_match": (
        u"Aucun échange correspondant. Effacez la recherche pour tout voir."
    ),
    "about.dlg_bad_link": u"Numéro d'échange invalide. Plage valide : 1–%(total)s.",
    "about.dlg_heading_c": u"Dialogue complet de construction (%(total)s)",
    "about.dlg_showing_c": u"Affichage de %(shown)s / %(total)s",

    # ------------------------------------------------------------- approval
    # Typographic section; renders beside the English inside the extension's
    # multi-signature prompt, so the wording stays plain and literal.
    "approval.title": u"Approuver la signature",
    "approval.wallet_title": u"Ce portefeuille demande une signature",
    "approval.site_prefix": u"Site : ",
    "approval.account": u"Compte : ",
    "approval.chain": u"Chaîne : ",
    "approval.remember": u"Mémoriser ce compte pour ce site",
    "approval.locked_note": (
        u"La session est verrouillée — saisissez le mot de passe de votre "
        u"portefeuille pour approuver."
    ),
    "approval.password": u"Mot de passe",
    "approval.approve": u"Approuver",
    "approval.deny": u"Refuser",
    "approval.close": u"Fermer",
    "approval.expires_in": u"Expire dans ",
    "approval.no_fields": u"Aucun champ affichable.",
    "approval.approved": u"Approuvé et diffusé.",
    "approval.denied": u"Refusé.",
    "approval.no_runtime": u"Runtime de l’extension manquant.",
    "approval.no_reply": u"Aucune réponse du signataire.",
    "approval.unknown_intent": u"Aucune demande d’approbation trouvée.",
    "approval.loading": u"Chargement de l’approbation…",
    "approval.load_failed": u"Impossible de charger l’approbation.",

    # ---------------------------------------------------------------- common
    "common.unknown_asset": u"Actif inconnu.",

    # ------------------------------------------------------------------- seo
    "seo.title_dashboard": u"Tableau de bord — Portefeuille BitShares",
    "seo.desc_dashboard": (
        u"Tableau de bord BitShares — soldes, marchés et activité de la chaîne "
        u"d'un coup d'œil. Parcourez librement ; les clés restent sur votre "
        u"appareil."
    ),
    "seo.title_market": u"Bourse BTS/USD — Portefeuille BitShares",
    "seo.desc_market": (
        u"Négociez des BTS contre des USD sur le carnet d'ordres BitShares — "
        u"offres d'achat, de vente et historique en direct, signés localement "
        u"sur votre appareil."
    ),
    "seo.title_pools": u"Pools de liquidité — Portefeuille BitShares",
    "seo.desc_pools": (
        u"Parcourez les pools de liquidité BitShares — paires, soldes et "
        u"activité lus en direct depuis la chaîne. Aucune connexion requise."
    ),
    "seo.title_explorer": (
        u"Explorateur de blockchain — Portefeuille BitShares"
    ),
    "seo.desc_explorer": (
        u"Explorez les blocs, transactions et actifs BitShares — données de la "
        u"chaîne en direct, consultables sans connexion."
    ),
    "seo.title_transfer": u"Envoyer des fonds — Portefeuille BitShares",
    "seo.desc_transfer": (
        u"Envoyez des actifs BitShares à n'importe quel compte. Vérifiez "
        u"chaque champ, puis signez localement — les clés ne quittent jamais "
        u"votre appareil."
    ),
    "seo.title_account": u"Compte %(name)s — Portefeuille BitShares",
    "seo.desc_account": (
        u"Consultez ce compte BitShares — soldes, ordres et historique lus en "
        u"direct depuis la chaîne. Aucune connexion requise."
    ),
    "seo.title_voting": u"Voter pour des témoins — Portefeuille BitShares",
    "seo.desc_voting": (
        u"Votez pour les témoins, membres du comité et workers BitShares. "
        u"Chaque bulletin est signé localement sur votre appareil."
    ),
    "seo.title_about": u"À propos — Portefeuille BitShares",
    "seo.desc_about": (
        u"À propos de ce portefeuille BitShares — clés locales, sans "
        u"inscription, sans pistage. Parcourez librement et signez localement."
    ),
    "seo.title_help": u"Aide — Portefeuille BitShares",
    "seo.desc_help": (
        u"Aide du portefeuille BitShares — guides pour les comptes, la "
        u"négociation, le vote et la récupération. Commencez ici si vous êtes "
        u"bloqué."
    ),
    "seo.title_login": u"Connexion — Portefeuille BitShares",
    "seo.desc_login": (
        u"Déverrouillez votre portefeuille BitShares local — mot de passe, "
        u"brainkey ou clés importées. Les clés ne quittent jamais cet appareil."
    ),
    "seo.title_markets": u"Marchés — Portefeuille BitShares",
    "seo.desc_markets": (
        u"Parcourez les marchés à carnet d'ordres BitShares par volume 24 h et "
        u"ouvrez le bureau de négociation de chaque paire. Aucune connexion "
        u"requise."
    ),
    "seo.title_account_net": (
        u"Réseau de comptes — Portefeuille BitShares"
    ),
    "seo.desc_account_net": (
        u"Cartographiez vers qui un compte envoie, à qui il prête et de qui il "
        u"emprunte — lu depuis l'index communautaire. Aucune connexion "
        u"requise."
    ),
    "seo.title_xrates": u"Taux de change — Portefeuille BitShares",
    "seo.desc_xrates": (
        u"Chaque actif de pool valorisé en BTS et au-delà aux derniers prix de "
        u"swap. Aucune connexion requise."
    ),

    # -------------------------------------------------------------- pool_net
    "pool_net.title": u"Réseau de pools",
    "pool_net.collapse": u"Réduire",
    "pool_net.expand": u"Développer",
    "pool_net.loading": u"Chargement du réseau…",
    "pool_net.empty": u"Aucun pool ne correspond à ce filtre.",
    "pool_net.canvas_label": (
        u"Carte du réseau de pools. Appuyez sur Entrée pour ouvrir BTS."
    ),
    "pool_net.twin": u"Lignes de pool (%(n)s)",
    "pool_net.direct": u"apparié avec BTS",
    "pool_net.hops": u"%(n)s sauts vers BTS",
    "pool_net.orphan": u"orphelin vis-à-vis de BTS",
    "pool_net.verdict_full": u"%(pools)s pools · %(assets)s actifs",
    "pool_net.verdict_path": u"%(a)s atteint %(b)s en %(n)s sauts",
    "pool_net.verdict_orphan": u"Aucune route entre %(a)s et %(b)s",
    "pool_net.verdict_star": u"Pools touchant %(s)s : %(n)s",
    "pool_net.prompt": (
        u"Touchez un nœud pour l'actif, une ligne pour le pool."
    ),
    "pool_net.legend": u"Marques",
    "pool_net.col_a": u"Actif 1",
    "pool_net.col_b": u"Actif 2",
    "pool_net.twin_more": (
        u"Affichage de %(shown)s pools sur %(n)s — réduisez le filtre pour en "
        u"voir moins."
    ),
    "pool_net.ready": u"%(pools)s pools · %(assets)s actifs",
    "pool_net.offline": (
        u"Réseau indisponible — squelette embarqué affiché. Réessayez une fois "
        u"connecté."
    ),
    "pool_net.offline_empty": (
        u"Réseau indisponible — aucun pool squelette en cache."
    ),
    "pool_net.partial": (
        u"Mise à jour en direct incomplète — pools embarqués affichés."
    ),
    "pool_net.phys": u"Physique",
    "pool_net.ramp": u"Taille du pool : petite → grande",

    # -------------------------------------------------------- unlockconfirm
    "unlockconfirm.password": u"Mot de passe",
    "unlockconfirm.empty_password": (
        u"Saisissez le mot de passe de votre portefeuille."
    ),
    "unlockconfirm.unlock_failed": u"Échec du déverrouillage.",
    "unlockconfirm.cancel": u"Retour",
    "unlockconfirm.unlock_post": u"Déverrouiller et publier",

    # ---------------------------------------------------------------- xrate
    "xrate.title": u"Taux de change",
    "xrate.intro": (
        u"Chaque actif de pool valorisé à son dernier swap, croisé via le "
        u"graphe des pools. Rien n'est signé et rien n'est stocké."
    ),
    "xrate.token_label": u"Ajouter un jeton de cotation",
    "xrate.add_btn": u"Ajouter une colonne",
    "xrate.base_pinned": (
        u"BTS est la colonne de base et ne peut pas être retirée."
    ),
    "xrate.loading": u"Lecture des pools…",
    "xrate.refresh_btn": u"Actualiser les prix",
    "xrate.show_all": u"Afficher tous les actifs",
    "xrate.retry_btn": u"Réessayer",
    "xrate.remove_btn": u"Retirer ",
    "xrate.empty": (
        u"Aucun actif de pool à moins de 3 sauts de BTS sur cette chaîne."
    ),
    "xrate.asset_col": u"Actif",
    "xrate.unknown_token": u"Aucun actif de pool nommé %(sym)s.",
    "xrate.unpriced": (
        u"Une jambe de cette route n'a encore aucun swap enregistré."
    ),
    "xrate.no_route_col": u"Aucune route vers %(sym)s en moins de 6 sauts de pool.",
    "xrate.status": (
        u"%(pools)s pools · %(assets)s actifs à moins de 3 sauts · %(done)s "
        u"pools sur %(total)s ont un dernier swap"
    ),
    "xrate.load_failed": u"Impossible de charger les taux de change : ",

    # ------------------------------------------------------------------ i18n
    # Typographic section. The honesty surface: it is the warning a French
    # reader gets about their own French, so it is translated, never left.
    "i18n.badge_label": (
        u"Statut de la traduction : traduite par une machine, non vérifiée "
        u"par un humain"
    ),
    "i18n.badge_body": (
        u"Ces traductions ont été écrites par une machine et n’ont pas été "
        u"vérifiées par un humain. Les lignes marquées d’un * sur les écrans "
        u"de signature affichent aussi l’anglais d’origine."
    ),
    "i18n.badge_details": u"Ce que cela signifie",
    "i18n.badge_improve": u"Aidez à améliorer cette traduction",
    "i18n.risk_show_english": (
        u"Afficher la référence anglaise pour cette ligne"
    ),
    "i18n.risk_about_translations": u"À propos de ces traductions",
}

# After a self-review pass one hint read as if "échange" (the word the exchange
# row of docs/i18n-glossary/fr.md reserves for the DEX venue) named a pool swap.
# Insert-only stays intact by DECLARING the superseded wording here: this script
# may replace a value only when the shipped value is byte-identical to the old
# wording declared below, i.e. only a value this same batch wrote.
REVISED = {
    "pool.swaps_hint": (
        u" Les swaps apparaissent après le premier échange dans ce pool — "
        u"lancez-en un depuis le panneau Swap ci-dessus.",
        u" Les swaps apparaissent après le premier swap dans ce pool — "
        u"lancez-en un depuis le panneau Swap ci-dessus.",
    ),
}


# Keys inside this chunk's sections whose French value is BYTE-IDENTICAL to
# English on purpose, listed here so the coverage of every untranslated key is
# explicit and auditable instead of implied by their absence from FR:
#
#   * brands and persisted ids (PINNED),
#   * words French already spells the same way ("Total", "Expiration",
#     "Delta", "Tickets", "Trollbox", "Swap", "Blockchain", "Action",
#     "Condition", "Attestation", "Sections", "Documentation", "Forum",
#     "Indexer", "Sections", "Restrictions", "Spotlight"…),
#   * loanwords a French crypto UI keeps in English (HTLC, SmartCoins, Pool,
#     Pools, Ticket, Airdrop, Worker, Vesting, Stake/Unstake, Swap/Stake,
#     Delta, Deal, Registry, Proxy, Spot, Swap, URL, TxBuilder),
#   * machine-readable sentinels (bad-asset-shape, "n/a"-free glue, "ok ",
#     "max", "—", "…", "i18n"),
#   * pure glue: unit suffixes, " · " separator rows, " @ id @ ts" rows,
#     "): ", " via ", " [op ", "Op ", "Tx ", " base ", " / quote ".
KEPT_ENGLISH = {
    "assets_feed.s1": EM,
    "explorer_assets.s1": EM,
    "barter.expiration": u"Expiration",
    "barter.paid_by_suffix": u"): ",
    "credit.deal": u"Deal",
    "credit.deal_2": u"Deal ",
    "credit.delta": u"Delta",
    "credit.total": u"Total",
    "credit.expiration": u"Expiration",
    "credit.expiration_mid": u" · Expiration ",
    "credit.total_prefix": u"Total ",
    "debit.spotlight_title": u"Spotlight",
    "borrow.position": u"Position ",
    "explorer.assets_mode_market": u"SmartCoins",
    "explorer.id_row": u"ID",
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.minutes_unit": u" minutes",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.price_base": u"base ",
    "explorer.price_quote": u" / quote ",
    "explorer.signatures_prefix": u"Signatures (",
    "explorer.th_mssr": u"MSSR",
    "explorer.th_time": u"Date",
    "explorer.tx_prefix": u"Tx ",
    "explorer.tx_title_prefix": u"Transaction ",
    "explorer.txs_row": u"Transactions",
    "explorer.votes_unit": u" votes",
    "explorer.tab_blocks": u"Blockchain",
    "explorer.stat_tps": u"Trx/s",
    "explorer.description": u"Description",
    "explorer.actions": u"ACTIONS",
    "explorer.core_suffix": u" (core)",
    "explorer.markets_sort_vol_desc": u"Volume ↓",
    "explorer.markets_sort_vol_asc": u"Volume ↑",
    "gateway.health_ok": u"ok ",
    "gateway.via": u" via ",
    "htlc.title": u"HTLC",
    "market_book.spread_prefix": u"Spread ",
    "market_orders.tape_max": u"max",
    "misc.id": u"ID",
    "misc.note": u"Note",
    "misc.restrictions": u"Restrictions",
    "notify.base_label": u"Base",
    "pool_detail.map_min_swaps": u"(min %(min)s swaps)",
    "swap.title": u"Swap",
    "proposals_ticket.title": u"Tickets",
    "samet.delta": u"Delta",
    "tickets.title": u"Tickets",
    "trade.expiration": u"Expiration ",
    "trade.row_expiration": u"Expiration",
    "trade.row_total": u"Total",
    "transfer.bad_asset_shape": u"bad-asset-shape",
    "transfer.expiration_label": u"Expiration",
    "vesting.title": u"Vesting",
    "vesting.id": u"ID",
    "vesting.total": u"Total",
    "vesting.vesting": u"Vesting",
    "wallet.brainkey": u"Brainkey",
    "createaccount.step_brainkey": u"Brainkey",
    "createworker.url": u"URL",
    "referrals.registrar": u"Registrar",
    "proposal.expiration": u"Expiration",
    "proposal.id": u"ID",
    "proposal.ticket": u"Ticket",
    "instant.expiration": u"Expiration",
    "instant.total": u"Total",
    "instant.via_mid": u" via ",
    "prediction.hdr_condition": u"Condition",
    "prediction.action": u"Action",
    "prediction.pmo_attestation": u"Attestation",
    "ticket.airdrop": u"Airdrop",
    "ticket.id": u"ID",
    "ticket.ticket": u"Ticket",
    "ticket.tickets": u"Tickets",
    # Example payload: account names and amounts, byte-verbatim by design.
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "vote.conf_votes": u" votes",
    # Pure " · " glue rows and a ticker placeholder: byte-verbatim.
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pools · %(hops)s",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.col_pool": u"Pool",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
    "i18n.badge_chip": u"i18n",
    "shell.menu": u"Menu",
    "vote.fee_core": u" (core)",
    "vote.proxy_row": u"Proxy",
    "vote.tab_workers": u"Workers (",
    "vote.url": u"URL",
    "pool.orientation_row": u"Orientation",
    "pool.pool_row": u"Pool",
    "pool.stake_title": u"Stake / unstake",
    "pool.stake_unstake_col": u"Stake/Unstake",
    "pool.swap_stake_col": u"Swap/Stake",
    "pool.stake_ratio_row": u"Ratio (spot)",
    "pool.uc_action": u"Action",
    "menu.p_spotlight": u"Spotlight",
    "menu.p_htlc": u"HTLC",
    "menu.p_tickets": u"Tickets",
    "menu.p_airdrop": u"Airdrop",
    "menu.p_trollbox": u"Trollbox",
    "menu.title": u"Menu",
    "menu.p_vesting": u"Vesting",
    "eslab.raw_index": u"Index",
    "help.topic_blockchain_title": u"Blockchain",
    "help.topic_workers_title": u"Workers",
    "help.topic_airdrop_title": u"Airdrops",
    "help.topic_spotlight_title": u"Spotlight",
    "help.documentation": u"Documentation",
    "help.code": u"Code",
    "help.forum": u"Forum",
    "help.sitemap_sections": u"Sections",
    "txbuilder.link_pools": u"Pools",
    "txbuilder.total_prefix": u"Total ",
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "trollbox.title": u"Trollbox",
    "trollbox.message_row": u"Message",
    "splash.card_pool_t": u"Pools",
    "common.page_n": u"Page %(n)s",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "nav.pools": u"Pools",
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
            "line count changed: %s (en %d, fr %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    # G7: the apostrophe convention is per-section and must not mix.
    section = key.split(".")[0]
    if section in TYPO_SECTIONS and "'" in value:
        problems.append("ASCII apostrophe in a typographic section: %s" % key)
    if section not in TYPO_SECTIONS and APO_TYPO in value:
        problems.append(
            "typographic apostrophe in an ASCII section: %s" % key
        )
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

    for k in sorted(KEPT_ENGLISH):
        if d.get(k) != e.get(k) or d.get(k) != KEPT_ENGLISH[k]:
            bad.append("kept-english key drifted: %s" % k)

    # Pinned ids must still equal en after the write.
    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(FR) if d.get(k) == e.get(k)]
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
        print("    %-18s %d identical to en" % (sec, by_section[sec]))
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
        shipped_old = frenchize(key, old)
        shipped_new = frenchize(key, new)
        if key not in before:
            print("REFUSING: revised key not in fr.json: %s" % key)
            return 1
        if before[key] not in (en_flat[key], shipped_old, shipped_new):
            print("REFUSING: would overwrite a value this batch did not "
                  "write: %s (%r)" % (key, before[key]))
            return 1
        if before[key] == shipped_new:
            continue
        if before[key] != shipped_old:
            print("REFUSING: %s does not hold the declared superseded "
                  "wording (%r)" % (key, before[key]))
            return 1
        check_batch(en_flat, key, shipped_new, problems)
        planned.append(key)
        deep_set(fr, key, shipped_new)
    for key, raw_value in sorted(FR.items()):
        if key in REVISED:
            continue  # owned by the REVISED loop above, on the same bytes
        value = frenchize(key, raw_value)
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

    # Coverage: FR + KEPT_ENGLISH must account for EVERY untranslated key of the
    # listed sections, so a forgotten string shows up as a refusal.
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

    # G5b: _meta.translated is the v1 CLAIM "these keys are translated". It
    # moves in lockstep with the bytes, for exactly the keys this batch
    # translated; the values kept byte-identical on purpose stay UNCLAIMED,
    # which is the honest state for them. Nothing else in _meta moves — filling
    # strings is not verification, so the controller's v2 provenance / verified
    # / high_risk fields stay untouched.
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

    print("fr chunk-B: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in SECTIONS:
        if by_section.get(sec):
            print("  %-18s %d" % (sec, by_section[sec]))
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
