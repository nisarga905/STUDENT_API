# Student API

A backend-only FastAPI application for managing student records in memory.

## Project structure

```text
app/
  api/routes/students.py  API endpoints
  models/student.py       In-memory student entity
  schemas/student.py      Request and response validation
  services/              Student storage and operations
  main.py                 FastAPI application
tests/                    API tests
```

The data is stored in memory and resets when the application restarts.

## Setup

From the repository directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use:

```powershell
.venv\Scripts\activate.bat
```

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.
Interactive documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## API endpoints

| Method | URL | Purpose |
|---|---|---|
| POST | `/api/students` | Add a student |
| GET | `/api/students` | View all students |
| GET | `/api/students/{id}` | View a student by ID |
| DELETE | `/api/students/{id}` | Delete a student |

Example student JSON:

```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "age": 21,
  "course": "Computer Science"
}
```

## Test in Postman

1. Start the server.
2. Set the request URL to `http://127.0.0.1:8000`.
3. Send:
   - `POST http://127.0.0.1:8000/api/students` with the JSON example in the request body and `Content-Type: application/json`.
   - `GET http://127.0.0.1:8000/api/students`
   - `GET http://127.0.0.1:8000/api/students/1`
   - `DELETE http://127.0.0.1:8000/api/students/1`

Successful creation returns HTTP `201`. Deletion returns HTTP `204`.

## Test in a web browser

The browser can directly test read requests:

- All students: `http://127.0.0.1:8000/api/students`
- Student ID 1: `http://127.0.0.1:8000/api/students/1`
- Swagger UI: `http://127.0.0.1:8000/docs`

Use Swagger UI to add and delete students from a browser.

## Run tests

```powershell
python -m pytest
```
