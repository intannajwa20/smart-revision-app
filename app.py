import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime, date, timedelta
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="Smart Revision Planner",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------
# Session state defaults
# ---------------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "student": {"password": "revision123", "full_name": "Demo Student"},
        "wawa": {"password": "1234", "full_name": "Wawa"},
        "admin": {"password": "smartplanner", "full_name": "Admin User"}
    }

if "planner_history" not in st.session_state:
    st.session_state.planner_history = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "full_name" not in st.session_state:
    st.session_state.full_name = ""

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "last_plan_data" not in st.session_state:
    st.session_state.last_plan_data = None

if "user_progress" not in st.session_state:
    st.session_state.user_progress = {}

if "user_settings" not in st.session_state:
    st.session_state.user_settings = {}

# ---------------------------------
# Styling
# ---------------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    line-height: 1.1;
}
.subtitle {
    font-size: 1.02rem;
    color: #d6d1e6;
    margin-bottom: 1rem;
}
.hero-box {
    padding: 1.5rem 1.7rem;
    border-radius: 24px;
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.10), transparent 28%),
        linear-gradient(135deg, rgba(142,68,173,0.30), rgba(20,20,35,0.96));
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.18);
}
.section-card {
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}
.small-label {
    font-size: 0.85rem;
    color: #bbb6cc;
    margin-bottom: 0.2rem;
}
.big-value {
    font-size: 1.15rem;
    font-weight: 700;
}
.subject-card {
    padding: 1.15rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.10);
}
.feedback-box {
    padding: 1rem 1.2rem;
    border-radius: 16px;
    background: rgba(142,68,173,0.12);
    border: 1px solid rgba(142,68,173,0.28);
    margin-top: 0.5rem;
}
.tag-high {
    display: inline-block;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    background: rgba(255, 99, 132, 0.15);
    border: 1px solid rgba(255, 99, 132, 0.3);
}
.tag-medium {
    display: inline-block;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    background: rgba(255, 206, 86, 0.12);
    border: 1px solid rgba(255, 206, 86, 0.28);
}
.tag-low {
    display: inline-block;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    background: rgba(75, 192, 192, 0.12);
    border: 1px solid rgba(75, 192, 192, 0.28);
}
.mini-card {
    padding: 1rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    min-height: 120px;
}
.download-card {
    padding: 1rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.8rem;
}
.login-wrap {
    max-width: 520px;
    margin: 2.5rem auto;
    padding: 2rem;
    border-radius: 24px;
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.08), transparent 30%),
        linear-gradient(135deg, rgba(142,68,173,0.25), rgba(20,20,35,0.96));
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 35px rgba(0,0,0,0.22);
}
.login-title {
    font-size: 2.2rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.3rem;
}
.login-subtitle {
    text-align: center;
    color: #d4cbe8;
    margin-bottom: 1.4rem;
}
.profile-box {
    padding: 1rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}
.progress-card {
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}
.checklist-card {
    padding: 1rem 1.1rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 0.7rem;
}
.done-chip {
    display: inline-block;
    padding: 0.24rem 0.55rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    background: rgba(75, 192, 192, 0.14);
    border: 1px solid rgba(75, 192, 192, 0.26);
}
.pending-chip {
    display: inline-block;
    padding: 0.24rem 0.55rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    background: rgba(255, 206, 86, 0.12);
    border: 1px solid rgba(255, 206, 86, 0.26);
}
.badge-box {
    padding: 0.85rem 1rem;
    border-radius: 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.6rem;
}
.level-box {
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(142,68,173,0.12);
    border: 1px solid rgba(142,68,173,0.28);
    margin-bottom: 1rem;
}
.settings-box {
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1rem;
}
.history-card {
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.8rem;
}
hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# User data defaults
# ---------------------------------
def ensure_user_data(username):
    if username not in st.session_state.planner_history:
        st.session_state.planner_history[username] = []

    if username not in st.session_state.user_progress:
        st.session_state.user_progress[username] = {
            "completed_sessions": {},
            "plans_generated": 0
        }

    if username not in st.session_state.user_settings:
        st.session_state.user_settings[username] = {
            "preferred_session_length": 60,
            "daily_study_goal_minutes": 120,
            "motivational_mode": "Cute",
            "theme_name": "Midnight Violet"
        }

# ---------------------------------
# Helper functions
# ---------------------------------
def convert_to_days(value, unit):
    if unit == "Day(s)":
        return int(value)
    if unit == "Week(s)":
        return int(value * 7)
    if unit == "Month(s)":
        return int(value * 30)
    return int(value)

def format_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours > 0 and remaining_minutes > 0:
        return f"{int(hours)} hour(s) {int(remaining_minutes)} minute(s)"
    if hours > 0:
        return f"{int(hours)} hour(s)"
    return f"{int(remaining_minutes)} minute(s)"

def shorten_text(text, max_len=14):
    return text if len(text) <= max_len else text[:max_len] + "..."

def get_priority_details(days_left):
    if days_left <= 3:
        return "Very High", 5, 60
    elif days_left <= 7:
        return "High", 4, 45
    elif days_left <= 14:
        return "Medium", 3, 30
    elif days_left <= 30:
        return "Low", 2, 20
    return "Very Low", 1, 15

def get_study_method(weakness_level):
    if weakness_level >= 4:
        return (
            "Active Recall + Practice Questions",
            "Revise deeply by chapter and do practice questions.",
            "Use flashcards, active recall, and topic-based exercises."
        )
    elif weakness_level == 3:
        return (
            "Concept Review + Short Quiz",
            "Review notes, understand key concepts, and do a short quiz.",
            "Use summary notes, short quizzes, and mini self-tests."
        )
    return (
        "Quick Recap",
        "Do a recap and review the important points only.",
        "Try a quick quiz, skim notes, or make a simple mind map."
    )

def calculate_readiness_score(days_left, avg_weakness):
    time_factor = min(days_left / 30, 1.0) * 50
    weakness_factor = ((6 - avg_weakness) / 5) * 50
    score = int(time_factor + weakness_factor)
    return max(0, min(score, 100))

def get_readiness_status(score):
    if score >= 80:
        return "Almost Ready"
    elif score >= 60:
        return "On Track"
    elif score >= 40:
        return "Needs Work"
    return "Focus Now"

def get_study_mood(score):
    if score >= 80:
        return "🌸 You’re in great shape"
    elif score >= 60:
        return "✨ You’re getting there"
    elif score >= 40:
        return "🫧 You need a stronger push"
    return "⚡ Time to lock in"

def get_motivation_message(mode, progress_percent, streak):
    if mode == "Cute":
        if progress_percent >= 80:
            return "🌷 You’re doing amazing. Keep going, pretty genius."
        if progress_percent >= 50:
            return "✨ You’re making beautiful progress. Don’t stop now."
        return "🫶 Small steps still count. Just begin."
    if mode == "Strict":
        if progress_percent >= 80:
            return "Good. Stay disciplined and finish strong."
        if progress_percent >= 50:
            return "You’re halfway there. No slacking."
        return "Focus. The work will not do itself."
    if streak >= 3:
        return "🔥 Consistency looks good on you."
    return "📚 One focused session can change your whole day."

def get_priority_badge(priority):
    if priority in ["Very High", "High"]:
        return '<span class="tag-high">Urgent</span>'
    elif priority == "Medium":
        return '<span class="tag-medium">Moderate</span>'
    return '<span class="tag-low">Manageable</span>'

def get_subject_icon(subject_name):
    name = subject_name.lower()
    if "data" in name:
        return "📊"
    if "database" in name or "sql" in name:
        return "🗂️"
    if "ai" in name or "artificial" in name or "neural" in name:
        return "🤖"
    if "math" in name or "statistics" in name or "calc" in name:
        return "🧮"
    if "program" in name or "coding" in name or "python" in name:
        return "💻"
    if "network" in name or "security" in name:
        return "🌐"
    return "📘"

def process_subject(subject_name, days_left, topics):
    if days_left <= 0:
        return {"error": f"Time left for subject '{subject_name}' must be greater than 0."}
    if len(topics) == 0:
        return {"error": f"Please enter at least one valid topic for subject '{subject_name}'."}

    exam_priority, urgency_score, base_minutes = get_priority_details(days_left)
    topic_suggestions = []

    for topic_name, weakness_level in topics:
        if weakness_level < 1 or weakness_level > 5:
            return {"error": f"Weakness level for '{topic_name}' in subject '{subject_name}' must be between 1 and 5."}

        recommended_minutes = base_minutes + (weakness_level * 15)
        study_method, suggestion, best_tip = get_study_method(weakness_level)

        if weakness_level >= 4:
            reminder = f"You should study {topic_name} first since your weakness level is high and the exam is getting closer."
        elif weakness_level == 3:
            reminder = f"You should give proper attention to {topic_name} because your understanding is moderate and still needs improvement."
        else:
            reminder = f"Since your weakness level is lower, you can study {topic_name} more lightly because you already have some core understanding."

        topic_suggestions.append({
            "subject": subject_name,
            "topic": topic_name,
            "weakness_level": weakness_level,
            "recommended_minutes": recommended_minutes,
            "reminder": reminder,
            "suggestion": suggestion,
            "best_tip": best_tip,
            "study_method": study_method,
            "days_left": days_left,
            "exam_priority": exam_priority,
            "urgency_score": urgency_score
        })

    topic_suggestions.sort(key=lambda x: (x["weakness_level"], x["urgency_score"]), reverse=True)
    avg_weakness = sum(t["weakness_level"] for t in topic_suggestions) / len(topic_suggestions)
    subject_priority_score = round(urgency_score + avg_weakness, 2)
    readiness_score = calculate_readiness_score(days_left, avg_weakness)

    return {
        "subject_name": subject_name,
        "subject_icon": get_subject_icon(subject_name),
        "days_left": days_left,
        "exam_priority": exam_priority,
        "subject_priority_score": subject_priority_score,
        "most_prioritized_topic": topic_suggestions[0]["topic"],
        "topic_suggestions": topic_suggestions,
        "average_weakness": round(avg_weakness, 2),
        "readiness_score": readiness_score,
        "readiness_status": get_readiness_status(readiness_score)
    }

def process_all_subjects(subjects_data):
    all_subject_results = []
    for subject in subjects_data:
        result = process_subject(subject["subject_name"], subject["days_left"], subject["topics"])
        if "error" in result:
            return {"error": result["error"]}
        all_subject_results.append(result)

    all_subject_results.sort(key=lambda x: x["subject_priority_score"], reverse=True)
    return {"all_subject_results": all_subject_results}

def flatten_topics(all_subject_results):
    rows = []
    for subject in all_subject_results:
        for topic in subject["topic_suggestions"]:
            rows.append({
                "Subject": topic["subject"],
                "Topic": topic["topic"],
                "Weakness Level": topic["weakness_level"],
                "Recommended Minutes": topic["recommended_minutes"],
                "Days Left": topic["days_left"],
                "Exam Priority": topic["exam_priority"],
                "Priority Score": subject["subject_priority_score"],
                "Study Method": topic["study_method"]
            })
    return pd.DataFrame(rows)

def generate_study_timetable(topic_df, start_date=None, preferred_session_length=60):
    if topic_df.empty:
        return pd.DataFrame()

    if start_date is None:
        start_date = date.today()

    preferred_session_length = max(20, min(int(preferred_session_length), 120))

    timetable_rows = []
    day_counter = 1
    session_counter = 1

    sorted_df = topic_df.sort_values(
        by=["Days Left", "Weakness Level", "Recommended Minutes"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    for _, row in sorted_df.iterrows():
        minutes_left = int(row["Recommended Minutes"])

        while minutes_left > 0:
            session_minutes = min(preferred_session_length, minutes_left)
            session_date = start_date + timedelta(days=day_counter - 1)

            timetable_rows.append({
                "Session ID": f"S{session_counter:03d}",
                "Day": f"Day {day_counter}",
                "Calendar Date": session_date.strftime("%Y-%m-%d"),
                "Subject": row["Subject"],
                "Topic": row["Topic"],
                "Study Duration": format_minutes(session_minutes),
                "Duration Minutes": session_minutes,
                "Study Method": row["Study Method"]
            })

            minutes_left -= session_minutes
            day_counter += 1
            session_counter += 1

    return pd.DataFrame(timetable_rows)

def get_focus_distribution(topic_df):
    if topic_df.empty:
        return pd.DataFrame(columns=["Category", "Count"])

    def classify(w):
        if w >= 4:
            return "High Focus"
        elif w == 3:
            return "Moderate Focus"
        return "Light Review"

    df = topic_df.copy()
    df["Category"] = df["Weakness Level"].apply(classify)
    return df["Category"].value_counts().rename_axis("Category").reset_index(name="Count")

def get_workload_by_subject(topic_df):
    if topic_df.empty:
        return pd.DataFrame(columns=["Subject", "Recommended Minutes"])
    out = topic_df.groupby("Subject", as_index=False)["Recommended Minutes"].sum()
    return out.sort_values("Recommended Minutes", ascending=False)

def get_today_focus(topic_df):
    if topic_df.empty:
        return None
    top = topic_df.sort_values(
        by=["Days Left", "Weakness Level", "Recommended Minutes"],
        ascending=[True, False, False]
    ).iloc[0]
    return {
        "subject": top["Subject"],
        "topic": top["Topic"],
        "reason": "High weakness and closer exam date."
    }

def build_plan_snapshot(username, summary_values, subjects_data, all_subject_results, topic_df, timetable_df, today_focus):
    progress_store = st.session_state.user_progress.get(username, {}).get("completed_sessions", {})
    relevant_session_ids = set(timetable_df["Session ID"].tolist()) if not timetable_df.empty else set()

    relevant_progress = {
        sid: progress_store[sid]
        for sid in progress_store
        if sid in relevant_session_ids
    }

    return {
        "plan_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "saved_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "summary_values": summary_values,
        "subjects_data": subjects_data,
        "all_subject_results": all_subject_results,
        "topic_df": topic_df.to_dict(orient="records"),
        "timetable_df": timetable_df.to_dict(orient="records"),
        "today_focus": today_focus,
        "progress_snapshot": relevant_progress
    }

def save_full_plan_entry(username, plan_snapshot):
    ensure_user_data(username)
    st.session_state.planner_history[username].append(plan_snapshot)

def load_plan_into_session(plan_entry):
    topic_df = pd.DataFrame(plan_entry.get("topic_df", []))
    timetable_df = pd.DataFrame(plan_entry.get("timetable_df", []))

    st.session_state.last_plan_data = {
        "all_subject_results": plan_entry.get("all_subject_results", []),
        "topic_df": topic_df,
        "timetable_df": timetable_df,
        "summary_values": plan_entry.get("summary_values", {}),
        "today_focus": plan_entry.get("today_focus"),
        "generated_on": plan_entry.get("saved_at", "")
    }

    if st.session_state.username not in st.session_state.user_progress:
        ensure_user_data(st.session_state.username)

    st.session_state.user_progress[st.session_state.username]["completed_sessions"] = plan_entry.get("progress_snapshot", {}).copy()

def export_plan_json(plan_entry):
    return json.dumps(plan_entry, indent=2).encode("utf-8")

def import_plan_json(uploaded_file):
    try:
        content = uploaded_file.read().decode("utf-8")
        plan_data = json.loads(content)
        required_keys = [
            "plan_id", "saved_at", "summary_values", "subjects_data",
            "all_subject_results", "topic_df", "timetable_df"
        ]
        if not all(key in plan_data for key in required_keys):
            return None, "Invalid JSON file structure."
        return plan_data, None
    except Exception as e:
        return None, f"Failed to import JSON: {str(e)}"

# ---------------------------------
# Progress / streak / XP / badges
# ---------------------------------
def get_completion_store(username):
    ensure_user_data(username)
    return st.session_state.user_progress[username]["completed_sessions"]

def get_session_completed(username, session_id):
    store = get_completion_store(username)
    return session_id in store

def set_session_completed(username, session_id, is_completed):
    store = get_completion_store(username)
    if is_completed:
        store[session_id] = date.today().isoformat()
    else:
        if session_id in store:
            del store[session_id]

def calculate_streaks(date_strings):
    if not date_strings:
        return 0, 0

    unique_dates = sorted(date.fromisoformat(d) for d in set(date_strings))
    best_streak = 1
    run = 1

    for i in range(1, len(unique_dates)):
        if unique_dates[i] == unique_dates[i - 1] + timedelta(days=1):
            run += 1
        else:
            best_streak = max(best_streak, run)
            run = 1

    best_streak = max(best_streak, run)

    today_value = date.today()
    if unique_dates[-1] == today_value:
        current_streak = 1
        idx = len(unique_dates) - 1
        while idx > 0 and unique_dates[idx - 1] == unique_dates[idx] - timedelta(days=1):
            current_streak += 1
            idx -= 1
    else:
        current_streak = 0

    return current_streak, best_streak

def get_badges(completed_sessions, current_streak, best_streak, completion_percent):
    badges = []

    if completed_sessions >= 1:
        badges.append("🌱 First Session Done")
    if completed_sessions >= 5:
        badges.append("📘 5 Sessions Completed")
    if completed_sessions >= 10:
        badges.append("🏅 10 Sessions Completed")
    if current_streak >= 3 or best_streak >= 3:
        badges.append("🔥 3-Day Streak")
    if current_streak >= 5 or best_streak >= 5:
        badges.append("👑 Consistency Queen")
    if completion_percent >= 50:
        badges.append("✨ Halfway There")
    if completion_percent >= 100:
        badges.append("🎓 Plan Completed")

    return badges

def get_progress_summary(username, timetable_df):
    ensure_user_data(username)

    if timetable_df is None or timetable_df.empty:
        return {
            "completed_sessions": 0,
            "total_sessions": 0,
            "completion_percent": 0,
            "completed_minutes": 0,
            "total_minutes": 0,
            "completed_minutes_text": format_minutes(0),
            "remaining_minutes_text": format_minutes(0),
            "current_streak": 0,
            "best_streak": 0,
            "completed_today": 0,
            "xp": 0,
            "level": 1,
            "xp_to_next_level": 100,
            "badges": []
        }

    store = get_completion_store(username)
    valid_session_ids = set(timetable_df["Session ID"].tolist())
    completed_ids = [sid for sid in store.keys() if sid in valid_session_ids]

    total_sessions = len(timetable_df)
    completed_sessions = len(completed_ids)
    completion_percent = int((completed_sessions / total_sessions) * 100) if total_sessions > 0 else 0

    completed_df = timetable_df[timetable_df["Session ID"].isin(completed_ids)]
    completed_minutes = int(completed_df["Duration Minutes"].sum()) if not completed_df.empty else 0
    total_minutes = int(timetable_df["Duration Minutes"].sum()) if not timetable_df.empty else 0
    remaining_minutes = max(total_minutes - completed_minutes, 0)

    completion_dates = sorted(set(store[sid] for sid in completed_ids if sid in store))
    current_streak, best_streak = calculate_streaks(completion_dates)

    today_str = date.today().isoformat()
    completed_today = sum(1 for sid in completed_ids if store.get(sid) == today_str)

    xp = completed_sessions * 20 + best_streak * 10
    level = (xp // 100) + 1
    xp_to_next_level = 100 - (xp % 100)
    badges = get_badges(completed_sessions, current_streak, best_streak, completion_percent)

    return {
        "completed_sessions": completed_sessions,
        "total_sessions": total_sessions,
        "completion_percent": completion_percent,
        "completed_minutes": completed_minutes,
        "total_minutes": total_minutes,
        "completed_minutes_text": format_minutes(completed_minutes),
        "remaining_minutes_text": format_minutes(remaining_minutes),
        "current_streak": current_streak,
        "best_streak": best_streak,
        "completed_today": completed_today,
        "xp": xp,
        "level": level,
        "xp_to_next_level": xp_to_next_level,
        "badges": badges
    }

def get_completion_badge(done):
    if done:
        return '<span class="done-chip">Completed</span>'
    return '<span class="pending-chip">Pending</span>'

def mark_all_for_date(username, timetable_df, selected_date, completed=True):
    daily_df = timetable_df[timetable_df["Calendar Date"] == selected_date]
    for _, row in daily_df.iterrows():
        set_session_completed(username, row["Session ID"], completed)

def reset_all_progress(username):
    ensure_user_data(username)
    st.session_state.user_progress[username]["completed_sessions"] = {}

# ---------------------------------
# Download helpers
# ---------------------------------
def create_download_text(all_subject_results, summary_values, timetable_df, progress_summary=None):
    output = StringIO()
    output.write("SMART REVISION PLAN\n")
    output.write("=" * 50 + "\n\n")
    output.write(f"Generated Date: {datetime.now().strftime('%d %B %Y')}\n")
    output.write(f"Most Prioritized Subject: {summary_values['most_prioritized_subject']}\n")
    output.write(f"Weakest Topic Overall: {summary_values['weakest_topic']}\n")
    output.write(f"Total Topics: {summary_values['total_topics']}\n")
    output.write(f"Total Recommended Study Time: {summary_values['total_study_time']}\n")
    output.write(f"Overall Readiness Score: {summary_values['overall_readiness']}%\n\n")

    if progress_summary:
        output.write("PROGRESS SUMMARY\n")
        output.write("=" * 50 + "\n")
        output.write(f"Completed Sessions: {progress_summary['completed_sessions']}/{progress_summary['total_sessions']}\n")
        output.write(f"Progress: {progress_summary['completion_percent']}%\n")
        output.write(f"Completed Time: {progress_summary['completed_minutes_text']}\n")
        output.write(f"Current Streak: {progress_summary['current_streak']} day(s)\n")
        output.write(f"Best Streak: {progress_summary['best_streak']} day(s)\n")
        output.write(f"XP: {progress_summary['xp']}\n")
        output.write(f"Level: {progress_summary['level']}\n\n")

    output.write("SUBJECT RANKINGS\n")
    output.write("=" * 50 + "\n")
    for i, subject in enumerate(all_subject_results, start=1):
        output.write(f"\nSubject Rank {i}: {subject['subject_name']}\n")
        output.write(f"Days Left: {subject['days_left']} day(s)\n")
        output.write(f"Exam Priority: {subject['exam_priority']}\n")
        output.write(f"Most Prioritized Topic: {subject['most_prioritized_topic']}\n")
        output.write(f"Average Weakness: {subject['average_weakness']}\n")
        output.write(f"Readiness Score: {subject['readiness_score']}%\n")
        for topic in subject["topic_suggestions"]:
            output.write(
                f" - {topic['topic']} | Weakness: {topic['weakness_level']} | "
                f"Duration: {format_minutes(topic['recommended_minutes'])} | "
                f"Method: {topic['study_method']}\n"
            )

    output.write("\n\nSTUDY TIMETABLE\n")
    output.write("=" * 50 + "\n")
    if not timetable_df.empty:
        for _, row in timetable_df.iterrows():
            output.write(
                f"{row['Day']} ({row['Calendar Date']}): {row['Subject']} - {row['Topic']} - "
                f"{row['Study Duration']} - {row['Study Method']}\n"
            )
    return output.getvalue()

# ---------------------------------
# PDF generation
# ---------------------------------
def draw_pdf_background(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#0B1020"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#6C3BB8"))
    canvas.rect(0, height - 70, width, 70, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#8E44AD"))
    canvas.rect(0, 0, width, 12, fill=1, stroke=0)
    canvas.setFillColor(colors.whitesmoke)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()

def build_revision_pdf(all_subject_results, summary_values, timetable_df, progress_summary=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=24, leading=30, alignment=TA_CENTER,
        textColor=colors.whitesmoke, spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=10.5, leading=15, alignment=TA_CENTER,
        textColor=colors.HexColor("#E3D9F7"), spaceAfter=18
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=colors.HexColor("#F0E4FF"),
        spaceBefore=10, spaceAfter=8
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=10, leading=14, textColor=colors.whitesmoke, alignment=TA_LEFT
    )
    small_style = ParagraphStyle(
        "SmallStyle", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9, leading=12, textColor=colors.HexColor("#EAEAF2"), alignment=TA_LEFT
    )

    story = []
    story.append(Spacer(1, 28))
    story.append(Paragraph("Smart Revision Planner", title_style))
    story.append(Paragraph(
        "A personalized revision report with ranked subjects, study priorities, progress tracking, and a day-by-day timetable.",
        subtitle_style
    ))
    story.append(Spacer(1, 18))

    cover_data = [
        ["Generated Date", datetime.now().strftime("%d %B %Y")],
        ["Top Subject", summary_values["most_prioritized_subject"]],
        ["Weakest Topic", summary_values["weakest_topic"]],
        ["Total Topics", str(summary_values["total_topics"])],
        ["Total Study Time", summary_values["total_study_time"]],
        ["Overall Readiness", f"{summary_values['overall_readiness']}%"],
    ]

    if progress_summary:
        cover_data.extend([
            ["Completed Sessions", f"{progress_summary['completed_sessions']}/{progress_summary['total_sessions']}"],
            ["Progress", f"{progress_summary['completion_percent']}%"],
            ["Current Streak", f"{progress_summary['current_streak']} day(s)"],
            ["Best Streak", f"{progress_summary['best_streak']} day(s)"],
            ["XP", str(progress_summary["xp"])],
            ["Level", str(progress_summary["level"])],
        ])

    cover_table = Table(cover_data, colWidths=[55 * mm, 105 * mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#131A2E")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#8E44AD")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#40395E")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Generated by Smart Revision Planner", small_style))
    story.append(PageBreak())

    story.append(Paragraph("Ranked Subject Review", heading_style))
    for i, subject in enumerate(all_subject_results, start=1):
        subject_title = (
            f"<b>{subject['subject_icon']} Subject Rank {i}: {subject['subject_name']}</b><br/>"
            f"Priority: {subject['exam_priority']} | "
            f"Top Topic: {subject['most_prioritized_topic']} | "
            f"Readiness: {subject['readiness_score']}% ({subject['readiness_status']})"
        )
        story.append(Paragraph(subject_title, body_style))
        story.append(Spacer(1, 5))

        topic_rows = [["Topic", "Weakness", "Duration", "Method"]]
        for topic in subject["topic_suggestions"]:
            topic_rows.append([
                topic["topic"],
                str(topic["weakness_level"]),
                format_minutes(topic["recommended_minutes"]),
                topic["study_method"]
            ])

        topic_table = Table(topic_rows, colWidths=[45 * mm, 20 * mm, 35 * mm, 70 * mm])
        topic_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6C3BB8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#131A2E")),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#40395E")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(topic_table)
        story.append(Spacer(1, 12))

    story.append(PageBreak())
    story.append(Paragraph("Automatic Study Timetable", heading_style))

    if timetable_df.empty:
        story.append(Paragraph("No timetable generated.", body_style))
    else:
        timetable_rows = [["ID", "Day", "Date", "Subject", "Topic", "Duration"]]
        for _, row in timetable_df.iterrows():
            timetable_rows.append([
                row["Session ID"],
                row["Day"],
                row["Calendar Date"],
                row["Subject"],
                row["Topic"],
                row["Study Duration"]
            ])

        timetable_table = Table(
            timetable_rows,
            colWidths=[18 * mm, 18 * mm, 28 * mm, 32 * mm, 42 * mm, 25 * mm],
            repeatRows=1
        )
        timetable_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6C3BB8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#131A2E")),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#40395E")),
            ("FONTSIZE", (0, 0), (-1, -1), 8.2),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(timetable_table)

    story.append(Spacer(1, 16))
    story.append(Paragraph("Stay consistent. Small progress still counts.", small_style))
    doc.build(story, onFirstPage=draw_pdf_background, onLaterPages=draw_pdf_background)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ---------------------------------
# Auth UI
# ---------------------------------
def login_view():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-title">🔐 Smart Planner Access</div>
        <div class="login-subtitle">
            Login or create an account to access your revision dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)

    mode_col1, mode_col2, mode_col3 = st.columns([1, 1, 1])
    with mode_col2:
        st.radio(
            "Choose access mode",
            ["login", "signup"],
            key="auth_mode",
            horizontal=True,
            label_visibility="collapsed"
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "login":
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", type="primary", use_container_width=True):
                if username in st.session_state.users and st.session_state.users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.full_name = st.session_state.users[username]["full_name"]
                    st.session_state.current_page = "Home"
                    ensure_user_data(username)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            with st.expander("Demo account"):
                st.write("Username: `student`")
                st.write("Password: `revision123`")

        else:
            full_name = st.text_input("Full Name", key="signup_name")
            username = st.text_input("Choose Username", key="signup_user")
            password = st.text_input("Choose Password", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

            if st.button("Create Account", type="primary", use_container_width=True):
                if not full_name or not username or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif username in st.session_state.users:
                    st.error("Username already exists.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    st.session_state.users[username] = {
                        "password": password,
                        "full_name": full_name
                    }
                    ensure_user_data(username)
                    st.success("Account created successfully. Please switch to login and sign in.")

# ---------------------------------
# Sidebar navigation
# ---------------------------------
def sidebar_panel():
    with st.sidebar:
        ensure_user_data(st.session_state.username)

        st.markdown("## 🌙 Planner Panel")
        st.write(f"Logged in as **{st.session_state.username}**")
        st.caption(f"Name: {st.session_state.full_name}")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Home", "Planner", "History", "Profile", "Downloads"],
            index=["Home", "Planner", "History", "Profile", "Downloads"].index(st.session_state.current_page)
        )
        st.session_state.current_page = page

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.full_name = ""
            st.session_state.current_page = "Home"
            st.rerun()

        st.markdown("---")
        st.markdown("### ✨ Cute focus tips")
        st.caption("Start with the hardest topic first.")
        st.caption("Short sessions are still productive.")
        st.caption("Consistency beats panic revision.")

# ---------------------------------
# Pages
# ---------------------------------
def home_page():
    ensure_user_data(st.session_state.username)

    st.markdown(f"""
    <div class="hero-box">
        <div class="main-title">📚 Smart Revision Planner</div>
        <div class="subtitle">
            Welcome back, <b>{st.session_state.full_name}</b>. This is your smart revision space.
        </div>
    </div>
    """, unsafe_allow_html=True)

    progress_summary = None
    settings = st.session_state.user_settings[st.session_state.username]

    if st.session_state.last_plan_data:
        progress_summary = get_progress_summary(
            st.session_state.username,
            st.session_state.last_plan_data["timetable_df"]
        )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="mini-card">
            <h4>🌷 What you can do here</h4>
            <p>Create smart study plans, save full plans, reopen old plans, import/export JSON, track progress, and export reports.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        history_count = len(st.session_state.planner_history.get(st.session_state.username, []))
        streak_text = f"{progress_summary['current_streak']} day(s)" if progress_summary else "0 day(s)"
        st.markdown(f"""
        <div class="mini-card">
            <h4>📌 Your activity</h4>
            <p>You have <b>{history_count}</b> saved full plans.</p>
            <p>Your current streak is <b>{streak_text}</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    if progress_summary:
        st.markdown("<hr>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completed Sessions", f"{progress_summary['completed_sessions']}/{progress_summary['total_sessions']}")
        m2.metric("Progress", f"{progress_summary['completion_percent']}%")
        m3.metric("Level", progress_summary["level"])
        m4.metric("XP", progress_summary["xp"])

        st.markdown(
            f"<div class='feedback-box'><b>Motivation:</b><br>{get_motivation_message(settings['motivational_mode'], progress_summary['completion_percent'], progress_summary['current_streak'])}</div>",
            unsafe_allow_html=True
        )

    if st.button("Go to Planner", type="primary"):
        st.session_state.current_page = "Planner"
        st.rerun()

def profile_page():
    ensure_user_data(st.session_state.username)

    st.subheader("👤 Profile & Settings")
    settings = st.session_state.user_settings[st.session_state.username]

    st.markdown(f"""
    <div class="profile-box">
        <h4>Account Details</h4>
        <p><b>Full Name:</b> {st.session_state.full_name}</p>
        <p><b>Username:</b> {st.session_state.username}</p>
        <p><b>Theme:</b> {settings['theme_name']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='settings-box'><h4>Study Preferences</h4></div>", unsafe_allow_html=True)

    session_length = st.selectbox(
        "Preferred session length (minutes)",
        [30, 45, 60, 90],
        index=[30, 45, 60, 90].index(settings["preferred_session_length"])
    )

    daily_goal = st.number_input(
        "Daily study goal (minutes)",
        min_value=30,
        max_value=600,
        value=settings["daily_study_goal_minutes"],
        step=30
    )

    motivational_mode = st.selectbox(
        "Motivational mode",
        ["Cute", "Strict", "Balanced"],
        index=["Cute", "Strict", "Balanced"].index(settings["motivational_mode"])
    )

    if st.button("Save Preferences", type="primary"):
        st.session_state.user_settings[st.session_state.username]["preferred_session_length"] = session_length
        st.session_state.user_settings[st.session_state.username]["daily_study_goal_minutes"] = daily_goal
        st.session_state.user_settings[st.session_state.username]["motivational_mode"] = motivational_mode
        st.success("Preferences saved successfully.")
        st.rerun()

    if st.session_state.last_plan_data:
        progress_summary = get_progress_summary(
            st.session_state.username,
            st.session_state.last_plan_data["timetable_df"]
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='level-box'><h4>⭐ Your Study Level</h4><p><b>Level {progress_summary['level']}</b> • XP: <b>{progress_summary['xp']}</b> • XP to next level: <b>{progress_summary['xp_to_next_level']}</b></p></div>",
            unsafe_allow_html=True
        )

        st.markdown("### 🏆 Earned Badges")
        if progress_summary["badges"]:
            for badge in progress_summary["badges"]:
                st.markdown(f"<div class='badge-box'>{badge}</div>", unsafe_allow_html=True)
        else:
            st.info("No badges yet. Complete sessions to unlock them.")

def history_page():
    ensure_user_data(st.session_state.username)

    st.subheader("🕰 Saved Plans")
    history = st.session_state.planner_history.get(st.session_state.username, [])

    upload_file = st.file_uploader("Import full plan JSON", type=["json"])
    if upload_file is not None:
        imported_plan, error = import_plan_json(upload_file)
        if error:
            st.error(error)
        else:
            st.session_state.planner_history[st.session_state.username].append(imported_plan)
            st.success("Plan imported successfully.")
            st.rerun()

    if not history:
        st.info("No saved plans yet. Generate a plan first.")
        return

    for idx, plan in enumerate(reversed(history)):
        actual_index = len(history) - 1 - idx
        summary = plan.get("summary_values", {})

        st.markdown("<div class='history-card'>", unsafe_allow_html=True)
        st.markdown(f"### 📘 Plan {actual_index + 1}")
        st.write(f"**Saved at:** {plan.get('saved_at', '-')}")
        st.write(f"**Top Subject:** {summary.get('most_prioritized_subject', '-')}")
        st.write(f"**Weakest Topic:** {summary.get('weakest_topic', '-')}")
        st.write(f"**Total Topics:** {summary.get('total_topics', '-')}")
        st.write(f"**Study Time:** {summary.get('total_study_time', '-')}")
        st.write(f"**Readiness:** {summary.get('overall_readiness', '-')}%")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(f"Open Plan {actual_index}", key=f"open_{actual_index}"):
                load_plan_into_session(plan)
                st.session_state.current_page = "Planner"
                st.success("Plan loaded successfully.")
                st.rerun()

        with c2:
            json_bytes = export_plan_json(plan)
            st.download_button(
                label=f"Export JSON {actual_index}",
                data=json_bytes,
                file_name=f"smart_revision_plan_{plan.get('plan_id', actual_index)}.json",
                mime="application/json",
                key=f"export_{actual_index}"
            )

        with c3:
            if st.button(f"Delete Plan {actual_index}", key=f"delete_{actual_index}"):
                st.session_state.planner_history[st.session_state.username].pop(actual_index)
                st.success("Plan deleted successfully.")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Clear All Saved Plans"):
        st.session_state.planner_history[st.session_state.username] = []
        st.success("All saved plans cleared.")
        st.rerun()

def planner_page():
    ensure_user_data(st.session_state.username)

    st.subheader("🧠 Build Your Revision Plan")
    settings = st.session_state.user_settings[st.session_state.username]

    top_col1, top_col2, top_col3 = st.columns([1, 1, 1])
    with top_col1:
        use_sample = st.checkbox("Load sample demo data")
    with top_col2:
        show_fun_mode = st.checkbox("Cute mode visuals", value=True)
    with top_col3:
        if st.button("Reset Form"):
            st.rerun()

    if use_sample:
        subjects_data = load_sample_data()
        st.info("Sample data loaded. Click the button below to generate the planner.")
    else:
        num_subjects = st.number_input(
            "How many subjects do you want to enter?",
            min_value=1, max_value=10, value=2, step=1
        )
        subjects_data = []

        for s in range(num_subjects):
            st.markdown(f"<div class='section-card'><h3>Subject {s+1}</h3></div>", unsafe_allow_html=True)

            subject_name = st.text_input(
                f"Enter subject name for Subject {s+1}",
                key=f"subject_name_{s}"
            ).strip()

            col1, col2 = st.columns(2)
            with col1:
                time_value = st.number_input(
                    f"Enter time left before exam for Subject {s+1}",
                    min_value=1, value=7, step=1, key=f"time_value_{s}"
                )
            with col2:
                time_unit = st.selectbox(
                    f"Select time unit for Subject {s+1}",
                    ["Day(s)", "Week(s)", "Month(s)"],
                    key=f"time_unit_{s}"
                )

            days_left = convert_to_days(time_value, time_unit)

            num_topics = st.number_input(
                f"How many topics for Subject {s+1}?",
                min_value=1, max_value=10, value=2, step=1, key=f"num_topics_{s}"
            )

            topics = []
            seen_topics = set()

            for t in range(num_topics):
                st.markdown(f"**Topic {t+1}**")
                topic_col1, topic_col2 = st.columns(2)
                with topic_col1:
                    topic_name = st.text_input(
                        f"Enter topic {t+1} name",
                        key=f"topic_name_{s}_{t}"
                    ).strip()
                with topic_col2:
                    weakness_level = st.slider(
                        f"Weakness level for Topic {t+1}",
                        min_value=1, max_value=5, value=3, key=f"weakness_{s}_{t}"
                    )

                if topic_name:
                    topic_key = topic_name.lower()
                    if topic_key not in seen_topics:
                        topics.append((topic_name, weakness_level))
                        seen_topics.add(topic_key)

            if subject_name:
                subjects_data.append({
                    "subject_name": subject_name,
                    "days_left": days_left,
                    "topics": topics
                })

    generate = st.button("Generate Smart Revision Plan", type="primary")

    if generate:
        if len(subjects_data) == 0:
            st.error("Please enter at least one subject.")
            return

        result = process_all_subjects(subjects_data)
        if "error" in result:
            st.error(result["error"])
            return

        all_subject_results = result["all_subject_results"]
        topic_df = flatten_topics(all_subject_results)
        timetable_df = generate_study_timetable(
            topic_df,
            start_date=date.today(),
            preferred_session_length=settings["preferred_session_length"]
        )
        today_focus = get_today_focus(topic_df)

        total_topics = len(topic_df)
        total_minutes = int(topic_df["Recommended Minutes"].sum()) if not topic_df.empty else 0
        most_prioritized_subject = all_subject_results[0]["subject_name"]
        weakest_topic_row = topic_df.sort_values(
            by=["Weakness Level", "Recommended Minutes"],
            ascending=[False, False]
        ).iloc[0]
        weakest_topic = f"{weakest_topic_row['Topic']} ({weakest_topic_row['Subject']})"
        overall_readiness = int(sum(s["readiness_score"] for s in all_subject_results) / len(all_subject_results))

        summary_values = {
            "most_prioritized_subject": most_prioritized_subject,
            "weakest_topic": weakest_topic,
            "total_topics": total_topics,
            "total_study_time": format_minutes(total_minutes),
            "overall_readiness": overall_readiness
        }

        st.session_state.user_progress[st.session_state.username]["plans_generated"] += 1

        st.session_state.last_plan_data = {
            "all_subject_results": all_subject_results,
            "topic_df": topic_df,
            "timetable_df": timetable_df,
            "summary_values": summary_values,
            "today_focus": today_focus,
            "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        plan_snapshot = build_plan_snapshot(
            st.session_state.username,
            summary_values,
            subjects_data,
            all_subject_results,
            topic_df,
            timetable_df,
            today_focus
        )
        save_full_plan_entry(st.session_state.username, plan_snapshot)

        if overall_readiness >= 80 and show_fun_mode:
            st.balloons()

        st.success("Your smart revision plan has been generated and saved as a full reusable plan.")
        st.rerun()

    plan = st.session_state.last_plan_data
    if not plan:
        return

    all_subject_results = plan["all_subject_results"]
    topic_df = plan["topic_df"]
    timetable_df = plan["timetable_df"]
    summary_values = plan["summary_values"]
    today_focus = plan["today_focus"]

    total_topics = summary_values["total_topics"]
    total_minutes = int(topic_df["Recommended Minutes"].sum()) if not topic_df.empty else 0
    overall_readiness = summary_values["overall_readiness"]
    progress_summary = get_progress_summary(st.session_state.username, timetable_df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Top Subject", shorten_text(summary_values["most_prioritized_subject"]))
    c2.metric("Weakest Topic", shorten_text(summary_values["weakest_topic"]))
    c3.metric("Total Topics", total_topics)
    c4.metric("Study Time", format_minutes(total_minutes))
    c5.metric("Readiness", f"{overall_readiness}%")

    st.markdown("<hr>", unsafe_allow_html=True)

    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Completed", f"{progress_summary['completed_sessions']}/{progress_summary['total_sessions']}")
    p2.metric("Progress", f"{progress_summary['completion_percent']}%")
    p3.metric("XP", progress_summary["xp"])
    p4.metric("Level", progress_summary["level"])
    p5.metric("Streak", f"{progress_summary['current_streak']} day(s)")

    st.progress(progress_summary["completion_percent"] / 100)

    st.markdown(
        f"<div class='feedback-box'><b>Motivation:</b><br>{get_motivation_message(settings['motivational_mode'], progress_summary['completion_percent'], progress_summary['current_streak'])}</div>",
        unsafe_allow_html=True
    )

    mini1, mini2 = st.columns(2)
    with mini1:
        mood_text = get_study_mood(overall_readiness)
        st.markdown(
            f"<div class='mini-card'><h4>🌷 Planner Status</h4><p>{mood_text}</p><p>Your current readiness is <b>{overall_readiness}%</b>.</p></div>",
            unsafe_allow_html=True
        )
    with mini2:
        if today_focus:
            st.markdown(
                f"<div class='mini-card'><h4>🎯 Today's Focus</h4><p><b>{today_focus['topic']}</b> — {today_focus['subject']}</p><p>Reason: {today_focus['reason']}</p></div>",
                unsafe_allow_html=True
            )

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 Dashboard",
        "✅ Daily Checklist",
        "📌 Subjects",
        "🗓 Timetable"
    ])

    with tab1:
        dash_col1, dash_col2 = st.columns(2)
        with dash_col1:
            st.markdown("<div class='section-card'><b>Subject Priority Score</b></div>", unsafe_allow_html=True)
            subject_chart_df = pd.DataFrame([
                {"Subject": f"{s['subject_icon']} {s['subject_name']}", "Priority Score": s["subject_priority_score"]}
                for s in all_subject_results
            ])
            st.bar_chart(subject_chart_df.set_index("Subject"))

        with dash_col2:
            st.markdown("<div class='section-card'><b>Topic Weakness Level</b></div>", unsafe_allow_html=True)
            weakness_chart_df = topic_df[["Topic", "Weakness Level"]].copy()
            st.bar_chart(weakness_chart_df.set_index("Topic"))

        st.markdown("<hr>", unsafe_allow_html=True)

        low1, low2 = st.columns(2)
        with low1:
            st.markdown("<div class='section-card'><b>Workload by Subject</b></div>", unsafe_allow_html=True)
            workload_df = get_workload_by_subject(topic_df)
            st.bar_chart(workload_df.set_index("Subject"))
        with low2:
            st.markdown("<div class='section-card'><b>Focus Distribution</b></div>", unsafe_allow_html=True)
            focus_df = get_focus_distribution(topic_df)
            st.bar_chart(focus_df.set_index("Category"))

        st.markdown("<hr>", unsafe_allow_html=True)

        extra1, extra2, extra3 = st.columns(3)
        extra1.markdown(
            f"<div class='progress-card'><h4>🔥 Current Streak</h4><p><b>{progress_summary['current_streak']}</b> day(s)</p></div>",
            unsafe_allow_html=True
        )
        extra2.markdown(
            f"<div class='progress-card'><h4>🏆 Best Streak</h4><p><b>{progress_summary['best_streak']}</b> day(s)</p></div>",
            unsafe_allow_html=True
        )
        extra3.markdown(
            f"<div class='progress-card'><h4>🎖 Badges</h4><p><b>{len(progress_summary['badges'])}</b> unlocked</p></div>",
            unsafe_allow_html=True
        )

        st.markdown("### 🏅 Badges")
        if progress_summary["badges"]:
            for badge in progress_summary["badges"]:
                st.markdown(f"<div class='badge-box'>{badge}</div>", unsafe_allow_html=True)
        else:
            st.info("Complete sessions to unlock badges.")

    with tab2:
        st.markdown("### ✅ Daily Study Checklist")

        available_dates = sorted(timetable_df["Calendar Date"].unique().tolist())
        today_str = date.today().strftime("%Y-%m-%d")
        default_index = available_dates.index(today_str) if today_str in available_dates else 0

        selected_date = st.selectbox(
            "Choose checklist date",
            options=available_dates,
            index=default_index
        )

        action1, action2, action3 = st.columns(3)
        with action1:
            if st.button("Mark All Completed"):
                mark_all_for_date(st.session_state.username, timetable_df, selected_date, completed=True)
                st.success("All sessions for selected date marked completed.")
                st.rerun()
        with action2:
            if st.button("Unmark All"):
                mark_all_for_date(st.session_state.username, timetable_df, selected_date, completed=False)
                st.success("All sessions for selected date unmarked.")
                st.rerun()
        with action3:
            if st.button("Reset All Progress"):
                reset_all_progress(st.session_state.username)
                st.success("All progress has been reset.")
                st.rerun()

        daily_df = timetable_df[timetable_df["Calendar Date"] == selected_date].copy()

        if daily_df.empty:
            st.info("No sessions scheduled for this date.")
        else:
            completed_count = 0

            for _, row in daily_df.iterrows():
                session_id = row["Session ID"]
                is_done = get_session_completed(st.session_state.username, session_id)

                st.markdown("<div class='checklist-card'>", unsafe_allow_html=True)
                st.markdown(
                    f"**{row['Session ID']} • {row['Subject']}**  \n"
                    f"Topic: **{row['Topic']}**  \n"
                    f"Duration: **{row['Study Duration']}**  \n"
                    f"Method: **{row['Study Method']}**  \n"
                    f"{get_completion_badge(is_done)}",
                    unsafe_allow_html=True
                )

                checked = st.checkbox(
                    f"Mark {session_id} as completed",
                    value=is_done,
                    key=f"check_{session_id}"
                )

                if checked != is_done:
                    set_session_completed(st.session_state.username, session_id, checked)
                    st.rerun()

                if checked:
                    completed_count += 1

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            percent = int((completed_count / len(daily_df)) * 100) if len(daily_df) > 0 else 0
            c1, c2, c3 = st.columns(3)
            c1.metric("Sessions for Selected Date", len(daily_df))
            c2.metric("Completed", completed_count)
            c3.metric("Daily Completion", f"{percent}%")

            st.progress(percent / 100)

    with tab3:
        for i, subject in enumerate(all_subject_results, start=1):
            st.markdown("<div class='subject-card'>", unsafe_allow_html=True)
            st.markdown(
                f"## {subject['subject_icon']} Subject Rank {i}: {subject['subject_name']} " + get_priority_badge(subject["exam_priority"]),
                unsafe_allow_html=True
            )

            info1, info2, info3, info4, info5 = st.columns(5)
            info1.markdown(
                f"<div class='small-label'>Days Left</div><div class='big-value'>{subject['days_left']} day(s)</div>",
                unsafe_allow_html=True
            )
            info2.markdown(
                f"<div class='small-label'>Exam Priority</div><div class='big-value'>{subject['exam_priority']}</div>",
                unsafe_allow_html=True
            )
            info3.markdown(
                f"<div class='small-label'>Top Topic</div><div class='big-value'>{subject['most_prioritized_topic']}</div>",
                unsafe_allow_html=True
            )
            info4.markdown(
                f"<div class='small-label'>Readiness</div><div class='big-value'>{subject['readiness_score']}%</div>",
                unsafe_allow_html=True
            )
            info5.markdown(
                f"<div class='small-label'>Status</div><div class='big-value'>{subject['readiness_status']}</div>",
                unsafe_allow_html=True
            )

            st.markdown("### Topic Suggestions")
            for j, topic in enumerate(subject["topic_suggestions"], start=1):
                with st.expander(f"Topic {j}: {topic['topic']}"):
                    st.write(f"**Weakness Level:** {topic['weakness_level']}")
                    st.progress(topic["weakness_level"] / 5)
                    st.write(f"**Recommended Study Duration:** {format_minutes(topic['recommended_minutes'])}")
                    st.write(f"**Study Method:** {topic['study_method']}")
                    st.write(f"**Reminder:** {topic['reminder']}")
                    st.write(f"**Suggestion:** {topic['suggestion']}")
                    st.write(f"**Best Tip:** {topic['best_tip']}")
            st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        if timetable_df.empty:
            st.info("No timetable generated.")
        else:
            display_df = timetable_df.copy()
            display_df["Completed"] = display_df["Session ID"].apply(
                lambda x: "Yes" if get_session_completed(st.session_state.username, x) else "No"
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)

def downloads_page():
    ensure_user_data(st.session_state.username)

    st.subheader("📥 Downloads")
    plan = st.session_state.last_plan_data

    if not plan:
        st.info("No generated planner found yet. Go to Planner first.")
        return

    summary_values = plan["summary_values"]
    timetable_df = plan["timetable_df"]
    all_subject_results = plan["all_subject_results"]
    progress_summary = get_progress_summary(st.session_state.username, timetable_df)

    overall_readiness = summary_values["overall_readiness"]
    if overall_readiness >= 80:
        feedback_text = "You're in a strong position. Stay consistent and keep revising smartly."
    elif overall_readiness >= 50:
        feedback_text = "You're doing okay, but some topics still need more focus."
    else:
        feedback_text = "Your exam is getting close, so focus on the weakest and most urgent topics first."

    st.markdown(
        f"<div class='feedback-box'><b>Personalized Feedback:</b><br>{feedback_text}</div>",
        unsafe_allow_html=True
    )

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Progress", f"{progress_summary['completion_percent']}%")
    p2.metric("Completed Sessions", f"{progress_summary['completed_sessions']}/{progress_summary['total_sessions']}")
    p3.metric("Current Streak", f"{progress_summary['current_streak']} day(s)")
    p4.metric("Level", progress_summary["level"])

    pdf_bytes = build_revision_pdf(all_subject_results, summary_values, timetable_df, progress_summary)
    txt_data = create_download_text(all_subject_results, summary_values, timetable_df, progress_summary)
    csv_data = timetable_df.assign(
        Completed=timetable_df["Session ID"].apply(
            lambda x: "Yes" if get_session_completed(st.session_state.username, x) else "No"
        )
    ).to_csv(index=False).encode("utf-8")

    st.markdown(
        "<div class='download-card'><b>📄 PDF Version</b><br>Best for presentation or saving a polished report.</div>",
        unsafe_allow_html=True
    )
    st.download_button(
        "📄 Download Styled Revision Plan (.pdf)",
        data=pdf_bytes,
        file_name="smart_revision_plan.pdf",
        mime="application/pdf"
    )

    st.markdown(
        "<div class='download-card'><b>📝 TXT Version</b><br>Best for simple quick notes.</div>",
        unsafe_allow_html=True
    )
    st.download_button(
        "📝 Download Revision Plan (.txt)",
        data=txt_data,
        file_name="smart_revision_plan.txt",
        mime="text/plain"
    )

    st.markdown(
        "<div class='download-card'><b>📊 CSV Timetable</b><br>Best for editing schedule data.</div>",
        unsafe_allow_html=True
    )
    st.download_button(
        "📊 Download Timetable (.csv)",
        data=csv_data,
        file_name="study_timetable.csv",
        mime="text/csv"
    )

# ---------------------------------
# Run app
# ---------------------------------
if not st.session_state.logged_in:
    login_view()
else:
    ensure_user_data(st.session_state.username)
    sidebar_panel()

    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Planner":
        planner_page()
    elif st.session_state.current_page == "History":
        history_page()
    elif st.session_state.current_page == "Profile":
        profile_page()
    elif st.session_state.current_page == "Downloads":
        downloads_page()
