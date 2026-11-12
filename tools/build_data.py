# -*- coding: utf-8 -*-
"""从已生成的视频与 TTS 时间轴重建前端数据文件。

产出：
  assets/data/course.json       —— 供调试与备份
  assets/data/course-data.js    —— 前端直接 <script> 引入，规避 file:// 的 fetch 限制

用法：
    python tools/build_data.py
"""

import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_videos import (CHAPTERS, DATA_DIR, VIDEO_DIR, TMP_DIR,  # noqa: E402
                          all_lessons, build_timeline)
from exercises import EXERCISES  # noqa: E402
from exercises_extra import EXERCISES_EXTRA  # noqa: E402

# 主练习 + 补充练习合并；每课按题目顺序拼接
_ALL_EX = {}
for _src in (EXERCISES, EXERCISES_EXTRA):
    for _lid, _items in _src.items():
        _ALL_EX.setdefault(_lid, []).extend(_items)


def exercises_for(lid):
    """返回该课的练习题数组，字段与前端约定一致。"""
    out = []
    for ex in _ALL_EX.get(lid, []):
        out.append({
            "q": ex.get("q", ""),
            "hint": ex.get("hint", ""),
            "answer": ex.get("answer", ""),
            "note": ex.get("note", ""),
            "output": ex.get("output", ""),
        })
    return out


def build():
    meta = {}
    tl_dir = os.path.join(TMP_DIR, "timeline")
    for ch, idx, ls in all_lessons():
        lid = ls["id"]
        dur = 0.0
        subs = []
        tl_path = os.path.join(tl_dir, lid + ".json")
        if os.path.exists(tl_path):
            with open(tl_path, encoding="utf-8") as f:
                tl = json.load(f)
            dur = tl.get("duration", 0.0)
            subs = tl.get("subtitles", [])
        else:
            # 没有时间轴文件时，用 TTS 音频现算（需要 .tmp/tts 仍然存在）
            items = build_timeline(ls, None)
            acc = 0.0
            for it in items:
                d = it["dur"]
                text = it["page"].get("narration", "").replace("\n", " ").strip()
                if text:
                    subs.append({"s": round(acc, 2), "e": round(acc + d, 2), "text": text})
                acc += d
            dur = acc
        mp4 = os.path.join(VIDEO_DIR, lid + ".mp4")
        size = round(os.path.getsize(mp4) / 1048576.0, 2) if os.path.exists(mp4) else 0
        meta[lid] = {
            "file": f"videos/{lid}.mp4",
            "duration": round(dur, 2),
            "size_mb": size,
            "subtitles": subs,
        }

    chapters = []
    for ch in CHAPTERS:
        lessons = []
        for idx, ls in enumerate(ch["lessons"], 1):
            lid = ls["id"]
            m = meta.get(lid, {})
            codes = []
            for p in ls["pages"]:
                if p.get("kind") == "code":
                    codes.append({
                        "title": p.get("title", ""),
                        "code": p.get("code", ""),
                        "output": p.get("output", ""),
                        "lang": "cpp",
                    })
                elif p.get("kind") == "term":
                    codes.append({
                        "title": p.get("title", ""),
                        "code": "\n".join(p.get("lines", [])),
                        "output": "",
                        "lang": "bash",
                    })
            recap = []
            for p in ls["pages"]:
                if p.get("kind") == "recap":
                    recap = [x if isinstance(x, str) else "：".join(x)
                             for x in p.get("items", [])]
            lessons.append({
                "id": lid,
                "index": idx,
                "title": ls["title"],
                "minutes": ls.get("minutes", 5),
                "tags": ls.get("tags", []),
                "video": m.get("file", f"videos/{lid}.mp4"),
                "thumb": f"thumbs/{lid}.jpg",
                "duration": m.get("duration", 0),
                "size_mb": m.get("size_mb", 0),
                "subtitles": m.get("subtitles", []),
                "code": codes,
                "recap": recap,
                "exercises": exercises_for(lid),
            })
        chapters.append({
            "id": ch["id"], "title": ch["title"], "desc": ch["desc"],
            "lessons": lessons,
        })

    total = sum(m["duration"] for m in meta.values())
    return {
        "title": "C++ 系统课程",
        "subtitle": "50 节课，从语法基础到现代 C++ 实战",
        "version": 2,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration": round(total, 1),
        "total_lessons": sum(len(c["lessons"]) for c in chapters),
        "chapters": chapters,
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    course = build()

    p1 = os.path.join(DATA_DIR, "course.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=1)

    p2 = os.path.join(DATA_DIR, "course-data.js")
    with open(p2, "w", encoding="utf-8") as f:
        f.write("/* 由 tools/build_data.py 自动生成，请勿手动修改 */\n")
        f.write("window.COURSE_DATA = ")
        json.dump(course, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    missing = [l["id"] for c in course["chapters"] for l in c["lessons"] if not l["size_mb"]]
    print(f"课时 {course['total_lessons']} 个，总时长 {course['total_duration']/60:.1f} 分钟")
    print(f"已生成视频 {course['total_lessons'] - len(missing)} 个"
          + (f"，缺失: {', '.join(missing)}" if missing else ""))
    print("数据 →", p1)
    print("数据 →", p2)


if __name__ == "__main__":
    main()
