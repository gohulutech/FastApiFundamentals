# FastAPI Fundamentals

A simple car-sharing REST API built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLModel](https://sqlmodel.tiangolo.com/), backed by SQLite. Built as a learning project to practice FastAPI fundamentals.

## Features

- CRUD operations for cars
- Create trips associated with a car
- Query cars by size and number of doors
- Interactive API docs at `/docs` (Swagger UI) and `/redoc`
- SQLite persistence via SQLModel (SQLAlchemy under the hood)

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)

## Setup

```bash
# Create a virtual environment and install dependencies
uv sync
```

## Running the app

```bash
uv run fastapi-fundamentals
```

Or, running uvicorn directly with auto-reload for development:

```bash
uv run uvicorn fastapi_fundamentals.carsharing:app --reload
```

The app will be available at `http://localhost:8000`.

- Interactive docs: http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                | Description                       |
|--------|-------------------------|-----------------------------------|
| GET    | `/api/cars`             | List cars (filter by `size` / `doors`) |
| GET    | `/api/cars/{id}`        | Get a single car by id            |
| POST   | `/api/cars/`            | Create a new car                  |
| PUT    | `/api/cars/{id}`        | Update an existing car            |
| DELETE | `/api/cars/{id}`        | Delete a car                      |
| POST   | `/api/cars/{id}/trips`  | Add a trip to a car               |

### Example: Create a car

```bash
curl -X POST http://localhost:8000/api/cars/ \
  -H "Content-Type: application/json" \
  -d '{"size": "m", "doors": 5, "transmission": "manual", "fuel": "hybrid"}'
```

## Project structure

```
src/fastapi_fundamentals/
├── __init__.py         # main() entry point (runs uvicorn)
├── carsharing.py       # FastAPI app wiring, middleware, exception handlers
├── db.py               # SQLite engine and session dependency
├── schemas.py          # SQLModel models and input/output schemas
├── create_user.py      # create-user CLI script
├── routers/
│   ├── cars.py         # /api/cars endpoints
│   ├── auth.py         # /auth token endpoints
│   └── web.py          # HTML pages (home, search)
└── templates/          # Jinja2 HTML templates
tests/
├── conftest.py         # shared fixtures (in-memory DB, TestClient)
├── test_cars.py
├── test_auth.py
└── test_schemas.py
```

## Database

The app uses a local SQLite database file (`carsharing.db`) that is created automatically on startup. It's gitignored, so it won't be committed to version control.

## Creating a user

```bash
uv run create-user
```

## Running the tests

```bash
uv run pytest
```
