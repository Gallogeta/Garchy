#!/usr/bin/env python3
"""
Gally AI Router — Multi-Provider Inference Engine
Seamless on-the-fly switching between:
- Local Offline AI (gally-cephalon-ai via Ollama)
- Google Gemini (Gemini 2.5 / 1.5 Flash & Pro)
- Anthropic Claude 3.5 Sonnet / Opus
- OpenAI GPT-4o / GPT-4o Mini
- DeepSeek R1 / V3
- Groq Llama 3.3 (Ultra Fast)
"""

import os
import sys
import json
import urllib.request
import urllib.parse

CONFIG_PATH = os.path.expanduser("~/.config/gally/ai_config.json")

DEFAULT_CONFIG = {
    "active_provider": "local_ollama",
    "active_model": "gally-cephalon-ai",
    "gemini_api_key": "",
    "claude_api_key": "",
    "openai_api_key": "",
    "deepseek_api_key": "",
    "groq_api_key": "",
    "voice_enabled": True,
    "voice_name": "en-US-AriaNeural",
    "mode": "normal",
    "internet_permitted": False,
    "document_access_permitted": False
}

AVAILABLE_MODELS = [
    ("⚡ Local: Cephalon Gally (Offline)", "local_ollama", "gally-cephalon-ai"),
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

HISTORY_PATH = os.path.expanduser("~/.config/gally/cephalon_history.json")

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

def stream_query(prompt, config, token_callback, complete_callback):
    """Routes query to selected provider with live streaming."""
    provider = config.get("active_provider", "local_ollama")
    model = config.get("active_model", "gally-cephalon-ai")
    
    collected_tokens = []
    
    try:
        if provider == "local_ollama":
            url = "http://127.0.0.1:11434/api/generate"
            payload = json.dumps({"model": model, "prompt": prompt, "stream": True}).encode("utf-8")
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
                raise ValueError("Google Gemini API Key is missing. Click '🔑 API Keys & Login' to enter your key.")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
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
                raise ValueError(f"{name} API Key is missing. Click '🔑 API Keys & Login' to enter your key.")

            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
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
                raise ValueError("Claude / Anthropic API Key is missing. Click '🔑 API Keys & Login' to enter your key.")
            url = "https://api.anthropic.com/v1/messages"
            payload = json.dumps({
                "model": model,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
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
        full_response = f"\n◈ Anomaly communicating with [{provider.upper()}]: {e}\n(Tip: Ensure API key is valid or switch to Local Offline model)."
        token_callback(full_response)

    complete_callback(full_response)

if __name__ == "__main__":
    cfg = load_ai_config()
    print("AI Router initialized. Active model:", cfg.get("active_model"))
