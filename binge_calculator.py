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
