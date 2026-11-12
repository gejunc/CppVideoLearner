# -*- coding: utf-8 -*-
"""生成应用图标（build/icon.ico）与窗口图标。

图形语言与课程视频一致：深蓝渐变底 + 青色播放三角 + C++ 字样。
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)

S = 1024


def background():
    """深蓝渐变 + 两处柔和光斑（numpy 计算，模糊消色带）。"""
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    t = yy / (S - 1)
    top, bot = np.array([12, 19, 40], np.float32), np.array([27, 49, 104], np.float32)
    img = top[None, None, :] + (bot - top)[None, None, :] * t[:, :, None]

    def glow(cx, cy, r, rgb, power):
        d = np.sqrt(((xx - cx) ** 2 + (yy - cy) ** 2)) / r
        g = np.clip(1 - d, 0, 1) ** power
        return g[:, :, None] * np.array(rgb, np.float32)[None, None, :]

    img = img + glow(S * 0.78, S * 0.16, S * 0.95, (14, 44, 110), 1.7)
    img = img + glow(S * 0.16, S * 0.94, S * 0.85, (0, 46, 40), 1.9)

    arr = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").filter(ImageFilter.GaussianBlur(28))


def make_icon():
    img = background().convert("RGBA")
    d = ImageDraw.Draw(img)

    # C++ 字样：精确居中（略微上移，给右下角三角留空间）
    f = ImageFont.truetype("C:\\Windows\\Fonts\\msyhbd.ttc", 430)
    text = "C++"
    bbox = d.textbbox((0, 0), text, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (S - w) / 2 - bbox[0] - 18
    y = (S - h) / 2 - bbox[1] - 46
    d.text((x, y), text, font=f, fill=(241, 245, 253))

    # 右下角播放三角
    cx, cy, r = S * 0.775, S * 0.775, S * 0.105
    d.polygon([(cx - r * 0.60, cy - r), (cx - r * 0.60, cy + r), (cx + r * 0.95, cy)],
              fill=(0, 209, 178))

    # 圆角裁切
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.21), fill=255)
    img.putalpha(mask)

    out = os.path.join(BUILD, "icon.ico")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    img.resize((256, 256), Image.LANCZOS).save(
        out, format="ICO", sizes=[(s, s) for s in sizes])
    print("图标 →", out)

    # macOS 用这张 1024×1024 的 PNG，electron-builder 会自己转成 .icns
    png = os.path.join(BUILD, "icon.png")
    img.resize((1024, 1024), Image.LANCZOS).save(png)
    print("图标 →", png)

    # Linux 常用 512
    img.resize((512, 512), Image.LANCZOS).save(os.path.join(BUILD, "icon-512.png"))
    print("图标 →", os.path.join(BUILD, "icon-512.png"))


if __name__ == "__main__":
    make_icon()
