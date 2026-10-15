#!/usr/bin/env python3
"""Rename "ウィットネス" -> "ブロック検証者" in vanilla/locales/ja.json.

Scope: ONLY the 38 block-producer keys (27 short + 11 long bodies).
Keys unchanged. Excluded by design (aborts if touched, never rewritten):
  * placeholders — %(account)s / %(op)s stay byte-identical.
  * route targets — "#/explorer/witnesses" stays (router path, code).
  * key names (*witness*, topic_witnesses_*) stay (code).
  * the DEFINITION "ブロック生成者" (block producer) in witnesses/proxy
    bodies stays — it glosses the office, not the term.
  * 証人 (court witness) never appears in these keys; do not introduce it.

Compound (per brief, from the locale's OWN attested words): ブロック検証者 —
block ブロック (89 keys, e.g. explorer_blocks.title) + validate 検証
(26 keys, e.g. gateway.validate_btn) + agent 者 (発行者 46 keys).
The katakana loanword バリデータ is unattested (0 strings) and is NOT used.
Hyphen "ウィットネスフィード" renders as ブロック検証者フィード (mirrored
concatenation); "になりました" becoming-verb and "として参加" action phrasing
keep locale grammar; tab/column headers stay short but explicit.

Safety gates (assert before write):
  G1 every target's CURRENT value contains ウィットネス, else abort.
  G2 every FULL target's current value EQUALS the expected old string.
  G3 every snippet occurs exactly its expected count.
  G4 placeholder multiset %(..)s unchanged per key; sitemap hrefs unchanged.
  G5 key set + _meta deep-equal before/after; non-target values untouched.
  G6 json.dumps(indent=2, ensure_ascii=False)+"\\n" formatting.

Usage: python3 tooling/rename_witness_validator_ja.py [--apply]
Dry run (asserts only) by default; --apply writes ja.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, "..", "vanilla", "locales", "ja.json")

WITNESS_RE = re.compile(r"ウィットネス")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {'account.op_witness_join': ('ウィットネス参加', 'ブロック検証者参加'),
 'account.op_witness_update': ('ウィットネス更新', 'ブロック検証者更新'),
 'account.sum_witness_create': ('ウィットネスになりました: %(account)s', 'ブロック検証者になりました: %(account)s'),
 'account.sum_witness_update': ('ウィットネス %(account)s を更新しました', 'ブロック検証者 %(account)s を更新しました'),
 'asset.witness_fed_note': ('ウィットネスフィード：有効なすべてのウィットネスが公開できます。',
                            'ブロック検証者フィード：有効なすべてのブロック検証者が公開できます。'),
 'explorer.stat_wit': ('有効なウィットネス', '有効なブロック検証者'),
 'explorer.th_witness': ('ウィットネス', 'ブロック検証者'),
 'explorer.witness_row': ('ウィットネス', 'ブロック検証者'),
 'help.topic_assets-mpa_text': ('ウィットネスの価格フィードに裏付けられた担保付きスマートコイン。',
                                'ブロック検証者の価格フィードに裏付けられた担保付きスマートコイン。'),
 'help.topic_glossary_text': ('このウォレットで使う名称: オブジェクト（1.x.y）、オペレーション、ウィットネス、委員会。',
                              'このウォレットで使う名称: オブジェクト（1.x.y）、オペレーション、ブロック検証者、委員会。'),
 'help.topic_voting_text': ('ウィットネス、委員会、グラント提案に投票します — プロキシに委任することもできます。',
                            'ブロック検証者、委員会、グラント提案に投票します — プロキシに委任することもできます。'),
 'help.topic_witnesses_title': ('ウィットネス', 'ブロック検証者'),
 'menu.d_asset_feed': ('発行者またはウィットネスとして価格フィードを発行。', '発行者またはブロック検証者として価格フィードを発行。'),
 'menu.d_voting': ('ウィットネス、委員会、グラント提案、プロキシ。', 'ブロック検証者、委員会、グラント提案、プロキシ。'),
 'news.voting_witnesses_committee_workers': ('投票 — ウィットネス、委員会、グラント提案', '投票 — ブロック検証者、委員会、グラント提案'),
 'seo.desc_voting': ('BitShares のウィットネス、委員会メンバー、グラント提案に投票します。すべての投票はデバイス上でローカルに署名されます。',
                     'BitShares のブロック検証者、委員会メンバー、グラント提案に投票します。すべての投票はデバイス上でローカルに署名されます。'),
 'seo.title_voting': ('ウィットネス投票 — BitShares ウォレット', 'ブロック検証者投票 — BitShares ウォレット'),
 'splash.pulse_witnesses': ('ウィットネス', 'ブロック検証者'),
 'vote.ballot_intro': ('あなたのステークがウィットネスと委員会を選び、グラント提案を支えます — 以下の数値と比率はすべてチェーンからのライブ読み取りです。',
                       'あなたのステークがブロック検証者と委員会を選び、グラント提案を支えます — 以下の数値と比率はすべてチェーンからのライブ読み取りです。'),
 'vote.confirm_witness_update_op_21': ('ウィットネス更新を確認（op %(op)s）', 'ブロック検証者更新を確認（op %(op)s）'),
 'vote.empty_list': ('ノードはウィットネスまたは委員会メンバーを返しませんでした。', 'ノードはブロック検証者または委員会メンバーを返しませんでした。'),
 'vote.join_as_witness': ('ウィットネスとして参加', 'ブロック検証者として参加'),
 'vote.no_witness_object_for_this_account_use_join_a': ('このアカウントにはウィットネスオブジェクトがありません — '
                                                        '代わりにウィットネス参加を使用してください。',
                                                        'このアカウントにはブロック検証者オブジェクトがありません — '
                                                        '代わりにブロック検証者参加を使用してください。'),
 'vote.tab_witnesses': ('ウィットネス（', 'ブロック検証者（'),
 'vote.update_witness': ('ウィットネスを更新', 'ブロック検証者を更新'),
 'vote.witness': ('ウィットネス', 'ブロック検証者'),
 'vote.witness_updated': ('ウィットネスを更新しました', 'ブロック検証者を更新しました')}

SNIPPETS = {'help.topic_assets-mpa_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_assets-private_body': [('ウィットネス', 'ブロック検証者', 3)],
 'help.topic_blockchain_body': [('ウィットネス', 'ブロック検証者', 3)],
 'help.topic_committee_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_dex-shorting_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_glossary_body': [('ウィットネス', 'ブロック検証者', 2)],
 'help.topic_settings_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_sitemap_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_tickets_body': [('ウィットネス', 'ブロック検証者', 1)],
 'help.topic_voting_body': [('ウィットネス', 'ブロック検証者', 4)],
 'help.topic_witnesses_body': [('ウィットネス', 'ブロック検証者', 3)]}


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
        print("OK ja: %d full + %d snippet keys renamed" % (len(FULL), len(SNIPPETS)))
    else:
        print("OK ja: dry run green (%d full + %d snippet keys would change)" % (len(FULL), len(SNIPPETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
