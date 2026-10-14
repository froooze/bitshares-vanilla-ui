#!/usr/bin/env python3
"""Rename Same-T brand to flash-loan wording in hi.json (REPLACE, not insert).

Owns: the hi Same-T -> फ्लैश लोन value replacements only.
Consumes: vanilla/locales/hi.json (ordered dict).
Side effects: overwrites hi.json in place with json.dumps(indent=2,
  ensure_ascii=False) + trailing newline, preserving key order.
Task: rename-samet-ru-tr-hi.

Each replacement asserts the CURRENT value before replacing and aborts
loudly otherwise. Most currents carry the English Same-T/Same-asset brand;
the two pooled-funds blurbs were already localized as समान-एसेट with no
Latin brand, so those two assert the known localized old phrase instead.
Formal आप register; postpositions में/से/को preserved; nukta kept where
the file writes it (फ़ंड vs फंड per key).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "vanilla", "locales", "hi.json")

BRAND_RE = re.compile(r"same[-_]?t|same[-_]?asset", re.IGNORECASE)


def abort(msg):
    print(f"ABORT hi: {msg}", file=sys.stderr)
    sys.exit(1)


def need_brand(cur, label):
    if not isinstance(cur, str) or not BRAND_RE.search(cur):
        abort(f"{label} current value lacks Same-T/Same-asset brand: {cur!r}")


def need_old(cur, needle, label):
    if not isinstance(cur, str) or needle not in cur:
        abort(f"{label} current value lacks expected old phrase {needle!r}: {cur!r}")


def main():
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)

    def get(sec, key):
        try:
            return d[sec][key]
        except KeyError:
            abort(f"missing key {sec}.{key}")

    reps = [
        ("samet", "title", "फ्लैश लोन फ़ंड"),
        ("samet", "same_t_funds", "फ्लैश लोन फ़ंड"),
        ("menu", "p_samet", "फ्लैश लोन फंड"),
        ("help", "topic_samet_title", "फ्लैश लोन फ़ंड"),
        ("account", "op_samet_borrow", "फ्लैश लोन उधार"),
        ("account", "op_samet_create", "फ्लैश लोन फंड निर्माण"),
        ("account", "op_samet_delete", "फ्लैश लोन फंड हटाना"),
        ("account", "op_samet_repay", "फ्लैश लोन चुकौती"),
        ("account", "op_samet_update", "फ्लैश लोन फंड अपडेट"),
        ("credit", "unknown_same_t_fund", "अज्ञात फ्लैश लोन फ़ंड।"),
        ("samet", "create_hint",
         " नीचे निर्माण फ़ॉर्म से एक बनाएँ — स्वामित्व वाले फ्लैश लोन फ़ंड यहाँ सूचीबद्ध हैं।"),
        ("samet", "same_asset_same_t_funds_borrowing_and_repayin",
         "फ्लैश लोन: उधार और चुकौती एक ही लेनदेन में होती है [67 उधार + 68 चुकौती] — चेन अकेला उधार अस्वीकार करती है। दरें 1,000,000 हर पर प्रतिशत हैं।"),
        ("samet", "same_t_backend_missing_credit_ui_js_failed_to",
         "फ्लैश लोन फ़ंड अनुपलब्ध है: credit-ui.js लोड नहीं हुआ।"),
        ("account", "sum_samet_create",
         "फ्लैश लोन फंड %(amount)s के साथ बनाया गया"),
        ("account", "sum_samet_delete",
         "फ्लैश लोन फंड %(fund)s हटाया गया"),
        ("account", "sum_samet_update",
         "फ्लैश लोन फंड %(fund)s अपडेट हुआ"),
    ]
    for sec, key, new in reps:
        cur = get(sec, key)
        need_brand(cur, f"{sec}.{key}")
        if "%(amount)s" in cur and "%(amount)s" not in new:
            abort(f"{sec}.{key} would drop %(amount)s placeholder")
        if "%(fund)s" in cur and "%(fund)s" not in new:
            abort(f"{sec}.{key} would drop %(fund)s placeholder")
        if key == "create_hint" and not new.startswith(" "):
            abort("create_hint lost load-bearing leading space")
        d[sec][key] = new

    cur = get("help", "topic_samet_text")
    need_old(cur, "समान-एसेट", "help.topic_samet_text")
    d["help"]["topic_samet_text"] = (
        "आहरण व चुकौती सहित पूल्ड फ्लैश लोन फ़ंड।")
    cur = get("menu", "d_samet")
    need_old(cur, "समान-एसेट", "menu.d_samet")
    d["menu"]["d_samet"] = "पूल किए फ्लैश लोन फंड और निकासी।"

    cur_body = get("help", "topic_samet_body")
    lines = cur_body.split("\n")
    if len(lines) < 2:
        abort("topic_samet_body has no content line")
    need_brand(lines[1], "help.topic_samet_body line 2")
    # Hindi uses the danda "। " as sentence separator, not ". ".
    parts = lines[1].split("। ")
    if len(parts) < 2:
        abort("topic_samet_body first line has unexpected shape")
    new_first = ("फ्लैश लोन फ़ंड (Same-T) अनेक आपूर्तिकर्ताओं से एक एसेट "
                 "पूल करते हैं। " + "। ".join(parts[1:]))
    if "(Same-T)" not in new_first:
        abort("new body first line lost (Same-T) bridge")
    lines[1] = new_first
    d["help"]["topic_samet_body"] = "\n".join(lines)

    cur_map = get("help", "topic_sitemap_body")
    old_link = "[Same-T फंड](#/samet)"
    new_link = "[फ्लैश लोन फंड](#/samet)"
    if old_link not in cur_map:
        abort(f"sitemap body lacks expected link {old_link!r}")
    if "#/samet" not in new_link:
        abort("sitemap new link lost #/samet hash")
    d["help"]["topic_sitemap_body"] = cur_map.replace(old_link, new_link, 1)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("hi: Same-T -> फ्लैश लोन replacements applied.")


if __name__ == "__main__":
    main()
