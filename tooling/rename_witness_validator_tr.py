#!/usr/bin/env python3
"""Rename "tanık"-family -> "blok doğrulayıcı"-family in vanilla/locales/tr.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITION "blok üreticisi/üreticiler" stays — it glosses the office.
  * şahit (court witness, 0 strings) is never introduced.

Compound (per brief, from the locale's OWN attested words):
blok doğrulayıcı (sing) / blok doğrulayıcılar (plur) — block blok
(84 keys) + validate doğrula (30 keys, e.g. gateway.validate_btn,
debit.verify_fills_suffix) + agent -yıcı (productive: üretici 21 keys).
Spaced compound, mirroring "blok üreticisi". Suffixes carry over onto the
-lar stem (Tanıklar->Blok doğrulayıcılar, -lara, -ların, -larına,
-lardan, -ları); the k->ğ mutated dative/accusative takes buffer-y inserts
(Tanığa->Blok doğrulayıcıya, Tanığı->Blok doğrulayıcıyı,
tanığa->blok doğrulayıcıya). "Tanık olarak katıl" action phrasing and the
quoted button echo in no_witness_object stay in sync by construction.

Safety gates (assert before write):
  G1 every target's CURRENT value contains a tanık-family word, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_tr.py [--apply]
Dry run (asserts only) by default; --apply writes tr.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "tr.json")

WITNESS_RE = re.compile(r"tan[ıi][kğ]", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('Tanığa katılım', 'Blok doğrulayıcıya katılım'),
 'account.op_witness_update': ('Tanık güncelleme', 'Blok doğrulayıcı güncelleme'),
 'account.sum_witness_create': ('Tanık oldu: %(account)s', 'Blok doğrulayıcı oldu: %(account)s'),
 'account.sum_witness_update': ('Tanık %(account)s güncellendi',
                                'Blok doğrulayıcı %(account)s güncellendi'),
 'asset.witness_fed_note': ('Tanık beslemesi: etkin tüm tanıklar yayınlayabilir.',
                            'Blok doğrulayıcı beslemesi: etkin tüm blok doğrulayıcılar '
                            'yayınlayabilir.'),
 'explorer.stat_wit': ('Aktif tanıklar', 'Aktif blok doğrulayıcılar'),
 'explorer.th_witness': ('Tanık', 'Blok doğrulayıcı'),
 'explorer.witness_row': ('Tanık', 'Blok doğrulayıcı'),
 'help.topic_assets-mpa_text': ('Tanıklardan fiyat beslemeli, teminatlı akıllı paralar.',
                                'Blok doğrulayıcılardan fiyat beslemeli, teminatlı akıllı '
                                'paralar.'),
 'help.topic_glossary_text': ('Bu cüzdanda kullanılan adlar: nesneler (1.x.y), işlemler, tanıklar, '
                              'komite.',
                              'Bu cüzdanda kullanılan adlar: nesneler (1.x.y), işlemler, blok '
                              'doğrulayıcılar, komite.'),
 'help.topic_voting_text': ('Tanıklara, komiteye ve hibe önerilerine oy verin — ya da vekile '
                            'devredin.',
                            'Blok doğrulayıcılara, komiteye ve hibe önerilerine oy verin — ya da '
                            'vekile devredin.'),
 'help.topic_witnesses_title': ('Tanıklar', 'Blok doğrulayıcılar'),
 'menu.d_asset_feed': ('İhraççı veya tanık olarak fiyat beslemesi yayınlayın.',
                       'İhraççı veya blok doğrulayıcı olarak fiyat beslemesi yayınlayın.'),
 'menu.d_voting': ('Tanıklar, komite, hibe önerileri ve vekiller.',
                   'Blok doğrulayıcılar, komite, hibe önerileri ve vekiller.'),
 'news.voting_witnesses_committee_workers': ('Oylama — tanıklar, komite, hibe önerileri',
                                             'Oylama — blok doğrulayıcılar, komite, hibe '
                                             'önerileri'),
 'seo.desc_voting': ('BitShares tanıklarına, komite üyelerine ve hibe önerilerine oy verin. Her oy '
                     'pusulası cihazınızda yerel olarak imzalanır.',
                     'BitShares blok doğrulayıcılarına, komite üyelerine ve hibe önerilerine oy '
                     'verin. Her oy pusulası cihazınızda yerel olarak imzalanır.'),
 'seo.title_voting': ('Tanıklara oy ver — BitShares Cüzdanı',
                      'Blok doğrulayıcılara oy ver — BitShares Cüzdanı'),
 'splash.pulse_witnesses': ('Tanıklar', 'Blok doğrulayıcılar'),
 'vote.ballot_intro': ('Hakedişiniz tanıkları ve komiteyi seçer, hibe önerilerinin bütçesini '
                       'oluşturur — aşağıdaki tüm sayılar ve paylar canlı zincir okumalarıdır.',
                       'Hakedişiniz blok doğrulayıcıları ve komiteyi seçer, hibe önerilerinin '
                       'bütçesini oluşturur — aşağıdaki tüm sayılar ve paylar canlı zincir '
                       'okumalarıdır.'),
 'vote.confirm_witness_update_op_21': ('Tanık güncellemeyi onayla (op %(op)s)',
                                       'Blok doğrulayıcı güncellemeyi onayla (op %(op)s)'),
 'vote.empty_list': ('Düğüm tanık veya komite üyesi döndürmedi.',
                     'Düğüm blok doğrulayıcı veya komite üyesi döndürmedi.'),
 'vote.join_as_witness': ('Tanık olarak katıl', 'Blok doğrulayıcı olarak katıl'),
 'vote.no_witness_object_for_this_account_use_join_a': ('Bu hesap için tanık nesnesi yok — bunun '
                                                        "yerine Tanık olarak katıl'ı kullanın.",
                                                        'Bu hesap için blok doğrulayıcı nesnesi '
                                                        'yok — bunun yerine Blok doğrulayıcı '
                                                        "olarak katıl'ı kullanın."),
 'vote.tab_witnesses': ('Tanıklar (', 'Blok doğrulayıcılar ('),
 'vote.update_witness': ('Tanığı güncelle', 'Blok doğrulayıcıyı güncelle'),
 'vote.witness': ('Tanık', 'Blok doğrulayıcı'),
 'vote.witness_updated': ('Tanık güncellendi', 'Blok doğrulayıcı güncellendi')}

SNIPPETS = {'help.topic_assets-mpa_body': [('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_assets-private_body': [('Tanık', 'Blok doğrulayıcı', 1),
                                    ('tanık', 'blok doğrulayıcı', 2)],
 'help.topic_blockchain_body': [('Tanık', 'Blok doğrulayıcı', 1), ('tanık', 'blok doğrulayıcı', 2)],
 'help.topic_committee_body': [('Tanık', 'Blok doğrulayıcı', 1)],
 'help.topic_dex-shorting_body': [('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_glossary_body': [('Tanık', 'Blok doğrulayıcı', 1), ('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_settings_body': [('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_sitemap_body': [('Tanık', 'Blok doğrulayıcı', 1)],
 'help.topic_tickets_body': [('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_voting_body': [('Tanık', 'Blok doğrulayıcı', 3), ('tanık', 'blok doğrulayıcı', 1)],
 'help.topic_witnesses_body': [('tanığa', 'blok doğrulayıcıya', 1),
                               ('Tanık', 'Blok doğrulayıcı', 2)]}


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
        print("OK tr: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK tr: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
