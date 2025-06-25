# import os
# import pandas as pd
# import re
# import json
# from dotenv import load_dotenv
# import google.generativeai as genai # type: ignore
# from google.api_core.exceptions import ResourceExhausted

# # === Load environment variables and configure Gemini API ===
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise Exception("❌ Gemini API key not found in .env file.")

# genai.configure(api_key=GEMINI_API_KEY)
# gemini = genai.GenerativeModel(model_name="models/gemini-1.5-flash")  # 👈 FLASH MODEL HERE

# # === Load dataset ===
# df = pd.read_csv("TMDB_tv_dataset_v3.csv")

# # === Cache setup ===
# CACHE_FILE = "cache.json"
# if os.path.exists(CACHE_FILE):
#     with open(CACHE_FILE, "r") as f:
#         cache = json.load(f)
# else:
#     cache = {}

# def save_cache():
#     with open(CACHE_FILE, "w") as f:
#         json.dump(cache, f, indent=2)

# def call_gemini_with_cache(key, prompt, default):
#     """Helper: Check cache, call Gemini if needed, handle quota and save cache."""
#     if key in cache:
#         return cache[key]
#     try:
#         response = gemini.generate_content(prompt)
#         text = response.text.lower()
#         cache[key] = text
#         save_cache()
#         return text
#     except ResourceExhausted:
#         print(f"⚠️ Gemini quota exceeded. Using default for {key}.")
#         return default

# def get_intro_outro_durations(title):
#     prompt = f"""
# You're an expert on classic TV shows. Please estimate the average intro and outro durations for "{title}".
# Reply only in the format: intro: X minutes, outro: Y minutes.
# Give realistic values as per known TV standards (e.g., intro usually 0.7–1.2 min for older shows).
# """

#     default = "intro: 1.5, outro: 1.5"
#     raw_text = call_gemini_with_cache(f"intro_outro_{title}", prompt, default)
#     numbers = re.findall(r"[\d.]+", raw_text)
#     if len(numbers) >= 2:
#         return float(numbers[0]), float(numbers[1])
#     else:
#         print("⚠️ Gemini response invalid, using default intro/outro 1.5 min.")
#         return 1.5, 1.5

# def get_estimated_runtime(title):
#     prompt = f"""
# Estimate the average episode runtime (in minutes) for the TV show "{title}".
# Only return a single number, like: runtime: X. No explanation.
# """
#     default = "runtime: 45"
#     raw_text = call_gemini_with_cache(f"runtime_{title}", prompt, default)
#     numbers = re.findall(r"[\d.]+", raw_text)
#     if numbers:
#         return float(numbers[0])
#     else:
#         print("⚠️ Gemini response invalid, using default runtime 45 min.")
#         return 45.0

# def get_smart_binge_tips(title, episodes, runtime, intro, outro, speed, overview):
#     prompt = f"""
# I’m watching the TV show "{title}", which has {episodes} episodes and an average episode length of {runtime} minutes.
# I'm skipping approximately {intro} minutes of intro and {outro} minutes of outro.
# I’ll be watching at {speed}x speed.

# Here’s the show’s summary: {overview}

# Can you suggest smart binge-watching tips like:
# - How to avoid fatigue
# - Which parts might be skippable
# """
#     default = "No binge tips available."
#     raw_text = call_gemini_with_cache(f"binge_tips_{title}", prompt, default)
#     return raw_text

# # === Main Program ===
# def main():
#     print("\n🎬 Welcome to the Series Binge Cost Calculator!\n")

#     search_query = input("Enter the name of a TV show: ").strip().lower()
#     matches = df[df['name'].str.lower().str.contains(search_query, na=False)]

#     if matches.empty:
#         print("❌ No matching shows found.")
#         return

#     print(f"\n✅ Found {len(matches)} match(es):")
#     pd.set_option('display.max_rows', 300)  # or use None to show all rows
#     print(matches[['name', 'number_of_seasons', 'number_of_episodes', 'episode_run_time']])

#     try:
#         selected_index = int(input("\nℹ️ Enter the index of the show you want to calculate for: "))
#         selected_show = df.loc[selected_index]
#     except (ValueError, KeyError):
#         print("⚠️ Invalid index entered. Exiting.")
#         return

#     title = selected_show['name']
#     episodes = selected_show['number_of_episodes']
#     runtime = selected_show['episode_run_time']
#     overview = selected_show['overview'] if pd.notna(selected_show['overview']) else "No overview available."

#     if episodes == 0 or pd.isna(episodes):
#         print("⚠️ Sorry, this show's episode count is invalid or missing. Exiting.")
#         return

#     if runtime == 0 or pd.isna(runtime):
#         print("\n🤖 Episode runtime is missing. Asking Gemini for a good estimate...")
#         runtime = get_estimated_runtime(title)
#         print(f"⏱️ Estimated runtime: {runtime} minutes")

#     print(f"\n📺 Selected Show: {title}")
#     print(f"Total Episodes: {episodes}, Episode Duration: {runtime} minutes")

#     print("\n🤖 Fetching estimated intro/outro duration using Gemini...")
#     intro, outro = get_intro_outro_durations(title)
#     print(f"⏱️ Estimated intro: {intro} min | outro: {outro} min")

#     print("\n🎛️ Choose playback speed (or enter a custom one):")
#     print("Common options: 1 (normal), 1.25, 1.5, 1.75, 2")
#     try:
#         speed = float(input("Enter your preferred playback speed (e.g., 1.5): "))
#         if speed <= 0:
#             raise ValueError
#     except ValueError:
#         print("⚠️ Invalid input. Using normal speed (1x).")
#         speed = 1.0

#     raw_watch_time = episodes * runtime
#     total_skipped = episodes * (intro + outro)
#     adjusted_time = raw_watch_time - total_skipped
#     final_time = adjusted_time / speed

#     print("\n🧮 Binge Time Calculation:")
#     print(f"📦 Raw total watch time: {raw_watch_time:.2f} minutes")
#     print(f"⏩ Time saved by skipping intros/outros: {total_skipped:.2f} minutes")
#     print(f"⚡ Final time after {speed}x speed: {final_time:.2f} minutes")
#     print(f"⏰ Total binge time: {final_time / 60:.2f} hours")

#     print("\n🤖 Fetching smart binge-watching tips from Gemini...")
#     tips = get_smart_binge_tips(title, episodes, runtime, intro, outro, speed, overview)
#     print("\n--- Gemini's Smart Binge-Watching Tips ---")
#     print(tips)

# if __name__ == "__main__":
#     main()


# import os
# import streamlit as st
# import pandas as pd
# from utils import (
#     get_intro_outro_durations,
#     get_estimated_runtime,
#     get_binge_tips,
#     load_dataset,
# )

# st.set_page_config(page_title="Binge Time Calculator", layout="centered")
# st.image("logo.png", width=120)
# st.title("🍿 Series Binge Cost Calculator")
# st.markdown("Estimate total binge time including playback speed and skipping intros/outros.")

# # Load dataset
# df = load_dataset("TMDB_tv_dataset_v3.csv")

# st.header("🔍 Step 1: Search & Select a TV Show")
# search_query = st.text_input("Enter TV show name", "Friends")

# matches = df[df['name'].str.lower().str.contains(search_query.lower(), na=False)]

# if matches.empty:
#     st.warning("No matching shows found. Try a different title.")
#     st.stop()

# selected = st.selectbox(
#     "Select from matches:",
#     matches[['name', 'number_of_seasons', 'number_of_episodes', 'episode_run_time']].apply(
#         lambda row: f"{row['name']} ({row['number_of_episodes']} eps, {row['episode_run_time']} min/ep)",
#         axis=1
#     ).tolist()
# )
# selected_show = matches.iloc[[i for i, row in matches.iterrows() if row['name'] in selected][0]]

# title = selected_show['name']
# episodes = selected_show['number_of_episodes']
# runtime = selected_show['episode_run_time']

# if episodes == 0 or pd.isna(episodes):
#     st.error("This show's episode count is missing. Cannot proceed.")
#     st.stop()

# # Playback speed input
# st.header("🎬 Step 2: Playback Speed")
# speed = st.selectbox("Playback speed:", [1.0, 1.25, 1.5, 1.75, 2.0], index=2)

# calculate = st.button("▶️ Search & Calculate Binge Time")

# if calculate:
#     # Patch missing runtime
#     if runtime == 0 or pd.isna(runtime):
#         st.info("Episode runtime missing. Asking Gemini for estimate...")
#         runtime = get_estimated_runtime(title)
#         st.success(f"Estimated runtime: {runtime:.1f} minutes")

#     # Get intro/outro durations
#     st.header("⏱️ Step 3: Binge Time Summary")
#     intro, outro = get_intro_outro_durations(title)
#     st.markdown(f"**Estimated intro:** {intro:.2f} min | **outro:** {outro:.2f} min")

#     raw_time = episodes * runtime
#     skipped_time = episodes * (intro + outro)
#     adjusted = raw_time - skipped_time
#     final = adjusted / speed

#     st.markdown(f"- 📦 Raw watch time: **{raw_time:.2f} min**")
#     st.markdown(f"- ⏩ Time saved by skipping intros/outros: **{skipped_time:.2f} min**")
#     st.markdown(f"- ⚡ Final time at {speed}x speed: **{final:.2f} min** (~{final/60:.2f} hrs)")

#     # Show tip button after calculation
#     get_tips = st.button("💡 Get Gemini Binge Tips")
#     if get_tips:
#         st.header("🧠 Gemini's Smart Binge Tips")
#         overview = selected_show['overview'] or "No overview available."
#         tips = get_binge_tips(title, episodes, runtime, intro, outro, speed, overview)
#         st.markdown(tips)


import streamlit as st
import pandas as pd
from utils import (
    get_intro_outro_durations,
    get_estimated_runtime,
    get_binge_tips,
    load_dataset,
)

st.set_page_config(page_title="Binge Time Calculator", layout="centered")
st.image("logo.png", width=120)
st.title("🍿 Series Binge Cost Calculator")
st.markdown("Estimate total binge time including playback speed and skipping intros/outros.")

# Load dataset once
df = load_dataset("TMDB_tv_dataset_v3.csv")

# Use session state to preserve data between interactions
if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "tips_fetched" not in st.session_state:
    st.session_state.tips_fetched = False
if "runtime" not in st.session_state:
    st.session_state.runtime = None
if "intro" not in st.session_state:
    st.session_state.intro = None
if "outro" not in st.session_state:
    st.session_state.outro = None
if "final" not in st.session_state:
    st.session_state.final = None
if "title" not in st.session_state:
    st.session_state.title = ""
if "episodes" not in st.session_state:
    st.session_state.episodes = 0
if "speed" not in st.session_state:
    st.session_state.speed = 1.5
if "overview" not in st.session_state:
    st.session_state.overview = ""

# Step 1: Search & Select
search_query = st.text_input("Enter TV show name", value="", placeholder="Type a show name to search...")

matches = df[df['name'].str.lower().str.contains(search_query.lower(), na=False)] if search_query else pd.DataFrame()

if search_query and matches.empty:
    st.warning("No matching shows found. Try a different title.")

if not matches.empty:
    selected = st.selectbox(
        "Select from matches:",
        matches[['name', 'number_of_seasons', 'number_of_episodes', 'episode_run_time']].apply(
            lambda row: f"{row['name']} ({row['number_of_episodes']} eps, {row['episode_run_time']} min/ep)",
            axis=1
        ).tolist()
    )
    selected_show = matches[matches['name'] == selected.split(" (")[0]].iloc[0]

    title = selected_show['name']
    episodes = selected_show['number_of_episodes']
    runtime = selected_show['episode_run_time']
    overview = selected_show['overview'] or "No overview available."

    speed = st.selectbox("Playback speed:", [1.0, 1.25, 1.5, 1.75, 2.0], index=2)

    calculate = st.button("▶️ Search & Calculate Binge Time")

    if calculate:
        if runtime == 0 or pd.isna(runtime):
            st.info("Episode runtime missing. Asking Gemini for estimate...")
            runtime = get_estimated_runtime(title)
            st.success(f"Estimated runtime: {runtime:.1f} minutes")

        intro, outro = get_intro_outro_durations(title)

        raw_time = episodes * runtime
        skipped_time = episodes * (intro + outro)
        adjusted = raw_time - skipped_time
        final = adjusted / speed

        # Save results in session state
        st.session_state.calculated = True
        st.session_state.tips_fetched = False
        st.session_state.runtime = runtime
        st.session_state.intro = intro
        st.session_state.outro = outro
        st.session_state.final = final
        st.session_state.title = title
        st.session_state.episodes = episodes
        st.session_state.speed = speed
        st.session_state.overview = overview

if st.session_state.calculated:
    st.header("⏱️ Binge Time Summary")
    st.markdown(f"**Show:** {st.session_state.title}")
    st.markdown(f"- Total Episodes: {st.session_state.episodes}")
    st.markdown(f"- Episode Runtime: {st.session_state.runtime:.2f} min")
    st.markdown(f"- Estimated intro: {st.session_state.intro:.2f} min | outro: {st.session_state.outro:.2f} min")
    st.markdown(f"- Playback Speed: {st.session_state.speed}x")
    st.markdown(f"- 📦 Raw watch time: {st.session_state.episodes * st.session_state.runtime:.2f} min")
    st.markdown(f"- ⏩ Time saved by skipping intros/outros: {(st.session_state.episodes * (st.session_state.intro + st.session_state.outro)):.2f} min")
    st.markdown(f"- ⚡ Final binge time: {st.session_state.final:.2f} min (~{st.session_state.final / 60:.2f} hrs)")

    get_tips = st.button("💡 Get Gemini Binge Tips")

    if get_tips:
        tips = get_binge_tips(
            st.session_state.title,
            st.session_state.episodes,
            st.session_state.runtime,
            st.session_state.intro,
            st.session_state.outro,
            st.session_state.speed,
            st.session_state.overview,
        )
        st.session_state.tips_fetched = True
        st.session_state.tips = tips

if st.session_state.tips_fetched:
    st.header("🧠 Gemini's Smart Binge Tips")
    st.markdown(st.session_state.tips)
