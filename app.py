import streamlit as st
import pandas as pd
from io import StringIO

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="Smart Revision Planner",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------
# Helper functions
# ---------------------------------
def convert_to_days(value, unit):
    if unit == "Day(s)":
        return int(value)
    elif unit == "Week(s)":
        return int(value * 7)
    elif unit == "Month(s)":
        return int(value * 30)
    return int(value)


def format_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0 and remaining_minutes > 0:
        return f"{int(hours)} hour(s) {int(remaining_minutes)} minute(s)"
    elif hours > 0:
        return f"{int(hours)} hour(s)"
    else:
        return f"{int(remaining_minutes)} minute(s)"


def get_priority_details(days_left):
    if days_left <= 3:
        return "Very High", 5, 60
    elif days_left <= 7:
        return "High", 4, 45
    elif days_left <= 14:
        return "Medium", 3, 30
    elif days_left <= 30:
        return "Low", 2, 20
    else:
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
    else:
        return (
            "Quick Recap",
            "Do a recap and review the important points only.",
            "Try a quick quiz, skim notes, or make a simple mind map."
        )


def calculate_readiness_score(days_left, avg_weakness):
    # Higher days left and lower weakness = better readiness
    time_factor = min(days_left / 30, 1.0) * 50
    weakness_factor = ((6 - avg_weakness) / 5) * 50
    score = int(time_factor + weakness_factor)
    return max(0, min(score, 100))


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
            reminder = (
                f"You should study {topic_name} first since your weakness level is high "
                f"and the exam is getting closer."
            )
        elif weakness_level == 3:
            reminder = (
                f"You should give proper attention to {topic_name} because your understanding "
                f"is moderate and still needs improvement."
            )
        else:
            reminder = (
                f"Since your weakness level is lower, you can study {topic_name} more lightly "
                f"because you already have some core understanding."
            )

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

    topic_suggestions.sort(
        key=lambda x: (x["weakness_level"], x["urgency_score"]),
        reverse=True
    )

    highest_weakness = topic_suggestions[0]["weakness_level"]
    avg_weakness = sum(t["weakness_level"] for t in topic_suggestions) / len(topic_suggestions)
    subject_priority_score = round(urgency_score + avg_weakness, 2)
    readiness_score = calculate_readiness_score(days_left, avg_weakness)

    return {
        "subject_name": subject_name,
        "days_left": days_left,
        "exam_priority": exam_priority,
        "subject_priority_score": subject_priority_score,
        "most_prioritized_topic": topic_suggestions[0]["topic"],
        "topic_suggestions": topic_suggestions,
        "average_weakness": round(avg_weakness, 2),
        "readiness_score": readiness_score
    }


def process_all_subjects(subjects_data):
    all_subject_results = []

    for subject in subjects_data:
        result = process_subject(
            subject["subject_name"],
            subject["days_left"],
            subject["topics"]
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


def generate_study_timetable(topic_df):
    if topic_df.empty:
        return pd.DataFrame()

    timetable_rows = []
    day_counter = 1

    sorted_df = topic_df.sort_values(
        by=["Days Left", "Weakness Level", "Recommended Minutes"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    for _, row in sorted_df.iterrows():
        minutes_left = int(row["Recommended Minutes"])

        while minutes_left > 0:
            session_minutes = min(60, minutes_left)
            timetable_rows.append({
                "Day": f"Day {day_counter}",
                "Subject": row["Subject"],
                "Topic": row["Topic"],
                "Study Duration": format_minutes(session_minutes),
                "Study Method": row["Study Method"]
            })
            minutes_left -= session_minutes
            day_counter += 1

    return pd.DataFrame(timetable_rows)


def create_download_text(all_subject_results, summary_values, timetable_df):
    output = StringIO()

    output.write("SMART REVISION PLAN\n")
    output.write("=" * 50 + "\n\n")

    output.write(f"Most Prioritized Subject: {summary_values['most_prioritized_subject']}\n")
    output.write(f"Weakest Topic Overall: {summary_values['weakest_topic']}\n")
    output.write(f"Total Topics: {summary_values['total_topics']}\n")
    output.write(f"Total Recommended Study Time: {summary_values['total_study_time']}\n")
    output.write(f"Overall Readiness Score: {summary_values['overall_readiness']}%\n\n")

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
                f"{row['Day']}: {row['Subject']} - {row['Topic']} - "
                f"{row['Study Duration']} - {row['Study Method']}\n"
            )

    return output.getvalue()


# ---------------------------------
# Sample data
# ---------------------------------
def load_sample_data():
    return [
        {
            "subject_name": "Data Science",
            "days_left": 7,
            "topics": [("Data Mining", 5), ("Data Visualization", 2)]
        },
        {
            "subject_name": "Database",
            "days_left": 14,
            "topics": [("SQL", 4), ("ERD", 3)]
        },
        {
            "subject_name": "Artificial Intelligence",
            "days_left": 3,
            "topics": [("Neural Networks", 5), ("Search Algorithm", 4)]
        }
    ]


# ---------------------------------
# UI
# ---------------------------------
st.title("📚 Smart Revision Planner")
st.write("Plan your study smarter based on exam time, topic weakness, and subject priority.")

use_sample = st.checkbox("Load sample demo data")

if use_sample:
    subjects_data = load_sample_data()
else:
    num_subjects = st.number_input(
        "How many subjects do you want to enter?",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )

    subjects_data = []

    for s in range(num_subjects):
        st.subheader(f"Subject {s+1}")

        subject_name = st.text_input(
            f"Enter subject name for Subject {s+1}",
            key=f"subject_name_{s}"
        ).strip()

        col1, col2 = st.columns(2)

        with col1:
            time_value = st.number_input(
                f"Enter time left before exam for Subject {s+1}",
                min_value=1,
                value=7,
                step=1,
                key=f"time_value_{s}"
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
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            key=f"num_topics_{s}"
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
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"weakness_{s}_{t}"
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

generate = st.button("Generate Smart Revision Plan")

# ---------------------------------
# Results
# ---------------------------------
if generate:
    if len(subjects_data) == 0:
        st.error("Please enter at least one subject.")
    else:
        result = process_all_subjects(subjects_data)

        if "error" in result:
            st.error(result["error"])
        else:
            all_subject_results = result["all_subject_results"]
            topic_df = flatten_topics(all_subject_results)
            timetable_df = generate_study_timetable(topic_df)

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

            st.success("Your smart revision plan has been generated!")

            # Summary metrics
            st.header("📊 Smart Summary Dashboard")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Top Subject", most_prioritized_subject)
            m2.metric("Weakest Topic", weakest_topic)
            m3.metric("Total Topics", total_topics)
            m4.metric("Study Time", format_minutes(total_minutes))
            m5.metric("Readiness", f"{overall_readiness}%")

            # Charts
            st.header("📈 Visual Analytics")

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.subheader("Subject Priority Score")
                subject_chart_df = pd.DataFrame([
                    {
                        "Subject": s["subject_name"],
                        "Priority Score": s["subject_priority_score"]
                    }
                    for s in all_subject_results
                ])
                st.bar_chart(subject_chart_df.set_index("Subject"))

            with chart_col2:
                st.subheader("Topic Weakness Level")
                weakness_chart_df = topic_df[["Topic", "Weakness Level"]].copy()
                st.bar_chart(weakness_chart_df.set_index("Topic"))

            # Ranked suggestions
            st.header("📌 Ranked Revision Suggestions")

            for i, subject in enumerate(all_subject_results, start=1):
                st.markdown("---")
                st.subheader(f"Subject Rank {i}: {subject['subject_name']}")

                info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                info_col1.write(f"**Days Left:** {subject['days_left']} day(s)")
                info_col2.write(f"**Exam Priority:** {subject['exam_priority']}")
                info_col3.write(f"**Top Topic:** {subject['most_prioritized_topic']}")
                info_col4.write(f"**Readiness:** {subject['readiness_score']}%")

                if subject["exam_priority"] == "Very High":
                    st.warning("This subject needs immediate attention.")
                elif subject["exam_priority"] == "High":
                    st.info("This subject should be revised soon.")
                elif subject["exam_priority"] == "Medium":
                    st.info("This subject needs balanced revision.")
                else:
                    st.success("This subject is less urgent for now.")

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

            # Timetable
            st.header("🗓 Automatic Study Timetable")
            if timetable_df.empty:
                st.info("No timetable generated.")
            else:
                st.dataframe(timetable_df, use_container_width=True)

            # Motivational feedback
            st.header("💡 Planner Feedback")
            if overall_readiness >= 80:
                st.success("You're in a strong position. Stay consistent and keep revising smartly.")
            elif overall_readiness >= 50:
                st.info("You're doing okay, but some topics still need more focus.")
            else:
                st.warning("Your exam is getting close, so focus on the weakest and most urgent topics first.")

            # Download button
            download_text = create_download_text(all_subject_results, summary_values, timetable_df)

            st.download_button(
                label="📥 Download Revision Plan",
                data=download_text,
                file_name="smart_revision_plan.txt",
                mime="text/plain"
            )
