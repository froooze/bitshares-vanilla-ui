#!/usr/bin/env python3
"""Rename treasury "worker" -> "proposta de grant" in pt.json (Brazilian).

Scope: ONLY values carrying the treasury-proposal sense (36 keys). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.
  * register stays Brazilian informal (você, conta vitalícia); ZERO
    apostrophes (pt.json ships none — gate below refuses any).

Compound (per brief, from the dict's OWN attested words): sing "proposta de
grant", plur "propostas de grant" — "proposta" (proposal.create_proposal
"Criar proposta") + loanword "grant" (no Portuguese grant noun is attested
anywhere in pt.json; thing-first order mirrors the ticket wave's "stake de
voto"). Pay stays the attested "pagamento", budget the attested "Orçamento",
refund "reembolso", recipients "beneficiários".

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip; G6 no
apostrophe introduced.

Usage: python3 tooling/rename_worker_grant_pt.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "pt.json")

WORKER_RE = re.compile(r"worker|trabalhador(?:es)?", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "Cria\u00e7\u00e3o de worker",
        "Cria\u00e7\u00e3o de proposta de grant",
    ),
    "account.sum_worker_create": (
        "Worker \"%(name)s\" criado",
        "Proposta de grant \"%(name)s\" criada",
    ),
    "createworker.confirm_worker_op_34": (
        "Confirmar worker (op %(op)s)",
        "Confirmar proposta de grant (op %(op)s)",
    ),
    "createworker.could_not_preview_the_worker": (
        "N\u00e3o foi poss\u00edvel visualizar o worker.",
        "N\u00e3o foi poss\u00edvel visualizar a proposta de grant.",
    ),
    "createworker.create_worker": (
        "Criar Worker",
        "Criar proposta de grant",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "Escreva um worker (op %(op)s). A pr\u00e9via \u00e9 ao vivo; a revis\u00e3o cota a taxa ao vivo, e ent\u00e3o Assinar e enviar transmite a op %(op)s diretamente \u2014 workers s\u00e3o criados por op direta, n\u00e3o por proposta.",
        "Escreva uma proposta de grant (op %(op)s). A pr\u00e9via \u00e9 ao vivo; a revis\u00e3o cota a taxa ao vivo, e ent\u00e3o Assinar e enviar transmite a op %(op)s diretamente \u2014 propostas de grant s\u00e3o criadas por op direta, n\u00e3o por proposta.",
    ),
    "createworker.enter_a_worker_name": (
        "Digite um nome de worker.",
        "Digite um nome de proposta de grant.",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "O propriet\u00e1rio paga a taxa e recebe o pagamento do worker \u2014 use uma conta vital\u00edcia que voc\u00ea controle.",
        "O propriet\u00e1rio paga a taxa e recebe o pagamento da proposta de grant \u2014 use uma conta vital\u00edcia que voc\u00ea controle.",
    ),
    "createworker.preview_worker": (
        "Visualizar worker",
        "Visualizar proposta de grant",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "Publicar um worker exige conta vital\u00edcia \u2014 contas b\u00e1sicas n\u00e3o podem pagar esta taxa. O propriet\u00e1rio abaixo j\u00e1 deve ter upgrade.",
        "Publicar uma proposta de grant exige conta vital\u00edcia \u2014 contas b\u00e1sicas n\u00e3o podem pagar esta taxa. O propriet\u00e1rio abaixo j\u00e1 deve ter upgrade.",
    ),
    "createworker.reading_existing_workers": (
        "Lendo workers existentes\u2026",
        "Lendo propostas de grant existentes\u2026",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "Backend de worker ausente: falha ao carregar js/account.js ou js/format.js.",
        "Backend de proposta de grant ausente: falha ao carregar js/account.js ou js/format.js.",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "Backend de worker ausente: falha ao carregar js/asset-ops.js.",
        "Backend de proposta de grant ausente: falha ao carregar js/asset-ops.js.",
    ),
    "createworker.worker_name": (
        "Nome do worker ",
        "Nome da proposta de grant ",
    ),
    "createworker.worker_preview_op_34": (
        "Pr\u00e9via do worker (op %(op)s)",
        "Pr\u00e9via da proposta de grant (op %(op)s)",
    ),
    "help.topic_workers_title": (
        "Workers",
        "Propostas de grant",
    ),
    "help.topic_voting_text": (
        "Vote em testemunhas, comit\u00ea e workers \u2014 ou entregue seu voto a um proxy.",
        "Vote em testemunhas, comit\u00ea e propostas de grant \u2014 ou entregue seu voto a um proxy.",
    ),
    "menu.d_voting": (
        "Testemunhas, comit\u00ea, workers e proxies.",
        "Testemunhas, comit\u00ea, propostas de grant e proxies.",
    ),
    "menu.p_worker": (
        "Criar Worker",
        "Criar proposta de grant",
    ),
    "news.voting_witnesses_committee_workers": (
        "Vota\u00e7\u00e3o \u2014 testemunhas, comit\u00ea, workers",
        "Vota\u00e7\u00e3o \u2014 testemunhas, comit\u00ea, propostas de grant",
    ),
    "seo.desc_voting": (
        "Vote em testemunhas, membros do comit\u00ea e workers da BitShares. Cada voto \u00e9 assinado localmente no seu dispositivo.",
        "Vote em testemunhas, membros do comit\u00ea e propostas de grant da BitShares. Cada voto \u00e9 assinado localmente no seu dispositivo.",
    ),
    "vote.ballot_intro": (
        "Seu stake elege testemunhas e comit\u00ea e financia workers \u2014 todas as contagens e cotas abaixo s\u00e3o leituras ao vivo da chain.",
        "Seu stake elege testemunhas e comit\u00ea e financia propostas de grant \u2014 todas as contagens e cotas abaixo s\u00e3o leituras ao vivo da chain.",
    ),
    "vote.empty_hint": (
        " Entradas aparecem quando a chain as cont\u00e9m \u2014 workers s\u00e3o propostos em #/create-worker.",
        " Entradas aparecem quando a chain as cont\u00e9m \u2014 propostas de grant s\u00e3o propostas em #/create-worker.",
    ),
    "vote.funding_unavailable_prefix": (
        "Financiamento de workers indispon\u00edvel (",
        "Financiamento de propostas de grant indispon\u00edvel (",
    ),
    "vote.hide_legacy_label": (
        " Ocultar propostas legadas (sempre ativo \u2014 workers expirados s\u00e3o exclu\u00eddos na busca)",
        " Ocultar propostas legadas (sempre ativo \u2014 propostas de grant expiradas s\u00e3o exclu\u00eddas na busca)",
    ),
    "vote.hide_legacy_title": (
        "Listas de workers v\u00eam de get_all_workers(false); linhas expiradas nunca chegam.",
        "Listas de propostas de grant v\u00eam de get_all_workers(false); linhas expiradas nunca chegam.",
    ),
    "vote.no_workers": (
        "Nenhum worker encontrado. Testnets costumam n\u00e3o ter nenhum \u2014 isto \u00e9 v\u00e1lido, n\u00e3o \u00e9 erro.",
        "Nenhuma proposta de grant encontrada. Testnets costumam n\u00e3o ter nenhuma \u2014 isto \u00e9 v\u00e1lido, n\u00e3o \u00e9 erro.",
    ),
    "vote.tab_workers": (
        "Workers (",
        "Propostas de grant (",
    ),
    "vote.worker_budget": (
        "Or\u00e7amento de workers: \u2014",
        "Or\u00e7amento de propostas de grant: \u2014",
    ),
    "vote.worker_budget_loading": (
        "Or\u00e7amento de workers: carregando\u2026",
        "Or\u00e7amento de propostas de grant: carregando\u2026",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        (
            "workers entregam projetos pagos",
            "benefici\u00e1rios de grant entregam projetos pagos",
            1,
        ),
    ],
    "help.topic_sitemap_body": [
        (
            "- [Criar Worker](#/create-worker)",
            "- [Criar proposta de grant](#/create-worker)",
            1,
        ),
    ],
    "help.topic_tickets_body": [
        (
            "votos de testemunhas, comit\u00ea e workers via lista de vota\u00e7\u00e3o normal",
            "votos de testemunhas, comit\u00ea e propostas de grant via lista de vota\u00e7\u00e3o normal",
            1,
        ),
    ],
    "help.topic_vesting_body": [
        (
            "pagamento de workers, recompensas de indica\u00e7\u00e3o",
            "pagamento de propostas de grant, recompensas de indica\u00e7\u00e3o",
            1,
        ),
    ],
    "help.topic_voting_body": [
        (
            "e quais projetos de workers recebem pagamento.",
            "e quais projetos de propostas de grant recebem pagamento.",
            1,
        ),
        (
            "ou workers. Voc\u00ea pode remover o proxy",
            "ou propostas de grant. Voc\u00ea pode remover o proxy",
            1,
        ),
        (
            "# Workers e o or\u00e7amento\nWorkers s\u00e3o propostas pagas que sobem de propostas a ativas quando superam em votos o worker de reembolso, pagas de um or\u00e7amento di\u00e1rio fixo por ordem de chegada conforme o ranking. Detalhes completos est\u00e3o no artigo Workers.",
            "# Propostas de grant e o or\u00e7amento\nPropostas de grant s\u00e3o propostas pagas que sobem de propostas a ativas quando superam em votos a proposta de grant de reembolso, pagas de um or\u00e7amento di\u00e1rio fixo por ordem de chegada conforme o ranking. Detalhes completos est\u00e3o no artigo Propostas de grant.",
            1,
        ),
    ],
    "help.topic_workers_body": [
        (
            "Workers s\u00e3o propostas para fazer algo \u00fatil",
            "Propostas de grant s\u00e3o propostas para fazer algo \u00fatil",
            1,
        ),
        (
            "Workers propostos est\u00e3o juntando votos. Quando uma proposta supera em votos o worker de reembolso, ela vira ativa",
            "Propostas de grant propostas est\u00e3o juntando votos. Quando uma proposta supera em votos a proposta de grant de reembolso, ela vira ativa",
            1,
        ),
        (
            "Todos os workers dividem um or\u00e7amento di\u00e1rio fixo",
            "Todas as propostas de grant dividem um or\u00e7amento di\u00e1rio fixo",
            1,
        ),
        (
            "se workers de ranking maior j\u00e1 consumiram os fundos do dia",
            "se propostas de grant de ranking maior j\u00e1 consumiram os fundos do dia",
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
    raw = open(P, encoding="utf-8").read()
    d = json.loads(raw)
    if json.dumps(d, indent=2, ensure_ascii=False) + "\n" != raw:
        print("FAIL: pt.json does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
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
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WORKER_RE.search(old):
            problems.append("ABORT %s: script's old string has no worker word (script bug)" % key)
            continue
        if "'" in new or "\u2019" in new:
            problems.append("ABORT %s: new string carries an apostrophe (pt ships none)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            got = cur.count(old_snip)
            if got != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, got, count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))
            if "'" in new_snip or "\u2019" in new_snip:
                problems.append("ABORT %s: snippet carries an apostrophe (pt ships none): %r" % (key, new_snip))

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

    after_vals = flatten(d)
    if "get_all_workers" not in after_vals["vote.hide_legacy_title"]:
        print("FAIL: get_all_workers token lost")
        return 1
    for k in ("createworker.worker_backend_missing_js_account_js_or_js_fo",
              "createworker.worker_backend_missing_js_asset_ops_js_failed"):
        if "js/" not in after_vals[k]:
            print("FAIL: file path lost in %s" % k)
            return 1
    for k in ("help.topic_sitemap_body", "vote.empty_hint"):
        if "#/create-worker" not in after_vals[k]:
            print("FAIL: route hash lost in %s" % k)
            return 1

    if set(after_vals) != before_keys:
        print("FAIL: key set drift")
        return 1
    if d.get("_meta") != before_meta:
        print("FAIL: _meta moved")
        return 1
    for k, v in before_vals.items():
        if k not in FULL and k not in SNIPPETS and after_vals[k] != v:
            print("FAIL: untouched key moved: %s" % k)
            return 1

    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    if apply:
        open(P, "w", encoding="utf-8").write(out)
        print("OK pt: %d full + %d snippet keys renamed to proposta(s) de grant" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK pt: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
