# StudySense 📚

A student-focused study tracking web app for managing subjects, tracking study time, and staying on top of revision.

## Features

- 📚 Manage subjects and topics
- ⏱️ Log study sessions
- 📊 Track daily study time and progress
- 🔁 Identify topics due for revision
- 🗑️ Delete subjects and topics
- 💾 Store data using SQLite
- 🌷 Clean and simple student-friendly interface

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja2

## How It Works

StudySense uses Flask to handle the application logic and SQLite to store subjects, topics, and study sessions.

Study sessions are recorded with their date and duration. The dashboard uses this data to calculate daily study time and identify topics that have not been studied for 3 or more days.

## Running the Project

1. Clone the repository.
2. Create a virtual environment.
3. Install the required dependencies:

```bash
pip install -r requirements.txt
