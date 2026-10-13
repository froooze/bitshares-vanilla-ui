#!/usr/bin/env python3
"""i18n pt chunk-B1: fill the "long tail" of help plus the pool and explorer
desks that pt.json still leaves in English.

Scope: ONLY the four sections listed below. The script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from pt.json, or one whose English master moved, is REFUSED;
  * PT + KEPT_ENGLISH together must account for EVERY untranslated key of the
    four sections, so a forgotten string is a refusal, never a silent English.

chunk-A owns account, account_net, settings, market, market_net and asset and
REFUSES anything outside them; this batch REFUSES anything outside help, pool,
pool_net and explorer. A key that crosses the line is a reviewer's problem,
never a script's silent edit.

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
                      this is the gate that keeps the long help bodies and the
                      sitemap's 83 lines honest;
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

Variant: the part of pt.json that is already translated is BRAZILIAN
Portuguese, so this batch is pt-BR too - the informal register, the imperative
"Digite ..." and "você" match the shipped dictionary rather than a
European-Portuguese or formal-register rewrite.

Vocabulary is reused verbatim from pt.json wherever that dictionary has already
settled a word, and from chunk-A where it settled one for the same word:
conta (m.), ativo (m.), saldo, ordem, execução, preço, quantidade, proposta,
taxa, comitê, testemunha, emissor, publicador, produtor, colateral, cadeia de
blocos, chain (loanword, f.), nó (m.), carteira (f.), pool (f.), swap, stake,
cota (f.), perna (f.), smartcoin, bitasset, HTLC, DEX, API, feed, memo,
brainkey (f.), vesting, ticket, worker, proxy, slate, ledger, bridge. Nothing is
invented where a Portuguese crypto UI keeps the English word - the run prints
every value that stays identical to en, so a reviewer checks the list instead
of guessing.

The help bodies are the honesty surface, so they stay plain: an amount, a
destination, an irreversible action or a permission is named the way the English
names it, and no marketing adjective is introduced. The site-map body keeps all
83 of its lines and every `#/route` hash byte-verbatim; only the visible link
labels move, and they move to the wording the menu already ships (menu.p_*),
so a label reads the same wherever the user meets it.

Numbers: no amount is retyped in a translated string - a bare value is
`Format`'s job (AGENTS.md 3.5) - and no prose number is invented. Where a
translated string quotes a number the English quotes (issue #3583, 26
September 2026, 3 October, first 100 assets, slice 1, 1.3.x, 1.19.x, 1.19.66,
BTS_USD, ?dialog=N) it keeps it byte-verbatim.

This script never runs git (other agents share this worktree).

Usage:
  python3 tooling/apply_i18n_pt_chunkB1.py                 # dry run (asserts)
  python3 tooling/apply_i18n_pt_chunkB1.py --apply         # writes pt.json
  python3 tooling/apply_i18n_pt_chunkB1.py --verify        # structural re-proof
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

# The four sections this batch owns. Everything else belongs to chunk-A (six
# sections) or to a later chunk-B slice, and is REFUSED here as out of scope.
SECTIONS = frozenset((
    "help", "pool", "pool_net", "explorer",
))

# Brands, network ids, theme ids and sentinels are DATA, not prose (rule 1 of
# the brief). They are deliberately ABSENT from PT below so they keep the
# English bytes, and the verify pass re-asserts every one after the write.
# None of them lives in this batch's four sections; the list is kept whole so a
# drift anywhere in the file is caught.
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
# The site map: one entry per English line, so the 83-line shape of the
# English master is visible in the source and cannot drift. Every link keeps
# its `#/route` byte-verbatim; the label follows menu.p_*, the wording the
# menu already ships for that very link.
# --------------------------------------------------------------------------
SITEMAP = [
    u"Todas as páginas desta carteira, agrupadas do jeito que o menu agrupa. "
    u"Tudo que tem um link abre direto; as visualizações de detalhe listadas em "
    u"Páginas sem cartão de menu abrem a partir das páginas que as contêm.",
    u"# Carteira",
    u"- [Painel](#/)",
    u"- [Minha Conta](#/account/me)",
    u"- [Contas](#/accounts)",
    u"- [Transferência](#/transfer)",
    u"- [Fatura](#/invoice)",
    u"- [Vesting](#/vesting)",
    u"- [Carteira](#/wallet)",
    u"- [Trocar senha da carteira](#/wallet/password)",
    u"- [Criar Carteira (Brainkey)](#/create-wallet-brainkey)",
    u"- [Importar conta existente](#/existing-account)",
    u"- [Registrar nova conta](#/create-account)",
    u"- [Entrar](#/login)",
    u"- [Registro](#/registration)",
    u"- [Indicações](#/referrals)",
    u"# Negociação",
    u"- [Exchange](#/markets)",
    u"- [Negociação instantânea](#/instant-trade)",
    u"- [Pools de liquidez](#/pools)",
    u"- [Cross Rates](#/cross-rates)",
    u"- [Empréstimo](#/borrow)",
    u"- [Troca](#/barter)",
    u"- [Depósito / Saque](#/deposit-withdraw)",
    u"- [Fundos Same-T](#/samet)",
    u"- [Spotlight](#/spotlight)",
    u"# Ganhar e Proteger",
    u"- [Oferta de crédito](#/credit-offer)",
    u"- [Débito direto](#/direct-debit)",
    u"- [HTLC](#/htlc)",
    u"- [Tickets](#/tickets)",
    u"- [Airdrop](#/airdrop)",
    u"- [Autoridades personalizadas](#/authorities)",
    u"- [Listas de contas](#/lists)",
    u"# Governança",
    u"- [Votação](#/voting)",
    u"- [Propostas](#/proposals)",
    u"- [Criar Worker](#/create-worker)",
    u"- [Mercados de previsão](#/prediction)",
    u"# Discover",
    u"- [Explorador](#/explorer)",
    u"- [Ativos](#/assets)",
    u"- [Criar Ativo](#/assets/create)",
    u"- [Emitir Ativo](#/assets/issue)",
    u"- [Publicar Feed](#/assets/feed)",
    u"- [Taxas da rede](#/explorer/fees)",
    u"- [Operações](#/ops)",
    u"- [Principais Operações](#/top-ops)",
    u"- [Notícias](#/news)",
    u"# Explorar",
    u"- [Explorar (Blockchain)](#/explorer)",
    u"- [Ativos](#/explorer/assets)",
    u"- [Pools](#/explorer/pools)",
    u"- [Contas](#/explorer/accounts)",
    u"- [Testemunhas](#/explorer/witnesses)",
    u"- [Comitê](#/explorer/committee)",
    u"- [Mercados](#/explorer/markets)",
    u"- [Taxas](#/explorer/fees)",
    u"- [Feeds](#/explorer/feeds)",
    u"# Labs",
    u"- [Laboratório API](#/api-lab)",
    u"- [Laboratório ES](#/es-lab)",
    u"- [Construtor de Transações](#/txbuilder)",
    u"- [Account Network](#/account-network)",
    u"# Personal",
    u"- [Trollbox](#/trollbox)",
    u"- [Favoritos](#/favourites)",
    u"- [Alertas de Preço](#/alerts)",
    u"- [Ajuda](#/help)",
    u"- [Limitações das traduções](#/help/translation-limitations)",
    u"- [Sobre](#/about)",
    u"- [Comunidade](#/community)",
    u"- [Configurações](#/settings)",
    u"# Páginas sem cartão de menu",
    u"Variantes de registro, mesas de conta e de mercado e visualizações de "
    u"detalhe abrem a partir das páginas acima ou de links em outros lugares "
    u"da carteira.",
    u"- [Registro local](#/registration/local)",
    u"- [Registro em nuvem](#/registration/cloud)",
    u"- [Página de conta de exemplo](#/account/committee-account)",
    u"- [Mesa de mercado de exemplo](#/market/BTS_USD)",
    u"- [Página de ativo de exemplo](#/asset/BTS)",
    u"- [Mesa de pool de exemplo](#/pools/1.19.66)",
    u"- [Visão geral do menu](#/menu)",
    u"Visualizações de detalhe de uma oferta de crédito específica, um negócio, "
    u"uma proposta, um bloco, uma transação, um HTLC, um mercado de previsão, "
    u"um destinatário de transferência, uma fatura, um gateway, uma aba de "
    u"configurações, uma aba do explorador ou um artigo de ajuda abrem a partir "
    u"das páginas que as contêm e recebem um id ou um nome no endereço.",
]

# The machine-translation honesty article. One entry per English line (23 of
# them, blank lines included) so the shape stays auditable in the source.
TRANSLATION_LIMITS = [
    u"Uma tradução marcada como preenchida por máquina foi escrita por uma "
    u"máquina. Ninguém a leu para conferir se diz o que o inglês diz — por isso "
    u"todo idioma exceto o inglês carrega o selo de marcador no cabeçalho desta "
    u"carteira. O inglês é o texto de onde os outros foram traduzidos, então "
    u"não carrega marcador.",
    u"",
    u"# O que o * em uma linha significa",
    u"Um * em uma linha de assinatura significa duas coisas ao mesmo tempo: o "
    u"texto foi preenchido por uma máquina e o inglês original está a um toque. "
    u"Toque no * e o inglês aparece abaixo da linha exatamente como o mestre "
    u"inglês desta carteira o guarda — o mesmo texto de onde todos os outros "
    u"idiomas foram traduzidos, não uma paráfrase dele.",
    u"",
    u"O marcador acompanha a linha, não as palavras dentro dela. Um * marca uma "
    u"linha traduzida inteira, e a carteira escolhe essas linhas por uma regra "
    u"fixa: toda linha em uma tela de assinatura, de ação irreversível ou de "
    u"recuperação — até um limite de tamanho, já que um parágrafo longo é coberto "
    u"por este artigo — mais qualquer linha, em qualquer lugar, cujo inglês traz "
    u"aviso de perigo. Então uma linha que só nomeia um id ou um valor ainda "
    u"carrega um (o campo Para de uma transferência, por exemplo), e um parágrafo "
    u"longo que menciona um id não carrega. Um valor cru da chain — um valor em "
    u"uma célula, um id em uma coluna, um símbolo de ativo — não é uma linha "
    u"traduzida, então nunca carrega um: não há texto em inglês atrás dele para "
    u"comparar.",
    u"",
    u"# O que significam os níveis de confiança",
    u"Todo idioma que esta carteira traz carrega uma nota, listada na tabela "
    u"abaixo. Alta significa que o texto acompanha de perto o inglês e lê de "
    u"forma natural. Boa significa que é usável, embora uma frase ainda possa "
    u"soar estranha. Moderada significa ler como rascunho e conferir o inglês "
    u"antes de confiar nela.",
    u"",
    u"Cada nota abaixo é a máquina que escreveu os textos avaliando o próprio "
    u"trabalho; ninguém independente auditou nenhuma. Uma nota descreve o que "
    u"já foi conferido, para o idioma como um todo e não linha por linha. O "
    u"próprio inglês é a referência: é escrito à mão, e todos os outros idiomas "
    u"são traduzidos a partir dele.",
    u"",
    u"# Como corrigir um texto",
    u"As correções começam com um relato. Diga em que idioma estava a linha, "
    u"informe a chave que essa linha revela, cole o inglês que ela deveria dizer "
    u"e sugira o texto que você usaria.",
    u"",
    u"- Um relato por linha deixa a correção fácil de aplicar.",
    u"- Relate primeiro as telas de assinatura: uma frase errada em um diálogo "
    u"de confirmação é o tipo caro.",
    u"- Use o link no fim deste artigo. Ele abre uma issue já rotulada para "
    u"traduções no tracker deste projeto, então não é preciso redigitar nada.",
    u"",
    u"# As correções são o único caminho para revisão humana",
    u"Nada mais tira um texto de preenchido por máquina: nem a frequência de uso "
    u"de um idioma, nem uma segunda máquina concordando com a primeira, nem uma "
    u"memória de tradução. Um texto passa a ser revisado por humano quando uma "
    u"pessoa o lê no próprio idioma e o aceita, e uma linha só é revisada por "
    u"humano no idioma que realmente foi conferido.",
    u"",
    u"Até lá o marcador fica onde está. Uma tradução que ninguém leu é melhor do "
    u"que nenhuma tradução, mas não é a mesma coisa que uma validada por uma "
    u"pessoa.",
]

BACKUPS = [
    u"# Faça backup cedo, faça duas vezes",
    u"Faça um backup da sua carteira local antes de financiá-la — um backup "
    u"costuma bastar daqui em diante, mas guarde-o em pelo menos dois lugares "
    u"seguros que só você alcança.",
    u"Não existe arquivo de backup nesta carteira: sua brainkey É o backup, e a "
    u"frase secreta sozinha não restaura nada. Sem as palavras E a frase "
    u"secreta seus fundos se perdem. Nunca guarde a frase secreta junto das "
    u"palavras.",
    u"# Sua brainkey é o backup",
    u"Se você nunca importou chaves brutas na mão, toda a sua carteira deriva de "
    u"forma determinística de uma brainkey — uma sequência de palavras. Anotar a "
    u"brainkey faz backup de todas as contas e fundos daquela carteira.",
    u"Veja-a no gerenciador da carteira e copie para o papel, guardado separado "
    u"de qualquer coisa digital. Arquivos .bin da carteira de referência não "
    u"podem ser importados aqui — a carteira diz isso na tela, e não existe "
    u"download de arquivo.",
    u"# Avançado: autoridades hierárquicas",
    u"Se você usa autoridades ponderadas de múltiplas contas em vez de chaves "
    u"simples, um backup de chaves sozinho pode NÃO restaurar o acesso — a "
    u"própria estrutura de autoridades importa.",
    u"Releia o artigo Permissões e registre a configuração completa de "
    u"autoridades, não apenas as palavras.",
]

WALLETS = [
    u"# Um app web com cofre local",
    u"Este aplicativo roda no seu navegador e conversa com um nó da chain como "
    u"porta de entrada para a rede. Tudo que é secreto fica no cofre local do "
    u"seu navegador.",
    u"# Sem login em nuvem",
    u"Esta carteira não tem login de usuário e senha: toda carteira aqui é local "
    u"a um único navegador. Para usar sua conta em um navegador ou computador "
    u"novo, parta da mesma brainkey — não existem credenciais que a abram de "
    u"qualquer lugar sozinhas.",
    u"# Carteira local",
    u"Uma carteira local é um banco de dados dentro de um navegador específico. "
    u"Ela não vai com você para outro computador ou navegador a menos que você "
    u"leve a brainkey e a importe.",
    u"Veja o artigo Backups antes de confiar uma carteira local com fundos reais.",
    u"# Disciplina de senha",
    u"A senha criptografa o cofre. Senhas curtas ou reutilizadas caem em "
    u"tentativas; uma frase secreta única escrita no papel não.",
    u"Trocar a senha recriptografa tudo — verifique a senha atual primeiro, "
    u"depois confirme que a carteira ainda desbloqueia antes de sair.",
]

BROWSER = [
    u"# Recursos detectados, nunca nomes de marca",
    u"Esta carteira nunca pergunta qual navegador você usa — ela testa os quatro "
    u"recursos de plataforma que realmente precisa: WebSocket (dados da chain), "
    u"WebCrypto (cofre de chaves), BigInt (aritmética de dinheiro) e "
    u"armazenamento local (configurações). O silêncio é uma aprovação: sem "
    u"banner em um navegador moderno significa que está tudo presente.",
    u"# A causa mais comum: contexto inseguro",
    u"Navegadores modernos expõem o WebCrypto só em contextos seguros: páginas "
    u"https, localhost e arquivos abertos. O mesmo navegador atualizado servido "
    u"em http simples (por exemplo um endereço de LAN) informa WebCrypto "
    u"ausente — o navegador está bem, o endereço não. Sirva a pasta por https ou "
    u"localhost, ou abra o index.html direto.",
    u"# O que continua funcionando",
    u"Navegar sempre funciona: saldos, mercados, explorador e votação leem dados "
    u"públicos da chain sem nenhum recurso da carteira. Só a assinatura local "
    u"precisa do recurso que falta. Dispensar o aviso o esconde nesta máquina; "
    u"ele nunca bloqueia uma página.",
]

ABOUT_MAKING = [
    u"# A construção desta carteira",
    u"O que vem a seguir é a história original da construção: cada prompt que "
    u"criou esta carteira, de \"acquire bitshares-ui\" em 26 de setembro de 2026 "
    u"até a correção da issue-1 em 3 de outubro, com as respostas dos "
    u"construtores — preservadas sem edição.",
    u"Ela registra as decisões que sustentam esta carteira: desistir de mais um "
    u"uplift de React depois da issue #3583 e sua armadilha de mil horas, para "
    u"que esta carteira não dependa de nada com ciclo de lançamento; assinar "
    u"cada transação localmente como a carteira antiga em vez de terceirizar; "
    u"três temas com o visual clássico como padrão; números em termos humanos, "
    u"nunca inteiros crus da chain; layouts pensados primeiro para celular desde "
    u"a fatia 1; e taxas lidas da chain ao vivo, nunca estimadas. Leia como "
    u"história: foi assim que a carteira foi construída.",
    u"# O arquivo completo dos diálogos",
    u"O registro completo, troca por troca, fica na página Sobre (#/about). "
    u"Expanda a seção \"Full build dialog\" lá para navegar por todas as "
    u"trocas, filtrar por palavra-chave ou abrir uma troca específica com "
    u"?dialog=N.",
]


def J(lines):
    """Join a markdown body authored as one source line per rendered line."""
    return u"\n".join(lines)


PT = {
    # --------------------------------------------------------------- explorer
    # Asset-type mode chips. "SmartCoins" is the name pt.json already gives the
    # market-pegged assets (help.topic_assets-mpa_body), so the chip that lists
    # them keeps it; the other three are ordinary words.
    "explorer.assets_mode_all": u"Todos",
    "explorer.assets_mode_prediction": u"Previsão",
    "explorer.assets_mode_user": u"Emitidos por usuários",
    # "of" / "Showing" glue: pt.json already settled both for the markets tab
    # (explorer.markets_of = "de", explorer.markets_showing = "Mostrando").
    "explorer.assets_of": u"de",
    "explorer.assets_showing": u"Mostrando",
    "explorer.feed_cer_premium": (
        u"Prêmio da taxa de câmbio central (CER) (estimativa pela regra do "
        u"publicador)"
    ),
    "explorer.feeds_of": u"de",
    "explorer.feeds_showing": u"Mostrando",
    "explorer.feeds_scanned_suffix": u"analisados (primeiros 100 ativos)",
    "explorer.no_assets_match": u"Nenhum ativo corresponde a \"%(q)s\".",

    # ------------------------------------------------------------------- pool
    # "any leg" wording is chunk-A's market_net.asset_1_field, reused verbatim.
    "pool.asset_1_field": u"Ativo 1 (qualquer perna)",
    "pool.asset_2_field": u"Ativo 2 (qualquer perna)",
    "pool.clear_btn": u"Limpar",
    "pool.delete_not_empty": (
        u"Não vazia — %(legs)s precisa ler 0 antes de excluir."
    ),
    "pool.direct_hit": u"Busca direta de pool — paginação oculta.",
    "pool.map_core_self": u"BTS é o token central da BitShares",
    "pool.min_swaps": u"Mín. swaps",
    "pool.my_swaps_hint": (
        u" Execute um pelo painel Swap acima — seus swaps nesta pool aparecem aqui."
    ),
    "pool.no_filter_match": u"Nenhum swap corresponde a estes filtros.",
    "pool.share_or_pool_hint": u"símbolo, 1.3.x, ou pool 1.19.x",
    # "Spot" is the pt finance word for an unhedged, immediate price; the pool
    # section already spells out "à vista"-style ratios nowhere, so this is the
    # first spelling of it in the dictionary.
    "pool.spot_row": u"À vista",
    "pool.stake_autofill_hint": (
        u"Digite uma quantidade — a outra é preenchida pela razão da pool."
    ),
    "pool.stake_preview_bad": (
        u"Confira as quantidades — sem estimativa de cotas."
    ),
    "pool.stake_preview_need_both": (
        u"Informe as duas quantidades para estimar cotas."
    ),
    "pool.stake_preview_unavailable": (
        u"Estimativa de cotas indisponível (offline)."
    ),
    "pool.stake_ratio_empty": u"A pool está vazia — informe as duas manualmente.",
    "pool.stake_ratio_row": u"Razão (à vista)",
    "pool.stake_shares_row": u"Cotas LP estimadas",
    # "Desk" is "mesa" everywhere in pt.json (market.exchange_desk, the desk
    # blurbs); "swap" is the word the pool section already ships.
    "pool.swap_desk": u"Mesa de swap",
    "pool.swap_mkt_preview_dash": u"Taxa de mercado (prévia): —",
    "pool.swap_mkt_row": u"Taxa de mercado",
    "pool.swap_preview": u"Cotação (prévia): ",
    "pool.swap_preview_dash": u"Cotação (prévia): —",
    "pool.swaps_hint": (
        u" Os swaps aparecem depois da primeira execução nesta pool — "
        u"execute um pelo painel Swap acima."
    ),
    # Unlock-gate header and its single row label (same shape as chunk-A's
    # settings.confirm_remove_action / account "Desbloqueie para assinar").
    "pool.uc_action": u"Ação",
    "pool.uc_title": u"Desbloqueie para continuar",

    # --------------------------------------------------------------- pool_net
    "pool_net.canvas_label": (
        u"Mapa da rede de pools. Pressione Enter para abrir o BTS."
    ),
    "pool_net.col_a": u"Ativo 1",
    "pool_net.col_b": u"Ativo 2",
    "pool_net.collapse": u"Recolher",
    "pool_net.expand": u"Expandir",
    # "touch" is graph-speak the English borrows from graph theory; "toca" keeps
    # the same plain figure and pairs with verdict_star below.
    "pool_net.empty": u"Nenhuma pool toca este filtro.",
    "pool_net.direct": u"pareado com BTS",
    "pool_net.hops": u"%(n)s saltos até BTS",
    "pool_net.legend": u"Marcas",
    "pool_net.loading": u"Carregando rede…",
    # "shipped skeleton" is the placeholder graph shape the view draws while the
    # node is unreachable - literally a skeleton, and saying so is the honest
    # reading, so "esqueleto" stays.
    "pool_net.offline": (
        u"Rede indisponível — mostrando o esqueleto que vem com o app. "
        u"Tente de novo quando conectado."
    ),
    "pool_net.offline_empty": (
        u"Rede indisponível — nenhum esqueleto de pools em cache."
    ),
    "pool_net.orphan": u"isolado do BTS",
    "pool_net.partial": (
        u"Atualização ao vivo incompleta — mostrando as pools que vêm com o app."
    ),
    "pool_net.phys": u"Física",
    "pool_net.prompt": (
        u"Toque em um nó para o ativo, em uma linha para a pool."
    ),
    "pool_net.ramp": u"Tamanho da pool: pequeno → grande",
    "pool_net.ready": u"%(pools)s pools · %(assets)s ativos",
    "pool_net.title": u"Rede de pools",
    "pool_net.twin": u"Linhas de pool (%(n)s)",
    "pool_net.twin_more": (
        u"Mostrando %(shown)s de %(n)s pools — restrinja o filtro para ver "
        u"menos."
    ),
    "pool_net.verdict_full": u"%(pools)s pools · %(assets)s ativos",
    "pool_net.verdict_orphan": u"Sem rota entre %(a)s e %(b)s",
    "pool_net.verdict_path": u"%(a)s alcança %(b)s em %(n)s saltos",
    "pool_net.verdict_star": u"Pools que tocam %(s)s: %(n)s",

    # ------------------------------------------------------------------- help
    # UI chrome around the confidence table.
    "help.about_link": u"Sobre esta carteira",
    "help.confidence_language": u"Idioma",
    "help.confidence_level": u"Confiança",
    "help.confidence_high": u"Alta",
    "help.confidence_good": u"Boa",
    "help.confidence_moderate": u"Moderada — verifique",
    "help.elastic": (
        u"Índice comunitário de histórico (histórico de terceiros)"
    ),
    "help.report_translation_link": u"Relate um problema de tradução no GitHub",
    "help.sitemap_sections": u"Seções",
    "help.translation_confidence_heading": (
        u"O grau de confiança de cada idioma"
    ),
    # Topic titles. The bodies below reuse the same wording, and the already
    # translated ones (Help topics) set the register.
    "help.topic_community_title": u"Comunidade",
    "help.topic_community_text": (
        u"Chats, fóruns, exploradores e código em torno da BitShares."
    ),
    "help.topic_browser_title": u"Suporte a navegadores",
    "help.topic_browser_text": (
        u"Quais navegadores rodam a carteira e o que significa o aviso de "
        u"compatibilidade."
    ),
    "help.topic_menu_title": u"Menu do site",
    "help.topic_menu_text": (
        u"Todas as páginas desta carteira, agrupadas como o menu de navegação "
        u"as agrupa."
    ),
    "help.topic_sitemap_title": u"Mapa do site",
    "help.topic_sitemap_text": (
        u"Todas as páginas desta carteira em uma só: cada página de menu mais os "
        u"fluxos e as visualizações de detalhe que não têm cartão de menu."
    ),
    "help.topic_about-making_title": u"A construção desta carteira",
    "help.topic_about-making_text": u"A história da construção desta carteira —",
    "help.topic_assets-feed_title": u"Publicando feeds de preço",
    "help.topic_assets-feed_text": (
        u"Publique feeds de preço dos ativos atrelados ao mercado que você "
        u"alimenta."
    ),
    "help.topic_assets-issue_title": u"Emitindo ativos",
    "help.topic_assets-issue_text": (
        u"Crie nova oferta de um ativo que você controla pela mesa de emissão."
    ),
    "help.topic_htlc_text": (
        u"Swaps travados por hash que ou pagam ou reembolsam."
    ),
    "help.topic_voting_text": (
        u"Vote em testemunhas, comitê e workers — ou entregue seu voto a um "
        u"proxy."
    ),
    "help.topic_translation-limitations_title": u"Limitações das traduções",
    "help.topic_translation-limitations_text": (
        u"Traduções preenchidas por máquina são marcadas; a referência em inglês "
        u"está sempre a um toque. Ajude-nos a corrigir uma linha."
    ),
    # Bodies, authored one source line per rendered line.
    "help.topic_about-making_body": J(ABOUT_MAKING),
    "help.topic_assets-feed_body": J([
        u"# Publicando feeds de preço",
        u"Publique o preço de liquidação de um ativo atrelado ao mercado pela "
        u"mesa de feed; o diálogo de confirmação mostra a taxa exata antes de "
        u"você assinar.",
    ]),
    "help.topic_assets-issue_body": J([
        u"# Emitindo ativos",
        u"Crie nova oferta de um ativo que sua conta controla pela mesa de "
        u"emissão; os valores usam a precisão do ativo e o diálogo de confirmação "
        u"mostra a taxa exata antes de você assinar.",
    ]),
    "help.topic_backups_body": J(BACKUPS),
    "help.topic_browser_body": J(BROWSER),
    "help.topic_community_body": J([
        u"# Comunidade",
        u"Pessoas e lugares em torno da BitShares — página inicial, código, "
        u"exploradores, fóruns e chats — ficam na página Comunidade.",
    ]),
    "help.topic_menu_body": J([
        u"# Menu do site",
        u"A página Menu lista todas as telas desta carteira por seção, então "
        u"qualquer mesa fica a um toque.",
    ]),
    "help.topic_sitemap_body": J(SITEMAP),
    "help.topic_translation-limitations_body": J(TRANSLATION_LIMITS),
    "help.topic_wallets_body": J(WALLETS),
}

# Keys whose Portuguese value is BYTE-IDENTICAL to English on purpose, listed
# here so the coverage of every untranslated key of this batch is explicit and
# auditable instead of implied by their absence from PT. Each one is asserted to
# still equal en after the write, so a later pass cannot quietly turn a
# deliberate loanword into an unclaimed drift:
#
#   * loanwords a Brazilian crypto UI keeps in English: Pool, Stake, Swap,
#     SmartCoins, Volume, Feed, Blockchain, Dashboard, Airdrops, Workers,
#     Gateways, API Lab, ES Lab, Backups, Spotlight;
#   * acronyms, ids and raw field names a table row or a tooltip prints as
#     data: ID, INFO, MCR, MSSR, Op, Tx, Trx/s, "base ", " (core)",
#     " (virtual)", " [op ", mcr %(mcr)s; mssr %(mssr)s;
#   * pure glue: placeholder rows whose whole text is a format skeleton
#     (%(id)s @ %(ts)s, %(sym)s (%(id)s) · …) with nothing to translate.
KEPT_ENGLISH = {
    # ---- explorer
    "explorer.assets_mode_market": u"SmartCoins",
    "explorer.core_suffix": u" (core)",
    "explorer.feed_mcr_mssr": u"MCR / MSSR",
    "explorer.feed_mcr_mssr_title": u"mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": u"%(id)s @ %(ts)s",
    "explorer.id_row": u"ID",
    "explorer.info_h": u"INFO",
    # The markets tab already sorts "Change" as "Variação" but keeps "Volume"
    # in English (explorer.discrete_tip_volume), so both volume sorts stay.
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
    # ---- pool
    "pool.pool_row": u"Pool",
    "pool.stake_link": u"Stake",
    "pool.swap_stake_col": u"Swap/Stake",
    # ---- pool_net
    "pool_net.col_pool": u"Pool",
    "pool_net.edge_card": u"%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": u"%(pool)s · %(a)s–%(b)s",
    "pool_net.node_card": u"%(sym)s (%(id)s) · %(n)s pools · %(hops)s",
    # ---- help
    "help.topic_airdrop_title": u"Airdrops",
    "help.topic_api-lab_title": u"API Lab",
    "help.topic_backups_title": u"Backups",
    "help.topic_blockchain_title": u"Blockchain",
    "help.topic_dashboard_title": u"Dashboard",
    "help.topic_es-lab_title": u"ES Lab",
    "help.topic_gateways_title": u"Gateways",
    "help.topic_spotlight_title": u"Spotlight",
    "help.topic_workers_title": u"Workers",
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

    print("pt chunk-B1: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    for sec in sorted(SECTIONS):
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    print("  _meta.translated: %d -> %d (+%d, v1 claim kept in lockstep)"
          % (len(claimed), len(meta["translated"]), len(added)))
    if same_as_en:
        print("  identical-to-en (loanwords / acronyms / ids / glue / "
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
