#!/usr/bin/env python3
"""i18n pt chunk-B2: the shell, menu and marketing surfaces plus the three
signing desks that pt.json still leaves in English.

Scope: ONLY the eleven sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from pt.json, or one whose English master moved, is REFUSED;
  * PT + KEPT_ENGLISH together must account for EVERY untranslated key of the
    eleven sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset; B1
owns help, pool, pool_net and explorer. Each of those batches REFUSES anything
outside its own sections, and so does this one. A key that crosses the line is
a reviewer's problem, never a script's silent edit.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key, and
                      single-brace {s} interpolations kept verbatim;
  G2  identifiers    values that are an object id / URL / route as a WHOLE stay
                      byte-verbatim;
  G3  pinned keys    shell.brand, the two footer brands, and the settings
                      network/theme/dash/placeholder tokens stay byte-verbatim
                      (the same list tooling/validate_translations.py checks);
  G4  structure      same line count and same markdown link hashes (#/...) for
                      every filled key, measured against the ENGLISH master -
                      this is the gate that keeps the about/splash bodies and
                      the 1.10.N proposal id honest;
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
                      introduce an ASCII or typographic one either.

Variant: the part of pt.json that is already translated is BRAZILIAN
Portuguese, so this batch is pt-BR too - the informal register, the imperative
"Negocie ..." and "você" match the shipped dictionary rather than a
European-Portuguese or formal-register rewrite.

Vocabulary is reused verbatim from pt.json wherever that dictionary has already
settled a word, and from chunks A and B1 where they settled one for the same
word: Painel (dashboard), Carteira, Exchange, Testemunha (witness), Comitê,
Emissor, Publicador, Produtor, Colateral, chain (loanword, f.), nó (m.), pool
(f.), swap, cota (f.), perna (f.), smartcoin, HTLC, DEX, API, feed, memo,
brainkey (f.), vesting, ticket, worker, proxy, slate, taxa, preço, quantidade,
ordem, proposta, ativo (m.), saldo, limpar, tentar novamente. The already
translated sections fix several labels outright and this batch keeps them:
"Total" (market.th_total, credit.total), "ID" (explorer.id_row), "Memo"
(confirm.memo), "Ticket" (ticket.ticket), "Exchange" (market.title),
"Trollbox", "Cross Rates", "Airdrop", "Spotlight", "Tickets", "Vesting",
"HTLC", "Velas" (market_ind.candle_count), "Limpe"/"Limpar" for a cleared
search (about.dlg_no_match), "Mostrando" (explorer.markets_showing), "nada é
assinado e nada é armazenado" (account_net.intro), and the about.dlg_* family
calling a back-and-forth a "exchange" - the same spelling about.dlg_no_match
and about.dlg_bad_link already ship.

about.making_body repeats the build story that B1 already translated as
help.topic_about-making_body, so this batch reuses B1's paragraph word for word
(one sentence drift between two copies of one text is a bug a reader notices).
For the same reason about.dlg_heading keeps the English "Full build dialog":
B1's pt body quotes that section name in English inside its own prose, and a
heading in one language beside its quoted name in another is not a glossary.

The seo.* values are meta descriptions: short, factual, no marketing adjective
that the page does not earn. Nothing is claimed there that a page does not do
(no login, keys local, live reads) - the same claims about.s1/s5 and
splash.trust_* already make in Portuguese.

trade, barter and proposal render DUAL-LINE inside signing dialogs, beside an
English reference the user can toggle. So those strings take the plainer,
more literal route: an amount, a destination or an irreversible action is named
exactly as the English names it ("Excluir proposta", not a softened verb; "Total
a vender", not a summary word), because a reader comparing two lines must not
have to guess which one hides the number.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where a
translated string quotes a number the English quotes (360px, 4K, 24 hours, 3
hops, 6 pool hops, op 22, op 24, 1.10.N, issue #3583, 26 September 2026, 3
October) it keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_pt_chunkB2.py                 # dry run (asserts)
  python3 tooling/apply_i18n_pt_chunkB2.py --apply         # writes pt.json
  python3 tooling/apply_i18n_pt_chunkB2.py --verify        # structural re-proof
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

# The eleven sections this batch owns. Everything else belongs to chunk-A (six
# sections), to chunk-B1 (four sections), or to a later chunk, and is REFUSED
# here as out of scope.
SECTIONS = frozenset((
    "seo", "splash", "about", "shell", "menu", "trade", "barter", "proposal",
    "trollbox", "xrate", "pool_detail",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from PT below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# Only shell.* of the three pinned groups live in this batch's sections; the
# settings ones are listed whole so a drift anywhere in the file is caught.
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


# --------------------------------------------------------------------------
# about.making_body is the build story B1 already translated as
# help.topic_about-making_body; it is reproduced here word for word (without
# the heading) so the About page and the help article read as one text.
# --------------------------------------------------------------------------
MAKING_BODY = (
    u"O que vem a seguir é a história original da construção: cada prompt que "
    u"criou esta carteira, de \"acquire bitshares-ui\" em 26 de setembro de 2026 "
    u"até a correção da issue-1 em 3 de outubro, com as respostas dos "
    u"construtores — preservadas sem edição. "
    u"Ela registra as decisões que sustentam esta carteira: desistir de mais um "
    u"uplift de React depois da issue #3583 e sua armadilha de mil horas, para "
    u"que esta carteira não dependa de nada com ciclo de lançamento; assinar "
    u"cada transação localmente como a carteira antiga em vez de terceirizar; "
    u"três temas com o visual clássico como padrão; números em termos humanos, "
    u"nunca inteiros crus da chain; layouts pensados primeiro para celular desde "
    u"a fatia 1; e taxas lidas da chain ao vivo, nunca estimadas. Leia como "
    u"história: foi assim que a carteira foi construída."
)


PT = {
    # -------------------------------------------------------------------- seo
    # Titles keep the " — Carteira BitShares" tail the shell brand already
    # ships (menu.p_wallet = Carteira), and reuse the page's own translated
    # name wherever pt.json has one: Painel, Exchange, Mercados, Explorador,
    # Ajuda, Entrar, Votação.
    "seo.title_about": u"Sobre — Carteira BitShares",
    "seo.title_account": u"Conta %(name)s — Carteira BitShares",
    "seo.title_account_net": u"Rede de contas — Carteira BitShares",
    "seo.title_dashboard": u"Painel — Carteira BitShares",
    "seo.title_explorer": u"Explorador — Carteira BitShares",
    "seo.title_help": u"Ajuda — Carteira BitShares",
    "seo.title_login": u"Entrar — Carteira BitShares",
    "seo.title_market": u"Exchange BTS/USD — Carteira BitShares",
    "seo.title_markets": u"Mercados — Carteira BitShares",
    "seo.title_pools": u"Pools de liquidez — Carteira BitShares",
    "seo.title_transfer": u"Enviar fundos — Carteira BitShares",
    "seo.title_voting": u"Votar em testemunhas — Carteira BitShares",
    # The page keeps its name (xrate.title, menu.p_xrates, the sitemap label
    # B1 shipped), so only the wallet half of the title is translated.
    "seo.title_xrates": u"Cross Rates — Carteira BitShares",
    # Descriptions: what the page actually does, no adjective it has not earned.
    "seo.desc_about": (
        u"Sobre esta carteira BitShares — chaves locais, sem cadastro, sem "
        u"rastreamento. Navegue livremente e assine localmente."
    ),
    "seo.desc_account": (
        u"Veja esta conta BitShares — saldos, ordens e histórico lidos ao vivo "
        u"da chain. Sem login."
    ),
    "seo.desc_account_net": (
        u"Mapeie para quem uma conta envia, empresta e toma emprestado — lido do "
        u"índice comunitário. Sem login."
    ),
    "seo.desc_dashboard": (
        u"Painel BitShares — saldos, mercados e atividade da chain em um "
        u"golpe de vista. Navegue livremente; as chaves ficam no seu dispositivo."
    ),
    "seo.desc_explorer": (
        u"Explore blocos, transações e ativos da BitShares — dados ao vivo da "
        u"chain, navegáveis sem login."
    ),
    "seo.desc_help": (
        u"Ajuda da carteira BitShares — guias de contas, negociação, votação e "
        u"recuperação. Comece aqui quando travar."
    ),
    "seo.desc_login": (
        u"Desbloqueie sua carteira local BitShares — senha, brainkey ou chaves "
        u"importadas. As chaves nunca saem deste dispositivo."
    ),
    "seo.desc_market": (
        u"Negocie BTS por USD no livro de ofertas BitShares — compras, vendas e "
        u"histórico ao vivo, assinados localmente no seu dispositivo."
    ),
    "seo.desc_markets": (
        u"Navegue pelos mercados do livro de ofertas BitShares por volume de 24h "
        u"e abra a mesa de qualquer par. Sem login."
    ),
    "seo.desc_pools": (
        u"Navegue pelas pools de liquidez BitShares — pares, saldos e atividade "
        u"lidos ao vivo da chain. Sem login."
    ),
    "seo.desc_transfer": (
        u"Envie ativos BitShares para qualquer conta. Confira cada campo e "
        u"assine localmente — as chaves nunca saem do seu dispositivo."
    ),
    "seo.desc_voting": (
        u"Vote em testemunhas, membros do comitê e workers da BitShares. Cada "
        u"voto é assinado localmente no seu dispositivo."
    ),
    "seo.desc_xrates": (
        u"Cada ativo de pool precificado em BTS e mais, pelo preço do último "
        u"swap. Sem login."
    ),

    # ----------------------------------------------------------------- splash
    # hero_title reuses about.hero_title's shipped wording; the step titles
    # are imperatives, like every other on-ramp line in the dictionary.
    "splash.card_dex_d": u"Compre e venda no mercado aberto.",
    "splash.card_explore_d": u"Leia blocos e histórico de contas.",
    "splash.card_pool_d": u"Ganhe uma parte fornecendo dois ativos em pool.",
    "splash.card_wallet_d": u"Guarde as chaves só neste dispositivo.",
    "splash.cards_title": u"Negocie, use pools, explore — comece aqui",
    "splash.cta_exchange": u"Negocie no exchange",
    "splash.hero_sub": u"Suas chaves. Seus fundos, on-chain.",
    "splash.hero_sub2": (
        u"Navegue nos mercados de graça. Desbloqueie só para assinar."
    ),
    "splash.hero_title": u"BitShares no seu navegador. Nada a instalar.",
    # "Head time" is the node's head block timestamp; the pulse row next to it
    # is already "Bloco principal", so the label names the same thing.
    "splash.pulse_stale": u"— desatualizado",
    "splash.pulse_time": u"Horário do bloco principal",
    "splash.pulse_title": u"Números da chain ao vivo",
    "splash.step1_d": u"Sem login — navegue primeiro na chain.",
    "splash.step1_t": u"Explore um pouco",
    "splash.step2_d": (
        u"A brainkey é gerada neste dispositivo. Anote no papel."
    ),
    "splash.step2_t": u"Crie uma carteira",
    "splash.step3_d": (
        u"Ordens limitadas, pools de liquidez e votos — tudo on-chain."
    ),
    "splash.step3_t": u"Negocie / pool / vote",
    "splash.topvol_unavailable": (
        u"O volume do maior mercado está offline — confira Configurações → Nós."
    ),
    "splash.trust_keys_d": (
        u"A assinatura acontece localmente no seu dispositivo. Nenhum servidor "
        u"vê uma senha ou uma chave."
    ),

    # ------------------------------------------------------------------ about
    # "exchange" stays the English loanword here: about.dlg_no_match and
    # about.dlg_bad_link (chunk-A) already call a back-and-forth an exchange.
    "about.dlg_no_reply": (
        u"Nenhuma resposta registrada — o prompt seguinte veio logo depois."
    ),
    "about.dlg_noscript": (
        u"Este arquivo precisa de JavaScript; o mesmo texto está em "
        u"docs/vanilla-ui-dialog.md no repositório de código."
    ),
    "about.dlg_search_clear": u"Limpar",
    "about.dlg_search_ph": u"Filtrar exchanges…",
    "about.dlg_showing": u"Mostrando",
    "about.dlg_showing_c": u"Mostrando %(shown)s / %(total)s",
    "about.dlg_unavailable": u"Arquivo de diálogos da construção indisponível.",
    "about.hero_lede": (
        u"Uma carteira para a blockchain BitShares — mercados, contas, "
        u"governança e exploração — rodando como arquivos web simples. Sem "
        u"framework, sem instalador, sem conta com a gente. Suas chaves nunca "
        u"saim deste navegador."
    ),
    "about.making_body": MAKING_BODY,
    "about.making_title": u"A construção desta carteira",
    "about.s2_title": u"Negocie no livro de ofertas real",
    "about.s3_body": (
        u"A carteira que ela substitui morreu sob cem pacotes parados e um "
        u"toolchain que ninguém consegue reproduzir. Feita para evitar "
        u"dependências de ciclo de lançamento: sem framework, sem gerenciador "
        u"de pacotes, sem etapa de build — a menor coisa que ainda roda em um "
        u"navegador daqui a dez anos."
    ),
    "about.s3_title": u"Roda por anos sem atualizações",
    "about.s4_body": (
        u"Quem volta se sente em casa na hora — as mesmas páginas, painéis e "
        u"palavras da carteira clássica — enquanto saldos, livros e status de "
        u"conexão se atualizam no lugar. Busca tolerante em mercados, contas e "
        u"ativos, três temas e layouts que funcionam de um celular de 360px a "
        u"uma mesa de negociação 4K."
    ),
    "about.s4_title": u"As mesmas páginas, atualizações ao vivo",
    "about.s5_body": (
        u"A chain fala em inteiros; você nunca os vê. Cada valor fica nas casas "
        u"decimais do seu ativo, cada porcentagem no seu valor real, e cada taxa "
        u"é lida da chain ao vivo antes de você assinar."
    ),

    # ------------------------------------------------------------------ shell
    # The footer relation fragments are prefixes: the branch name is appended
    # by the caller, so "à frente de" must read as "ahead of <branch>".
    "shell.footer_ahead": u"%(n)s commits à frente de",
    "shell.footer_ahead_one": u"1 commit à frente de",
    "shell.footer_at_build": u"no build de %(date)s",
    "shell.footer_behind": u"%(n)s commits atrás de",
    "shell.footer_behind_one": u"1 commit atrás de",
    "shell.footer_dahead": u"%(n)s à frente",
    "shell.footer_dbehind": u"%(n)s atrás de",
    "shell.footer_diverged": u"divergido de",
    "shell.footer_offbranch": u"não está no Master",
    "shell.footer_sync": u"em sincronia com",

    # ------------------------------------------------------------------- menu
    "menu.blurb_labs": (
        u"Ferramentas poderosas para trabalhar com a chain e os nós."
    ),
    "menu.blurb_personal": u"Chat, alertas e sua configuração.",
    "menu.d_account_net": u"Rastreie para quem uma conta transfere.",
    "menu.d_xrates": u"Preços de pool para cada ativo em BTS e mais.",
    # The page this label opens calls itself "Rede de contas"
    # (account_net.title), so the label says the same thing. NOTE: the sitemap
    # label B1 shipped for #/account-network reads "Account Network" in
    # English; the two labels now differ, which is a reviewer call, not a
    # blocker (help-test.js only ties labels to hrefs, and it is green).
    "menu.p_account_net": u"Rede de contas",
    "menu.section_explore": u"Descobrir",
    "menu.section_personal": u"Pessoal",

    # ------------------------------------------------------------------ trade
    # Unlock-gate labels reuse the shipped row labels where the dictionary has
    # them: Valor (trade.row_amount), Preço (trade.row_price), Total
    # (market.th_total). Dual-line readers get a literal "Total a vender".
    "trade.fok_label": u"Preencher ou matar ",
    "trade.row_fok": u"Preencher ou matar",
    "trade.tab_single": u"Única",
    "trade.uc_amount": u"Valor",
    "trade.uc_orders": u"Ordens",
    "trade.uc_price": u"Preço",
    "trade.uc_range": u"Faixa de preço",
    "trade.uc_title": u"Desbloqueie para continuar",
    "trade.uc_total": u"Total a vender",

    # ----------------------------------------------------------------- barter
    # Step chips follow the verbs the section already uses in prose
    # ("Pré-visualize a troca primeiro", "montando a proposta").
    "barter.confirm_barter_proposal_op_22": (
        u"Confirmar proposta de troca (op %(op)s)"
    ),
    "barter.propose_barter_op_22": u"Propor troca (op %(op)s)",
    "barter.step_build": u"Montar",
    "barter.step_preview": u"Pré-visualizar",
    "barter.step_propose": u"Propor",
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        u"Prévia de swap atômico de dois lados. Pré-visualize primeiro; depois, "
        u"PROPOR inclui as transferências dos dois lados em uma proposta "
        u"(op %(op)s, pagador da taxa = Par A)."
    ),
    "barter.uc_title": u"Desbloqueie para assinar",

    # --------------------------------------------------------------- proposal
    # Irreversible action keeps the plain verb, and the multisig story keeps
    # the 1.10.N id byte-verbatim.
    "proposal.confirm_proposal_create_op_22": (
        u"Confirmar criação de proposta (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        u"Confirmar exclusão de proposta (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": u"Excluir proposta (op %(op)s)",
    "proposal.multisig_story": (
        u"Conta compartilhada? Um co-owner propõe e compartilha o id 1.10.N; "
        u"os demais aprovam abaixo. Trabalho com várias operações ou em vários "
        u"dispositivos continua no construtor de transações."
    ),
    # The op-name list; "lista branca" is the spelling proposal.inner_whitelist_2
    # already ships ("Listagem (branca / preta)").
    "proposal.op_7": u"lista branca",
    "proposal.open_txbuilder": u"Abrir o construtor de transações",
    "proposal.viewing_as": (
        u"Vendo como %(name)s (%(id)s) — desbloqueie para agir como você mesmo."
    ),

    # --------------------------------------------------------------- trollbox
    "trollbox.channel_row": u"Canal",
    "trollbox.fee": u"Taxa",
    "trollbox.language_row": u"Idioma",
    "trollbox.message_row": u"Mensagem",
    "trollbox.post_review_title": u"Revisar mensagem",
    "trollbox.size_row": u"Tamanho",
    "trollbox.unlock_post": u"Desbloquear e publicar",

    # ------------------------------------------------------------------ xrate
    # "Nada é assinado e nada é armazenado" is account_net.intro's own closing
    # clause, reused so the two read-only graph pages say the same thing.
    "xrate.add_btn": u"Adicionar coluna",
    "xrate.asset_col": u"Ativo",
    "xrate.base_pinned": (
        u"BTS é a coluna base e não pode ser removida."
    ),
    "xrate.empty": u"Nenhum ativo de pool a até 3 saltos de BTS nesta chain.",
    "xrate.intro": (
        u"Cada ativo de pool precificado pelo seu último swap, cruzando o grafo "
        u"de pools. Nada é assinado e nada é armazenado."
    ),
    "xrate.load_failed": u"Não foi possível carregar as cross rates: ",
    "xrate.loading": u"Lendo pools…",
    "xrate.no_route_col": u"Sem rota para %(sym)s em até 6 saltos de pool.",
    "xrate.refresh_btn": u"Atualizar preços",
    "xrate.remove_btn": u"Remover ",
    "xrate.retry_btn": u"Tentar novamente",
    "xrate.show_all": u"Mostrar todos os ativos",
    "xrate.status": (
        u"%(pools)s pools · %(assets)s ativos a até 3 saltos · %(done)s de "
        u"%(total)s pools têm um último swap"
    ),
    "xrate.token_label": u"Adicionar token de cotação",
    "xrate.unknown_token": u"Nenhum ativo de pool chamado %(sym)s.",
    "xrate.unpriced": u"Uma perna desta rota ainda não tem swap registrado.",

    # ------------------------------------------------------------ pool_detail
    # "candles" is Velas here, the word market_ind.candle_count already ships.
    "pool_detail.candle_capped": u"janela truncada",
    "pool_detail.candle_count": (
        u"%(swaps)s swaps · %(count)s × %(bucket)s velas"
    ),
    "pool_detail.candle_count_partial": (
        u"%(swaps)s swaps · %(actual)s de %(requested)s × %(bucket)s velas"
    ),
    "pool_detail.invert": u"Inverter",
    "pool_detail.invert_label": (
        u"Inverter a orientação do gráfico (A por B / B por A)"
    ),
    "pool_detail.map_connects": (
        u"Uma linha conecta dois ativos quando existe uma pool financiada e "
        u"houve uma negociação nas últimas 24 horas."
    ),
    "pool_detail.map_connects_fallback": (
        u"Uma linha conecta dois ativos quando existe uma pool financiada. A "
        u"atividade de negociação em 24h não é confirmada (histórico "
        u"indisponível) — mostrando as pools financiadas."
    ),
    "pool_detail.map_min_swaps": u"(mín. %(min)s swaps)",
}

# Keys whose Portuguese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from PT. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift. Most were already sitting at
# these exact bytes when this batch started - earlier chunks settled them - and
# this batch re-asserts rather than rewrites them:
#
#   * brands and data: shell.brand, shell.footer_brand,
#     shell.footer_brand_vanilla (the PINNED list);
#   * product / page names a Brazilian crypto UI keeps in English: Exchange,
#     HTLC, Vesting, Tickets, Airdrop, Spotlight, Trollbox, Cross Rates, Labs;
#   * the section heading "Discover" is translated (Descobrir), but "Labs",
#     "Personal" is not: a lab section keeps its Latin name in pt;
#   * ordinary Portuguese words that happen to be spelled like English:
#     Menu, Total, ID, Memo, Ticket, bytes;
#   * pure glue: a punctuation-only suffix (barter.paid_by_suffix), a
#     network/host pair (shell.footer_net_host), a currency placeholder
#     (xrate.token_placeholder), and the two authority suffixes whose words
#     (active / owner) pt.json keeps as authority names everywhere
#     (proposal.required_active, proposal.owner_approvals);
#   * the build-dialog heading, whose English name B1's translated body
#     already quotes in prose.
KEPT_ENGLISH = {
    # ---- shell
    "shell.brand": u"BitShares",
    "shell.footer_brand": u"BITSHARES",
    "shell.footer_brand_vanilla": u"BITSHARES VANILLA UI",
    "shell.footer_net_host": u"%(net)s - %(host)s",
    "shell.menu": u"Menu",
    # ---- menu
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
    # ---- splash
    "splash.card_dex_t": u"Exchange",
    "splash.card_pool_t": u"Pools",
    # ---- about
    "about.dlg_heading": u"Full build dialog",
    "about.dlg_heading_c": u"Full build dialog (%(total)s)",
    # ---- trade
    "trade.row_total": u"Total",
    # ---- barter
    "barter.paid_by_suffix": u"): ",
    # ---- proposal
    "proposal.active_suffix": u" (active): ",
    "proposal.id": u"ID",
    "proposal.memo": u"Memo",
    "proposal.owner_suffix": u" (owner): ",
    "proposal.ticket": u"Ticket",
    # ---- trollbox
    "trollbox.bytes_prefix": u"Bytes: ",
    "trollbox.bytes_unit": u"bytes",
    "trollbox.title": u"Trollbox",
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

    print("pt chunk-B2: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
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

    with open(PT_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(pt, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/pt.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
