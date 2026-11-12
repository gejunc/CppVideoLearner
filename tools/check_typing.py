# -*- coding: utf-8 -*-
"""验证打字动画的节奏：对某一课的代码页，按时序采样「已揭示字符数」。

用法：python tools/check_typing.py l01
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import FPS, clamp  # noqa: E402
from build_videos import CHAPTERS, TMP_DIR  # noqa: E402

TARGET = sys.argv[1] if len(sys.argv) > 1 else "l01"


def find_lesson(lid):
    for ch in CHAPTERS:
        for ls in ch["lessons"]:
            if ls["id"] == lid:
                return ch, ls
    return None, None


def main():
    ch, ls = find_lesson(TARGET)
    if not ls:
        print("找不到课时", TARGET)
        return 1

    tl = os.path.join(TMP_DIR, "timeline", TARGET + ".json")
    if not os.path.exists(tl):
        print("缺少时间轴，先跑 build_videos.py")
        return 1
    durs = [s["e"] - s["s"] for s in json.load(open(tl, encoding="utf-8"))["subtitles"]]

    idx = 0
    for p in ls["pages"]:
        if not p.get("narration", "").strip():
            continue
        if idx >= len(durs):
            break
        dur = durs[idx]
        idx += 1
        if p.get("kind") != "code":
            continue

        code = p.get("code", "")
        lines = code.split("\n")
        total = sum(len(l) for l in lines)
        span = clamp(dur * 0.62, total / 45.0, total / 14.0)
        span = max(0.4, min(span, dur * 0.85))

        print(f"\n【{p.get('title')}】{total} 字符，本页 {dur:.1f}s，打字窗口 {span:.2f}s")
        print("  秒数   已揭示字符   瞬时速度(字/秒)")
        assert span > 0
        prev = 0.0
        step = 1.0
        t = 0.0
        while t <= min(dur, span + 3.0) + 0.01:
            pr = clamp((t - 0.25) / span)
            shown = pr * (total + 1)
            speed = (shown - prev) / step if t > 0 else 0.0
            print(f"  {t:5.1f}  {shown:10.1f}   {speed:10.1f}")
            prev = shown
            t += step
        # 完成时间
        done = 0.25 + span
        print(f"  -> 在 {done:.1f}s 打完，之后 {max(0, dur - done):.1f}s 展示完整代码")
    return 0


if __name__ == "__main__":
    sys.exit(main())
