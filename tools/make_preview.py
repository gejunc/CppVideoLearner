# -*- coding: utf-8 -*-
"""从成片里抽几帧拼成课程预览图。"""

import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_videos import find_ffmpeg  # noqa: E402

TMP = os.path.join(ROOT, ".tmp")
OUT = os.path.join(TMP, "course-preview.png")

PICKS = [
    ("l01", 3.0, "封面：第 1 章 · 起步"),
    ("l28", 46.0, "并发：互斥量保护临界区"),
    ("l41", 30.0, "C++20：ranges 管道"),
    ("l47", 70.0, "项目课：记账本的数据模型"),
]


def grab():
    ff = find_ffmpeg()
    frames = []
    for lid, t, label in PICKS:
        src = os.path.join(ROOT, "assets", "videos", lid + ".mp4")
        dst = os.path.join(TMP, f"f_{lid}.png")
        subprocess.run([ff, "-y", "-v", "error", "-ss", str(t), "-i", src,
                        "-frames:v", "1", dst], check=True)
        frames.append((dst, label))
    return frames


def compose(frames):
    W, H = 960, 540
    canvas = Image.new("RGB", (W * 2, H * 2), (10, 15, 30))
    for i, (path, label) in enumerate(frames):
        im = Image.open(path).resize((W, H), Image.LANCZOS)
        x, y = (i % 2) * W, (i // 2) * H
        canvas.paste(im, (x, y))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype("C:\\Windows\\Fonts\\msyhbd.ttc", 22)
    for i, (path, label) in enumerate(frames):
        x, y = (i % 2) * W, (i // 2) * H
        d.rectangle([x, y + H - 44, x + W, y + H], fill=(6, 10, 20))
        d.text((x + 18, y + H - 36), label, font=f, fill=(200, 214, 240))
    # 中线
    d.line([(W, 0), (W, H * 2)], fill=(20, 30, 52), width=2)
    d.line([(0, H), (W * 2, H)], fill=(20, 30, 52), width=2)
    canvas.save(OUT)
    print("预览图 →", OUT)


if __name__ == "__main__":
    compose(grab())
