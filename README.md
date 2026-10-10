# School Management System

A beginner-friendly Python command-line project for storing basic student and teacher records in a local JSON file.

## Features

- Register students and teachers
- View a student or teacher record using their ID
- Add or update marks for a student's subject
- Calculate a student's average from recorded marks
- List all registered students and teachers
- Delete a student record after confirmation
- Check required fields, age, email format, and marks
- Save records between runs in `school_data.json`

## Requirements

- Python 3.9 or later
- No third-party packages are required

## Run the program

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Run:

   ```bash
   python main.py
   ```

   On some systems, use `python3 main.py` instead.
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

## Run basic tests

From the project folder, run:

```bash
python -m unittest discover -s tests
```

## Data and limitations

Records are stored locally in a JSON file. The file is intended for practice and should not be used to store sensitive personal information. This is an educational command-line project, not a production school system; it does not include accounts, access control, attendance, fees, a graphical interface, or multi-user database support.
