from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
import sqlite3

from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field


DB_PATH = Path(__file__).parent / "students.db"


@contextmanager
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def create_table():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield


app = FastAPI(title="Student Database API", lifespan=lifespan)


class StudentInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: EmailStr
    phone: str | None = None
    course: str | None = None
    address: str | None = None
    enrollment_date: date | None = None


def clean(student):
    data = student.model_dump(mode="json")
    data["name"] = data["name"].strip()
    if not data["name"]:
        raise HTTPException(422, "Name cannot be blank")
    return data


def get_student(student_id):
    with get_db() as con:
        row = con.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(404, "Student not found")
    return dict(row)


@app.post("/students", status_code=201)
def create_student(student: StudentInput):
    data = clean(student)
    try:
        with get_db() as con:
            cur = con.execute("""
                INSERT INTO students
                (name, date_of_birth, email, phone, course,
                 address, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tuple(data.values()))
            student_id = cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Email already exists") from exc

    return get_student(student_id)


@app.get("/students")
def list_students(name: str | None = None,
                  course: str | None = None):
    sql = "SELECT * FROM students WHERE 1=1"
    params = []

    if name:
        sql += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        sql += " AND course LIKE ?"
        params.append(f"%{course}%")

    with get_db() as con:
        rows = con.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


@app.get("/students/{student_id}")
def read_student(student_id: int):
    return get_student(student_id)


@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentInput):
    get_student(student_id)
    data = clean(student)

    try:
        with get_db() as con:
            con.execute("""
                UPDATE students
                SET name=?, date_of_birth=?, email=?, phone=?,
                    course=?, address=?, enrollment_date=?
                WHERE id=?
            """, (*data.values(), student_id))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Email already exists") from exc

    return get_student(student_id)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    get_student(student_id)
    with get_db() as con:
        con.execute(
            "DELETE FROM students WHERE id = ?", (student_id,)
        )
    return {"message": "Student deleted successfully"}