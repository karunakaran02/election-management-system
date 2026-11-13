from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from polling.core.rate_limit import limiter
from polling.database import engine, get_db
from polling.api.routes.auth import router as auth_router
from polling.api.routes.voting import router as voting_router
from polling.api.routes.officers import router as officer_router
from polling.api.routes.redis import router as redisDb_router
from polling.core.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Before application start")
    yield
    await engine.dispose()
    print("Application destroy")


app = FastAPI(
    title="Voter polling",
    lifespan=lifespan,
    description=(
        "Election Management System is a web-based application designed to manage elections "
        "efficiently and securely. It handles user authentication and role-based access for "
        "administrators, voters, and polling officers, manages voter registration, addresses, "
        "polling stations, elections, and voter eligibility, and tracks voter participation "
        "while maintaining data integrity and preventing duplicate participation records."
    ),
    version="1.0",
    debug=False,
    docs_url="/voter_docs",
    redoc_url="/voter_redoc",
)

app.include_router(auth_router)
app.include_router(voting_router)
app.include_router(officer_router)
app.include_router(redisDb_router)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health/db")
async def get_db_health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }

