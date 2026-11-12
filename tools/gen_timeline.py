# -*- coding: utf-8 -*-
"""从已生成的 course.json 反推每课时间轴，落到 .tmp/timeline/。

视频生成时也会写这份文件；这个脚本只是为了让"先有视频、后补时间轴"的
场景也能跑通，从而可以安全删除中间产生的 TTS wav。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_videos import TMP_DIR, DATA_DIR  # noqa: E402


def main():
    src = os.path.join(DATA_DIR, "course.json")
    with open(src, encoding="utf-8") as f:
        course = json.load(f)

    out_dir = os.path.join(TMP_DIR, "timeline")
    os.makedirs(out_dir, exist_ok=True)

    n = 0
    for ch in course["chapters"]:
        for ls in ch["lessons"]:
            subs = ls.get("subtitles") or []
            if not subs:
                print(f"  ! {ls['id']} 没有字幕数据，跳过")
                continue
            with open(os.path.join(out_dir, ls["id"] + ".json"), "w",
                      encoding="utf-8") as f:
                json.dump({"duration": ls.get("duration", 0), "subtitles": subs},
                          f, ensure_ascii=False)
            n += 1
    print(f"已写出 {n} 份时间轴 → {out_dir}")


if __name__ == "__main__":
    main()
