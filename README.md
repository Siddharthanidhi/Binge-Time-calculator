# 🍿 Binge Time Calculator

**Estimate how long it would take to binge a TV show with smart calculations, including skipping intros/outros and changing playback speed. Powered by Gemini AI.**

![Logo](logo.png)

---

## 🔍 Features

- 🎬 Search for any TV show from a large TMDB-based dataset  
- ⏱️ Calculates:
  - Total watch time
  - Time saved by skipping intros/outros
  - Final watch time with custom playback speed
- 🤖 Gemini AI Integration:
  - Estimates missing episode runtime or intro/outro durations
  - Provides binge-watching tips (like when to take breaks, skip filler, etc.)
- 💻 Clean and user-friendly Streamlit interface

---

## 🧪 Example

> You search for _"Friends"_, select the correct match, set 1.5x speed, and the app tells you:
> - Estimated 76 hours of binge
> - You save 15+ hours by skipping intros/outros
> - Gemini suggests when to pause or avoid fatigue

---

## 🧰 Tech Stack

- Python 3.11+
- Streamlit
- Pandas
- Google Gemini API (via `google-generativeai`)
- dotenv

---
