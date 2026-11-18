"""Burnout Check-in: run locally with `streamlit run app.py`."""
import datetime
import json

import joblib
import pandas as pd
import streamlit as st

from fusion import combine
from journal import analyze_journal, keyword_crisis

st.set_page_config(page_title="Burnout Check-in", page_icon="🌊", layout="centered")

def apply_ocean_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #D3E1F9 0%, #A4C3E8 100%);
            background-attachment: fixed;
        }
        h1, h2, h3, h4, label, p { color: #2D3E50; }

        /* Banner */
        .hero {
            background: linear-gradient(135deg, #2D3E50 0%, #4C86B6 100%);
            border-radius: 20px;
            padding: 28px 28px 22px;
            margin-bottom: 18px;
        }
        .hero h1 { color: #FFFFFF; margin: 0 0 6px; padding: 0; }
        .hero p  { color: #D3E1F9; margin: 0; font-size: 0.95rem; }

        /* Form as a card */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid #7BA9DB;
            border-radius: 18px;
            padding: 1.2rem;
        }

        /* Submit button */
        [data-testid="stFormSubmitButton"] button {
            background: #2D3E50;
            color: #FFFFFF;
            border: none;
            border-radius: 999px;
            padding: 0.5rem 1.6rem;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            background: #4C86B6;
            color: #FFFFFF;
        }

        /* Quote card */
        .stMarkdown blockquote {
            background: rgba(255, 255, 255, 0.65);
            border-left: 5px solid #4C86B6;
            border-radius: 0 14px 14px 0;
            padding: 14px 18px;
            color: #2D3E50;
        }

        /* Expander */
        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid #7BA9DB;
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_ocean_theme()

LABELS = {
    "sleep_hours": "Sleep (hours per night)",
    "study_hours_per_day": "Study (hours per day)",
    "screen_time": "Screen time (hours per day)",
    "physical_activity": "Physical activity",
    "exam_pressure": "Exam pressure",
    "social_support": "Social support",
    "financial_stress": "Financial stress",
}


@st.cache_resource
def load_model():
    return joblib.load("burnout_model.joblib")


@st.cache_resource
def load_ranges():
    with open("feature_ranges.json") as f:
        return json.load(f)


model = load_model()
ranges = load_ranges()
FEATURES = list(model.feature_names_in_)  # same order the model was trained on


def show_crisis_help():
    st.error("It sounds like things are really hard right now.")
    st.markdown(
        "You don't have to handle this alone. Please reach out to someone now:\n\n"
        "- **Call or text 988** (Suicide & Crisis Lifeline, US) any time\n"
        "- **Text HOME to 741741** (Crisis Text Line, US)\n"
        "- Outside the US: contact your local emergency number\n"
        "- Tell a friend, family member, RA, or campus counseling that you need support"
    )


st.markdown(
    f"""
    <div class="hero">
      <h1>🌊 Daily Journal</h1>
      <p>{datetime.date.today():%A, %B %d} · Let the day wash out. This is a private space,
      not a diagnosis or a clinical tool, and nothing you type is stored.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("checkin"):
    st.subheader("Your week")
    c1, c2 = st.columns(2)
    values = {}
    for i, feat in enumerate(FEATURES):
        r = ranges[feat]
        col = c1 if i % 2 == 0 else c2
        values[feat] = col.slider(
            LABELS.get(feat, feat), float(r["min"]), float(r["max"]), float(r["default"]), step=0.1
        )
    entry = st.text_area(
        "How has this week been? (optional, a few sentences)",
        placeholder="e.g. I've been staying up late for midterms and can't focus...",
    )
    submitted = st.form_submit_button("Check in", type="primary")

if submitted:
    # Safety first: a crisis path never depends on the model or the API.
    if entry.strip() and keyword_crisis(entry):
        show_crisis_help()
        st.stop()

    row = pd.DataFrame([values], columns=FEATURES)
    model_score = float(model.predict(row)[0])

    journal, error = (None, None)
    if entry.strip():
        with st.spinner("Reading your journal entry..."):
            journal, error = analyze_journal(entry)
        if error:
            st.warning("Couldn't analyze the journal right now, so this result uses your answers only.")

    level, reason = combine(model_score, journal)

    if level == "URGENT":
        show_crisis_help()
        st.stop()

    colors = {"High": "🔴", "Elevated": "🟠", "Low": "🟢"}
    st.subheader(f"{colors[level]} Signs of burnout: {level}")
    st.write(reason)

    m1, m2 = st.columns(2)
    m1.metric("From your answers", f"{model_score:.1f} / 10")
    m2.metric(
        "From your journal",
        f"{journal['burnout_language_score']:.1f} / 10" if journal else "not used",
    )

    if journal:
        if journal["themes"]:
            st.write("**Themes we noticed:**", ", ".join(journal["themes"]))
        if journal["protective_factors"]:
            st.write("**What's helping you:**", ", ".join(journal["protective_factors"]))

    st.markdown("#### Gentle next steps")
    if level == "Low":
        st.write("Keep doing what works. Check in again next week to see your trend.")
    else:
        st.write(
            "- Take a real break today: a walk, a meal with a friend, or an early night\n"
            "- Talk to someone you trust about how the week has gone\n"
            "- Campus counseling is free for most students, and you don't need to be in crisis to go"
        )

    
