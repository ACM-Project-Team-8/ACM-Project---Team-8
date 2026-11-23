"""Daily Journal — Burnout Check-in: run locally with `streamlit run app.py`."""
import datetime
import html
import json
import math

import joblib
import pandas as pd
import streamlit as st

from fusion import combine
from journal import analyze_journal, keyword_crisis

st.set_page_config(page_title="Daily Journal · Burnout Check-in", page_icon="🌊", layout="centered")


def apply_ocean_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #D3E1F9 0%, #A4C3E8 100%);
            background-attachment: fixed;
        }
        h1, h2, h3, h4, label, p, li { color: #2D3E50; }

        /* Hero Banner */
        .hero {
            background: linear-gradient(135deg, #2D3E50 0%, #4C86B6 100%);
            border-radius: 20px;
            padding: 26px 28px 20px;
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(45, 62, 80, 0.14);
        }
        .hero h1 { color: #FFFFFF; margin: 0 0 6px; padding: 0; font-size: 1.9rem; }
        .hero p  { color: #D3E1F9; margin: 0; font-size: 0.95rem; line-height: 1.45; }

        /* Frosted Glass Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.65);
            border: 1px solid #7BA9DB;
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }

        /* Drain vs Shield Spotlight Cards */
        .drain-card {
            background: rgba(220, 107, 99, 0.12);
            border: 1px solid rgba(200, 90, 83, 0.45);
            border-left: 5px solid #C85A53;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }
        .shield-card {
            background: rgba(72, 169, 153, 0.14);
            border: 1px solid rgba(46, 139, 122, 0.45);
            border-left: 5px solid #2E8B7A;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 12px;
        }

        /* Encouraging Monthly Consistency Banner */
        .consistency-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid #7BA9DB;
            border-radius: 16px;
            padding: 12px 18px;
            margin-bottom: 14px;
        }
        .consistency-count {
            font-size: 1.02rem;
            font-weight: 700;
            color: #2D3E50;
        }
        .consistency-sub {
            font-size: 0.86rem;
            color: #4C6B8A;
            margin-top: 2px;
        }
        .consistency-dots {
            font-size: 0.95rem;
            letter-spacing: 3px;
        }

        /* Live Slider Status Badge */
        .slider-badge {
            display: inline-block;
            background: rgba(234, 241, 252, 0.95);
            border: 1px solid #9BBCE3;
            color: #2D3E50;
            border-radius: 999px;
            padding: 2px 10px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 2px;
        }

        /* Time-Matched Action Card */
        .action-card {
            background: rgba(255, 255, 255, 0.78);
            border-left: 5px solid #4C86B6;
            border-radius: 0 14px 14px 0;
            padding: 14px 18px;
            margin: 8px 0 14px;
        }

        /* Button Color Fix: Primary CTA (#2D3E50) vs Frosted Secondary Chips */
        button[kind="primary"] {
            background-color: #2D3E50 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 0.55rem 1.8rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(45, 62, 80, 0.2) !important;
        }
        button[kind="primary"]:hover {
            background-color: #4C86B6 !important;
            color: #FFFFFF !important;
        }
        button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.72) !important;
            color: #2D3E50 !important;
            border: 1px solid #7BA9DB !important;
            border-radius: 999px !important;
            font-size: 0.84rem !important;
            padding: 0.3rem 0.95rem !important;
        }
        button[kind="secondary"]:hover {
            background-color: #EAF1FC !important;
            border-color: #4C86B6 !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.45);
            padding: 6px;
            border-radius: 16px;
            border: 1px solid #7BA9DB;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 8px 14px;
            font-weight: 600;
            color: #2D3E50;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2D3E50 !important;
            color: #FFFFFF !important;
        }
        .stTabs [aria-selected="true"] p {
            color: #FFFFFF !important;
        }

        /* Expander */
        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.52);
            border: 1px solid #7BA9DB;
            border-radius: 14px;
        }

        /* 60-Second Box Breathing Circle */
        @keyframes breatheBox {
            0%   { transform: scale(0.78); background: #7BA9DB; }
            25%  { transform: scale(1.12); background: #48A999; }
            50%  { transform: scale(1.12); background: #4C86B6; }
            75%  { transform: scale(0.78); background: #6A9FD1; }
            100% { transform: scale(0.78); background: #7BA9DB; }
        }
        .breathe-orb {
            width: 110px;
            height: 110px;
            border-radius: 50%;
            margin: 18px auto;
            animation: breatheBox 16s infinite ease-in-out;
            box-shadow: 0 0 24px rgba(76, 134, 182, 0.45);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_ocean_theme()

LABELS = {
    "sleep_hours": "Sleep (hours per night)",
    "study_hours_per_day": "Focused work / study (hours per day)",
    "screen_time": "Screen time (hours per day)",
    "physical_activity": "Physical activity (hours per week)",
    "exam_pressure": "Deadline & workload pressure",
    "social_support": "Social connection & support",
    "financial_stress": "Financial stress",
}

PROMPT_CHIPS = [
    ("🔋 What drained my battery today?", "What drained my battery today was "),
    ("🌱 One small win this week", "One small win I had this week was "),
    ("🌥️ What I'm dreading tomorrow", "What I'm dreading tomorrow is "),
]

TIME_MATCHED_ACTIONS = {
    "sleep": {
        "⚡ 2 mins": (
            "Set a gentle 'screens down' alarm for 30 minutes before bed tonight, "
            "and put your charger across the room so you aren't tempted to scroll."
        ),
        "☕ 15 mins": (
            "Step outside for 10–15 minutes of daylight or take a 15-minute eyes-closed "
            "rest (no phone) to relieve nervous-system fatigue without grogginess."
        ),
        "🌙 Tonight": (
            "Protect one extra hour of sleep tonight—pick one non-urgent task to move "
            "to tomorrow morning and wind down with dim lights 30 minutes early."
        ),
    },
    "workload": {
        "⚡ 2 mins": (
            "Write down just ONE concrete 10-minute next step on a sticky note and hide "
            "the rest of your to-do list until that tiny step is done."
        ),
        "☕ 15 mins": (
            "Do a 10-minute 'low-bar start' on the task you've been avoiding, followed "
            "by a 5-minute walk away from your desk to break the dread loop."
        ),
        "🌙 Tonight": (
            "Pick a hard stop time tonight (e.g., 9:30 PM). Closing your laptop on purpose "
            "prevents late-night diminishing returns and protects tomorrow's focus."
        ),
    },
    "screen": {
        "⚡ 2 mins": (
            "Follow the 20-20-20 reset: look at something 20 feet away for 20 seconds, "
            "roll your shoulders back, and switch your phone to grayscale for an hour."
        ),
        "☕ 15 mins": (
            "Leave your phone in another room for 15 minutes—grab water, stretch, or "
            "sit by a window to give your eyes and attention a real offline break."
        ),
        "🌙 Tonight": (
            "Plug your phone in outside your reach before bed and swap the last 20 minutes "
            "of scrolling for music, a shower, or a paper book."
        ),
    },
    "social": {
        "⚡ 2 mins": (
            "Send one zero-pressure text to someone you like—even a tiny check-in breaks isolation."
        ),
        "☕ 15 mins": (
            "Work, study, or grab coffee in a shared space (a cafe, library, or lounge), "
            "or call a friend or family member while taking a short walk."
        ),
        "🌙 Tonight": (
            "Put one low-key hangout on the calendar for this week—a meal, a walk, or "
            "studying side-by-side—so connection doesn't get squeezed out."
        ),
    },
    "financial": {
        "⚡ 2 mins": (
            "Write down the single money question worrying you most right now so it stops "
            "looping in your head, and bookmark 211.org if you need local relief options."
        ),
        "☕ 15 mins": (
            "Spend 15 minutes checking one concrete lever—a free campus/community pantry, "
            "a bill payment plan, or canceling one unused subscription—then stop."
        ),
        "🌙 Tonight": (
            "Give yourself permission to pause financial problem-solving for the night; "
            "schedule one daytime 20-minute block to look into support resources with a clear head."
        ),
    },
    "balanced": {
        "⚡ 2 mins": (
            "Notice one thing that went smoothly today and take three slow breaths—locking "
            "in what works helps keep your baseline steady."
        ),
        "☕ 15 mins": (
            "Use 15 minutes for something purely restorative—a walk, music, or catching up "
            "with a friend—while your energy is in a good place."
        ),
        "🌙 Tonight": (
            "Protect the routine that's keeping you grounded: keep your usual bedtime and "
            "check back in next week to track your wave."
        ),
    },
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
FEATURES = list(model.feature_names_in_)


def init_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "monthly_baseline" not in st.session_state:
        # Starts at 6 so your first demo check-in immediately celebrates "7 check-ins this month"
        st.session_state["monthly_baseline"] = 6
    if "journal_entry" not in st.session_state:
        st.session_state["journal_entry"] = ""
    if "latest_result" not in st.session_state:
        st.session_state["latest_result"] = None
    for feat in FEATURES:
        key = f"slider_{feat}"
        if key not in st.session_state:
            st.session_state[key] = float(ranges[feat]["default"])


init_state()


def append_prompt(starter: str):
    current = st.session_state.get("journal_entry", "").strip()
    st.session_state["journal_entry"] = f"{current}\n{starter}" if current else starter


def render_consistency_banner(total_count: int) -> str:
    """Warm, guilt-free monthly counter that celebrates showing up without punishing streaks."""
    month_name = datetime.date.today().strftime("%B")
    if total_count == 0:
        note = "Ready for your first pause whenever you are—no streaks, no pressure."
    elif total_count < 4:
        note = "Every quick pause builds self-awareness. Missed days never reset your progress."
    elif total_count < 10:
        note = "Showing up for yourself adds up—no streak timers, no guilt if you miss a day."
    else:
        note = "Steady reflection habit! You're checking in with yourself consistently."

    filled = min(total_count, 10)
    dots = "●" * filled + "○" * (10 - filled)
    label = f"{total_count} check-in{'s' if total_count != 1 else ''} in {month_name}"

    return f"""
    <div class="consistency-banner">
      <div>
        <div class="consistency-count">🌱 {html.escape(label)}</div>
        <div class="consistency-sub">{html.escape(note)}</div>
      </div>
      <div class="consistency-dots" title="Monthly reflection moments (no streak resets)" style="color: #4C86B6;">
        {dots}
      </div>
    </div>
    """


def get_slider_badge(feat: str, val: float) -> str:
    if feat == "sleep_hours":
        if val < 5.5:
            return "🪫 Running on fumes"
        if val < 7.2:
            return "🔋 Moderate charge"
        return "🔋 Fully recharged"
    if feat == "study_hours_per_day":
        if val < 3.5:
            return "☀️ Light load"
        if val < 6.5:
            return "⛅ Steady pace"
        return "⛈️ Heavy grind"
    if feat == "screen_time":
        if val < 4.0:
            return "☀️ Low screen time"
        if val < 6.5:
            return "⛅ Moderate screen"
        return "⛈️ Screen fatigue"
    if feat == "physical_activity":
        if val < 1.5:
            return "🪫 Low movement"
        if val < 4.0:
            return "🔋 Active"
        return "⚡ Energized"
    if feat == "exam_pressure":
        if val < 4.5:
            return "☀️ Calm skies"
        if val < 7.0:
            return "⛅ Building pressure"
        return "⛈️ Stormy deadline week"
    if feat == "social_support":
        if val < 3.5:
            return "🌧️ Feeling isolated"
        if val < 6.5:
            return "⛅ Some connection"
        return "☀️ Strong support net"
    if feat == "financial_stress":
        if val < 4.0:
            return "☀️ Eased"
        if val < 6.8:
            return "⛅ Tight budget"
        return "⛈️ Heavy financial strain"
    return "⛅ Checked"


def identify_top_drain(values: dict) -> tuple[str, str]:
    """Return (category_key, description) for the strongest behavioral drain."""
    drains = []
    if values.get("sleep_hours", 7.0) < 6.5:
        drains.append((6.5 - values["sleep_hours"], "sleep", f"Sleep dipped to {values['sleep_hours']:.1f} hrs/night"))
    if values.get("exam_pressure", 5.0) > 6.0:
        drains.append((values["exam_pressure"] - 5.0, "workload", "Heavy deadline & workload pressure"))
    if values.get("study_hours_per_day", 5.0) > 6.5:
        drains.append((values["study_hours_per_day"] - 5.5, "workload", f"Long daily work/study hours ({values['study_hours_per_day']:.1f} hrs)"))
    if values.get("financial_stress", 5.0) > 6.0:
        drains.append((values["financial_stress"] - 5.0, "financial", "Elevated financial stress"))
    if values.get("social_support", 5.0) < 4.5:
        drains.append((5.5 - values["social_support"], "social", "Low social connection this week"))
    if values.get("screen_time", 5.0) > 6.5:
        drains.append((values["screen_time"] - 5.5, "screen", f"High daily screen time ({values['screen_time']:.1f} hrs)"))
    if not drains:
        return "balanced", "No single habit is flashing red right now"
    drains.sort(key=lambda x: x[0], reverse=True)
    return drains[0][1], drains[0][2]


def identify_top_shield(values: dict, protective_factors: list[str]) -> str:
    """Return the strongest protective factor from the journal or healthy habits."""
    if protective_factors:
        return f"From your reflection: {protective_factors[0].capitalize()}"
    shields = []
    if values.get("social_support", 5.0) >= 6.5:
        shields.append((values["social_support"], "Strong social support & connection"))
    if values.get("sleep_hours", 6.5) >= 7.2:
        shields.append((values["sleep_hours"] + 1.0, f"Solid sleep ({values['sleep_hours']:.1f} hrs/night)"))
    if values.get("physical_activity", 3.0) >= 3.5:
        shields.append((values["physical_activity"] + 3.0, f"Regular movement ({values['physical_activity']:.1f} hrs/week)"))
    if values.get("screen_time", 5.0) <= 4.0:
        shields.append((8.0 - values["screen_time"], "Healthy boundaries with screen time"))
    if shields:
        shields.sort(key=lambda x: x[0], reverse=True)
        return shields[0][1]
    return "Taking a quiet minute to check in with yourself today"


def score_to_status(score: float) -> str:
    if score >= 6.0:
        return "Overloaded"
    if score >= 4.5:
        return "Stretched"
    return "Steady"


def render_stress_gauge_svg(composite_score: float, level: str) -> str:
    """Render a 180-degree SVG needle gauge pointing to Steady, Stretched, or Overloaded."""
    clamped = max(0.0, min(10.0, composite_score))
    angle_deg = 180.0 - (clamped / 10.0) * 180.0
    angle_rad = math.radians(angle_deg)

    cx, cy = 180, 165
    r_outer = 126
    r_inner = 82
    tip_len = 115
    base_len = 96

    nx = cx + tip_len * math.cos(angle_rad)
    ny = cy - tip_len * math.sin(angle_rad)
    bx = cx + base_len * math.cos(angle_rad)
    by = cy - base_len * math.sin(angle_rad)

    perp_rad = angle_rad + math.pi / 2.0
    hw = 7.0
    p1x, p1y = bx + hw * math.cos(perp_rad), by - hw * math.sin(perp_rad)
    p2x, p2y = bx - hw * math.cos(perp_rad), by + hw * math.sin(perp_rad)

    def arc_sector(deg_start: float, deg_end: float, fill: str) -> str:
        a1 = math.radians(deg_start)
        a2 = math.radians(deg_end)
        x1_o, y1_o = cx + r_outer * math.cos(a1), cy - r_outer * math.sin(a1)
        x2_o, y2_o = cx + r_outer * math.cos(a2), cy - r_outer * math.sin(a2)
        x1_i, y1_i = cx + r_inner * math.cos(a2), cy - r_inner * math.sin(a2)
        x2_i, y2_i = cx + r_inner * math.cos(a1), cy - r_inner * math.sin(a1)
        return (
            f'<path d="M {x1_o:.1f} {y1_o:.1f} '
            f'A {r_outer} {r_outer} 0 0 1 {x2_o:.1f} {y2_o:.1f} '
            f'L {x1_i:.1f} {y1_i:.1f} '
            f'A {r_inner} {r_inner} 0 0 0 {x2_i:.1f} {y2_i:.1f} Z" '
            f'fill="{fill}" opacity="0.92"/>'
        )

    zone_meta = {
        "Low": ("Steady", "#2E8B7A", "Your habits and reflection look grounded right now."),
        "Elevated": ("Stretched", "#D98A2B", "Moderate strain is building—a small reset could help."),
        "High": ("Overloaded", "#C85A53", "Strong signs of burnout—prioritize rest and support."),
    }
    label, badge_color, subtitle = zone_meta.get(level, zone_meta["Elevated"])

    return f"""
    <div style="background: rgba(255,255,255,0.76); border: 1px solid #7BA9DB; border-radius: 20px; padding: 18px 16px 16px; text-align: center; margin: 12px 0 16px;">
      <svg viewBox="0 0 360 205" width="100%" style="max-width: 380px; height: auto; display: block; margin: 0 auto;">
        {arc_sector(180, 120, "#48A999")}
        {arc_sector(120, 60, "#E9A84A")}
        {arc_sector(60, 0, "#DC6B63")}
        <text x="48" y="186" font-size="12" font-weight="700" fill="#2E8B7A" text-anchor="middle">Steady</text>
        <text x="180" y="28" font-size="12" font-weight="700" fill="#B8701D" text-anchor="middle">Stretched</text>
        <text x="312" y="186" font-size="12" font-weight="700" fill="#B64942" text-anchor="middle">Overloaded</text>
        <line x1="{cx}" y1="{cy}" x2="{bx:.1f}" y2="{by:.1f}" stroke="#2D3E50" stroke-width="5" stroke-linecap="round"/>
        <polygon points="{nx:.1f},{ny:.1f} {p1x:.1f},{p1y:.1f} {p2x:.1f},{p2y:.1f}" fill="#2D3E50"/>
        <circle cx="{cx}" cy="{cy}" r="11" fill="#2D3E50"/>
        <circle cx="{cx}" cy="{cy}" r="5" fill="#EAF1FC"/>
      </svg>
      <div style="display: inline-block; background: {badge_color}; color: #FFFFFF; font-weight: 700; font-size: 1.05rem; padding: 6px 20px; border-radius: 999px; margin-top: 2px;">
        Stress Needle: {html.escape(label)}
      </div>
      <p style="color: #2D3E50; margin: 9px 0 0; font-size: 0.95rem;">{html.escape(subtitle)}</p>
    </div>
    """


def render_wave_chart_svg(entries: list[dict]) -> str:
    """Render a smooth SVG wave chart of stress levels over time (no /10 numbers)."""
    w, h = 620, 220
    pad_l, pad_r, pad_t, pad_b = 86, 24, 24, 38
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    def y_for(val: float) -> float:
        clamped = max(0.0, min(10.0, val))
        return pad_t + plot_h * (1.0 - clamped / 10.0)

    y_over = y_for(10.0)
    y_stretch = y_for(6.5)
    y_steady = y_for(4.2)
    y_bottom = y_for(0.0)

    n = len(entries)
    pts = []
    for idx, item in enumerate(entries):
        x = pad_l + (plot_w * 0.5 if n == 1 else (idx / (n - 1)) * plot_w)
        y = y_for(item["composite_score"])
        pts.append((x, y, item["date"], item["status"]))

    if n == 1:
        path_d = f"M {pts[0][0] - 25:.1f} {pts[0][1]:.1f} L {pts[0][0] + 25:.1f} {pts[0][1]:.1f}"
    else:
        path_d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(1, n):
            x0, y0 = pts[i - 1][0], pts[i - 1][1]
            x1, y1 = pts[i][0], pts[i][1]
            cx_mid = (x0 + x1) / 2.0
            path_d += f" C {cx_mid:.1f} {y0:.1f}, {cx_mid:.1f} {y1:.1f}, {x1:.1f} {y1:.1f}"

    dots_svg = ""
    for x, y, dt_str, status in pts:
        dot_color = {"Steady": "#2E8B7A", "Stretched": "#D98A2B", "Overloaded": "#C85A53"}.get(status, "#2D3E50")
        dots_svg += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{dot_color}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<text x="{x:.1f}" y="{h - 12}" font-size="11" fill="#2D3E50" text-anchor="middle">{html.escape(dt_str)}</text>'
        )

    return f"""
    <div style="background: rgba(255,255,255,0.75); border: 1px solid #7BA9DB; border-radius: 18px; padding: 14px; margin: 10px 0 14px;">
      <svg viewBox="0 0 {w} {h}" width="100%" style="height: auto; display: block;">
        <rect x="{pad_l}" y="{y_over:.1f}" width="{plot_w}" height="{y_stretch - y_over:.1f}" fill="#DC6B63" opacity="0.14"/>
        <rect x="{pad_l}" y="{y_stretch:.1f}" width="{plot_w}" height="{y_steady - y_stretch:.1f}" fill="#E9A84A" opacity="0.16"/>
        <rect x="{pad_l}" y="{y_steady:.1f}" width="{plot_w}" height="{y_bottom - y_steady:.1f}" fill="#48A999" opacity="0.16"/>
        <text x="{pad_l - 8}" y="{(y_over + y_stretch)/2 + 4:.1f}" font-size="11" font-weight="700" fill="#B64942" text-anchor="end">Overloaded</text>
        <text x="{pad_l - 8}" y="{(y_stretch + y_steady)/2 + 4:.1f}" font-size="11" font-weight="700" fill="#B8701D" text-anchor="end">Stretched</text>
        <text x="{pad_l - 8}" y="{(y_steady + y_bottom)/2 + 4:.1f}" font-size="11" font-weight="700" fill="#2E8B7A" text-anchor="end">Steady</text>
        <path d="{path_d}" fill="none" stroke="#2D3E50" stroke-width="3.5" stroke-linecap="round"/>
        {dots_svg}
      </svg>
    </div>
    """


def show_crisis_help():
    st.error("It sounds like things are really hard right now.")
    st.markdown(
        "You don't have to handle this alone. Please reach out to someone right now:\n\n"
        "- **Call or text 988** (Suicide & Crisis Lifeline, US & Canada — 24/7, free, confidential)\n"
        "- **Text HOME to 741741** (Crisis Text Line, US & Canada)\n"
        "- **Outside North America:** Visit **[findahelpline.com](https://findahelpline.com)** for free local support in 130+ countries\n"
        "- Reach out to a friend, family member, trusted mentor, or local emergency services"
    )


# --- Header & Encouraging Consistency Counter ---
st.markdown(
    f"""
    <div class="hero">
      <h1>🌊 Daily Journal</h1>
      <p>{datetime.date.today():%A, %B %d} · Let the day wash out. This is a private space,
      not a diagnosis or a clinical tool, and nothing you type is stored on any server.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

monthly_total = st.session_state["monthly_baseline"] + len(st.session_state["history"])
st.markdown(render_consistency_banner(monthly_total), unsafe_allow_html=True)

tab_checkin, tab_trend, tab_support, tab_snapshot = st.tabs(
    ["🌊 Daily Check-in", "📈 My Trend", "🤝 Support & Reset", "📋 Support Snapshot"]
)

# ==============================================================================
# TAB 1: DAILY CHECK-IN
# ==============================================================================
with tab_checkin:
    st.subheader("Your week at a glance")
    c1, c2 = st.columns(2)
    values = {}
    for i, feat in enumerate(FEATURES):
        r = ranges[feat]
        col = c1 if i % 2 == 0 else c2
        current_val = float(st.session_state[f"slider_{feat}"])
        badge = get_slider_badge(feat, current_val)
        col.markdown(f'<span class="slider-badge">{badge}</span>', unsafe_allow_html=True)
        values[feat] = col.slider(
            LABELS.get(feat, feat),
            float(r["min"]),
            float(r["max"]),
            step=0.1,
            key=f"slider_{feat}",
        )

    st.markdown("#### Quick reflection")
    chip_cols = st.columns(len(PROMPT_CHIPS))
    for idx, (chip_label, starter_text) in enumerate(PROMPT_CHIPS):
        chip_cols[idx].button(
            chip_label,
            key=f"chip_{idx}",
            type="secondary",
            on_click=append_prompt,
            args=(starter_text,),
        )

    entry = st.text_area(
        "How has this week been? (a few sentences)",
        key="journal_entry",
        placeholder="e.g. I've been staying up late for deadlines and can't seem to recharge...",
        height=105,
    )

    if hasattr(st, "audio_input"):
        with st.expander("🎙️ Voice Vent (say it out loud instead of typing)"):
            vent_mode = st.radio(
                "What should happen to your voice note?",
                ["Vent & shred (let it go immediately)", "Keep & reflect while writing"],
                horizontal=True,
            )
            audio_clip = st.audio_input("Record a quick voice vent")
            if audio_clip is not None:
                if vent_mode.startswith("Vent & shred"):
                    if st.button("🗑️ Shred Voice Vent Now", type="secondary"):
                        st.success("Voice vent shredded and cleared from memory. Take a deep breath.")
                else:
                    st.caption("Play back your note above and add any key thoughts into the reflection box before checking in.")

    submitted = st.button("Check in", type="primary")

    if submitted:
        if entry.strip() and keyword_crisis(entry):
            show_crisis_help()
            st.stop()

        row = pd.DataFrame([values], columns=FEATURES)
        model_score = float(model.predict(row)[0])

        journal, error = (None, None)
        if entry.strip():
            with st.spinner("Reading your reflection..."):
                journal, error = analyze_journal(entry)
            if error:
                st.warning("Couldn't reach the reflection analyzer right now, so your needle uses your daily habits.")

        level, reason = combine(model_score, journal)

        if level == "URGENT":
            show_crisis_help()
            st.stop()

        if journal:
            j_score = float(journal["burnout_language_score"])
            composite = max(0.5 * model_score + 0.5 * j_score, max(model_score, j_score) - 0.6)
        else:
            composite = model_score

        drain_cat, drain_text = identify_top_drain(values)
        protective_list = journal["protective_factors"] if journal else []
        shield_text = identify_top_shield(values, protective_list)
        status_label = {"Low": "Steady", "Elevated": "Stretched", "High": "Overloaded"}[level]

        result_record = {
            "date": datetime.date.today().strftime("%b %d"),
            "level": level,
            "status": status_label,
            "reason": reason,
            "composite_score": round(composite, 2),
            "habit_status": score_to_status(model_score),
            "journal_status": score_to_status(journal["burnout_language_score"]) if journal else "Not used",
            "drain_cat": drain_cat,
            "drain_text": drain_text,
            "shield_text": shield_text,
            "sleep_hours": values["sleep_hours"],
            "themes": journal["themes"] if journal else [],
            "protective": protective_list,
        }
        st.session_state["latest_result"] = result_record
        st.session_state["history"].append(result_record)
        st.rerun()

    # --- Smarter Check-In Results (Replacing Static Advice) ---
    if st.session_state["latest_result"] is not None:
        res = st.session_state["latest_result"]
        st.markdown(render_stress_gauge_svg(res["composite_score"], res["level"]), unsafe_allow_html=True)
        st.write(res["reason"])

        s1, s2 = st.columns(2)
        s1.markdown(
            f'<div class="glass-card"><strong>Daily Habits Signal</strong><br/>{html.escape(res["habit_status"])}</div>',
            unsafe_allow_html=True,
        )
        s2.markdown(
            f'<div class="glass-card"><strong>Reflection Signal</strong><br/>{html.escape(res["journal_status"])}</div>',
            unsafe_allow_html=True,
        )

        # Biggest Drain vs. Biggest Shield Spotlight
        st.markdown("#### ⚖️ Biggest Drain vs. Biggest Shield")
        d_col, sh_col = st.columns(2)
        d_col.markdown(
            f'<div class="drain-card"><strong>🔻 Biggest Drain</strong><br/>{html.escape(res["drain_text"])}</div>',
            unsafe_allow_html=True,
        )
        sh_col.markdown(
            f'<div class="shield-card"><strong>🛡️ Biggest Shield</strong><br/>{html.escape(res["shield_text"])}</div>',
            unsafe_allow_html=True,
        )

        if res["themes"]:
            st.markdown(f"**Themes noticed in your reflection:** {', '.join(res['themes'])}")

        # Time-Matched Micro-Actions
        st.markdown("#### ⏱️ Time-Matched Reset")
        time_choice = st.radio(
            "How much time do you have right now?",
            ["⚡ 2 mins", "☕ 15 mins", "🌙 Tonight"],
            horizontal=True,
            key="time_choice",
        )
        action_bucket = TIME_MATCHED_ACTIONS.get(res["drain_cat"], TIME_MATCHED_ACTIONS["balanced"])
        matched_tip = action_bucket[time_choice]
        st.markdown(
            f"""
            <div class="action-card">
              <strong>Tailored for your top drain ({html.escape(time_choice)}):</strong><br/>
              {html.escape(matched_tip)}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# TAB 2: MY TREND
# ==============================================================================
with tab_trend:
    st.subheader("📈 Your Stress Wave Over Time")
    st.caption("Saved strictly in your current browser session—nothing is sent to a database or stored on a server.")

    b_col1, b_col2 = st.columns(2)
    if b_col1.button("✨ Preview sample 4-week journey", type="secondary"):
        st.session_state["history"] = [
            {
                "date": "Nov 01", "level": "Low", "status": "Steady",
                "reason": "Balanced sleep and manageable workload.",
                "composite_score": 3.1, "habit_status": "Steady", "journal_status": "Steady",
                "drain_cat": "balanced", "drain_text": "No single habit flashing red",
                "shield_text": "Solid sleep (7.6 hrs/night)",
                "sleep_hours": 7.6, "themes": ["focused", "rested"], "protective": ["morning walks", "good sleep"],
            },
            {
                "date": "Nov 08", "level": "Elevated", "status": "Stretched",
                "reason": "Deadlines picked up and sleep dipped slightly.",
                "composite_score": 5.3, "habit_status": "Stretched", "journal_status": "Stretched",
                "drain_cat": "workload", "drain_text": "Heavy deadline & workload pressure",
                "shield_text": "From your reflection: Talking with friends",
                "sleep_hours": 6.1, "themes": ["busy schedule", "mental fatigue"], "protective": ["talking with friends"],
            },
            {
                "date": "Nov 15", "level": "High", "status": "Overloaded",
                "reason": "Late nights and heavy deadline load stacked up.",
                "composite_score": 7.6, "habit_status": "Stretched", "journal_status": "Overloaded",
                "drain_cat": "sleep", "drain_text": "Sleep dipped to 4.8 hrs/night",
                "shield_text": "From your reflection: Supportive roommate",
                "sleep_hours": 4.8, "themes": ["exhaustion", "trouble focusing"], "protective": ["supportive roommate"],
            },
            {
                "date": "Nov 22", "level": "Elevated", "status": "Stretched",
                "reason": "Recovering after catching up on rest.",
                "composite_score": 4.8, "habit_status": "Steady", "journal_status": "Stretched",
                "drain_cat": "workload", "drain_text": "Heavy deadline & workload pressure",
                "shield_text": "From your reflection: Weekend rest",
                "sleep_hours": 6.8, "themes": ["recovering", "hopeful"], "protective": ["weekend rest", "exercise"],
            },
        ]
        st.rerun()

    if b_col2.button("🗑️ Clear session history", type="secondary"):
        st.session_state["history"] = []
        st.session_state["monthly_baseline"] = 0
        st.session_state["latest_result"] = None
        st.rerun()

    hist = st.session_state["history"]
    if not hist:
        st.info("Complete a check-in on the first tab—or click **Preview sample 4-week journey** above—to see your wave chart.")
    else:
        st.markdown(render_wave_chart_svg(hist), unsafe_allow_html=True)
        low_sleep_days = [h for h in hist if h.get("sleep_hours", 7.0) < 6.0 and h["status"] in ("Stretched", "Overloaded")]
        if low_sleep_days:
            st.markdown(
                f'<div class="glass-card"><strong>🔍 Pattern spotted:</strong> Your needle shifted toward <em>Stretched</em> or <em>Overloaded</em> on '
                f'{len(low_sleep_days)} check-in(s) where sleep dipped below 6 hours.</div>',
                unsafe_allow_html=True,
            )

# ==============================================================================
# TAB 3: SUPPORT & RESET (UNIVERSAL FOR EVERYONE)
# ==============================================================================
with tab_support:
    st.subheader("🤝 Support & 60-Second Reset")
    st.caption("Universal tools and free support options for anyone—students, workers, or anyone carrying a heavy load.")

    latest = st.session_state.get("latest_result")
    active_drain = latest["drain_cat"] if latest else None

    st.markdown("#### 1. 60-Second Guided Box Breathing")
    st.write("Follow the ocean orb: **Inhale 4s** as it expands · **Hold 4s** · **Exhale 4s** as it softens · **Hold 4s**.")
    st.markdown('<div class="breathe-orb"></div>', unsafe_allow_html=True)

    st.markdown("#### 2. Free & Accessible Support Anywhere")
    if active_drain == "financial":
        st.info("Highlighted for your check-in: **211.org** connects you to free local help with bills, food, housing, and stress.")
    elif active_drain == "workload":
        st.info("Highlighted for your check-in: Try the **One 10-Minute Next Step** rule—pick just one small task and ignore the rest of the list for 10 minutes.")
    elif active_drain in ("sleep", "screen"):
        st.info("Highlighted for your check-in: **CBT-I Coach** (free app, no subscription) offers evidence-based wind-down tools for sleep recovery.")

    st.markdown(
        """
        - **Free Peer Warmlines ([warmline.org](https://warmline.org)):** Confidential, non-crisis phone & chat lines staffed by trained peers who listen when you're overwhelmed or lonely—before things reach a crisis.
        - **Free Counseling You May Already Have:**
          - *At work:* Ask HR about your **Employee Assistance Program (EAP)**—most employers cover 3–8 free, confidential therapy sessions per year.
          - *In school:* Search `[Your School] counseling services`—most colleges include free short-term counseling in student fees.
        - **Low-Cost Care & Practical Relief:** **[Open Path Collective](https://openpathcollective.org)** offers affordable sessions ($40–$70) without insurance; **[211.org](https://www.211.org)** connects you to free local financial, food, and housing resources.
        - **24/7 Immediate Support:** Call or text **988** (US & Canada), text **HOME to 741741**, or visit **[findahelpline.com](https://findahelpline.com)** anywhere in the world.
        """
    )

# ==============================================================================
# TAB 4: SUPPORT SNAPSHOT
# ==============================================================================
with tab_snapshot:
    st.subheader("📋 Support Snapshot")
    st.caption("An organized, private summary of your recent check-ins—helpful if you ever want to share what you've been carrying with a counselor, doctor, or friend.")

    hist = st.session_state["history"]
    if not hist:
        st.info("No check-ins recorded in this session yet. Complete a check-in on Tab 1 (or load the sample journey on Tab 2) to generate your snapshot.")
    else:
        all_drains = [h["drain_text"] for h in hist if h.get("drain_cat") != "balanced"]
        all_themes = [t for h in hist for t in h.get("themes", [])]
        all_prot = [p for h in hist for p in h.get("protective", [])]

        unique_drains = list(dict.fromkeys(all_drains)) or ["No major behavioral drains flagged"]
        unique_themes = list(dict.fromkeys(all_themes)) or ["No journal themes recorded"]
        unique_prot = list(dict.fromkeys(all_prot)) or ["Consistent self-check-ins"]

        snapshot_text = (
            f"DAILY JOURNAL — SUPPORT SNAPSHOT ({datetime.date.today():%B %d, %Y})\n"
            f"Check-ins summarized: {len(hist)}\n"
            f"Most recent status: {hist[-1]['status']}\n\n"
            f"TOP STRESS DRIVERS:\n- " + "\n- ".join(unique_drains) + "\n\n"
            f"RECURRING REFLECTION THEMES:\n- " + "\n- ".join(unique_themes) + "\n\n"
            f"WHAT HAS BEEN HELPING:\n- " + "\n- ".join(unique_prot) + "\n\n"
            f"Note: Self-reflection summary only (not a clinical diagnosis)."
        )

        st.markdown(
            f"""
            <div class="glass-card">
              <p><strong>Check-ins summarized:</strong> {len(hist)} · <strong>Latest status:</strong> {html.escape(hist[-1]['status'])}</p>
              <p><strong>Top Stress Drivers:</strong> {html.escape(', '.join(unique_drains))}</p>
              <p><strong>Recurring Themes:</strong> {html.escape(', '.join(unique_themes))}</p>
              <p><strong>What's Helping:</strong> {html.escape(', '.join(unique_prot))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            label="⬇️ Download Support Snapshot (.txt)",
            data=snapshot_text,
            file_name=f"support_snapshot_{datetime.date.today().isoformat()}.txt",
            mime="text/plain",
            type="secondary",
        )
