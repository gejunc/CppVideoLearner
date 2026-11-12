# -*- coding: utf-8 -*-
"""渲染若干代表页面为 PNG，用于人工检查排版效果。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from course_a import CHAPTERS_A
from course_b import CHAPTERS_B

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp", "preview")
os.makedirs(OUT, exist_ok=True)

CHAPTERS = CHAPTERS_A + CHAPTERS_B


def find(kind, nth=0):
    hits = []
    for ch in CHAPTERS:
        for idx, ls in enumerate(ch["lessons"], 1):
            for p in ls["pages"]:
                if p.get("kind") == kind:
                    hits.append((ch, idx, ls, p))
    return hits[min(nth, len(hits) - 1)]


def shots():
    plan = [
        ("cover", 0, 1.4, "01_cover.png"),
        ("bullets", 0, 6.0, "02_bullets.png"),
        ("code", 0, 4.2, "03_code.png"),
        ("code", 3, 8.0, "04_code_long.png"),
        ("term", 0, 6.0, "05_term.png"),
        ("recap", 0, 3.4, "06_recap.png"),
        ("bullets", 6, 7.0, "07_bullets2.png"),
    ]
    for kind, nth, t, name in plan:
        ch, idx, ls, page = find(kind, nth)
        ctx = {
            "chapter": ch["title"], "course_title": "C++ 系统课程",
            "lesson_title": ls["title"], "lesson_index": idx,
            "minutes": ls.get("minutes", 5), "page": page,
        }
        dur = 9.0
        img = engine.render_frame(ctx, t, dur, 0.42, 2, 5)
        img.save(os.path.join(OUT, name))
        print("saved", name)


if __name__ == "__main__":
    shots()
