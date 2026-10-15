#!/usr/bin/env python3
"""Rename "заверитель"-family -> "блок-валидатор"-family in vanilla/locales/ru.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITION "производитель блоков" stays — it glosses the office.
  * свидетель (court witness) never appears here; do not introduce it.

Compound (per brief, from the locale's OWN attested words where possible):
блок-валидатор (sing) / блок-валидаторы (plur), inflected by case —
block блок (239 word-forms incl. compounds, e.g. explorer_blocks.title)
plus the industry loanword валидатор, UNATTESTED (0 strings) but the
standard crypto term. The alternative built from the attested провер stem
(проверяющие, cf. help.topic_witnesses_text) would read as "checker", not
the office noun, so it is rejected. LOW CONFIDENCE, flagged honestly: case
endings are composed by analogy from the hard-р stem (-а/-ом/-ы/-ов/-ами,
vs the soft-л stem of заверитель) — a native speaker should re-read the
8 mapped forms. Hyphen mirrors de Block-Validator; "Фид от заверителей"
renders as "Фид от блок-валидаторов".

Safety gates (assert before write):
  G1 every target's CURRENT value contains a заверитель-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_ru.py [--apply]
Dry run (asserts only) by default; --apply writes ru.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ru.json")

WITNESS_RE = re.compile(r"заверител", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('Вступление в заверители', 'Вступление в блок-валидаторы'),
 'account.op_witness_update': ('Обновление заверителя', 'Обновление блок-валидатора'),
 'account.sum_witness_create': ('Стал заверителем: %(account)s',
                                'Стал блок-валидатором: %(account)s'),
 'account.sum_witness_update': ('Обновлён заверитель %(account)s',
                                'Обновлён блок-валидатор %(account)s'),
 'asset.witness_fed_note': ('Фид от заверителей: публиковать могут все активные заверители.',
                            'Фид от блок-валидаторов: публиковать могут все активные '
                            'блок-валидаторы.'),
 'explorer.stat_wit': ('Активные заверители', 'Активные блок-валидаторы'),
 'explorer.th_witness': ('Заверитель', 'Блок-валидатор'),
 'explorer.witness_row': ('Заверитель', 'Блок-валидатор'),
 'help.topic_assets-mpa_text': ('Смарткоины, обеспеченные залогом, с ценовыми фидами от '
                                'заверителей.',
                                'Смарткоины, обеспеченные залогом, с ценовыми фидами от '
                                'блок-валидаторов.'),
 'help.topic_glossary_text': ('Имена, используемые в кошельке: объекты (1.x.y), операции, '
                              'заверители, комитет.',
                              'Имена, используемые в кошельке: объекты (1.x.y), операции, '
                              'блок-валидаторы, комитет.'),
 'help.topic_voting_text': ('Голосуйте за заверителей, комитет, грант-предложения — или передайте '
                            'голосование прокси.',
                            'Голосуйте за блок-валидаторов, комитет, грант-предложения — или '
                            'передайте голосование прокси.'),
 'help.topic_witnesses_title': ('Заверители', 'Блок-валидаторы'),
 'menu.d_asset_feed': ('Публикация ценовых фидов как эмитент или заверитель.',
                       'Публикация ценовых фидов как эмитент или блок-валидатор.'),
 'menu.d_voting': ('Заверители, комитет, грант-предложения и прокси.',
                   'Блок-валидаторы, комитет, грант-предложения и прокси.'),
 'news.voting_witnesses_committee_workers': ('Голосование — заверители, комитет, грант-предложения',
                                             'Голосование — блок-валидаторы, комитет, '
                                             'грант-предложения'),
 'seo.desc_voting': ('Голосование за заверителей, членов комитета и грант-предложений BitShares. '
                     'Каждый бюллетень подписывается локально на вашем устройстве.',
                     'Голосование за блок-валидаторов, членов комитета и грант-предложений '
                     'BitShares. Каждый бюллетень подписывается локально на вашем устройстве.'),
 'seo.title_voting': ('Голосование за заверителей — кошелёк BitShares',
                      'Голосование за блок-валидаторов — кошелёк BitShares'),
 'splash.pulse_witnesses': ('Заверители', 'Блок-валидаторы'),
 'vote.ballot_intro': ('Ваш стейк выбирает заверителей и комитет и финансирует грант-предложения — '
                       'все числа и доли ниже читаются из живой цепи.',
                       'Ваш стейк выбирает блок-валидаторов и комитет и финансирует '
                       'грант-предложения — все числа и доли ниже читаются из живой цепи.'),
 'vote.confirm_witness_update_op_21': ('Подтвердите обновление заверителя (op %(op)s)',
                                       'Подтвердите обновление блок-валидатора (op %(op)s)'),
 'vote.empty_list': ('Узел не вернул ни заверителей, ни членов комитета.',
                     'Узел не вернул ни блок-валидаторов, ни членов комитета.'),
 'vote.join_as_witness': ('Стать заверителем', 'Стать блок-валидатором'),
 'vote.no_witness_object_for_this_account_use_join_a': ('Нет объекта заверителя для этого аккаунта '
                                                        '— вместо этого используйте «Стать '
                                                        'заверителем».',
                                                        'Нет объекта блок-валидатора для этого '
                                                        'аккаунта — вместо этого используйте '
                                                        '«Стать блок-валидатором».'),
 'vote.tab_witnesses': ('Заверители (', 'Блок-валидаторы ('),
 'vote.update_witness': ('Обновить заверителя', 'Обновить блок-валидатора'),
 'vote.witness': ('Заверитель', 'Блок-валидатор'),
 'vote.witness_updated': ('Заверитель обновлён', 'Блок-валидатор обновлён')}

SNIPPETS = {'help.topic_assets-mpa_body': [('заверители', 'блок-валидаторы', 1)],
 'help.topic_assets-private_body': [('заверителей', 'блок-валидаторов', 2),
                                    ('заверители', 'блок-валидаторы', 1)],
 'help.topic_blockchain_body': [('заверителями', 'блок-валидаторами', 1),
                                ('заверителей', 'блок-валидаторов', 1),
                                ('Заверители', 'Блок-валидаторы', 1)],
 'help.topic_committee_body': [('заверители', 'блок-валидаторы', 1)],
 'help.topic_dex-shorting_body': [('заверителей', 'блок-валидаторов', 1)],
 'help.topic_glossary_body': [('заверители', 'блок-валидаторы', 1),
                              ('Заверители', 'Блок-валидаторы', 1)],
 'help.topic_settings_body': [('заверителей', 'блок-валидаторов', 1)],
 'help.topic_sitemap_body': [('Заверители', 'Блок-валидаторы', 1)],
 'help.topic_tickets_body': [('заверителей', 'блок-валидаторов', 1)],
 'help.topic_voting_body': [('заверителей', 'блок-валидаторов', 1),
                            ('Заверители', 'Блок-валидаторы', 3)],
 'help.topic_witnesses_body': [('заверителей', 'блок-валидаторов', 1),
                               ('заверители', 'блок-валидаторы', 1),
                               ('Заверители', 'Блок-валидаторы', 1)]}


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
    raw = open(LOC, encoding="utf-8").read()
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
            problems.append("ABORT %s: current value has no witness-family word: %r" % (key, cur))
            continue
        if cur != old:
            problems.append("ABORT %s: current != expected old.\n got: %r\n exp: %r" % (key, cur, old))
            continue
        if sorted(PLACEHOLDER_RE.findall(cur)) != sorted(PLACEHOLDER_RE.findall(new)):
            problems.append("ABORT %s: placeholder multiset would change" % key)
            continue
        if not WITNESS_RE.search(old):
            problems.append("ABORT %s: script old has no witness word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = dig(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WITNESS_RE.search(cur):
            problems.append("ABORT %s: current value has no witness-family word" % key)
            continue
        # Occurrence tally with a leftmost-longest alternation: a bare form
        # (e.g. 증인) is a substring of its own particle/case siblings, so
        # str.count would attribute one occurrence twice. Each occurrence
        # belongs to exactly one (longest) alternative.
        ordered_gate = sorted(reps, key=lambda r: len(r[0]), reverse=True)
        alt_gate = re.compile("|".join(re.escape(o) for o, _n, _c in ordered_gate))
        tally = {}
        for m in alt_gate.finditer(cur):
            tally[m.group(0)] = tally.get(m.group(0), 0) + 1
        for old_snip, new_snip, count in reps:
            if not WITNESS_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no witness word (script bug): %r" % (key, old_snip))
                continue
            if tally.get(old_snip, 0) != count:
                problems.append("ABORT %s: snippet occurs %d != %d: %r" % (key, tally.get(old_snip, 0), count, old_snip))
            if sorted(PLACEHOLDER_RE.findall(old_snip)) != sorted(PLACEHOLDER_RE.findall(new_snip)):
                problems.append("ABORT %s: snippet placeholder change: %r" % (key, old_snip))

    if "help.topic_sitemap_body" in SNIPPETS:
        sm = before_vals["help.topic_sitemap_body"]
        if sm.count("#/explorer/witnesses") != 1:
            problems.append("ABORT sitemap: expected exactly one #/explorer/witnesses link")

    if problems:
        print("FAIL (%d):" % len(problems))
        print("\n".join(problems))
        return 1

    for key, (old, new) in FULL.items():
        set_dig(d, key, new)
    for key, reps in SNIPPETS.items():
        cur = dig(d, key)
        # Single leftmost-longest pass: sequential replaces would miscount,
        # because a bare form (e.g. 증인) is a substring of its own
        # particle/case siblings. Alternation ordered longest-first replaces
        # each occurrence exactly once; the gate above already proved the
        # per-form counts on the pristine string.
        ordered = sorted(reps, key=lambda r: len(r[0]), reverse=True)
        alt = re.compile("|".join(re.escape(o) for o, _n, _c in ordered))
        mapping = {o: n for o, n, _c in ordered}
        cur, nsub = alt.subn(lambda m: mapping[m.group(0)], cur)
        assert nsub == sum(c for _o, _n, c in reps), key
        if key == "help.topic_sitemap_body":
            assert HREF_RE.findall(before_vals[key]) == HREF_RE.findall(cur), "sitemap href drift"
            assert cur.count("#/explorer/witnesses") == 1, "sitemap link drift"
        set_dig(d, key, cur)

    for key in list(FULL) + list(SNIPPETS):
        v = dig(d, key)
        if WITNESS_RE.search(v):
            print("FAIL: %s still carries a witness-family word: %r" % (key, v[:160]))
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
        open(LOC, "w", encoding="utf-8").write(out)
        print("OK ru: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ru: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
