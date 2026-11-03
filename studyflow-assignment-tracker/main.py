# StudyFlow - a local student assignment dashboard for The Spirit's Work.
# Setup (macOS): python3 -m venv .venv
# Then: source .venv/bin/activate && python3 -m pip install -r requirements.txt
# Run: python3 main.py   |   Open: http://localhost:5000
# Uses Flask, HTML/CSS/JavaScript, and built-in SQLite. No accounts needed.

from datetime import date
import json
from pathlib import Path
import sqlite3

from flask import Flask, g, jsonify, render_template, request
from werkzeug.exceptions import HTTPException


BASE_DIR = Path(__file__).resolve().parent
PRIORITIES = ("high", "medium", "low")
FIELDS = {"title", "course", "due_date", "priority", "notes", "completed"}


class ValidationError(ValueError):
    """An input error that can be explained beside the relevant form field."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("Please check the highlighted fields.")


def parse_date(text):
    """Reuse the CLI's strict, real-calendar-date validation."""
    result = date.fromisoformat(text)
    if result.isoformat() != text:
        raise ValueError("Use YYYY-MM-DD.")
    return result


def validate_assignment(data, partial=False):
    """Validate JSON types, required fields, lengths, dates, and priorities."""
    if not isinstance(data, dict):
        raise ValidationError({"form": "Send an assignment as a JSON object."})
    errors = {}
    cleaned = {}
    if set(data) - FIELDS:
        errors["form"] = "The request contains an unknown field."
    if partial and not data:
        errors["form"] = "Include at least one field to update."
    limits = {"title": 160, "course": 80, "due_date": 10, "priority": 10, "notes": 2000}
    for field, limit in limits.items():
        if partial and field not in data:
            continue
        value = data.get(field, "" if field == "notes" else None)
        if not isinstance(value, str):
            errors[field] = "Please enter text."
            continue
        value = value.strip()
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            errors[field] = "Please enter valid Unicode text."
            continue
        if "\x00" in value:
            errors[field] = "Text cannot contain null characters."
            continue
        if not value and field != "notes":
            errors[field] = "This field is required."
        elif len(value) > limit:
            errors[field] = f"Use at most {limit} characters."
        elif field == "due_date":
            try:
                parse_date(value)
            except ValueError:
                errors[field] = "Enter a real date in YYYY-MM-DD format."
        elif field == "priority":
            value = value.lower()
            if value not in PRIORITIES:
                errors[field] = "Choose High, Medium, or Low."
        cleaned[field] = value
    if not partial or "completed" in data:
        completed = data.get("completed", False)
        if type(completed) is not bool:
            errors["completed"] = "Completion must be true or false."
        else:
            cleaned["completed"] = int(completed)
    if errors:
        raise ValidationError(errors)
    return cleaned


def get_db():
    """Open one SQLite connection per request, then reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(str(g.app_database), timeout=5)
        g.db.row_factory = sqlite3.Row
    return g.db


def serialize_assignment(row):
    """Validate stored records too, then add a deadline label for the browser."""
    record = dict(row)
    if type(record.get("id")) is not int or record["id"] <= 0:
        raise ValueError("Invalid assignment ID.")
    if type(record.get("completed")) is not int or record["completed"] not in (0, 1):
        raise ValueError("Invalid stored completion value.")
    record["completed"] = bool(record["completed"])
    cleaned = validate_assignment({field: record[field] for field in FIELDS})
    record.update(cleaned)
    record["completed"] = bool(record["completed"])
    days_left = (parse_date(record["due_date"]) - date.today()).days
    if record["completed"]:
        status = "completed"
    elif days_left < 0:
        status = "overdue"
    elif days_left == 0:
        status = "today"
    elif days_left <= 7:
        status = "upcoming"
    else:
        status = "pending"
    record["status"] = status
    record["days_left"] = days_left
    return record


def init_database(app):
    """Create tables and import valid legacy JSON once, without modifying it."""
    connection = sqlite3.connect(str(app.config["DATABASE"]), timeout=5)
    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
                    course TEXT NOT NULL CHECK(length(trim(course)) BETWEEN 1 AND 80),
                    due_date TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('high', 'medium', 'low')),
                    notes TEXT NOT NULL DEFAULT '' CHECK(length(notes) <= 2000),
                    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1))
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                )
            """)
        legacy_file = Path(app.config["LEGACY_FILE"])
        imported = connection.execute(
            "SELECT value FROM metadata WHERE key = ?", ("legacy_imported",)
        ).fetchone()
        if imported or not legacy_file.is_file():
            return
        try:
            legacy = json.loads(legacy_file.read_text(encoding="utf-8"))
            if not isinstance(legacy, list):
                raise ValueError("The JSON root must be a list.")
            records = []
            for item in legacy:
                # Old files have no notes; the validator supplies the default.
                records.append(validate_assignment(item))
            with connection:
                for record in records:
                    insert_assignment(connection, record)
                connection.execute(
                    "INSERT INTO metadata (key, value) VALUES (?, ?)",
                    ("legacy_imported", "yes"),
                )
            app.config["IMPORT_NOTICE"] = f"Imported {len(records)} assignments from your original tracker."
        except (ValueError, UnicodeError, OSError, RecursionError):
            app.logger.warning("Legacy JSON could not be imported; the original file was preserved.")
            app.config["IMPORT_NOTICE"] = (
                "Your original assignments.json could not be imported. "
                "It is unchanged; check its fields and dates, then restart StudyFlow."
            )
    finally:
        connection.close()


def insert_assignment(connection, record):
    """Use placeholders so user text is always data, never SQL."""
    return connection.execute(
        """INSERT INTO assignments (title, course, due_date, priority, notes, completed)
           VALUES (?, ?, ?, ?, ?, ?)""",
        tuple(record[field] for field in ("title", "course", "due_date", "priority", "notes", "completed")),
    ).lastrowid


def create_app(test_config=None):
    """Build the Flask app; tests can supply a separate temporary database."""
    app = Flask(__name__)
    app.config.update(
        DATABASE=BASE_DIR / "studyflow.sqlite3",
        LEGACY_FILE=BASE_DIR / "assignments.json",
        MAX_CONTENT_LENGTH=32 * 1024,
        IMPORT_NOTICE="",
    )
    if test_config:
        app.config.update(test_config)

    @app.before_request
    def prepare_request():
        g.app_database = app.config["DATABASE"]
        # JSON-only mutations and an origin check protect the local app from
        # another website trying to submit forms to it in the background.
        if request.method in ("POST", "PATCH", "DELETE"):
            origin = request.headers.get("Origin")
            if origin and origin != request.host_url.rstrip("/"):
                return jsonify(error="This request must come from your StudyFlow page."), 403
            if not request.is_json:
                return jsonify(error="Send data as application/json."), 415

    @app.teardown_appcontext
    def close_database(error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(ValidationError)
    def invalid_input(error):
        return jsonify(error=str(error), fields=error.errors), 400

    @app.errorhandler(RecursionError)
    def overly_nested_json(error):
        return jsonify(error="The JSON is nested too deeply. Send a simple assignment object."), 400

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.error("SQLite operation failed: %s", error)
        return jsonify(error="Your database is unavailable. Nothing was changed. Please retry."), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {
            400: "The request could not be read. Send valid JSON.",
            404: "That assignment or page could not be found. Refresh and try again.",
            405: "That action is not supported for this address.",
            413: "This request is too large. Keep notes under 2,000 characters.",
        }
        return jsonify(error=messages.get(error.code, error.description)), error.code

    def find_assignment(assignment_id):
        if assignment_id < 1 or assignment_id > 9223372036854775807:
            return None
        return get_db().execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/assignments")
    def list_assignments():
        allowed = {"q", "status", "priority", "course", "sort"}
        if set(request.args) - allowed or any(len(request.args.getlist(key)) != 1 for key in request.args):
            raise ValidationError({"filters": "Use one value for each supported filter."})
        search = request.args.get("q", "").strip()
        course = request.args.get("course", "").strip()
        status = request.args.get("status", "all")
        priority = request.args.get("priority", "all")
        sort = request.args.get("sort", "due_asc")
        if (len(search) > 160 or len(course) > 80
                or status not in ("all", "pending", "completed", "overdue", "upcoming", "today")
                or priority not in ("all",) + PRIORITIES
                or sort not in ("due_asc", "due_desc", "priority", "newest")):
            raise ValidationError({"filters": "One or more filters are invalid. Reset filters and try again."})

        # Read all valid records once so summary numbers always describe the
        # full workspace, even when the visible assignment list is filtered.
        records = []
        invalid_count = 0
        for row in get_db().execute("SELECT * FROM assignments").fetchall():
            try:
                records.append(serialize_assignment(row))
            except (ValueError, KeyError, TypeError, OverflowError):
                invalid_count += 1
        stats = {
            "total": len(records),
            "pending": sum(not record["completed"] for record in records),
            "completed": sum(record["completed"] for record in records),
            "overdue": sum(record["status"] == "overdue" for record in records),
            "upcoming": sum(record["status"] in ("today", "upcoming") for record in records),
        }
        courses = sorted({record["course"] for record in records}, key=str.casefold)
        selected = []
        for record in records:
            if search and search.casefold() not in (record["title"] + " " + record["course"]).casefold():
                continue
            if course and record["course"] != course:
                continue
            if priority != "all" and record["priority"] != priority:
                continue
            if status == "pending" and record["completed"]:
                continue
            if status == "upcoming" and record["status"] not in ("today", "upcoming"):
                continue
            if status in ("completed", "overdue", "today") and record["status"] != status:
                continue
            selected.append(record)
        if sort in ("due_asc", "due_desc"):
            selected.sort(key=lambda record: (record["due_date"], record["id"]), reverse=sort == "due_desc")
        elif sort == "priority":
            selected.sort(key=lambda record: (PRIORITIES.index(record["priority"]), record["due_date"], record["id"]))
        else:
            selected.sort(key=lambda record: record["id"], reverse=True)
        warning = ""
        if invalid_count:
            warning = f"{invalid_count} invalid stored assignment(s) were hidden. Their database records have been preserved."
        unfinished = [record for record in records if not record["completed"]]
        next_assignment = min(unfinished, key=lambda record: (record["due_date"], record["id"]), default=None)
        return jsonify(
            assignments=selected, stats=stats, courses=courses,
            today=date.today().isoformat(), warning=warning,
            import_notice=app.config["IMPORT_NOTICE"], next_assignment=next_assignment,
        )

    @app.post("/api/assignments")
    def add_assignment():
        record = validate_assignment(request.get_json())
        connection = get_db()
        with connection:
            assignment_id = insert_assignment(connection, record)
            row = connection.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
            result = serialize_assignment(row)
        return jsonify(assignment=result, message="Assignment added. You've got this!"), 201

    @app.patch("/api/assignments/<int:assignment_id>")
    def update_assignment(assignment_id):
        changes = validate_assignment(request.get_json(), partial=True)
        row = find_assignment(assignment_id)
        if row is None:
            return jsonify(error="This assignment no longer exists. Refresh your list."), 404
        # Every column name comes from the fixed validated field allowlist.
        columns = ", ".join(field + " = ?" for field in changes)
        connection = get_db()
        with connection:
            connection.execute(
                "UPDATE assignments SET " + columns + " WHERE id = ?",
                tuple(changes.values()) + (assignment_id,),
            )
            row = connection.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
            try:
                result = serialize_assignment(row)
            except (ValueError, KeyError, TypeError, OverflowError):
                # Roll back if a previously damaged record is still invalid.
                raise ValidationError({"form": "This saved record needs all its details corrected before it can be updated."})
        return jsonify(assignment=result, message="Assignment updated.")

    @app.delete("/api/assignments/<int:assignment_id>")
    def delete_assignment(assignment_id):
        data = request.get_json()
        if not isinstance(data, dict) or set(data) != {"confirm"} or data["confirm"] is not True:
            raise ValidationError({"confirm": "Please confirm before deleting this assignment."})
        if find_assignment(assignment_id) is None:
            return jsonify(error="This assignment no longer exists. Refresh your list."), 404
        connection = get_db()
        with connection:
            connection.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        return jsonify(message="Assignment deleted.")

    try:
        init_database(app)
    except (sqlite3.Error, OSError) as error:
        # Keep serving the page; API calls show a useful retryable error.
        app.logger.error("Database initialization failed: %s", error)
    return app


def main():
    """Start a local-only development server, with the debugger disabled."""
    print("StudyFlow is starting at http://localhost:5000")
    create_app().run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
