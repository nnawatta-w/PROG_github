import json
import os
from pathlib import Path
import tempfile
from datetime import date


DATA_FILE = Path(__file__).resolve().parent / "assignments.json"
PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}


def parse_date(text):
    """Return a date, requiring the exact YYYY-MM-DD format."""
    result = date.fromisoformat(text)
    if result.isoformat() != text:
        raise ValueError("Use YYYY-MM-DD.")
    return result


def load_assignments():
    """Read and validate saved data; a missing file means a fresh start."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            assignments = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(assignments, list):
        raise ValueError("The JSON file must contain a list of assignments.")

    required = {"course", "title", "due_date", "priority", "completed"}
    for number, assignment in enumerate(assignments, start=1):
        if not isinstance(assignment, dict) or set(assignment) != required:
            raise ValueError(f"Assignment {number} has missing or unexpected fields.")
        for field in ("course", "title", "due_date", "priority"):
            if not isinstance(assignment[field], str) or not assignment[field].strip():
                raise ValueError(f"Assignment {number} has an invalid {field}.")
        parse_date(assignment["due_date"])
        if assignment["priority"] not in PRIORITIES.values():
            raise ValueError(f"Assignment {number} has an invalid priority.")
        if not isinstance(assignment["completed"], bool):
            raise ValueError(f"Assignment {number} has an invalid completion status.")
    return assignments


def save_assignments(assignments):
    """Write a temporary file first, then replace the saved file safely."""
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=DATA_FILE.parent,
            prefix=".assignments-", suffix=".tmp", delete=False
        ) as file:
            temporary_path = Path(file.name)
            json.dump(assignments, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temporary_path, DATA_FILE)
        return True
    except OSError as error:
        print(f"Could not save assignments: {error}")
        return False
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass  # A cleanup problem must not hide the original save error.


def read_text(prompt, current=None):
    """Require text when adding; allow Enter to keep a value when editing."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        if current is not None:
            return current
        print("Please enter some text.")


def read_due_date(current=None):
    """Keep asking until the user enters a real date in the right format."""
    prompt = "Due date (YYYY-MM-DD): "
    if current is not None:
        prompt = f"Due date [{current}] (Enter to keep): "
    while True:
        text = input(prompt).strip()
        if not text and current is not None:
            return current
        try:
            return parse_date(text).isoformat()
        except ValueError:
            print("Invalid date. Enter a real date as YYYY-MM-DD, such as 2027-02-28.")


def read_priority(current=None):
    """Accept a priority number or name, ignoring letter case."""
    prompt = "Priority (1 = High, 2 = Medium, 3 = Low): "
    if current is not None:
        prompt = f"Priority [{current}] (1 = High, 2 = Medium, 3 = Low; Enter to keep): "
    while True:
        text = input(prompt).strip()
        if not text and current is not None:
            return current
        if text in PRIORITIES:
            return PRIORITIES[text]
        for priority in PRIORITIES.values():
            if text.lower() == priority.lower():
                return priority
        print("Invalid priority. Choose 1, 2, 3, High, Medium, or Low.")


def assignment_status(assignment):
    """Describe the deadline relative to the computer's local date."""
    if assignment["completed"]:
        return "COMPLETED"
    days_left = (parse_date(assignment["due_date"]) - date.today()).days
    if days_left < 0:
        return "OVERDUE"
    if days_left == 0:
        return "DUE TODAY"
    if days_left <= 7:
        return "UPCOMING (within 7 days)"
    return "PENDING"


def view_assignments(assignments):
    """Show numbered records so long course names and titles remain readable."""
    if not assignments:
        print("\nNo assignments yet. Choose 1 to add one.")
        return
    print("\nYOUR ASSIGNMENTS")
    for number, assignment in enumerate(assignments, start=1):
        print(f"{number}. {assignment['title']} [{assignment_status(assignment)}]")
        print(f"   Course: {assignment['course']}")
        print(f"   Due: {assignment['due_date']} | Priority: {assignment['priority']}")


def select_assignment(assignments):
    """Validate a displayed number and return its index, or None to cancel."""
    view_assignments(assignments)
    if not assignments:
        return None
    while True:
        text = input("Assignment number (0 to cancel): ").strip()
        try:
            number = int(text)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if number == 0:
            print("Cancelled.")
            return None
        if 1 <= number <= len(assignments):
            return number - 1
        print(f"Choose a number from 1 to {len(assignments)}, or 0 to cancel.")


def add_assignment(assignments):
    """Collect a complete record before adding it to the list."""
    assignment = {
        "course": read_text("Course name: "),
        "title": read_text("Assignment title: "),
        "due_date": read_due_date(),
        "priority": read_priority(),
        "completed": False,
    }
    assignments.append(assignment)
    return True


def complete_assignment(assignments):
    """Mark a selected assignment as completed."""
    index = select_assignment(assignments)
    if index is None:
        return False
    if assignments[index]["completed"]:
        print("That assignment is already completed.")
        return False
    assignments[index]["completed"] = True
    return True


def edit_assignment(assignments):
    """Update assignment details, keeping any field left blank."""
    index = select_assignment(assignments)
    if index is None:
        return False
    assignment = assignments[index]
    print("Press Enter to keep the current value for any field.")
    assignment["course"] = read_text(f"Course [{assignment['course']}]: ", assignment["course"])
    assignment["title"] = read_text(f"Title [{assignment['title']}]: ", assignment["title"])
    assignment["due_date"] = read_due_date(assignment["due_date"])
    assignment["priority"] = read_priority(assignment["priority"])
    return True


def delete_assignment(assignments):
    """Delete only after the user explicitly confirms the selected record."""
    index = select_assignment(assignments)
    if index is None:
        return False
    while True:
        answer = input(f"Delete '{assignments[index]['title']}'? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            assignments.pop(index)
            return True
        if answer in ("no", "n"):
            print("Deletion cancelled.")
            return False
        print("Please enter yes or no.")


def sort_assignments(assignments):
    """Sort earliest deadlines first; ISO date strings sort chronologically."""
    if not assignments:
        view_assignments(assignments)
        return False
    assignments.sort(key=lambda assignment: assignment["due_date"])
    return True


def main():
    """Run the menu and save each successful change before accepting it."""
    print("STUDENT ASSIGNMENT TRACKER - The Spirit's Work")
    try:
        assignments = load_assignments()
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        print(f"Could not load {DATA_FILE.name}: {error}")
        print("Your saved file has been left unchanged. Repair it or move it aside before retrying.")
        return

    actions = {
        "1": add_assignment,
        "3": complete_assignment,
        "4": edit_assignment,
        "5": delete_assignment,
        "6": sort_assignments,
    }
    try:
        while True:
            print("\n1. Add assignment\n2. View all assignments\n3. Mark assignment completed")
            print("4. Edit assignment\n5. Delete assignment\n6. Sort by due date\n0. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye! All successful changes have been saved.")
                break
            if choice == "2":
                view_assignments(assignments)
            elif choice in actions:
                # Work on copies so failed saves or interrupted edits lose no saved data.
                updated = [assignment.copy() for assignment in assignments]
                if actions[choice](updated):
                    if save_assignments(updated):
                        assignments = updated
                        print("Change saved.")
                        if choice == "6":
                            view_assignments(assignments)
                    else:
                        print("Change was not applied. Your previous assignments are unchanged.")
            else:
                print("Invalid menu choice. Enter 0, 1, 2, 3, 4, 5, or 6.")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye! Unfinished input was cancelled; earlier changes are already saved.")


if __name__ == "__main__":
    main()
