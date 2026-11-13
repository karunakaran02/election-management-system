# Election Management System (EMS) API

A secure, high-performance asynchronous REST API built to manage election workflows with strict data integrity. The system handles authentication, role-based access control, polling officer administration, polling station mapping, voter eligibility rolls, and real-time vote recording while preventing duplicate participation.

---

### Key Capabilities

- **Role-Based Access Control (RBAC)**: Fine-grained security for `admin`, `polling_officer`, and `voter` roles powered by JWT Bearer tokens and Argon2 password hashing.
- **Vote Integrity & Double-Voting Prevention**: Database-enforced constraints and voter roll verification ensure every eligible citizen votes at most once per election.
- **Polling Officer Administration**: Full lifecycle management (registration, credentialing, station assignment, and deactivation) by system administrators.
- **Asynchronous Architecture**: Built on **FastAPI**, **SQLAlchemy 2.0 (AsyncIO)**, and **PostgreSQL (`asyncpg`)** for high throughput during peak election hours.
- **Abuse Prevention**: **Redis**-backed rate limiting with SlowAPI to safeguard sensitive endpoints against brute force and scraping.
- **Database Migrations**: Version-controlled relational schema managed through **Alembic**.

---

### Tech Stack
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with asyncpg & SQLAlchemy 2.0
- **Caching & Rate Limiting**: Redis & SlowAPI
- **Auth & Security**: PyJWT & Pwdlib (Argon2)
- **Migrations**: Alembic

---

### Getting Started

#### 1. Clone the repository
```bash
git clone https://github.com/karunakaran02/election-management-system.git
cd election-management-system
```

#### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -e .
```

#### 4. Configure environment variables
Copy `.env.example` to `.env` and update with your credentials:
```bash
cp .env.example .env
```

#### 5. Run database migrations
```bash
alembic upgrade head
```

#### 6. Start the development server
```bash
uvicorn polling.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/voter_docs`
- ReDoc: `http://localhost:8000/voter_redoc`
