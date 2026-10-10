import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class SchoolManagementTests(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(main.valid_email("student@example.com"))

    def test_malformed_emails_are_rejected(self):
        for email in (
            "student name@example.com",
            "student@example",
            "@example.com",
            "student@.com",
            "student@example..com",
            "student@exa\nmple.com",
        ):
            with self.subTest(email=email):
                self.assertFalse(main.valid_email(email))

    def test_find_id_is_case_insensitive_and_ignores_outer_spaces(self):
        records = [{"roll_no": "CS101", "name": "Asha"}]
        self.assertEqual(main.find_by_id(records, "roll_no", " cs101 ")["name"], "Asha")

    def test_unknown_id_returns_none(self):
        self.assertIsNone(main.find_by_id([], "roll_no", "CS999"))

    def test_average_for_empty_grades_is_zero(self):
        self.assertEqual(main.calculate_average({}), 0)

    def test_average_for_grades(self):
        self.assertEqual(main.calculate_average({"Math": 80, "Science": 90}), 85)

    def test_student_registration_saves_a_record(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "school_data.json"
            test_data = {"students": [], "teachers": []}
            responses = iter(["CS1", "Asha", "18", "asha@example.com"])
            with patch.object(main, "DATABASE", database), patch.object(main, "data", test_data), patch("builtins.input", side_effect=lambda _prompt: next(responses)):
                main.Student().register()
                loaded = main.load_data()
            self.assertEqual(loaded["students"][0]["roll_no"], "CS1")
            self.assertEqual(loaded["students"][0]["name"], "Asha")

    def test_add_grade_updates_subject_mark(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "school_data.json"
            test_data = {"students": [{"name": "Asha", "age": 18, "email": "asha@example.com", "roll_no": "CS1", "grades": {"Math": 70}}], "teachers": []}
            responses = iter(["CS1", "Math", "88"])
            with patch.object(main, "DATABASE", database), patch.object(main, "data", test_data), patch("builtins.input", side_effect=lambda _prompt: next(responses)):
                main.Student().add_grade()
                loaded = main.load_data()
            self.assertEqual(loaded["students"][0]["grades"]["Math"], 88.0)

    def test_invalid_grade_input_is_reprompted(self):
        responses = iter(["nan", "120", "75"])
        with patch("builtins.input", side_effect=lambda _prompt: next(responses)):
            self.assertEqual(main.ask_mark(), 75.0)

    def test_valid_data(self):
        value = {
            "students": [{"name": "Asha", "age": 18, "email": "asha@example.com", "roll_no": "CS1", "grades": {"Math": 80}}],
            "teachers": [{"name": "Ravi", "age": 35, "email": "ravi@example.com", "emp_id": "T1", "subject": "Math"}],
        }
        self.assertIs(main.validate_data(value), value)

    def test_invalid_grade_in_saved_data_is_rejected(self):
        value = {
            "students": [{"name": "Asha", "age": 18, "email": "asha@example.com", "roll_no": "CS1", "grades": {"Math": 120}}],
            "teachers": [],
        }
        with self.assertRaises(RuntimeError):
            main.validate_data(value)

    def test_duplicate_ids_ignore_case(self):
        value = {
            "students": [
                {"name": "Asha", "age": 18, "email": "asha@example.com", "roll_no": "CS1", "grades": {}},
                {"name": "Aman", "age": 19, "email": "aman@example.com", "roll_no": "cs1", "grades": {}},
            ],
            "teachers": [],
        }
        with self.assertRaises(RuntimeError):
            main.validate_data(value)

    def test_save_and_load_round_trip(self):
        value = {"students": [], "teachers": []}
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "school_data.json"
            with patch.object(main, "DATABASE", database):
                self.assertTrue(main.save_data(value))
                self.assertEqual(main.load_data(), value)
                self.assertTrue(database.exists())

    def test_corrupt_json_is_reported_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "school_data.json"
            database.write_text("{not json", encoding="utf-8")
            with patch.object(main, "DATABASE", database):
                with self.assertRaises(RuntimeError):
                    main.load_data()
                self.assertEqual(database.read_text(encoding="utf-8"), "{not json")


if __name__ == "__main__":
    unittest.main()
