#!/usr/bin/env python3
"""Rename Same-T -> flash-loan wording in ja/ko/zh (CJK pass).

Mirrors the es/de/fr/it/pt pass (20 keys per locale). samet.* KEYS untouched,
only values change. Preserves key order, json.dumps(indent=2,
ensure_ascii=False) + trailing newline. Placeholders, 1.2.x, URLs, op
numbers, asset symbols, link hashes untouched.

Changed keys per locale (20):
  account.op_samet_borrow/create/delete/repay/update (5)
  account.sum_samet_create/delete/update (3; borrow/repay are generic, untouched)
  credit.unknown_same_t_fund (1)
  samet.title, samet.same_t_funds, samet.same_asset_... (explainer),
    samet.same_t_backend_... , samet.create_hint (5)
  help.topic_samet_title/text/body (3)
  help.topic_sitemap_body (sitemap link label only) (1)
  menu.p_samet, menu.d_samet (2)
"""
import json
import re
import sys

LOCALES = ["ja", "ko", "zh"]

# (section, key) in stable order for auditability
CHANGED_KEYS = [
    ("account", "op_samet_borrow"),
    ("account", "op_samet_create"),
    ("account", "op_samet_delete"),
    ("account", "op_samet_repay"),
    ("account", "op_samet_update"),
    ("account", "sum_samet_create"),
    ("account", "sum_samet_delete"),
    ("account", "sum_samet_update"),
    ("credit", "unknown_same_t_fund"),
    ("samet", "title"),
    ("samet", "same_t_funds"),
    ("samet", "same_asset_same_t_funds_borrowing_and_repayin"),
    ("samet", "same_t_backend_missing_credit_ui_js_failed_to"),
    ("samet", "create_hint"),
    ("help", "topic_samet_title"),
    ("help", "topic_samet_text"),
    ("help", "topic_samet_body"),
    ("menu", "p_samet"),
    ("menu", "d_samet"),
    # sitemap handled separately (substring replace inside large body)
]

NEW = {
    "ja": {
        ("account", "op_samet_borrow"): "フラッシュローン借入",
        ("account", "op_samet_create"): "フラッシュローン資金作成",
        ("account", "op_samet_delete"): "フラッシュローン資金削除",
        ("account", "op_samet_repay"): "フラッシュローン返済",
        ("account", "op_samet_update"): "フラッシュローン資金更新",
        ("account", "sum_samet_create"): "%(amount)s で フラッシュローン資金を作成しました",
        ("account", "sum_samet_delete"): "フラッシュローン資金 %(fund)s を削除しました",
        ("account", "sum_samet_update"): "フラッシュローン資金 %(fund)s を更新しました",
        ("credit", "unknown_same_t_fund"): "不明なフラッシュローン資金。",
        ("samet", "title"): "フラッシュローン資金",
        ("samet", "same_t_funds"): "フラッシュローン資金",
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin"): "フラッシュローン：借入と返済は1つのトランザクションで実行されます［67 借入＋68 返済］ — 単独の借入はチェーンに拒否されます。レートは分母1,000,000に対するパーセントです。",
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to"): "フラッシュローン資金は利用できません：credit-ui.js の読み込みに失敗しました。",
        ("samet", "create_hint"): " 下の作成フォームから作成してください — 所有するフラッシュローン資金はここに一覧表示されます。",
        ("help", "topic_samet_title"): "フラッシュローン資金",
        ("help", "topic_samet_text"): "プールされたフラッシュローン資金。借入と返済ができます。",
        ("help", "topic_samet_body"): "# プール資金、同種入出\nフラッシュローン資金(Same-T)は多数供給者から1アセットをプールします。借り手はファンドから借入し、金利付きで返済します。チェーンが残高・スケジュールを強制します。\n# 建値の規律\nファンドは整数単位建て（1M基準）です。同一アセットで作成、借入、返済し、規模投入前にファンド制限に留意してください。\n# 同一トランザクション規則\n対のファンド操作は1トランザクションに属します。分割脚は半端な取引を立ち往生させます。画面は対を一緒に作成します — 一度確認、一度署名。",
        ("menu", "p_samet"): "フラッシュローン資金",
        ("menu", "d_samet"): "プールされたフラッシュローン資金と借入。",
    },
    "ko": {
        ("account", "op_samet_borrow"): "플래시론 대출",
        ("account", "op_samet_create"): "플래시론 펀드 생성",
        ("account", "op_samet_delete"): "플래시론 펀드 삭제",
        ("account", "op_samet_repay"): "플래시론 상환",
        ("account", "op_samet_update"): "플래시론 펀드 업데이트",
        ("account", "sum_samet_create"): "플래시론 펀드를 생성했습니다(%(amount)s)",
        ("account", "sum_samet_delete"): "플래시론 펀드 %(fund)s 삭제됨",
        ("account", "sum_samet_update"): "플래시론 펀드 %(fund)s 업데이트됨",
        ("credit", "unknown_same_t_fund"): "알 수 없는 플래시론 펀드입니다.",
        ("samet", "title"): "플래시론 펀드",
        ("samet", "same_t_funds"): "플래시론 펀드",
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin"): "플래시론: 대출과 상환은 하나의 트랜잭션[67 대출 + 68 상환]으로 일어납니다 — 단독 대출은 체인이 거부합니다. 이율은 분모 1,000,000 기준 퍼센트입니다.",
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to"): "플래시론 펀드를 사용할 수 없습니다. credit-ui.js를 불러오지 못했습니다.",
        ("samet", "create_hint"): " 아래 생성 양식에서 새로 만드십시오 — 보유한 플래시론 펀드가 여기에 표시됩니다.",
        ("help", "topic_samet_title"): "플래시론 펀드",
        ("help", "topic_samet_text"): "출금과 상환이 있는 플래시론 풀 펀드.",
        ("help", "topic_samet_body"): "# 풀 자금, 같은 자산 입출\n플래시론 펀드(Same-T)는 많은 공급자로부터 하나의 자산을 모읍니다. 차입자는 자금에서 가져가고 이자 포함 상환하며 체인이 잔액과 일정을 강제합니다.\n# 액면 규율\n자금은 정수 단위(1M 기준)로 표시됩니다. 같은 자산으로 생성, 출금 및 상환하고 규모를 넣기 전에 자금 한도를 살피십시오.\n# 동일 트랜잭션 규칙\n짝을 이루는 자금 작업은 하나의 트랜잭션에 속합니다. 다리를 나누면 거래 절반이 묶일 수 있습니다. 데스크가 쌍을 함께 만듭니다 — 한 번 검토하고 한 번 서명하십시오.",
        ("menu", "p_samet"): "플래시론 펀드",
        ("menu", "d_samet"): "플래시론 풀 펀드와 출금을 제공합니다.",
    },
    "zh": {
        ("account", "op_samet_borrow"): "闪电贷借入",
        ("account", "op_samet_create"): "闪电贷资金池创建",
        ("account", "op_samet_delete"): "闪电贷资金池删除",
        ("account", "op_samet_repay"): "闪电贷还款",
        ("account", "op_samet_update"): "闪电贷资金池更新",
        ("account", "sum_samet_create"): "已创建闪电贷资金池，规模 %(amount)s",
        ("account", "sum_samet_delete"): "已删除闪电贷资金池 %(fund)s",
        ("account", "sum_samet_update"): "已更新闪电贷资金池 %(fund)s",
        ("credit", "unknown_same_t_fund"): "未知闪电贷资金池。",
        ("samet", "title"): "闪电贷资金池",
        ("samet", "same_t_funds"): "闪电贷资金池",
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin"): "闪电贷：借入与还款在同一笔交易中完成 [67 借入 + 68 还款] — 链上拒绝单独的借入操作。费率为分母为 1,000,000 的百分比。",
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to"): "闪电贷资金池不可用：credit-ui.js 加载失败。",
        ("samet", "create_hint"): " 请通过下方的创建表单新建一个 — 您拥有的闪电贷资金池将列在此处。",
        ("help", "topic_samet_title"): "闪电贷资金池",
        ("help", "topic_samet_text"): "汇集的闪电贷资金池，支取与还款。",
        ("help", "topic_samet_body"): "# 同进同出的汇集资金\n闪电贷资金池(Same-T)汇集多供应商的同一资产。借入方按池支取并还本付息；链上强制余额与计划。\n# 面额纪律\n资金池以整单位计价（1M 基础）：创建、支取、还款用同一资产，投入前看清池限额。\n# 同笔交易规则\n成对池操作须进同一笔交易：拆开两边可能让半边交易悬空。操作台成对构建——核对一次，签名一次。",
        ("menu", "p_samet"): "闪电贷资金池",
        ("menu", "d_samet"): "汇集的闪电贷资金池与支取。",
    },
}

# old sitemap link labels (label only changes, hash kept)
OLD_SITEMAP_LABEL = {
    "ja": "- [Same-T ファンド](#/samet)",
    "ko": "- [Same-T 펀드](#/samet)",
    "zh": "- [Same-T 基金](#/samet)",
}
NEW_SITEMAP_LABEL = {
    "ja": "- [フラッシュローン資金](#/samet)",
    "ko": "- [플래시론 펀드](#/samet)",
    "zh": "- [闪电贷资金池](#/samet)",
}

# locale brand fragments accepted by the pre-replace assertion
BRAND_OK = {
    "ja": ["Same-T", "SameT", "Same-asset", "同一", "同種", "ファンド", "資金"],
    "ko": ["Same-T", "SameT", "Same-asset", "동일", "같은", "펀드", "자금", "풀"],
    "zh": ["Same-T", "SameT", "Same-asset", "同资产", "同进", "资金池", "基金"],
}


def fail(msg):
    print(f"ABORT: {msg}", file=sys.stderr)
    sys.exit(1)


def assert_brand(code, key, cur):
    frags = BRAND_OK[code] + ["Same"]
    if not any(f.lower() in cur.lower() if f == "Same" else f in cur for f in frags):
        fail(f"{code} {key}: current value lacks brand: {cur!r}")


def assert_guards(code, new_val):
    for tok in ("%(name)s", "%(amount)s", "%(fund)s", "%(s)s", "1.2.", "http", "67", "68"):
        pass  # placeholders/numbers checked per-key below
    if "#/samet" in new_val and new_val.count("#/samet") != 1 and code:
        pass


for code in LOCALES:
    path = f"/workspace/vanilla/locales/{code}.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    # 1) assert + replace the 19 direct keys
    for sec, k in CHANGED_KEYS:
        cur = d[sec][k]
        assert_brand(code, f"{sec}.{k}", cur)
        new_val = NEW[code][(sec, k)]
        # guard placeholders preserved where the old had them
        for ph in re.findall(r"%\([^)]+\)s", cur):
            if ph not in new_val:
                fail(f"{code} {sec}.{k}: placeholder {ph} lost")
        for ph in re.findall(r"%\([^)]+\)s", new_val):
            if ph not in cur:
                fail(f"{code} {sec}.{k}: placeholder {ph} added")
        # op numbers preserved in explainer
        if k == "same_asset_same_t_funds_borrowing_and_repayin":
            for n in ("67", "68", "1,000,000"):
                if n not in cur or n not in new_val:
                    fail(f"{code} {sec}.{k}: number {n} missing")
            if "credit-ui.js" in new_val:
                fail(f"{code} {sec}.{k}: explainer must not mention credit-ui.js")
        if k == "same_t_backend_missing_credit_ui_js_failed_to":
            if "credit-ui.js" not in cur or "credit-ui.js" not in new_val:
                fail(f"{code} {sec}.{k}: credit-ui.js must be preserved")
        if k == "create_hint" and not new_val.startswith(" "):
            fail(f"{code} {sec}.{k}: leading-space glue lost")
        if "(Same-T)" in new_val and "(Same-T)" not in new_val:
            fail("unreachable")
        d[sec][k] = new_val
    # 2) sitemap link: replace ONLY the label, keep the hash
    sm = d["help"]["topic_sitemap_body"]
    old_link = OLD_SITEMAP_LABEL[code]
    new_link = NEW_SITEMAP_LABEL[code]
    if old_link not in sm:
        fail(f"{code} sitemap: expected link {old_link!r} not found")
    if sm.count("#/samet") != 1:
        fail(f"{code} sitemap: expected exactly one #/samet link")
    d["help"]["topic_sitemap_body"] = sm.replace(old_link, new_link)
    # 3) write back preserving key order
    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"{code}: updated {len(CHANGED_KEYS)} keys + sitemap link")

print("done.")
