#!/usr/bin/env python3
"""Rename treasury worker -> grant proposal in vanilla/locales/ja.json.

Scope: ONLY values carrying the treasury-proposal sense (30 FULL + 6 snippet bodies). Keys unchanged.
Excluded by design (aborts if touched, reported, never rewritten):
  * placeholders (%(name)s, %(op)s stay byte-identical; code-bound).
  * code identifiers (get_all_workers in vote.hide_legacy_title stays).
  * route hashes (#/create-worker in sitemap + empty_hint stays).
  * file paths (js/ in backend-missing strings stays).
  * chrome with no worker word (daily_pay, work dates, pay_destination ...),
    help.topic_workers_text and menu.d_worker — untouched.

Compound (per brief, from dict's OWN attested words where possible): グラント提案 / グラント受益者 (recipients).
Pay keeps attested pay word (never transliterated pay); budget/funding keep attested words;
recipients (PEOPLE) use beneficiary word attested in referrals body, not proposals.

Safety gates: G1 current has worker-family word; G2 current == expected old
(FULL) or snippet counts (SNIPPETS); G3 placeholders/hrefs/identifiers kept;
G4 key set + _meta + untouched values; G5 formatting round-trip.

Usage: python3 tooling/rename_worker_grant_ja.py [--apply]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "vanilla", "locales", "ja.json")

WORKER_RE = re.compile(r"ワーカー")
PLACEHOLDER_RE = re.compile(r"%\([^)]*\)s")
HREF_RE = re.compile(r"\]\(#[^)]*\)")

FULL = {
    "account.op_worker_create": (
        "ワーカー作成",
        "グラント提案作成",
    ),
    "account.sum_worker_create": (
        "ワーカー「%(name)s」を作成しました",
        "グラント提案「%(name)s」を作成しました",
    ),
    "createworker.confirm_worker_op_34": (
        "ワーカーを確認（op %(op)s）",
        "グラント提案を確認（op %(op)s）",
    ),
    "createworker.could_not_preview_the_worker": (
        "ワーカーをプレビューできませんでした。",
        "グラント提案をプレビューできませんでした。",
    ),
    "createworker.create_worker": (
        "ワーカー作成",
        "グラント提案作成",
    ),
    "createworker.draft_a_worker_op_34_preview_is_live_review_q": (
        "ワーカーを作成します（op %(op)s）。プレビューはライブ値で、確認画面には実際の手数料が表示されます。その後「署名して送信」で op %(op)s を直接ブロードキャストします — ワーカーは提案ではなく直接の操作で作成されます。",
        "グラント提案を作成します（op %(op)s）。プレビューはライブ値で、確認画面には実際の手数料が表示されます。その後「署名して送信」で op %(op)s を直接ブロードキャストします — グラント提案は提案ではなく直接の操作で作成されます。",
    ),
    "createworker.enter_a_worker_name": (
        "ワーカー名を入力してください。",
        "グラント提案名を入力してください。",
    ),
    "createworker.owner_pays_the_fee_and_receives_the_": (
        "所有者が手数料を支払い、ワーカー報酬を受け取ります — ご自身が管理するライフタイムメンバーアカウントを使用してください。",
        "所有者が手数料を支払い、グラント提案報酬を受け取ります — ご自身が管理するライフタイムメンバーアカウントを使用してください。",
    ),
    "createworker.preview_worker": (
        "ワーカーをプレビュー",
        "グラント提案をプレビュー",
    ),
    "createworker.publishing_a_worker_requires_a_lifeti": (
        "ワーカーの公開にはライフタイムメンバーアカウントが必要です — ベーシックアカウントではこの手数料を支払えません。下の所有者は既にアップグレード済みである必要があります。",
        "グラント提案の公開にはライフタイムメンバーアカウントが必要です — ベーシックアカウントではこの手数料を支払えません。下の所有者は既にアップグレード済みである必要があります。",
    ),
    "createworker.reading_existing_workers": (
        "既存のワーカーを読み取り中…",
        "既存のグラント提案を読み取り中…",
    ),
    "createworker.worker_backend_missing_js_account_js_or_js_fo": (
        "ワーカーバックエンドが見つかりません：js/account.js または js/format.js の読み込みに失敗しました。",
        "グラント提案バックエンドが見つかりません：js/account.js または js/format.js の読み込みに失敗しました。",
    ),
    "createworker.worker_backend_missing_js_asset_ops_js_failed": (
        "ワーカーバックエンドが見つかりません：js/asset-ops.js の読み込みに失敗しました。",
        "グラント提案バックエンドが見つかりません：js/asset-ops.js の読み込みに失敗しました。",
    ),
    "createworker.worker_name": (
        "ワーカー名 ",
        "グラント提案名 ",
    ),
    "createworker.worker_preview_op_34": (
        "ワーカーのプレビュー（op %(op)s）",
        "グラント提案のプレビュー（op %(op)s）",
    ),
    "help.topic_workers_title": (
        "ワーカー",
        "グラント提案",
    ),
    "help.topic_voting_text": (
        "ウィットネス、委員会、ワーカーに投票します — プロキシに委任することもできます。",
        "ウィットネス、委員会、グラント提案に投票します — プロキシに委任することもできます。",
    ),
    "menu.d_voting": (
        "ウィットネス、委員会、ワーカー、プロキシ。",
        "ウィットネス、委員会、グラント提案、プロキシ。",
    ),
    "menu.p_worker": (
        "ワーカー作成",
        "グラント提案作成",
    ),
    "news.voting_witnesses_committee_workers": (
        "投票 — ウィットネス、委員会、ワーカー",
        "投票 — ウィットネス、委員会、グラント提案",
    ),
    "seo.desc_voting": (
        "BitShares のウィットネス、委員会メンバー、ワーカーに投票します。すべての投票はデバイス上でローカルに署名されます。",
        "BitShares のウィットネス、委員会メンバー、グラント提案に投票します。すべての投票はデバイス上でローカルに署名されます。",
    ),
    "vote.ballot_intro": (
        "あなたのステークがウィットネスと委員会を選び、ワーカーを支えます — 以下の数値と比率はすべてチェーンからのライブ読み取りです。",
        "あなたのステークがウィットネスと委員会を選び、グラント提案を支えます — 以下の数値と比率はすべてチェーンからのライブ読み取りです。",
    ),
    "vote.empty_hint": (
        " チェーンに記録があると項目が表示されます — ワーカーは #/create-worker から提案されます。",
        " チェーンに記録があると項目が表示されます — グラント提案は #/create-worker から提案されます。",
    ),
    "vote.funding_unavailable_prefix": (
        "ワーカー資金を利用できません（",
        "グラント提案資金を利用できません（",
    ),
    "vote.hide_legacy_label": (
        " 旧来の提案を非表示（常に有効 — 期限切れワーカーは取得時に除外されます）",
        " 旧来の提案を非表示（常に有効 — 期限切れグラント提案は取得時に除外されます）",
    ),
    "vote.hide_legacy_title": (
        "ワーカーリストは get_all_workers(false) から取得します。期限切れ行は到達しません。",
        "グラント提案リストは get_all_workers(false) から取得します。期限切れ行は到達しません。",
    ),
    "vote.no_workers": (
        "ワーカーが見つかりませんでした。テストネットでは無いことが多く、これは正常でありエラーではありません。",
        "グラント提案が見つかりませんでした。テストネットでは無いことが多く、これは正常でありエラーではありません。",
    ),
    "vote.tab_workers": (
        "ワーカー（",
        "グラント提案（",
    ),
    "vote.worker_budget": (
        "ワーカー予算: —",
        "グラント提案予算: —",
    ),
    "vote.worker_budget_loading": (
        "ワーカー予算: 読み込み中…",
        "グラント提案予算: 読み込み中…",
    ),
}

SNIPPETS = {
    "help.topic_glossary_body": [
        ("ワーカーは有償案件を届けます", "グラント受益者は有償案件を届けます", 1,),
    ],
    "help.topic_sitemap_body": [
        ("ワーカー", "グラント提案", 1,),
    ],
    "help.topic_tickets_body": [
        ("ワーカー", "グラント提案", 1,),
    ],
    "help.topic_vesting_body": [
        ("ワーカー", "グラント提案", 1,),
    ],
    "help.topic_voting_body": [
        ("ワーカー", "グラント提案", 6,),
    ],
    "help.topic_workers_body": [
        ("ワーカー", "グラント提案", 5,),
    ],
}


def digd(d, key):
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
        print(f"FAIL: {P} does not round-trip indent=2/ensure_ascii=False + \\n")
        return 1
    before_keys = set(flatten(d))
    before_meta = json.loads(json.dumps(d.get("_meta")))
    before_vals = flatten(d)

    problems = []

    for key, (old, new) in FULL.items():
        try:
            cur = digd(d, key)
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
            problems.append("ABORT %s: script old has no worker word (script bug)" % key)
            continue

    for key, reps in SNIPPETS.items():
        try:
            cur = digd(d, key)
        except KeyError:
            problems.append("missing key %s" % key)
            continue
        if not isinstance(cur, str) or not WORKER_RE.search(cur):
            problems.append("ABORT %s: current value has no worker-family word" % key)
            continue
        for old_snip, new_snip, count in reps:
            if not WORKER_RE.search(old_snip) and key != "help.topic_glossary_body":
                # glossary old_snip contains worker word by definition; allow generic check
                pass
            # For glossary, old_snip must contain worker word; enforce
            if key == "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
                continue
            if key != "help.topic_glossary_body" and not WORKER_RE.search(old_snip):
                problems.append("ABORT %s: snippet has no worker word (script bug): %r" % (key, old_snip))
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
        cur = digd(d, key)
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
        print(f"OK {P}: renamed")
    else:
        print(f"OK {P}: dry run green")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
