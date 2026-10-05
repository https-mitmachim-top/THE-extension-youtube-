#!/usr/bin/env python3
"""
Universal media downloader - interactive CLI wrapper around yt-dlp, ffmpeg,
ffprobe and aria2c.

Flow:
  1. Ask for a URL, detect the source site.
  2. If it's a YouTube *channel* link, ask whether to grab only Shorts, only
     regular uploads, or both (a YouTube playlist or single video skips this).
  3. Regardless of site, ask whether to download audio, video, or just the
     thumbnail/cover image.
  4. Ask the format/resolution questions specific to that choice and download.

Requires yt-dlp, ffmpeg, ffprobe and aria2c to already be installed and
reachable on PATH.
"""

import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

REQUIRED_TOOLS = ["yt-dlp", "ffmpeg", "ffprobe", "aria2c"]

# Words that mean "give me the best/maximum available" in either language.
BEST_WORDS = {
    "best", "max", "maximum", "highest",
    "מקסימלי", "מקסימלית", "מקסימום", "מירבי", "מירבית",
    "הכי טוב", "הכי טובה", "הכי גבוה", "הכי גבוהה",
}

# yt-dlp's own supported values for --audio-format ("best" handled separately).
VALID_AUDIO_FORMATS = {"aac", "alac", "flac", "m4a", "mp3", "opus", "vorbis", "wav"}

# Sensible video containers out of yt-dlp's --remux-video/--recode-video list
# (the full list also includes audio-only containers like mp3/wav, which
# don't make sense as a "video format" answer here).
VALID_VIDEO_FORMATS = {"avi", "flv", "gif", "mkv", "mov", "mp4", "webm"}

# Set to True only if you've confirmed (e.g. via `yt-dlp --no-check-certificate
# -j URL` in a terminal) that SSL errors here are caused by local antivirus /
# proxy software intercepting HTTPS traffic, and you accept the tradeoff of
# skipping certificate verification entirely. Prefer fixing the real cause
# (e.g. `pip install pip_system_certs`, or excluding python/yt-dlp from your
# antivirus's HTTPS scanning) over leaving this on permanently.
DISABLE_SSL_VERIFY = False

# aria2c is used as yt-dlp's external downloader for multi-connection speed.
ARIA2_ARGS = "aria2c:-x 16 -s 16 -k 1M"

SITE_PATTERNS = {
    "youtube": r"(youtube\.com|youtu\.be)",
    "tiktok": r"tiktok\.com",
    "instagram": r"instagram\.com",
    "twitter/x": r"(twitter\.com|x\.com)",
    "facebook": r"(facebook\.com|fb\.watch)",
    "vimeo": r"vimeo\.com",
}

CHANNEL_TAB_SUFFIXES = [
    "/videos", "/shorts", "/streams", "/playlists", "/community", "/about", "/featured",
]


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def check_dependencies():
    missing = [t for t in REQUIRED_TOOLS if shutil.which(t) is None]
    if missing:
        print("חסרים הכלים הבאים במערכת: " + ", ".join(missing))
        print("יש להתקין אותם ולוודא שהם נגישים דרך PATH.")
        sys.exit(1)


def run(cmd):
    """Run a command, letting it print live to the terminal. Raise on failure."""
    print("\n$ " + " ".join(shlex.quote(c) for c in cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"הפקודה נכשלה (קוד יציאה {result.returncode}): {cmd[0]}")


def ask_text(prompt):
    return input(prompt).strip()


def ask_choice(prompt, options):
    """options: mapping of key -> label, e.g. {'1': 'אודיו', '2': 'וידאו'}."""
    print("\n" + prompt)
    for key, label in options.items():
        print(f"  {key}. {label}")
    while True:
        choice = input("בחירה: ").strip()
        if choice in options:
            return choice
        print("בחירה לא תקינה, נסה שוב.")


def normalize_choice(text):
    return text.strip().lower()


def ask_format(prompt, valid_formats):
    """Ask for a format, accepting any case, re-prompting until it's a
    recognized value or a 'best' synonym. Returns the normalized lowercase
    format string, or 'best'."""
    while True:
        text = ask_text(prompt)
        norm = normalize_choice(text)
        if norm in BEST_WORDS:
            return "best"
        if norm in valid_formats:
            return norm
        print(
            "פורמט לא נתמך. אפשרויות: "
            + ", ".join(sorted(valid_formats))
            + ", best"
        )


def sanitize_filename(name):
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = name.strip().strip(".")
    return name[:150] or "file"


# --------------------------------------------------------------------------- #
# Site / URL classification
# --------------------------------------------------------------------------- #

def detect_site(url):
    for name, pattern in SITE_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return name
    return "other"


def classify_youtube_url(url):
    """Returns 'channel', 'playlist' or 'video'."""
    u = url.split("#")[0]

    # Check single-video shapes FIRST (even a watch?v=...&list=... URL is
    # treated as "just this video", matching how most people expect a pasted
    # video link to behave - yt-dlp's own default would otherwise silently
    # grab the whole playlist).
    is_single_video = bool(
        re.search(r"[?&]v=[A-Za-z0-9_-]{6,}", u)
        or re.search(r"youtu\.be/[A-Za-z0-9_-]{6,}", u)
        or re.search(r"youtube\.com/shorts/[A-Za-z0-9_-]{6,}", u)
        or re.search(r"youtube\.com/live/[A-Za-z0-9_-]{6,}", u)
        or re.search(r"youtube\.com/embed/[A-Za-z0-9_-]{6,}", u)
    )
    if is_single_video:
        return "video"

    if "/playlist" in u or re.search(r"[?&]list=", u):
        return "playlist"

    if re.search(r"youtube\.com/(channel/|c/|@|user/)", u, re.IGNORECASE):
        return "channel"

    return "video"


def get_channel_base_url(url):
    base = url.split("?")[0].rstrip("/")
    for suffix in CHANNEL_TAB_SUFFIXES:
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base


# --------------------------------------------------------------------------- #
# Resolution parsing
# --------------------------------------------------------------------------- #

def parse_resolution_input(text):
    norm = normalize_choice(text)
    if norm in BEST_WORDS:
        return {"mode": "best"}
    m = re.match(r"^(\d+)\s*[x×]\s*(\d+)$", norm)
    if m:
        return {"mode": "exact", "width": int(m.group(1)), "height": int(m.group(2))}
    m2 = re.match(r"^(\d+)\s*p?$", norm)
    if m2:
        return {"mode": "height", "height": int(m2.group(1))}
    print("לא זוהתה רזולוציה תקינה - משתמש בברירת מחדל: הרזולוציה המקסימלית.")
    return {"mode": "best"}


# --------------------------------------------------------------------------- #
# ffprobe / ffmpeg / aria2c helpers
# --------------------------------------------------------------------------- #

def probe_file(path):
    """Return a short human-readable summary of a media file using ffprobe."""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
    except Exception:
        return ""
    fmt = data.get("format", {})
    parts = []
    dur = fmt.get("duration")
    if dur:
        try:
            parts.append(f"{float(dur):.1f} שנ'")
        except ValueError:
            pass
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and s.get("width"):
            parts.append(f"{s['width']}x{s.get('height', '?')} ({s.get('codec_name', '')})")
        elif s.get("codec_type") == "audio":
            parts.append(f"{s.get('codec_name', '')} {s.get('sample_rate', '')}Hz")
    size = fmt.get("size")
    if size:
        try:
            parts.append(f"{int(size) / 1024 / 1024:.1f}MB")
        except ValueError:
            pass
    return " | ".join(str(p) for p in parts if p)


def download_file_aria2c(url, out_path):
    directory = os.path.dirname(os.path.abspath(out_path)) or "."
    filename = os.path.basename(out_path)
    os.makedirs(directory, exist_ok=True)
    cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "-d", directory, "-o", filename, url]
    run(cmd)


def resize_image(path, width, height):
    if width and height:
        vf = f"scale={width}:{height}"
    elif height:
        vf = f"scale=-2:{height}"
    elif width:
        vf = f"scale={width}:-2"
    else:
        return
    tmp = path + ".tmp.jpg"
    run(["ffmpeg", "-y", "-i", path, "-vf", vf, tmp])
    os.replace(tmp, path)


def embed_cover_ffmpeg(audio_path, image_path, out_path):
    ext = os.path.splitext(out_path)[1].lower()
    if ext == ".wav":
        print("פורמט WAV אינו תומך בהטמעת תמונת עטיפה - הקובץ יישמר ללא תמונה.")
        return False
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-i", image_path, "-map", "0", "-map", "1", "-c", "copy"]
    if ext == ".mp3":
        cmd += ["-id3v2_version", "3"]
    cmd += [
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        "-disposition:v", "attached_pic",
        out_path,
    ]
    run(cmd)
    return True


def pick_thumbnail(thumbnails, res):
    valid = [t for t in thumbnails if t.get("width") and t.get("height")]
    if not valid:
        return thumbnails[-1] if thumbnails else None
    if res["mode"] == "exact":
        target_area = res["width"] * res["height"]
        return min(valid, key=lambda t: abs(t["width"] * t["height"] - target_area))
    if res["mode"] == "height":
        return min(valid, key=lambda t: abs(t["height"] - res["height"]))
    return max(valid, key=lambda t: t["width"] * t["height"])


def get_video_info_json(url, no_playlist=False):
    cmd = ["yt-dlp", "-j", "--no-warnings", "--ignore-errors"]
    if no_playlist:
        cmd.append("--no-playlist")
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True)
    items = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not items and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "לא ניתן היה לשלוף מידע על הסרטון")
    return items


def find_recent_info_jsons(since_ts):
    files = glob.glob(os.path.join("**", "*.info.json"), recursive=True)
    return [f for f in files if os.path.getmtime(f) >= since_ts - 2]


def find_media_file_for_stem(stem):
    for candidate in glob.glob(stem + ".*"):
        if not candidate.endswith((".info.json", ".jpg", ".jpeg", ".png", ".webp", ".part", ".tmp")):
            return candidate
    return None


def apply_custom_cover(info_path, cover_res):
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    stem = info_path[: -len(".info.json")]
    audio_path = find_media_file_for_stem(stem)
    thumbnails = info.get("thumbnails", [])
    title = info.get("title", os.path.basename(stem))

    if not audio_path or not thumbnails:
        print(f"לא נמצאה תמונת עטיפה זמינה עבור: {title}")
        os.remove(info_path)
        return

    thumb = pick_thumbnail(thumbnails, cover_res)
    cover_path = stem + "_cover.jpg"
    download_file_aria2c(thumb["url"], cover_path)
    if cover_res["mode"] != "best":
        resize_image(cover_path, cover_res.get("width"), cover_res.get("height"))

    ext = os.path.splitext(audio_path)[1]
    tmp_out = stem + "_with_cover" + ext
    if embed_cover_ffmpeg(audio_path, cover_path, tmp_out):
        os.replace(tmp_out, audio_path)
        print(f"תמונת עטיפה הוטמעה: {title}  {probe_file(audio_path)}")

    if os.path.exists(cover_path):
        os.remove(cover_path)
    os.remove(info_path)


# --------------------------------------------------------------------------- #
# Download orchestrators
# --------------------------------------------------------------------------- #

def download_audio(url, fmt, embed_cover, cover_res, bulk, restrict_single):
    fmt_norm = normalize_choice(fmt)
    if fmt_norm in BEST_WORDS:
        fmt_norm = "best"

    custom_cover = embed_cover and cover_res and cover_res["mode"] != "best"

    cmd = [
        "yt-dlp", "-f", "bestaudio/best",
        "--no-warnings",
        "--external-downloader", "aria2c",
        "--external-downloader-args", ARIA2_ARGS,
        "-x", "--audio-format", fmt_norm, "--audio-quality", "0",
    ]
    if restrict_single:
        cmd.append("--no-playlist")
    if bulk:
        cmd += ["--ignore-errors", "--download-archive", "downloaded_archive.txt",
                "-o", "%(uploader)s/%(title)s.%(ext)s"]

    if embed_cover and not custom_cover:
        cmd += ["--embed-thumbnail", "--convert-thumbnails", "jpg"]
    elif custom_cover:
        cmd += ["--write-info-json"]

    cmd.append(url)

    start_ts = time.time()
    run(cmd)

    if custom_cover:
        for info_path in find_recent_info_jsons(start_ts):
            try:
                apply_custom_cover(info_path, cover_res)
            except Exception as e:
                print(f"שגיאה בהטמעת תמונת עטיפה: {e}")


def build_format_selector(res):
    if res["mode"] == "best":
        return "bestvideo+bestaudio/best"
    h = res["height"]
    return f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"


def download_video(url, res, fmt, bulk, restrict_single):
    fmt_norm = normalize_choice(fmt)
    use_best_fmt = fmt_norm in BEST_WORDS

    cmd = [
        "yt-dlp", "-f", build_format_selector(res),
        "--no-warnings",
        "--external-downloader", "aria2c",
        "--external-downloader-args", ARIA2_ARGS,
    ]
    if not use_best_fmt:
        # merge-output-format picks the container for the initial merge;
        # recode-video guarantees the *final* file matches it even if the
        # source codec wouldn't otherwise fit that container.
        cmd += ["--merge-output-format", fmt_norm, "--recode-video", fmt_norm]
    if restrict_single:
        cmd.append("--no-playlist")
    if bulk:
        cmd += ["--ignore-errors", "--download-archive", "downloaded_archive.txt",
                "-o", "%(uploader)s/%(title)s.%(ext)s"]
    cmd.append(url)
    run(cmd)


def download_thumbnail_only(url, res, bulk, restrict_single):
    if bulk:
        print("שים לב: שליפת תמונות עבור ערוץ/פלייליסט שלם עשויה לקחת זמן.")
    items = get_video_info_json(url, no_playlist=restrict_single)
    if not items:
        print("לא נמצא מידע על הסרטון/ים.")
        return
    for item in items:
        thumbnails = item.get("thumbnails", [])
        title = item.get("title", "thumbnail")
        if not thumbnails:
            print(f"לא נמצאה תמונה עבור: {title}")
            continue
        thumb = pick_thumbnail(thumbnails, res)
        folder = sanitize_filename(item.get("uploader", "")) if bulk else ""
        if folder:
            os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, sanitize_filename(title) + ".jpg")
        download_file_aria2c(thumb["url"], out_path)
        if res["mode"] != "best":
            resize_image(out_path, res.get("width"), res.get("height"))
        print(f"הורד: {out_path}  {probe_file(out_path)}")


# --------------------------------------------------------------------------- #
# Main flow
# --------------------------------------------------------------------------- #

def main():
    check_dependencies()
    print("=== מוריד מדיה אוניברסלי (yt-dlp + ffmpeg + ffprobe + aria2c) ===")

    url = ask_text("\nהכנס קישור לסרטון / ערוץ / פלייליסט: ")
    site = detect_site(url)
    print(f"זוהה אתר: {site}")

    targets = [url]
    bulk = False
    restrict_single = False

    if site == "youtube":
        kind = classify_youtube_url(url)
        if kind == "channel":
            choice = ask_choice(
                "הקישור הוא של ערוץ יוטיוב. אילו סרטונים להוריד?",
                {
                    "1": "רק סרטוני שורטס (Shorts)",
                    "2": "רק סרטונים רגילים",
                    "3": "גם שורטס וגם סרטונים רגילים",
                },
            )
            base = get_channel_base_url(url)
            if choice == "1":
                targets = [base + "/shorts"]
            elif choice == "2":
                targets = [base + "/videos"]
            else:
                targets = [base + "/videos", base + "/shorts"]
            bulk = True
        elif kind == "playlist":
            print("זוהה כפלייליסט - יורדו כל הפריטים בו.")
            bulk = True
        else:
            print("זוהה כסרטון בודד.")
            restrict_single = True

    content_choice = ask_choice(
        "מה תרצה להוריד?",
        {"1": "אודיו", "2": "וידאו", "3": "תמונת עטיפה (Thumbnail)"},
    )

    if content_choice == "1":
        embed_choice = ask_choice(
            "האם לכלול תמונת עטיפה מוטבעת בקובץ השמע?",
            {"1": "כן", "2": "לא"},
        )
        embed_cover = embed_choice == "1"
        cover_res = None
        if embed_cover:
            cover_res = parse_resolution_input(
                ask_text("מה הרזולוציה הרצויה לתמונת העטיפה? (למשל 1280x720, או 'best' למקסימלית): ")
            )
        audio_fmt = ask_format(
            "איזה פורמט אודיו? (mp3 / m4a / flac / opus / vorbis / aac / alac / wav / best): ",
            VALID_AUDIO_FORMATS,
        )
        for target in targets:
            download_audio(target, audio_fmt, embed_cover, cover_res, bulk, restrict_single)

    elif content_choice == "2":
        video_res = parse_resolution_input(
            ask_text("מה הרזולוציה הרצויה לווידאו? (למשל 1080, 1920x1080, או 'best' למקסימלית): ")
        )
        video_fmt = ask_format(
            "איזה פורמט וידאו? (mp4 / mkv / webm / avi / mov / flv / gif / best): ",
            VALID_VIDEO_FORMATS,
        )
        for target in targets:
            download_video(target, video_res, video_fmt, bulk, restrict_single)

    else:
        thumb_res = parse_resolution_input(
            ask_text("מה הרזולוציה הרצויה לתמונת העטיפה? (למשל 1280x720, או 'best' למקסימלית): ")
        )
        for target in targets:
            download_thumbnail_only(target, thumb_res, bulk, restrict_single)

    print("\n✔ הושלם.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nהופסק על ידי המשתמש.")
        sys.exit(1)
    except Exception as e:
        print(f"\nשגיאה: {e}")
        sys.exit(1)
