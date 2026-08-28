#!/usr/bin/env python3
"""
🌌 Garchy OS — Format-Aware Cephalon AI File & Directory Inspector
Extracts accurate metadata for archives (.7z, .zip, .tar), audio/video (ffprobe),
images (Pillow), text/code, and binaries, providing grounded, non-hallucinated AI diagnostics.
"""

import os
import sys
import json
import time
import subprocess
import mimetypes
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gally_ai_router
import gally_memory_manager

CYAN = "\033[1;36m"
GOLD = "\033[1;33m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
PURPLE = "\033[1;35m"
WHITE = "\033[1;37m"
SLATE = "\033[0;90m"
RESET = "\033[0m"

ARCHIVE_EXTS = {".7z", ".zip", ".tar", ".gz", ".zst", ".bz2", ".xz", ".rar", ".tgz", ".tbz2", ".tar.zst"}
MEDIA_AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus", ".wma"}
MEDIA_VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp", ".ico", ".tiff"}

def print_header():
    print(f"\n{CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║ {GOLD}🤖 CEPHALON AI — FORMAT-AWARE FILE INSPECTOR & DIAGNOSTICS{CYAN}                   ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{RESET}\n")

def get_file_info(target_path):
    if not os.path.exists(target_path):
        return None, "File or directory does not exist."
    
    st = os.stat(target_path)
    is_dir = os.path.isdir(target_path)
    size_str = ""
    
    if is_dir:
        try:
            out = subprocess.check_output(["du", "-sh", target_path], stderr=subprocess.DEVNULL).decode().split()[0]
            size_str = out
        except Exception:
            size_str = "Unknown"
        file_count = sum([len(files) for r, d, files in os.walk(target_path)])
        dir_count = sum([len(d) for r, d, files in os.walk(target_path)])
        file_type = f"Directory ({file_count} files, {dir_count} subfolders)"
    else:
        size_bytes = st.st_size
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes / (1024*1024):.2f} MB"
        
        try:
            mime_out = subprocess.check_output(["file", "-b", target_path], stderr=subprocess.DEVNULL).decode().strip()
            file_type = mime_out
        except Exception:
            file_type = mimetypes.guess_type(target_path)[0] or "Unknown Binary/Data"

    info = {
        "path": os.path.abspath(target_path),
        "name": os.path.basename(target_path) or target_path,
        "is_dir": is_dir,
        "size": size_str,
        "type": file_type,
        "perms": oct(st.st_mode)[-3:],
    }
    return info, None

def inspect_content(target_path, is_dir):
    """
    Intelligently extracts readable structure and metadata based on exact file format.
    """
    if is_dir:
        try:
            out = subprocess.check_output(["ls", "-lah", target_path], stderr=subprocess.DEVNULL).decode()
            return "directory", f"Directory Listing:\n{out[:4000]}"
        except Exception as e:
            return "directory", f"Directory listing error: {e}"

    _, ext = os.path.splitext(target_path.lower())
    full_lower = target_path.lower()

    # 1. Archives (.7z, .zip, .tar, .tar.zst, .gz, etc.)
    if ext in ARCHIVE_EXTS or full_lower.endswith(".7z") or full_lower.endswith(".tar.zst") or full_lower.endswith(".tar.gz"):
        try:
            out = subprocess.check_output(["7z", "l", target_path], stderr=subprocess.DEVNULL).decode(errors="replace")
            return "archive", f"7-Zip Archive Manifest & File Listing:\n{out[:6000]}"
        except Exception:
            try:
                out = subprocess.check_output(["tar", "-tf", target_path], stderr=subprocess.DEVNULL).decode(errors="replace")
                return "archive", f"TAR Archive File Listing:\n{out[:6000]}"
            except Exception as e:
                return "archive", f"Archive read error: {e}"

    # 2. Audio & Video Files
    if ext in MEDIA_AUDIO_EXTS or ext in MEDIA_VIDEO_EXTS:
        try:
            out = subprocess.check_output(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", target_path],
                stderr=subprocess.DEVNULL
            ).decode(errors="replace")
            meta = json.loads(out)
            fmt = meta.get("format", {})
            tags = fmt.get("tags", {})
            streams = meta.get("streams", [])
            
            stream_info = []
            for s in streams:
                codec_type = s.get("codec_type")
                codec = s.get("codec_name")
                if codec_type == "audio":
                    rate = s.get("sample_rate")
                    channels = s.get("channels")
                    stream_info.append(f"Audio Stream: {codec} ({channels} channels, {rate} Hz)")
                elif codec_type == "video":
                    w = s.get("width")
                    h = s.get("height")
                    fps = s.get("r_frame_rate")
                    stream_info.append(f"Video Stream: {codec} ({w}x{h} @ {fps} fps)")

            duration_secs = float(fmt.get("duration", 0))
            mins = int(duration_secs // 60)
            secs = int(duration_secs % 60)
            bitrate = int(fmt.get("bit_rate", 0)) // 1000 if fmt.get("bit_rate") else "Unknown"

            res = f"""Media Metadata (ffprobe):
• Format: {fmt.get('format_long_name', ext[1:].upper())}
• Duration: {mins}m {secs}s ({duration_secs:.2f} seconds)
• Overall Bitrate: {bitrate} kbps
• Streams: {', '.join(stream_info)}
• Tags/ID3:
  - Title: {tags.get('title', tags.get('TITLE', 'N/A'))}
  - Artist: {tags.get('artist', tags.get('ARTIST', 'N/A'))}
  - Album: {tags.get('album', tags.get('ALBUM', 'N/A'))}
  - Date/Year: {tags.get('date', tags.get('DATE', 'N/A'))}
  - Genre: {tags.get('genre', tags.get('GENRE', 'N/A'))}
"""
            return "media", res
        except Exception as e:
            return "media", f"Multimedia inspection: {e}"

    # 3. Images
    if ext in IMAGE_EXTS:
        try:
            with Image.open(target_path) as img:
                res = f"""Image Metadata (Pillow):
• Dimensions: {img.width} x {img.height} pixels
• Format: {img.format}
• Color Mode: {img.mode}
• Animated/Frames: {getattr(img, 'n_frames', 1)}
"""
                return "image", res
        except Exception as e:
            return "image", f"Image inspection: {e}"

    # 4. Text / Source Code / Config Files
    try:
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(180)]
            content = "".join([l for l in lines if l])
            # Verify it's not binary
            if "\x00" in content:
                return "binary", "[Binary executable or data file — no plain text preview available]"
            if len(lines) >= 180:
                content += "\n... [Truncated at 180 lines] ..."
            return "text", content
    except Exception as e:
        return "binary", f"[Binary or Non-UTF8 file data]: {e}"

def query_ai_streaming(prompt_text, cfg):
    sys_inst = gally_memory_manager.get_mode_system_instruction(
        mode=cfg.get("mode", "normal"),
        internet_ok=cfg.get("internet_permitted", True),
        doc_ok=cfg.get("document_access_permitted", True)
    )

    full_chunks = []
    def on_token(t):
        print(t, end="", flush=True)
        full_chunks.append(t)

    def on_complete(resp):
        print("\n")

    gally_ai_router.stream_query(
        prompt=prompt_text,
        config=cfg,
        token_callback=on_token,
        complete_callback=on_complete,
        system_instruction=sys_inst
    )
    return "".join(full_chunks)

def main():
    if len(sys.argv) < 2:
        print(f"{RED}Error: No file or directory path specified.{RESET}")
        print(f"Usage: python3 gally_inspect_file.py <path>")
        sys.exit(1)

    target_path = sys.argv[1]
    print_header()

    info, err = get_file_info(target_path)
    if err:
        print(f"{RED}❌ Error: {err}{RESET}")
        sys.exit(1)

    print(f"{WHITE}📄 Target:{RESET}     {CYAN}{info['name']}{RESET}")
    print(f"{WHITE}📂 Full Path:{RESET}  {SLATE}{info['path']}{RESET}")
    print(f"{WHITE}📦 Type:{RESET}       {GOLD}{info['type']}{RESET}")
    print(f"{WHITE}⚖️  Size:{RESET}       {GREEN}{info['size']}{RESET}  |  {WHITE}Permissions:{RESET} {SLATE}{info['perms']}{RESET}")
    print(f"{CYAN}────────────────────────────────────────────────────────────────────────────────{RESET}\n")

    category, content_data = inspect_content(info['path'], info['is_dir'])

    prompt = f"""Operator asked you to inspect and explain this file/folder:
- Name: {info['name']}
- Full Path: {info['path']}
- Size: {info['size']}
- Detected Format Category: {category}
- MIME / File Type: {info['type']}

--- EXTRACTED FILE DATA & MANIFEST ---
{content_data[:6000]}
-------------------------------------

As Cephalon Gally:
1. Explain accurately what this file/folder is, its true contents based on the manifest above, and what it is used for.
2. Break down the key contents (e.g. tracks/files inside archive, code functions, image specs, or media tags).
3. Provide practical guidance on how the Operator can open, extract, play, run, or edit this in Garchy OS.
Do NOT guess or hallucinate that it is Cephalon AI's own configuration. Stick strictly to the extracted manifest and data.
"""

    cfg = gally_ai_router.load_ai_config()
    active_mod = cfg.get("active_model", "gally-cephalon-ai")
    print(f"{GOLD}◈ CEPHALON GALLY [{active_mod.upper()}]: Analyzing neural matrices...{RESET}\n")

    try:
        query_ai_streaming(prompt, cfg)
    except Exception as e:
        print(f"{RED}❌ Analysis streaming error: {e}{RESET}")

    # Interactive Follow-up Loop
    print(f"{CYAN}────────────────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{GOLD}💡 You can ask follow-up questions about this file below, or press Enter to exit:{RESET}")
    
    while True:
        try:
            query = input(f"\n{CYAN}◈ OPERATOR [{info['name']}]: {RESET}").strip()
            if not query:
                break
            if query.lower() in ["exit", "quit", "q"]:
                break

            followup_prompt = f"File Context: {info['path']} ({info['name']})\nCategory: {category}\nData:\n{content_data[:3000]}\n\nOperator asked: {query}"
            print(f"\n{GOLD}◈ CEPHALON GALLY:{RESET} ")
            query_ai_streaming(followup_prompt, cfg)
        except (KeyboardInterrupt, EOFError):
            break

    print(f"\n{SLATE}Session closed. Cephalon standing by.{RESET}")

if __name__ == "__main__":
    main()
