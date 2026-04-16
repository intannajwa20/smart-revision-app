import json
from io import StringIO, BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
import pandas as pd


def build_plan_snapshot(state, username, summary_values, subjects_data, all_subject_results, topic_df, timetable_df, today_focus):
    progress_store = state.user_progress.get(username, {}).get("completed_sessions", {})
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


def save_full_plan_entry(state, username, plan_snapshot):
    state.planner_history[username].append(plan_snapshot)


def load_plan_into_session(state, username, plan_entry):
    topic_df = pd.DataFrame(plan_entry.get("topic_df", []))
    timetable_df = pd.DataFrame(plan_entry.get("timetable_df", []))

    state.last_plan_data = {
        "all_subject_results": plan_entry.get("all_subject_results", []),
        "topic_df": topic_df,
        "timetable_df": timetable_df,
        "summary_values": plan_entry.get("summary_values", {}),
        "today_focus": plan_entry.get("today_focus"),
        "generated_on": plan_entry.get("saved_at", "")
    }

    state.user_progress[username]["completed_sessions"] = plan_entry.get("progress_snapshot", {}).copy()


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


def create_download_text(all_subject_results, summary_values, timetable_df, progress_summary, format_minutes):
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


def build_revision_pdf(all_subject_results, summary_values, timetable_df, progress_summary, format_minutes):
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
