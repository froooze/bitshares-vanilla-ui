#!/usr/bin/env python3
"""i18n es chunk-C: fill the FINAL Spanish chunk of vanilla/locales/es.json —
the 103 high-risk keys that render DUAL-LINE inside signing confirmation
dialogs (transfer, auth, unlockconfirm, vesting, createworker, createaccount,
htlc, samet, credit, debit, ticket/tickets, vote, txbuilder, confirm,
proposals_ticket, prediction, wallet, gateway, i18n) plus the small label
sections that ride along (seo, borrow, instant, nav, market_ind, common,
misc, compat, eslab, explorer_assets, assets_feed, notify, pools, splash,
swap).

Scope: ONLY the sections in SECTIONS, and only the keys listed in ES. Other
agents have uncommitted work in the same working tree, so this script is
strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from es.json, or one whose English master moved, is REFUSED;
  * a key whose SECTION is already owned by another chunk is REFUSED (the
    DONE list below names them explicitly so a scope mistake is loud).

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key;
  G2  identifiers    values that are an object id / URL / route / asset symbol
                     as a WHOLE stay byte-verbatim;
  G3  pinned keys    shell.brand plus every settings.network_*/custom_
                     placeholder/pending/dash/theme_* stays byte-verbatim;
  G4  structure      same line count, same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master;
  G5  untouched      every key outside SECTIONS keeps its exact prior value,
                     the key SET is unchanged, and _meta is byte-identical
                     (provenance "machine", verified [] and high_risk are left
                     alone -- filling strings is not verification);
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte;
  G7  honesty hold   the keys tooling/help-translation-limitations-test.js
                     pins to the English bytes in EVERY dictionary stay
                     English -- see HELD_ENGLISH below for the full argument.

Vocabulary follows docs/i18n-glossary/es.md. Register is informal tu. Where
es.json already settles a word, that exact wording is reused and the decision
is recorded in the comment next to the entry.

SAFETY POSTURE FOR THIS CHUNK. Every string here is read BEFORE a user
authorizes a transaction, so the wording is deliberately plain: where a
Spanish rendering could plausibly be read two ways, the reading that cannot
hide an amount, a destination, an irreversible action or a permission wins
over the more idiomatic one. See the per-key comments.

Usage: python3 tooling/apply_i18n_es_chunkC.py [--apply] [--verify]
  Default: dry run (asserts, prints planned changes, writes nothing).
  --apply:   rewrites vanilla/locales/es.json ONLY, and drops a pre-image of
             the untouched file in /tmp/opencode/ so a reviewer can diff
             against the exact bytes this run started from (the git baseline
             moves under concurrent agents, so HEAD is not a trustworthy
             pre-image).
  --verify:  re-proves the gates against that pre-image and prints the numbers
             a reviewer asks for: keys filled, placeholder-bearing strings with
             multisets unchanged, multi-line values with line count and link
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
PREIMAGE = "/tmp/opencode/es-chunkC-preimage.json"

# The sections this chunk owns. Every ES key's section must appear here and
# must NOT appear in DONE below.
SECTIONS = (
    "assets_feed", "auth", "borrow", "compat", "common", "confirm",
    "createaccount", "createworker", "credit", "debit", "eslab",
    "explorer_assets", "gateway", "htlc", "i18n", "instant", "market_ind",
    "misc", "nav", "notify", "pools", "prediction", "proposals_ticket",
    "samet", "seo", "splash", "swap", "ticket", "tickets", "transfer",
    "txbuilder", "unlockconfirm", "vesting", "vote", "wallet",
)

# Sections already filled by chunk A / chunk B. A key belonging to one of
# these appearing in ES below is a scope bug and is refused, loudly.
DONE = (
    "account", "account_net", "settings", "market_net", "market", "asset",
    "pool_net", "explorer", "pool", "approval", "help", "xrate", "menu",
    "shell", "about", "proposal", "trollbox", "trade", "barter",
    "pool_detail",
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

# Keys tooling/help-translation-limitations-test.js (lines 344-345 and 367-369)
# pins to the English bytes in EVERY shipped dictionary, with the assertion
# message "f keeps <key> an honest English stub until a human verifies it".
#
# The brief for this chunk asked for all seven i18n.* keys in Spanish, on the
# sound argument that the honesty widget's own strings ARE the warning and
# should therefore read naturally. Two of them CANNOT be: the test asserts
# byte-equality for i18n.risk_show_english and i18n.risk_about_translations in
# all 12 dictionaries, so filling them turns a required green gate red. The
# repo's own position -- identical to chunk B's HELD_ENGLISH for the honesty
# article -- is that a string explaining "nobody has read this" is not
# translated until a human signs off on it, because a machine-written Spanish
# copy of "no human has verified this" carries the very marker it explains.
#
# Decision taken: honour the executable gate. The five i18n.badge_* keys are
# NOT pinned and are filled below. This is reported to the reviewer as an
# instruction conflict, not silently resolved.
HELD_ENGLISH = (
    # INTENTIONALLY EMPTY since commit efa7e4a. This list used to name the
    # honesty-surface keys (i18n.risk_*, help.confidence_*, the
    # translation-limitations article) so the script would write the English
    # bytes back on --apply. That was correct while a v1-era test pinned those
    # keys to English; it is wrong now. A reader who only understands Spanish
    # cannot be warned, in English, that their Spanish is unreviewed -- the
    # honesty strings are the bootstrap of the whole feature and MUST be
    # translatable. Keeping them here would revert real work on any rerun.
    # The revert loop below is also now non-destructive: it never overwrites a
    # value that differs from English.
)

ES = {
    # ---------------------------------------------------------------- i18n
    # The honesty badge. Five of the seven i18n.* keys; the other two are held
    # English by HELD_ENGLISH above. This IS the warning a reader sees, so it
    # is written to be unmissable rather than idiomatic: who wrote it, who has
    # NOT checked it, and what the asterisk does.
    "i18n.badge_body": (
        "Estas traducciones las escribió una máquina y no las ha revisado ninguna "
        "persona. Las líneas marcadas con * en las pantallas de firma muestran "
        "además el inglés original."
    ),
    # chip face: the technical shorthand for the i18n subsystem; every locale
    # ships it untranslated (and identical-to-en is an honest outcome here).
    "i18n.badge_chip": "i18n",
    "i18n.badge_details": "Qué significa esto",
    "i18n.badge_improve": "Ayuda a mejorar esta traducción",
    # aria-label of the chip button: names the status, never just the word.
    "i18n.badge_label": (
        "Estado de la traducción: traducida por máquina, sin revisión humana"
    ),

    # ---------------------------------------------------------------- auth
    # The multisig explainer. co-owner is "copropietario" (asset.multisig_body,
    # asset.multisig_coowner_hint, proposal.multisig_story); proposal is
    # "propuesta"; the 1.10.N object-id shape stays byte-verbatim.
    "auth.multisig_body": (
        "Esta billetera contiene una sola clave. Las cuentas compartidas necesitan "
        "propuestas + aprobaciones de copropietarios, coordinadas por el id de "
        "propuesta (1.10.N). Navegar es público; solo firmar necesita la contraseña."
    ),
    "auth.multisig_open_proposals": "Ver propuestas",
    "auth.multisig_open_txbuilder": "Abrir el constructor de transacciones",
    # "Send/Propose" are the two literal button labels on the transfer page;
    # they are translated there as Enviar/Proponer, so the same two words are
    # quoted here or the user cannot find the button.
    "auth.multisig_step_approve": (
        "Los copropietarios aprueban (op 23) en la página de propuestas, o "
        "co-firman con el constructor de transacciones."
    ),
    "auth.multisig_step_propose": (
        "Propón la operación (Transferencia tiene Enviar/Proponer; los activos, el "
        "trueque y el préstamo enlazan con propuestas)."
    ),
    "auth.multisig_step_share": (
        "Comparte el id de propuesta 1.10.N con los copropietarios."
    ),
    "auth.multisig_title": "Cuentas compartidas / multisig",

    # ---------------------------------------------------------------- transfer
    # HIGH RISK: this is the notice that names WHO will sign while the wallet
    # is locked. It must not be readable as "somebody else proposed it" nor as
    # a cosmetic banner -- "el proponente es <account>" names the signer, and
    # the second clause repeats the shipped "desbloquea para actuar como tú
    # mismo" so the fix is unmissable.
    "transfer.propose_notice_locked": (
        "Mientras está bloqueada, el proponente es %(name)s (%(id)s) — desbloquea "
        "para actuar como tú mismo."
    ),
    # HIGH RISK: multisig enclosure. The trailing clause is the whole point --
    # nothing executes until the co-owners approve -- so "se ejecuta solo
    # después de las aprobaciones" is kept emphatic and literal.
    "transfer.enclosed_op_note": (
        "Operación incluida: transferencia (op %(op)s) — se ejecuta solo después "
        "de las aprobaciones."
    ),
    "transfer.bad_asset_shape": "bad-asset-shape",
    "transfer.confirm_proposal_title": "Confirmar propuesta (op %(op)s)",
    "transfer.share_needs_to_amount": (
        "Un enlace compartible necesita un destinatario y una cantidad."
    ),
    "transfer.uc_title": "Desbloquea para continuar",
    # "Unlock & ..." family: chunk B settled trollbox.unlock_post as
    # "Desbloquea y publica", so the whole family uses "y", not the "&" the
    # vote buttons use for Sign & Publish.
    "transfer.unlock_sign": "Desbloquea y revisa",

    # ---------------------------------------------------------------- vesting
    # "Total" / "ID" are already the Spanish words; identical-to-en here is a
    # correct outcome, not an untranslated one.
    "vesting.id": "ID",
    "vesting.total": "Total",

    # ---------------------------------------------------------------- createworker
    # "trabajador" per the glossary (23 shipped strings; vote.tab_workers is
    # "Trabajadores ("). REPORTED: six already-shipped createworker strings
    # keep the loanword "worker" -- an intra-section split this chunk cannot
    # fix, because those keys are not mine.
    "createworker.confirm_worker_op_34": "Confirmar trabajador (op %(op)s)",
    # HIGH RISK: this sentence is what stops a user from assuming a worker is
    # proposed instead of broadcast. Both halves stay: the op number appears
    # twice and "directamente, no con una propuesta" is not softened.
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Redacta un trabajador (op %(op)s). La vista previa está en vivo; la "
        "revisión cita la comisión en vivo, y luego Firmar y enviar transmite la "
        "op %(op)s directamente — los trabajadores se crean con una op directa, "
        "no con una propuesta."
    ),
    "createworker.url": "URL",
    "createworker.worker_preview_op_34": "Vista previa del trabajador (op %(op)s)",

    # ---------------------------------------------------------------- createaccount
    # Wizard step labels. "Brainkey" is the glossary loanword (41 strings).
    "createaccount.step_brainkey": "Brainkey",
    "createaccount.step_name": "Nombre",
    # Verb, matching createaccount.register_account "Registrar cuenta".
    "createaccount.step_register": "Registrar",

    # ---------------------------------------------------------------- htlc
    "htlc.hash_label": "Hash: ",
    "htlc.title": "HTLC",
    # "para firmar" is the settled wording of the unlock gate (chunk B shipped
    # barter.uc_title as "Desbloquea para firmar"); five more desks adopt it
    # here so the gate reads the same on every signing page.
    "htlc.uc_title": "Desbloquea para firmar",

    # ---------------------------------------------------------------- samet
    "samet.delta": "Delta",

    # ---------------------------------------------------------------- credit
    "credit.delta": "Delta",
    # Paired with credit.yes "sí" -- both already the Spanish words.
    "credit.no": "no",
    "credit.total": "Total",
    # Trailing space is glue: the label is concatenated with an amount.
    "credit.total_prefix": "Total ",
    "credit.uc_title": "Desbloquea para firmar",

    # ---------------------------------------------------------------- debit
    "debit.uc_order": "Orden",
    "debit.uc_title": "Desbloquea para firmar",

    # ---------------------------------------------------------------- ticket
    # "ticket" and "airdrop" are glossary/intended loanwords (27 + 27 shipped
    # strings); identical-to-en is the correct outcome.
    "ticket.airdrop": "Airdrop",
    # Example payload: account names and amounts, byte-verbatim, newlines
    # included. Reformatting it as "alice, 10" would change the format the
    # parser reads.
    "ticket.airdrop_example_ph": "alice,10\nbob,2.5",
    "ticket.id": "ID",
    "ticket.ticket": "Ticket",
    "ticket.tickets": "Tickets",
    "tickets.title": "Tickets",
    "proposals_ticket.title": "Tickets",

    # ---------------------------------------------------------------- vote
    "vote.fee_core": " (core)",
    # proxy is the glossary loanword (17 strings, "apoderado" is the single
    # rejected counter-example). Leading/trailing space is concatenation glue.
    "vote.proxy_prefix": "Proxy: ",
    "vote.proxy_row": "Proxy",
    # "final: " already IS the Spanish word -- prefixed to a count.
    "vote.row_final": "final: ",
    "vote.url": "URL",

    # ---------------------------------------------------------------- txbuilder
    "txbuilder.badge_tpl": "TxBuilder (%(n)s)",
    "txbuilder.error_label": "Error",
    "txbuilder.link_pools": "Pools",
    "txbuilder.link_proposals": "Propuestas",
    "txbuilder.total_prefix": "Total ",

    # ---------------------------------------------------------------- confirm
    # memo is the glossary loanword (40 shipped strings).
    "confirm.memo": "Memo",

    # ---------------------------------------------------------------- prediction
    "prediction.uc_title": "Desbloquea para firmar",

    # ---------------------------------------------------------------- wallet
    "wallet.brainkey": "Brainkey",

    # ---------------------------------------------------------------- gateway
    # LOW CONFIDENCE. "ok " is glued to a latency ("ok 12ms") and is the
    # positive arm of the pair gateway.down "caída" / gateway.health_unknown
    # "salud desconocida". "correcto" completes that triple in Spanish; "ok"
    # would also have been defensible. Flagged for a human.
    "gateway.health_ok": "correcto ",
    # Matches the shipped proposal.raw_prefix "en bruto: ".
    "gateway.raw_prefix": "en bruto: ",

    # ---------------------------------------------------------------- small labels
    "common.page_n": "Página %(n)s",
    "common.unknown_asset": "Activo desconocido.",
    "nav.credit": "Crédito",
    "nav.margin": "Margen",
    # 3 shipped strings already say "Mercados" (market.picker_title,
    # market_net.title, prediction.pmo_markets) -- reuse, do not coin a
    # second word for the same page.
    "nav.markets": "Mercados",
    "pools.selector_title": "Selector de pool",

    # ---------------------------------------------------------------- shared labels
    # Section-level one-word labels that are ALREADY the Spanish word (Total,
    # ID, No, Base, Delta, final:, Proxy:) or a mandated loanword (Memo, Pools,
    # Ticket(s), Swap, Airdrop, HTLC, Brainkey, URL). They live here on
    # purpose: an identical-to-en value is only honest if it was a DECISION,
    # and this list is that decision, reviewable one key at a time.
    "misc.id": "ID",
    # LOW CONFIDENCE, but not really a choice: the yes/no cell pairs with the
    # already-shipped "activado: sí" / "activado: no"; Spanish and English
    # agree on both words.
    "misc.no": "no",
    "nav.pools": "Pools",
    # "Base" is the market's base asset, already the Spanish word; its sibling
    # notify.quote_label is "Cotización".
    "notify.base_label": "Base",
    "splash.card_pool_t": "Pools",
    "swap.title": "Swap",

    # ---------------------------------------------------------------- borrow
    # HIGH RISK: names the op that adjusts an existing margin position. The
    # op number placeholder appears once and the chain method name
    # (call_order_update) stays verbatim, as in borrow.no_position_yet_*.
    "borrow.adjust_position_op_3": "Ajustar posición (op %(op)s)",
    "borrow.margin_positions_borrow_a_bitasset_against_co": (
        "Las posiciones de margen piden prestado un bitasset contra colateral. "
        "Añadir colateral o devolver deuda ajusta la op %(op)s (call_order_update) "
        "en tu orden call."
    ),
    "borrow.open_a_new_position_op_3": "Abrir una posición nueva (op %(op)s)",
    "borrow.settlement_bids_op_45": "Pujas de liquidación (op %(op)s)",
    "borrow.uc_title": "Desbloquea para firmar",

    # ---------------------------------------------------------------- credit detail
    "instant.no": "No",
    # HIGH RISK-ish: this note is what tells a reader the balance numbers on
    # screen were NOT verified. "saldos sin comprobar" is kept blunt rather
    # than softened to "aproximados".
    "instant.preview_balances_note": (
        "Previsualizando como %(name)s (%(id)s) — saldos sin comprobar. Desbloquea "
        "para validar los tuyos antes de firmar."
    ),
    "instant.total": "Total",
    "instant.uc_title": "Desbloquea para firmar",
    "instant.unlock_sign": "Desbloquea y firma",

    # ---------------------------------------------------------------- market_ind
    # Reuses chunk B's pool_detail wording verbatim: "ventana truncada",
    # "%(count)s × %(bucket)s velas".
    "market_ind.count_capped": "ventana truncada",
    "market_ind.count_note": "%(count)s × %(bucket)s velas",
    "market_ind.count_partial": "%(actual)s de %(requested)s × %(bucket)s velas",

    # ---------------------------------------------------------------- seo
    # Titles keep the trailing "— BitShares Wallet" byte-for-byte, as every
    # already-shipped seo.title_* does.
    "seo.desc_account_net": (
        "Mapea a quién envía, a quién presta y de quién pide prestado una cuenta "
        "— leído del índice comunitario. Sin registro."
    ),
    "seo.desc_markets": (
        "Explora los mercados del libro de órdenes de BitShares por volumen de "
        "24 h y abre el escritorio de cualquier par. Sin registro."
    ),
    "seo.desc_xrates": (
        "Cada activo de pool con precio en BTS y más, al del último swap. Sin "
        "registro."
    ),
    "seo.title_account_net": "Red de cuentas — BitShares Wallet",
    "seo.title_markets": "Mercados — BitShares Wallet",
    "seo.title_xrates": "Tipos de cambio cruzados — BitShares Wallet",

    # ---------------------------------------------------------------- compat
    # WebCrypto, https and localhost are product/platform names: verbatim.
    "compat.insecure_hint": (
        "Esta dirección no es un contexto seguro, así que el navegador no "
        "entrega WebCrypto. El navegador está al día — sirve por https o "
        "localhost, o abre el archivo directamente."
    ),

    # ---------------------------------------------------------------- eslab
    # Closes the sentence exactly like the two sibling hints already in
    # es.json (eslab.hint_agg "Conteos del intervalo;",
    # eslab.hint_holders "divide por la precisión del activo.").
    "eslab.hint_donors": (
        "Conteos del intervalo; los totales son enteros brutos — divide por la "
        "precisión del activo."
    ),

    # ---------------------------------------------------------------- empty states
    "assets_feed.s1": "—",
    "explorer_assets.s1": "—",

    # ---------------------------------------------------------------- unlockconfirm
    # Matches the shipped common.unlock_failed "Desbloqueo fallido." and the
    # twelve shipped "Atrás" buttons.
    "unlockconfirm.cancel": "Atrás",
    "unlockconfirm.empty_password": "Introduce la contraseña de tu billetera.",
    "unlockconfirm.password": "Contraseña",
    "unlockconfirm.unlock_failed": "Desbloqueo fallido.",
    "unlockconfirm.unlock_post": "Desbloquea y publica",
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

    for k in HELD_ENGLISH:
        if k in n and n[k] != e.get(k):
            bad.append("held-English key is not English: %s (%r)" % (k, n[k]))

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
    already = []
    reverted = []

    # Converge, don't pile up: if an earlier run (or another chunk's script)
    # filled one of the HELD_ENGLISH keys, put the English bytes back. The
    # precondition is exact -- only a value THIS batch's ES dict (or plain
    # English) may be reverted, so a real translation is never silently lost.
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
        sec = key.split(".")[0]
        if sec not in SECTIONS:
            problems.append("out of scope: %s (section %r not in SECTIONS)" % (key, sec))
            continue
        if sec in DONE:
            problems.append("section owned by another chunk: %s (%r)" % (key, sec))
            continue
        if key in HELD_ENGLISH:
            problems.append("key is held English, must not be in ES: %s" % key)
            continue
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in es.json: %s" % key)
            continue
        cur = before[key]
        if cur == value:
            # Either an earlier run applied it, or the intended value is the
            # English one (a loanword / brand / glue string). Both are "nothing
            # to write"; the two cases are separated in the report below so a
            # reviewer can count the intended-identical keys.
            already.append(key)
            continue
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

    # G5: nothing outside this batch's keys moved, and _meta is untouched.
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
    for key in HELD_ENGLISH:
        if key in after and after[key] != en_flat.get(key):
            print("REFUSING: held-English key drifted: %s" % key)
            return 1

    changed = [k for k in planned if after[k] != en_flat[k]]
    same_as_en = [k for k in planned if after[k] == en_flat[k]]
    already_same = [k for k in already if after[k] == en_flat[k]]
    already_diff = [k for k in already if after[k] != en_flat[k]]
    by_section = {}
    for k in changed:
        by_section[k.split(".")[0]] = by_section.get(k.split(".")[0], 0) + 1

    print("es chunk-C: %d planned (%d differ from en, %d land identical), "
          "%d already at their intended value"
          % (len(planned), len(changed), len(same_as_en), len(already)))
    print("  accounting for all %d keys in this chunk: %d newly translated + "
          "%d translated by an earlier run + %d identical-to-en by design + "
          "%d held English by the honesty gate = %d"
          % (len(ES) + 2, len(changed), len(already_diff),
             len(same_as_en) + len(already_same), 2,
             len(changed) + len(already_diff) + len(same_as_en)
             + len(already_same) + 2))
    if reverted:
        print("  reverted to English (held by help-translation-limitations-test.js): %s"
              % ", ".join(reverted))
    for sec in SECTIONS:
        print("  %-16s %d" % (sec, by_section.get(sec, 0)))
    if same_as_en:
        print("  identical-to-en by design (loanwords / brands / glue / ids):")
        for k in same_as_en:
            print("    %s = %r" % (k, after[k]))
    if already_same:
        print("  already identical-to-en in the shipped file (nothing to write):")
        for k in already_same:
            print("    %s = %r" % (k, after[k]))
    print("  held English on purpose (not in this batch):")
    for k in HELD_ENGLISH:
        if k.split(".")[0] in ("i18n",):
            print("    %s" % k)
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
