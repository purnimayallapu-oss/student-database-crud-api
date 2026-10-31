Student Database CRUD API

Project Overview

A REST API built using Python, FastAPI, and SQLite to manage student records. It supports creating, retrieving, updating, and deleting student information.

Technologies Used

- Python
- FastAPI
- SQLite
- Uvicorn
- Pydantic

Features

- Create a student record
- Retrieve all student records
- Retrieve a student by ID
- Filter students by name or course
- Update student details
- Delete a student record
- Validate input data
- Prevent duplicate email addresses

API Endpoints

Method| Endpoint| Purpose
POST| "/students"| Create a student
GET| "/students"| List students
GET| "/students/{student_id}"| Retrieve one student
PUT| "/students/{student_id}"| Update a student
DELETE| "/students/{student_id}"| Delete a student

Setup Instructions

1. Install Python.
2. Open the project folder in a terminal.
3. Install dependencies:

pip install -r requirements.txt

4. Start the API:

python -m uvicorn main:app --reload

5. Open the interactive API documentation:

http://127.0.0.1:8000/docs

The SQLite database is initialized automatically when the application starts.

Database Fields

- ID
- Name
- Date of birth
- Email
- Phone
- Course
- Address
- Enrollment date

Testing

All CRUD endpoints were tested using the interactive FastAPI Swagger documentation.

Privacy

Use fictional test records. Do not publish real student personal information.