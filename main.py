import json
import math
from abc import ABC, abstractmethod
from pathlib import Path

DATABASE = Path("school_data.json")


def valid_email(email):
    email = email.strip()
    if any(char.isspace() for char in email) or email.count("@") != 1:
        return False
    local_part, domain = email.split("@")
    return bool(
        local_part
        and domain
        and "." in domain
        and not domain.startswith(".")
        and not domain.endswith(".")
        and ".." not in domain
    )


def validate_data(data):
    """Check the stored JSON structure before the app uses it."""
    if not isinstance(data, dict):
        raise RuntimeError(f"{DATABASE} must contain a JSON object.")

    data.setdefault("students", [])
    data.setdefault("teachers", [])
    if not isinstance(data["students"], list) or not isinstance(data["teachers"], list):
        raise RuntimeError(f"{DATABASE} has an unexpected format.")

    def check_records(records, id_key, record_type):
        seen_ids = set()
        required = {
            "student": {"name", "age", "email", "roll_no", "grades"},
            "teacher": {"name", "age", "email", "emp_id", "subject"},
        }[record_type]
        for record in records:
            if not isinstance(record, dict) or not required.issubset(record):
                raise RuntimeError(f"{DATABASE} contains an incomplete {record_type} record.")
            for field in ("name", "email", id_key):
                if not isinstance(record[field], str) or not record[field].strip():
                    raise RuntimeError(f"{DATABASE} contains an invalid {field} in a {record_type} record.")
            if not isinstance(record["age"], int) or isinstance(record["age"], bool) or record["age"] <= 0:
                raise RuntimeError(f"{DATABASE} contains an invalid age in a {record_type} record.")
            if not valid_email(record["email"]):
                raise RuntimeError(f"{DATABASE} contains an invalid email in a {record_type} record.")
            record_id = record[id_key].strip().casefold()
            if record_id in seen_ids:
                raise RuntimeError(f"{DATABASE} contains duplicate {id_key} values.")
            seen_ids.add(record_id)

            if record_type == "student":
                grades = record["grades"]
                if not isinstance(grades, dict):
                    raise RuntimeError(f"{DATABASE} contains invalid grades for a student.")
                for subject, mark in grades.items():
                    if not isinstance(subject, str) or not subject.strip():
                        raise RuntimeError(f"{DATABASE} contains an invalid subject name.")
                    if (
                        not isinstance(mark, (int, float))
                        or isinstance(mark, bool)
                        or not math.isfinite(mark)
                        or not 0 <= mark <= 100
                    ):
                        raise RuntimeError(f"{DATABASE} contains marks outside the 0-100 range.")
            elif not isinstance(record["subject"], str) or not record["subject"].strip():
                raise RuntimeError(f"{DATABASE} contains an invalid teacher subject.")

    check_records(data["students"], "roll_no", "student")
    check_records(data["teachers"], "emp_id", "teacher")
    return data


def load_data():
    if not DATABASE.exists():
        return {"students": [], "teachers": []}

    try:
        with DATABASE.open("r", encoding="utf-8") as file:
            stored_data = json.load(file)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"{DATABASE} is not valid JSON. Fix the file before running the program again."
        ) from error
    except OSError as error:
        raise RuntimeError(f"Could not read {DATABASE}: {error}") from error

    return validate_data(stored_data)


def save_data(data):
    temporary_file = DATABASE.with_suffix(".tmp")
    try:
        temporary_file.write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(DATABASE)
        return True
    except (OSError, TypeError, ValueError) as error:
        print(f"Could not save data: {error}")
        try:
            temporary_file.unlink(missing_ok=True)
        except OSError:
            pass
        return False


def ask_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_positive_integer(prompt, current_value=None):
    while True:
        value = input(prompt).strip()
        if not value and current_value is not None:
            return current_value
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("Enter a whole number greater than zero.")


def ask_mark(prompt="Marks (0-100): "):
    while True:
        raw_value = input(prompt).strip()
        try:
            mark = float(raw_value)
            if math.isfinite(mark) and 0 <= mark <= 100:
                return mark
        except ValueError:
            pass
        print("Enter a number from 0 to 100.")


def find_by_id(records, key, value):
    target = value.strip().casefold()
    return next(
        (record for record in records if str(record.get(key, "")).strip().casefold() == target),
        None,
    )


def calculate_average(grades):
    return sum(grades.values()) / len(grades) if grades else 0


class Person(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def show_details(self):
        pass


class Student(Person):
    def get_role(self):
        return "Student"

    def register(self):
        roll_no = ask_non_empty("Roll number: ")
        if find_by_id(data["students"], "roll_no", roll_no):
            print("A student with that roll number already exists.")
            return

        name = ask_non_empty("Student name: ")
        age = ask_positive_integer("Age: ")
        email = ask_non_empty("Email: ")
        if not valid_email(email):
            print("Invalid email address.")
            return

        student = {"name": name, "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        data["students"].append(student)
        if save_data(data):
            print(f"Student {name} registered successfully.")
        else:
            data["students"].remove(student)

    def show_details(self):
        roll_no = ask_non_empty("Roll number: ")
        student = find_by_id(data["students"], "roll_no", roll_no)
        if not student:
            print("Student not found.")
            return

        grades = student["grades"]
        print("\nStudent details")
        print(f"Name: {student['name']}")
        print(f"Roll number: {student['roll_no']}")
        print(f"Age: {student['age']}")
        print(f"Email: {student['email']}")
        print(f"Grades: {grades if grades else 'No grades recorded'}")
        print(f"Average marks: {calculate_average(grades):.2f}")

    def add_grade(self):
        roll_no = ask_non_empty("Roll number: ")
        student = find_by_id(data["students"], "roll_no", roll_no)
        if not student:
            print("Student not found.")
            return

        subject = ask_non_empty("Subject: ")
        mark = ask_mark()
        grades = student["grades"]
        old_mark = grades.get(subject)
        grades[subject] = mark
        if save_data(data):
            action = "updated" if old_mark is not None else "added"
            print(f"Marks {action} successfully.")
        elif old_mark is None:
            grades.pop(subject, None)
        else:
            grades[subject] = old_mark

    def delete(self):
        roll_no = ask_non_empty("Roll number of the student to delete: ")
        student = find_by_id(data["students"], "roll_no", roll_no)
        if not student:
            print("Student not found.")
            return

        confirmation = input(
            f"Delete {student['name']} ({student['roll_no']})? (y/n): "
        ).strip().casefold()
        if confirmation != "y":
            print("Deletion cancelled.")
            return

        original_index = data["students"].index(student)
        data["students"].pop(original_index)
        if save_data(data):
            print("Student record deleted.")
        else:
            data["students"].insert(original_index, student)


class Teacher(Person):
    def get_role(self):
        return "Teacher"

    def register(self):
        emp_id = ask_non_empty("Employee ID: ")
        if find_by_id(data["teachers"], "emp_id", emp_id):
            print("A teacher with that employee ID already exists.")
            return

        name = ask_non_empty("Teacher name: ")
        age = ask_positive_integer("Age: ")
        email = ask_non_empty("Email: ")
        if not valid_email(email):
            print("Invalid email address.")
            return
        subject = ask_non_empty("Subject taught: ")

        teacher = {"name": name, "age": age, "email": email, "subject": subject, "emp_id": emp_id}
        data["teachers"].append(teacher)
        if save_data(data):
            print(f"Teacher {name} registered successfully.")
        else:
            data["teachers"].remove(teacher)

    def show_details(self):
        emp_id = ask_non_empty("Employee ID: ")
        teacher = find_by_id(data["teachers"], "emp_id", emp_id)
        if not teacher:
            print("Teacher not found.")
            return

        print("\nTeacher details")
        print(f"Name: {teacher['name']}")
        print(f"Employee ID: {teacher['emp_id']}")
        print(f"Age: {teacher['age']}")
        print(f"Email: {teacher['email']}")
        print(f"Subject: {teacher['subject']}")


def list_records():
    print("\nStudents")
    if not data["students"]:
        print("No students registered.")
    else:
        for student in data["students"]:
            print(f"{student['roll_no']} | {student['name']} | Age: {student['age']}")

    print("\nTeachers")
    if not data["teachers"]:
        print("No teachers registered.")
    else:
        for teacher in data["teachers"]:
            print(f"{teacher['emp_id']} | {teacher['name']} | Subject: {teacher['subject']}")


def print_menu():
    print("\n=== School Management System ===")
    print("1. Register student")
    print("2. Register teacher")
    print("3. Add or update student marks")
    print("4. Show student details")
    print("5. Show teacher details")
    print("6. List all students and teachers")
    print("7. Delete a student record")
    print("0. Exit")


def main():
    student = Student()
    teacher = Teacher()

    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            student.register()
        elif choice == "2":
            teacher.register()
        elif choice == "3":
            student.add_grade()
        elif choice == "4":
            student.show_details()
        elif choice == "5":
            teacher.show_details()
        elif choice == "6":
            list_records()
        elif choice == "7":
            student.delete()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please select an option from the menu.")


try:
    data = load_data()
except RuntimeError as error:
    print(error)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
