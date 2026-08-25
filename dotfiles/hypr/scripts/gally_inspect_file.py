#!/usr/bin/env python3
"""
🌌 Garchy OS — Cephalon AI File & Directory Inspector
Inspects file metadata, reads contents, checks security, and performs deep streaming AI analysis with interactive follow-up Q&A.
"""

import os
import sys
import json
import time
import subprocess
import mimetypes

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

def print_header():
    print(f"\n{CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║ {GOLD}🤖 CEPHALON AI — DEEP FILE INSPECTOR & DIAGNOSTICS{CYAN}                          ║{RESET}")
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

def read_preview(target_path, is_dir, max_lines=180):
    if is_dir:
        try:
            out = subprocess.check_output(["ls", "-lah", target_path], stderr=subprocess.DEVNULL).decode()
            return f"Directory Listing:\n{out[:4000]}"
        except Exception as e:
            return f"Directory listing error: {e}"
    else:
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join([l for l in lines if l])
                if len(lines) >= max_lines:
                    content += f"\n... [Truncated at {max_lines} lines] ..."
                return content
        except Exception as e:
            return f"[Binary or Non-UTF8 file data]: {e}"

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

    preview = read_preview(info['path'], info['is_dir'])

    prompt = f"""Operator requested deep inspection and analysis of this {'directory' if info['is_dir'] else 'file'}.
Target Path: {info['path']}
File Type: {info['type']}
File Size: {info['size']}

Content Preview:
```
{preview[:6000]}
```

As Cephalon Gally, provide a clear, helpful breakdown:
1. 💡 What is this file/folder and what is its purpose?
2. 🔍 Key structures, important lines, or configuration parameters.
3. ⚠️ Any potential bugs, security concerns, or performance optimizations.
4. 🚀 Practical recommendations for how the Operator can use or edit it.
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

            followup_prompt = f"File Context: {info['path']}\nOperator asked: {query}"
            print(f"\n{GOLD}◈ CEPHALON GALLY:{RESET} ")
            query_ai_streaming(followup_prompt, cfg)
        except (KeyboardInterrupt, EOFError):
            break

    print(f"\n{SLATE}Session closed. Cephalon standing by.{RESET}")

if __name__ == "__main__":
    main()
