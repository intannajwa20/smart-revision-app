from datetime import date, timedelta
import pandas as pd


def ensure_user_data(state, username):
    if username not in state.planner_history:
        state.planner_history[username] = []

    if username not in state.user_progress:
        state.user_progress[username] = {
            "completed_sessions": {},
            "plans_generated": 0
        }

    if username not in state.user_settings:
        state.user_settings[username] = {
            "preferred_session_length": 60,
            "daily_study_goal_minutes": 120,
            "motivational_mode": "Cute",
            "theme_name": "Midnight Violet"
        }


def get_mode_tone_text(mode, weakness_level, topic_name):
    mode = (mode or "Cute").strip()

    if mode == "Cute":
        if weakness_level >= 4:
            reminder = f"You should study {topic_name} first, love. This topic needs extra care because your weakness level is high and the exam is getting close."
            suggestion = "Revise deeply in a calm way, then test yourself with practice questions."
            best_tip = "Use flashcards, active recall, and repeat the hardest parts gently until they feel familiar."
        elif weakness_level == 3:
            reminder = f"{topic_name} still needs proper attention. You’re not lost, but this topic needs more polishing."
            suggestion = "Review the concept clearly, then do a short quiz to check your understanding."
            best_tip = "Use summary notes and mini self-tests to build confidence step by step."
        else:
            reminder = f"You already have some foundation in {topic_name}, so this can be a lighter review."
            suggestion = "Do a quick recap and keep the important points fresh."
            best_tip = "A short quiz, mind map, or note review is enough here."

    elif mode == "Strict":
        if weakness_level >= 4:
            reminder = f"Prioritize {topic_name} immediately. This is a weak area and you cannot afford to delay it."
            suggestion = "Study the full concept properly and complete practice questions after revision."
            best_tip = "Use active recall and repeat difficult questions until you can answer without hesitation."
        elif weakness_level == 3:
            reminder = f"{topic_name} requires proper effort. Your understanding is moderate, not secure."
            suggestion = "Review the concept and test yourself with a short evaluation."
            best_tip = "Do not rely on passive reading. Use short quizzes and self-checks."
        else:
            reminder = f"{topic_name} is relatively stable, but it still needs maintenance."
            suggestion = "Do a focused recap and confirm the core points."
            best_tip = "Keep it concise, but do not ignore it."

    elif mode == "Brutal":
        if weakness_level >= 4:
            reminder = f"{topic_name} is basically waving a red flag at you. Study it first before it embarrasses you in the exam."
            suggestion = "Sit down, suffer productively, and drill this topic with serious practice questions."
            best_tip = "Stop romanticizing being confused. Use active recall until your brain finally gets the memo."
        elif weakness_level == 3:
            reminder = f"{topic_name} is not terrible, but it’s also not giving future genius energy yet."
            suggestion = "Review it properly before it turns into a last-minute regret."
            best_tip = "Quiz yourself now, so you don’t cry over it later."
        else:
            reminder = f"{topic_name} is one of the few things not actively trying to ruin your exam."
            suggestion = "Do a quick recap and move on before you waste too much time here."
            best_tip = "Keep it short. This topic does not need a full emotional documentary."

    else:  # Balanced
        if weakness_level >= 4:
            reminder = f"{topic_name} should be your first priority because your weakness level is high and the exam is approaching."
            suggestion = "Revise the full concept carefully and reinforce it with practice questions."
            best_tip = "Use active recall and focused exercises to improve faster."
        elif weakness_level == 3:
            reminder = f"{topic_name} still needs attention because your understanding is moderate."
            suggestion = "Review the main concepts and check your progress with a short quiz."
            best_tip = "Use summary notes and mini self-tests."
        else:
            reminder = f"{topic_name} is more manageable, so you can treat it as a lighter review."
            suggestion = "Do a quick recap to keep the important points fresh."
            best_tip = "Use a brief quiz, mind map, or short note review."

    return reminder, suggestion, best_tip


def get_mode_feedback_text(mode, overall_readiness):
    mode = (mode or "Cute").strip()

    if mode == "Cute":
        if overall_readiness >= 80:
            return "You’re in a really lovely position right now. Stay consistent and keep revising smartly."
        elif overall_readiness >= 50:
            return "You’re doing okay, but a few topics still need a little more love and attention."
        return "The exam is getting close, so focus gently but seriously on your weakest and most urgent topics first."

    if mode == "Strict":
        if overall_readiness >= 80:
            return "You are in a strong position. Maintain discipline and finish properly."
        elif overall_readiness >= 50:
            return "Your preparation is acceptable, but several weak areas still need direct attention."
        return "Your exam is approaching. Focus immediately on your weakest and most urgent topics."

    if mode == "Brutal":
        if overall_readiness >= 80:
            return "Shockingly impressive. Try not to ruin it now — just stay consistent and finish strong."
        elif overall_readiness >= 50:
            return "You’re surviving, not thriving. Tighten up those weak topics before they humble you."
        return "This is not the time to stare at the ceiling dramatically. Attack the weakest topics first and save yourself."

    if overall_readiness >= 80:
        return "You’re in a strong position. Keep the momentum and revise consistently."
    elif overall_readiness >= 50:
        return "You’re doing fairly well, but some topics still need more focus."
    return "Your exam is getting close, so prioritize the weakest and most urgent topics first."


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

    if mode == "Brutal":
        if progress_percent >= 80:
            return "💀 Wow. Look at you being productive for once. Finish the job."
        if progress_percent >= 50:
            return "⚔️ Not bad. But don’t celebrate like you’ve graduated already."
        if streak >= 3:
            return "🔥 A streak? Suspiciously impressive. Keep moving before the laziness returns."
        return "🚨 Babe, the exam is not scared of you yet. Open the notes and fight back."

    if streak >= 3:
        return "🔥 Consistency looks good on you."
    return "📚 One focused session can change your whole day."


def get_completion_store(state, username):
    ensure_user_data(state, username)
    return state.user_progress[username]["completed_sessions"]


def get_session_completed(state, username, session_id):
    store = get_completion_store(state, username)
    return session_id in store


def set_session_completed(state, username, session_id, is_completed):
    store = get_completion_store(state, username)
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


def get_progress_summary(state, username, timetable_df, format_minutes):
    ensure_user_data(state, username)

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

    store = get_completion_store(state, username)
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


def mark_all_for_date(state, username, timetable_df, selected_date, completed=True):
    daily_df = timetable_df[timetable_df["Calendar Date"] == selected_date]
    for _, row in daily_df.iterrows():
        set_session_completed(state, username, row["Session ID"], completed)


def reset_all_progress(state, username):
    ensure_user_data(state, username)
    state.user_progress[username]["completed_sessions"] = {}


def enrich_timetable_status(state, username, timetable_df):
    if timetable_df is None or timetable_df.empty:
        return pd.DataFrame()

    df = timetable_df.copy()
    today_str = date.today().strftime("%Y-%m-%d")

    def get_status(row):
        completed = get_session_completed(state, username, row["Session ID"])
        if completed:
            return "Completed"
        if row["Calendar Date"] < today_str:
            return "Overdue"
        if row["Calendar Date"] == today_str:
            return "Today"
        return "Upcoming"

    df["Status"] = df.apply(get_status, axis=1)
    return df


def get_overdue_sessions(state, username, timetable_df):
    if timetable_df is None or timetable_df.empty:
        return pd.DataFrame()
    enriched = enrich_timetable_status(state, username, timetable_df)
    return enriched[enriched["Status"] == "Overdue"].copy()


def get_today_sessions(state, username, timetable_df):
    if timetable_df is None or timetable_df.empty:
        return pd.DataFrame()
    enriched = enrich_timetable_status(state, username, timetable_df)
    return enriched[enriched["Status"] == "Today"].copy()


def filter_timetable_df(df, subject_filter="All", status_filter="All", search_text=""):
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()

    if subject_filter != "All":
        filtered = filtered[filtered["Subject"] == subject_filter]

    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]

    if search_text.strip():
        q = search_text.strip().lower()
        filtered = filtered[
            filtered["Subject"].str.lower().str.contains(q, na=False) |
            filtered["Topic"].str.lower().str.contains(q, na=False) |
            filtered["Study Method"].str.lower().str.contains(q, na=False) |
            filtered["Session ID"].str.lower().str.contains(q, na=False)
        ]

    return filtered


def build_calendar_view(df):
    if df is None or df.empty:
        return pd.DataFrame()

    cal = df.groupby("Calendar Date").agg(
        Sessions=("Session ID", "count"),
        Subjects=("Subject", lambda x: ", ".join(sorted(set(x)))),
        Overdue=("Status", lambda x: int((x == "Overdue").sum())),
        Today=("Status", lambda x: int((x == "Today").sum())),
        Completed=("Status", lambda x: int((x == "Completed").sum())),
        Upcoming=("Status", lambda x: int((x == "Upcoming").sum()))
    ).reset_index()

    return cal


def get_daily_goal_progress(state, username, timetable_df, daily_goal_minutes):
    if timetable_df is None or timetable_df.empty:
        return 0, 0

    store = get_completion_store(state, username)
    today_str = date.today().isoformat()

    completed_today_ids = [sid for sid, dt in store.items() if dt == today_str]
    completed_today_df = timetable_df[timetable_df["Session ID"].isin(completed_today_ids)]

    completed_minutes_today = int(completed_today_df["Duration Minutes"].sum()) if not completed_today_df.empty else 0
    percent = min(int((completed_minutes_today / daily_goal_minutes) * 100), 100) if daily_goal_minutes > 0 else 0

    return completed_minutes_today, percent
