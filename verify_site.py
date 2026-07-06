#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查演示站是否可被爬虫/大模型直接读取（不执行 JavaScript）。"""

from __future__ import annotations

import sys

import httpx

CHECKS = [
    ("/", ["GEO Growth", "生成式引擎优化", "AI 友好度"], 800),
    ("/faq.html", ["常见问题", "GEO"], 400),
    ("/llms.txt", ["GEO Growth", "Generative Engine Optimization"], 200),
    ("/robots.txt", ["Allow", "Sitemap"], 20),
    ("/sitemap.xml", ["<urlset", "faq.html"], 50),
    ("/ai/overview.md", ["GEO Growth", "思迪信息"], 100),
    ("/ai/agent-guidelines.md", ["Agent", "GEO Growth"], 80),
]


def normalize_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def main() -> None:
    if len(sys.argv) != 2:
        print("用法: python verify_site.py https://你的用户名.gitee.io/geo-demo")
        raise SystemExit(1)

    base = normalize_url(sys.argv[1])
    print(f"检查站点: {base}\n")
    passed = 0
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "GEO-Demo-Verifier/1.0"}) as client:
        for path, keywords, min_len in CHECKS:
            url = base + path
            try:
                response = client.get(url)
                body = response.text
                ok_len = len(body) >= min_len
                ok_kw = all(k in body for k in keywords)
                ok_type = path.endswith(".txt") or path.endswith(".md") or path.endswith(".xml") or "<html" in body.lower()
                not_spa = not (len(body) < 500 and 'id="app"' in body and "module" in body)
                ok = response.status_code == 200 and ok_len and ok_kw and ok_type and not_spa
                status = "PASS" if ok else "FAIL"
                print(f"[{status}] {path}  status={response.status_code}  len={len(body)}")
                if not ok:
                    if not ok_len:
                        print(f"       期望长度 >= {min_len}")
                    if not ok_kw:
                        missing = [k for k in keywords if k not in body]
                        print(f"       缺少关键词: {missing}")
                    if not not_spa:
                        print("       疑似 Vue SPA 空壳，正文不可读")
                else:
                    passed += 1
            except Exception as exc:
                print(f"[FAIL] {path}  请求失败: {exc}")

    print(f"\n结果: {passed}/{len(CHECKS)} 通过")
    if passed == len(CHECKS):
        print("演示站已满足「可被爬虫直接读取」的基本要求。")
    else:
        print("请检查 Gitee Pages 是否部署成功、文件是否在仓库根目录。")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
