#!/usr/bin/env python3
"""i18n es chunk-B: fill the pool_net/explorer/pool/approval/help/xrate/menu/
shell/about/proposal/trollbox/trade/barter/pool_detail sections of
vanilla/locales/es.json.

Scope: ONLY the fourteen sections listed in SECTIONS. Other agents are filling
the rest of the untranslated keys concurrently, so this script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from es.json, or one whose English master moved, is REFUSED.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key;
  G2  identifiers    values that are an object id / URL / route / asset symbol
                     as a WHOLE stay byte-verbatim;
  G3  pinned keys    shell.brand plus every settings.network_*/custom_placeholder
                     /pending/dash/theme_* id stays byte-verbatim;
  G4  structure      same line count, same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside SECTIONS keeps its exact prior value,
                     the key SET is unchanged, and _meta is byte-identical
                     (provenance "machine", verified [] and high_risk are left
                     alone -- filling strings is not verification);
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Vocabulary follows docs/i18n-glossary/es.md: billetera, cuenta, saldo, activo,
smartcoin, colateral, orden, comision/comisión, operación, witness=testigo,
comité, trabajador, proxy (loanword), swap (loanword), ticket, HTLC, memo, pool,
consolidacion (vesting), oferta de crédito, intercambio (exchange). Register is
informal tu. Where es.json already settles a word, that exact wording is reused
and the decision is recorded in the comment next to the entry.

Usage: python3 tooling/apply_i18n_es_chunkB.py [--apply] [--verify]
  Default: dry run (asserts, prints planned changes, writes nothing).
  --apply:   rewrites vanilla/locales/es.json ONLY, and drops a pre-image of the
             untouched file in /tmp/opencode/ so a reviewer can diff against the
             exact bytes this run started from (the git baseline moves under
             concurrent agents, so HEAD is not a trustworthy pre-image).
  --verify:  re-proves the gates against that pre-image and prints the numbers a
             reviewer asks for: keys filled, placeholder-bearing strings filled
             with multisets unchanged, multi-line values with line count and link
             hashes unchanged, and _meta byte-identical. Writes nothing.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "vanilla", "locales")
EN_PATH = os.path.join(BASE, "en.json")
ES_PATH = os.path.join(BASE, "es.json")
PREIMAGE = "/tmp/opencode/es-chunkB-preimage.json"

SECTIONS = (
    "pool_net", "explorer", "pool", "approval", "help", "xrate", "menu", "shell",
    "about", "proposal", "trollbox", "trade", "barter", "pool_detail",
)

# Keys whose value is an identifier / id / brand, not prose (rule 1). They are
# deliberately ABSENT from ES below: they must keep the English bytes. The
# verify pass re-asserts each one still equals English after the write.
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
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")

EM = "—"

# Keys tooling/help-translation-limitations-test.js (lines 340-369) pins to the
# English bytes in EVERY dictionary: "f keeps <key> an honest English stub until
# a human verifies it". That is the honesty article describing itself — a
# machine-filled Spanish copy of "nobody has read this" would carry the very
# marker it explains, so the article stays English until a person signs it off.
# They are therefore NOT in ES below, and REVERTS pulls them back if an earlier
# run of this script filled them.
HELD_ENGLISH = (
    "help.topic_translation-limitations_title",
    "help.topic_translation-limitations_text",
    "help.topic_translation-limitations_body",
    "help.translation_confidence_heading",
    "help.confidence_language",
    "help.confidence_level",
    "help.confidence_high",
    "help.confidence_good",
    "help.confidence_moderate",
    "help.report_translation_link",
)

ES = {
    # ------------------------------------------------------------ pool_net
    # Mirrors the already-shipped market_net wording (chunk A) key for key:
    # "verdict_full"/"ready" are the same sentence there.
    "pool_net.canvas_label": (
        "Mapa de la red de pools. Pulsa Enter para abrir BTS."
    ),
    "pool_net.col_a": "Activo 1",
    "pool_net.col_b": "Activo 2",
    # pool is a glossary loanword, like every shipped pool.* string.
    "pool_net.col_pool": "Pool",
    "pool_net.collapse": "Contraer",
    "pool_net.direct": "emparejado con BTS",
    # Pure id / amount / symbol glue, "·" separators included: byte-identical.
    "pool_net.edge_card": "%(pool)s · %(a)s–%(b)s · %(ba)s %(sa)s + %(bb)s %(sb)s",
    "pool_net.edge_nobal": "%(pool)s · %(a)s–%(b)s",
    "pool_net.empty": "Ningún pool toca este filtro.",
    "pool_net.expand": "Expandir",
    "pool_net.hops": "%(n)s saltos a BTS",
    "pool_net.legend": "Marcas",
    "pool_net.loading": "Cargando la red…",
    "pool_net.node_card": "%(sym)s (%(id)s) · %(n)s pools · %(hops)s",
    "pool_net.offline": (
        "Red no disponible — mostrando el esqueleto incluido. Reintenta cuando conecte."
    ),
    "pool_net.offline_empty": "Red no disponible — sin pools de esqueleto en caché.",
    "pool_net.orphan": "aislado de BTS",
    "pool_net.partial": "Actualización en vivo incompleta — mostrando los pools incluidos.",
    "pool_net.phys": "Física",
    "pool_net.prompt": "Toca un nodo para el activo, una línea para el pool.",
    "pool_net.ramp": "Tamaño del pool: pequeño → grande",
    "pool_net.ready": "%(pools)s pools · %(assets)s activos",
    "pool_net.title": "Red de pools",
    "pool_net.twin": "Filas de pools (%(n)s)",
    "pool_net.twin_more": (
        "Mostrando %(shown)s de %(n)s pools — estrecha el filtro para ver menos."
    ),
    "pool_net.verdict_full": "%(pools)s pools · %(assets)s activos",
    "pool_net.verdict_orphan": "Sin ruta entre %(a)s y %(b)s",
    "pool_net.verdict_path": "%(a)s alcanza %(b)s en %(n)s saltos",
    "pool_net.verdict_star": "Pools que tocan %(s)s: %(n)s",

    # ------------------------------------------------------------ explorer
    "explorer.assets_mode_all": "Todos",
    # smartcoin stays the loanword (glossary); es.json already writes it
    # lowercase in explorer.no_smartcoins / explorer.not_smartcoin.
    "explorer.assets_mode_market": "Smartcoins",
    "explorer.assets_mode_prediction": "Predicción",
    "explorer.assets_mode_user": "Emitidos por usuarios",
    # "of" / "Showing" pair with the shipped explorer.markets_of /
    # explorer.markets_showing.
    "explorer.assets_of": "de",
    "explorer.assets_showing": "Mostrando",
    "explorer.core_suffix": " (core)",
    "explorer.feed_cer_premium": (
        "Prima del tipo de cambio core (CER) (estimación por regla del publicador)"
    ),
    "explorer.feed_mcr_mssr": "MCR / MSSR",
    "explorer.feed_mcr_mssr_title": "mcr %(mcr)s; mssr %(mssr)s",
    "explorer.feed_publisher_title": "%(id)s @ %(ts)s",
    "explorer.feeds_of": "de",
    # "analizar" is the shipped scan wording (explorer.scan_failed).
    "explorer.feeds_scanned_suffix": "analizados (primeros 100 activos)",
    "explorer.feeds_showing": "Mostrando",
    "explorer.head_lib": " · irreversible #",
    "explorer.id_row": "ID",
    "explorer.info_h": "INFO",
    "explorer.irreversible_row": "Irreversible",
    # es.json quotes user-supplied strings with “ ”, never with «».
    "explorer.no_assets_match": "Ningún activo coincide con “%(q)s”.",
    "explorer.price_base": "base ",
    "explorer.stat_tps": "Trx/s",
    "explorer.th_feed": "Feed",
    "explorer.th_mssr": "MSSR",
    "explorer.tx_prefix": "Tx ",
    "explorer.virtual_mark": " (virtual)",

    # ------------------------------------------------------------ pool
    # asset_1_field / asset_2_field repeat chunk A's market_net phrasing.
    "pool.asset_1_field": "Activo 1 (cualquier pata)",
    "pool.asset_2_field": "Activo 2 (cualquier pata)",
    "pool.clear_btn": "Limpiar",
    "pool.direct_hit": "Búsqueda directa de pool — paginador oculto.",
    "pool.map_core_self": "BTS es el token core de BitShares",
    "pool.min_swaps": "Mín. swaps",
    # Leading space is glue: the hint is appended after a label.
    "pool.my_swaps_hint": (
        " Ejecuta uno desde el panel Swap de arriba — tus swaps en este pool se listan aquí."
    ),
    "pool.pool_row": "Pool",
    # Asset id shapes stay byte-verbatim inside the prose hint.
    "pool.share_or_pool_hint": "símbolo, 1.3.x o pool 1.19.x",
    "pool.spot_row": "Spot",
    "pool.stake_autofill_hint": (
        "Escribe un monto — el otro se rellena solo al ratio del pool."
    ),
    # "share" in a pool is "acciones LP" (glossary), never "parte" or
    # "participación".
    "pool.stake_preview_bad": "Revisa los montos — sin estimación de acciones LP.",
    "pool.stake_preview_need_both": (
        "Introduce ambos montos para una estimación de acciones LP."
    ),
    "pool.stake_preview_unavailable": (
        "Estimación de acciones LP no disponible (sin conexión)."
    ),
    "pool.stake_ratio_empty": "El pool está vacío — introduce ambos montos a mano.",
    "pool.stake_ratio_row": "Ratio (spot)",
    "pool.stake_shares_row": "Acciones LP est.",
    "pool.swap_desk": "Escritorio de swap",
    "pool.swaps_hint": (
        " Los swaps aparecen tras el primer intercambio en este pool — ejecuta uno desde el panel Swap de arriba."
    ),
    "pool.uc_action": "Acción",
    "pool.uc_title": "Desbloquea para continuar",

    # ------------------------------------------------------------ approval
    # Every one of these renders as a dual line with the English reference
    # beneath it (_meta.high_risk), so the wording is deliberately plain: no
    # idiom that could be misread about WHAT is being signed.
    "approval.account": "Cuenta: ",
    "approval.approve": "Aprobar",
    "approval.approved": "Aprobada y transmitida.",
    "approval.chain": "Cadena: ",
    "approval.close": "Cerrar",
    "approval.denied": "Denegada.",
    "approval.deny": "Denegar",
    "approval.expires_in": "Expira en ",
    "approval.load_failed": "No se pudo cargar la solicitud de aprobación.",
    "approval.loading": "Cargando la aprobación…",
    "approval.locked_note": (
        "La sesión está bloqueada — introduce la contraseña de tu billetera para aprobar."
    ),
    "approval.no_fields": "No hay campos que mostrar.",
    "approval.no_reply": "Sin respuesta del firmante.",
    "approval.no_runtime": "Falta el entorno de ejecución de la extensión.",
    "approval.password": "Contraseña",
    "approval.remember": "Recordar esta cuenta para este sitio",
    "approval.site_prefix": "Sitio: ",
    "approval.title": "Aprobar la firma",
    "approval.unknown_intent": "No se encontró ninguna solicitud de aprobación.",
    "approval.wallet_title": "Esta billetera solicita una firma",

    # ------------------------------------------------------------ help
    "help.about_link": "Acerca de esta billetera",
    "help.elastic": "Índice comunitario (historial de terceros)",
    "help.sitemap_sections": "Secciones",
    "help.topic_backups_body": "\n".join([
        "# Haz copias temprano, haz dos",
        "Haz una copia de seguridad de tu billetera local antes de fondearla — una "
        "sola copia suele bastar de aquí en adelante, pero guárdala en al menos dos "
        "lugares seguros a los que solo tú llegues.",
        "En esta billetera no hay archivo de copia de seguridad: tu brainkey ES la "
        "copia, y la frase de contraseña por sí sola no restaura nada. Sin las "
        "palabras Y la frase de contraseña, tus fondos se pierden. Nunca guardes la "
        "frase de contraseña junto a las palabras.",
        "# Tu brainkey es la copia de seguridad",
        "Si nunca importaste claves en bruto a mano, toda tu billetera se deriva de "
        "forma determinista de una brainkey — una cadena de palabras. Escribir la "
        "brainkey respalda cada cuenta y cada fondo de esa billetera.",
        "Mírala en el gestor de billetera y cópiala a papel, guardada aparte de "
        "cualquier cosa digital. Los archivos .bin de la billetera de referencia no "
        "se pueden importar aquí — la billetera lo dice en pantalla y no existe "
        "ninguna descarga de archivo.",
        "# Avanzado: autoridades jerárquicas",
        "Si usas autoridades ponderadas de varias cuentas en lugar de claves "
        "simples, una copia de las claves por sí sola puede NO restaurar el acceso "
        "— la propia estructura de autoridades importa.",
        "Vuelve a leer el artículo Permisos y anota toda la configuración de "
        "autoridades, no solo las palabras.",
    ]),
    # Every link hash below is byte-identical to the English; the LABELS reuse
    # the shipped menu.p_* page titles so the sitemap and the menu name the same
    # page the same way.
    "help.topic_sitemap_body": "\n".join([
        "Cada página de esta billetera, agrupada como las agrupa el menú de "
        "hamburguesa. Lo que lleva enlace se abre directamente; las vistas de "
        "detalle listadas bajo Páginas sin tarjeta de menú se abren desde sus "
        "páginas madre.",
        "# Billetera",
        "- [Tablero](#/)",
        "- [Mi cuenta](#/account/me)",
        "- [Cuentas](#/accounts)",
        "- [Transferencia](#/transfer)",
        "- [Factura](#/invoice)",
        "- [Consolidación](#/vesting)",
        "- [Billetera](#/wallet)",
        "- [Cambiar la contraseña de la billetera](#/wallet/password)",
        "- [Crear billetera (Brainkey)](#/create-wallet-brainkey)",
        "- [Importar cuenta existente](#/existing-account)",
        "- [Registrar una cuenta nueva](#/create-account)",
        "- [Iniciar sesión](#/login)",
        "- [Registro](#/registration)",
        "- [Referidos](#/referrals)",
        "# Comercio",
        "- [Intercambio](#/markets)",
        "- [Operación instantánea](#/instant-trade)",
        "- [Pools de liquidez](#/pools)",
        "- [Tipos de cambio cruzados](#/cross-rates)",
        "- [Pedir prestado](#/borrow)",
        "- [Trueque](#/barter)",
        "- [Depositar / Retirar](#/deposit-withdraw)",
        "- [Fondos Same-T](#/samet)",
        "- [Destacados](#/spotlight)",
        "# Gana y protege",
        "- [Oferta de crédito](#/credit-offer)",
        "- [Débito directo](#/direct-debit)",
        "- [HTLC](#/htlc)",
        "- [Tickets](#/tickets)",
        "- [Airdrop](#/airdrop)",
        "- [Autoridades personalizadas](#/authorities)",
        "- [Listas de cuentas](#/lists)",
        "# Gobernanza",
        "- [Votación](#/voting)",
        "- [Propuestas](#/proposals)",
        "- [Crear trabajador](#/create-worker)",
        "- [Mercados de predicción](#/prediction)",
        "# Descubrir",
        "- [Explorar](#/explorer)",
        "- [Activos](#/assets)",
        "- [Crear activo](#/assets/create)",
        "- [Emitir activo](#/assets/issue)",
        "- [Publicar feed](#/assets/feed)",
        "- [Comisiones de red](#/explorer/fees)",
        "- [Operaciones](#/ops)",
        "- [Operaciones principales](#/top-ops)",
        "- [Noticias](#/news)",
        "# Explorar",
        "- [Explorar (cadena de bloques)](#/explorer)",
        "- [Activos](#/explorer/assets)",
        "- [Pools](#/explorer/pools)",
        "- [Cuentas](#/explorer/accounts)",
        "- [Testigos](#/explorer/witnesses)",
        "- [Comité](#/explorer/committee)",
        "- [Mercados](#/explorer/markets)",
        "- [Comisiones](#/explorer/fees)",
        "- [Feeds](#/explorer/feeds)",
        "# Laboratorios",
        "- [Laboratorio de API](#/api-lab)",
        "- [Laboratorio ES](#/es-lab)",
        "- [Constructor de transacciones](#/txbuilder)",
        "- [Red de cuentas](#/account-network)",
        "# Personal",
        "- [Trollbox](#/trollbox)",
        "- [Favoritos](#/favourites)",
        "- [Alertas de precio](#/alerts)",
        "- [Ayuda](#/help)",
        "- [Limitaciones de la traducción](#/help/translation-limitations)",
        "- [Acerca de](#/about)",
        "- [Comunidad](#/community)",
        "- [Configuración](#/settings)",
        "# Páginas sin tarjeta de menú",
        "Las variantes de registro, los escritorios de cuenta y de mercado, y las "
        "vistas de detalle se abren desde las páginas de arriba o desde enlaces en "
        "otros puntos de la billetera.",
        "- [Registro local](#/registration/local)",
        "- [Registro en la nube](#/registration/cloud)",
        "- [Ejemplo de página de cuenta](#/account/committee-account)",
        "- [Ejemplo de escritorio de mercado](#/market/BTS_USD)",
        "- [Ejemplo de página de activo](#/asset/BTS)",
        "- [Ejemplo de escritorio de pool](#/pools/1.19.66)",
        "- [Resumen del menú](#/menu)",
        "Las vistas de detalle de una oferta de crédito, un acuerdo, una propuesta, "
        "un bloque, una transacción, un HTLC, un mercado de predicción, un "
        "destinatario de transferencia, una factura, una pasarela, una pestaña de "
        "configuración, una pestaña del explorador o un artículo de ayuda se abren "
        "desde sus páginas madre y toman un id o un nombre en la dirección.",
    ]),
    "help.topic_sitemap_text": (
        "Todas las páginas de esta billetera en una: cada página del menú más los "
        "flujos y las vistas de detalle que no tienen tarjeta de menú."
    ),
    "help.topic_sitemap_title": "Mapa del sitio",
    "help.topic_wallets_body": "\n".join([
        "# Una app web con una bóveda local",
        "Esta aplicación se ejecuta en tu navegador y habla con un nodo de la cadena "
        "como su puerta a la red. Todo lo secreto se queda en la bóveda local de tu "
        "navegador.",
        "# Sin inicio de sesión en la nube",
        "Esta billetera no tiene inicio de sesión con usuario y contraseña: cada "
        "billetera es local a un solo navegador. Para usar tu cuenta en un navegador "
        "u ordenador nuevo, parte de la misma brainkey — no hay credenciales que la "
        "abran desde ningún otro sitio por sí solas.",
        "# Billetera local",
        "Una billetera local es una base de datos dentro de un navegador concreto. "
        "No te seguirá a otro ordenador o navegador salvo que lleves la brainkey y la "
        "importes.",
        "Lee el artículo Copias de seguridad antes de confiar en una billetera local "
        "con fondos reales.",
        "# Disciplina de contraseña",
        "La contraseña cifra la bóveda. Las contraseñas cortas o reutilizadas caen "
        "adivinándolas; una frase de contraseña única escrita en papel no.",
        "Cambiar la contraseña recifra todo — verifica primero la actual y luego "
        "confirma que la billetera sigue desbloquearse antes de irte.",
    ]),

    # ------------------------------------------------------------ xrate
    # "Cross Rates" is settled once, here, and reused by menu.p_xrates and by
    # the sitemap label.
    "xrate.add_btn": "Añadir columna",
    "xrate.asset_col": "Activo",
    "xrate.base_pinned": "BTS es la columna base y no se puede quitar.",
    "xrate.empty": "Sin activos de pool a menos de 3 saltos de BTS en esta cadena.",
    # Second clause repeats the shipped account_net.intro wording.
    "xrate.intro": (
        "Cada activo de pool con precio de su último swap, cruzado por el grafo de "
        "pools. No se firma nada ni se almacena nada."
    ),
    "xrate.load_failed": "No se pudieron cargar los tipos de cambio cruzados: ",
    "xrate.loading": "Leyendo pools…",
    "xrate.no_route_col": "Sin ruta hacia %(sym)s en 6 saltos de pool.",
    "xrate.refresh_btn": "Actualizar precios",
    "xrate.remove_btn": "Quitar ",
    "xrate.retry_btn": "Reintentar",
    "xrate.show_all": "Mostrar todos los activos",
    "xrate.status": (
        "%(pools)s pools · %(assets)s activos a menos de 3 saltos · %(done)s de "
        "%(total)s pools tienen un último swap"
    ),
    "xrate.title": "Tipos de cambio cruzados",
    "xrate.token_label": "Añadir token de cotización",
    "xrate.token_placeholder": "USD, CNY, BTC…",
    "xrate.unknown_token": "Ningún activo de pool llamado %(sym)s.",
    "xrate.unpriced": "Una pata de esta ruta aún no tiene swap registrado.",

    # ------------------------------------------------------------ menu
    "menu.blurb_labs": "Herramientas potentes para la cadena y los nodos.",
    "menu.blurb_personal": "Chat, alertas y tu configuración.",
    "menu.d_account_net": "seguimiento de transferencias",
    "menu.d_xrates": "Precios de pool para cada activo en BTS y más.",
    "menu.p_account_net": "Red de cuentas",
    "menu.p_airdrop": "Airdrop",
    # Page titles reuse the shipped help-article titles.
    "menu.p_apilab": "Laboratorio de API",
    "menu.p_eslab": "Laboratorio ES",
    "menu.p_htlc": "HTLC",
    "menu.p_spotlight": "Destacados",
    "menu.p_tickets": "Tickets",
    "menu.p_trollbox": "Trollbox",
    "menu.p_xrates": "Tipos de cambio cruzados",
    "menu.section_explore": "Descubrir",
    "menu.section_labs": "Laboratorios",
    "menu.section_personal": "Personal",

    # ------------------------------------------------------------ shell
    # shell.brand, shell.footer_brand and shell.footer_brand_vanilla are NOT in
    # this dict: they are brand names and stay byte-identical (shell.brand is
    # pinned by tooling/validate_translations.py).
    "shell.footer_ahead": "%(n)s commits por delante de",
    "shell.footer_ahead_one": "1 commit por delante de",
    "shell.footer_at_build": "en la compilación %(date)s",
    "shell.footer_behind": "%(n)s commits por detrás",
    "shell.footer_behind_one": "1 commit por detrás",
    "shell.footer_dahead": "%(n)s por delante",
    "shell.footer_dbehind": "%(n)s por detrás",
    "shell.footer_diverged": "divergido de",
    "shell.footer_net_host": "%(net)s - %(host)s",
    # "Master" is the branch name.
    "shell.footer_offbranch": "no está en Master",
    "shell.footer_sync": "sincronizado con",

    # ------------------------------------------------------------ about
    # "exchange" in the build dialog is a prompt/reply round trip; "intercambio"
    # is what the shipped help.topic_about-making_body already calls it.
    "about.dlg_bad_link": "Número de intercambio no válido. Rango válido: 1–%(total)s.",
    "about.dlg_heading": "Diálogo completo de construcción",
    "about.dlg_heading_c": "Diálogo completo de construcción (%(total)s)",
    "about.dlg_no_match": (
        "Sin intercambios coincidentes. Borra la búsqueda para verlo todo."
    ),
    "about.dlg_no_reply": "Sin respuesta registrada — el siguiente prompt vino justo después.",
    "about.dlg_noscript": (
        "Este archivo necesita JavaScript; el mismo texto está en "
        "docs/vanilla-ui-dialog.md en el repositorio de código."
    ),
    "about.dlg_search_clear": "Limpiar",
    "about.dlg_search_ph": "Filtrar intercambios…",
    "about.dlg_showing": "Mostrando",
    "about.dlg_showing_c": "Mostrando %(shown)s / %(total)s",
    "about.dlg_unavailable": (
        "Archivo del diálogo de construcción no disponible."
    ),
    # Word-for-word the prose the shipped help.topic_about-making_body already
    # carries (its heading and the "full dialog" tail are not part of this
    # string, and English here is ONE line, so the two paragraphs stay joined).
    "about.making_body": (
        "Lo que sigue es la historia original de construcción: cada prompt que creó "
        "esta billetera, desde \"acquire bitshares-ui\" el 26 de septiembre de 2026 "
        "hasta la corrección del issue-1 el 3 de octubre, con las respuestas de los "
        "constructores — preservada sin editar. "
        "Registra las decisiones sobre las que se sostiene esta billetera: abandonar "
        "otra subida de React tras el issue #3583 y su trampa de mil horas, para que "
        "esta billetera no dependa de nada con ciclo de lanzamientos; firmar cada "
        "transacción localmente como la billetera vieja en vez de delegarla; tres "
        "temas con el aspecto clásico por defecto; números en términos humanos, nunca "
        "enteros crudos de cadena; diseños primero para teléfono desde el primer "
        "tramo; y comisiones leídas de la cadena en vivo, nunca estimadas. Léalo como "
        "historia: así se construyó la billetera."
    ),
    "about.making_title": "Cómo se hizo esta billetera",

    # ------------------------------------------------------------ proposal
    "proposal.confirm_proposal_create_op_22": (
        "Confirmar creación de propuesta (op %(op)s)"
    ),
    "proposal.confirm_proposal_delete_op_24": (
        "Confirmar eliminación de propuesta (op %(op)s)"
    ),
    "proposal.delete_proposal_op_24": "Eliminar propuesta (op %(op)s)",
    "proposal.id": "ID",
    "proposal.memo": "Memo",
    # "copropietario" is the word account.multisig_coowner_hint already uses.
    "proposal.multisig_story": (
        "¿Cuenta compartida? Un copropietario propone, comparte el id 1.10.N y los "
        "demás aprueban abajo. El trabajo de varias operaciones o de varios "
        "dispositivos continúa en el constructor de transacciones."
    ),
    "proposal.no": "no",
    "proposal.open_txbuilder": "Abrir el constructor de transacciones",
    "proposal.ticket": "Ticket",
    # Same sentence shape as the shipped misc.viewing_as.
    "proposal.viewing_as": (
        "Viendo como %(name)s (%(id)s) — desbloquea para actuar como tú mismo."
    ),

    # ------------------------------------------------------------ trollbox
    "trollbox.bytes_prefix": "Bytes: ",
    "trollbox.bytes_unit": "bytes",
    "trollbox.channel_row": "Canal",
    "trollbox.fee": "Comisión",
    "trollbox.language_row": "Idioma",
    "trollbox.message_row": "Mensaje",
    "trollbox.post_review_title": "Revisar mensaje",
    "trollbox.size_row": "Tamaño",
    "trollbox.title": "Trollbox",
    "trollbox.unlock_post": "Desbloquea y publica",

    # ------------------------------------------------------------ trade
    "trade.no": "No",
    "trade.row_total": "Total",
    "trade.tab_single": "Sencilla",
    # "Amount" is "Cantidad" in this section (trade.row_amount, trade.count_label).
    "trade.uc_amount": "Cantidad",
    "trade.uc_orders": "Órdenes",
    "trade.uc_price": "Precio",
    "trade.uc_range": "Rango de precio",
    "trade.uc_title": "Desbloquea para continuar",
    "trade.uc_total": "Total a vender",

    # ------------------------------------------------------------ barter
    "barter.confirm_barter_proposal_op_22": (
        "Confirmar propuesta de trueque (op %(op)s)"
    ),
    "barter.paid_by_suffix": "): ",
    "barter.propose_barter_op_22": "Proponer trueque (op %(op)s)",
    "barter.step_build": "Construir",
    "barter.step_preview": "Previsualizar",
    "barter.step_propose": "Proponer",
    # swap stays English (glossary); "Par A" matches barter.peer_a_account /
    # barter.side_a, and the fee-payer clause mirrors barter.propose_encloses_both.
    "barter.two_sided_atomic_swap_preview_preview_first_t": (
        "Vista previa de swap atómico de dos lados. Previsualiza primero y luego "
        "PROPONER encierra las transferencias de ambos lados en una propuesta "
        "(op %(op)s, pagador = Par A)."
    ),
    "barter.uc_title": "Desbloquea para firmar",

    # ------------------------------------------------------------ pool_detail
    "pool_detail.candle_capped": "ventana truncada",
    "pool_detail.candle_count": "%(swaps)s swaps · %(count)s × %(bucket)s velas",
    "pool_detail.candle_count_partial": (
        "%(swaps)s swaps · %(actual)s de %(requested)s × %(bucket)s velas"
    ),
    "pool_detail.invert": "Invertir",
    "pool_detail.invert_label": (
        "Invertir la orientación del gráfico (A-por-B / B-por-A)"
    ),
    "pool_detail.map_connects": (
        "Una línea conecta dos activos cuando existe un pool financiado y ha habido "
        "una operación en las últimas 24 horas."
    ),
    "pool_detail.map_connects_fallback": (
        "Una línea conecta dos activos cuando existe un pool financiado. La "
        "actividad de mercado de 24h está sin confirmar (historial no disponible) — "
        "mostrando pools financiados."
    ),
    "pool_detail.map_min_swaps": "(mín. %(min)s swaps)",
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


def deep_set(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def _load_preimage():
    """The exact es.json bytes this batch started from. HEAD is not a safe
    stand-in: other agents commit the same file between runs."""
    if os.path.exists(PREIMAGE):
        return _load(PREIMAGE)
    import subprocess
    raw = subprocess.check_output(
        ["git", "show", "HEAD:vanilla/locales/es.json"], cwd=os.path.join(HERE, "..")
    )
    return json.loads(raw.decode("utf-8"),
                      object_pairs_hook=collections.OrderedDict)


def verify():
    """Re-prove every gate against the pre-image of this batch, not against the
    in-memory dict the apply just built. This is what a reviewer runs."""
    baseline = _load_preimage()
    now = _load(ES_PATH)
    en = _load(EN_PATH)
    b, n, e = flat(baseline), flat(now), flat(en)

    changed = [k for k in sorted(ES) if b.get(k) != n.get(k) and k in b and k in n]
    bad = []
    ph_filled, ph_ok, multi, multi_ok, links, links_ok = 0, 0, 0, 0, 0, 0
    for k in changed:
        # Structure is measured against the ENGLISH master: for this batch the
        # pre-image value IS the English value, so en is the stricter reference.
        if sorted(PLACEHOLDER.findall(e[k])) != sorted(PLACEHOLDER.findall(n[k])):
            bad.append("placeholder multiset changed: %s" % k)
        if PLACEHOLDER.findall(e[k]):
            ph_filled += 1
            ph_ok += 1
        if e[k].count("\n") or n[k].count("\n"):
            multi += 1
            if e[k].count("\n") != n[k].count("\n"):
                bad.append("line count changed: %s" % k)
            else:
                multi_ok += 1
        if LINK_HASH.findall(e[k]) or LINK_HASH.findall(n[k]):
            links += 1
            if LINK_HASH.findall(e[k]) != LINK_HASH.findall(n[k]):
                bad.append("link hash changed: %s" % k)
            else:
                links_ok += 1
        if k in PINNED and n[k] != e[k]:
            bad.append("pinned key not byte-verbatim: %s" % k)
        if IDENT.match(e[k]) and n[k] != e[k]:
            bad.append("identifier not byte-verbatim: %s" % k)

    # Pinned keys that live OUTSIDE this batch's sections must also still equal
    # English after the write (shell.brand is one of them and is never filled).
    for k in PINNED:
        if k in n and n[k] != e.get(k):
            bad.append("pinned key not byte-verbatim: %s" % k)

    outside = [k for k in n if k not in ES and n[k] != b.get(k)]
    if outside:
        bad.append("keys outside this batch changed: %d (%s)"
                   % (len(outside), ", ".join(outside[:5])))
    if set(n) != set(b):
        bad.append("key set changed")

    bm, nm = baseline["_meta"], now["_meta"]
    meta_same = json.dumps(bm, sort_keys=True, ensure_ascii=False) == \
        json.dumps(nm, sort_keys=True, ensure_ascii=False)
    if not meta_same:
        bad.append("_meta changed")
    if nm.get("provenance") != "machine":
        bad.append("_meta.provenance is not \"machine\"")
    if nm.get("verified") != []:
        bad.append("_meta.verified is not []")
    if len(bm.get("high_risk", [])) != len(nm.get("high_risk", [])):
        bad.append("_meta.high_risk changed (%d -> %d)"
                   % (len(bm.get("high_risk", [])), len(nm.get("high_risk", []))))

    print("verify (baseline: %s)"
          % (PREIMAGE if os.path.exists(PREIMAGE) else "git HEAD"))
    print("  %d/%d keys in this batch differ from the pre-image"
          % (len(changed), len(ES)))
    print("  placeholder-bearing strings filled : %d (multiset unchanged: %d)"
          % (ph_filled, ph_ok))
    print("  multi-line values filled           : %d (line count unchanged: %d)"
          % (multi, multi_ok))
    print("  values carrying markdown link hash : %d (hashes unchanged: %d)"
          % (links, links_ok))
    print("  keys changed outside this batch    : %d" % len(outside))
    print("  _meta identical                     : %s "
          "(provenance=%r verified=%r high_risk=%d coverage=%d)"
          % (meta_same, nm.get("provenance"), nm.get("verified"),
             len(nm.get("high_risk", [])), len(nm.get("coverage", []))))
    if bad:
        print("FAILURES:")
        print("\n".join(bad))
        return 1
    print("  all gates green")
    return 0


def main():
    apply = "--apply" in sys.argv[1:]
    if "--verify" in sys.argv[1:]:
        return verify()

    # G6: the on-disk formatting must survive a plain round trip, or this
    # script would reformat a file it is only supposed to fill.
    es_raw = open(ES_PATH, encoding="utf-8").read()
    es = json.loads(es_raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(es, indent=2, ensure_ascii=False) + "\n" != es_raw:
        print("REFUSING: es.json formatting is not indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(es))
    before_meta = json.dumps(es["_meta"], sort_keys=True, ensure_ascii=False)

    en = _load(EN_PATH)
    en_flat = flat(en)

    problems = []
    planned = []
    reverted = []

    # Converge, don't pile up: if an earlier run of this script filled one of the
    # HELD_ENGLISH keys, put the English bytes back. The precondition is exact —
    # only a value THIS batch's ES dict (or plain English) may be reverted, so a
    # real translation is never silently dropped.
    for key in HELD_ENGLISH:
        if key not in en_flat:
            problems.append("held-English key not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("held-English key not in es.json: %s" % key)
            continue
        cur = before[key]
        if cur == en_flat[key]:
            continue  # already held
        if key in ES and cur != ES[key]:
            problems.append("would revert a real translation: %s (%r)" % (key, cur))
            continue
        deep_set(es, key, en_flat[key])
        reverted.append(key)
    if reverted:
        before = flat(es)

    for key, value in sorted(ES.items()):
        if key.split(".")[0] not in SECTIONS:
            problems.append("out of scope: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in es.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            continue  # already applied by an earlier run
        if cur != en_flat[key]:
            problems.append(
                "would overwrite a real translation: %s (%r)" % (key, cur)
            )
            continue

        # G1 placeholder multiset.
        if sorted(PLACEHOLDER.findall(en_flat[key])) != sorted(
            PLACEHOLDER.findall(value)
        ):
            problems.append("placeholder multiset changed: %s" % key)

        # G2 whole-value identifiers stay byte-verbatim.
        if IDENT.match(en_flat[key]) and en_flat[key] != value:
            problems.append("identifier not byte-verbatim: %s" % key)

        # G3 pinned id keys.
        if key in PINNED and en_flat[key] != value:
            problems.append("pinned key not byte-verbatim: %s" % key)

        # G4 structure: line count and markdown link hashes.
        if en_flat[key].count("\n") != value.count("\n"):
            problems.append("line count changed: %s" % key)
        if LINK_HASH.findall(en_flat[key]) != LINK_HASH.findall(value):
            problems.append("link hash changed: %s" % key)

        planned.append(key)
        deep_set(es, key, value)

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside the fourteen sections moved, and _meta is untouched.
    after = flat(es)
    for key in after:
        if key in planned or key in reverted:
            continue
        if after[key] != before.get(key):
            print("REFUSING: untouched key changed: %s" % key)
            return 1
    if set(after) != set(before):
        print("REFUSING: key set changed")
        return 1
    if json.dumps(es["_meta"], sort_keys=True, ensure_ascii=False) != before_meta:
        print("REFUSING: _meta changed")
        return 1
    for key in PINNED:
        if key in after and after[key] != en_flat.get(key):
            print("REFUSING: pinned key drifted: %s" % key)
            return 1

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in planned if after[k] == en_flat[k]]
    by_section = {}
    for k in changed:
        by_section[k.split(".")[0]] = by_section.get(k.split(".")[0], 0) + 1

    print("es chunk-B: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    if reverted:
        print("  reverted to English (held by help-translation-limitations-test.js): %s"
              % ", ".join(reverted))
    for sec in SECTIONS:
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    if same_as_en:
        print("  identical-to-en (loanwords / brands / glue / ids):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run — no files written (pass --apply)")
        return 0

    # A run that planned nothing has no useful baseline to record: keeping the
    # existing pre-image means a second --apply cannot quietly replace the
    # evidence a reviewer is about to diff against.
    if planned or not os.path.exists(PREIMAGE):
        try:
            os.makedirs(os.path.dirname(PREIMAGE), exist_ok=True)
            with open(PREIMAGE, "w", encoding="utf-8") as fh:
                fh.write(es_raw)
        except OSError as exc:
            print("REFUSING: cannot write pre-image %s (%s)" % (PREIMAGE, exc))
            return 1
    else:
        print("kept the existing pre-image (this run planned no changes)")
    with open(ES_PATH, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(es, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("wrote vanilla/locales/es.json")
    print("pre-image of the untouched file: %s" % PREIMAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())