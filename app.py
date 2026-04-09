import streamlit as st

# -------------------------------
# Helper functions
# -------------------------------

def convert_to_days(value, unit):
    if unit == "Day(s)":
        return value
    elif unit == "Week(s)":
        return value * 7
    elif unit == "Month(s)":
        return value * 30
    else:
        raise ValueError("Invalid time unit.")


def format_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0 and remaining_minutes > 0:
        return f"{int(hours)} hour(s) {int(remaining_minutes)} minute(s)"
    elif hours > 0:
        return f"{int(hours)} hour(s)"
    else:
        return f"{int(remaining_minutes)} minute(s)"


# -------------------------------
# Process one subject
# -------------------------------

def process_subject(subject_name, days_left, topics):
    if days_left <= 0:
        return {"error": f"Time left for subject '{subject_name}' must be greater than 0."}

    if len(topics) == 0:
        return {"error": f"Please enter at least one topic for subject '{subject_name}'."}

    for topic_name, weakness_level in topics:
        if weakness_level < 1 or weakness_level > 5:
            return {"error": f"Weakness level for '{topic_name}' in subject '{subject_name}' must be between 1 and 5."}

    if days_left <= 3:
        exam_priority = "Very High"
        urgency_score = 5
        base_minutes = 60
    elif days_left <= 7:
        exam_priority = "High"
        urgency_score = 4
        base_minutes = 45
    elif days_left <= 14:
        exam_priority = "Medium"
        urgency_score = 3
        base_minutes = 30
    elif days_left <= 30:
        exam_priority = "Low"
        urgency_score = 2
        base_minutes = 20
    else:
        exam_priority = "Very Low"
        urgency_score = 1
        base_minutes = 15

    topic_suggestions = []

    for topic_name, weakness_level in topics:
        recommended_minutes = base_minutes + (weakness_level * 15)

        if weakness_level >= 4:
            reminder = (
                f"You should study {topic_name} first since your weakness level is high "
                f"and the exam is getting closer."
            )
            suggestion = "Revise deeply by chapter and do practice questions."
            best_tip = "Use flashcards and topic-based exercises."
        elif weakness_level == 3:
            reminder = (
                f"You should give proper attention to {topic_name} because your understanding "
                f"is moderate and still needs improvement."
            )
            suggestion = "Review notes, understand key concepts, and do a short quiz."
            best_tip = "Use summary notes and short quizzes."
        else:
            reminder = (
                f"Since your weakness level is lower, you can study {topic_name} more lightly "
                f"because you already have some core understanding."
            )
            suggestion = "Do a recap and review the important points only."
            best_tip = "Try a quick quiz or make a simple mind map."

        topic_suggestions.append({
            "topic": topic_name,
            "weakness_level": weakness_level,
            "recommended_minutes": recommended_minutes,
            "reminder": reminder,
            "suggestion": suggestion,
            "best_tip": best_tip
        })

    topic_suggestions.sort(key=lambda x: x["weakness_level"], reverse=True)

    most_prioritized_topic = topic_suggestions[0]["topic"]
    highest_weakness = topic_suggestions[0]["weakness_level"]

    subject_priority_score = urgency_score + highest_weakness

    return {
        "subject_name": subject_name,
        "days_left": days_left,
        "exam_priority": exam_priority,
        "subject_priority_score": subject_priority_score,
        "most_prioritized_topic": most_prioritized_topic,
        "topic_suggestions": topic_suggestions
    }


# -------------------------------
# Process all subjects
# -------------------------------

def process_all_subjects(subjects_data):
    all_subject_results = []

    for subject in subjects_data:
        subject_name = subject["subject_name"]
        days_left = subject["days_left"]
        topics = subject["topics"]

        result = process_subject(subject_name, days_left, topics)

        if "error" in result:
            return {"error": result["error"]}

        all_subject_results.append(result)

    all_subject_results.sort(key=lambda x: x["subject_priority_score"], reverse=True)

    return {"all_subject_results": all_subject_results}


# -------------------------------
# Streamlit page config
# -------------------------------

st.set_page_config(
    page_title="Smart Revision Planner",
    page_icon="📚",
    layout="wide"
)

# -------------------------------
# Header
# -------------------------------

st.title("📚 Smart Revision Planner")
st.markdown(
    "Plan your revision smarter based on **exam time**, **topic weakness**, and **subject priority**."
)

# -------------------------------
# Subject input
# -------------------------------

num_subjects = st.number_input(
    "How many subjects do you want to enter?",
    min_value=1,
    max_value=10,
    value=2,
    step=1
)

subjects_data = []

for s in range(num_subjects):
    st.markdown("---")
    st.subheader(f"Subject {s+1}")

    subject_name = st.text_input(
        f"Enter subject name for Subject {s+1}",
        key=f"subject_name_{s}"
    )

    col1, col2 = st.columns(2)

    with col1:
        time_value = st.number_input(
            f"Enter time left before exam for {subject_name if subject_name else f'Subject {s+1}'}",
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
        f"How many topics for {subject_name if subject_name else f'Subject {s+1}'}?",
        min_value=1,
        max_value=10,
        value=2,
        step=1,
        key=f"num_topics_{s}"
    )

    topics = []

    for t in range(num_topics):
        st.markdown(f"**Topic {t+1}**")
        topic_col1, topic_col2 = st.columns(2)

        with topic_col1:
            topic_name = st.text_input(
                f"Enter topic {t+1} name",
                key=f"topic_name_{s}_{t}"
            )

        with topic_col2:
            weakness_level = st.slider(
                f"Weakness level for Topic {t+1}",
                min_value=1,
                max_value=5,
                value=3,
                key=f"weakness_{s}_{t}"
            )

        if topic_name.strip():
            topics.append((topic_name.strip(), weakness_level))

    subjects_data.append({
        "subject_name": subject_name.strip() if subject_name else f"Subject {s+1}",
        "days_left": days_left,
        "topics": topics
    })

# -------------------------------
# Generate plan
# -------------------------------

if st.button("Generate Smart Revision Plan"):
    result = process_all_subjects(subjects_data)

    if "error" in result:
        st.error(result["error"])
    else:
        st.success("Your smart revision plan has been generated!")

        st.header("📌 Revision Suggestions")

        for i, subject in enumerate(result["all_subject_results"], start=1):
            st.markdown("---")
            st.subheader(f"Subject Rank {i}: {subject['subject_name']}")
            st.write(f"**Time Left Before Exam:** {subject['days_left']} day(s)")
            st.write(f"**Exam Priority:** {subject['exam_priority']}")
            st.write(f"**Most Prioritized Topic:** {subject['most_prioritized_topic']}")

            st.markdown("### Topic Suggestions")
            for j, topic in enumerate(subject["topic_suggestions"], start=1):
                with st.expander(f"Topic {j}: {topic['topic']}"):
                    st.write(f"**Weakness Level:** {topic['weakness_level']}")
                    st.write(f"**Recommended Study Duration:** {format_minutes(topic['recommended_minutes'])}")
                    st.write(f"**Reminder:** {topic['reminder']}")
                    st.write(f"**Suggestion:** {topic['suggestion']}")
                    st.write(f"**Best Tip:** {topic['best_tip']}")
