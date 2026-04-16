import pandas as pd
from datetime import date, timedelta


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
        return "Active Recall + Practice Questions"
    elif weakness_level == 3:
        return "Concept Review + Short Quiz"
    return "Quick Recap"


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


def process_subject(subject_name, days_left, topics, mode, get_mode_tone_text):
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
        study_method = get_study_method(weakness_level)
        reminder, suggestion, best_tip = get_mode_tone_text(mode, weakness_level, topic_name)

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


def process_all_subjects(subjects_data, mode, get_mode_tone_text):
    all_subject_results = []
    for subject in subjects_data:
        result = process_subject(
            subject["subject_name"],
            subject["days_left"],
            subject["topics"],
            mode,
            get_mode_tone_text
        )
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


def load_sample_data():
    return [
        {"subject_name": "Data Science", "days_left": 7, "topics": [("Data Mining", 5), ("Data Visualization", 2)]},
        {"subject_name": "Database", "days_left": 14, "topics": [("SQL", 4), ("ERD", 3)]},
        {"subject_name": "Artificial Intelligence", "days_left": 3, "topics": [("Neural Networks", 5), ("Search Algorithm", 4)]}
    ]
