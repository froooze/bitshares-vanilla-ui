#!/usr/bin/env python3
"""i18n pt chunk-A: fill the six "core desk" sections of vanilla/locales/pt.json
(account, account_net, settings, market, market_net, asset) that the wallet
already half-translates. chunk-B (_chunkB.py) owns everything else and REFUSES
these six as out of scope.

Scope: ONLY the six sections listed below. The script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from pt.json, or one whose English master moved, is REFUSED;
  * PT + KEPT_ENGLISH together must account for EVERY untranslated key of the
    six sections, so a forgotten string is a refusal, never a silent English.

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
                      an untranslated key must still equal en. Filling strings is
                      not verification, so the controller's v2 provenance /
                      verified / high_risk fields are never touched here;
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                      newline round-trips the untouched file byte-for-byte;
  G7  typography     pt.json ships ZERO apostrophes (Portuguese needs none:
                      "sua conta", not "sua' conta"), so this batch must not
                      introduce an ASCII or typographic one either.

Variant: the part of pt.json that was already translated is BRAZILIAN
Portuguese (it, for example, says "Digite sua senha" / "Carteira bloqueada" and
"usuário" for user-issued assets), so this batch is pt-BR too. The informal
"você" register and the imperative "Digite ..." therefore match the shipped
dictionary rather than a European-Portuguese or formal-register rewrite.

Vocabulary is reused verbatim from pt.json wherever that dictionary has already
settled a word: conta (m.), ativo (m.), saldo, ordem, execução, preço,
quantidade, proposta, taxa, comitê, testemunha, emissor, publicador, produtor,
colateral, colateral de garantia, chain (loanword, f.), nó (m.), carteira (f.),
pool (f.), swap, stake, smartcoin, bitasset, HTLC, DEX, API, feed, memo,
brainkey (f.), vesting, ticket, worker, proxy, slate. Nothing is invented where
a Portuguese crypto UI keeps the English word - the run prints every value that
stays identical to en, so a reviewer checks the list instead of guessing.

The honesty surface and every signing-adjacent string are deliberately plain:
an amount, a destination, an irreversible action or a permission is named the
way the English names it.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where a
translated string quotes a number the English quotes (24h, 360px, 4K, op 23,
1.10.N, 1.2.N) it keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_pt_chunkA.py                 # dry run (asserts)
  python3 tooling/apply_i18n_pt_chunkA.py --apply         # writes pt.json
  python3 tooling/apply_i18n_pt_chunkA.py --verify        # structural re-proof
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

# The six sections this batch owns. Everything else is chunk-B's, and is
# REFUSED here as out of scope - a key that crosses the line is a reviewer's
# problem, never this script's silent edit.
SECTIONS = frozenset((
    "account", "account_net", "settings", "market", "market_net", "asset",
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
EM = u"—"


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
    # ---------------------------------------------------------------- account
    # op labels: the nominal "ação de objeto" shape pt.json already ships
    # ("Criação de ativo", "Atualização de conta", "Execução de ordem").
    "account.draw_network": u"Desenhar rede",
    "account.multisig_checking": u"Verificando autoridades…",
    "account.multisig_open_txbuilder": u"Abrir construtor de transações",
    "account.multisig_shared": (
        u"Conta compartilhada — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        u"Chave única — active %(ath)s/%(an)s · owner %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        u"Conta compartilhada? As propostas ficam na página de propostas."
    ),
    "account.multisig_unavailable": (
        u"Autoridades indisponíveis — as propostas continuam listadas na página "
        u"de propostas."
    ),
    "account.multisig_view_proposals": u"Ver propostas",
    "account.op_assert_op": u"Afirmação",
    "account.op_asset_burn": u"Queima de ativo",
    "account.op_asset_issue": u"Emissão de ativo",
    "account.op_asset_settle": u"Liquidação de ativo",
    "account.op_asset_update": u"Atualização de ativo",
    "account.op_authority_create": u"Criação de autoridade",
    "account.op_authority_delete": u"Exclusão de autoridade",
    "account.op_authority_update": u"Atualização de autoridade",
    "account.op_balance_claim": u"Resgate de saldo",
    "account.op_blind_from": u"Transferência de cego",
    "account.op_blind_to": u"Transferência para cego",
    "account.op_blind_transfer": u"Transferência cega",
    "account.op_claim_fees": u"Resgate de taxas",
    "account.op_claim_pool": u"Resgate do pool",
    "account.op_collateral_bid": u"Lance de colateral",
    "account.op_committee_join": u"Entrada no comitê",
    "account.op_committee_update": u"Atualização do comitê",
    "account.op_custom_op": u"Operação personalizada",
    "account.op_deal_expired": u"Acordo expirado",
    "account.op_deal_repay": u"Pagamento de acordo",
    "account.op_deal_update": u"Atualização de acordo",
    "account.op_debit_claim": u"Resgate de débito direto",
    "account.op_debit_create": u"Criação de débito direto",
    "account.op_debit_delete": u"Exclusão de débito direto",
    "account.op_debit_update": u"Atualização de débito direto",
    "account.op_execute_bid": u"Execução de lance",
    "account.op_fba_distribute": u"Distribuição de FBA",
    "account.op_fee_pool_fund": u"Financiamento do pool de taxas",
    "account.op_feed_producers_update": u"Atualização de produtores de feed",
    "account.op_feed_publish": u"Publicação de feed",
    "account.op_global_settle": u"Liquidação global",
    "account.op_htlc_create": u"Criação de HTLC",
    "account.op_htlc_extend": u"Extensão de HTLC",
    "account.op_htlc_redeem": u"Resgate de HTLC",
    "account.op_htlc_redeemed": u"HTLC resgatado",
    "account.op_htlc_refund": u"Reembolso de HTLC",
    "account.op_issuer_update": u"Atualização do emissor",
    "account.op_offer_accept": u"Aceite de crédito",
    "account.op_offer_create": u"Criação de oferta de crédito",
    "account.op_offer_delete": u"Exclusão de oferta de crédito",
    "account.op_offer_update": u"Atualização de oferta de crédito",
    "account.op_order_update": u"Atualização de ordem",
    "account.op_override_transfer": u"Transferência com override",
    "account.op_params_update": u"Atualização de parâmetros globais",
    "account.op_pool_create": u"Criação de pool",
    "account.op_pool_delete": u"Exclusão de pool",
    "account.op_pool_deposit": u"Depósito em pool",
    "account.op_pool_swap": u"Swap em pool",
    "account.op_pool_update": u"Atualização de pool",
    "account.op_pool_withdraw": u"Retirada de pool",
    "account.op_proposal_create": u"Criação de proposta",
    "account.op_proposal_delete": u"Exclusão de proposta",
    "account.op_proposal_update": u"Atualização de proposta",
    "account.op_samet_borrow": u"Empréstimo Same-T",
    "account.op_samet_create": u"Criação de fundo Same-T",
    "account.op_samet_delete": u"Exclusão de fundo Same-T",
    "account.op_samet_update": u"Atualização de fundo Same-T",
    "account.op_samet_repay": u"Pagamento Same-T",
    "account.op_settle_cancel": u"Cancelamento de liquidação",
    "account.op_smartcoin_update": u"Atualização de smartcoin",
    "account.op_ticket_create": u"Criação de ticket",
    "account.op_ticket_update": u"Atualização de ticket",
    "account.op_vesting_create": u"Criação de vesting",
    "account.op_vesting_withdraw": u"Retirada de vesting",
    "account.op_witness_join": u"Entrada como testemunha",
    "account.op_witness_update": u"Atualização de testemunha",
    "account.op_worker_create": u"Criação de worker",
    "account.page_total": u"Total da página ≈ ",
    "account.portfolio_page": u"Página %(page)s de %(pages)s",
    "account.prices_cover_this_page": (
        u"Os preços cobrem esta página — vire a página para precificar mais "
        u"ativos."
    ),
    # History one-liners. Every one names the action, the amount slot and the
    # counterparty slot in the order the English names them.
    "account.sum_account_create": u"Conta %(name)s registrada",
    "account.sum_account_transfer": u"Conta transferida para %(owner)s",
    "account.sum_account_update": u"Conta atualizada: %(account)s",
    "account.sum_asset_burn": u"%(amount)s queimados",
    "account.sum_asset_create": u"Ativo %(symbol)s criado",
    "account.sum_asset_issue": u"%(amount)s emitidos para %(to)s",
    "account.sum_asset_settle": u"Liquidação de %(amount)s solicitada",
    "account.sum_asset_update": u"Ativo %(asset)s atualizado",
    "account.sum_authorities": u"Autoridades de %(account)s atualizadas",
    "account.sum_balance_claim": u"%(amount)s resgatados",
    "account.sum_bid": u"Lance de %(coll)s por %(debt)s",
    "account.sum_blind": (
        u"Transferência cega (%(in)s entrando, %(out)s saindo)"
    ),
    "account.sum_call_update": (
        u"Posição ajustada: %(coll)s de colateral, %(debt)s de dívida"
    ),
    "account.sum_claim_fees": u"%(amount)s em taxas resgatados",
    "account.sum_committee_create": u"Tornou-se membro do comitê: %(account)s",
    "account.sum_committee_update": u"Membro do comitê %(account)s atualizado",
    "account.sum_custom": u"Operação personalizada por %(account)s",
    "account.sum_deal_expired": u"Acordo %(deal)s expirado",
    "account.sum_deal_repay": u"%(amount)s pagos no acordo %(deal)s",
    "account.sum_deal_update": u"Acordo %(deal)s atualizado",
    "account.sum_debit_claim": u"Débito de %(amount)s resgatado",
    "account.sum_debit_create": u"Débito de %(amount)s autorizado para %(to)s",
    "account.sum_debit_delete": u"Permissão de débito %(perm)s excluída",
    "account.sum_debit_update": u"Débito de %(amount)s atualizado para %(to)s",
    "account.sum_execute_bid": u"Lance %(coll)s executado por %(debt)s",
    "account.sum_fee_pool_fund": (
        u"Pool de taxas de %(asset)s financiado com %(amount)s"
    ),
    "account.sum_feed": (
        u"Feed publicado para %(asset)s por %(publisher)s"
    ),
    "account.sum_feed_producers": (
        u"%(n)s produtores de feed definidos para %(asset)s"
    ),
    "account.sum_fill": u"Executada: pagou %(pays)s, recebeu %(receives)s",
    "account.sum_global_settle": u"%(asset)s liquidado globalmente",
    "account.sum_htlc_claimed": u"HTLC %(id)s resgatado",
    "account.sum_htlc_create": (
        u"HTLC %(id)s: %(amount)s de %(from)s para %(to)s"
    ),
    "account.sum_htlc_extend": u"HTLC %(id)s estendido",
    "account.sum_htlc_redeem": u"HTLC %(id)s resgatado",
    "account.sum_htlc_refund": u"HTLC %(id)s reembolsado",
    "account.sum_issuer_update": u"Novo emissor de %(asset)s: %(issuer)s",
    "account.sum_offer_accept": (
        u"%(amount)s emprestados contra %(coll)s (oferta %(offer)s)"
    ),
    "account.sum_offer_create": u"Oferta de crédito criada em %(asset)s",
    "account.sum_offer_delete": u"Oferta %(offer)s excluída",
    "account.sum_offer_update": u"Oferta %(offer)s atualizada",
    "account.sum_order_cancel": u"Ordem %(order)s cancelada",
    "account.sum_order_create": u"%(sell)s oferecidos por pelo menos %(buy)s",
    "account.sum_order_update": u"Ordem %(order)s atualizada",
    "account.sum_pool_create": u"Pool %(a)s / %(b)s criada",
    "account.sum_pool_delete": u"Pool %(pool)s excluída",
    "account.sum_pool_deposit": (
        u"%(a)s + %(b)s depositedos em stake na pool %(pool)s"
    ),
    "account.sum_pool_swap": (
        u"%(sell)s → pelo menos %(buy)s trocados na pool %(pool)s"
    ),
    "account.sum_pool_update": u"Pool %(pool)s atualizada",
    "account.sum_pool_withdraw": (
        u"%(shares)s retirados de stake na pool %(pool)s"
    ),
    "account.sum_proposal_create": u"%(n)s operações propostas",
    "account.sum_proposal_delete": u"Proposta %(proposal)s excluída",
    "account.sum_proposal_update": u"Proposta %(proposal)s aprovada",
    "account.sum_samet_borrow": u"%(amount)s emprestados do fundo %(fund)s",
    "account.sum_samet_create": u"Fundo SameT criado com %(amount)s",
    "account.sum_samet_delete": u"Fundo SameT %(fund)s excluído",
    "account.sum_samet_repay": u"%(amount)s pagos ao fundo %(fund)s",
    "account.sum_samet_update": u"Fundo SameT %(fund)s atualizado",
    "account.sum_settle_cancel": u"Liquidação de %(amount)s cancelada",
    "account.sum_smartcoin_update": u"Smartcoin %(asset)s atualizada",
    "account.sum_ticket_create": u"Ticket %(amount)s criado",
    "account.sum_ticket_update": u"Ticket %(ticket)s atualizado",
    "account.sum_transfer": u"Transferência de %(amount)s de %(from)s para %(to)s",
    "account.sum_transfer_recv": u"%(amount)s recebidos de %(from)s",
    "account.sum_transfer_send": u"%(amount)s enviados para %(to)s",
    "account.sum_upgrade": u"%(account)s sofreu upgrade",
    "account.sum_vesting_create": u"%(amount)s entraram em vesting para %(owner)s",
    "account.sum_vesting_withdraw": u"%(amount)s em vesting retirados",
    "account.sum_whitelist": u"%(account)s adicionado à lista",
    "account.sum_witness_create": u"Tornou-se testemunha: %(account)s",
    "account.sum_witness_update": u"Testemunha %(account)s atualizada",
    "account.sum_worker_create": u"Worker \"%(name)s\" criado",
    "account.total": u"Total ≈ ",
    "account.upgrade_row_upgrade": u"Upgrade",

    # ------------------------------------------------------------ account_net
    "account_net.canvas_missing": (
        u"O canvas da rede está indisponível nesta compilação; a tabela abaixo "
        u"continua listando todas as linhas."
    ),
    "account_net.class_credit": u"Crédito",
    "account_net.class_credit_help": u"Ofertas de crédito aceitas e pagas.",
    "account_net.class_debit": u"Débito direto",
    "account_net.class_debit_help": (
        u"Permissões de débito direto e retiradas."
    ),
    "account_net.class_htlc_help": (
        u"Contratos com hash e timelock e suas atualizações."
    ),
    "account_net.class_override": u"Transferência com override",
    "account_net.class_override_help": (
        u"Transferências cuja taxa é paga pelo emissor do ativo."
    ),
    "account_net.class_transfer": u"Transferência",
    "account_net.class_transfer_help": u"Transferências diretas entre contas.",
    "account_net.class_vesting_help": (
        u"Saldos em vesting administrados por terceiros."
    ),
    "account_net.depth_1": u"1 salto",
    "account_net.depth_2": u"2 saltos",
    "account_net.depth_label": u"Profundidade",
    "account_net.detail_hint": (
        u"Toque em uma linha para ver o detalhe; toque em uma conta para abri-la."
    ),
    "account_net.detail_line": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ops · %(kind)s"
    ),
    "account_net.detail_line_one": (
        u"%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s op · %(kind)s"
    ),
    "account_net.detail_span": u"%(first)s → %(last)s",
    "account_net.es_bad_account": (
        u"Esse nome não é uma conta nesta chain."
    ),
    "account_net.es_disabled": (
        u"O índice comunitário está desligado. Ligue-o em Configurações para "
        u"desenhar este mapa."
    ),
    "account_net.es_unavailable": (
        u"O índice comunitário está inacessível agora. Tente de novo em instantes."
    ),
    "account_net.go": u"Desenhar rede",
    "account_net.idle": u"Nada desenhado ainda.",
    "account_net.intro": (
        u"Digite uma ou mais contas para ver com quem elas transferem, para quem "
        u"emprestam e de quem tomam emprestado. Lido do índice comunitário de "
        u"histórico; nada é assinado e nada é armazenado."
    ),
    "account_net.kind_flow": u"fluxo",
    "account_net.kind_relation": u"relação",
    "account_net.more_assets": u" + mais %(n)s",
    "account_net.need_class": (
        u"Ligue pelo menos um tipo de linha para desenhar."
    ),
    "account_net.need_seeds": u"Digite pelo menos uma conta para mapear.",
    "account_net.no_amount": u"sem valor",
    "account_net.ring1_label": u"Anel 1",
    "account_net.ring2_label": u"Anel 2",
    "account_net.scanning": u"Lendo o índice comunitário…",
    "account_net.seeds_label": u"Contas para mapear",
    "account_net.stale_settings": (
        u"As configurações de profundidade ou de vizinhos mudaram — pressione "
        u"Desenhar rede."
    ),
    "account_net.status_credit_index": (
        u"%(n)s linhas de crédito resolvidas do índice (o objeto de oferta ou "
        u"acordo sumiu da chain)"
    ),
    "account_net.status_credit_missing": (
        u"%(n)s linhas de crédito ignoradas (oferta ou acordo não encontrado "
        u"na chain)"
    ),
    "account_net.status_depth": u"mapa %(depth)s",
    "account_net.status_edge_cap": u"primeiras %(n)s linhas exibidas",
    "account_net.status_expanded": u"expandido: %(names)s",
    "account_net.status_expansion_scanned": (
        u"%(n)s operações indexadas de expansões"
    ),
    "account_net.status_expansion_truncated": (
        u"varreduras de expansão truncadas nas operações mais recentes"
    ),
    "account_net.status_graph": u"%(nodes)s contas · %(edges)s linhas",
    "account_net.status_node_cap": u"primeiras %(n)s contrapartes exibidas",
    "account_net.status_scanned": (
        u"%(scanned)s operações indexadas de %(n)s conta(s)"
    ),
    "account_net.status_self": u"%(n)s autotransferências ignoradas",
    "account_net.status_shape": u"%(n)s entradas ilegíveis ignoradas",
    "account_net.status_truncated": (
        u"%(n)s operações mais recentes por conta"
    ),
    "account_net.status_unexpanded": (
        u"%(n)s contrapartes diretas não expandidas"
    ),
    "account_net.status_unknown": u"não encontradas: %(names)s",
    "account_net.title": u"Rede de contas",
    "account_net.twin_amount": u"Quantidade",
    "account_net.twin_class": u"Tipo",
    "account_net.twin_depth": u"Salto",
    "account_net.twin_empty": (
        u"Nenhuma linha entre estas contas nas operações indexadas analisadas."
    ),
    "account_net.twin_from": u"De",
    "account_net.twin_relation": u"Fluxo/relação",
    "account_net.twin_span": u"Primeiro → último",
    "account_net.twin_summary": u"Visualização em tabela (acessível)",
    "account_net.twin_to": u"Para",

    # --------------------------------------------------------------- settings
    "settings.age_s": u"%(n)s s",
    "settings.confirm_back": u"Voltar",
    "settings.confirm_remove_action": u"Ação",
    "settings.confirm_remove_hide": (
        u"Ocultar este nó (continua oculto até ser adicionado de novo)"
    ),
    "settings.confirm_remove_result": u"Resultado",
    "settings.confirm_remove_switch": u"O nó ativo muda para %(node)s",
    "settings.confirm_remove_title": u"Remover nó?",
    "settings.confirm_remove_unlist": u"Remover da minha lista",
    "settings.discover_note": (
        u"**Buscar nós pesquisa no GitHub listas de nós e depois testa o que "
        u"encontra. O GitHub e os nós testados veem seu endereço de rede. Os "
        u"resultados são candidatos para sua revisão — nada é adicionado "
        u"automaticamente."
    ),
    "settings.geo_note": (
        u"*Os locais e provedores vêm de ipaddress.to (https, sem chave) — ele vê "
        u"seu endereço quando consultado; as respostas ficam em cache neste "
        u"dispositivo por 24 horas."
    ),
    "settings.hist_no": u"NÃO",
    "settings.hist_yes": u"SIM",
    "settings.language_title": u"Idioma",
    "settings.node_timeout": u"Tempo limite",
    "settings.sign_auto": u"Automático (extensão quando disponível)",
    "settings.sign_badge": (
        u"Assinatura pela extensão ativa — detalhes em Entrar"
    ),
    "settings.sign_badge_local": (
        u"Assinatura nesta página — detalhes em Entrar"
    ),
    "settings.sign_browser": u"Assinar sempre nesta página",
    "settings.sign_ext": u"Usar sempre a extensão",
    "settings.sign_ext_absent": (
        u"Nenhuma extensão detectada neste dispositivo — as assinaturas "
        u"acontecem nesta página."
    ),
    "settings.sign_ext_present": u"Extensão detectada neste dispositivo.",
    "settings.sign_guide": u"Como instalar a extensão",
    "settings.sign_mode_browser": (
        u"As assinaturas acontecem na memória desta página."
    ),
    "settings.sign_mode_ext": (
        u"As assinaturas são aprovadas na janela da extensão."
    ),
    "settings.sign_mode_ext_page": (
        u"As assinaturas ficam na extensão — isoladas dos sites."
    ),
    "settings.sign_revoke": u"Revogar",
    "settings.sign_sites": u"Sites conectados",
    "settings.sign_sites_empty": (
        u"Nenhum site aprovado ainda — as aprovações aparecem aqui, com revogação "
        u"por site."
    ),
    "settings.sign_sites_story_a": u"Exemplo: um jogo de dados em ",
    "settings.sign_sites_story_b": (
        u" quer jogar como sua conta — aprovar lista o site aqui, vinculado "
        u"somente a essa conta. As assinaturas ainda perguntam toda vez. (Este "
        u"link não leva a lugar algum — é um exemplo fictício.)"
    ),
    "settings.sign_title": u"Assinatura",
    "settings.sign_warn": (
        u"Qualquer script rodando nesta página — inclusive uma cópia hospedada "
        u"comprometida — pode ler suas chaves enquanto a carteira está "
        u"desbloqueada. Roteie a assinatura pela extensão, ou use uma cópia que "
        u"você controla."
    ),
    "settings.th_handshake": u"Handshake",
    "settings.th_history": u"Histórico",
    "settings.th_location": u"Local *",
    "settings.th_participation": u"Participação",
    "settings.th_provider": u"Provedor *",
    "settings.theme_title": u"Tema",

    # ----------------------------------------------------------------- market
    "market.adjust_button": u"Ajustar",
    "market.confirm_adjust": u"Confirmar ajuste",
    "market.discrete_fills": u"execuções",
    "market.discrete_no_fills": (
        u"Sem execuções ainda — faça uma ordem ou tente outro par."
    ),
    "market.discrete_tip_account": u"Conta",
    "market.discrete_tip_block": u"Bloco",
    "market.discrete_tip_order": u"Ordem",
    "market.discrete_tip_price": u"Preço",
    "market.discrete_tip_time": u"Hora",
    "market.discrete_tip_volume_quote": u"Volume (cotação)",
    "market.discrete_unavailable": u"Indicadores indisponíveis em Discrete.",
    "market.discrete_volume": u"Volume discreto",
    "market.exchange_desk": u"Mesa de negociação",
    "market.fail_update": u"Falha na atualização.",
    "market.flt_max_price": u"Preço máximo",
    "market.flt_min_price": u"Preço mínimo",
    "market.loading_pool_map": u"Carregando mapa…",
    "market.map_aria": (
        u"Rede de mercados. As linhas são mercados que tiveram execução nas "
        u"últimas 24 horas."
    ),
    "market.map_connects": (
        u"Uma linha conecta dois ativos quando houve negociação no mercado nas "
        u"últimas 24 horas."
    ),
    "market.map_connects_fallback": (
        u"Uma linha conecta dois ativos quando existe uma pool financiada. A "
        u"atividade de negociação em 24h não é confirmada (histórico "
        u"indisponível) — mostrando as pools financiadas."
    ),
    "market.map_edge_fills": u"%(desk)s · %(a)s–%(b)s · %(fills)s execuções/24h",
    "market.map_hops_empty": (
        u"Nenhum mercado teve execução nas últimas 24 horas ao redor destas "
        u"pernas."
    ),
    "market.map_hops_filtered": (
        u"Uma linha é um mercado que teve execução nas últimas 24 horas. "
        u"Mostrando %(shown)s de %(total)s pares (mín. %(min)s execuções/24h)."
    ),
    "market.map_hops_no_route": (
        u"Sem rota para BTS por mercados com execução."
    ),
    "market.map_hops_note": (
        u"Uma linha é um mercado que teve execução nas últimas 24 horas. "
        u"%(pairs)s pares exibidos."
    ),
    "market.map_leg_ok": u"{s} conecta a BTS",
    "market.map_leg_orphan": (
        u"ATENÇÃO: {s} não tem rota por mercados com execução!"
    ),
    "market.min_fills": u"Mín. execuções",
    "market.no_filter_match": (
        u"Nenhuma execução corresponde a estes filtros."
    ),
    "market.plots_group": u"Gráficos",
    "market.settle_first100": (
        u"Mostrando os primeiros 100 (limite de 100 em get_settle_orders)"
    ),
    "market.settle_no_cancel": (
        u"Ordens de liquidação não podem ser canceladas — elas executam na "
        u"liquidação (após o atraso de liquidação forçada do ativo)."
    ),
    "market.tf_discrete": u"Discreto",
    "market.update_amount": u"Quantidade para venda (novo total) ",
    "market.update_amount_change": u"Variação da quantidade",
    "market.update_bad_amount": u"Digite uma quantidade maior que zero.",
    "market.update_bad_expiry": u"Digite um vencimento no futuro.",
    "market.update_bad_price": u"Digite um preço maior que zero.",
    "market.update_broadcasting": u"Transmitindo atualização…",
    "market.update_done": u"Ordem atualizada",
    "market.update_expiry": u"Novo vencimento ",
    "market.update_expiry_change": u"Vencimento (antigo → novo)",
    "market.update_no_change": (
        u"Nenhuma alteração — edite preço, quantidade ou vencimento."
    ),
    "market.update_price": u"Novo preço ",
    "market.update_price_change": u"Preço (antigo → novo)",
    "market.update_review": u"Revisar atualização",
    "market.update_title": u"Ajustar ordem",

    # ------------------------------------------------------------- market_net
    "market_net.asset_1_field": u"Ativo 1 (qualquer perna)",
    "market_net.asset_2_field": u"Ativo 2 (qualquer perna)",
    "market_net.band_title": u"Rede de mercados",
    "market_net.canvas_label": (
        u"Mapa da rede de mercados. Pressione Enter para abrir o mercado."
    ),
    "market_net.clear_btn": u"Limpar",
    "market_net.col_last": u"Último",
    "market_net.col_market": u"Mercado",
    "market_net.col_vol": u"Vol 24h",
    "market_net.collapse": u"Recolher",
    "market_net.edge_card_fills": (
        u"%(desk)s · %(a)s–%(b)s · %(fills)s execuções/24h"
    ),
    "market_net.empty": u"Nenhum mercado encontrado para este filtro.",
    "market_net.expand": u"Expandir",
    "market_net.list_btn": u"Listar mercados",
    "market_net.loading": u"Carregando mercados…",
    "market_net.map_empty": u"Nenhum mercado com volume recente.",
    "market_net.map_fallback": (
        u"%(pairs)s pares · %(assets)s ativos · execuções 24h não confirmadas"
    ),
    "market_net.map_hops_ready": (
        u"%(pairs)s pares · %(assets)s ativos · execuções 24h"
    ),
    "market_net.map_ready": u"%(markets)s mercados · %(assets)s ativos",
    "market_net.node_card": u"%(sym)s (%(id)s) · %(n)s mercados",
    "market_net.offline": (
        u"Rede indisponível — mostrando mercados em cache. Tente de novo quando "
        u"conectado."
    ),
    "market_net.open_desk": u"Abrir %(id)s",
    "market_net.prompt": (
        u"Toque em um nó para o ativo, em uma linha para o mercado."
    ),
    "market_net.ramp": u"Volume 24h: baixo → alto",
    "market_net.ramp_fills": u"Execuções 24h: baixo → alto",
    "market_net.selector_title": u"Seletor de mercados",
    "market_net.spark_label": u"Tendência de 7 dias de %(id)s",
    "market_net.subtitle": (
        u"Principais mercados do livro de ofertas por volume 24h. Escolha uma "
        u"linha para abrir a mesa."
    ),
    "market_net.title": u"Mercados",
    "market_net.top_note": (
        u"Primeiros %(shown)s de %(probed)s testados — por volume 24h."
    ),
    "market_net.twin": u"Linhas de mercado (%(n)s)",
    "market_net.twin_more": (
        u"Mostrando %(shown)s de %(n)s mercados — restrinja o filtro para ver "
        u"menos."
    ),
    "market_net.verdict_full": u"%(markets)s mercados · %(assets)s ativos",
    "market_net.verdict_no_path": (
        u"Sem rota por mercados com execução entre %(a)s e %(b)s"
    ),
    "market_net.verdict_path": (
        u"%(a)s alcança %(b)s em %(n)s mercados com execução"
    ),
    "market_net.verdict_star": u"Mercados que tocam %(s)s: %(n)s",
    "market_net.verdict_web": u"Mercados alcançáveis a partir de %(s)s: %(n)s",

    # ------------------------------------------------------------------ asset
    "asset.cer_row": u"Taxa de câmbio central (CER)",
    "asset.committee_fed_note": (
        u"Alimentado pelo comitê: todos os membros ativos do comitê podem "
        u"publicar."
    ),
    "asset.feed_history_title": u"Histórico de feeds",
    "asset.flags_title": u"Sinalizadores",
    "asset.history_capped": (
        u"Mostrando os primeiros 8 publicadores (limitado por velocidade)…"
    ),
    "asset.history_days": u"Período",
    "asset.history_exchange": u"Carregando exchange + pools…",
    "asset.history_failed": (
        u"Não foi possível carregar o histórico de feeds."
    ),
    "asset.history_loading": u"Carregando histórico de feeds…",
    "asset.history_pub": u"Publicador %(i)s/%(n)s…",
    "asset.invert_btn": u"Inverter",
    "asset.issue_memo_no_key": (
        u"Nenhuma chave de memo registrada para esta conta."
    ),
    "asset.issue_memo_warning": (
        u"Anexe um memo — ele é gravado na chain em texto puro."
    ),
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        u"O emissor assume a conta que está sendo visualizada (%(id)s "
        u"bloqueada, sua conta desbloqueada) — digite qualquer emissor que você "
        u"controle. Aberto de uma página de conta, cole aqui o nome dessa conta."
    ),
    "asset.loading_producers": u"Carregando produtores…",
    "asset.multisig_body": (
        u"Se este ativo exigir mais de uma aprovação, a Assinatura direta "
        u"falha — proponha a mudança e peça a aprovação dos co-proprietários "
        u"(op 23)."
    ),
    "asset.multisig_coowner_hint": (
        u"Co-proprietário? Proponha a mudança na página de propostas e peça a "
        u"aprovação dos co-proprietários (op 23)."
    ),
    "asset.multisig_open_proposals": u"Ver propostas",
    "asset.multisig_open_txbuilder": u"Abrir construtor de transações",
    "asset.multisig_title": u"Emissor compartilhado? Proponha",
    "asset.new_issuer_field": u"Novo emissor",
    "asset.no_history": (
        u"Sem histórico neste período — os publicadores publicam com pouca "
        u"frequência; tente 90d."
    ),
    "asset.no_producers": (
        u"Nenhum feed publicado ainda — os produtores aparecem aqui depois que "
        u"publicam."
    ),
    "asset.orientation_note": u"%(m)s por %(b)s",
    "asset.owner_key_note": u"Requer a chave active do proprietário do ativo.",
    "asset.plot_feeds": u"Plotar feeds",
    "asset.producer_col": u"Produtor",
    "asset.producers_failed": u"Não foi possível carregar os produtores.",
    "asset.producers_live_title": u"Produtores de feed",
    "asset.producers_title": u"Produtores de feed (op %(op)s)",
    "asset.publish_op19_title": u"Publicar feed (op %(op)s)",
    "asset.published_col": u"Publicado",
    "asset.viewing_notice": (
        u"Visualizando como %(name)s (%(id)s) — desbloqueie para assinar."
    ),
    "asset.witness_fed_note": (
        u"Alimentado por testemunhas: todas as testemunhas ativas podem "
        u"publicar."
    ),
}

# Keys whose Portuguese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from PT. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * brands (shell.brand, the two footer brands — PINNED),
#   * the settings network ids, theme ids, placeholder, pending and dash
#     sentinels (PINNED),
#   * loanwords a Brazilian crypto UI keeps in English ("Exchange", "Head",
#     "Handshake", "Ping", "Chain", "Log", "Vol", "Total", "MCR", "NFT", "PMA",
#     "UIA", "Op", "BB", "EMA", "PSAR", "SMA", "24h Δ", "7d", "—", "swaps",
#     "Bitasset", "Smartcoin", "HTLC", "Vesting", "Delta", "ID", "Upgrade"),
#   * indicator acronyms (BB, EMA, PSAR, SMA) and numeric sentinels (—),
#   * pure glue: unit/suffix rows, " · " separator rows, "@ price" rows and the
#     bare example payload seeds.
KEPT_ENGLISH = {
    "account_net.class_htlc": u"HTLC",
    "account_net.class_vesting": u"Vesting",
    "account_net.no_amount_twin": u"",  # placeholder, never shipped - see below
    "account_net.seeds_placeholder": u"committee-account, alice, 1.2.42",
    "account_net.twin_count": u"Ops",
    "asset.bitasset_row": u"Bitasset",
    "asset.mcr_row": u"MCR",
    "asset.nft_row": u"NFT",
    "asset.op_col": u"Op",
    "asset.smartcoin_row": u"Smartcoin",
    "asset.tab_pma": u"PMA",
    "asset.tab_uia": u"UIA",
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
    "market.stat_empty": u"—",
    "market.th_total": u"Total",
    "market.title": u"Exchange",
    "market.vol_label": u"Vol",
    "market.vol_lin": u"Vol: Linear",
    "market.vol_log": u"Vol: Log",
    "market_net.col_change": u"24h Δ",
    "market_net.col_spark": u"7d",
    "market_net.edge_card": u"%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_price": u"@ %(price)s",
    "settings.dash": u"—",
    "settings.custom_placeholder": u"wss://…",
    "settings.network_devnet": u"devnet",
    "settings.network_mainnet": u"mainnet",
    "settings.network_testnet": u"testnet",
    "settings.pending": u"…",
    "settings.theme_dark": u"dark",
    "settings.theme_light": u"light",
    "settings.theme_original_blue": u"original-blue",
    "settings.th_chain": u"Chain",
    "settings.th_head": u"Head",
    "settings.th_ping": u"Ping",
}
# `account_net.no_amount_twin` never existed in en.json; drop it here so the
# KEPT_ENGLISH coverage check only ever sees real keys.
del KEPT_ENGLISH["account_net.no_amount_twin"]


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
    hit = suspicious(value)
    if hit:
        problems.append(
            "suspicious code point U+%04X in %s" % (ord(hit), key)
        )


def check_apostrophe(batch, problems):
    """G7: pt.json ships zero apostrophes, so this batch must add none.

    Portuguese does not need them for possession ("sua conta"), and none of the
    3076 strings already translated in pt.json carries one - so a stray ' or ’
    here would be the only such spelling in the whole dictionary.
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
    # tooling/check_i18n.py reads it in both directions — a claimed key that
    # still reads English is a false claim, and an unclaimed key that is no
    # longer English is an undeclared translation. So the claim moves in
    # lockstep with the bytes, for exactly the keys this batch translated. The
    # values kept byte-identical on purpose (loanwords, brands, ids, glue) stay
    # UNCLAIMED, which is the honest state for them. Nothing else in _meta
    # moves — filling strings is not verification, so the controller's v2
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

    print("pt chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
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

    with open(PT_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(pt, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/pt.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())