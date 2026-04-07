# Ticket Management System API

A production-ready REST API built with FastAPI, SQLAlchemy, PostgreSQL, and JWT.

## Features
- Scalable Clean Architecture & Pydantic Validation
- JWT-based Auth with full Role-Based Access Control (RBAC)
- Tickets CRUD & Pagination filters
- Rule-based AI NLP Parser for Queries (`/api/v1/ai/query`)
- Docker Support

## Setup Locally
1. Ensure Python 3.10+ is installed. Run `pip install -r requirements.txt`
2. Run PostgreSQL locally and set your DB password in `.env` (copied from `.env.example`). To easily get an instance running, you can run `docker-compose up -d db`.
3. Apply migrations: `alembic upgrade head`
4. Run server: `uvicorn app.main:app --reload`
5. Access APIs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Setup with Docker
1. Ensure Docker Desktop is running.
2. Run `docker-compose up --build -d`
3. The API will spin up mapped to port 8000. Wait a few seconds for the `db` service to be ready and Alembic to migrate.

## Testing
Comprehensive testing is available using SQLite dynamically for isolated contexts.
```bash
pytest
```
