import unittest

from main import find_by_id, valid_email


class SchoolManagementTests(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(valid_email("student@example.com"))

    def test_email_with_spaces_is_invalid(self):
        self.assertFalse(valid_email("student name@example.com"))

    def test_email_without_domain_dot_is_invalid(self):
        self.assertFalse(valid_email("student@example"))

    def test_find_id_is_case_insensitive(self):
        records = [{"roll_no": "CS101", "name": "Asha"}]
        self.assertEqual(find_by_id(records, "roll_no", "cs101")["name"], "Asha")

    def test_unknown_id_returns_none(self):
        self.assertIsNone(find_by_id([], "roll_no", "CS999"))


if __name__ == "__main__":
    unittest.main()
