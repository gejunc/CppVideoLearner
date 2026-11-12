# -*- coding: utf-8 -*-
"""把课程数据渲染成 MP4 视频 + 字幕 + 前端所需的数据文件。

流水线
------
1. 收集所有页面的旁白，批量交给 Windows TTS 合成 wav
2. 按旁白时长算出每页的停留时间，得到时间轴
3. 逐帧渲染 PNG 像素，通过管道喂给 ffmpeg 编码成 H.264
4. 把各页 wav 与静音拼成完整音轨，与视频封装成 mp4
5. 输出 VTT 字幕、课程 JSON、课时缩略图

用法：
    python tools/build_videos.py              # 全部课时
    python tools/build_videos.py --only l01   # 只生成指定课时
    python tools/build_videos.py --jobs 4     # 并行进程数
"""

import argparse
import json
import os
import subprocess
import sys
import time
import wave
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine
from engine import FPS, H, W
from course_a import CHAPTERS_A
from course_b import CHAPTERS_B
from course_c import CHAPTERS_C
from course_d import CHAPTERS_D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(ROOT, "assets", "videos")
DATA_DIR = os.path.join(ROOT, "assets", "data")
TMP_DIR = os.path.join(ROOT, ".tmp")
THUMB_DIR = os.path.join(ROOT, "assets", "thumbs")

FFMPEG = None
SAMPLE_RATE = 44100
CHANNELS = 1
SAMPWIDTH = 2

CHAPTERS = CHAPTERS_A + CHAPTERS_B + CHAPTERS_C + CHAPTERS_D


# ------------------------------------------------------------------ 工具
def find_ffmpeg():
    global FFMPEG
    if FFMPEG:
        return FFMPEG
    try:
        import imageio_ffmpeg
        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FFMPEG = "ffmpeg"
    return FFMPEG


def all_lessons():
    out = []
    for ch in CHAPTERS:
        for idx, ls in enumerate(ch["lessons"], 1):
            out.append((ch, idx, ls))
    return out


def lesson_pages(ls):
    return ls["pages"]


# ------------------------------------------------------------------ TTS
def tts_manifest(lessons, only=None):
    """生成 TTS 任务清单：[(key, text)]"""
    jobs = []
    for ch, _idx, ls in lessons:
        if only and ls["id"] not in only:
            continue
        for pi, page in enumerate(lesson_pages(ls)):
            text = page.get("narration", "").strip()
            if text:
                jobs.append((f"{ls['id']}_p{pi}", text))
    return jobs


PS_TTS = r"""
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$jobs = Get-Content -Raw -Encoding UTF8 "{manifest}" | ConvertFrom-Json
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(44100, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $synth.SelectVoice("Microsoft Huihui Desktop") } catch { }
$synth.Rate = -1
$synth.Volume = 100
$ok = 0
foreach ($j in $jobs) {
    $synth.SetOutputToWaveFile($j.wav, $fmt)
    $synth.Speak($j.text)
    $synth.SetOutputToNull()
    $ok++
}
$synth.Dispose()
Write-Output "tts done: $ok"
"""


def run_tts(jobs, names=("pwsh", "powershell")):
    """一次性把所有旁白合成为 wav（避免反复启动 PowerShell）。"""
    os.makedirs(TMP_DIR, exist_ok=True)
    manifest = []
    for key, text in jobs:
        manifest.append({"wav": os.path.join(TMP_DIR, "tts", key + ".wav"), "text": text})
    os.makedirs(os.path.join(TMP_DIR, "tts"), exist_ok=True)
    mpath = os.path.join(TMP_DIR, "tts_manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False)

    script = PS_TTS.replace("{manifest}", mpath.replace("\\", "\\\\"))
    spath = os.path.join(TMP_DIR, "tts.ps1")
    with open(spath, "w", encoding="utf-8-sig") as f:
        f.write(script)

    for exe in names:
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", spath],
                capture_output=True, text=True, timeout=3600,
            )
            if r.returncode == 0:
                print("[tts]", (r.stdout or "").strip())
                return True
        except FileNotFoundError:
            continue
        except Exception as e:
            print("[tts] failed:", e)
    return False


def wav_info(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def wav_frames(path):
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == CHANNELS, path
        assert w.getsampwidth() == SAMPWIDTH, path
        assert w.getframerate() == SAMPLE_RATE, path
        return w.readframes(w.getnframes())


SILENCE = b"\x00\x00" * 1024


def silence(seconds):
    n = int(seconds * SAMPLE_RATE)
    return b"\x00\x00" * max(0, n)


# ------------------------------------------------------------------ 时间轴
MIN_DUR = {"cover": 4.2, "bullets": 4.6, "code": 5.2, "term": 4.8, "recap": 4.0}
LEAD, TAIL = 0.30, 0.75


def build_timeline(ls, audio_map):
    """返回 [(page, start, dur, audio_bytes)]"""
    pages = lesson_pages(ls)
    items = []
    for pi, page in enumerate(pages):
        key = f"{ls['id']}_p{pi}"
        path = os.path.join(TMP_DIR, "tts", key + ".wav")
        adur = 0.0
        raw = b""
        if os.path.exists(path):
            try:
                adur = wav_info(path)
                raw = wav_frames(path)
            except Exception as e:
                print(f"  ! wav 读取失败 {key}: {e}")
        kind = page.get("kind", "bullets")
        min_d = MIN_DUR.get(kind, 4.0)
        if kind == "code":
            chars = len(page.get("code", ""))
            min_d = max(min_d, chars / 42.0 + 1.6)
        dur = max(min_d, adur + LEAD + TAIL)
        dur = round(dur * FPS) / FPS  # 对齐到帧
        items.append({
            "page": page, "dur": dur,
            "audio": silence(LEAD) + raw + silence(max(0.0, dur - LEAD - adur)),
        })
    return items


# ------------------------------------------------------------------ 渲染
def render_lesson(args):
    ch, idx, ls, only_audio = args
    t0 = time.time()
    lid = ls["id"]
    items = build_timeline(ls, None)
    total = sum(it["dur"] for it in items)
    nframes = int(round(total * FPS))

    ctx = {
        "chapter": ch["title"],
        "course_title": "C++ 系统课程",
        "lesson_title": ls["title"],
        "lesson_index": idx,
        "minutes": ls.get("minutes", 5),
        "page": None,
    }

    # 帧边界
    bounds = []
    acc = 0.0
    for it in items:
        bounds.append((acc, acc + it["dur"]))
        acc += it["dur"]

    os.makedirs(VIDEO_DIR, exist_ok=True)
    silent_mp4 = os.path.join(TMP_DIR, f"{lid}_video.mp4")
    final_mp4 = os.path.join(VIDEO_DIR, f"{lid}.mp4")

    cmd = [
        find_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        silent_mp4,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=W * H * 3)
    try:
        for fi in range(nframes):
            t_global = fi / FPS
            pi = 0
            for i, (s, e) in enumerate(bounds):
                if t_global < e or i == len(bounds) - 1:
                    pi = i
                    break
            t_local = t_global - bounds[pi][0]
            ctx["page"] = items[pi]["page"]
            img = engine.render_frame(ctx, t_local, items[pi]["dur"],
                                     t_global / total, pi + 1, len(items))
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"{lid} 视频编码失败")

    # 音轨
    wav_path = os.path.join(TMP_DIR, f"{lid}_audio.wav")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(CHANNELS)
        w.setsampwidth(SAMPWIDTH)
        w.setframerate(SAMPLE_RATE)
        for it in items:
            w.writeframes(it["audio"])

    # 封装
    cmd2 = [
        find_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", silent_mp4, "-i", wav_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", final_mp4,
    ]
    subprocess.run(cmd2, check=True)

    # 字幕
    vtt_path = os.path.join(DATA_DIR, f"{lid}.vtt")
    write_vtt(vtt_path, items, bounds)

    # 时间轴落盘：这样删掉临时 TTS 也能重新汇总前端数据
    subs = []
    for i, it in enumerate(items):
        s, e = bounds[i]
        text = it["page"].get("narration", "").replace("\n", " ").strip()
        if text:
            subs.append({"s": round(s, 2), "e": round(e, 2), "text": text})
    tl_dir = os.path.join(TMP_DIR, "timeline")
    os.makedirs(tl_dir, exist_ok=True)
    with open(os.path.join(tl_dir, lid + ".json"), "w", encoding="utf-8") as f:
        json.dump({"duration": round(total, 2), "subtitles": subs}, f,
                  ensure_ascii=False)

    # 缩略图：取封面页 1.5 秒处
    thumb = os.path.join(THUMB_DIR, f"{lid}.jpg")
    ctx["page"] = items[0]["page"]
    frame = engine.render_frame(ctx, min(1.5, items[0]["dur"] - 0.1),
                                items[0]["dur"], 0.02, 1, len(items))
    frame.resize((640, 360), Image.LANCZOS).save(thumb, quality=88)

    size_mb = os.path.getsize(final_mp4) / 1048576.0
    return {
        "id": lid, "file": f"videos/{lid}.mp4", "duration": round(total, 2),
        "frames": nframes, "size_mb": round(size_mb, 2),
        "seconds": round(time.time() - t0, 1),
    }


def ts(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def write_vtt(path, items, bounds):
    lines = ["WEBVTT", ""]
    for i, it in enumerate(items):
        s, e = bounds[i]
        text = it["page"].get("narration", "").replace("\n", " ")
        lines.append(f"{ts(s)} --> {ts(e)}")
        lines.append(text)
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------------ 课程数据
def build_course_json(results):
    meta = {r["id"]: r for r in results}
    chapters = []
    for ch in CHAPTERS:
        lessons = []
        for idx, ls in enumerate(ch["lessons"], 1):
            lid = ls["id"]
            m = meta.get(lid, {})
            code_samples = [
                {"title": p.get("title", ""), "code": p.get("code", ""),
                 "output": p.get("output", "")}
                for p in ls["pages"] if p.get("kind") == "code"
            ]
            recap = []
            for p in ls["pages"]:
                if p.get("kind") == "recap":
                    recap = [x if isinstance(x, str) else "：".join(x) for x in p.get("items", [])]
            lessons.append({
                "id": lid,
                "index": idx,
                "title": ls["title"],
                "minutes": ls.get("minutes", 5),
                "tags": ls.get("tags", []),
                "video": m.get("file", f"videos/{lid}.mp4"),
                "vtt": f"data/{lid}.vtt",
                "thumb": f"thumbs/{lid}.jpg",
                "duration": m.get("duration", 0),
                "code": code_samples,
                "recap": recap,
            })
        chapters.append({
            "id": ch["id"], "title": ch["title"], "desc": ch["desc"],
            "lessons": lessons,
        })
    total_dur = sum(r.get("duration", 0) for r in results)
    return {
        "title": "C++ 系统课程",
        "subtitle": "26 节课，从语法基础到现代 C++ 实战",
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration": round(total_dur, 1),
        "total_lessons": sum(len(c["lessons"]) for c in chapters),
        "chapters": chapters,
    }


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="逗号分隔的课时 id")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--skip-tts", action="store_true")
    ap.add_argument("--skip-render", action="store_true")
    args = ap.parse_args()

    only = set(x.strip() for x in args.only.split(",") if x.strip()) or None
    for d in (VIDEO_DIR, DATA_DIR, TMP_DIR, THUMB_DIR):
        os.makedirs(d, exist_ok=True)

    lessons = all_lessons()
    print(f"共 {len(lessons)} 个课时")

    if not args.skip_tts:
        jobs = tts_manifest(lessons, only)
        print(f"TTS: {len(jobs)} 段旁白...")
        t1 = time.time()
        if not run_tts(jobs):
            print("TTS 失败，将用静音替代")
        print(f"TTS 完成，用时 {time.time() - t1:.1f}s")

    if args.skip_render:
        return

    targets = [(ch, idx, ls, None) for ch, idx, ls in lessons
               if not only or ls["id"] in only]
    print(f"开始渲染 {len(targets)} 个课时，并行 {args.jobs} 进程...")
    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {ex.submit(render_lesson, t): t[2]["id"] for t in targets}
        for fu in as_completed(futs):
            lid = futs[fu]
            try:
                r = fu.result()
                results.append(r)
                print(f"  [OK] {lid}  {r['duration']:>6.1f}s  {r['size_mb']:>5.1f}MB  "
                      f"渲染 {r['seconds']}s")
            except Exception as e:
                print(f"  [FAIL] {lid}: {e}")

    results.sort(key=lambda r: r["id"])
    course = build_course_json(results)
    with open(os.path.join(DATA_DIR, "course.json"), "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=1)

    total = sum(r["duration"] for r in results)
    print(f"\n完成：{len(results)} 课时，总时长 {total/60:.1f} 分钟，"
          f"用时 {(time.time()-t0)/60:.1f} 分钟")
    print(f"数据：{os.path.join(DATA_DIR, 'course.json')}")


if __name__ == "__main__":
    main()
