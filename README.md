# School Management System

A beginner-friendly Python command-line project that stores basic student and teacher records in a local JSON file.

## Features

- Register students and teachers
- View a student or teacher record using their ID
- Add or update marks for a student's subject and calculate the average marks
- List all registered students and teachers
- Delete a student record after confirmation
- Validate required fields, ages, email addresses, and marks
- Check saved JSON data for invalid records and duplicate IDs when starting
- Save records between runs in `school_data.json`
- Run a small automated test suite; GitHub Actions runs it on pushes and pull requests

## Requirements

- Python 3.9 or later
- No third-party packages required

## Run the program

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Run `python main.py` (or `python3 main.py` on some systems).
4. Select an option from the menu and follow the prompts.

The `school_data.json` file is created automatically when you save the first record.

## Menu

| Option | Action |
| --- | --- |
| 1 | Register student |
| 2 | Register teacher |
| 3 | Add or update student marks |
| 4 | Show student details and average marks |
| 5 | Show teacher details |
| 6 | List all students and teachers |
| 7 | Delete a student record |
| 0 | Exit |

## Run tests

From the project folder, run:

```bash
python -m unittest discover -s tests -v
```

## Data and limitations

Records are stored locally in a JSON file. The file is intended for practice and should not contain sensitive personal information. This is an educational command-line project, not a production school system; it does not include user accounts, access control, attendance, fees, a graphical interface, or multi-user database support.
