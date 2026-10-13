#!/usr/bin/env python3
"""i18n pt chunk-B3: the LAST untranslated Portuguese keys - the high-risk
signing desks, the honesty surface, and the glue that surrounds both.

Scope: every section that still holds a key byte-equal to en after chunks A,
B1 and B2. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from pt.json, or one whose English master moved, is REFUSED;
  * PT + KEPT_ENGLISH together must account for EVERY untranslated key of the
    owned sections, so a forgotten string is a refusal, never a silent English.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/validate_translations.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside this batch keeps its exact prior value,
                      the key SET is unchanged, and _meta keeps its v1 shape
                      (version 1, untranslated false) with `translated` moving in
                      lockstep with the bytes: a claimed key must differ from en,
                      an unclaimed key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  typography     pt.json ships ZERO apostrophes (Portuguese needs none:
                      "sua conta", not "sua' conta"), so this batch must not
                      introduce an ASCII or typographic one either;
  G8  affix          leading/trailing whitespace matches the English master, so
                      a concatenative prefix ("Site: ", "Total ", " via ", "Op ")
                      still glues to the value the caller appends;
  G9  aria length    i18n.risk_show_english is read ALOUD at every signing line,
                      so it is capped at 40 characters instead of being padded
                      out to match the English sentence.

Why this batch is the delicate one. trade, barter, proposal, transfer, borrow,
credit, htlc, instant, debit, prediction, vote, createworker, account_net,
txbuilder and approval all render DUAL-LINE inside signing confirmation dialogs:
the user reads this Portuguese with the English one tap away and a warning that
no human checked it. So where a misreading could hide an amount, a destination,
an irreversible action or a permission, the PLainer, more literal wording wins
over the more idiomatic one - "Pagar tudo", not a softened verb; "Total ≈",
"Op incluída: transferência", "Lances de liquidação" keep the English's literal
shape so a reader comparing two lines never has to guess which one hides the
number. Amounts themselves are never retyped: a bare value is Format's job
(AGENTS.md 3.5), so every translated string here carries the same
placeholders, the same op numbers and the same 1.10.N ids the English carries.

The honesty surface (i18n.badge_*, i18n.risk_*) is translated, never left in
English: it is the only warning a Portuguese reader ever gets about their own
Portuguese. Everything else that stays English here is a loanword or a
sentinel, and every one of them is listed in KEPT_ENGLISH with its reason.

KEPT_ENGLISH is the largest part of this batch (about 160 of 270 keys), and that
is the honest answer rather than a dodge: BitShares crypto UIs in Portuguese keep
DEX, HTLC, BitShares, Memo, Swap, Proxy, Smartcoin, Pool, Brainkey, Worker,
Ticket, Vesting, Exchange, Trollbox, Airdrop, Spotlight, Labs and API in
English; "Total", "ID", "Status", "Delta", "Spread", "Log", "Volume", "Base",
"Chain", "Node" and "Feed" are ordinary Portuguese words that happen to be
spelled like English; and the rest is data or glue (op numbers, theme and
network ids, "%(net)s - %(host)s", " (active): ", "—", "…") that must not move
at all. This batch re-asserts chunk B2's pinned English rather than rewriting
it, so the two batches cannot disagree.

Variant: the part of pt.json that is already translated is BRAZILIAN
Portuguese (você, "Carteira", "Navegue", "Trave", "Resgate", "Pools de
Liquidez", "Cadastro"), so this batch is pt-BR too - the informal register
matches the shipped dictionary rather than a European-Portuguese or
formal-register rewrite.

Vocabulary is reused verbatim from pt.json wherever that dictionary has already
settled a word: Carteira, Conta, Ativo, Saldo, Valor, Preço, Quantidade, Ordem
("Criarão de ordem limite"), Operação, Taxa, Transação, Bloco, Colateral,
Precisão, Mercado, Exchange (loanword), Mesa, Swap, Stake, Pool (f.), Cotas LP,
Testemunha, Comitê, Worker, Proxy, Slate, Vesting, Proposta, Ticket, HTLC,
Brainkey, Memo, Gateway, Nó, Chain, Autoridade, Emissor, Produtor, Acordo
(credit.deal), Liquidação (settle), Último/Recente. Where pt.json already had a
sibling string for the same English words, the batch reuses that string's
wording word for word:

  * "Desbloqueie para assinar" is barter.uc_title's own line, reused for
    borrow.uc_title, credit.uc_title, htlc.uc_title, instant.uc_title,
    debit.uc_title and prediction.uc_title;
  * "Desbloqueie para continuar" is trade.uc_title's and pool.uc_title's, so
    transfer.uc_title matches them;
  * "Ver propostas" / "Abrir o construtor de transações" are
    transfer.view_proposals / proposal.open_txbuilder, reused for the two
    auth.multisig_* buttons;
  * "Limpe"/"Limpar", "Mostrando", "Nada é assinado e nada é armazenado",
    "Página", "Carteira bloqueada", "Falha ao desbloquear." and
    "Não foi possível carregar ..." are the shipped shapes;
  * "cotas" for share (pool.shares_field "Cotas LP", help.topic_prediction_body
    "Cotas SIM/NÃO"), never "ações" - "ações" would read as SHARES OF STOCK in
    a pt trading UI, which is the exact misreading a signing dialog cannot
    afford.

One deliberate alignment with an earlier chunk: auth.multisig_step_* uses
"co-proprietário" (asset.multisig_body, asset.multisig_coowner_hint, 2 strings)
rather than proposal.multisig_story's "co-owner" (1 string), so the majority
form spreads and the split is named here instead of left silent.

Numbers: no amount is retyped in a translated string, and no prose number is
invented. Where a translated string quotes a number the English quotes (op 3,
op 21, op 23, op 34, op 45, 1.10.N, 1.2.42, 24h, 7d, 360px) it keeps it
byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_pt_chunkB3.py                 # dry run (asserts)
  python3 tooling/apply_i18n_pt_chunkB3.py --apply         # writes pt.json
  python3 tooling/apply_i18n_pt_chunkB3.py --verify        # structural re-proof
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
PT_PATH = os.path.join(BASE, "pt.json")

# Every section this batch owns: each one still holds at least one key
# byte-equal to en after chunks A, B1 and B2. Sections owned by an earlier
# chunk but already fully translated (account, asset, help bodies, settings
# bodies, ...) are absent from the remaining set and therefore absent here.
SECTIONS = frozenset((
    "about", "account", "account_net", "apilab", "approval", "asset",
    "assets_feed", "auth", "barter", "borrow", "common", "compat", "confirm",
    "createaccount", "createworker", "credit", "dashboard", "debit", "eslab",
    "explorer", "explorer_assets", "gateway", "help", "htlc", "i18n",
    "instant", "market", "market_book", "market_charts", "market_ind",
    "market_net", "market_orders", "menu", "misc", "nav", "news", "notify",
    "pool", "pool_net", "pools", "prediction", "proposal",
    "proposals_ticket", "samet", "settings", "shell", "splash", "swap",
    "ticket", "tickets", "tour", "trade", "transfer", "trollbox", "txbuilder",
    "unlockconfirm", "vesting", "vote", "wallet", "xrate",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from PT below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
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

# G9: the English reference toggle is an aria-label read aloud at every
# signing line; it must not become a sentence.
ARIA_MAX = {"i18n.risk_show_english": 40}


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


PT = {
    # ------------------------------------------------------------ account_net
    # The edge line already reads as placeholders in pt.json
    # (account_net.twin_span "Primeiro → último"), so only the counted noun
    # moves: "ops" is an abbreviation no pt reader parses as a count, while
    # account_net.status_scanned already ships "operações".
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s operações · "
        u"%(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s operação · "
        u"%(kind)s"
    ),
    "account_net.twin_count": u"Operações",

    # -------------------------------------------------------------- approval
    # The extension approval dialog. A permission surface, so the buttons keep
    # the plain verb of the English: Approve/Deny are "Aprovar"/"Recusar", and
    # the result lines name what happened ("Aprovada e transmitida.", not a
    # celebratory "Tudo certo!").
    "approval.account": u"Conta: ",
    "approval.approve": u"Aprovar",
    "approval.approved": u"Aprovada e transmitida.",
    "approval.close": u"Fechar",
    "approval.denied": u"Recusada.",
    "approval.deny": u"Recusar",
    "approval.expires_in": u"Expira em ",
    "approval.load_failed": u"Não foi possível carregar a aprovação.",
    "approval.loading": u"Carregando aprovação…",
    "approval.locked_note": (
        u"Sessão bloqueada — digite a senha da sua carteira para aprovar."
    ),
    "approval.no_fields": u"Nenhum campo para mostrar.",
    "approval.no_reply": u"Nenhuma resposta de quem assinou.",
    "approval.no_runtime": u"Runtime da extensão ausente.",
    "approval.password": u"Senha",
    "approval.remember": u"Lembrar desta conta para este site",
    "approval.title": u"Aprovar assinatura",
    "approval.unknown_intent": u"Nenhum pedido de aprovação encontrado.",
    "approval.wallet_title": u"Esta carteira solicita uma assinatura",

    # ------------------------------------------------------------------- auth
    # The shared-account story. "co-proprietário" is the form asset.multisig_body
    # and asset.multisig_coowner_hint already ship (2 strings) against
    # proposal.multisig_story's single "co-owner"; this batch spreads the
    # majority and the split is named in the report.
    "auth.multisig_body": (
        u"Esta carteira tem uma chave. Contas compartilhadas precisam de "
        u"propostas + aprovações de co-proprietários, coordenadas pelo id da "
        u"proposta (1.10.N). Navegar é público; só a assinatura pede a senha."
    ),
    "auth.multisig_open_proposals": u"Ver propostas",
    "auth.multisig_open_txbuilder": u"Abrir o construtor de transações",
    "auth.multisig_step_approve": (
        u"Os co-proprietários aprovam (op 23) na página de propostas, ou "
        u"assinam juntos pelo construtor de transações."
    ),
    "auth.multisig_step_propose": (
        u"Proponha a operação (Transferência tem Enviar/Propor; ativos, troca "
        u"e empréstimo ligam a propostas)."
    ),
    "auth.multisig_step_share": (
        u"Compartilhe o id da proposta 1.10.N com os co-proprietários."
    ),
    "auth.multisig_title": u"Contas compartilhadas / multisig",

    # ----------------------------------------------------------------- common
    "common.page_n": u"Página %(n)s",
    "common.unknown_asset": u"Ativo desconhecido.",

    # ----------------------------------------------------------------- compat
    "compat.insecure_hint": (
        u"Este endereço não é um contexto seguro, então o navegador não "
        u"libera o WebCrypto. O navegador está atualizado — sirva por https "
        u"ou localhost, ou abra o arquivo direto."
    ),

    # ---------------------------------------------------------- createaccount
    # The three step chips: Brainkey keeps the loanword (B1 shipped
    # "Brainkey (faça backup)" and "Gerar nova brainkey").
    "createaccount.step_name": u"Nome",
    "createaccount.step_register": u"Registrar",

    # ------------------------------------------------------------ createworker
    # A worker creation is a DIRECT op, not a proposal, and the English says so
    # in the same breath; keeping that clause is what stops a reader from
    # waiting for co-owner approvals that will never come.
    "createworker.confirm_worker_op_34": u"Confirmar worker (op %(op)s)",
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        u"Escreva um worker (op %(op)s). A prévia é ao vivo; a revisão cota a "
        u"taxa ao vivo, e então Assinar e enviar transmite a op %(op)s "
        u"diretamente — workers são criados por op direta, não por proposta."
    ),
    "createworker.worker_preview_op_34": u"Prévia do worker (op %(op)s)",

    # ----------------------------------------------------------------- credit
    # "Acordo" is credit.deal's own shipped word (28 strings), never "negócio".
    "credit.my_deals_borrower": u"Meus acordos (mutuário)",
    "credit.no_borrower_deals": (
        u"Nenhum acordo de mutuário ainda — os acordos aparecem depois que você "
        u"toma emprestado contra uma oferta."
    ),
    "credit.uc_title": u"Desbloqueie para assinar",

    # -------------------------------------------------------------- dashboard
    # "Navegue nos mercados de graça" is splash.hero_sub2's own clause.
    "dashboard.tagline": (
        u"Navegue nos mercados de graça — crie uma carteira para negociar."
    ),
    "dashboard.welcome": u"Negocie BTS com as chaves que você tem",

    # ------------------------------------------------------------------ debit
    "debit.uc_order": u"Ordem",
    "debit.uc_title": u"Desbloqueie para assinar",

    # ------------------------------------------------------------------ eslab
    # "divida pela precisão do ativo" is eslab.hint_holders's own clause.
    "eslab.hint_donors": (
        u"Contagens na janela; totais são inteiros brutos — divida pela "
        u"precisão do ativo."
    ),

    # ---------------------------------------------------------------- gateway
    # The deposit half of a bridge: the only sentence that must NOT read as
    # "this page moves your money". "Esta página não transmite nada." is
    # gateway.send_external_suffix's own clause.
    "gateway.intro_a": (
        u"Envie suas moedas externas para o endereço mostrado. Esta página não "
        u"transmite nada. "
    ),
    "gateway.intro_b": (
        u"Os saques terminam em Transferência com uma prévia da taxa ao vivo."
    ),

    # ------------------------------------------------------------------- help
    # The nine remaining help titles are page NAMES, and every one of them
    # matches its page: menu.p_dashboard and nav.dashboard already ship "Painel",
    # so the dashboard article is titled "Painel" too. The other eight keep
    # their English page name (Airdrops, API Lab, Backups, Blockchain, ES Lab,
    # Gateways, Spotlight, Workers) - see KEPT_ENGLISH.
    "help.topic_dashboard_title": u"Painel",

    # ------------------------------------------------------------------- htlc
    "htlc.hash_field": u"Hash em hex",
    "htlc.list_sub": (
        u"Trave fundos a um hash — quem recebe resgata com o segredo antes da "
        u"expiração, ou você é reembolsado. Qualquer um pode ler; a senha é "
        u"pedida só na assinatura."
    ),
    "htlc.uc_title": u"Desbloqueie para assinar",

    # -------------------------------------------------------------------- i18n
    # THE HONESTY SURFACE. These are the only words a Portuguese reader ever
    # gets about their own Portuguese, so they are translated rather than left
    # in English - and they are stated as plainly as possible: a machine wrote
    # this, no person checked it, and the original English is right there.
    # "confiro"/"conferidas" matches help.topic_translation-limitations_body's
    # "ninguém a leu para conferir". risk_show_english is an aria-label read
    # aloud at every signing line, so it is the SHORT form (gate G9).
    "i18n.badge_body": (
        u"Estas traduções foram escritas por uma máquina e não foram "
        u"conferidas por uma pessoa. Linhas marcadas com * nas telas de "
        u"assinatura também mostram o inglês original."
    ),
    "i18n.badge_details": u"O que isso significa",
    "i18n.badge_improve": u"Ajude a melhorar esta tradução",
    "i18n.badge_label": (
        u"Estado da tradução: traduzida por máquina, não verificada por uma "
        u"pessoa"
    ),
    "i18n.risk_about_translations": u"Sobre estas traduções",
    "i18n.risk_show_english": u"Mostrar o inglês desta linha",

    # ---------------------------------------------------------------- instant
    # "Preencher ou matar" is trade.row_fok / trade.fok_label's own wording.
    "instant.fill_or_kill": u"Preencher ou matar",
    "instant.preview_balances_note": (
        u"Visualizando como %(name)s (%(id)s) — saldos não conferidos. "
        u"Desbloqueie para validar os seus antes de assinar."
    ),
    "instant.uc_title": u"Desbloqueie para assinar",
    "instant.unlock_sign": u"Desbloqueie e assine",

    # ------------------------------------------------------------ market_ind
    # "velas" is market_ind.candle_count's own word (chunk A) and pool_detail's
    # (chunk B2) - "candles" is not a word a pt chart reader parses.
    "market_ind.count_capped": u"janela truncada",
    "market_ind.count_note": u"%(count)s × %(bucket)s velas",
    "market_ind.count_partial": (
        u"%(actual)s de %(requested)s × %(bucket)s velas"
    ),

    # -------------------------------------------------------------------- nav
    # The compact nav bar. exchange/pools keep the venue and pool loanwords
    # (nav.exchange, nav.pools already ship those bytes elsewhere); the other
    # three move to the words the same bar already uses for their pages
    # (account_net.class_credit "Crédito", borrow.borrow_margin
    # "Empréstimo (Margem)", market_net.title "Mercados").
    "nav.credit": u"Crédito",
    "nav.margin": u"Margem",
    "nav.markets": u"Mercados",

    # ------------------------------------------------------------------- news
    "news.explorer_blocks_and_transactions": u"Explore a chain",

    # ------------------------------------------------------------------ pools
    # "Seletor de pools" matches market_net.selector_title "Seletor de
    # mercados" and pools.title "Pools de Liquidez".
    "pools.selector_title": u"Seletor de pools",

    # ------------------------------------------------------------ prediction
    "prediction.uc_title": u"Desbloqueie para assinar",

    # ------------------------------------------------------------------- tour
    # The tour's own words; s2 and s5 were shipped by an earlier chunk and
    # this batch keeps their register ("mesa de negociação", "o exchange").
    "tour.away_note": (
        u"Na mesa Exchange — abra-a para ver isto destacado."
    ),
    "tour.s1_body": (
        u"Toda página lê dados públicos da chain sem login. Abra um mercado "
        u"para começar — sua senha é pedida só na assinatura."
    ),
    "tour.s1_title": u"Navegue em tudo de graça, assine localmente",
    "tour.s3_body": (
        u"Velas de preço, volume e profundidade, mais o menu de indicadores: "
        u"sobreposições como SMA e EMA, osciladores como RSI, MACD e "
        u"Estocástico. Abra o exchange para ver ao vivo."
    ),
    "tour.s3_title": u"Veja gráficos de preço ao vivo",
    "tour.s4_body": (
        u"Os painéis Comprar e Vender aceitam qualquer número para treinar. "
        u"Nada sai da sua máquina até você revisar e assinar com a carteira "
        u"desbloqueada. Abra o exchange para experimentar."
    ),
    "tour.s4_title": u"Pratique comprar e vender",

    # --------------------------------------------------------------- transfer
    # The most dangerous strings in the batch: a destination, a proposer and an
    # enclosed op. The English shapes are kept literally - "Op incluída:
    # transferência (op N)" names the op and the type, and the locked-proposer
    # notice keeps "enquanto bloqueado" so nobody signs as committee-account
    # by accident.
    "transfer.confirm_proposal_title": u"Confirmar proposta (op %(op)s)",
    "transfer.enclosed_op_note": (
        u"Op incluída: transferência (op %(op)s) — só executa após as "
        u"aprovações."
    ),
    "transfer.propose_notice_locked": (
        u"O proponente é %(name)s (%(id)s) enquanto bloqueado — desbloqueie "
        u"para agir como você mesmo."
    ),
    "transfer.share_needs_to_amount": (
        u"Um link compartilhável precisa de um destinatário e de um valor."
    ),
    "transfer.uc_title": u"Desbloqueie para continuar",
    "transfer.unlock_sign": u"Desbloqueie e revise",

    # -------------------------------------------------------------- txbuilder
    "txbuilder.link_proposals": u"Propostas",

    # ---------------------------------------------------------- unlockconfirm
    "unlockconfirm.cancel": u"Voltar",
    "unlockconfirm.empty_password": u"Digite a senha da sua carteira.",
    "unlockconfirm.password": u"Senha",
    "unlockconfirm.unlock_failed": u"Falha ao desbloquear.",
    "unlockconfirm.unlock_post": u"Desbloqueie e publique",

    # ------------------------------------------------------------------ vote
    # The vote slate is the loanword slate (vote.sent_middle already ships
    # "o novo slate não foi observado"), and "self" stays untranslated because
    # it is a voting_account value a reader can verify on chain.
    "vote.ballot_intro": (
        u"Seu stake elege testemunhas e comitê e financia workers — todas as "
        u"contagens e cotas abaixo são leituras ao vivo da chain."
    ),
    "vote.confirm_witness_update_op_21": (
        u"Confirmar atualização de testemunha (op %(op)s)"
    ),
    "vote.direct_note": u"Votação publicada diretamente (voting_account %(id)s).",
    "vote.in_sync": u"O slate de votos bate com a chain — nada para publicar.",
    "vote.proxies_follow_another_account_s_slate_re": (
        u"Proxies seguem o slate de votos de outra conta — leia como a votação "
        u"funciona antes de definir um."
    ),
    "vote.proxy_follows": (
        u" — seu stake segue esta conta; o slate de votos abaixo é somente "
        u"leitura."
    ),
    "vote.retried_prefix": (
        u"O nó rejeitou o modo proxy %(mode)s, então o voto foi publicado como "
        u"self (voting_account %(id)s)."
    ),
    "vote.retry_self": (
        u"O nó rejeitou o modo proxy %(mode)s — tentando mais uma vez como "
        u"self…"
    ),

    # ----------------------------------------------------------------- borrow
    # The margin desk. "Pagar tudo" for Repay in full, and the two confirm
    # titles keep the op number and the position wording the button acts on.
    "borrow.adjust": u"Ajustar",
    "borrow.adjust_position_op_3": u"Ajustar posição (op %(op)s)",
    "borrow.bids_no_cancel": (
        u"Lances não podem ser cancelados depois de feitos — eles são "
        u"executados ou expiram."
    ),
    "borrow.close_position": u"Fechar posição",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        u"Posições de margem tomam um bitasset emprestado contra colateral. "
        u"Reforçar o colateral ou pagar a dívida ajusta a posição pela op "
        u"%(op)s (call_order_update) na sua ordem de margem."
    ),
    "borrow.open_a_new_position_op_3": u"Abrir nova posição (op %(op)s)",
    "borrow.repay_full": u"Pagar tudo",
    "borrow.settlement_bids_op_45": u"Lances de liquidação (op %(op)s)",
    "borrow.uc_title": u"Desbloqueie para assinar",
}

# Keys whose Portuguese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from PT. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift. This is the majority of the
# batch, in five honest families:
#
#   1. product / protocol names a Brazilian crypto UI keeps in English:
#      Exchange, HTLC, Vesting, Tickets, Ticket, Airdrop, Spotlight, Trollbox,
#      Cross Rates, Labs, Worker, Brainkey, Memo, Bitasset, Smartcoin, PMA,
#      UIA, NFT, Swap, API Lab, ES Lab, Blockchain, Backups, Workers;
#   2. ordinary Portuguese words that happen to be spelled like English and are
#      already the shipped form of their row: Total (and its "Total " prefix
#      and "Total ≈ " label), ID, Menu, Status, Delta, PnL, Log, Volume, Vol,
#      Spread, Base, Chain, Feed, Info, Upgrade, Pool, Pools, Ok, Ok;
#   3. technical tokens with no Portuguese form that a pt reader would
#      recognise: Ping, Handshake, Head, MCR, MSSR, SMA, EMA, BB, PSAR, Op,
#      Tx, Trx/s, URL, API, NFT, PMA, UIA, core, raw, via, base, smartcoin;
#   4. DATA: asset symbols, object ids (1.2.42), op numbers, theme ids, network
#      ids, and the wss:// placeholder - none of these may move;
#   5. pure GLUE: prefixes and suffixes the caller concatenates
#      ("): ", " (active): ", " (owner): ", " [op ", "Op ", "Tx ", "base ",
#      "raw: ", " via ", " (core)", " (virtual)", "—", "…", "final: ",
#      "expands_in_utc", "%(net)s - %(host)s"), plus the arrow-only
#      account_net.detail_span.
KEPT_ENGLISH = {
    # ---- about (chunk B2's build-dialog heading, re-asserted)
    "about.dlg_heading": u"Full build dialog",
    "about.dlg_heading_c": u"Full build dialog (%(total)s)",

    # ---- account
    # "Total ≈ " is the Total family plus the ≈ glyph (account.page_total
    # already ships "Total da página ≈ "); "Upgrade" is the noun pt.json
    # already uses in account.op_upgrade / account.upgrade_btn.
    "account.total": u"Total ≈ ",
    "account.upgrade_row_upgrade": u"Upgrade",

    # ---- account_net
    "account_net.class_htlc": u"HTLC",
    "account_net.class_vesting": u"Vesting",
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",

    # ---- apilab / eslab / compat-less pages
    "apilab.title": u"API Lab",
    "eslab.title": u"ES Lab",

    # ---- asset
    "asset.bitasset_row": u"Bitasset",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.op_col": u"Op",
    "asset.smartcoin_row": u"Smartcoin",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",

    # ---- sentinels
    "assets_feed.s1": u"—",
    "explorer_assets.s1": u"—",
    "market.stat_empty": u"—",
    "settings.dash": u"—",

    # ---- barter
    "barter.paid_by_suffix": u"): ",

    # ---- confirm / proposal / misc / ticket / vesting authority labels
    "confirm.memo": u"Memo",
    "proposal.active_suffix": u" (active): ",
    "proposal.id": u"ID",
    "proposal.memo": u"Memo",
    "proposal.owner_suffix": u" (owner): ",
    "proposal.ticket": u"Ticket",
    "misc.id": u"ID",

    # ---- credit / samet / trade / txbuilder / market: the Total family and
    #      the "ops"/Delta unit labels
    "credit.delta": u"Delta",
    "credit.total": u"Total",
    "credit.total_prefix": u"Total ",
    "instant.total": u"Total",
    "samet.delta": u"Delta",
    "trade.row_total": u"Total",
    "txbuilder.total_prefix": u"Total ",
    "vesting.total": u"Total",

    # ---- createworker
    "createworker.url": u"URL",
    "vote.url": u"URL",

    # ---- approval: the two prefixes that are already the Portuguese form.
    # "Site:" is settings.sign_sites' own word ("Sites conectados") and "Chain:"
    # is the chain loanword this dictionary uses for the ledger everywhere
    # (txbuilder.chain_prefix, settings.th_chain), so neither moves; only the
    # account prefix does, because "Account:" would be the one English noun
    # left on a permission dialog.
    "approval.chain": u"Chain: ",
    "approval.site_prefix": u"Site: ",

    # ---- createaccount
    "createaccount.step_brainkey": u"Brainkey",

    # ---- debit
    "debit.spotlight_title": u"Spotlight",

    # ---- explorer: data, acronyms, sort glyphs and pure glue
    "explorer.assets_mode_market": u"SmartCoins",
    "explorer.core_suffix": u" (core)",
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.info_h": u"INFO",
    "explorer.markets_sort_vol_asc": u"Volume ↑",
    "explorer.markets_sort_vol_desc": u"Volume ↓",
    "explorer.op_badge_prefix": u" [op ",
    "explorer.op_prefix": u"Op ",
    "explorer.price_base": u"base ",
    "explorer.stat_tps": u"Trx/s",
    "explorer.tab_blocks": u"Blockchain",
    "explorer.th_feed": u"Feed",
    "explorer.th_mssr": u"MSSR",
    "explorer.tx_prefix": u"Tx ",
    "explorer.virtual_mark": u" (virtual)",

    # ---- gateway
    "gateway.health_ok": u"ok ",
    "gateway.raw_prefix": u"raw: ",
    "gateway.via": u" via ",

    # ---- help: the eight page-name titles that match their page
    "help.topic_airdrop_title": u"Airdrops",
    "help.topic_api-lab_title": u"API Lab",
    "help.topic_backups_title": u"Backups",
    "help.topic_blockchain_title": u"Blockchain",
    "help.topic_es-lab_title": u"ES Lab",
    "help.topic_gateways_title": u"Gateways",
    "help.topic_spotlight_title": u"Spotlight",
    "help.topic_workers_title": u"Workers",

    # ---- htlc
    "htlc.hash_label": u"Hash: ",
    "htlc.title": u"HTLC",

    # ---- i18n
    "i18n.badge_chip": u"i18n",

    # ---- instant / market_net / market / market_book / market_charts /
    #      market_orders: glue and unit labels
    "instant.via_mid": u" via ",
    "market.chg_label": u"24h Δ",
    "market.discrete_swaps": u"swaps",
    "market.discrete_tip_volume": u"Volume",
    "market.log_label": u"Log",
    "market.map_edge_price": u"@ %(price)s · %(vol)s",
    "market.ov_bb": u"BB",
    "market.ov_ema": u"EMA",
    "market.ov_psar": u"PSAR",
    "market.ov_sma": u"SMA",
    "market.stat_chg": u"24h Δ",
    "market.th_total": u"Total",
    "market.title": u"Exchange",
    "market.vol_label": u"Vol",
    "market.vol_lin": u"Vol: Linear",
    "market.vol_log": u"Vol: Log",
    "market_book.spread_prefix": u"Spread ",
    "market_book.title": u"Exchange",
    "market_charts.title": u"Exchange",
    "market_orders.title": u"Exchange",
    "market_net.col_change": u"24h Δ",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",

    # ---- menu (chunk B2's burger labels, re-asserted)
    "menu.p_airdrop": u"Airdrop",
    "menu.p_exchange": u"Exchange",
    "menu.p_htlc": u"HTLC",
    "menu.p_spotlight": u"Spotlight",
    "menu.p_tickets": u"Tickets",
    "menu.p_trollbox": u"Trollbox",
    "menu.p_vesting": u"Vesting",
    "menu.p_xrates": u"Cross Rates",
    "menu.section_labs": u"Labs",
    "menu.title": u"Menu",

    # ---- nav
    "nav.exchange": u"Exchange",
    "nav.pools": u"Pools",

    # ---- notify
    "notify.base_label": u"Base",

    # ---- pool / pool_net / pools
    "pool.pool_row": u"Pool",
    "pool.stake_link": u"Stake",
    "pool.swap_stake_col": u"Swap/Stake",
    "pool_net.col_pool": u"Pool",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pools · %(hops)s",

    # ---- prediction
    "prediction.hdr_status": u"Status",
    "prediction.pnl": u"PnL",

    # ---- settings: headers and ids
    "settings.custom_placeholder": u"wss://…",
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.pending": u"…",
    "settings.th_chain": u"Chain",
    "settings.th_handshake": u"Handshake",
    "settings.th_head": u"Head",
    "settings.th_ping": u"Ping",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",

    # ---- shell (chunk B2's footer and burger labels, re-asserted)
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    "shell.menu": u"Menu",

    # ---- splash
    "splash.card_dex_t": u"Exchange",
    "splash.card_pool_t": u"Pools",

    # ---- swap / tickets / ticket
    "swap.title": u"Swap",
    "proposals_ticket.title": u"Tickets",
    "tickets.title": u"Tickets",
    "ticket.airdrop": u"Airdrop",
    "ticket.airdrop_example_ph": u"alice,10\nbob,2.5",
    "ticket.id": u"ID",
    "ticket.ticket": u"Ticket",
    "ticket.tickets": u"Tickets",

    # ---- transfer
    "transfer.bad_asset_shape": u"bad-asset-shape",

    # ---- trollbox (chunk B2's, re-asserted)
    "trollbox.bytes_prefix": u"Bytes: ",
    "trollbox.bytes_unit": u"bytes",
    "trollbox.title": u"Trollbox",

    # ---- txbuilder
    "txbuilder.badge_tpl": u"TxBuilder (%(n)s)",
    "txbuilder.chain_prefix": u"Chain: ",
    "txbuilder.link_pools": u"Pools",

    # ---- vesting
    "vesting.id": u"ID",
    "vesting.title": u"Vesting",
    "vesting.vesting": u"Vesting",

    # ---- vote
    "vote.proxy_prefix": u"Proxy: ",
    "vote.proxy_row": u"Proxy",
    "vote.row_final": u"final: ",
    "vote.tab_workers": u"Workers (",

    # ---- wallet
    "wallet.brainkey": u"Brainkey",

    # ---- xrate
    "xrate.title": u"Cross Rates",
    "xrate.token_placeholder": u"USD, CNY, BTC…",
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


def edge_space(value):
    """(leading, trailing) run lengths - the affixes a caller concatenates."""
    return (len(value) - len(value.lstrip()),
            len(value) - len(value.rstrip()))


def check_batch(en_flat, key, value, problems):
    """G1-G4 + G8/G9 + punctuation hygiene for one key/value pair."""
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
            "line count changed: %s (en %d, pt %d)"
            % (key, master.count("\n"), value.count("\n"))
        )
    if LINK_HASH.findall(master) != LINK_HASH.findall(value):
        problems.append("link hash changed: %s" % key)
    if edge_space(master) != edge_space(value):
        problems.append(
            "affix changed: %s (en %r, pt %r)"
            % (key, edge_space(master), edge_space(value))
        )
    cap = ARIA_MAX.get(key)
    if cap is not None and len(value) > cap:
        problems.append(
            "aria-label too long: %s (%d chars, cap %d)"
            % (key, len(value), cap)
        )
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_apostrophe(batch, problems):
    """G7: pt.json ships zero apostrophes, so this batch must add none.

    Portuguese does not need them for possession ("sua conta"), and none of the
    thousands of strings already translated in pt.json carries one - so a stray
    ' or ’ here would be the only such spelling in the whole dictionary.
    """
    for key, value in sorted(batch.items()):
        if APO_ASCII in value:
            problems.append("G7: ASCII apostrophe in %s" % key)
        if APO_TYPO in value:
            problems.append("G7: typographic apostrophe in %s" % key)


def verify():
    """Structural re-proof of the shipped file against the en master."""
    pt, en = load(PT_PATH), load(EN_PATH)
    d, e = flat(pt), flat(en)
    bad = []
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    affixes = affixes_ok = 0
    for key in sorted(PT):
        if key not in d:
            bad.append("key missing from pt.json: %s" % key)
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
        if e[key] != e[key].strip() or d[key] != d[key].strip():
            affixes += 1
            if edge_space(e[key]) == edge_space(d[key]):
                affixes_ok += 1
        hit = suspicious(d[key])
        if hit:
            bad.append(
                "suspicious code point U+%04X in %s" % (ord(hit), key)
            )
    check_apostrophe(PT, bad)

    for key in PINNED:
        if key in d and d[key] != e.get(key):
            bad.append("pinned key not byte-verbatim: %s" % key)

    same = [k for k in sorted(PT) if d.get(k) == e.get(k)]
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
        and k not in PT and k not in KEPT_ENGLISH
    ]

    print("verify: %d/%d keys of this batch differ from the en master"
          % (len(PT) - len(same), len(PT)))
    print("  keys kept byte-identical to en on purpose: %d"
          % (len(KEPT_ENGLISH) + len(same)))
    print("  placeholder-bearing strings in batch    : %d (multiset ok: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values in batch              : %d (line count ok: %d)"
          % (multi, multi_ok))
    print("  values carrying a markdown link hash    : %d (hashes ok: %d)"
          % (links, links_ok))
    print("  values with a leading/trailing affix   : %d (affix ok: %d)"
          % (affixes, affixes_ok))
    for sec in sorted(by_section):
        print("    %-12s %d identical to en" % (sec, by_section[sec]))
    print("  keys in my sections still at en, not in this batch: %d"
          % len(scope_left))
    for k in scope_left:
        print("      %s = %r" % (k, d.get(k)))
    meta = pt.get("_meta", {})
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
    raw = open(PT_PATH, encoding="utf-8").read()
    pt = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(pt, indent=2, ensure_ascii=False) + "\n" != raw:
        print("REFUSING: pt.json formatting is not "
              "indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(pt))
    before_meta = json.dumps(pt["_meta"], sort_keys=True, ensure_ascii=False)
    en_flat = flat(load(EN_PATH))

    problems = []
    planned = []
    for key, value in sorted(PT.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in pt.json: %s" % key)
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
        deep_set(pt, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    both = sorted(set(PT) & set(KEPT_ENGLISH))
    if both:
        print("REFUSING: listed twice (PT and KEPT_ENGLISH): %s"
              % ", ".join(both[:5]))
        return 1
    owned = set(PT) | set(KEPT_ENGLISH)
    for key, value in sorted(KEPT_ENGLISH.items()):
        if key.split(".")[0] not in SECTIONS:
            print("REFUSING: out of scope: %s" % key)
            return 1
        if key not in en_flat:
            print("REFUSING: not in en master: %s" % key)
            return 1
        if key not in before:
            print("REFUSING: not in pt.json: %s" % key)
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

    check_apostrophe(PT, problems)
    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch moved, and the key set is unchanged.
    after = flat(pt)
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
    # UNCLAIMED, which is the honest state for them. Nothing else in _meta
    # moves - filling strings is not verification, so the controller's v2
    # provenance/verified/high_risk fields stay untouched.
    meta = pt["_meta"]
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
    added = sorted(k for k in PT
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

    print("pt chunk-B3: %d planned, %d differ from en, %d intentionally "
          "identical" % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-16s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    print("  keys kept identical to en on purpose: %d"
          % len(KEPT_ENGLISH))
    if same_as_en:
        print("  identical-to-en in PT (listed anyway - deliberately NOT "
              "claimed): %s" % ", ".join(same_as_en))
    if not apply:
        print("dry run - no files written (pass --apply)")
        return 0

    with open(PT_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(pt, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/pt.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
