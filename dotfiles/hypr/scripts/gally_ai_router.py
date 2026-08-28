#!/usr/bin/env python3
"""
Gally AI Router — Terminal-Native Multi-Provider Inference & Login Engine
Supports in-terminal login, API key management, on-the-fly model switching,
multi-turn conversational memory, and real-time streaming for Local, Gemini, Claude, OpenAI, DeepSeek, and Groq.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")
HISTORY_PATH = os.path.expanduser("~/.config/gally/cephalon_history.json")

DEFAULT_CONFIG = {
    "active_provider": "local_ollama",
    "active_model": "qwen2.5:0.5b",
    "gemini_api_key": "",
    "claude_api_key": "",
    "openai_api_key": "",
    "deepseek_api_key": "",
    "groq_api_key": "",
    "openrouter_api_key": "",
    "voice_enabled": True,
    "voice_name": "en-US-AriaNeural",
    "mode": "normal",
    "internet_permitted": False,
    "document_access_permitted": False
}

AVAILABLE_MODELS = [
    ("⚡ Tier 1: Qwen 2.5 (Fast & Lightweight - Default)", "local_ollama", "qwen2.5:0.5b"),
    ("🌌 Tier 2: Cephalon Gally (Current Matrix)", "local_ollama", "gally-cephalon-ai"),
    ("🚀 Tier 3: Hermes 3 Llama (High-Performing Free Tier)", "local_ollama", "hermes3:8b"),
    ("✨ Google Gemini 1.5 Flash", "gemini", "gemini-1.5-flash"),
    ("✨ Google Gemini 1.5 Pro", "gemini", "gemini-1.5-pro"),
    ("🚀 Claude 3.5 Sonnet", "claude", "claude-3-5-sonnet-20241022"),
    ("🧠 OpenAI GPT-4o", "openai", "gpt-4o"),
    ("🧠 OpenAI GPT-4o Mini", "openai", "gpt-4o-mini"),
    ("🦙 DeepSeek Chat / R1", "deepseek", "deepseek-chat"),
    ("⚡ Groq Llama 3.3 (300 t/s)", "groq", "llama-3.3-70b-versatile")
]

def load_ai_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_ai_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history(history_list):
    try:
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        trimmed = history_list[-100:]
        with open(HISTORY_PATH, "w") as f:
            json.dump(trimmed, f, indent=2)
    except Exception:
        pass

def mask_key(key_str):
    if not key_str or len(key_str) < 8:
        return "[ NOT CONFIGURED ]"
    return f"{key_str[:6]}...{key_str[-4:]}"

def build_chat_history_turns(history_list, max_turns=16):
    """
    Extracts clean (role, content) turns from conversation history.
    Normalizes 'operator' -> 'user', 'cephalon' -> 'assistant'.
    Ensures turns alternate properly without empty texts.
    """
    if not history_list:
        return []
    
    recent = history_list[-max_turns:]
    turns = []
    for item in recent:
        role = item.get("role", "")
        text = item.get("text", "").strip()
        if not text:
            continue
        
        # Skip technical terminal output blocks from multi-turn chat context
        if text.startswith("┌──") or text.startswith("◈ ACTIVE") or text.startswith("◈ CEPHALON SYSTEM STATUS"):
            continue
            
        norm_role = "user" if role in ["operator", "user"] else "assistant"
        
        if turns and turns[-1]["role"] == norm_role:
            turns[-1]["content"] += f"\n{text}"
        else:
            turns.append({"role": norm_role, "content": text})
            
    return turns

def handle_terminal_command(raw_input, config):
    """Interprets in-terminal login, API key commands, and model switching."""
    cmd = raw_input.strip()
    cmd_lower = cmd.lower()
    
    # 1. Login / Keys Overview Help
    if cmd_lower in ["login", "keys", "api", "api-key", "apikey", "auth"]:
        g_key = mask_key(config.get("gemini_api_key"))
        c_key = mask_key(config.get("claude_api_key"))
        o_key = mask_key(config.get("openai_api_key"))
        d_key = mask_key(config.get("deepseek_api_key"))
        q_key = mask_key(config.get("groq_api_key"))
        
        msg = f"""┌─────────────────────────────────────────────────────────────┐
│ 🔑 CEPHALON CLOUD AI LOGIN & API KEY MATRIX                │
├─────────────────────────────────────────────────────────────┤
│ To register or update an API key, type in this terminal:    │
│                                                             │
│   login gemini <YOUR_KEY>                                   │
│   login claude <YOUR_KEY>                                   │
│   login openai <YOUR_KEY>                                   │
│   login deepseek <YOUR_KEY>                                 │
│   login groq <YOUR_KEY>                                     │
│                                                             │
│ CURRENT REGISTERED STATUS:                                  │
│ • Google Gemini: {g_key}
│ • Anthropic Claude: {c_key}
│ • OpenAI GPT-4o: {o_key}
│ • DeepSeek R1: {d_key}
│ • Groq Cloud: {q_key}
│                                                             │
│ Switch models anytime: type 'model <name>' or 'models'      │
└─────────────────────────────────────────────────────────────┘"""
        return True, msg, config

    # 2. Set / Login Key Directive
    parts = cmd.split()
    if (len(parts) >= 3 and parts[0].lower() in ["login", "set"]) or (len(parts) >= 4 and parts[0].lower() == "set" and parts[1].lower() == "key"):
        if parts[0].lower() == "set" and parts[1].lower() == "key":
            provider = parts[2].lower()
            key_val = parts[3].strip()
        else:
            provider = parts[1].lower()
            key_val = parts[2].strip()
            
        key_fields = {
            "gemini": "gemini_api_key",
            "google": "gemini_api_key",
            "claude": "claude_api_key",
            "anthropic": "claude_api_key",
            "openai": "openai_api_key",
            "gpt": "openai_api_key",
            "deepseek": "deepseek_api_key",
            "groq": "groq_api_key"
        }
        
        if provider in key_fields:
            field = key_fields[provider]
            config[field] = key_val
            
            # Automatically activate corresponding model on login
            if "gemini" in provider or "google" in provider:
                config["active_provider"] = "gemini"
                config["active_model"] = "gemini-1.5-flash"
                p_name = "Google Gemini 1.5 Flash"
            elif "claude" in provider or "anthropic" in provider:
                config["active_provider"] = "claude"
                config["active_model"] = "claude-3-5-sonnet-20241022"
                p_name = "Claude 3.5 Sonnet"
            elif "openai" in provider or "gpt" in provider:
                config["active_provider"] = "openai"
                config["active_model"] = "gpt-4o"
                p_name = "OpenAI GPT-4o"
            elif "deepseek" in provider:
                config["active_provider"] = "deepseek"
                config["active_model"] = "deepseek-chat"
                p_name = "DeepSeek Chat / R1"
            elif "groq" in provider:
                config["active_provider"] = "groq"
                config["active_model"] = "llama-3.3-70b-versatile"
                p_name = "Groq Llama 3.3 (300 t/s)"
                
            save_ai_config(config)
            return True, f"◈ Key registered! Switched active neural engine to: [ {p_name} ].", config
        else:
            return True, f"◈ Unknown provider '{provider}'. Supported: gemini, claude, openai, deepseek, groq.", config

    # 3. Model Switcher Directive
    if len(parts) >= 2 and parts[0].lower() in ["model", "use", "switch"]:
        target = parts[1].lower()
        if target in ["qwen", "qwen2.5", "tier1", "low", "default", "fast"]:
            config["active_provider"] = "local_ollama"
            config["active_model"] = "qwen2.5:0.5b"
            save_ai_config(config)
            return True, "◈ Switched to: [ ⚡ Tier 1: Qwen 2.5 (Fast & Lightweight - Default) ].", config

        elif target in ["gally", "cephalon", "tier2", "mid", "current", "local", "offline"]:
            config["active_provider"] = "local_ollama"
            config["active_model"] = "gally-cephalon-ai"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🌌 Tier 2: Cephalon Gally (Current Matrix) ].", config

        elif target in ["hermes", "hermes3", "tier3", "high", "nous"]:
            config["active_provider"] = "local_ollama"
            config["active_model"] = "hermes3:8b"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🚀 Tier 3: Hermes 3 Llama (High-Performing Free Tier) ].", config

        elif target in ["gemini", "flash", "gemini-flash"]:
            if not config.get("gemini_api_key"):
                return True, "◈ [ ! ] Gemini API key missing. Type: login gemini <your_key>", config
            config["active_provider"] = "gemini"
            config["active_model"] = "gemini-1.5-flash"
            save_ai_config(config)
            return True, "◈ Switched to: [ ✨ Google Gemini 1.5 Flash ].", config

        elif target in ["pro", "gemini-pro"]:
            if not config.get("gemini_api_key"):
                return True, "◈ [ ! ] Gemini API key missing. Type: login gemini <your_key>", config
            config["active_provider"] = "gemini"
            config["active_model"] = "gemini-1.5-pro"
            save_ai_config(config)
            return True, "◈ Switched to: [ ✨ Google Gemini 1.5 Pro ].", config

        elif target in ["claude", "sonnet", "anthropic"]:
            if not config.get("claude_api_key"):
                return True, "◈ [ ! ] Claude API key missing. Type: login claude <your_key>", config
            config["active_provider"] = "claude"
            config["active_model"] = "claude-3-5-sonnet-20241022"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🚀 Claude 3.5 Sonnet ].", config

        elif target in ["openai", "gpt", "gpt4", "gpt-4o"]:
            if not config.get("openai_api_key"):
                return True, "◈ [ ! ] OpenAI API key missing. Type: login openai <your_key>", config
            config["active_provider"] = "openai"
            config["active_model"] = "gpt-4o"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🧠 OpenAI GPT-4o ].", config

        elif target in ["mini", "gpt-mini", "gpt-4o-mini"]:
            if not config.get("openai_api_key"):
                return True, "◈ [ ! ] OpenAI API key missing. Type: login openai <your_key>", config
            config["active_provider"] = "openai"
            config["active_model"] = "gpt-4o-mini"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🧠 OpenAI GPT-4o Mini ].", config

        elif target in ["deepseek", "r1"]:
            if not config.get("deepseek_api_key"):
                return True, "◈ [ ! ] DeepSeek API key missing. Type: login deepseek <your_key>", config
            config["active_provider"] = "deepseek"
            config["active_model"] = "deepseek-chat"
            save_ai_config(config)
            return True, "◈ Switched to: [ 🦙 DeepSeek Chat / R1 ].", config

        elif target in ["groq", "llama"]:
            if not config.get("groq_api_key"):
                return True, "◈ [ ! ] Groq API key missing. Type: login groq <your_key>", config
            config["active_provider"] = "groq"
            config["active_model"] = "llama-3.3-70b-versatile"
            save_ai_config(config)
            return True, "◈ Switched to: [ ⚡ Groq Llama 3.3 (300 t/s) ].", config

    # 4. List Models
    if cmd_lower in ["models", "list models", "show models"]:
        cur = config.get("active_model")
        msg = "◈ AVAILABLE NEURAL ENGINES:\n"
        for (name, _, m_id) in AVAILABLE_MODELS:
            marker = " [ACTIVE ★]" if m_id == cur else ""
            msg += f"  • {name}{marker}\n"
        msg += "\nType 'model <name>' to switch (e.g. 'model local', 'model gemini', 'model claude')."
        return True, msg, config

    # 5. Mode Switcher Directive
    if len(parts) >= 2 and parts[0].lower() == "mode":
        target_mode = parts[1].lower()
        if target_mode in ["non_adult", "non-adult", "child", "junior", "teen", "teenager", "preteen"]:
            config["mode"] = "non_adult"
            save_ai_config(config)
            return True, "◈ Switched Operation Persona to: [ 🌱 NON-ADULT MODE (Ages 10-16) ].", config
        elif target_mode in ["normal", "standard", "default", "adult"]:
            config["mode"] = "normal"
            save_ai_config(config)
            return True, "◈ Switched Operation Persona to: [ 🚀 NORMAL MODE (Ages 16+) ].", config
        elif target_mode in ["sudo", "professional", "professional_sudo", "admin", "sysadmin"]:
            config["mode"] = "professional_sudo"
            save_ai_config(config)
            return True, "◈ Switched Operation Persona to: [ ⚡ PROFESSIONAL SUDO MODE ].", config
        else:
            return True, f"◈ Unknown mode '{target_mode}'. Options: 'mode non-adult' (10-16), 'mode normal' (16+), 'mode sudo'.", config

    # 6. General Status
    if cmd_lower in ["status", "info"]:
        cur_p = config.get("active_provider", "local_ollama").upper()
        cur_m = config.get("active_model", "gally-cephalon-ai")
        mode = config.get("mode", "normal").upper()
        mode_label = "NON-ADULT (Ages 10-16)" if mode in ["NON_ADULT", "CHILD"] else ("NORMAL (Ages 16+)" if mode == "NORMAL" else "PROFESSIONAL SUDO")
        msg = f"""◈ CEPHALON SYSTEM STATUS:
  • Active Engine: {cur_p} ({cur_m})
  • Operation Persona: [{mode_label}]
  • Internet Sandbox: {'ALLOWED 🔓' if config.get('internet_permitted') else 'RESTRICTED 🔒'}
  • User Documents: {'PERMITTED 📂' if config.get('document_access_permitted') else 'PROTECTED 🛡️'}
  • Voice Synthesis: {'ON 🔊' if config.get('voice_enabled') else 'OFF 🔇'}"""
        return True, msg, config

    return False, None, config

def stream_query(prompt, config, token_callback, complete_callback, history_messages=None, system_instruction=None):
    """
    Routes query to selected provider with live streaming and multi-turn conversational memory.
    """
    provider = config.get("active_provider", "local_ollama")
    model = config.get("active_model", "gally-cephalon-ai")
    
    if system_instruction is None:
        import gally_memory_manager
        system_instruction = gally_memory_manager.get_mode_system_instruction(
            config.get("mode", "normal"),
            config.get("internet_permitted", False),
            config.get("document_access_permitted", False)
        )
    
    turns = build_chat_history_turns(history_messages, max_turns=16)
    
    collected_tokens = []
    
    try:
        if provider == "local_ollama":
            # Build messages array for Ollama /api/chat
            chat_messages = [{"role": "system", "content": system_instruction}]
            for t in turns:
                chat_messages.append({"role": t["role"], "content": t["content"]})
            if not chat_messages or chat_messages[-1]["content"] != prompt:
                chat_messages.append({"role": "user", "content": prompt})

            url = "http://127.0.0.1:11434/api/chat"
            payload = json.dumps({"model": model, "messages": chat_messages, "stream": True}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    for line in resp:
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            t = data.get("message", {}).get("content", "")
                            if t:
                                collected_tokens.append(t)
                                token_callback(t)
            except Exception:
                # Fallback to /api/generate if /api/chat is not available
                url = "http://127.0.0.1:11434/api/generate"
                dialog_text = f"{system_instruction}\n\n"
                for t in turns:
                    prefix = "Operator" if t["role"] == "user" else "Cephalon Gally"
                    dialog_text += f"{prefix}: {t['content']}\n"
                if not dialog_text.endswith(f"Operator: {prompt}\n"):
                    dialog_text += f"Operator: {prompt}\nCephalon Gally:"
                payload = json.dumps({"model": model, "prompt": dialog_text, "stream": True}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    for line in resp:
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            t = data.get("response", "")
                            if t:
                                collected_tokens.append(t)
                                token_callback(t)

        elif provider == "gemini":
            api_key = config.get("gemini_api_key", "").strip()
            if not api_key:
                raise ValueError("Google Gemini API Key is missing. Type in terminal: login gemini <YOUR_KEY>")
            
            gemini_contents = []
            for t in turns:
                g_role = "user" if t["role"] == "user" else "model"
                gemini_contents.append({"role": g_role, "parts": [{"text": t["content"]}]})
            if not gemini_contents or gemini_contents[-1]["parts"][0]["text"] != prompt:
                gemini_contents.append({"role": "user", "parts": [{"text": prompt}]})

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
            payload = json.dumps({
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                },
                "contents": gemini_contents
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data = json.loads(line_str[6:])
                        for cand in data.get("candidates", []):
                            for part in cand.get("content", {}).get("parts", []):
                                t = part.get("text", "")
                                if t:
                                    collected_tokens.append(t)
                                    token_callback(t)

        elif provider in ["openai", "deepseek", "groq"]:
            if provider == "openai":
                api_key = config.get("openai_api_key", "").strip()
                url = "https://api.openai.com/v1/chat/completions"
                name = "OpenAI"
            elif provider == "deepseek":
                api_key = config.get("deepseek_api_key", "").strip()
                url = "https://api.deepseek.com/v1/chat/completions"
                name = "DeepSeek"
            else: # groq
                api_key = config.get("groq_api_key", "").strip()
                url = "https://api.groq.com/openai/v1/chat/completions"
                name = "Groq"

            if not api_key:
                raise ValueError(f"{name} API Key is missing. Type in terminal: login {provider} <YOUR_KEY>")

            chat_messages = [{"role": "system", "content": system_instruction}]
            for t in turns:
                chat_messages.append({"role": t["role"], "content": t["content"]})
            if not chat_messages or chat_messages[-1]["content"] != prompt:
                chat_messages.append({"role": "user", "content": prompt})

            payload = json.dumps({
                "model": model,
                "messages": chat_messages,
                "stream": True
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: ") and line_str != "data: [DONE]":
                        data = json.loads(line_str[6:])
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            t = delta.get("content", "")
                            if t:
                                collected_tokens.append(t)
                                token_callback(t)

        elif provider == "claude":
            api_key = config.get("claude_api_key", "").strip()
            if not api_key:
                raise ValueError("Claude / Anthropic API Key is missing. Type in terminal: login claude <YOUR_KEY>")
            
            claude_messages = []
            for t in turns:
                claude_messages.append({"role": t["role"], "content": t["content"]})
            if not claude_messages or claude_messages[-1]["content"] != prompt:
                claude_messages.append({"role": "user", "content": prompt})
                
            # Ensure first message is user role
            while claude_messages and claude_messages[0]["role"] != "user":
                claude_messages.pop(0)

            url = "https://api.anthropic.com/v1/messages"
            payload = json.dumps({
                "model": model,
                "max_tokens": 4096,
                "system": system_instruction,
                "messages": claude_messages,
                "stream": True
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data = json.loads(line_str[6:])
                        if data.get("type") == "content_block_delta":
                            t = data.get("delta", {}).get("text", "")
                            if t:
                                collected_tokens.append(t)
                                token_callback(t)

        full_response = "".join(collected_tokens)
        if not full_response:
            full_response = "Operator, model stream concluded with nominal status."
    except Exception as e:
        full_response = f"\n◈ Anomaly communicating with [{provider.upper()}]: {e}\n(Tip: Type 'login' in terminal to register or update your API key)."
        token_callback(full_response)

    complete_callback(full_response)
