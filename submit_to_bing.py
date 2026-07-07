#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_to_bing.py — 用 IndexNow 协议主动把演示站 URL 推给 Bing。

为什么推 Bing：Bing 的索引被 GPT / Copilot 复用，所以进 Bing 索引 = 部分桥接到
「被大模型爬」。这是 github.io 演示站目前唯一能主动 push 进爬取通道的手段。

IndexNow 协议：https://www.indexnow.org/

前置条件（必须先做，否则会 422 失败）：
  1. 本目录下的 6102ea5eb7a7d03ee7899f028b70fc64.txt 已经 git push 到 GitHub Pages，
     且 https://damnshi.github.io/geo-demo/6102ea5eb7a7d03ee7899f028b70fc64.txt
     能在线访问、返回内容就是这串 key。
     （GitHub Pages 部署通常要等 1~2 分钟。）
  2. 已在 bing.com/webmasters 添加站点并验证所有权（可选，但强烈推荐——
     验证后能在面板看抓取状态、收录数、AI bot 访问）。

用法：
    python submit_to_bing.py          # 推所有默认 URL
    python submit_to_bing.py --dry    # 只打印不真发，用来先核对
"""

import sys
import httpx

# ---- 配置 ----
SITE_BASE = "https://damnshi.github.io/geo-demo"
HOST = "damnshi.github.io"
INDEXNOW_KEY = "6102ea5eb7a7d03ee7899f028b70fc64"  # 必须和 {key}.txt 文件名 + 内容一致
INDEXNOW_ENDPOINT = "https://www.bing.com/indexnow"

# 要推的 URL 列表（和 verify_site.py 的 CHECKS 对齐）
URLS = [
    f"{SITE_BASE}/",
    f"{SITE_BASE}/faq.html",
    f"{SITE_BASE}/llms.txt",
    f"{SITE_BASE}/robots.txt",
    f"{SITE_BASE}/sitemap.xml",
    f"{SITE_BASE}/ai/overview.md",
    f"{SITE_BASE}/ai/agent-guidelines.md",
    f"{SITE_BASE}/ai/source-pages.md",
]


def selfcheck_key_file(key_location: str) -> bool:
    """先 GET 一下 key 文件，确认已部署且内容正确，避免 422。"""
    print(f"自检 key 文件: {key_location}")
    try:
        r = httpx.get(key_location, timeout=15, follow_redirects=True)
    except Exception as e:
        print(f"  访问失败: {e}")
        print("  请先 git add + commit + push，等 GitHub Pages 部署完再跑本脚本。")
        return False
    remote = r.text.strip()
    if r.status_code != 200 or remote != INDEXNOW_KEY:
        print(f"  状态码: {r.status_code}")
        print(f"  实际内容: {remote[:80]!r}")
        print(f"  期望内容: {INDEXNOW_KEY!r}")
        print("  key 文件还没部署成功，先 push 再等 1~2 分钟。")
        return False
    print("  key 文件自检通过 ✓")
    return True


def main() -> None:
    dry = "--dry" in sys.argv
    key_location = f"{SITE_BASE}/{INDEXNOW_KEY}.txt"

    print(f"站点: {SITE_BASE}")
    print(f"key 文件: {key_location}")
    print(f"推送 URL 数: {len(URLS)}")
    for u in URLS:
        print(f"  - {u}")

    if dry:
        print("\n[dry] 未实际发送。去掉 --dry 真发。")
        return

    if not selfcheck_key_file(key_location):
        sys.exit(1)

    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": key_location,
        "urlList": URLS,
    }

    print(f"\n正在推送到 Bing IndexNow ({INDEXNOW_ENDPOINT}) ...")
    try:
        resp = httpx.post(INDEXNOW_ENDPOINT, json=payload, timeout=30)
    except Exception as e:
        print(f"请求失败: {e}")
        sys.exit(1)

    print(f"HTTP {resp.status_code}")
    # IndexNow 状态码：
    #   200 = 已接受，会很快来抓
    #   202 = 已接受，排队中
    #   422 = key 验证失败（key 文件没部署 / 内容不对 / 路径不对）
    if resp.status_code in (200, 202):
        print("已接受。Bing 通常 24~48 小时内来抓。")
        print("下一步：")
        print("  1. 去 bing.com/webmasters 看抓取状态与收录数")
        print("  2. 过 1~2 周不带链接问 Perplexity / 秘塔「GEO 工具有哪些」，复测召回")
    elif resp.status_code == 422:
        print("key 验证失败——确认 {key}.txt 已 push 且能在线访问，内容是 key 本身。")
        sys.exit(1)
    else:
        print(f"未预期状态码，响应: {resp.text[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
