from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, datetime

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            minutes INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Get all subjects
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    # Today's study time
    today = date.today().isoformat()

    cursor.execute("""
        SELECT COALESCE(SUM(minutes), 0)
        FROM study_sessions
        WHERE date = ?
    """, (today,))

    today_minutes = cursor.fetchone()[0]

    # Get topics for the dashboard
    cursor.execute("""
        SELECT
            topics.id,
            topics.name,
            subjects.name
        FROM topics
        JOIN subjects
            ON topics.subject_id = subjects.id
        ORDER BY subjects.name, topics.name
    """)

    dashboard_topics = cursor.fetchall()

    # Find topics that may need revision
    cursor.execute("""
        SELECT
            topics.name,
            subjects.name,
            MAX(study_sessions.date)
        FROM topics
        JOIN subjects
            ON topics.subject_id = subjects.id
        LEFT JOIN study_sessions
            ON topics.id = study_sessions.topic_id
        GROUP BY topics.id
        ORDER BY MAX(study_sessions.date) ASC
    """)

    revision_topics = cursor.fetchall()

    conn.close()

    revision_due = []
    today_date = date.today()

    for topic in revision_topics:

        last_studied = topic[2]

        if last_studied:

            last_date = datetime.strptime(
                last_studied,
                "%Y-%m-%d"
            ).date()

            days_since = (today_date - last_date).days

            if days_since >= 3:

                revision_due.append({
                    "topic": topic[0],
                    "subject": topic[1],
                    "days": days_since
                })

    return render_template(
        "index.html",
        subjects=subjects,
        today_minutes=today_minutes,
        revision_due=revision_due,
        dashboard_topics=dashboard_topics
    )


@app.route("/add_subject", methods=["POST"])
def add_subject():

    name = request.form["name"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO subjects (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/subject/<int:subject_id>")
def subject(subject_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM subjects WHERE id = ?",
        (subject_id,)
    )

    subject = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM topics WHERE subject_id = ?",
        (subject_id,)
    )

    topics = cursor.fetchall()

    conn.close()

    return render_template(
        "subject.html",
        subject=subject,
        topics=topics
    )


@app.route("/add_topic/<int:subject_id>", methods=["POST"])
def add_topic(subject_id):

    name = request.form["name"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO topics (subject_id, name)
        VALUES (?, ?)
        """,
        (subject_id, name)
    )

    conn.commit()
    conn.close()

    return redirect(f"/subject/{subject_id}")


@app.route("/add_session/<int:topic_id>", methods=["POST"])
def add_session(topic_id):

    minutes = request.form["minutes"]
    session_date = request.form["date"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO study_sessions
        (topic_id, minutes, date)
        VALUES (?, ?, ?)
        """,
        (topic_id, minutes, session_date)
    )

    conn.commit()
    conn.close()

    return redirect(request.referrer)


@app.route("/delete_topic/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT subject_id FROM topics WHERE id = ?",
        (topic_id,)
    )

    result = cursor.fetchone()

    if result:

        subject_id = result[0]

        cursor.execute(
            "DELETE FROM study_sessions WHERE topic_id = ?",
            (topic_id,)
        )

        cursor.execute(
            "DELETE FROM topics WHERE id = ?",
            (topic_id,)
        )

        conn.commit()
        conn.close()

        return redirect(f"/subject/{subject_id}")

    conn.close()

    return redirect("/")


@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM topics WHERE subject_id = ?",
        (subject_id,)
    )

    topics = cursor.fetchall()

    for topic in topics:

        cursor.execute(
            "DELETE FROM study_sessions WHERE topic_id = ?",
            (topic[0],)
        )

    cursor.execute(
        "DELETE FROM topics WHERE subject_id = ?",
        (subject_id,)
    )

    cursor.execute(
        "DELETE FROM subjects WHERE id = ?",
        (subject_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
