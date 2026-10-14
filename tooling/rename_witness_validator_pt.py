#!/usr/bin/env python3
"""Rename "testemunha" -> "validador de blocos" in vanilla/locales/pt.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).

Compound (per brief, from locale's own attested words): sing
"validador de blocos", plur "validadores de blocos" — "bloco"/"blocos"
plus the "validar/validados/validade" stem ("produtoras de blocos" is the
help article's *definition*, not the term). Title case at sentence/title
start ("Validador(es) de blocos"), lowercase elsewhere. The old noun is
feminine ("a testemunha", "as testemunhas", "testemunha atualizada",
"produtoras"); the new noun is masculine, so articles, demonstratives and
participles flip with it ("o validador", "os validadores", "atualizado",
"produtores") — each flip below is explicit, never a bare noun swap. The
approved term is the full compound everywhere — bare "validador" alone is
not enough.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a testemunha-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\n" formatting.

Usage: python3 tooling/rename_witness_validator_pt.py [--apply]
Dry run (asserts only) by default; --apply writes pt.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PT = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

WITNESS_RE = re.compile(r"testemunha", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_witness_join": (
        "Entrada como testemunha",
        "Entrada como validador de blocos",
    ),
    "account.op_witness_update": (
        "Atualiza\xe7\xe3o de testemunha",
        "Atualiza\xe7\xe3o de validador de blocos",
    ),
    "account.sum_witness_create": (
        "Tornou-se testemunha: %(account)s",
        "Tornou-se validador de blocos: %(account)s",
    ),
    "account.sum_witness_update": (
        "Testemunha %(account)s atualizada",
        "Validador de blocos %(account)s atualizado",
    ),
    "asset.witness_fed_note": (
        "Alimentado por testemunhas: todas as testemunhas ativas podem publicar.",
        "Alimentado por validadores de blocos: todos os validadores de blocos ativos podem publicar.",
    ),
    "explorer.stat_wit": (
        "Testemunhas ativas",
        "Validadores de blocos ativos",
    ),
    "explorer.th_witness": (
        "Testemunha",
        "Validador de blocos",
    ),
    "explorer.witness_row": (
        "Testemunha",
        "Validador de blocos",
    ),
    "help.topic_assets-mpa_text": (
        "Smartcoins lastreadas em colateral com feeds de pre\xe7o das testemunhas.",
        "Smartcoins lastreadas em colateral com feeds de pre\xe7o dos validadores de blocos.",
    ),
    "help.topic_glossary_text": (
        "Nomes usados nesta carteira: objetos (1.x.y), opera\xe7\xf5es, testemunhas, comit\xea.",
        "Nomes usados nesta carteira: objetos (1.x.y), opera\xe7\xf5es, validadores de blocos, comit\xea.",
    ),
    "help.topic_voting_text": (
        "Vote em testemunhas, comit\xea e propostas de grant \u2014 ou entregue seu voto a um proxy.",
        "Vote em validadores de blocos, comit\xea e propostas de grant \u2014 ou entregue seu voto a um proxy.",
    ),
    "help.topic_witnesses_title": (
        "Testemunhas",
        "Validadores de blocos",
    ),
    "menu.d_asset_feed": (
        "Publique feeds de pre\xe7o como emissor ou testemunha.",
        "Publique feeds de pre\xe7o como emissor ou validador de blocos.",
    ),
    "menu.d_voting": (
        "Testemunhas, comit\xea, propostas de grant e proxies.",
        "Validadores de blocos, comit\xea, propostas de grant e proxies.",
    ),
    "news.voting_witnesses_committee_workers": (
        "Vota\xe7\xe3o \u2014 testemunhas, comit\xea, propostas de grant",
        "Vota\xe7\xe3o \u2014 validadores de blocos, comit\xea, propostas de grant",
    ),
    "seo.desc_voting": (
        "Vote em testemunhas, membros do comit\xea e propostas de grant da BitShares. Cada voto \xe9 assinado localmente no seu dispositivo.",
        "Vote em validadores de blocos, membros do comit\xea e propostas de grant da BitShares. Cada voto \xe9 assinado localmente no seu dispositivo.",
    ),
    "seo.title_voting": (
        "Votar em testemunhas \u2014 Carteira BitShares",
        "Votar em validadores de blocos \u2014 Carteira BitShares",
    ),
    "splash.pulse_witnesses": (
        "Testemunhas",
        "Validadores de blocos",
    ),
    "vote.ballot_intro": (
        "Seu stake elege testemunhas e comit\xea e financia propostas de grant \u2014 todas as contagens e cotas abaixo s\xe3o leituras ao vivo da chain.",
        "Seu stake elege validadores de blocos e comit\xea e financia propostas de grant \u2014 todas as contagens e cotas abaixo s\xe3o leituras ao vivo da chain.",
    ),
    "vote.confirm_witness_update_op_21": (
        "Confirmar atualiza\xe7\xe3o de testemunha (op %(op)s)",
        "Confirmar atualiza\xe7\xe3o de validador de blocos (op %(op)s)",
    ),
    "vote.empty_list": (
        "O n\xf3 n\xe3o retornou testemunhas nem membros do comit\xea.",
        "O n\xf3 n\xe3o retornou validadores de blocos nem membros do comit\xea.",
    ),
    "vote.join_as_witness": (
        "Entrar como testemunha",
        "Entrar como validador de blocos",
    ),
    "vote.no_witness_object_for_this_account_use_join_a": (
        "Sem objeto de testemunha para esta conta \u2014 use Entrar como testemunha.",
        "Sem objeto de validador de blocos para esta conta \u2014 use Entrar como validador de blocos.",
    ),
    "vote.tab_witnesses": (
        "Testemunhas (",
        "Validadores de blocos (",
    ),
    "vote.update_witness": (
        "Atualizar testemunha",
        "Atualizar validador de blocos",
    ),
    "vote.witness": (
        "Testemunha",
        "Validador de blocos",
    ),
    "vote.witness_updated": (
        "Testemunha atualizada",
        "Validador de blocos atualizado",
    ),
}

SNIPPETS = {
    "help.topic_assets-mpa_body": [
        (
            "testemunhas publicam os feeds de pre\xe7o do mundo real",
            "validadores de blocos publicam os feeds de pre\xe7o do mundo real",
            1,
        ),
    ],
    "help.topic_assets-private_body": [
        (
            "n\xe3o as testemunhas \u2014 escolhe quem pode publicar",
            "n\xe3o os validadores de blocos \u2014 escolhe quem pode publicar",
            1,
        ),
        (
            "sem esperar feeds de testemunhas.",
            "sem esperar feeds de validadores de blocos.",
            1,
        ),
        (
            "n\xe3o o das testemunhas:",
            "n\xe3o o dos validadores de blocos:",
            1,
        ),
    ],
    "help.topic_blockchain_body": [
        (
            "chamados testemunhas, e os mais votados",
            "chamados validadores de blocos, e os mais votados",
            1,
        ),
        (
            "contra o trabalho das testemunhas,",
            "contra o trabalho dos validadores de blocos,",
            1,
        ),
        (
            "Veja os artigos Vota\xe7\xe3o e Testemunhas.",
            "Veja os artigos Vota\xe7\xe3o e Validadores de blocos.",
            1,
        ),
    ],
    "help.topic_committee_body": [
        (
            "Como as testemunhas, membros do comit\xea",
            "Como os validadores de blocos, membros do comit\xea",
            1,
        ),
    ],
    "help.topic_dex-shorting_body": [
        (
            "o lastro m\xednimo das testemunhas.",
            "o lastro m\xednimo dos validadores de blocos.",
            1,
        ),
    ],
    "help.topic_glossary_body": [
        (
            "propostas, testemunhas \u2014 quase tudo",
            "propostas, validadores de blocos \u2014 quase tudo",
            1,
        ),
        (
            "Testemunhas produzem blocos;",
            "Validadores de blocos produzem blocos;",
            1,
        ),
    ],
    "help.topic_settings_body": [
        (
            "participa\xe7\xe3o de testemunhas e atraso",
            "participa\xe7\xe3o de validadores de blocos e atraso",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Testemunhas](#/explorer/witnesses)",
            "- [Validadores de blocos](#/explorer/witnesses)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "alimenta votos de testemunhas, comit\xea",
            "alimenta votos de validadores de blocos, comit\xea",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "n\xe3o pode votar diretamente em testemunhas, membros",
            "n\xe3o pode votar diretamente em validadores de blocos, membros",
            1,
        ),
        (
            "# Testemunhas\nTestemunhas constroem e assinam blocos",
            "# Validadores de blocos\nValidadores de blocos constroem e assinam blocos",
            1,
        ),
        (
            "est\xe3o no artigo Testemunhas.",
            "est\xe3o no artigo Validadores de blocos.",
            1,
        ),
    ],
    "help.topic_witnesses_body": [
        (
            "# O que as testemunhas fazem\nTestemunhas s\xe3o as produtoras",
            "# O que os validadores de blocos fazem\nValidadores de blocos s\xe3o os produtores",
            1,
        ),
        (
            "em quantas testemunhas quiser, e cada uma recebe",
            "em quantos validadores de blocos quiser, e cada um recebe",
            1,
        ),
    ],
}


def dig(d, key):
    node = d
    for seg in key.split("."):
        node = node[seg]
    return node


def set_dig(d, key, value):
    segs = key.split(".")
    node = d
    for seg in segs[:-1]:
        node = node[seg]
    node[segs[-1]] = value


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + "."))
        else:
            out[prefix + k] = v
    return out


def main():
    apply = "--apply" in sys.argv
    raw = open(PT, encoding="utf-8").read()
    d = json.loads(raw)
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no testemunha-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script's old string has no testemunha word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no testemunha-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no testemunha word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        for old_snip, new_snip, count in reps:
            assert cur.count(old_snip) == count, key
            cur = cur.replace(old_snip, new_snip)
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
        set_dig(d, key, cur)

    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        if WITNESS_RE.search(v):
            print("FAIL: %s still carries a testemunha word: %r" % (key, v[:120]))
            return 1

    after_keys = set(flatten(d))
    if after_keys != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    after_vals = flatten(d)
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(PT, "w", encoding="utf-8").write(out)
        print("OK pt: %d full + %d snippet keys renamed to validador de blocos" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK pt: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
