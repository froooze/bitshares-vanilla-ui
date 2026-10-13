#!/usr/bin/env python3
"""i18n es: translate the HONESTY SURFACE -- the bootstrap strings of the
machine-translation warning itself.

Why this batch exists
---------------------
es.json is _meta v2 with provenance "machine", so the wallet labels its Spanish
strings as unreviewed. Until now the label and the asterisk's own labels were
the only thing a Spanish-only reader could read about it: all 11 honesty keys
were still byte-identical to English. A reader who only speaks Spanish could
therefore read "traducida por máquina, sin revisión humana" in the header chip
but not the asterisk's aria-label, not the confidence table under the article,
and not the article itself -- so the most safety-critical strings on the page
were the least translatable ones. commit 3432d9b removed the gate that pinned
them (`tooling/help-translation-limitations-test.js` now requires presence and
non-emptiness in every dict instead of byte-equality with en, with that commit's
own comment: "the honesty strings in particular MUST be translatable: a reader
who only understands the target language cannot be warned in a language they do
not read"). That unblocks this batch.

Scope: ONLY the keys in ES below, in vanilla/locales/es.json, and NOTHING else.
Other agents have uncommitted work in the same working tree and are handling the
other 11 dictionaries separately, so this script is strictly insert-only:

  * a key already holding a NON-English value is REFUSED (never overwritten);
  * a key holding the English value is filled with the translation below;
  * a key already holding this batch's translation is skipped (re-runnable);
  * a key missing from es.json, or whose English master moved, is REFUSED;
  * no key outside ES is even read, let alone written.

Safety gates asserted before anything is written (see main()):

  G1  placeholders   %(name)s multiset unchanged for every filled key;
  G2  identifiers    a value that is an object id / URL / route / asset symbol
                     as a WHOLE stays byte-verbatim;
  G3  never-translate  i18n.badge_chip, shell.brand, settings.theme_* and
                     settings.network_* are refused if they ever appear in ES;
  G4  structure      same line count and same markdown link hashes (#/...) for
                     every filled key, measured against the ENGLISH master --
                     the article body is markdown that paintBlock() splits on
                     blank lines and re-reads `# ` / `- ` prefixes, so a
                     drifted newline or bullet marker breaks the rendered page
                     while every JSON gate stays green;
  G5  untouched      every key outside ES keeps its exact prior value, the key
                     SET is unchanged, and _meta is byte-identical (filling
                     strings is not verification: provenance stays "machine",
                     verified stays []);
  G6  formatting     json.dumps(indent=2, ensure_ascii=False) + trailing
                     newline round-trips the untouched file byte-for-byte.

Wording decisions, in the order they were made
----------------------------------------------
* Register is informal tu, matching every other shipped article. `pulsa` is the
  dict's established word for tapping a control (borrow.unlocked_rereview_note,
  confirm.fee_hint), so "one tap away" is "a un toque" and "Tap the *" is
  "Pulsa el *".
* i18n.risk_show_english / i18n.risk_about_translations reuse the wording
  tooling/risk-text-test.js already asserts in its locale-aware sandbox
  ("Mostrar la referencia en inglés de esta línea", "Acerca de estas
  traducciones"). Keeping the shipped dict identical to the strings the test
  already models means the widget reads as one voice with its own test.
* The confidence levels are NOT composed into a sentence anywhere: help-ui.js
  paints them as table CELLS (paintConfidence -> TableRenderer column "level")
  and as the second line of a phone card. So they are bare labels, and Spanish
  gender has to agree with a noun. They agree with the column header
  (`Confianza`, feminine): Alta / Buena / Moderada — verifícala. The article
  prose below then uses the same three adjectives in the same gender, so a
  reader who lands on the prose and a reader who lands on the table are reading
  the same word for the same rating.
* `strings` is translated as `textos`, not `cadenas`: `cadena` is already the
  chain in 20+ shipped strings (bloque/cadena/blockchain) and reusing it for an
  i18n string would be a true homonym.
* `issue`, `chip`, `paraphrase` handling: `issue` stays a loanword (the shipped
  dict already keeps it in help.topic_about-making_body), and the marker chip is
  named concretely as «i18n» on first mention because that is literally what the
  widget renders.
* The transfer's `To` field is `Para` in this dict (transfer.to_label,
  confirm.to, htlc.to), so the article says "el campo Para de una transferencia"
  rather than coining a second word for a label the reader has to find on screen.

Usage: python3 tooling/apply_i18n_es_honesty.py [--apply] [--verify]
  Default: dry run (asserts, prints planned changes, writes nothing).
  --apply:   rewrites vanilla/locales/es.json ONLY, and drops a pre-image of
             the untouched file in /tmp/opencode/ so a reviewer can diff against
             the exact bytes this run started from (the git baseline moves under
             concurrent agents, so HEAD is not a trustworthy pre-image).
  --verify:  re-proves the gates against that pre-image and prints the numbers a
             reviewer asks for. Writes nothing.
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
PREIMAGE = "/tmp/opencode/es-honesty-preimage.json"

# Byte-verbatim for life: the chip face, the brand, and the theme / network
# *ids* (the stored-preference values, never prose). The display labels that
# share the prefixes -- settings.theme_label / _title / _classic /
# _vanilla_light / _dex_dark -- are ordinary prose and ARE translated by an
# earlier chunk ("Tema", "Clásico", "Vanilla claro", "DEX oscuro"); asserting
# equality with English across the whole prefix would flag correct translations
# as drift, which is why the id keys are enumerated instead.
NEVER = (
    "i18n.badge_chip",
    "shell.brand",
    "shell.footer_brand",
    "shell.footer_brand_vanilla",
    "settings.theme_original_blue",
    "settings.theme_light",
    "settings.theme_dark",
    "settings.network_mainnet",
    "settings.network_testnet",
    "settings.network_devnet",
)
# Scope guard only: this batch may not ADD a key under either prefix. It says
# nothing about the existing keys under them.
NEVER_PREFIXES = ("settings.theme_", "settings.network_")

PLACEHOLDER = re.compile(r"%\([A-Za-z0-9_]+\)s")
IDENT = re.compile(
    r"^(1\.\d+\.\d+|#[#/][\w\-.?=&%/]*|https?://\S+|wss?://\S+)$"
)
LINK_HASH = re.compile(r"\]\((#[^)]*)\)")

_BODY = [
    "Una traducción marcada como hecha por máquina la escribió una máquina. Nadie "
    "la ha leído para comprobar que dice lo que dice el inglés — por eso todos los "
    "idiomas menos el inglés llevan el chip «i18n» en la cabecera de esta billetera. "
    "El inglés es el texto del que se tradujeron los demás, así que no lleva "
    "marcador.",

    "# Qué significa el * en una línea\n"
    "Un * en una línea de firma significa dos cosas a la vez: la redacción la "
    "rellenó una máquina y el inglés original está a un toque. Pulsa el * y el "
    "inglés aparece bajo la línea tal y como lo guarda el texto maestro en "
    "inglés de esta billetera — el mismo texto del que se tradujeron todos los "
    "demás idiomas, no una paráfrasis.",

    "El marcador va pegado a la línea, no a las palabras de dentro. Un * marca una "
    "línea traducida entera, y la billetera elige esas líneas con una regla fija: "
    "toda línea de una pantalla de firma, de acción irreversible o de recuperación "
    "— hasta un tope de longitud, porque un párrafo largo queda cubierto por este "
    "artículo — más cualquier línea, en cualquier pantalla, cuyo inglés lleve una "
    "palabra de aviso. Así que una línea que solo menciona un id o una cantidad "
    "también lleva una (el campo Para de una transferencia, por ejemplo), y un "
    "párrafo largo que menciona un id no. Un valor de la cadena sin más — una "
    "cantidad en una celda, un id en una columna, el símbolo de un activo — no es "
    "una línea traducida, así que nunca lleva una: detrás no hay redacción en "
    "inglés con la que compararlo.",

    "# Qué significan los niveles de confianza\n"
    "Cada idioma que incluye esta billetera lleva una calificación, listada en la "
    "tabla de abajo. Alta significa que la redacción sigue de cerca el inglés y se "
    "lee de forma natural. Buena significa que es utilizable, aunque alguna frase "
    "todavía puede sonar torpe. Moderada significa que la leas como un borrador y "
    "que compruebes el inglés antes de fiarte de ella.",

    "Todas las calificaciones de abajo son la máquina que escribió los textos "
    "calificando su propio trabajo; nadie independiente las ha auditado. Una "
    "calificación describe lo que se ha comprobado hasta ahora, para el idioma "
    "entero y no línea por línea. El inglés es la referencia: está escrito a "
    "mano, y todos los demás idiomas se traducen a partir de él.",

    "# Cómo corregir un texto\n"
    "Las correcciones empiezan con un reporte. Di en qué idioma estaba la línea, "
    "da la clave que esa línea muestra, pega el inglés que debería decir y sugiere "
    "la redacción que usarías en su lugar.",

    "- Un reporte por línea hace que la corrección sea fácil de aplicar.\n"
    "- Reporta primero las pantallas de firma: una frase equivocada en un diálogo "
    "de confirmación es el caso caro.\n"
    "- Usa el enlace del final de este artículo. Abre un issue ya etiquetado para "
    "traducciones en el rastreador de este proyecto, así que no hay que volver a "
    "escribir nada.",

    "# Las correcciones son el único camino a la revisión humana\n"
    "Nada más saca un texto de «hecho por máquina»: ni la frecuencia de uso de un "
    "idioma, ni una segunda máquina que coincida con la primera, ni una memoria de "
    "traducción. Un texto pasa a estar revisado por una persona cuando alguien lo "
    "lee en su idioma y lo acepta, y una línea solo está revisada para el idioma "
    "que de verdad se comprobó.",

    "Hasta entonces el marcador se queda donde está. Una traducción que nadie ha "
    "leído es mejor que no tener traducción, pero no es lo mismo que una que "
    "alguien haya respaldado.",
]

ES = {
    # ------------------------------------------------------- the two asterisk
    # labels. aria-label of the * button, so it is spoken at EVERY signing line:
    # kept to one short clause. The wording is not invented here --
    # tooling/risk-text-test.js:315-316 already asserts exactly these two strings
    # in its locale-aware sandbox, so shipping them makes the widget agree with
    # the test that covers it.
    "i18n.risk_show_english": "Mostrar la referencia en inglés de esta línea",
    # Label of the link under the expanded English line; it points at the
    # article. Register matches badge_details ("Qué significa esto").
    "i18n.risk_about_translations": "Acerca de estas traducciones",

    # ------------------------------------------------------- the article head
    # Article title: also the entry in the help index and the burger-menu
    # sitemap, so it is a noun phrase that names a limit, not a task.
    "help.topic_translation-limitations_title": "Límites de la traducción",
    # The one-line summary the help index shows under the title.
    "help.topic_translation-limitations_text": (
        "Las traducciones hechas por máquina están señaladas; el inglés original "
        "está siempre a un toque. Ayúdanos a corregir una línea."
    ),
    # The article itself. Structure (blank-line blocks, `# ` headings, `- `
    # bullets, the literal * marker) is byte-for-byte the English shape, because
    # paintBlock() re-parses it; wording follows the per-key decisions in the
    # module docstring.
    "help.topic_translation-limitations_body": "\n\n".join(_BODY),

    # ------------------------------------------------------- the confidence table
    # Column headers. "Idioma" and "Confianza" are both already the dict's words
    # (settings.language_title, trollbox.language_row / proposal.trust).
    "help.confidence_language": "Idioma",
    "help.confidence_level": "Confianza",
    # Bare cell labels, agreed feminine with the header "Confianza" -- see the
    # docstring. The prose section above reuses the same three adjectives in the
    # same gender, so table and prose cannot drift.
    "help.confidence_high": "Alta",
    "help.confidence_good": "Buena",
    "help.confidence_moderate": "Moderada — verifícala",
    # h2 above the generated table. Not in the task's list of 8, but it is the
    # heading of the very table those 8 keys fill; leaving it English would put a
    # Spanish table under an English heading in a Spanish article.
    "help.translation_confidence_heading": "Cuánta confianza tiene cada idioma",
    # The article's primary action: a call to action, so a verb phrase. "Informa
    # de" is the standard Spanish for "report something to somebody" and carries
    # the informal tu that every other shipped string uses.
    "help.report_translation_link": (
        "Informa de un problema de traducción en GitHub"
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
        ["git", "show", "HEAD:vanilla/locales/es.json"],
        cwd=os.path.join(HERE, "..")
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
    ph_filled = ph_ok = multi = multi_ok = links = links_ok = 0
    for k in changed:
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
        if IDENT.match(e[k]) and n[k] != e[k]:
            bad.append("identifier not byte-verbatim: %s" % k)

    for k in NEVER:
        if k in n and n[k] != e.get(k):
            bad.append("never-translate key is not byte-verbatim: %s" % k)

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
        bad.append('_meta.provenance is not "machine"')
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

    # G6: the on-disk formatting must survive a plain round trip, or this script
    # would reformat a file it is only supposed to fill.
    es_raw = open(ES_PATH, encoding="utf-8").read()
    es = json.loads(es_raw, object_pairs_hook=collections.OrderedDict)
    if json.dumps(es, indent=2, ensure_ascii=False) + "\n" != es_raw:
        print("REFUSING: es.json formatting is not indent=2/ensure_ascii=False + \\n")
        return 1
    before = collections.OrderedDict(flat(es))
    before_meta = json.dumps(es["_meta"], sort_keys=True, ensure_ascii=False)

    en_flat = flat(_load(EN_PATH))

    problems = []
    planned = []
    already = []

    for key in NEVER:
        if key in ES:
            problems.append("never-translate key is in ES: %s" % key)
    for key in sorted(ES):
        if key.startswith(NEVER_PREFIXES):
            problems.append("never-translate key is in ES: %s" % key)
        if key not in en_flat:
            problems.append("not in en master: %s" % key)
            continue
        if key not in before:
            problems.append("not in es.json: %s" % key)
            continue
        cur = before[key]
        if cur == ES[key]:
            already.append(key)
            continue
        if cur != en_flat[key]:
            problems.append("would overwrite a real translation: %s (%r)"
                            % (key, cur))
            continue

        # G1 placeholder multiset.
        if sorted(PLACEHOLDER.findall(en_flat[key])) != sorted(
                PLACEHOLDER.findall(ES[key])):
            problems.append("placeholder multiset changed: %s" % key)
        # G2 whole-value identifiers stay byte-verbatim.
        if IDENT.match(en_flat[key]) and en_flat[key] != ES[key]:
            problems.append("identifier not byte-verbatim: %s" % key)
        # G4 structure: line count and markdown link hashes, against en.
        if en_flat[key].count("\n") != ES[key].count("\n"):
            problems.append("line count changed: %s (%d vs %d)"
                            % (key, en_flat[key].count("\n"), ES[key].count("\n")))
        if LINK_HASH.findall(en_flat[key]) != LINK_HASH.findall(ES[key]):
            problems.append("link hash changed: %s" % key)

        planned.append(key)
        deep_set(es, key, ES[key])

    if problems:
        print("REFUSING:")
        print("\n".join(problems))
        return 1

    # G5: nothing outside this batch's keys moved, and _meta is untouched.
    after = flat(es)
    for key in after:
        if key in planned:
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

    print("es honesty batch: %d planned, %d already at their intended value"
          % (len(planned), len(already)))
    for k in sorted(ES):
        state = "translate" if k in planned else ("already" if k in already
                                                  else "UNPLANNED")
        print("  %-8s %s" % (state, k))
    if not apply:
        print("dry run -- no files written (pass --apply)")
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