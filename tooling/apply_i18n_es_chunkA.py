#!/usr/bin/env python3
"""i18n es chunk-A: fill the account/account_net/settings/market/market_net/asset
sections of vanilla/locales/es.json.

Scope: ONLY the six sections listed in SECTIONS. Other agents are filling the
rest of the 705 untranslated keys concurrently, so this script is strictly
insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from es.json, or one whose English master moved, is REFUSED.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key;
  G2  identifiers    values that are an object id / URL / route / asset symbol
                     as a WHOLE stay byte-verbatim;
  G3  pinned keys    settings.network_mainnet, settings.network_testnet,
                     settings.network_devnet, settings.custom_placeholder,
                     settings.pending, settings.dash, settings.theme_*_*
                     byte-verbatim;
  G4  structure      same line count, same markdown link hashes (#/...) for
                     every filled key;
  G5  untouched      every key outside SECTIONS keeps its exact prior value,
                     and _meta is byte-identical (provenance "machine",
                     verified [] left alone -- filling strings is not
                     verification);
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Vocabulary follows docs/i18n-glossary/es.md: billetera, cuenta, saldo, activo,
smartcoin, colateral, orden, comisión, operacion, witness=testigo, comite,
trabajador, proxy (loanword), swap (loanword), ticket, HTLC, memo, pool,
consolidacion (vesting), oferta de credito, intercambio (exchange). Register
is informal tu, matching the rest of the shipped UI strings. Where es.json
already settles a word, that exact wording is reused.

Usage: python3 tooling/apply_i18n_es_chunkA.py [--apply] [--verify]
  Default: dry run (asserts, prints planned changes, writes nothing).
  --apply:   rewrites vanilla/locales/es.json ONLY.
  --verify:  re-proves the gates against the committed baseline
             (git show HEAD:vanilla/locales/es.json) and prints the numbers a
             reviewer asks for: keys filled, placeholder-bearing strings filled
             with multisets unchanged, multi-line values with line count and
             link hashes unchanged, and _meta byte-identical. Writes nothing.
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

SECTIONS = ("account", "account_net", "settings", "market", "market_net", "asset")

# Keys whose value is an identifier / id, not prose (rule 1).
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
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")

EM = "—"

ES = {
    # ---------------------------------------------------------------- account_net
    "account_net.title": "Red de cuentas",
    "account_net.intro": (
        "Introduce una o más cuentas para ver a quién envían, a quién prestan "
        "y de quién toman prestado. Se lee del índice comunitario de historial; "
        "no se firma nada ni se almacena nada."
    ),
    "account_net.seeds_label": "Cuentas para mapear",
    # account names + an object id: byte-verbatim.
    "account_net.seeds_placeholder": "committee-account, alice, 1.2.42",
    "account_net.go": "Dibujar la red",
    "account_net.idle": "Nada dibujado todavía.",
    "account_net.scanning": "Leyendo el índice comunitario…",
    "account_net.need_seeds": "Introduce al menos una cuenta para mapear.",
    "account_net.need_class": "Activa al menos un tipo de línea para dibujar.",
    "account_net.canvas_missing": (
        "El lienzo de red no está disponible en esta versión; la tabla de abajo "
        "sigue listando cada línea."
    ),
    "account_net.class_transfer": "Transferencia",
    "account_net.class_transfer_help": "Transferencias directas entre cuentas.",
    "account_net.class_credit": "Crédito",
    "account_net.class_credit_help": "Ofertas de crédito aceptadas y reembolsadas.",
    "account_net.class_override": "Transferencia con override",
    "account_net.class_override_help": (
        "Transferencias cuya comisión paga el emisor del activo."
    ),
    "account_net.class_debit": "Débito directo",
    "account_net.class_debit_help": (
        "Permisos y retiradas de débito directo."
    ),
    "account_net.class_htlc": "HTLC",
    "account_net.class_htlc_help": (
        "Contratos de bloqueo temporal con hash y sus actualizaciones."
    ),
    "account_net.class_vesting": "Consolidación",
    "account_net.class_vesting_help": (
        "Saldos en consolidación que administra un tercero."
    ),
    "account_net.status_scanned": (
        "%(scanned)s operaciones indexadas de %(n)s cuenta(s)"
    ),
    "account_net.status_graph": "%(nodes)s cuentas · %(edges)s líneas",
    "account_net.status_truncated": "%(n)s operaciones más recientes por cuenta",
    "account_net.status_node_cap": "primeras %(n)s contrapartes mostradas",
    "account_net.status_edge_cap": "primeras %(n)s líneas mostradas",
    "account_net.status_self": "%(n)s transferencias a sí mismo omitidas",
    "account_net.status_shape": "%(n)s entradas ilegibles omitidas",
    "account_net.status_credit_missing": (
        "%(n)s líneas de crédito omitidas (oferta o acuerdo no encontrado en cadena)"
    ),
    "account_net.status_unknown": "no encontrado: %(names)s",
    "account_net.detail_hint": (
        "Toca una línea para ver su detalle; toca una cuenta para abrirla."
    ),
    "account_net.detail_line": (
        "%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s ops · %(kind)s"
    ),
    "account_net.detail_span": "%(first)s → %(last)s",
    "account_net.kind_flow": "flujo",
    "account_net.kind_relation": "relación",
    "account_net.no_amount": "sin importe",
    "account_net.more_assets": " + %(n)s más",
    "account_net.twin_summary": "Vista de tabla (accesible)",
    "account_net.twin_from": "Desde",
    "account_net.twin_to": "Hacia",
    "account_net.twin_class": "Tipo",
    "account_net.twin_relation": "Flujo/relación",
    "account_net.twin_amount": "Importe",
    "account_net.twin_count": "Ops",
    "account_net.twin_span": "Primero → último",
    "account_net.twin_empty": (
        "Sin líneas entre estas cuentas en las operaciones indexadas exploradas."
    ),
    "account_net.es_disabled": (
        "El índice comunitario está desactivado. Actívalo en Configuración para "
        "dibujar este mapa."
    ),
    "account_net.es_bad_account": "Ese nombre no es una cuenta en esta cadena.",
    "account_net.es_unavailable": (
        "El índice comunitario no es accesible ahora mismo. Inténtalo de nuevo "
        "en un momento."
    ),
    "account_net.detail_line_one": (
        "%(from)s → %(to)s · %(class)s · %(amount)s · %(count)s op · %(kind)s"
    ),
    "account_net.status_credit_index": (
        "%(n)s líneas de crédito resueltas desde el índice (su objeto de oferta "
        "o acuerdo ya no está en la cadena)"
    ),
    "account_net.depth_label": "Profundidad",
    "account_net.depth_1": "1 salto",
    "account_net.depth_2": "2 saltos",
    "account_net.ring1_label": "Anillo 1",
    "account_net.ring2_label": "Anillo 2",
    "account_net.stale_settings": (
        "Cambió la profundidad o los vecinos — pulsa Dibujar la red."
    ),
    "account_net.status_depth": "mapa de %(depth)s",
    "account_net.status_expanded": "expandido: %(names)s",
    "account_net.status_unexpanded": "%(n)s contrapartes directas sin expandir",
    "account_net.status_expansion_scanned": (
        "%(n)s operaciones indexadas de las expansiones"
    ),
    "account_net.status_expansion_truncated": (
        "las exploraciones de expansión se truncaron a las operaciones más "
        "nuevas"
    ),
    "account_net.twin_depth": "Salto",

    # ---------------------------------------------------------------- market_net
    "market_net.title": "Mercados",
    "market_net.subtitle": (
        "Principales mercados del libro de órdenes por volumen 24h. Elige una "
        "fila para abrir el escritorio."
    ),
    "market_net.asset_1_field": "Activo 1 (cualquier pata)",
    "market_net.asset_2_field": "Activo 2 (cualquier pata)",
    "market_net.list_btn": "Listar mercados",
    "market_net.clear_btn": "Limpiar",
    "market_net.loading": "Cargando mercados…",
    "market_net.empty": "No se encontraron mercados para este filtro.",
    "market_net.offline": (
        "Red no disponible — mostrando mercados en caché. Reintenta cuando conecte."
    ),
    "market_net.col_market": "Mercado",
    "market_net.col_last": "Último",
    "market_net.col_change": "24h Δ",
    "market_net.col_vol": "Vol 24h",
    "market_net.col_spark": "7d",
    "market_net.band_title": "Red de mercados",
    "market_net.collapse": "Contraer",
    "market_net.expand": "Expandir",
    "market_net.edge_card": "%(desk)s · %(a)s–%(b)s · %(vol)s",
    "market_net.edge_card_fills": (
        "%(desk)s · %(a)s–%(b)s · %(fills)s ejecuciones/24h"
    ),
    "market_net.edge_card_price": "@ %(price)s",
    "market_net.node_card": "%(sym)s (%(id)s) · %(n)s mercados",
    "market_net.map_empty": "Sin mercados con volumen reciente.",
    "market_net.map_fallback": (
        "%(pairs)s pares · %(assets)s activos · ejecuciones 24h sin confirmar"
    ),
    "market_net.map_hops_ready": (
        "%(pairs)s pares · %(assets)s activos · ejecuciones 24h"
    ),
    "market_net.map_ready": "%(markets)s mercados · %(assets)s activos",
    "market_net.open_desk": "Abrir %(id)s",
    "market_net.prompt": (
        "Toca un nodo para el activo, una línea para el mercado."
    ),
    "market_net.ramp": "Volumen 24h: bajo → alto",
    "market_net.ramp_fills": "Ejecuciones 24h: baja → alta",
    "market_net.selector_title": "Selector de mercados",
    "market_net.spark_label": "Tendencia de 7 días para %(id)s",
    "market_net.canvas_label": (
        "Mapa de la red de mercados. Pulsa Enter para abrir el mercado."
    ),
    "market_net.top_note": (
        "Las primeras %(shown)s de %(probed)s probadas — por volumen 24h."
    ),
    "market_net.twin": "Filas de mercados (%(n)s)",
    "market_net.twin_more": (
        "Mostrando %(shown)s de %(n)s mercados — estrecha el filtro para ver menos."
    ),
    "market_net.verdict_full": "%(markets)s mercados · %(assets)s activos",
    "market_net.verdict_no_path": (
        "Sin ruta por mercados con ejecuciones entre %(a)s y %(b)s"
    ),
    "market_net.verdict_path": (
        "%(a)s alcanza %(b)s en %(n)s mercados con ejecuciones"
    ),
    "market_net.verdict_star": "Mercados que tocan %(s)s: %(n)s",
    "market_net.verdict_web": "Mercados alcanzables desde %(s)s: %(n)s",

    # ---------------------------------------------------------------- asset
    "asset.bitasset_row": "Bitasset",
    "asset.cer_row": "Tipo de cambio core (CER)",
    "asset.committee_fed_note": (
        "Con feed del comité: todos los miembros activos del comité pueden publicar."
    ),
    "asset.feed_history_title": "Historial de feeds",
    "asset.flags_title": "Permisos",
    "asset.history_capped": (
        "Mostrando los primeros 8 publicadores (limitado por velocidad)…"
    ),
    "asset.history_days": "Rango",
    "asset.history_exchange": "Cargando intercambio + pools…",
    "asset.history_failed": "No se pudo cargar el historial de feeds.",
    "asset.history_loading": "Cargando historial de feeds…",
    "asset.history_pub": "Publicador %(i)s/%(n)s…",
    "asset.invert_btn": "Invertir",
    "asset.issuer_defaults_to_the_viewing_as_accoun": (
        "El emisor por defecto es la cuenta que estás viendo (%(id)s bloqueada, "
        "tu cuenta desbloqueada) — escribe cualquier emisor que controles. Si "
        "abriste esto desde una página de cuenta, pega aquí ese nombre de cuenta."
    ),
    "asset.loading_producers": "Cargando productores…",
    "asset.mcr_row": "MCR",
    "asset.multisig_body": (
        "Si este activo necesita más de una aprobación, la firma directa falla "
        "— propone el cambio y pide a los copropietarios que lo aprueben (op 23)."
    ),
    "asset.multisig_coowner_hint": (
        "¿Copropietario? Propón el cambio en la página de propuestas y pide a los "
        "copropietarios que lo aprueben (op 23)."
    ),
    "asset.multisig_open_proposals": "Ver propuestas",
    "asset.multisig_open_txbuilder": "Abrir el constructor de transacciones",
    "asset.multisig_title": "¿Emisor compartido? Propónlo",
    "asset.nft_row": "NFT",
    "asset.no_history": (
        "Sin historial en este rango — los publicadores publican poco; prueba 90d."
    ),
    "asset.no_producers": (
        "Aún no hay feeds publicados — los productores aparecen aquí cuando publiquen."
    ),
    "asset.offset_row": "Desplazamiento",
    "asset.op_col": "Op",
    "asset.orientation_note": "%(m)s por %(b)s",
    "asset.plot_feeds": "Graficar feeds",
    "asset.producer_col": "Productor",
    "asset.producers_failed": "No se pudieron cargar los productores.",
    "asset.producers_live_title": "Productores de feeds",
    "asset.producers_title": "Productores de feeds (op %(op)s)",
    "asset.publish_op19_title": "Publicar feed (op %(op)s)",
    "asset.published_col": "Publicado",
    "asset.smartcoin_row": "Smartcoin",
    "asset.tab_pma": "PMA",
    "asset.tab_uia": "UIA",
    "asset.viewing_notice": "Viendo como %(name)s (%(id)s) — desbloquea para firmar.",
    "asset.witness_fed_note": (
        "Con feed de testigos: todos los testigos activos pueden publicar."
    ),

    # ---------------------------------------------------------------- settings
    "settings.age_s": "%(n)s s",
    "settings.confirm_back": "Atrás",
    "settings.confirm_remove_action": "Acción",
    "settings.confirm_remove_hide": (
        "Ocultar este nodo (permanece oculto hasta volver a añadirlo)"
    ),
    "settings.confirm_remove_result": "Resultado",
    "settings.confirm_remove_switch": "El nodo activo pasa a %(node)s",
    "settings.confirm_remove_title": "¿Eliminar nodo?",
    "settings.confirm_remove_unlist": "Quitar de mi lista",
    "settings.custom_placeholder": "wss://…",
    "settings.dash": EM,
    "settings.discover_note": (
        "**Buscar nodos busca listas de nodos en GitHub y luego prueba lo que "
        "encuentra. GitHub y los nodos probados ven tu dirección de red. Los "
        "resultados son candidatos para tu revisión — no se añade nada "
        "automáticamente."
    ),
    "settings.geo_note": (
        "*Las ubicaciones y los proveedores vienen de ipaddress.to (https, sin "
        "clave) — ve tu dirección cuando se le pregunta; las respuestas se "
        "guardan en caché en este dispositivo 24 horas."
    ),
    "settings.hist_no": "NO",
    "settings.hist_yes": "SÍ",
    "settings.language_title": "Idioma",
    "settings.network_devnet": "devnet",
    "settings.network_mainnet": "mainnet",
    "settings.network_testnet": "testnet",
    "settings.pending": "…",
    "settings.sign_auto": "Automático (extensión cuando esté disponible)",
    "settings.sign_badge": (
        "Firma con extensión activa — detalles en Iniciar sesión"
    ),
    "settings.sign_badge_local": (
        "Firma en esta página — detalles en Iniciar sesión"
    ),
    "settings.sign_browser": "Firmar siempre en esta página",
    "settings.sign_ext": "Usar siempre la extensión",
    "settings.sign_ext_absent": (
        "No se detectó ninguna extensión en este dispositivo — las firmas ocurren "
        "en esta página."
    ),
    "settings.sign_ext_present": "Extensión detectada en este dispositivo.",
    "settings.sign_guide": "Cómo instalar la extensión",
    "settings.sign_mode_browser": "Las firmas ocurren en la memoria de esta página.",
    "settings.sign_mode_ext": "Las firmas se aprueban en la ventana de la extensión.",
    "settings.sign_mode_ext_page": (
        "Las firmas permanecen en la extensión — aisladas de los sitios web."
    ),
    "settings.sign_revoke": "Revocar",
    "settings.sign_sites": "Sitios conectados",
    "settings.sign_sites_empty": (
        "Aún no hay sitios aprobados — las aprobaciones aparecen aquí con "
        "revocación por sitio."
    ),
    "settings.sign_sites_story_a": "Ejemplo: un juego de dados en ",
    "settings.sign_sites_story_b": (
        " pide jugar como tu cuenta — aprobarlo lo lista aquí, ligado solo a esa "
        "cuenta. Las firmas siguen pidiéndose cada vez. (Ese enlace no lleva a "
        "ningún sitio — es un ejemplo ficticio.)"
    ),
    "settings.sign_title": "Firma",
    "settings.sign_warn": (
        "Cualquier script que se ejecute en esta página — incluida una copia "
        "alojada comprometida — podría leer tus claves mientras estén "
        "desbloqueadas. Pasa la firma por la extensión, o ejecuta una copia que "
        "controls."
    ),
    "settings.th_chain": "Cadena",
    "settings.th_handshake": "Handshake",
    "settings.th_head": "Cabeza",
    "settings.th_history": "Historial",
    "settings.th_location": "Ubicación *",
    "settings.th_participation": "Participación",
    "settings.th_ping": "Ping",
    "settings.th_provider": "Proveedor *",
    "settings.theme_classic": "Clásico",
    "settings.theme_dark": "dark",
    "settings.theme_dex_dark": "DEX oscuro",
    "settings.theme_light": "light",
    "settings.theme_original_blue": "original-blue",
    "settings.theme_title": "Tema",
    "settings.theme_vanilla_light": "Vanilla claro",

    # ---------------------------------------------------------------- market
    "market.chg_label": "24h Δ",
    "market.discrete_fills": "ejecuciones",
    "market.discrete_no_fills": (
        "Aún sin ejecuciones — coloca una orden o prueba otro par."
    ),
    "market.discrete_swaps": "swaps",
    "market.discrete_tip_account": "Cuenta",
    "market.discrete_tip_block": "Bloque",
    "market.discrete_tip_order": "Orden",
    "market.discrete_tip_price": "Precio",
    "market.discrete_tip_time": "Hora",
    "market.discrete_tip_volume": "Volumen",
    "market.discrete_tip_volume_quote": "Volumen (quote)",
    "market.discrete_unavailable": "Indicadores no disponibles en Discrete.",
    "market.discrete_volume": "Volumen Discrete",
    "market.exchange_desk": "Escritorio de intercambio",
    "market.loading_pool_map": "Cargando mapa…",
    "market.log_label": "Log",
    "market.map_aria": (
        "Red de mercados. Las líneas son mercados con ejecuciones en las últimas "
        "24 horas."
    ),
    "market.map_connects": (
        "Una línea conecta dos activos cuando ha habido una operación de mercado "
        "en las últimas 24 horas."
    ),
    "market.map_connects_fallback": (
        "Una línea conecta dos activos cuando existe un pool financiado. La "
        "actividad de mercado de 24h está sin confirmar (historial no "
        "disponible) — mostrando pools financiados."
    ),
    "market.map_edge_fills": "%(desk)s · %(a)s–%(b)s · %(fills)s ejecuciones/24h",
    "market.map_edge_price": "@ %(price)s · %(vol)s",
    "market.map_hops_empty": (
        "Ningún mercado tuvo ejecuciones en las últimas 24 horas alrededor de "
        "estas patas."
    ),
    "market.map_hops_filtered": (
        "Una línea es un mercado con ejecuciones en las últimas 24 horas. "
        "Mostrando %(shown)s de %(total)s pares (mín. %(min)s ejecuciones/24h)."
    ),
    "market.map_hops_no_route": "Sin ruta hacia BTS por mercados con ejecuciones.",
    "market.map_hops_note": (
        "Una línea es un mercado con ejecuciones en las últimas 24 horas. "
        "%(pairs)s pares mostrados."
    ),
    "market.map_leg_ok": "{s} conecta con BTS",
    "market.map_leg_orphan": "AVISO: ¡{s} no tiene ruta por mercados con ejecuciones!",
    "market.min_fills": "Mín. ejecuciones",
    "market.ov_bb": "BB",
    "market.ov_ema": "EMA",
    "market.ov_psar": "PSAR",
    "market.ov_sma": "SMA",
    "market.stat_chg": "24h Δ",
    "market.stat_empty": EM,
    "market.tf_discrete": "Discrete",
    "market.th_total": "Total",
    "market.vol_label": "Vol",
    "market.vol_log": "Vol: Log",

    # ---------------------------------------------------------------- account
    "account.draw_network": "Dibujar la red",
    "account.multisig_checking": "Comprobando autoridades…",
    "account.multisig_open_txbuilder": "Abrir el constructor de transacciones",
    "account.multisig_shared": (
        "Cuenta compartida — activa %(ath)s/%(an)s · propietaria %(oth)s/%(on)s."
    ),
    "account.multisig_single": (
        "Clave única — activa %(ath)s/%(an)s · propietaria %(oth)s/%(on)s."
    ),
    "account.multisig_single_hint": (
        "¿Cuenta compartida? Las propuestas están en la página de propuestas."
    ),
    "account.multisig_unavailable": (
        "Autoridades no disponibles — las propuestas siguen listándose en la "
        "página de propuestas."
    ),
    "account.multisig_view_proposals": "Ver propuestas",
    "account.page_total": "Total de la página ≈ ",
    "account.portfolio_page": "Página %(page)s de %(pages)s",
    "account.prices_cover_this_page": (
        "Los precios cubren esta página — cambia de página para cotizar más activos."
    ),
    "account.raw_prefix": "raw ",
    "account.total": "Total ≈ ",
    # Operation labels: noun-phrase "… de …", matching the ten already-shipped
    # account.op_* values (Creación de cuenta, Actualización de orden call,
    # Ejecución de orden, Lista blanca de cuenta, …).
    "account.op_assert_op": "Afirmación",
    "account.op_asset_burn": "Quema de activo",
    "account.op_asset_issue": "Emisión de activo",
    "account.op_asset_settle": "Liquidación de activo",
    "account.op_asset_update": "Actualización de activo",
    "account.op_authority_create": "Creación de autoridad",
    "account.op_authority_delete": "Eliminación de autoridad",
    "account.op_authority_update": "Actualización de autoridad",
    "account.op_balance_claim": "Reclamo de saldo",
    "account.op_blind_from": "Transferencia desde ciega",
    "account.op_blind_to": "Transferencia a ciega",
    "account.op_blind_transfer": "Transferencia ciega",
    "account.op_claim_fees": "Reclamo de comisiones",
    "account.op_claim_pool": "Reclamo de pool",
    "account.op_collateral_bid": "Puja de colateral",
    "account.op_committee_join": "Ingreso al comité",
    "account.op_committee_update": "Actualización de comité",
    "account.op_custom_op": "Operación personalizada",
    "account.op_deal_expired": "Acuerdo expirado",
    "account.op_deal_repay": "Reembolso de acuerdo",
    "account.op_deal_update": "Actualización de acuerdo",
    "account.op_debit_claim": "Reclamo de débito directo",
    "account.op_debit_create": "Creación de débito directo",
    "account.op_debit_delete": "Eliminación de débito directo",
    "account.op_debit_update": "Actualización de débito directo",
    "account.op_execute_bid": "Ejecución de puja",
    "account.op_fba_distribute": "Distribución de FBA",
    "account.op_fee_pool_fund": "Financiación del fondo de comisiones",
    "account.op_feed_producers_update": "Actualización de productores de feeds",
    "account.op_feed_publish": "Publicación de feed",
    "account.op_global_settle": "Liquidación global",
    "account.op_htlc_create": "Creación de HTLC",
    "account.op_htlc_extend": "Extensión de HTLC",
    "account.op_htlc_redeem": "Canje de HTLC",
    "account.op_htlc_redeemed": "HTLC canjeado",
    "account.op_htlc_refund": "Reembolso de HTLC",
    "account.op_issuer_update": "Actualización de emisor",
    "account.op_offer_accept": "Aceptación de oferta de crédito",
    "account.op_offer_create": "Creación de oferta de crédito",
    "account.op_offer_delete": "Eliminación de oferta de crédito",
    "account.op_offer_update": "Actualización de oferta de crédito",
    "account.op_order_update": "Actualización de orden",
    "account.op_override_transfer": "Anulación override_transfer",
    "account.op_params_update": "Actualización de parámetros globales",
    "account.op_pool_create": "Creación de pool",
    "account.op_pool_delete": "Eliminación de pool",
    "account.op_pool_deposit": "Depósito en pool",
    "account.op_pool_swap": "Swap en pool",
    "account.op_pool_update": "Actualización de pool",
    "account.op_pool_withdraw": "Retirada de pool",
    "account.op_proposal_create": "Creación de propuesta",
    "account.op_proposal_delete": "Eliminación de propuesta",
    "account.op_proposal_update": "Actualización de propuesta",
    "account.op_samet_borrow": "Préstamo Same-T",
    "account.op_samet_create": "Creación de fondo Same-T",
    "account.op_samet_delete": "Eliminación de fondo Same-T",
    "account.op_samet_repay": "Devolución Same-T",
    "account.op_samet_update": "Actualización de fondo Same-T",
    "account.op_settle_cancel": "Cancelación de liquidación",
    "account.op_smartcoin_update": "Actualización de smartcoin",
    "account.op_ticket_create": "Creación de ticket",
    "account.op_ticket_update": "Actualización de ticket",
    "account.op_vesting_create": "Creación de consolidación",
    "account.op_vesting_withdraw": "Retirada de consolidación",
    "account.op_witness_join": "Ingreso como testigo",
    "account.op_witness_update": "Actualización de testigo",
    "account.op_worker_create": "Creación de trabajador",
    # History one-liners: past tense, same voice as the already-shipped
    # trade/vesting summaries.
    "account.sum_account_create": "Registró %(name)s",
    "account.sum_account_transfer": "Transfirió la cuenta a %(owner)s",
    "account.sum_account_update": "Cuenta actualizada: %(account)s",
    "account.sum_asset_burn": "Quemó %(amount)s",
    "account.sum_asset_create": "Creó el activo %(symbol)s",
    "account.sum_asset_issue": "Emitió %(amount)s a %(to)s",
    "account.sum_asset_settle": "Solicitó la liquidación de %(amount)s",
    "account.sum_asset_update": "Actualizó el activo %(asset)s",
    "account.sum_authorities": "Actualizó las autoridades de %(account)s",
    "account.sum_balance_claim": "Reclamó %(amount)s",
    "account.sum_bid": "Pujó %(coll)s por %(debt)s",
    "account.sum_blind": "Transferencia ciega (%(in)s dentro, %(out)s fuera)",
    "account.sum_call_update": (
        "Ajustó la posición: %(coll)s de colateral, %(debt)s de deuda"
    ),
    "account.sum_claim_fees": "Reclamó %(amount)s en comisiones",
    "account.sum_committee_create": "Se convirtió en miembro del comité: %(account)s",
    "account.sum_committee_update": "Actualizó al miembro del comité %(account)s",
    "account.sum_custom": "Operación personalizada de %(account)s",
    "account.sum_deal_expired": "El acuerdo %(deal)s expiró",
    "account.sum_deal_repay": "Reembolsó %(amount)s en el acuerdo %(deal)s",
    "account.sum_deal_update": "Actualizó el acuerdo %(deal)s",
    "account.sum_debit_claim": "Reclamó %(amount)s de débito",
    "account.sum_debit_create": "Autorizó un débito de %(amount)s para %(to)s",
    "account.sum_debit_delete": "Eliminó el permiso de débito %(perm)s",
    "account.sum_debit_update": "Actualizó el débito de %(amount)s para %(to)s",
    "account.sum_execute_bid": "Ejecutó la puja de %(coll)s por %(debt)s",
    "account.sum_fee_pool_fund": (
        "Financió el fondo de comisiones de %(asset)s con %(amount)s"
    ),
    "account.sum_feed": "Feed publicado para %(asset)s por %(publisher)s",
    "account.sum_feed_producers": "Fijó %(n)s productores de feeds para %(asset)s",
    "account.sum_fill": "Ejecutada: pagó %(pays)s, recibió %(receives)s",
    "account.sum_global_settle": "Liquidó globalmente %(asset)s",
    "account.sum_htlc_claimed": "HTLC %(id)s reclamado",
    "account.sum_htlc_create": "HTLC %(id)s: %(amount)s de %(from)s a %(to)s",
    "account.sum_htlc_extend": "Extendió el HTLC %(id)s",
    "account.sum_htlc_redeem": "Canj" + "e" + "ó el HTLC %(id)s",
    "account.sum_htlc_refund": "HTLC %(id)s reembolsado",
    "account.sum_issuer_update": "Nuevo emisor de %(asset)s: %(issuer)s",
    "account.sum_offer_accept": (
        "Tomó prestado %(amount)s contra %(coll)s (oferta %(offer)s)"
    ),
    "account.sum_offer_create": "Creó una oferta de crédito en %(asset)s",
    "account.sum_offer_delete": "Eliminó la oferta %(offer)s",
    "account.sum_offer_update": "Actualizó la oferta %(offer)s",
    "account.sum_order_cancel": "Canceló la orden %(order)s",
    "account.sum_order_create": "Ofreció %(sell)s por al menos %(buy)s",
    "account.sum_order_update": "Actualizó la orden %(order)s",
    "account.sum_pool_create": "Creó el pool %(a)s / %(b)s",
    "account.sum_pool_delete": "Eliminó el pool %(pool)s",
    "account.sum_pool_deposit": "Participó %(a)s + %(b)s en el pool %(pool)s",
    "account.sum_pool_swap": (
        "Hizo un swap de %(sell)s → al menos %(buy)s en el pool %(pool)s"
    ),
    "account.sum_pool_update": "Actualizó el pool %(pool)s",
    "account.sum_pool_withdraw": "Retiró %(shares)s del pool %(pool)s",
    "account.sum_proposal_create": "Propuso %(n)s operaciones",
    "account.sum_proposal_delete": "Eliminó la propuesta %(proposal)s",
    "account.sum_proposal_update": "Aprobó la propuesta %(proposal)s",
    "account.sum_samet_borrow": "Tomó prestado %(amount)s del fondo %(fund)s",
    "account.sum_samet_create": "Creó el fondo Same-T con %(amount)s",
    "account.sum_samet_delete": "Eliminó el fondo Same-T %(fund)s",
    "account.sum_samet_repay": "Devolvió %(amount)s al fondo %(fund)s",
    "account.sum_samet_update": "Actualizó el fondo Same-T %(fund)s",
    "account.sum_settle_cancel": "Canceló la liquidación de %(amount)s",
    "account.sum_smartcoin_update": "Actualizó la smartcoin %(asset)s",
    "account.sum_ticket_create": "Creó el ticket %(amount)s",
    "account.sum_ticket_update": "Actualizó el ticket %(ticket)s",
    "account.sum_transfer": "Transferencia de %(amount)s de %(from)s a %(to)s",
    "account.sum_transfer_recv": "Recibió %(amount)s de %(from)s",
    "account.sum_transfer_send": "Envió %(amount)s a %(to)s",
    "account.sum_upgrade": "Mejoró %(account)s",
    "account.sum_vesting_create": "Consolidó %(amount)s para %(owner)s",
    "account.sum_vesting_withdraw": "Retiró %(amount)s consolidado",
    "account.sum_whitelist": "Incluyó %(account)s en la lista blanca",
    "account.sum_witness_create": "Se convirtió en testigo: %(account)s",
    "account.sum_witness_update": "Actualizó al testigo %(account)s",
    "account.sum_worker_create": "Creó el trabajador \"%(name)s\"",
}


# Repairs to an EARLIER run of this same script, applied before the fill so a
# re-run converges instead of refusing. Asserted against the exact bad value:
# a typo that silently changed would be a silent money-looking string, so the
# assertion is the point. The bug: a stray U+00B7 MIDDLE DOT slipped into
# "Canj·eó" (see REPAIRS).
REPAIRS = {
    "account.sum_htlc_redeem": (
        "Canj" + "·" + "e" + "ó el HTLC %(id)s",
        "Canj" + "e" + "ó el HTLC %(id)s",
    ),
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


def verify():
    """Re-prove every gate against the COMMITTED baseline, not against the
    in-memory dict this script just built. This is what a reviewer runs."""
    import subprocess

    baseline = json.loads(
        subprocess.check_output(
            ["git", "show", "HEAD:vanilla/locales/es.json"], cwd=os.path.join(HERE, "..")
        ).decode("utf-8"),
        object_pairs_hook=collections.OrderedDict,
    )
    now = json.loads(
        open(ES_PATH, encoding="utf-8").read(),
        object_pairs_hook=collections.OrderedDict,
    )
    en = json.loads(
        open(EN_PATH, encoding="utf-8").read(),
        object_pairs_hook=collections.OrderedDict,
    )
    b, n, e = flat(baseline), flat(now), flat(en)

    changed = [k for k in sorted(ES) if b.get(k) != n.get(k) and k in b and k in n]
    bad = []
    ph_filled, ph_ok, multi, multi_ok, links, links_ok = 0, 0, 0, 0, 0, 0
    for k in changed:
        if sorted(PLACEHOLDER.findall(b[k])) != sorted(PLACEHOLDER.findall(n[k])):
            bad.append("placeholder multiset changed: %s" % k)
        if PLACEHOLDER.findall(b[k]):
            ph_filled += 1
            ph_ok += 1
        if b[k].count("\n") or n[k].count("\n"):
            multi += 1
            if b[k].count("\n") != n[k].count("\n"):
                bad.append("line count changed: %s" % k)
            else:
                multi_ok += 1
        if LINK_HASH.findall(b[k]) or LINK_HASH.findall(n[k]):
            links += 1
            if LINK_HASH.findall(b[k]) != LINK_HASH.findall(n[k]):
                bad.append("link hash changed: %s" % k)
            else:
                links_ok += 1
        if n[k] != e[k] and k in PINNED:
            bad.append("pinned key not byte-verbatim: %s" % k)
        if IDENT.match(e[k]) and n[k] != e[k]:
            bad.append("identifier not byte-verbatim: %s" % k)

    outside = [k for k in n if k not in ES and n[k] != b.get(k)]
    if outside:
        bad.append("keys outside this batch changed: %d" % len(outside))

    bm, nm = baseline["_meta"], now["_meta"]
    meta_same = json.dumps(bm, sort_keys=True) == json.dumps(nm, sort_keys=True)
    if not meta_same:
        bad.append("_meta changed")
    if nm.get("provenance") != "machine":
        bad.append("_meta.provenance is not \"machine\"")
    if nm.get("verified") != []:
        bad.append("_meta.verified is not []")
    if bm.get("high_risk") != nm.get("high_risk"):
        bad.append("_meta.high_risk changed")
    if bm.get("coverage") != nm.get("coverage"):
        bad.append("_meta.coverage changed")

    print("verify: %d/%d keys in this batch differ from the committed baseline"
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

    en = json.loads(
        open(EN_PATH, encoding="utf-8").read(),
        object_pairs_hook=collections.OrderedDict,
    )
    en_flat = flat(en)

    problems = []
    planned = []
    repaired = []

    for key, (bad, good) in sorted(REPAIRS.items()):
        if before.get(key) != bad:
            if before.get(key) == good:
                continue  # already repaired
            problems.append("repair precondition failed: %s (%r)"
                            % (key, before.get(key)))
            continue
        deep_set(es, key, good)
        repaired.append(key)

    if repaired:
        # Re-snapshot so the fill loop sees the repaired text as current and
        # treats the key as already-applied rather than as someone else's work.
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

    # G5: nothing outside the six sections moved, and _meta is untouched.
    after = flat(es)
    for key in after:
        if key in planned or key in repaired:
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

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in changed if after[k] == en_flat[k]]
    by_section = {}
    for k in changed:
        by_section[k.split(".")[0]] = by_section.get(k.split(".")[0], 0) + 1

    print("es chunk-A: %d planned, %d differ from en, %d intentionally identical"
          % (len(planned), len(changed), len(same_as_en)))
    if repaired:
        print("  repaired typo in %d key(s): %s"
              % (len(repaired), ", ".join(repaired)))
    for sec in SECTIONS:
        print("  %-12s %d" % (sec, by_section.get(sec, 0)))
    if same_as_en:
        print("  identical-to-en (loanwords / bare ids / symbols):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if not apply:
        print("dry run — no files written (pass --apply)")
        return 0

    with open(ES_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(es, indent=2, ensure_ascii=False))
        f.write("\n")
    print("wrote vanilla/locales/es.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
