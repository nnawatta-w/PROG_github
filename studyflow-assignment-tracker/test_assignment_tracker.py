"""Behavior tests using temporary data files; no external packages needed."""

import contextlib
from datetime import date, timedelta
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import legacy_tracker as tracker


class AssignmentTrackerTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.data_file = Path(self.folder.name) / "assignments.json"
        self.file_patch = patch.object(tracker, "DATA_FILE", self.data_file)
        self.file_patch.start()
        self.addCleanup(self.file_patch.stop)

    def assignment(self, days=0, completed=False):
        return {
            "course": "Python 101",
            "title": "Practice",
            "due_date": (date.today() + timedelta(days=days)).isoformat(),
            "priority": "High",
            "completed": completed,
        }

    def run_menu(self, answers):
        output = io.StringIO()
        with patch("builtins.input", side_effect=answers):
            with contextlib.redirect_stdout(output):
                tracker.main()
        return output.getvalue()

    def run_cli(self, answers):
        # Run the real entry point in a separate process and isolated folder.
        shutil.copyfile(tracker.__file__, Path(self.folder.name) / "main.py")
        result = subprocess.run(
            [sys.executable, "main.py"], input="\n".join(answers) + "\n",
            text=True, capture_output=True, cwd=self.folder.name, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_full_cli_workflow_and_reload(self):
        output = self.run_cli([
            "2",  # Empty list.
            "1", "Python 101", "Essay", "2027-12-20", "1",
            "1", "Math", "Worksheet", "2027-01-10", "3",
            "6",  # Worksheet becomes number 1 after sorting.
            "3", "1",  # Complete the worksheet.
            "4", "2", "Writing", "Revised essay", "2027-11-01", "Medium",
            "5", "1", "no",  # Keep the worksheet.
            "2", "0",
        ])
        self.assertIn("No assignments yet", output)
        self.assertIn("Deletion cancelled", output)
        self.assertIn("[COMPLETED]", output)
        records = tracker.load_assignments()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["title"], "Worksheet")
        self.assertTrue(records[0]["completed"])
        self.assertEqual(records[1], {
            "course": "Writing", "title": "Revised essay",
            "due_date": "2027-11-01", "priority": "Medium", "completed": False,
        })
        # A new process must load the records saved by the first process.
        output = self.run_cli(["2", "5", "1", "yes", "2", "0"])
        self.assertIn("Worksheet [COMPLETED]", output)
        self.assertIn("Revised essay", output)
        self.assertEqual(tracker.load_assignments(), [records[1]])

    def test_invalid_cli_input_recovers(self):
        output = self.run_cli([
            "banana", "7", "-1", "",
            "1", "", "  ", "Science", "", "Report",
            "tomorrow", "2027-02-30", "2027-2-03", "2028-02-29",
            "0", "urgent", "mEdIuM",
            "3", "abc", "1.5", "-1", "99", "1",
            "5", "1", "maybe", "n", "0",
        ])
        for message in (
            "Invalid menu choice", "Please enter some text", "Invalid date",
            "Invalid priority", "Please enter a whole number",
            "Choose a number from", "Please enter yes or no",
        ):
            self.assertIn(message, output)
        record = tracker.load_assignments()[0]
        self.assertEqual(record["due_date"], "2028-02-29")
        self.assertEqual(record["priority"], "Medium")
        self.assertTrue(record["completed"])

    def test_deadline_labels_at_boundaries(self):
        for days, expected in [
            (-1, "OVERDUE"), (0, "DUE TODAY"),
            (1, "UPCOMING (within 7 days)"), (7, "UPCOMING (within 7 days)"),
            (8, "PENDING"),
        ]:
            with self.subTest(days=days):
                self.assertEqual(tracker.assignment_status(self.assignment(days)), expected)
        self.assertEqual(tracker.assignment_status(self.assignment(-10, True)), "COMPLETED")

    def test_dates_validate_leap_year_and_format(self):
        self.assertEqual(tracker.parse_date("2028-02-29"), date(2028, 2, 29))
        for invalid in ("2027-02-29", "2027-13-01", "2027-04-31", "2027-1-01", "", "today"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    tracker.parse_date(invalid)

    def test_save_load_unicode_and_missing_file(self):
        self.assertEqual(tracker.load_assignments(), [])
        record = self.assignment()
        record["title"] = "การบ้าน 📚"
        self.assertTrue(tracker.save_assignments([record]))
        self.assertEqual(tracker.load_assignments(), [record])
        self.assertEqual(list(Path(self.folder.name).glob("*.tmp")), [])

    def test_corrupt_json_is_reported_and_preserved(self):
        for contents in ("{broken", "{}", "[null]", '[{"course": "Math"}]'):
            with self.subTest(contents=contents):
                self.data_file.write_text(contents, encoding="utf-8")
                self.assertIn("Could not load", self.run_menu([]))
                self.assertEqual(self.data_file.read_text(encoding="utf-8"), contents)

    def test_invalid_saved_fields_are_rejected(self):
        for field, invalid in (
            ("course", " "), ("title", 123), ("due_date", "2027-02-30"),
            ("priority", "Urgent"), ("completed", "false"), ("completed", 1),
        ):
            with self.subTest(field=field, invalid=invalid):
                record = self.assignment()
                record[field] = invalid
                self.data_file.write_text(json.dumps([record]), encoding="utf-8")
                with self.assertRaises(ValueError):
                    tracker.load_assignments()

    def test_unreadable_file_is_reported(self):
        with patch.object(Path, "open", side_effect=PermissionError("access denied")):
            self.assertIn("Could not load", self.run_menu([]))

    def test_invalid_file_encoding_is_reported(self):
        self.data_file.write_bytes(b"\xff\xfe")
        self.assertIn("Could not load", self.run_menu([]))
        self.assertEqual(self.data_file.read_bytes(), b"\xff\xfe")

    def test_failed_save_preserves_previous_file_and_cleans_temp(self):
        previous = [self.assignment()]
        self.assertTrue(tracker.save_assignments(previous))
        with patch.object(tracker.os, "replace", side_effect=PermissionError("access denied")):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(tracker.save_assignments([]))
        self.assertEqual(tracker.load_assignments(), previous)
        self.assertEqual(list(Path(self.folder.name).glob("*.tmp")), [])

    def test_failed_save_keeps_menu_list_unchanged(self):
        with patch.object(tracker, "save_assignments", return_value=False):
            output = self.run_menu(["1", "Math", "Quiz", "2027-01-01", "2", "2", "0"])
        self.assertIn("Change was not applied", output)
        self.assertIn("No assignments yet", output)
        self.assertFalse(self.data_file.exists())

    def test_empty_list_actions_and_selection_cancellation(self):
        output = self.run_menu(["2", "3", "4", "5", "6", "0"])
        self.assertEqual(output.count("No assignments yet"), 5)
        self.assertFalse(self.data_file.exists())
        previous = [self.assignment()]
        tracker.save_assignments(previous)
        output = self.run_menu(["3", "0", "4", "0", "5", "0", "0"])
        self.assertEqual(output.count("Cancelled."), 3)
        self.assertEqual(tracker.load_assignments(), previous)

    def test_blank_edit_keeps_fields_and_completion(self):
        previous = [self.assignment(completed=True)]
        tracker.save_assignments(previous)
        self.run_menu(["4", "1", "", "", "", "", "0"])
        self.assertEqual(tracker.load_assignments(), previous)

    def test_completing_completed_assignment_does_not_save(self):
        tracker.save_assignments([self.assignment(completed=True)])
        with patch.object(tracker, "save_assignments") as save:
            output = self.run_menu(["3", "1", "0"])
        self.assertIn("already completed", output)
        save.assert_not_called()

    def test_interrupts_cancel_unfinished_add_and_edit(self):
        previous = [self.assignment()]
        tracker.save_assignments(previous)
        for interruption in (EOFError, KeyboardInterrupt):
            for answers in (
                [interruption], ["1", "Math", interruption],
                ["4", "1", "Changed course", interruption],
                ["5", "1", interruption],
            ):
                with self.subTest(interruption=interruption, answers=answers):
                    self.assertIn("Goodbye!", self.run_menu(answers))
                    self.assertEqual(tracker.load_assignments(), previous)


if __name__ == "__main__":
    unittest.main()
