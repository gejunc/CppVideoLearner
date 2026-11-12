# -*- coding: utf-8 -*-
"""交付验收：检查课程数据、视频、练习题、项目源码是否齐全且自洽。

只读，不修改任何文件。
"""

import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "course-data.js")
VIDEOS = os.path.join(ROOT, "assets", "videos")
THUMBS = os.path.join(ROOT, "assets", "thumbs")
SAMPLE = os.path.join(ROOT, "assets", "samples", "account_book.cpp")
EXE_PORTABLE = os.path.join(ROOT, "release", "CppVideoLearner.exe")
EXE_UNPACKED = os.path.join(ROOT, "release", "win-unpacked", "CppVideoLearner.exe")

REQUIRED_CHAPTER_TITLES = ["并发", "工具链", "模板", "C++20", "工程实践", "项目实战"]

ok = True
def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  -> ' + str(detail)) if detail else ''}")


def main():
    check("course-data.js 存在", os.path.exists(DATA))
    raw = open(DATA, encoding="utf-8").read()
    m = re.search(r"window\.COURSE_DATA\s*=\s*(\{.*\});\s*$", raw, re.S)
    check("course-data.js 可解析", bool(m))
    course = json.loads(m.group(1))

    chapters = course["chapters"]
    lessons = [ls for ch in chapters for ls in ch["lessons"]]

    check("章节数 = 14", len(chapters) == 14, len(chapters))
    check("课时数 = 50", len(lessons) == 50, len(lessons))

    # 新增章节都在
    titles = " ".join(ch["title"] for ch in chapters)
    for kw in REQUIRED_CHAPTER_TITLES:
        check(f"包含「{kw}」章节", kw in titles)

    # 每课题数
    ex_counts = [len(ls.get("exercises") or []) for ls in lessons]
    check("每课至少 2 道练习题", min(ex_counts) >= 2, f"最少 {min(ex_counts)}")
    check("练习题总数 = 100", sum(ex_counts) == 100, sum(ex_counts))

    # 练习题字段完整
    bad_ex = 0
    for ls in lessons:
        for ex in ls.get("exercises") or []:
            if not ex.get("q") or not ex.get("answer"):
                bad_ex += 1
    check("每题都有题目和参考答案", bad_ex == 0, f"缺失 {bad_ex}")

    # 视频文件与数据一一对应
    missing_v = [ls["id"] for ls in lessons if not os.path.exists(os.path.join(VIDEOS, ls["id"] + ".mp4"))]
    check("每课都有 mp4", not missing_v, ",".join(missing_v[:5]))
    missing_t = [ls["id"] for ls in lessons if not os.path.exists(os.path.join(THUMBS, ls["id"] + ".jpg"))]
    check("每课都有缩略图", not missing_t, ",".join(missing_t[:5]))

    # 字幕非空
    no_sub = [ls["id"] for ls in lessons if not (ls.get("subtitles") or [])]
    check("每课都有字幕", not no_sub, ",".join(no_sub[:5]))

    # 时长合理（每课 1~5 分钟）
    durs = [ls.get("duration", 0) for ls in lessons]
    check("每课时长在 60~300 秒", all(60 <= d <= 300 for d in durs),
          f"{min(durs):.0f}~{max(durs):.0f}")

    # 代码示例
    no_code = [ls["id"] for ls in lessons if not (ls.get("code") or [])]
    check("每课都有代码片段", not no_code, ",".join(no_code[:5]))

    # 项目课
    proj = [ls for ls in lessons if ls["id"] in ("l47", "l48", "l49", "l50")]
    check("项目课 4 节齐全", len(proj) == 4, len(proj))
    check("项目课章节名正确", any("项目实战" in ch["title"] for ch in chapters))

    # 项目源码
    check("记账本源码存在", os.path.exists(SAMPLE))
    if os.path.exists(SAMPLE):
        src = open(SAMPLE, encoding="utf-8").read()
        lines = src.count("\n") + 1
        check("记账本源码 ≥ 200 行", lines >= 200, f"{lines} 行")
        for kw in ("class Ledger", "struct Transaction", "byCategory", "save", "load"):
            check(f"源码包含 {kw}", kw in src)

    # 打包产物
    check("portable exe 存在", os.path.exists(EXE_PORTABLE))
    check("win-unpacked exe 存在", os.path.exists(EXE_UNPACKED))

    # 新章节的视频都在且有内容
    big = [ls for ls in lessons if ls["id"] in ("l27", "l33", "l34", "l40", "l41")]
    for ls in big:
        p = os.path.join(VIDEOS, ls["id"] + ".mp4")
        size_mb = os.path.getsize(p) / 1048576.0 if os.path.exists(p) else 0
        check(f"{ls['id']} 视频非空", size_mb > 0.5, f"{size_mb:.1f} MB")

    total_min = course["total_duration"] / 60
    print(f"\n课程总时长 {total_min:.1f} 分钟，练习题 {sum(ex_counts)} 道")
    print("验收结果:", "全部通过" if ok else "有失败项")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
