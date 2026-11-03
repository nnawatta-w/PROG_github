# StudyFlow — Student Assignment Tracker

StudyFlow is a Python Flask web application that helps students organize coursework, track deadlines, and see their progress in one personal study dashboard. Assignment data stays in a local SQLite database, with no account or external service required.

## Problem being solved

Assignments can become difficult to manage when deadlines, course information, and reminders are scattered across different places. StudyFlow brings these details together so students can identify overdue work, plan upcoming tasks, and keep track of completed assignments.

## Features

- Create, edit, and delete assignments with a title, course, due date, priority, and optional notes.
- Mark assignments as completed or reopen them.
- View total, pending, completed, and overdue counts, plus overall completion progress.
- Identify overdue assignments, assignments due today, and deadlines within the next seven days.
- Search by assignment title or course; combine status, priority, and course filters.
- Sort by due date, priority, or recently added assignments.
- Save changes automatically to SQLite and retain them after restarting.
- Use a responsive dashboard with keyboard navigation and accessible form feedback.
- Validate input on the backend and show helpful errors for invalid data or database failures.
- Import valid data from an existing local `assignments.json` once, while preserving the original file.

## Technologies

- **Python 3.9 or newer**
- **Flask** for routes, JSON API endpoints, and Jinja templates
- **Werkzeug** for HTTP exception handling
- **SQLite**, through Python's built-in `sqlite3` module
- **HTML, CSS, JavaScript, and SVG** for the browser interface
- **unittest** and Flask's test client for automated tests

## Installation

Install Python 3.9 or newer and Git, then clone this repository using its GitHub **Code** URL:

```sh
git clone <repository-url>
cd studyflow-assignment-tracker
python3 -m venv .venv
```

Activate the virtual environment on macOS or Linux:

```sh
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```sh
python3 -m pip install -r requirements.txt
```

On Windows, use `python` if `python3` is unavailable. Flask also installs its required supporting packages, including Jinja2. SQLite and the test framework are included with Python. No API keys or environment variables are required.

## Run the application

From the project folder, with the virtual environment activated:

```sh
python3 main.py
```

Keep this terminal running, then open **http://127.0.0.1:5000** in a browser. **http://localhost:5000** also works when localhost resolves to the IPv4 loopback address. On some Macs, localhost may reach a different service over IPv6; use `127.0.0.1` in that case.

The server listens on `127.0.0.1:5000`, with Flask's debugger disabled. Stop it with **Ctrl+C**. If the port is already occupied by another StudyFlow instance, use the running instance or stop it before starting another.

The first run creates `studyflow.sqlite3` automatically beside `main.py`. A fresh clone starts with no assignments. Due-date labels use the computer's local calendar date. This development server is intended for local use; publishing this source repository does not host a live web application.

## Run the tests

```sh
python3 -B -m unittest -v test_studyflow test_assignment_tracker
```

The suite contains **41 tests**: 26 Flask backend tests and 15 tests for the preserved command-line tracker. Tests use isolated temporary databases and files rather than personal assignment data. They cover creation, updates, completion, deletion, persistence, filtering, sorting, date boundaries, input validation, legacy import, and database error handling. Backend tests use Flask's test client and do not open or control a browser.

## Project structure

```text
studyflow-assignment-tracker/
├── README.md                    # Overview, installation, and usage
├── .gitignore                   # Excludes local data and generated files
├── requirements.txt             # Python dependencies
├── main.py                      # Flask app, validation, API, and SQLite storage
├── legacy_tracker.py            # Preserved original command-line tracker
├── test_studyflow.py             # Flask test-client tests
├── test_assignment_tracker.py    # Original tracker regression tests
├── templates/
│   └── index.html               # Dashboard and assignment dialogs
└── static/
    ├── app.js                   # Browser interactions and API requests
    ├── styles.css               # Responsive dashboard styling
    ├── favicon.svg              # Browser icon
    └── icons.svg                # Interface icons
```

To run the original command-line version separately, use `python3 legacy_tracker.py`. It stores its local data in `assignments.json`, which is excluded from Git along with the web application's database.

## Data and repository privacy

Commit source code and documentation only. Virtual environments, `.env` files, credentials, SQLite databases, legacy assignment data, logs, and temporary files are excluded by `.gitignore`. Keep backups of any personal data outside the public repository. Review staged changes before every commit because ignore rules do not remove files that are already tracked.

## Update the repository

Make changes inside this repository folder, run the tests, and review the diff:

```sh
python3 -B -m unittest -v test_studyflow test_assignment_tracker
git status --short
git diff
git add -- <changed-source-files>
git diff --cached
git commit -m "Describe the change"
git push origin main
```

Replace `<changed-source-files>` with the specific safe files you changed. Do not force push or commit local assignment data.

## University submission

Submit the public GitHub repository URL through the university's required submission system. The repository URL gives the instructor access to the source code, setup instructions, and tests. Check that the repository is publicly accessible and that its README and source files appear on the `main` branch before submitting. The local application address (`127.0.0.1:5000`) is for testing on your own computer and is not the submission link.
