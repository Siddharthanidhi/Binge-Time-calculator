# utils.py

import os
import re
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai # type: ignore
from pathlib import Path

# === Load environment ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("❌ Gemini API key not found in .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# === Cache directory ===
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)

def load_dataset(path):
    return pd.read_csv(path)

def cache_response(key, response):
    with open(CACHE_DIR / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump({"text": response}, f)

def load_cached_response(key):
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["text"]
    return None

def call_gemini_with_cache(key, prompt, fallback=""):
    cached = load_cached_response(key)
    if cached:
        return cached

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        cache_response(key, text)
        return text
    except Exception as e:
        print(f"⚠️ Gemini API failed: {e}")
        return fallback

# === Known intro/outro durations for accuracy ===
KNOWN_SHOW_DURATIONS = {
    "friends": (0.75, 0.4),
    "breaking bad": (0.65, 0.5),
    "stranger things": (0.9, 0.6),
    "the office": (0.75, 0.45),
    "game of thrones": (1.0, 0.6),
    "money heist": (0.85, 0.6),
    "the big bang theory": (0.8, 0.3),
    "dark": (1.0, 0.5),
    "sherlock": (1.0, 1.0)
}

def get_intro_outro_durations(title):
    title_key = title.strip().lower()
    if title_key in KNOWN_SHOW_DURATIONS:
        return KNOWN_SHOW_DURATIONS[title_key]

    prompt = f"""
You're an expert on TV show editing.
Estimate the average intro and outro duration (in minutes) for the show "{title}".
Respond only in this format: intro: X, outro: Y.
"""
    default = "intro: 1.5, outro: 1.5"
    raw = call_gemini_with_cache(f"intro_outro_{title_key}", prompt, default)
    numbers = re.findall(r"[\d.]+", raw)
    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    else:
        return 1.5, 1.5

def get_estimated_runtime(title):
    prompt = f"""
Estimate the average episode runtime (in minutes) for the TV show "{title}".
Return only the number.
"""
    raw = call_gemini_with_cache(f"runtime_{title.lower()}", prompt, "45")
    numbers = re.findall(r"[\d.]+", raw)
    return float(numbers[0]) if numbers else 45.0

def get_binge_tips(title, episodes, runtime, intro, outro, speed, overview):
    prompt = f"""
I’m watching the TV show "{title}", which has {episodes} episodes with ~{runtime} minutes each.
I skip {intro} min intro and {outro} min outro per episode and watch at {speed}x speed.

Here's the summary:
{overview}

Give binge-watching tips like:
- How to avoid fatigue
- Best way to plan the watch
- Skippable filler suggestions (if any)
- Humor or warnings
"""
    return call_gemini_with_cache(f"tips_{title.lower()}", prompt, "")
