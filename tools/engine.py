# -*- coding: utf-8 -*-
"""视频渲染引擎：把课程页面数据渲染成 1920x1080 的帧。

设计要点
--------
* 单帧纯 RGB 绘制，不用 RGBA 合成，速度优先。
* 淡入效果用「前景色向背景色插值」近似，视觉上等同透明度渐变。
* 代码高亮用正则做词法着色；等宽字体不含中文字形，中文用雅黑补位。
* 所有版式在内容区内垂直居中，避免大片空白。
"""

import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 24

# 内容区
CONTENT_TOP = 226
CONTENT_BOT = 962
LEFT, RIGHT = 120, 1800

# ---------------------------------------------------------------- 配色
BG_TOP = (11, 16, 32)
BG_BOT = (20, 26, 46)
INK = (232, 236, 245)
INK_DIM = (150, 160, 182)
INK_FAINT = (104, 114, 138)
ACCENT = (79, 140, 255)
ACCENT_2 = (0, 209, 178)
PANEL = (16, 22, 38)
LINE = (45, 55, 82)

# 代码配色（One Dark 风格）
C_TEXT = (212, 216, 224)
C_KEY = (198, 120, 221)
C_TYPE = (86, 182, 194)
C_STR = (152, 195, 121)
C_NUM = (209, 154, 102)
C_COM = (106, 118, 140)
C_PRE = (229, 192, 123)
C_FUN = (97, 175, 239)
C_PUN = (150, 158, 176)

_FONT_DIR = "C:\\Windows\\Fonts\\"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_FONT_DIR + name, size)
    return _cache[key]


def f_ui(size):
    return font("msyh.ttc", size)


def f_ui_b(size):
    return font("msyhbd.ttc", size)


def f_mono(size):
    return font("CascadiaMono.ttf", size)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease(t):
    """缓出曲线，让动画更顺。"""
    t = clamp(t)
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------- 背景
BG = None


def build_background():
    """numpy 生成渐变柔光，大半径高斯模糊消除色带，最后叠细网格。"""
    from PIL import ImageFilter

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / (H - 1)
    img = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        img[:, :, c] = BG_TOP[c] + (BG_BOT[c] - BG_TOP[c]) * t

    def glow(cx, cy, rx, ry, rgb, power):
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        g = np.clip(1.0 - d, 0.0, 1.0) ** power
        for c in range(3):
            img[:, :, c] += rgb[c] * g

    glow(1620, -60, 1500, 1100, (16, 34, 70), 1.6)      # 右上蓝
    glow(120, 1100, 1100, 800, (2, 34, 30), 1.8)        # 左下青

    arr = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(arr, "RGB").filter(ImageFilter.GaussianBlur(90))

    # 抖动，避免 8bit 量化产生色带
    rng = np.random.default_rng(7)
    a = np.asarray(im, np.float32) + rng.uniform(-1.2, 1.2, (H, W, 3))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

    # 细网格
    d = ImageDraw.Draw(im)
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=(19, 25, 43))
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=(19, 25, 43))
    return im


def bg():
    global BG
    if BG is None:
        BG = build_background()
    return BG.copy()


# ---------------------------------------------------------------- 中英混排
def is_cjk(ch):
    o = ord(ch)
    return (
        0x2E80 <= o <= 0x9FFF
        or 0x3000 <= o <= 0x303F
        or 0xF900 <= o <= 0xFAFF
        or 0xFF00 <= o <= 0xFFEF
        or 0x2010 <= o <= 0x203A     # 引号、破折号
        or o in (0x00B7, 0x2192, 0x2190)
    )


def runs(text):
    """把文本切成 [(片段, 是否为中文)]，同类的相邻字符合并。"""
    out = []
    for ch in text:
        k = is_cjk(ch)
        if out and out[-1][1] == k:
            out[-1][0] += ch
        else:
            out.append([ch, k])
    return [(t, k) for t, k in out]


def mixed_width(d, text, f_a, f_c):
    w = 0.0
    for seg, cjk in runs(text):
        w += d.textlength(seg, font=(f_c if cjk else f_a))
    return w


def draw_mixed(d, x, y, text, f_a, f_c, fill):
    """按中英文分别选字体绘制，返回结束 x。"""
    for seg, cjk in runs(text):
        f = f_c if cjk else f_a
        d.text((x, y), seg, font=f, fill=fill)
        x += d.textlength(seg, font=f)
    return x


def cjk_of(f_ascii, ratio=0.93):
    return f_ui(max(10, int(f_ascii.size * ratio)))


def text_w(d, s, f):
    return d.textlength(s, font=f)


# ---------------------------------------------------------------- C++ 高亮
KW = {
    "if", "else", "for", "while", "do", "switch", "case", "default", "break",
    "continue", "return", "goto", "try", "catch", "throw", "new", "delete",
    "using", "namespace", "public", "private", "protected", "class", "struct",
    "enum", "union", "template", "typename", "virtual", "override", "final",
    "static", "const", "constexpr", "consteval", "inline", "explicit", "friend",
    "operator", "this", "nullptr", "true", "false", "sizeof", "decltype",
    "noexcept", "mutable", "volatile", "extern", "auto", "co_await", "co_return",
    "co_yield", "static_cast", "dynamic_cast", "const_cast", "reinterpret_cast",
    "and", "or", "not", "typedef", "alignas", "alignof", "static_assert",
}
TYPES = {
    "int", "double", "float", "char", "bool", "void", "long", "short",
    "unsigned", "signed", "wchar_t", "char8_t", "char16_t", "char32_t",
    "size_t", "ptrdiff_t", "string", "vector", "map", "set", "array", "pair",
    "unique_ptr", "shared_ptr", "weak_ptr", "make_unique", "make_shared",
    "ifstream", "ofstream", "fstream", "istringstream", "ostringstream",
    "exception", "runtime_error", "invalid_argument", "out_of_range",
    "cout", "cin", "cerr", "endl", "std", "string_view", "greater",
    "int8_t", "int16_t", "int32_t", "int64_t", "uint8_t", "uint32_t", "mtx",
}

_TOK = re.compile(
    r"(?P<com>//[^\n]*)"
    r"|(?P<str>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<pre>^[ \t]*#[^\n]*)"
    r"|(?P<num>\b(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?)[uUlLfF]*\b)"
    r"|(?P<id>[A-Za-z_]\w*)"
    r"|(?P<pun>[{}()\[\];,.<>+\-*/%=!&|^~?:])"
    r"|(?P<sp>\s+)",
    re.M,
)


_TOKEN_CACHE = {}


def tokenize_cpp(line):
    """把一行代码切成 (文本, 颜色) 片段（结果缓存，逐帧复用）。"""
    hit = _TOKEN_CACHE.get(line)
    if hit is not None:
        return hit
    out = _tokenize_cpp(line)
    _TOKEN_CACHE[line] = out
    return out


def _tokenize_cpp(line):
    out = []
    pos = 0
    for m in _TOK.finditer(line):
        if m.start() > pos:
            out.append((line[pos:m.start()], C_TEXT))
        kind = m.lastgroup
        s = m.group()
        if kind == "com":
            col = C_COM
        elif kind == "str":
            col = C_STR
        elif kind == "pre":
            col = C_PRE
        elif kind == "num":
            col = C_NUM
        elif kind == "sp":
            col = C_TEXT
        elif kind == "pun":
            col = C_PUN
        else:
            if s in KW:
                col = C_KEY
            elif s in TYPES:
                col = C_TYPE
            elif line[m.end():m.end() + 1] == "(":
                col = C_FUN
            else:
                col = C_TEXT
        out.append((s, col))
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], C_TEXT))
    return out


# ---------------------------------------------------------------- 页面 chrome
def draw_chrome(img, d, ctx, t_global, page_no, page_total):
    d.ellipse([92, 62, 104, 74], fill=ACCENT)
    fc = f_ui(23)
    x = 120
    x = draw_mixed(d, x, 52, ctx["chapter"], fc, fc, INK_DIM)
    d.text((x + 14, 52), "·", font=fc, fill=INK_FAINT)
    draw_mixed(d, x + 32, 52, ctx["course_title"], fc, fc, INK_FAINT)

    label = f"{page_no:02d} / {page_total:02d}"
    lw = text_w(d, label, f_mono(22))
    d.text((W - 96 - lw, 53), label, font=f_mono(22), fill=INK_FAINT)

    bar_y = H - 58
    d.rounded_rectangle([96, bar_y, W - 96, bar_y + 6], radius=3, fill=(28, 36, 58))
    pw = int((W - 192) * clamp(t_global))
    if pw > 6:
        d.rounded_rectangle([96, bar_y, 96 + pw, bar_y + 6], radius=3, fill=ACCENT)

    f = f_ui(20)
    name = ctx["lesson_title"]
    d.text((W - 96 - text_w(d, name, f), H - 96), name, font=f, fill=(70, 80, 102))


# ---------------------------------------------------------------- 各页类型
def page_cover(img, d, ctx, t, dur):
    a1 = ease(t / 0.7)
    a2 = ease((t - 0.35) / 0.8)
    a3 = ease((t - 0.9) / 0.9)
    rise = int(26 * (1 - ease(t / 1.2)))

    d.rounded_rectangle([120, 300 + rise, 128, 478 + rise], radius=4,
                        fill=mix(BG_TOP, ACCENT, min(1, a1 * 1.4)))
    fc = f_ui(30)
    draw_mixed(d, 160, 296 + rise, ctx["chapter"], fc, fc, mix(BG_TOP, ACCENT_2, a2))

    title = ctx["page"].get("title", "")
    f = f_ui_b(96)
    if text_w(d, title, f) > W - 760:
        f = f_ui_b(78)
    d.text((158, 366 + rise), title, font=f, fill=mix(BG_TOP, INK, a2))

    sub = ctx["page"].get("subtitle", "")
    if sub:
        fs = f_ui(40)
        d.text((162, 508 + rise), sub, font=fs, fill=mix(BG_TOP, INK_DIM, a2))

    meta = f"第 {ctx['lesson_index']} 课   ·   {ctx['minutes']} 分钟   ·   C++17"
    fm = f_ui(27)
    draw_mixed(d, 162, 650 + rise, meta, fm, fm, mix(BG_TOP, INK_FAINT, a3))

    # 右下角装饰圆环 + 播放三角
    a = ease((t - 0.4) / 1.3)
    if a > 0.01:
        cx, cy = 1548, 560
        for rr in (300, 240, 180):
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                      outline=mix(BG_TOP, (26, 44, 80), a * 0.9), width=2)
        d.polygon([(cx - 88, cy + 66), (cx - 88, cy - 66), (cx + 74, cy)],
                  fill=mix(BG_TOP, (30, 52, 96), a))


def page_bullets(img, d, ctx, t, dur):
    items = ctx["page"].get("items", [])
    title = ctx["page"].get("title", "")
    ta = ease(t / 0.55)
    d.text((LEFT, 150), title, font=f_ui_b(56), fill=mix(BG_TOP, INK, ta))
    d.rounded_rectangle([LEFT, 232, LEFT + int(96 * ta), 238], radius=3, fill=ACCENT)

    n = max(1, len(items))
    row_h = 156 if n <= 3 else (134 if n == 4 else 116)
    block_h = row_h * n
    y0 = CONTENT_TOP + max(20, (CONTENT_BOT - CONTENT_TOP - block_h) // 2)
    start, span = 0.5, max(1.0, dur - 1.6)
    step = span / n

    for i, item in enumerate(items):
        if isinstance(item, str):
            head, body = item, ""
        else:
            head, body = item
        a = ease((t - (start + i * step)) / 0.45)
        if a <= 0.001:
            continue
        y = y0 + i * row_h
        rise = int(18 * (1 - a))
        bx, by = LEFT + 2, y + rise
        d.rounded_rectangle([bx, by, bx + 54, by + 54], radius=14,
                            fill=mix(BG_TOP, (30, 44, 78), a),
                            outline=mix(BG_TOP, (48, 66, 108), a), width=2)
        num = str(i + 1)
        d.text((bx + 27 - text_w(d, num, f_mono(26)) / 2, by + 7), num,
               font=f_mono(26), fill=mix(BG_TOP, ACCENT, a))

        fh = f_ui_b(40)
        x1 = bx + 78
        x1 = draw_mixed(d, x1, by - 4, head, fh, fh, mix(BG_TOP, INK, a))
        if body:
            fb = f_ui(28)
            draw_mixed(d, bx + 78, by + 56, body, fb, fb, mix(BG_TOP, INK_DIM, a))


_METRICS_CACHE = {}


def code_metrics(d, lines, out_lines, has_out):
    """挑选能放下的最大字号，返回 (字体, 中文字体, 行高, 面板高, 输出高, 面板宽)。"""
    key = (tuple(lines), tuple(out_lines), has_out)
    hit = _METRICS_CACHE.get(key)
    if hit is not None:
        return hit
    avail_w = RIGHT - LEFT - 46
    avail_h = CONTENT_BOT - CONTENT_TOP
    for size, lh in ((32, 52), (30, 50), (28, 47), (26, 44), (24, 41),
                     (22, 38), (20, 35), (18, 31)):
        fa = f_mono(size)
        fc = cjk_of(fa)
        widest = max((mixed_width(d, ln, fa, fc) for ln in lines), default=0)
        panel_h = 60 + lh * len(lines) + 18
        out_h = 0
        oa, oc, olh = f_mono(25), cjk_of(f_mono(25)), 40
        if has_out:
            out_h = 34 + olh * len(out_lines) + 14
            widest = max(widest, max((mixed_width(d, s, oa, oc) for s in out_lines), default=0))
        if widest <= avail_w - 46 and panel_h + (out_h + 22 if has_out else 0) <= avail_h:
            pw = int(min(RIGHT - LEFT, max(1080, 84 + widest + 56)))
            res = (fa, fc, lh, panel_h, out_h, pw)
            _METRICS_CACHE[key] = res
            return res
    pw = RIGHT - LEFT
    res = (f_mono(18), cjk_of(f_mono(18)), 31,
           60 + 31 * len(lines) + 18, 0, pw)
    _METRICS_CACHE[key] = res
    return res


def page_code(img, d, ctx, t, dur):
    page = ctx["page"]
    title = page.get("title", "")
    code = page.get("code", "")
    output = page.get("output", "")

    ta = ease(t / 0.5)
    d.text((LEFT, 128), title, font=f_ui_b(46), fill=mix(BG_TOP, INK, ta))
    d.rounded_rectangle([LEFT, 196, LEFT + int(84 * ta), 201], radius=3, fill=ACCENT)

    lines = code.split("\n")
    out_lines = output.split("\n") if output else []
    has_out = bool(output)
    fa, fc, lh, panel_h, out_h, panel_w = code_metrics(d, lines, out_lines, has_out)
    panel_r = LEFT + panel_w

    total_h = panel_h + (out_h + 22 if has_out else 0)
    top = CONTENT_TOP + max(0, (CONTENT_BOT - CONTENT_TOP - total_h) // 2)

    d.rounded_rectangle([LEFT, top, panel_r, top + panel_h], radius=18,
                        fill=PANEL, outline=LINE, width=2)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([LEFT + 22 + i * 26, top + 20, LEFT + 34 + i * 26, top + 32], fill=c)

    x_code = LEFT + 84
    inner_top = top + 58

    total_chars = sum(len(l) for l in lines)
    # 打字节奏有两个坑，这里都绕开了：
    #
    # 1) 不能用缓出曲线。ease() 的导数是 3(1-t)^2，起始速度是收尾的几十倍，
    #    观感就是“开头飞快、越打越慢、最后卡住”。打字要的是稳定节奏，用线性。
    #
    # 2) 时长不能固定占页时长的 60%。旁白长而代码短的页（比如第 1 课那页只有
    #    94 个字符却配了 38 秒旁白）会被拖成每秒四个字，慢得让人以为卡住了。
    #    改成由字符数决定：目标速度 14~45 字/秒，同时必须在本页打完。
    span = clamp(dur * 0.62, total_chars / 45.0, total_chars / 14.0)
    span = max(0.4, min(span, dur * 0.85))
    p = clamp((t - 0.25) / span)
    shown = p * (total_chars + 1)

    lf = f_mono(max(13, fa.size - 7))
    used = 0
    cursor = (x_code, inner_top)
    for i, ln in enumerate(lines):
        y = inner_top + i * lh
        num = str(i + 1)
        d.text((LEFT + 64 - text_w(d, num, lf), y + max(2, lh // 6)), num,
               font=lf, fill=(72, 82, 106))

        n_show = min(len(ln), max(0, int(shown - used)))
        used += len(ln) + 1
        text = ln[:n_show]
        x = x_code
        for seg, col in tokenize_cpp(text):
            x = draw_mixed(d, x, y, seg, fa, fc, col)
        if n_show < len(ln):
            cursor = (x, y)
            break

    if p < 0.999:
        d.rectangle([cursor[0], cursor[1] + 5, cursor[0] + 9, cursor[1] + lh - 8],
                    fill=ACCENT)

    if has_out:
        a = ease((t - dur * 0.58) / 0.9)
        if a > 0.01:
            oy = top + panel_h + 22
            d.rounded_rectangle([LEFT, oy, panel_r, oy + out_h], radius=14,
                                fill=mix(BG_TOP, (10, 14, 26), a),
                                outline=mix(BG_TOP, (38, 48, 72), a), width=2)
            fo = f_ui(21)
            draw_mixed(d, LEFT + 26, oy + 8, "输出", fo, fo, mix(BG_TOP, ACCENT_2, a))
            oa, oc = f_mono(25), cjk_of(f_mono(25))
            oy2 = oy + 40
            for ln in out_lines:
                draw_mixed(d, LEFT + 30, oy2, ln, oa, oc,
                           mix(BG_TOP, (126, 231, 187), a))
                oy2 += 40


def page_term(img, d, ctx, t, dur):
    page = ctx["page"]
    title = page.get("title", "")
    lines = page.get("lines", [])
    ta = ease(t / 0.5)
    d.text((LEFT, 128), title, font=f_ui_b(46), fill=mix(BG_TOP, INK, ta))
    d.rounded_rectangle([LEFT, 196, LEFT + int(84 * ta), 201], radius=3, fill=ACCENT_2)

    fa = f_mono(28)
    fc = cjk_of(fa)
    lh = 46
    panel_h = 64 + lh * len(lines) + 22
    top = CONTENT_TOP + max(0, (CONTENT_BOT - CONTENT_TOP - panel_h) // 2)
    d.rounded_rectangle([LEFT, top, RIGHT, top + panel_h], radius=18,
                        fill=(9, 13, 24), outline=LINE, width=2)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([LEFT + 24 + i * 26, top + 20, LEFT + 36 + i * 26, top + 32], fill=c)
    d.text((RIGHT - 110, top + 14), "bash", font=f_ui(20), fill=(64, 74, 96))

    y = top + 62
    n = max(1, len(lines))
    step = max(0.10, (dur - 1.1) / n)
    for i, ln in enumerate(lines):
        a = ease((t - 0.3 - i * step) / 0.32)
        if a <= 0.001:
            y += lh
            continue
        if ln.startswith("$"):
            col = mix((9, 13, 24), (130, 210, 255), a)
        elif ln.startswith("#"):
            col = mix((9, 13, 24), C_COM, a)
        else:
            col = mix((9, 13, 24), (126, 231, 187), a)
        draw_mixed(d, LEFT + 34, y, ln, fa, fc, col)
        y += lh


def page_recap(img, d, ctx, t, dur):
    items = ctx["page"].get("items", [])
    title = ctx["page"].get("title", "")
    ta = ease(t / 0.5)
    d.text((LEFT, 150), title, font=f_ui_b(56), fill=mix(BG_TOP, INK, ta))
    d.rounded_rectangle([LEFT, 232, LEFT + int(96 * ta), 238], radius=3, fill=ACCENT_2)

    n = max(1, len(items))
    row_h = 150 if n <= 3 else (122 if n == 4 else 100)
    block_h = row_h * n
    y0 = CONTENT_TOP + max(16, (CONTENT_BOT - CONTENT_TOP - block_h) // 2)

    for i, it in enumerate(items):
        a = ease((t - 0.45 - i * 0.24) / 0.42)
        if a <= 0.001:
            continue
        y = y0 + i * row_h
        r = 22
        cx, cy = LEFT + 26, y + 26
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=mix(BG_TOP, (22, 50, 46), a))
        d.line([(cx - 9, cy + 1), (cx - 2, cy + 8), (cx + 10, cy - 7)],
               fill=mix(BG_TOP, ACCENT_2, a), width=4)
        f = f_ui(34)
        draw_mixed(d, LEFT + 74, y + 2, it, f, f, mix(BG_TOP, INK, a))


RENDERERS = {
    "cover": page_cover,
    "bullets": page_bullets,
    "code": page_code,
    "term": page_term,
    "recap": page_recap,
}


def render_frame(ctx, t, dur, t_global, page_no, page_total):
    img = bg()
    d = ImageDraw.Draw(img)
    page = ctx["page"]
    fn = RENDERERS.get(page.get("kind", "bullets"), page_bullets)
    fn(img, d, ctx, t, dur)
    draw_chrome(img, d, ctx, t_global, page_no, page_total)
    return img
