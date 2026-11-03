"""Endpoint tests using Flask's test client and isolated temporary databases."""

from datetime import date, timedelta
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from main import create_app


class StudyFlowTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.config = {
            "TESTING": True,
            "DATABASE": Path(self.folder.name) / "test.sqlite3",
            "LEGACY_FILE": Path(self.folder.name) / "assignments.json",
        }
        self.app = create_app(self.config)
        self.client = self.app.test_client()

    def record(self, **changes):
        record = {
            "title": "Research paper", "course": "Psychology",
            "due_date": (date.today() + timedelta(days=3)).isoformat(),
            "priority": "medium", "notes": "Read chapter 2 first.",
        }
        record.update(changes)
        return record

    def add(self, **changes):
        response = self.client.post("/api/assignments", json=self.record(**changes))
        self.assertEqual(response.status_code, 201, response.json)
        return response.json["assignment"]

    def listing(self, **filters):
        response = self.client.get("/api/assignments", query_string=filters)
        self.assertEqual(response.status_code, 200, response.json)
        return response.json

    def test_empty_dashboard_and_local_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"StudyFlow", response.data)
        self.assertIn(b'lang="en"', response.data)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        for asset in ("app.js", "styles.css", "icons.svg", "favicon.svg"):
            with self.subTest(asset=asset):
                response = self.client.get("/static/" + asset)
                self.assertEqual(response.status_code, 200)
                response.close()
        data = self.listing()
        self.assertEqual(data["assignments"], [])
        self.assertEqual(data["stats"], {"total": 0, "pending": 0, "completed": 0, "overdue": 0, "upcoming": 0})
        self.assertEqual(data["courses"], [])
        self.assertIsNone(data["next_assignment"])

    def test_create_and_persist_across_app_restart(self):
        assignment = self.add(title="  การบ้าน 📚  ", priority="HIGH")
        self.assertEqual(assignment["title"], "การบ้าน 📚")
        self.assertEqual(assignment["priority"], "high")
        self.assertFalse(assignment["completed"])
        client = create_app(self.config).test_client()
        records = client.get("/api/assignments").json["assignments"]
        self.assertEqual(records, [assignment])

    def test_optional_notes_default_to_empty(self):
        record = self.record()
        del record["notes"]
        response = self.client.post("/api/assignments", json=record)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["assignment"]["notes"], "")

    def test_update_all_fields_and_preserve_completion(self):
        assignment = self.add(completed=True)
        updated = self.record(title="New title", course="Math", due_date="2028-02-29", priority="low", notes="Updated notes")
        response = self.client.patch(f"/api/assignments/{assignment['id']}", json=updated)
        self.assertEqual(response.status_code, 200)
        for field, value in updated.items():
            self.assertEqual(response.json["assignment"][field], value)
        self.assertTrue(response.json["assignment"]["completed"])

    def test_complete_and_reopen_assignment(self):
        assignment = self.add()
        path = f"/api/assignments/{assignment['id']}"
        for completed in (True, False):
            response = self.client.patch(path, json={"completed": completed})
            self.assertEqual(response.status_code, 200)
            self.assertIs(response.json["assignment"]["completed"], completed)
            self.assertEqual(self.listing()["stats"]["completed"], int(completed))

    def test_delete_requires_explicit_confirmation(self):
        assignment = self.add()
        path = f"/api/assignments/{assignment['id']}"
        for payload in ({}, {"confirm": False}, {"confirm": "yes"}, {"confirm": 1}, {"confirm": True, "extra": 1}, []):
            self.assertEqual(self.client.delete(path, json=payload).status_code, 400)
        self.assertEqual(self.listing()["stats"]["total"], 1)
        self.assertEqual(self.client.delete(path, json={"confirm": True}).status_code, 200)
        self.assertEqual(self.listing()["stats"]["total"], 0)
        self.assertEqual(self.client.delete(path, json={"confirm": True}).status_code, 404)

    def test_search_by_title_and_course_ignores_case(self):
        one = self.add(title="Essay", course="History")
        two = self.add(title="Algebra", course="Mathematics")
        self.assertEqual([a["id"] for a in self.listing(q="ESSAY")["assignments"]], [one["id"]])
        self.assertEqual([a["id"] for a in self.listing(q="  math  ")["assignments"]], [two["id"]])
        self.assertEqual(self.listing(q="absent")["assignments"], [])

    def test_combined_filters_and_unfiltered_statistics(self):
        one = self.add(course="Math", priority="high")
        self.add(course="Math", priority="low")
        self.add(course="Art", priority="high", completed=True)
        data = self.listing(status="pending", priority="high", course="Math", q="paper")
        self.assertEqual([a["id"] for a in data["assignments"]], [one["id"]])
        self.assertEqual(data["stats"]["total"], 3)
        self.assertEqual(data["stats"]["pending"], 2)
        self.assertEqual(data["stats"]["completed"], 1)
        self.assertEqual(data["courses"], ["Art", "Math"])

    def test_deadline_boundaries_and_status_filters(self):
        for days in (-1, 0, 1, 7, 8):
            self.add(title=str(days), due_date=(date.today() + timedelta(days=days)).isoformat())
        self.add(title="done", due_date=(date.today() - timedelta(days=20)).isoformat(), completed=True)
        data = self.listing()
        statuses = {a["title"]: a["status"] for a in data["assignments"]}
        self.assertEqual(statuses, {"-1": "overdue", "0": "today", "1": "upcoming", "7": "upcoming", "8": "pending", "done": "completed"})
        self.assertEqual(data["stats"], {"total": 6, "pending": 5, "completed": 1, "overdue": 1, "upcoming": 3})
        for status, expected in (("upcoming", 3), ("overdue", 1), ("today", 1), ("completed", 1), ("pending", 5)):
            with self.subTest(status=status):
                self.assertEqual(len(self.listing(status=status)["assignments"]), expected)
        self.assertEqual(data["next_assignment"]["title"], "-1")

    def test_sort_due_dates_priority_and_newest(self):
        first = self.add(title="Late high", due_date="2028-12-10", priority="high")
        second = self.add(title="Early low", due_date="2028-01-01", priority="low")
        third = self.add(title="Early high", due_date="2028-02-01", priority="high")
        orders = {
            "due_asc": [second, third, first], "due_desc": [first, third, second],
            "priority": [third, first, second], "newest": [third, second, first],
        }
        for sort, records in orders.items():
            with self.subTest(sort=sort):
                self.assertEqual([a["id"] for a in self.listing(sort=sort)["assignments"]], [a["id"] for a in records])

    def test_missing_and_blank_required_fields(self):
        for field in ("title", "course", "due_date", "priority"):
            for value in (None, "", "   "):
                record = self.record()
                if value is None:
                    del record[field]
                else:
                    record[field] = value
                with self.subTest(field=field, value=value):
                    response = self.client.post("/api/assignments", json=record)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.json["fields"])
        self.assertEqual(self.listing()["stats"]["total"], 0)

    def test_invalid_types_and_values_never_create_records(self):
        invalid = [
            ("title", 123), ("course", []), ("notes", {}), ("notes", None),
            ("due_date", 20270101), ("priority", "urgent"), ("completed", "false"),
            ("completed", 1), ("completed", None), ("title", "x" * 161),
            ("course", "x" * 81), ("notes", "x" * 2001),
            ("title", "\ud800"), ("title", "bad\x00text"),
        ]
        for field, value in invalid:
            with self.subTest(field=field, value=repr(value)[:30]):
                response = self.client.post("/api/assignments", json=self.record(**{field: value}))
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json["fields"])
        self.assertEqual(self.listing()["stats"]["total"], 0)

    def test_malformed_and_impossible_dates(self):
        for invalid in ("2027-02-29", "2027-02-30", "2027-13-01", "2027-1-01", "tomorrow", "20270101", "0000-01-01"):
            with self.subTest(invalid=invalid):
                response = self.client.post("/api/assignments", json=self.record(due_date=invalid))
                self.assertEqual(response.status_code, 400)
        self.add(due_date="2028-02-29")

    def test_invalid_update_preserves_saved_values(self):
        original = self.add()
        path = f"/api/assignments/{original['id']}"
        for changes in ({}, {"title": ""}, {"due_date": "2027-02-30"}, {"id": 9}, {"completed": "yes"}):
            self.assertEqual(self.client.patch(path, json=changes).status_code, 400)
            self.assertEqual(self.listing()["assignments"], [original])

    def test_malformed_json_and_non_object_input(self):
        for body in ("{broken", "null", "[]", "123", '"text"', "[" * 1100 + "]" * 1100):
            with self.subTest(body=body[:20]):
                response = self.client.post("/api/assignments", data=body, content_type="application/json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)
        self.assertEqual(self.client.post("/api/assignments", data={"title": "form"}).status_code, 415)

    def test_oversized_request_is_rejected(self):
        response = self.client.post("/api/assignments", json=self.record(notes="x" * 40000))
        self.assertEqual(response.status_code, 413)

    def test_unknown_fields_and_invalid_filters(self):
        self.assertEqual(self.client.post("/api/assignments", json=self.record(extra="value")).status_code, 400)
        for query in (
            {"status": "missing"}, {"priority": "urgent"}, {"sort": "DROP TABLE assignments"},
            {"q": "x" * 161}, {"course": "x" * 81}, {"extra": "1"},
            [("status", "pending"), ("status", "completed")],
        ):
            with self.subTest(query=query):
                response = self.client.get("/api/assignments", query_string=query)
                self.assertEqual(response.status_code, 400)

    def test_missing_and_out_of_range_ids(self):
        for assignment_id in (0, -1, 999, 10 ** 100):
            path = f"/api/assignments/{assignment_id}"
            self.assertEqual(self.client.patch(path, json={"completed": True}).status_code, 404)
            self.assertEqual(self.client.delete(path, json={"confirm": True}).status_code, 404)
        self.assertEqual(self.client.get("/missing").status_code, 404)
        self.assertEqual(self.client.put("/api/assignments", json={}).status_code, 405)

    def test_sql_and_html_input_is_stored_as_text(self):
        payload = "<img src=x onerror=alert(1)> '; DROP TABLE assignments; --"
        self.add(title=payload, course="O'Brien", notes=payload)
        self.assertEqual(self.listing(q="DROP TABLE")["assignments"][0]["title"], payload)
        self.assertEqual(self.listing(course="O'Brien")["stats"]["total"], 1)
        self.add(title="Still works")
        self.assertEqual(self.listing()["stats"]["total"], 2)

    def test_cross_origin_writes_are_rejected(self):
        response = self.client.post("/api/assignments", json=self.record(), headers={"Origin": "https://other.example"})
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/assignments", json=self.record(), headers={"Origin": "http://localhost"})
        self.assertEqual(response.status_code, 201)

    def test_invalid_stored_record_is_hidden_and_preserved(self):
        bad = self.add(title="Damaged record")
        good = self.add(title="Healthy record")
        with sqlite3.connect(self.config["DATABASE"]) as connection:
            connection.execute("UPDATE assignments SET due_date = ? WHERE id = ?", ("not-a-date", bad["id"]))
        data = self.listing()
        self.assertEqual([a["id"] for a in data["assignments"]], [good["id"]])
        self.assertIn("1 invalid", data["warning"])
        self.assertEqual(data["stats"]["total"], 1)
        with sqlite3.connect(self.config["DATABASE"]) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM assignments").fetchone()[0], 2)
        response = self.client.patch(f"/api/assignments/{bad['id']}", json={"completed": True})
        self.assertEqual(response.status_code, 400)
        with sqlite3.connect(self.config["DATABASE"]) as connection:
            self.assertEqual(connection.execute("SELECT completed FROM assignments WHERE id = ?", (bad["id"],)).fetchone()[0], 0)

    def test_database_errors_return_helpful_response(self):
        with patch("main.sqlite3.connect", side_effect=sqlite3.OperationalError("database is locked")):
            response = self.client.get("/api/assignments")
        self.assertEqual(response.status_code, 503)
        self.assertIn("retry", response.json["error"])
        self.assertNotIn("locked", response.json["error"])
        self.assertEqual(self.listing()["stats"]["total"], 0)

    def test_failed_write_is_rolled_back(self):
        # A trigger simulates a database rejecting a write after validation.
        with sqlite3.connect(self.config["DATABASE"]) as connection:
            connection.execute("CREATE TRIGGER reject_insert BEFORE INSERT ON assignments BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
        response = self.client.post("/api/assignments", json=self.record())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.listing()["stats"]["total"], 0)

    def test_database_initialization_error_keeps_page_available(self):
        broken_config = dict(self.config, DATABASE=Path(self.folder.name) / "missing" / "db.sqlite3")
        app = create_app(broken_config)
        client = app.test_client()
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/api/assignments").status_code, 503)

    def test_legacy_import_happens_once_and_original_is_preserved(self):
        legacy = self.record(priority="High", completed=True)
        del legacy["notes"]
        contents = json.dumps([legacy])
        self.config["LEGACY_FILE"].write_text(contents, encoding="utf-8")
        app = create_app(self.config)
        client = app.test_client()
        data = client.get("/api/assignments").json
        self.assertEqual(data["stats"]["total"], 1)
        self.assertTrue(data["assignments"][0]["completed"])
        self.assertEqual(data["assignments"][0]["priority"], "high")
        self.assertIn("Imported 1", data["import_notice"])
        assignment_id = data["assignments"][0]["id"]
        client.delete(f"/api/assignments/{assignment_id}", json={"confirm": True})
        restarted = create_app(self.config).test_client()
        self.assertEqual(restarted.get("/api/assignments").json["stats"]["total"], 0)
        self.assertEqual(self.config["LEGACY_FILE"].read_text(encoding="utf-8"), contents)

    def test_invalid_legacy_json_import_is_all_or_nothing(self):
        for contents in ("{broken", "{}", json.dumps([self.record(), self.record(due_date="invalid")])):
            with self.subTest(contents=contents[:20]):
                self.config["LEGACY_FILE"].write_text(contents, encoding="utf-8")
                app = create_app(self.config)
                data = app.test_client().get("/api/assignments").json
                self.assertEqual(data["stats"]["total"], 0)
                self.assertIn("could not be imported", data["import_notice"])
                self.assertEqual(self.config["LEGACY_FILE"].read_text(encoding="utf-8"), contents)


if __name__ == "__main__":
    unittest.main()
