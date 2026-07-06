#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""部署 Gitee Pages 后，用公网 URL 替换所有文件中的占位符。"""

from __future__ import annotations

import sys
from pathlib import Path

PLACEHOLDER = "YOUR_GITEE_PAGES_URL"
ROOT = Path(__file__).resolve().parent
TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".md"}


def normalize_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def main() -> None:
    if len(sys.argv) != 2:
        print("用法: python set_demo_url.py https://你的用户名.gitee.io/geo-demo")
        raise SystemExit(1)

    new_url = normalize_url(sys.argv[1])
    changed_files = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if path.name == "set_demo_url.py":
            continue
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER not in text:
            continue
        path.write_text(text.replace(PLACEHOLDER, new_url), encoding="utf-8")
        changed_files += 1
        print(f"已更新: {path.relative_to(ROOT)}")

    print(f"\n完成。共更新 {changed_files} 个文件。")
    print(f"演示站根地址: {new_url}/")
    print("下一步: python verify_site.py", new_url)


if __name__ == "__main__":
    main()
